# Synthetic UHS–MRV Dataset for OFP–OSDU Integration in Hydrogen Storage Reporting (SUHS-OFPOSDU)

## Authors
- **Sreekanth Muktevi**  
- **Yogesh Nagpal** 
- **Rajesh Leela Thotakura**  
- **Jyotsna Muktevi** 

---

## Abstract / Overview
This dataset represents, to the best of our knowledge, the **first publicly available synthetic Underground Hydrogen Storage (UHS) dataset** explicitly mapped to both the **Open Footprint (OFP) model** and the **Open Subsurface Data Universe (OSDU) schemas**.  
It was developed to fill a critical gap by enabling **interoperability testing, MRV (Measurement, Reporting, and Verification) prototyping, and ESG reporting validation** for hydrogen storage systems in the energy sector.  

The dataset includes **annual, daily, and monthly injection/withdrawal records** across 10 synthetic facilities with realistic reservoir-specific behavior, energy use, and mass balance validation.  
All values are **synthetically generated** but follow realistic industry ranges and relationships, supporting reproducible research while avoiding confidentiality issues.  

---

## Background & Motivation
- **Hydrogen today**: widely used in refining, ammonia/fertilizer, methanol, and chemicals, with pilots in steel, mobility, and power.  
- **Why UHS**: enables seasonal storage of hydrogen, balancing renewable energy and ensuring industrial continuity.  
- **Maturity**:  
  - Salt caverns → operational today (commercial use in US & EU).  
  - Depleted gas fields / saline aquifers → pilot / feasibility studies only.  
- **Why synthetic data**:  
  - Real-world UHS data is **confidential or unavailable**.  
  - Standards (OFP, OSDU, OGMP) are evolving faster than commercial deployment.  
  - Synthetic datasets provide a **safe, standards-aligned testbed** for system development, research, and training.  

---

## Dataset Contents
- `data/uhs_full_dataset_v1.0.csv` – Facility-level annual summary (10 facilities, QA-checked).  
- `data/uhs_daily_v1.0.csv` – Daily injection/withdrawal with seasonality.  
- `data/uhs_monthly_v1.0.csv` – Monthly roll-up from daily.  
- `schema/schema.yaml` – Dataset schema definition.  
- `schema/schema_crosswalk.csv` – Field-to-OFP/OSDU/MRV mapping.  
- `docs/NOTES.md` – Methodology and QA validation rules.  
- `LICENSE.txt` – License (CC BY 4.0).  
- `CITATION.cff` – Citation metadata.  

---

“Annual file start/end dates represent the reporting year (2024). Daily and monthly tables provide the actual time series of injection/withdrawal activities within this period.”

---
## Schema Alignment
This dataset has been explicitly mapped to the OFP emissions model and to publicly available OSDU Well-Known Schemas (WKS) and Well-Known Entities (WKE), including:

- **WKS:master-data–Facility** → `facility_id`, `country_code`, `lat`, `lon`, `reservoir_type`  
- **WKS:master-data–Asset** → `capture_tech`, `pipeline_length_km`, `transport_mode`  
- **WKE:Wellbore / Well** → `well_id`, `injection_start_date`, `injection_end_date`, `avg_reservoir_pressure_MPa`, `avg_reservoir_temp_C`  
- **WKE:ProductionData** → `h2_injected_tonnes`, `h2_withdrawn_tonnes`, `methane_co_produced_tonnes`  
- **WKE:Measurement** → `h2_cushion_gas_tonnes`, `compression_energy_MWh`, `h2_losses_tonnes`  
- **WKE:Event / Method** → `leak_events_count`, `leak_mass_tonnes`, `mmv_methods`, `ogmp_source_category`  
- **(Proposed) EnvironmentalData extension** → `h2_net_stored_tonnes`  

---

## QA & Validation Rules
- **Mass balance:** `net = injected − withdrawn − losses ≥ 0`.  
- **Additivity:** daily & monthly totals = annual.  
- **Reservoir-specific logic:**  
  - Salt cavern → low losses (0.05–0.5%), high cycling, cushion gas constant.  
  - Depleted gas → moderate losses (0.1–1%), methane co-production possible.  
  - Saline aquifer → higher uncertainty, losses (0.2–1.5%).  
- **Energy intensity:** compression energy / tonne-cycle ∈ 0.1–0.5 MWh/t-cycle.  
- **Leak logic:** 0 events ⇒ 0 leak mass; >0 events ⇒ leak mass >0.  
- **Transport coherence:** pipeline mode requires pipeline length >0, non-pipeline ⇒ length=0.  
- **Geo/date checks:** coordinates in US bounds; dates within 2024.  

---

## Intended Uses
- UHS MRV reporting system prototyping.  
- Data model integration testing between OFP and OSDU.  
- Benchmarking analytics pipelines for hydrogen storage.  
- Academic research, teaching, and training.  

---

## Coordinates Disclaimer
All latitude/longitude values are **synthetic**, generated randomly within U.S. bounds. They do **not** represent real UHS sites.  

---

## Licensing & Citation
- Licensed under **Creative Commons CC BY 4.0**.  
- Users are free to share and adapt with appropriate credit.  

**Citation:**  
Muktevi, S., Nagpal, Y., Thotakura, R. L., & Muktevi, J. (2025). *Synthetic UHS–MRV Dataset for OFP–OSDU Integration in Hydrogen Storage Reporting (SUHS-OFPOSDU)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.TBD  

---

## Disclaimer
This dataset is entirely **synthetic** and does not represent any real company, facility, or reservoir data.  
Salt cavern examples reflect **commercial practice**, while depleted gas and saline aquifer examples are based on **pilot / feasibility scenarios**.  
The dataset is provided solely for **educational, research, and development purposes**.  

---