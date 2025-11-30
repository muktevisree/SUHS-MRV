# SUHS-MRV Changelog

This file tracks notable changes to the SUHS-MRV repository and dataset.

---

## v2.0 – Synthetic UHS Dataset Refresh

**Date:** 2025-11-30  
**Status:** Current version

- Reworked dataset generator (`src/generator.py`) to use a clearer, config-driven architecture.  
- Added physics helper module (`src/physics.py`) to centralize thermodynamic, loss, and purity calculations.  
- Introduced `config/uhs_config.yaml` as the single source of truth for generation parameters.  
- Implemented realistic injection/withdrawal cycle logic with ramping and capacity caps.  
- Added explicit working-gas purity tracking and MRV mass-balance residual computation.  
- Generated new v2.0 CSV outputs under `data/generated/`.  
- Expanded documentation in `docs/`:
  - `modeling_overview.md`  
  - `uhs_physics_model.md`  
  - `schema_mapping_ofp_osdu.md`  
  - `usage_examples.md`  
  - `data_dictionary.md`  
  - `evaluation_metrics.md`  
  - `model_architecture.md`  
  - `dataset_release_notes.md`  
  - `validation_checks.md`  
  - this `changelog.md`.

---

## v1.x – Legacy UHS Dataset (Archived)

- Earlier experimental versions of the UHS dataset and scripts.  
- Any retained files should be treated as historical and not used for new work.
- All older files are moved to legacy folders respectively 

---
