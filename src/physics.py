"""
physics.py
----------------------------------------------------------------------
Core physics and validation helpers for the SUHS-MRV Underground
Hydrogen Storage (UHS) synthetic dataset.

Implements:
- Temperature vs. depth with noise
- Compressibility factor Z (piecewise)
- Real-gas relationships (P, V, T, mass)
- Simple porous-reservoir Darcy-based pressure change helper
- Loss and purity models
- Mass-balance residuals and basic validation helpers

All numerical ranges and distributions are controlled by
config/uhs_config.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

import math
import numpy as np


# -------------------------------------------------------------------
# DATA CLASSES FOR CONFIG VIEWS
# -------------------------------------------------------------------


@dataclass
class ThermoConfig:
    gas_constant_R_J_per_molK: float
    molar_mass_H2_kg_per_mol: float
    compressibility_segments: List[Dict[str, float]]


@dataclass
class TemperatureNoiseConfig:
    distribution: str
    mean: float
    std: float


@dataclass
class LossConfig:
    loss_min: float
    loss_max: float
    static_leak_min_kg_per_year: float
    static_leak_max_kg_per_year: float


@dataclass
class PurityConfig:
    inlet_mean: float
    inlet_std: float
    inlet_min: float
    inlet_max: float
    outlet_noise_mean: float
    outlet_noise_std: float
    outlet_noise_min: float
    outlet_noise_max: float


@dataclass
class ValidationConfig:
    pressure_margin_mpa: float
    temperature_min_c: float
    temperature_max_c: float
    purity_min_pct: float
    purity_max_pct: float
    loss_fraction_min: float
    loss_fraction_max: float
    allow_missing_values: bool
    mass_balance_tolerance_fraction: float


# -------------------------------------------------------------------
# CONFIG BUILDERS
# -------------------------------------------------------------------


def build_thermo_config(cfg: Dict[str, Any]) -> ThermoConfig:
    thermo = cfg["thermodynamics"]
    segments = thermo["compressibility_Z"]["segments"]
    return ThermoConfig(
        gas_constant_R_J_per_molK=thermo["gas_constant_R_J_per_molK"],
        molar_mass_H2_kg_per_mol=thermo["molar_mass_H2_kg_per_mol"],
        compressibility_segments=segments,
    )


def build_temperature_noise_config(cfg: Dict[str, Any]) -> TemperatureNoiseConfig:
    tn = cfg["thermodynamics"]["temperature_noise_c"]
    return TemperatureNoiseConfig(
        distribution=tn["distribution"],
        mean=tn["mean"],
        std=tn["std"],
    )


def build_loss_config(cfg: Dict[str, Any]) -> LossConfig:
    loss_cfg = cfg["losses"]["loss_fraction"]
    static_leak = cfg["losses"]["static_leak_kg_per_year"]
    return LossConfig(
        loss_min=loss_cfg["min"],
        loss_max=loss_cfg["max"],
        static_leak_min_kg_per_year=static_leak["min"],
        static_leak_max_kg_per_year=static_leak["max"],
    )


def build_purity_config(cfg: Dict[str, Any]) -> PurityConfig:
    p_cfg = cfg["purity"]
    inlet = p_cfg["inlet_purity_pct"]
    outlet = p_cfg["outlet_purity_noise_pct"]
    return PurityConfig(
        inlet_mean=inlet["mean"],
        inlet_std=inlet["std"],
        inlet_min=inlet["min"],
        inlet_max=inlet["max"],
        outlet_noise_mean=outlet["mean"],
        outlet_noise_std=outlet["std"],
        outlet_noise_min=outlet["min"],
        outlet_noise_max=outlet["max"],
    )


def build_validation_config(cfg: Dict[str, Any]) -> ValidationConfig:
    v = cfg["validation"]
    purity = v["purity_pct"]
    temp = v["temperature_c"]
    loss = v["loss_fraction"]
    return ValidationConfig(
        pressure_margin_mpa=v["pressure_bounds_margin_mpa"],
        temperature_min_c=temp["min"],
        temperature_max_c=temp["max"],
        purity_min_pct=purity["min"],
        purity_max_pct=purity["max"],
        loss_fraction_min=loss["min"],
        loss_fraction_max=loss["max"],
        allow_missing_values=v["allow_missing_values"],
        mass_balance_tolerance_fraction=cfg["mass_balance"]["tolerance_fraction"],
    )


# -------------------------------------------------------------------
# THERMODYNAMICS
# -------------------------------------------------------------------


def get_compressibility_z(pressure_mpa: float, thermo: ThermoConfig) -> float:
    """
    Approximate compressibility factor Z for hydrogen, given pressure
    in MPa, using piecewise-constant segments defined in config.
    """
    for seg in thermo.compressibility_segments:
        pmin = seg["pressure_min_mpa"]
        pmax = seg["pressure_max_mpa"]
        if pmin <= pressure_mpa < pmax:
            return float(seg["Z"])
    # Fallback to last segment if outside range
    return float(thermo.compressibility_segments[-1]["Z"])


def compute_temperature_c(
    depth_m: float,
    base_temperature_c: float,
    gradient_c_per_km: float,
    noise_cfg: TemperatureNoiseConfig,
    rng: np.random.Generator,
) -> float:
    """
    Compute temperature at depth using a simple geothermal gradient:

        T = base_temperature_c + gradient_c_per_km * depth_km + noise

    Depth is in meters, gradient in °C per km.
    """
    depth_km = depth_m / 1000.0
    temperature = base_temperature_c + gradient_c_per_km * depth_km

    if noise_cfg.distribution == "normal":
        noise = rng.normal(noise_cfg.mean, noise_cfg.std)
    else:
        noise = 0.0

    return float(temperature + noise)


def mass_from_pvt(
    pressure_mpa: float,
    temperature_c: float,
    volume_m3: float,
    thermo: ThermoConfig,
) -> float:
    """
    Compute hydrogen mass (kg) from P [MPa], T [°C], and volume [m3],
    using a simple real-gas relationship:

        P * V = Z * n * R * T

    where:
        P in Pa   (MPa -> Pa)
        V in m3
        T in K    (°C -> K)
        R in J/(mol*K)
        n moles
        Z compressibility factor

    mass_kg = n * molar_mass_H2
    """
    if volume_m3 <= 0:
        return 0.0

    pressure_pa = pressure_mpa * 1.0e6
    temperature_k = temperature_c + 273.15

    Z = get_compressibility_z(pressure_mpa, thermo)
    R = thermo.gas_constant_R_J_per_molK
    M = thermo.molar_mass_H2_kg_per_mol

    n_moles = (pressure_pa * volume_m3) / (Z * R * temperature_k)
    mass_kg = n_moles * M

    return max(float(mass_kg), 0.0)


def pressure_from_mass(
    mass_kg: float,
    temperature_c: float,
    volume_m3: float,
    thermo: ThermoConfig,
) -> float:
    """
    Invert the real-gas relationship to compute P [MPa] from mass [kg],
    T [°C], and volume [m3].

    We solve P using a simple fixed-point iteration for Z(P).
    """
    if volume_m3 <= 0 or mass_kg <= 0:
        return 0.0

    temperature_k = temperature_c + 273.15
    R = thermo.gas_constant_R_J_per_molK
    M = thermo.molar_mass_H2_kg_per_mol

    n_moles = mass_kg / M

    # Initial guess and fixed-point iterations
    pressure_pa = 1.0e7  # ~10 MPa
    for _ in range(5):
        pressure_mpa = pressure_pa / 1.0e6
        Z = get_compressibility_z(pressure_mpa, thermo)
        pressure_pa = (Z * n_moles * R * temperature_k) / max(volume_m3, 1e-9)

    pressure_mpa_final = pressure_pa / 1.0e6
    return max(float(pressure_mpa_final), 0.0)


# -------------------------------------------------------------------
# POROUS-RESERVOIR DARCY HELPER (OPTIONAL)
# -------------------------------------------------------------------


def approximate_darcy_pressure_change_mpa(
    rate_m3_per_s: float,
    viscosity_cp: float,
    length_m: float,
    permeability_mD: float,
    area_m2: float,
) -> float:
    """
    Simplified Darcy-based pressure change [MPa] across reservoir rock:

        ΔP = (Q * μ * L) / (k * A)

    Q : volumetric flow rate [m3/s]
    μ : viscosity [Pa.s]  (1 cP = 1e-3 Pa.s)
    L : flow length [m]
    k : permeability [m2] (1 mD ≈ 9.869e-16 m2)
    A : flow area [m2]

    Used to generate plausible trends rather than full simulation.
    """
    if rate_m3_per_s <= 0 or area_m2 <= 0 or permeability_mD <= 0:
        return 0.0

    mu_pa_s = viscosity_cp * 1.0e-3
    k_m2 = permeability_mD * 9.869e-16

    delta_p_pa = (rate_m3_per_s * mu_pa_s * length_m) / (k_m2 * area_m2)
    delta_p_mpa = delta_p_pa / 1.0e6
    return max(float(delta_p_mpa), 0.0)


# -------------------------------------------------------------------
# LOSSES & PURITY
# -------------------------------------------------------------------


def sample_loss_fraction(loss_cfg: LossConfig, rng: np.random.Generator) -> float:
    """
    Sample a dimensionless loss fraction from configured bounds.
    """
    return float(rng.uniform(loss_cfg.loss_min, loss_cfg.loss_max))


def compute_cycle_losses_kg(
    working_gas_kg: float,
    loss_fraction: float,
) -> float:
    """
    Compute cycle losses as a proportion of current working gas mass.
    """
    if working_gas_kg <= 0 or loss_fraction <= 0:
        return 0.0
    return max(float(working_gas_kg * loss_fraction), 0.0)


def sample_inlet_purity_pct(purity_cfg: PurityConfig, rng: np.random.Generator) -> float:
    """
    Sample inlet hydrogen purity [%] from a normal distribution and
    clip to [inlet_min, inlet_max].
    """
    val = rng.normal(purity_cfg.inlet_mean, purity_cfg.inlet_std)
    val = max(purity_cfg.inlet_min, val)
    val = min(purity_cfg.inlet_max, val)
    return float(val)


def update_purity_out_pct(
    purity_in_pct: float,
    purity_cfg: PurityConfig,
    rng: np.random.Generator,
) -> float:
    """
    Compute outlet purity [%] from inlet purity and a small noise term.
    This allows minor drift in purity between inlet and outlet.
    """
    noise = rng.normal(
        purity_cfg.outlet_noise_mean,
        purity_cfg.outlet_noise_std,
    )
    purity_out = purity_in_pct + noise

    # Clip outlet purity to a safe range (0–100) and within config inlet bounds
    purity_out = max(0.0, purity_out)
    purity_out = min(100.0, purity_out)
    purity_out = max(purity_cfg.inlet_min, purity_out)
    purity_out = min(purity_cfg.inlet_max, purity_out)

    return float(purity_out)


# -------------------------------------------------------------------
# VALIDATION HELPERS & MASS BALANCE
# -------------------------------------------------------------------


def mass_balance_residual_fraction(
    injected_kg: float,
    withdrawn_kg: float,
    losses_kg: float,
    delta_storage_kg: float,
) -> float:
    """
    Compute a dimensionless mass-balance residual:

        residual = |in - out - losses - Δstorage| / max(in, epsilon)

    Values close to zero indicate good numerical consistency.
    """
    eps = 1e-9
    numerator = abs(injected_kg - withdrawn_kg - losses_kg - delta_storage_kg)
    denom = max(abs(injected_kg), eps)
    return float(numerator / denom)


def check_pressure_within_bounds(
    pressure_mpa: float,
    p_min_mpa: float,
    p_max_mpa: float,
    margin_mpa: float,
) -> bool:
    """
    True if pressure is within [p_min - margin, p_max + margin].
    """
    lower = p_min_mpa - margin_mpa
    upper = p_max_mpa + margin_mpa
    return (pressure_mpa >= lower) and (pressure_mpa <= upper)


def check_temperature_range(
    temperature_c: float,
    vcfg: ValidationConfig,
) -> bool:
    return (vcfg.temperature_min_c <= temperature_c <= vcfg.temperature_max_c)


def check_purity_range(
    purity_pct: float,
    vcfg: ValidationConfig,
) -> bool:
    return (vcfg.purity_min_pct <= purity_pct <= vcfg.purity_max_pct)


def check_loss_fraction_range(
    loss_fraction: float,
    vcfg: ValidationConfig,
) -> bool:
    return (vcfg.loss_fraction_min <= loss_fraction <= vcfg.loss_fraction_max)


def is_mass_balance_ok(
    injected_kg: float,
    withdrawn_kg: float,
    losses_kg: float,
    delta_storage_kg: float,
    vcfg: ValidationConfig,
) -> bool:
    """
    Return True if mass-balance residual is within configured tolerance.
    """
    residual = mass_balance_residual_fraction(
        injected_kg, withdrawn_kg, losses_kg, delta_storage_kg
    )
    return residual <= vcfg.mass_balance_tolerance_fraction
