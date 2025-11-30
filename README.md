# Synthetic Underground Hydrogen Storage MRV Dataset (SUHS-MRV)
### Version 2.0 – Fully QA-Checked (November 2025)

The **SUHS-MRV** dataset is an open, synthetic, and standards-aligned dataset designed for research, digital MRV workflows, and data-science applications in **Underground Hydrogen Storage (UHS)**.  
This dataset aligns explicitly with:

- **Open Footprint (OFP) Well-Known Schemas**  
- **Open Subsurface Data Universe (OSDU) WKS/WKE standards**  
- MRV principles for hydrogen storage projects  
- FAIR data practices  
- Reproducible scientific computing

This version (v2.0) includes **fully rewritten and validated synthetic data**, reflecting corrected physics models, stable randomness, and reviewer-aligned data ranges.

---

## 🔥 What’s New in v2.0 (2025)
- Rebuilt generator with strict physics validation  
- Stable configuration using `uhs_config.yaml`  
- Corrected injection/withdrawal logic  
- Clean working-gas inventory dynamics  
- Updated purity and loss modeling  
- All indentation and Python import issues resolved  
- Fully deterministic run using Numpy `Generator(seed)`  
- Generated 100% clean CSV files:
  - `facility_metadata.csv`
  - `facility_timeseries.csv`
  - `cycle_summary.csv`

---

## 📁 Repository Structure
SUHS-MRV/
│
├── src/
│   ├── generator.py
│   ├── physics.py
│   ├── utils.py
│   └── validation.py
│
├── config/
│   └── uhs_config.yaml
│
├── data/
│   └── generated/
│       ├── facility_metadata.csv
│       ├── facility_timeseries.csv
│       └── cycle_summary.csv
│
├── docs/
│
├── notebooks/
│
├── requirements.txt
├── CITATION.cff
├── LICENSE.txt
└── README.md

---

## 🧪 Dataset Outputs (Three CSVs)

### 1. **facility_metadata.csv**
One row per UHS facility. Includes:
- Facility ID  
- Type (salt cavern / depleted reservoir)  
- Depth  
- Temperature  
- Pressure min/max  
- Working gas capacity  
- Cushion gas  
- Porosity / permeability (for porous reservoirs)  
- Volume model used  

### 2. **facility_timeseries.csv**
Weekly time-series data:
- Pressure (MPa)  
- Temperature (°C)  
- Working gas mass (kg)  
- Hydrogen injected / withdrawn (kg)  
- Dynamic losses  
- Static losses  
- Purity in / purity out  
- Mass-balance residual indicator  

### 3. **cycle_summary.csv**
Per-cycle aggregated performance:
- Total injection/withdrawal  
- Losses  
- Average pressure  
- Average temperature  
- Efficiency  
- Start/end timestamps  

---

## 🧠 Scientific Basis & Modeling

The dataset uses:
- **Realistic thermodynamics** (ideal gas with custom tweak parameters)  
- **Temperature gradient modeling**  
- **Dynamic & static losses**  
- **Purity-in / purity-out modeling**  
- **Mass-balance validation**  
- **Cycle-based operational patterns**  

---

## 🔧 How to Run Locally (Python)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m src.generator

Output CSVs appear under: data/generated/

---

## 🎯 Standards Alignment

### OSDU WKS/WKE Mapping  
Fields are mapped to:
- `WKS:master-data–Facility`
- `WKS:master-data–Asset`
- `WKE:Well`
- `WKE:ProductionData`
- `WKE:Measurement`

### OFP Emissions Model Mapping  
Includes:
- Energy use  
- Compression losses  
- Leakage models  
- MRV-ready fields

All mappings are described in `docs/`.

---

## 📚 Citation

If you use SUHS-MRV, cite:
Muktevi, S. (2025).
Synthetic Underground Hydrogen Storage MRV Dataset (SUHS-MRV) v2.0.
GitHub Repository: https://github.com/muktevisree/SUHS-MRV

IEEE Data Descriptions submission is planned for Dec 2025.

---

## 📄 License
MIT License – free for research, education, commercial, and derivative use.

---

## 🧩 Future Releases

- v2.1 – Add visual analytics notebook  
- v3.0 – Multi-facility MRV integration  
- v3.5 – Spatial GIS model (shapefiles + GeoJSON)  

---

## 🤝 Contributions Welcome
Pull requests, issues, and improvements are invited.
