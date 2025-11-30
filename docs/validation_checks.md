# SUHS-MRV Validation Checks

Version: v2.0  
Last Updated: 2025-11-30

This document summarizes recommended validation checks for the SUHS-MRV dataset. They can be implemented with `src/validation.py` or directly in notebooks.

---

## 1. File-Level Checks

1. **Presence of generated CSVs**

   Confirm that these exist under `data/generated/`:

   - `facility_metadata.csv`  
   - `facility_timeseries.csv`  
   - `cycle_summary.csv`

2. **Row-count sanity**

   - Each `facility_id` in `facility_metadata.csv` should appear in the other two files.  
   - Number of unique `facility_id` values should match across the three files.

---

## 2. Schema & Type Checks

- All required columns documented in `docs/data_dictionary.md` should be present.  
- Data types should be consistent:

  - IDs as strings or integers.  
  - Timestamps as datetime types.  
  - Pressures, temperatures, masses, losses, purity as numeric.

---

## 3. Range & Domain Checks

Recommended numeric checks:

- **Mass & inventory**
  - `working_gas_kg >= 0`  
  - `cushion_gas_kg >= 0`  
  - `injected_kg >= 0`  
  - `withdrawn_kg >= 0`  
  - `losses_kg >= 0`

- **Capacity constraints**
  - `working_gas_kg <= working_gas_capacity_kg` for all timesteps.  
  - Per-cycle injected and withdrawn mass ≤ 25% of `working_gas_capacity_kg`.

- **Pressure & temperature**
  - `pressure_mpa` within `[pressure_min_mpa, pressure_max_mpa]` from metadata.  
  - `temperature_c` within a reasonable band around base temperature + gradient.

- **Purity**
  - `0.0 <= purity_pct <= 100.0`

---

## 4. Logical Consistency Checks

Examples:

- When both `injected_kg` and `withdrawn_kg` are zero, changes in `working_gas_kg` should mainly come from losses.  
- When `injected_kg` is large relative to capacity, pressure should increase for that step.  
- When `withdrawn_kg` is large, pressure should not increase without a clear reason.

---

## 5. Mass-Balance Residuals

The MRV residual is expected to be close to zero for normal operation:

```text
residual = (m_new - (m_prev + inj - wd - static_losses - dynamic_losses)) / max(capacity, eps)

Use residuals to:
	•	Compute summary statistics per facility (mean, median, percentiles).
	•	Flag facilities or time ranges where abs(residual) exceeds a chosen threshold.

⸻

**6. Cross-File Consistency**

For each facility_id and cycle_index:
	•	Aggregates of facility_timeseries.csv over the cycle should approximately match values in cycle_summary.csv
(e.g., total injected mass vs. total_injected_kg).

Small differences can arise from rounding.

⸻

**7. Reproducibility Checks**
	•	Re-run python -m src.generator with the same config and seed.
	•	Confirm that resulting CSVs match previous ones (e.g., via checksums or diff).

⸻

**8. Notebook Support**

03_validate_uhs_dataset.ipynb (or an equivalent notebook) can be used to:
	•	Run these checks interactively.
	•	Plot distributions for pressure, temperature, purity, losses, and residuals.
	•	Export summary validation reports if needed.
