"""
generator.py
----------------------------------------------------------------------
Generate the Synthetic Underground Hydrogen Storage MRV (SUHS-MRV)
dataset using the configuration in config/uhs_config.yaml and the
physics helpers in physics.py.

Outputs three CSV files under data/generated/:

  - facility_metadata.csv
  - facility_timeseries.csv
  - cycle_summary.csv

This module is designed to be readable and reproducible so that the
generation procedure can be described clearly in the accompanying paper.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

import numpy as np
import pandas as pd
import yaml

from physics import (
    build_thermo_config,
    build_temperature_noise_config,
    build_loss_config,
    build_purity_config,
    build_validation_config,
    ThermoConfig,
    TemperatureNoiseConfig,
    LossConfig,
    PurityConfig,
    ValidationConfig,
    compute_temperature_c,
    mass_from_pvt,
    pressure_from_mass,
    sample_loss_fraction,
    compute_cycle_losses_kg,
    sample_inlet_purity_pct,
    update_purity_out_pct,
    mass_balance_residual_fraction,
)


# ---------------------------------------------------------------------
# CONFIG LOADING
# ---------------------------------------------------------------------


def load_config(path: str = "config/uhs_config.yaml") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


# ---------------------------------------------------------------------
# FACILITY GENERATION
# ---------------------------------------------------------------------


def _sample_lognormal_bounded(
    rng: np.random.Generator,
    mean: float,
    sigma: float,
    min_val: float,
    max_val: float,
) -> float:
    """Sample from a lognormal and clip to [min_val, max_val]."""
    value = rng.lognormal(mean=np.log(mean), sigma=sigma)
    value = max(min_val, min(value, max_val))
    return float(value)


def _sample_uniform(
    rng: np.random.Generator,
    min_val: float,
    max_val: float,
) -> float:
    return float(rng.uniform(min_val, max_val))


def create_facilities(
    cfg: Dict[str, Any],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Create facility-level metadata based on config.

    Returns a DataFrame with one row per facility, including:
      - facility_id, facility_type
      - basic location placeholders (country, region, lat/lon)
      - depth, cavern_volume, porosity, permeability, pressure bounds
    """
    n_facilities = cfg["global"]["n_facilities"]
    weights = cfg["global"]["facility_type_weights"]
    facility_types = list(weights.keys())
    type_probs = np.array(list(weights.values()), dtype=float)
    type_probs = type_probs / type_probs.sum()

    # For now, simple placeholder geography (can be refined later)
    countries = ["US", "DE", "NL", "FR", "NO"]
    regions = ["Gulf Coast", "North Sea", "Onshore EU", "Offshore EU", "Nordic"]

    salt_cfg = cfg["facility_types"]["salt_cavern"]
    porous_cfg = cfg["facility_types"]["porous_reservoir"]

    rows = []

    for i in range(n_facilities):
        facility_type = rng.choice(facility_types, p=type_probs)

        country_code = rng.choice(countries)
        region = rng.choice(regions)
        latitude = float(rng.uniform(-60.0, 60.0))
        longitude = float(rng.uniform(-180.0, 180.0))

        if facility_type == "salt_cavern":
            depth = _sample_uniform(
                rng,
                salt_cfg["depth_m"]["min"],
                salt_cfg["depth_m"]["max"],
            )
            # Cavern volume from configured lognormal distribution
            cav_conf = salt_cfg["cavern_volume_m3"]
            cavern_volume_m3 = _sample_lognormal_bounded(
                rng,
                mean=cav_conf["mean"],
                sigma=cav_conf["sigma"],
                min_val=cav_conf["min"],
                max_val=cav_conf["max"],
            )
            porosity = np.nan
            permeability = np.nan
            pmin = salt_cfg["pressure_min_mpa"]
            pmax = salt_cfg["pressure_max_mpa"]

        else:  # porous_reservoir
            depth = _sample_uniform(
                rng,
                porous_cfg["depth_m"]["min"],
                porous_cfg["depth_m"]["max"],
            )
            poro_conf = porous_cfg["porosity"]
            perm_conf = porous_cfg["permeability_mD"]

            porosity = _sample_uniform(
                rng,
                poro_conf["min"],
                poro_conf["max"],
            )
            permeability = _sample_lognormal_bounded(
                rng,
                mean=perm_conf["mean"],
                sigma=perm_conf["sigma"],
                min_val=perm_conf["min"],
                max_val=perm_conf["max"],
            )

            # For porous reservoirs, approximate an effective storage volume
            # by sampling from the same distribution used for caverns.
            # This represents an equivalent pore volume for storage.
            cav_conf = salt_cfg["cavern_volume_m3"]
            cavern_volume_m3 = _sample_lognormal_bounded(
                rng,
                mean=cav_conf["mean"],
                sigma=cav_conf["sigma"],
                min_val=cav_conf["min"],
                max_val=cav_conf["max"],
            )

            pmin = porous_cfg["pressure_min_mpa"]
            pmax = porous_cfg["pressure_max_mpa"]

        rows.append(
            {
                "facility_id": f"UHS_{i+1:03d}",
                "facility_type": facility_type,
                "country_code": country_code,
                "region": region,
                "latitude": latitude,
                "longitude": longitude,
                "depth_m": depth,
                "cavern_volume_m3": cavern_volume_m3,
                "porosity": porosity,
                "permeability_mD": permeability,
                "pressure_min_mpa": pmin,
                "pressure_max_mpa": pmax,
            }
        )

    df = pd.DataFrame(rows)
    return df


