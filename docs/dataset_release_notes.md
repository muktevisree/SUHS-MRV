# SUHS-MRV Dataset – Release Notes

## Version: v2.0  
Last Updated: 2025-11-30  
Maintainer: Sreekanth Muktevi

---

## 1. Overview

SUHS-MRV (Synthetic Underground Hydrogen Storage – Measurement, Reporting & Verification) is a fully synthetic, physics-informed dataset for UHS facilities. Version 2.0 is the current, QA’d version used in the GitHub repository.

---

## 2. What’s New in v2.0

- **New generator implementation**
  - Reworked `src/generator.py` for clarity, reproducibility, and easier review.  
  - Structured around explicit configuration, physics helpers, and facility-level simulation.

- **Config-driven design**
  - All key parameters now live in `config/uhs_config.yaml` (facility counts, physics, losses, purity, validation settings).  
  - Easier to document how data are generated and to tweak scenarios.

- **Improved physics layer**
  - Centralized thermodynamic and loss functions in `src/physics.py`.  
  - Clear separation between mass/pressure relationships, loss models, and purity tracking.

- **Operational realism**
  - Injection/withdrawal cycles constrained with:
    - Random-walk cycle fractions with ramping limits.  
    - Hard cap of ≤ 25% of working capacity per cycle.  
    - Distinct modes: `injection_heavy`, `withdrawal_heavy`, `balanced`.

- **Purity and MRV tracking**
  - Explicit working-gas purity state updated every cycle.  
  - Mass-balance residuals computed per step to support MRV diagnostics.

- **Documentation overhaul**
  - New docs in `docs/`:
    - `modeling_overview.md`  
    - `uhs_physics_model.md`  
    - `schema_mapping_ofp_osdu.md`  
    - `usage_examples.md`  
    - `data_dictionary.md`  
    - `evaluation_metrics.md`  
    - `model_architecture.md`  
    - `dataset_release_notes.md` (this file)

---

## 3. Dataset Contents

v2.0 generates three primary CSV files under `data/generated/`:

1. **`facility_metadata.csv`**  
   - One row per facility.  
   - Geometry, depth, pressure envelopes, capacity, basic rock/reservoir parameters, facility type.

2. **`facility_timeseries.csv`**  
   - One row per facility per time step.  
   - Working inventories, injection/withdrawal rates, temperature, pressure, purity, losses, residuals, and flags.

3. **`cycle_summary.csv`**  
   - Aggregated per-cycle metrics.  
   - Total injected/withdrawn mass, total losses, average pressure/temperature, cycle efficiency.

---

## 4. Backwards Compatibility

- v2.0 is conceptually aligned with earlier SUHS work but is **not** guaranteed to be drop-in compatible with any legacy CSVs.  
- Legacy artifacts (if retained) should be treated as historical and are not recommended for new work.

---

## 5. Reproducibility

- Generation is controlled via a random seed in `config/uhs_config.yaml`.  
- Using the same:
  - configuration file,  
  - code version, and  
  - random seed  
  should regenerate the same dataset.

---

## 6. Known Limitations

- Physics is intentionally simplified for explainability and speed; this is not a full reservoir simulation model.  
- Focus is on UHS operations and MRV, not detailed geomechanics or multi-phase flow.  
- OFP / OSDU mappings cover the most relevant entities but are not exhaustive.

---

## 7. Planned Enhancements

Possible future work:

- Additional facility types and stress-test scenarios.  
- Extended schema mappings (more OSDU WKEs and OFP entities).  
- Example integrations with validator tools and SynData-ESG modules.  
- Optional noise models for sensor failures and reporting gaps.

---
