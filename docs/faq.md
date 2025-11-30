# SUHS-MRV – Frequently Asked Questions (FAQ)

---

## 1. What is SUHS-MRV?

SUHS-MRV is a **synthetic**, physics-informed dataset that represents underground hydrogen storage (UHS) operations along with measurement, reporting, and verification (MRV) signals. It is intended for research, prototyping, and demonstrations where real data are unavailable or restricted.

---

## 2. What files does the dataset include?

Under `data/generated/` you will find:

- `facility_metadata.csv` – one row per facility.  
- `facility_timeseries.csv` – time-step-level operational data.  
- `cycle_summary.csv` – per-cycle aggregates.

---

## 3. How do I regenerate the dataset?

1. Create and activate a Python virtual environment.  
2. Install dependencies:

   `pip install -r requirements.txt`

3. From the repo root, run:

   `python -m src.generator`

4. CSVs are written into `data/generated/`.

---

## 4. Can I change the number of facilities or simulation years?

Yes. Edit `config/uhs_config.yaml`:

- `global.n_facilities` – number of facilities.  
- `global.simulation.n_years` – duration of the simulation.  
- `global.simulation.time_step` – time-step frequency (`weekly`, `daily`, or `monthly`).

---

## 5. Is this a reservoir simulator?

No. The model is **physics-informed**, but simplified for transparency and speed. It is not a full reservoir simulation tool and should not be used for engineering design or safety-critical decisions.

---

## 6. How are losses and purity modeled?

- Losses are split into:
  - Static components (baseline leakage / micro-losses).  
  - Dynamic components (cycle-induced, pressure/temperature related).

- Purity is tracked as a working-state variable, updated each cycle using:
  - Inlet purity,  
  - Injection/withdrawal masses, and  
  - Simple mixing rules.

See `docs/uhs_physics_model.md` for details.

---

## 7. How is the dataset aligned with OFP and OSDU?

The dataset includes fields that map to:

- Open Footprint (OFP) concepts for inventories, flows, and MRV residuals.  
- OSDU master-data and time-series entities for facilities, wells, and measurements.

Mappings are documented in `docs/schema_mapping_ofp_osdu.md`.

---

## 8. What license applies?

The project’s official license is defined in `LICENSE.txt` at the repository root. That file is the authoritative source for terms of use.

---

## 9. Can I use SUHS-MRV in a publication or demo?

In general, yes—subject to the conditions in `LICENSE.txt`. When possible, please:

- Cite the GitHub repository.  
- Cite any associated publications or technical reports describing the dataset.

---

## 10. How can I report issues or suggest improvements?

- Open a GitHub Issue with:
  - SUHS-MRV version (e.g., v2.0),  
  - Python version and OS,  
  - Steps to reproduce the problem or a minimal notebook,  
  - Any error messages or stack traces.

---