# ---------------------------------------------------------------------
# TIME AXIS & CYCLING PATTERNS
# ---------------------------------------------------------------------


def generate_time_index(
    start_date: str,
    n_years: int,
) -> pd.DatetimeIndex:
    """
    Generate a weekly time index for the full simulation period.
    """
    start = datetime.fromisoformat(start_date)
    n_weeks = n_years * 52
    dates = [start + timedelta(weeks=i) for i in range(n_weeks)]
    return pd.DatetimeIndex(dates)


def assign_active_cycles_per_year(
    cfg: Dict[str, Any],
    time_index: pd.DatetimeIndex,
    rng: np.random.Generator,
) -> Dict[int, np.ndarray]:
    """
    For each year in the simulation, choose which weeks are active cycles.

    Returns a mapping:
        year -> array of indices in time_index that are active.
    """
    cyc_cfg = cfg["cycling"]
    min_c = cyc_cfg["min_cycles_per_year"]
    max_c = cyc_cfg["max_cycles_per_year"]

    # Group week indices by year
    year_to_indices: Dict[int, list] = {}
    for idx, ts in enumerate(time_index):
        year = ts.year
        year_to_indices.setdefault(year, []).append(idx)

    year_active_indices: Dict[int, np.ndarray] = {}
    for year, indices in year_to_indices.items():
        n_indices = len(indices)
        n_cycles = int(rng.integers(min_c, max_c + 1))
        n_cycles = min(n_cycles, n_indices)
        active = rng.choice(indices, size=n_cycles, replace=False)
        active.sort()
        year_active_indices[year] = active

    return year_active_indices


# ---------------------------------------------------------------------
# FACILITY-LEVEL SIMULATION
# ---------------------------------------------------------------------


