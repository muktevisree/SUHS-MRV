# SUHS-MRV Model Architecture

Version: v2.0  
Last Updated: 2025-11-30

This document describes the internal architecture of the SUHS-MRV (Synthetic Underground Hydrogen Storage – Measurement, Reporting & Verification) dataset generator.

The codebase is organized into the following main layers:

1. **Configuration Layer** (`config/uhs_config.yaml`)  
2. **Physics Layer** (`src/physics.py`)  
3. **Generation Layer** (`src/generator.py`)  
4. **Validation Layer** (`src/validation.py`)  
5. **Utilities & Notebooks** (`src/utils.py`, `notebooks/`)

---

## 1. Configuration Layer

**File:** `config/uhs_config.yaml`

All high-level parameters used for dataset generation are defined in a single YAML file. This includes:

- Global settings (random seed, number of facilities, simulation start date and duration).  
- Facility type definitions (salt cavern, porous reservoir) and their distributions for depth, volume, pressures, etc.  
- Physics-related settings (temperature gradients, base temperatures).  
- Operational patterns (cycle modes, cycle fractions, ramping limits).  
- Loss, purity, and validation configuration blocks.

The YAML file is parsed at runtime and converted into typed configuration objects in `physics.py`.

---

## 2. Physics Layer (`src/physics.py`)

The physics layer holds small, composable functions that translate subsurface physics into simplified numerical models. It is deliberately lightweight so it can be ported to other codebases if needed.

Main responsibilities:

- Build configuration data classes from raw YAML  
  (`build_thermo_config`, `build_temperature_noise_config`,  
  `build_loss_config`, `build_purity_config`, `build_validation_config`).  
- Compute temperature at depth with geothermal gradient and noise (`compute_temperature_c`).  
- Convert between mass and pressure given volume and thermodynamic settings (`mass_from_pvt`, `pressure_from_mass`).  
- Sample loss fractions and compute static/dynamic losses (`sample_loss_fraction`, `compute_cycle_losses_kg`).  
- Sample inlet purity and update outlet/working purity (`sample_inlet_purity_pct`, `update_purity_out_pct`).  
- Compute mass-balance residual fractions (`mass_balance_residual_fraction`).

These functions do **not** depend on pandas; they only use NumPy and plain Python types.

---

## 3. Generation Layer (`src/generator.py`)

The generation layer orchestrates the full dataset creation process. It is responsible for:

1. **Loading configuration**  
   - `load_config()` reads `config/uhs_config.yaml` and returns a dictionary.

2. **Facility metadata generation**  
   - `generate_facility_metadata()` uses the YAML config and physics helpers to sample:
     - Facility-level geometry (depth, volume, porosity, etc.).  
     - Pressure and temperature envelopes.  
     - Working-gas and cushion-gas capacities.  
   - Output is a `pandas.DataFrame` written to `data/generated/facility_metadata.csv`.

3. **Time index construction**  
   - `_build_time_index()` converts user-friendly frequencies (`weekly`, `daily`, `monthly`) into pandas-compatible offsets (`W`, `D`, `MS`).  
   - Generates a common time index for all facilities over the requested number of years.

4. **Facility-level simulation**  
   - `simulate_facility()` is the main engine that:
     - Initializes inventories (working gas, cushion gas, purity).  
     - Iterates over time steps and assigns injection / withdrawal cycles.  
     - Computes injected/withdrawn mass with ramping and hard caps (≤ 25% of capacity per cycle).  
     - Applies static and dynamic loss models.  
     - Updates working gas and purity.  
     - Tracks mass-balance residuals and flags potential anomalies.  
   - Returns:
     - A per-timestep time series for the facility.  
     - A per-cycle summary table with totals and efficiencies.

5. **Dataset assembly and writing**  
   - `generate_uhs_dataset()` loops over all facilities, calls `simulate_facility()`, concatenates the results, and writes three CSVs:
     - `data/generated/facility_metadata.csv`  
     - `data/generated/facility_timeseries.csv`  
     - `data/generated/cycle_summary.csv`

End users typically only call `generate_uhs_dataset()` from Python or the notebooks.

---

## 4. Validation Layer (`src/validation.py`)

The validation layer provides reusable checks that can be run after dataset generation or embedded into notebooks:

- Schema and column checks (required columns present, dtypes consistent).  
- Basic range checks (pressures within configured envelopes, purity between 0–100%, non-negative masses).  
- Logical consistency checks (no negative working gas, inventories never exceed capacity).  
- Mass-balance diagnostics using residual fractions.  
- Simple aggregations to confirm that injection/withdrawal totals and losses remain in expected bands.

These utilities are intended for both internal QA and external reviewers.

---

## 5. Utilities & Notebooks

- **`src/utils.py`** contains helper functions that do not belong to the physics core (e.g., random seeding helpers, small plotting or aggregation utilities).  
- **`notebooks/`** currently includes, for example:
  - `01_generate_uhs_dataset.ipynb` – basic generation script and quick inspection.  
  - `02_explore_and_plot_uhs_dataset.ipynb` – exploratory plots and statistics.  
  - `03_validate_uhs_dataset.ipynb` – example validation workflow using `src/validation.py`.

Users can adapt these notebooks to their own UHS scenarios.

---

## 6. Relationship to OFP & OSDU

While SUHS-MRV is synthetic, its structure is aligned with:

- **Open Footprint (OFP)** concepts for inventories and MRV residuals.  
- **OSDU** master-data and production schemas for facilities, wells, and time-series measurements.

Mapping details are captured in `docs/schema_mapping_ofp_osdu.md`.

---