def _compute_facility_capacity_kg(
    facility_row: pd.Series,
    cfg: Dict[str, Any],
    thermo_cfg: ThermoConfig,
    temp_noise_cfg: TemperatureNoiseConfig,
    rng: np.random.Generator,
) -> Tuple[float, float]:
    """
    Compute working gas capacity and cushion gas mass for a facility.

    Returns:
      working_capacity_kg, cushion_gas_kg
    """
    ftype = facility_row["facility_type"]
    depth_m = float(facility_row["depth_m"])
    volume_m3 = float(facility_row["cavern_volume_m3"])

    if ftype == "salt_cavern":
        fcfg = cfg["facility_types"]["salt_cavern"]
        working_frac = fcfg["working_gas_fraction_of_total"]
        base_T = fcfg["base_temperature_c"]
        grad = fcfg["temperature_gradient_c_per_km"]
        pmax = fcfg["pressure_max_mpa"]
    else:
        fcfg = cfg["facility_types"]["porous_reservoir"]
        working_frac = fcfg["working_gas_fraction_of_pore_volume"]
        base_T = fcfg["base_temperature_c"]
        grad = fcfg["temperature_gradient_c_per_km"]
        pmax = fcfg["pressure_max_mpa"]

    # Use a representative reservoir temperature at depth
    temp_c = compute_temperature_c(
        depth_m=depth_m,
        base_temperature_c=base_T,
        gradient_c_per_km=grad,
        noise_cfg=temp_noise_cfg,
        rng=rng,
    )

    # Total gas mass at maximum pressure (simplified)
    total_mass_kg = mass_from_pvt(
        pressure_mpa=pmax,
        temperature_c=temp_c,
        volume_m3=volume_m3,
        thermo=thermo_cfg,
    )

    working_capacity_kg = max(total_mass_kg * working_frac, 0.0)
    cushion_gas_kg = max(total_mass_kg - working_capacity_kg, 0.0)

    return working_capacity_kg, cushion_gas_kg


def simulate_facility_timeseries(
    facility_row: pd.Series,
    cfg: Dict[str, Any],
    thermo_cfg: ThermoConfig,
    temp_noise_cfg: TemperatureNoiseConfig,
    loss_cfg: LossConfig,
    purity_cfg: PurityConfig,
    val_cfg: ValidationConfig,
    time_index: pd.DatetimeIndex,
    year_active_indices: Dict[int, np.ndarray],
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Simulate weekly timeseries for a single facility.

    Returns:
      timeseries_df, cycle_summary_df
    """
    ftype = facility_row["facility_type"]
    depth_m = float(facility_row["depth_m"])
    volume_m3 = float(facility_row["cavern_volume_m3"])

    if ftype == "salt_cavern":
        fcfg = cfg["facility_types"]["salt_cavern"]
    else:
        fcfg = cfg["facility_types"]["porous_reservoir"]

    base_T = fcfg["base_temperature_c"]
    grad = fcfg["temperature_gradient_c_per_km"]
    pmin = float(facility_row["pressure_min_mpa"])
    pmax = float(facility_row["pressure_max_mpa"])

    cyc_cfg = cfg["cycling"]
    dist_cfg = cfg["distributions"]

    working_capacity_kg, cushion_gas_kg = _compute_facility_capacity_kg(
        facility_row, cfg, thermo_cfg, temp_noise_cfg, rng
    )

    # Initialize states
    working_gas_kg = working_capacity_kg * 0.5  # start half full
    static_leak_per_year = _sample_uniform(
    rng,
    loss_cfg.static_leak_min_kg_per_year,
    loss_cfg.static_leak_max_kg_per_year,
)
    static_leak_per_week = static_leak_per_year / 52.0

    injection_mean = dist_cfg["injection_mass_kg"]["relative_mean"]
    injection_sigma = dist_cfg["injection_mass_kg"]["relative_sigma"]
    inj_min_frac = dist_cfg["injection_mass_kg"]["min_fraction_of_capacity"]
    inj_max_frac = dist_cfg["injection_mass_kg"]["max_fraction_of_capacity"]

    withdrawal_mean = dist_cfg["withdrawal_mass_kg"]["relative_mean"]
    withdrawal_sigma = dist_cfg["withdrawal_mass_kg"]["relative_sigma"]
    wdr_min_frac = dist_cfg["withdrawal_mass_kg"]["min_fraction_of_capacity"]
    wdr_max_frac = dist_cfg["withdrawal_mass_kg"]["max_fraction_of_capacity"]

    pressure_noise_mean = dist_cfg["pressure_noise_mpa"]["mean"]
    pressure_noise_std = dist_cfg["pressure_noise_mpa"]["std"]

    max_delta_frac = cyc_cfg["max_relative_change_in_cycle_mass"]["per_cycle"]
    cap_min_frac = cyc_cfg["cycle_mass_fraction_of_capacity"]["min"]
    cap_max_frac = cyc_cfg["cycle_mass_fraction_of_capacity"]["max"]

    mode_mix = cyc_cfg["mode_mix"]
    mode_choices = ["injection_heavy", "withdrawal_heavy", "balanced"]
    mode_probs = np.array(
        [
            mode_mix["injection_heavy_fraction"],
            mode_mix["withdrawal_heavy_fraction"],
            mode_mix["balanced_fraction"],
        ],
        dtype=float,
    )
    mode_probs = mode_probs / mode_probs.sum()

    records = []
    cycle_records = []

    last_cycle_fraction = 0.1
    cycle_index = 0

    for idx, ts in enumerate(time_index):
        year = ts.year
        active_indices = year_active_indices.get(year, np.array([], dtype=int))
        is_active = idx in active_indices

        # Base temperature at this time step
        temperature_c = compute_temperature_c(
            depth_m=depth_m,
            base_temperature_c=base_T,
            gradient_c_per_km=grad,
            noise_cfg=temp_noise_cfg,
            rng=rng,
        )

        # Static leak applies every week
        working_gas_kg = max(working_gas_kg - static_leak_per_week, 0.0)
        static_losses_kg = static_leak_per_week

        h2_injected_kg = 0.0
        h2_withdrawn_kg = 0.0
        cycle_efficiency = np.nan
        purity_in_pct = np.nan
        purity_out_pct = np.nan
        dynamic_losses_kg = 0.0

        if is_active:
            cycle_index += 1

            mode = rng.choice(mode_choices, p=mode_probs)

            # Sample target cycle mass fraction and apply ramping constraint
            target_frac = rng.lognormal(mean=np.log(injection_mean), sigma=injection_sigma)
            target_frac = max(cap_min_frac, min(target_frac, cap_max_frac))
            # enforce ramping
            delta = target_frac - last_cycle_fraction
            delta = max(-max_delta_frac, min(delta, max_delta_frac))
            cycle_frac = last_cycle_fraction + delta
            cycle_frac = max(cap_min_frac, min(cycle_frac, cap_max_frac))
            last_cycle_fraction = cycle_frac

            target_mass = working_capacity_kg * cycle_frac

            if mode == "injection_heavy":
                h2_injected_kg = target_mass
                h2_withdrawn_kg = target_mass * float(rng.uniform(0.1, 0.6))
            elif mode == "withdrawal_heavy":
                h2_withdrawn_kg = target_mass
                h2_injected_kg = target_mass * float(rng.uniform(0.1, 0.6))
            else:  # balanced
                base = target_mass
                eps = float(rng.uniform(-0.1, 0.1)) * target_mass
                h2_injected_kg = max(base + eps, 0.0)
                h2_withdrawn_kg = max(base - eps, 0.0)

            # Cycle loss fraction and dynamic losses
            loss_fraction = sample_loss_fraction(loss_cfg, rng)
            dynamic_losses_kg = compute_cycle_losses_kg(working_gas_kg, loss_fraction)

            # Update working gas inventory
            prev_working = working_gas_kg
            working_gas_kg = (
                working_gas_kg + h2_injected_kg - h2_withdrawn_kg - dynamic_losses_kg - static_losses_kg
            )

            # Clamp to [0, capacity] and adjust if needed
            if working_gas_kg < 0.0:
                deficit = -working_gas_kg
                # reduce withdrawals to fix
                reduction = min(deficit, h2_withdrawn_kg)
                h2_withdrawn_kg -= reduction
                working_gas_kg = 0.0

            if working_gas_kg > working_capacity_kg:
                excess = working_gas_kg - working_capacity_kg
                # reduce injection to fix
                reduction = min(excess, h2_injected_kg)
                h2_injected_kg -= reduction
                working_gas_kg = working_capacity_kg

            total_cycle_losses_kg = dynamic_losses_kg + static_losses_kg
            delta_storage_kg = working_gas_kg - prev_working

            # Cycle efficiency and purity
            if h2_injected_kg > 0:
                cycle_efficiency = h2_withdrawn_kg / h2_injected_kg
            else:
                cycle_efficiency = np.nan

            purity_in_pct = sample_inlet_purity_pct(purity_cfg, rng)
            purity_out_pct = update_purity_out_pct(
                purity_in_pct, purity_cfg, rng
            )

            # Mass balance check (can be used in validation notebook)
            _ = mass_balance_residual_fraction(
                injected_kg=h2_injected_kg,
                withdrawn_kg=h2_withdrawn_kg,
                losses_kg=total_cycle_losses_kg,
                delta_storage_kg=delta_storage_kg,
            )

            cycle_records.append(
                {
                    "facility_id": facility_row["facility_id"],
                    "cycle_index": cycle_index,
                    "cycle_start": ts,
                    "cycle_end": ts + timedelta(weeks=1),
                    "total_injected_kg": h2_injected_kg,
                    "total_withdrawn_kg": h2_withdrawn_kg,
                    "total_losses_kg": total_cycle_losses_kg,
                    "avg_pressure_mpa": np.nan,  # filled below
                    "avg_temperature_c": temperature_c,
                    "cycle_efficiency": cycle_efficiency,
                }
            )
        else:
            # No active cycle this week; only static leak already applied
            total_cycle_losses_kg = static_losses_kg

        # Compute pressure from current gas inventory (working + cushion)
        total_gas_kg = working_gas_kg + cushion_gas_kg
        pressure_mpa = pressure_from_mass(
            mass_kg=total_gas_kg,
            temperature_c=temperature_c,
            volume_m3=volume_m3,
            thermo=thermo_cfg,
        )

        # Add random pressure noise
        pressure_mpa += float(
            rng.normal(pressure_noise_mean, pressure_noise_std)
        )
        # Clamp to facility pressure bounds with small margin considered in validation
        pressure_mpa = max(pmin - val_cfg.pressure_margin_mpa, pressure_mpa)
        pressure_mpa = min(pmax + val_cfg.pressure_margin_mpa, pressure_mpa)

        # If no active cycle, reuse previous purity values if available
        if not np.isfinite(purity_in_pct):
            if records:
                purity_in_pct = records[-1]["purity_in_pct"]
                purity_out_pct = records[-1]["purity_out_pct"]
            else:
                # default high purity
                purity_in_pct = purity_cfg.inlet_mean
                purity_out_pct = purity_cfg.inlet_mean

        records.append(
            {
                "facility_id": facility_row["facility_id"],
                "timestamp": ts,
                "cycle_index": cycle_index if is_active else 0,
                "is_cycle_active": bool(is_active),
                "h2_injected_kg": h2_injected_kg,
                "h2_withdrawn_kg": h2_withdrawn_kg,
                "working_gas_kg": working_gas_kg,
                "cushion_gas_kg": cushion_gas_kg,
                "losses_kg": total_cycle_losses_kg,
                "pressure_mpa": pressure_mpa,
                "temperature_c": temperature_c,
                "purity_in_pct": purity_in_pct,
                "purity_out_pct": purity_out_pct,
                "cycle_efficiency": cycle_efficiency,
            }
        )

    ts_df = pd.DataFrame(records)
    cycles_df = pd.DataFrame(cycle_records)

    if not cycles_df.empty:
        # Fill avg_pressure_mpa from timeseries: average over the week where cycle_index matches
        merged = (
            ts_df[["facility_id", "timestamp", "cycle_index", "pressure_mpa"]]
            .copy()
        )
        merged_active = merged[merged["cycle_index"] > 0]
        if not merged_active.empty:
            avg_pressures = (
                merged_active.groupby(["facility_id", "cycle_index"])["pressure_mpa"]
                .mean()
                .reset_index()
                .rename(columns={"pressure_mpa": "avg_pressure_mpa"})
            )
            cycles_df = cycles_df.drop(columns=["avg_pressure_mpa"])
            cycles_df = cycles_df.merge(
                avg_pressures,
                on=["facility_id", "cycle_index"],
                how="left",
            )

    return ts_df, cycles_df


# ---------------------------------------------------------------------
# MAIN DATASET GENERATION PIPELINE
# ---------------------------------------------------------------------


def generate_uhs_dataset(
    config_path: str = "config/uhs_config.yaml",
    output_dir: str = "data/generated",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    High-level function to generate the full SUHS-MRV dataset.

    Returns:
      facility_metadata_df, facility_timeseries_df, cycle_summary_df
    """
    cfg = load_config(config_path)

    seed = cfg["global"]["random_seed"]
    rng = np.random.default_rng(seed)

    thermo_cfg = build_thermo_config(cfg)
    temp_noise_cfg = build_temperature_noise_config(cfg)
    loss_cfg = build_loss_config(cfg)
    purity_cfg = build_purity_config(cfg)
    val_cfg = build_validation_config(cfg)

    # 1) Facility-level metadata
    facility_df = create_facilities(cfg, rng)

    # 2) Time index & cycle activation patterns
    sim_cfg = cfg["global"]["simulation"]
    time_index = generate_time_index(
        start_date=sim_cfg["start_date"],
        n_years=sim_cfg["n_years"],
    )
    year_active_indices = assign_active_cycles_per_year(
        cfg, time_index, rng
    )

    # 3) Simulate each facility
    ts_frames = []
    cycle_frames = []

    for _, row in facility_df.iterrows():
        ts_df, cycles_df = simulate_facility_timeseries(
            facility_row=row,
            cfg=cfg,
            thermo_cfg=thermo_cfg,
            temp_noise_cfg=temp_noise_cfg,
            loss_cfg=loss_cfg,
            purity_cfg=purity_cfg,
            val_cfg=val_cfg,
            time_index=time_index,
            year_active_indices=year_active_indices,
            rng=rng,
        )
        ts_frames.append(ts_df)
        cycle_frames.append(cycles_df)

    timeseries_df = pd.concat(ts_frames, ignore_index=True)

    if cycle_frames:
        cycle_summary_df = pd.concat(cycle_frames, ignore_index=True)
    else:
        cycle_summary_df = pd.DataFrame(
            columns=[
                "facility_id",
                "cycle_index",
                "cycle_start",
                "cycle_end",
                "total_injected_kg",
                "total_withdrawn_kg",
                "total_losses_kg",
                "avg_pressure_mpa",
                "avg_temperature_c",
                "cycle_efficiency",
            ]
        )

    # 4) Write to CSV
    os.makedirs(output_dir, exist_ok=True)
    facility_path = os.path.join(output_dir, "facility_metadata.csv")
    timeseries_path = os.path.join(output_dir, "facility_timeseries.csv")
    cycle_path = os.path.join(output_dir, "cycle_summary.csv")

    facility_df.to_csv(facility_path, index=False)
    timeseries_df.to_csv(timeseries_path, index=False)
    cycle_summary_df.to_csv(cycle_path, index=False)

    print(f"Written: {facility_path}")
    print(f"Written: {timeseries_path}")
    print(f"Written: {cycle_path}")

    return facility_df, timeseries_df, cycle_summary_df


if __name__ == "__main__":
    generate_uhs_dataset()
