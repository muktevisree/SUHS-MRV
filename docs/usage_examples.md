**Usage Examples**

**SUHS–MRV Dataset (v2.0)**

This document provides practical examples for reading, analyzing, validating, and visualizing the SUHS-MRV synthetic Underground Hydrogen Storage dataset.

The examples use Python, Pandas, and Matplotlib, but the dataset is tool-agnostic and can be used with R, Matlab, Excel PowerQuery, Polars, Spark, or any data platform.

⸻

**1. Loading the Dataset**

1.1 Load all CSV files

import pandas as pd

facility = pd.read_csv(“data/generated/facility_metadata.csv”)
ts = pd.read_csv(“data/generated/facility_timeseries.csv”)
cycles = pd.read_csv(“data/generated/cycle_summary.csv”)

print(facility.head())
print(ts.head())
print(cycles.head())

⸻

**2. Filtering Time Series by Facility**

2.1 Select a single facility

facility_id = “FAC-001”
ts_f1 = ts[ts[“facility_id”] == facility_id]

print(ts_f1.head())

⸻

**3. Plot Pressure vs Time**

import matplotlib.pyplot as plt

f = ts_f1

plt.figure(figsize=(12,5))
plt.plot(f[“timestamp”], f[“pressure_mpa”])
plt.title(“Pressure (MPa) vs Time”)
plt.xlabel(“Date”)
plt.ylabel(“Pressure (MPa)”)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

⸻

**4. Plot Injection & Withdrawal**

plt.figure(figsize=(12,5))
plt.plot(f[“timestamp”], f[“h2_injected_kg”], label=“Injected”)
plt.plot(f[“timestamp”], f[“h2_withdrawn_kg”], label=“Withdrawn”)
plt.legend()
plt.title(“Injection/Withdrawal Profile”)
plt.xlabel(“Date”)
plt.ylabel(“Mass (kg)”)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

⸻

**5. MRV Mass-Balance Residual Analysis**

5.1 Identify high residuals

high_residuals = f[f[“mrv_residual”] > 1e-3]
print(high_residuals)

5.2 Histogram

f[“mrv_residual”].hist(bins=50)

⸻

**6. Purity Analysis**

6.1 Plot purity over time

plt.figure(figsize=(12,5))
plt.plot(f[“timestamp”], f[“h2_working_purity_pct”])
plt.title(“Working Gas Purity (%) Over Time”)
plt.xlabel(“Date”)
plt.ylabel(“Purity (%)”)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

6.2 Detect purity degradation

impurity_df = f[f[“h2_working_purity_pct”] < 98.0]
print(impurity_df)

⸻

**7. Cycle Summary Examples**

7.1 Injection/Withdrawal Efficiency

cycles[“efficiency_ratio”] = (
cycles[“total_withdrawn_kg”] /
(cycles[“total_injected_kg”] - cycles[“total_losses_kg”])
)

print(cycles[[“facility_id”, “cycle_index”, “efficiency_ratio”]].head())

⸻

**8. Facility-Level Analytics**

8.1 Compute average depth, porosity, temperature

facility[[“depth_m”, “porosity”, “base_temperature_c”]].describe()

8.2 Compare cavern vs porous reservoirs

facility.groupby(“facility_type”)[“working_capacity_kg”].mean()

⸻

**9. Merging Data for End-to-End Analysis**

merged = ts.merge(facility, on=“facility_id”, how=“left”)
merged = merged.merge(cycles, on=[“facility_id”, “cycle_index”], how=“left”)

print(merged.head())

⸻

**10. Querying for Anomalies**

10.1 High pressure anomaly

anomalies = merged[
(merged[“pressure_mpa”] > merged[“pressure_max_mpa”] * 0.95)
]

print(anomalies)

10.2 Negative efficiencies

bad_cycles = cycles[cycles[“cycle_efficiency”] < 0.85]
print(bad_cycles)

⸻

**11. Exporting Cleaned or Filtered Subsets**

11.1 Export a single facility

ts_f1.to_csv(“facility_FAC001_timeseries.csv”, index=False)

11.2 Export anomaly-only dataset

anomalies.to_csv(“anomalies.csv”, index=False)

⸻

**12. Using with OSDU or OFP Pipelines**

12.1 OSDU

The dataset maps directly to OSDU WKS/WKE:
	•	Measurement
	•	ProductionData
	•	Facility master data
	•	Temperature/Pressure data

You can convert the CSV to JSON via:

facility.to_json(“facility.json”, orient=“records”)

12.2 OFP

OFP requires:
	•	working_gas_mass
	•	losses
	•	purity
	•	MRV residuals

These fields are already included in timeseries.

⸻

**13. Using with ML / Forecasting**

13.1 Build a simple LSTM model

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

model = Sequential()
model.add(LSTM(64, input_shape=(seq_len, num_features)))
model.add(Dense(1))
model.compile(optimizer=“adam”, loss=“mse”)

⸻

**14. Notebook Integration**

Recommended structure:

notebooks/
├── 01_exploration.ipynb
├── 02_pressure_prediction.ipynb
├── 03_purity_forecasting.ipynb
└── 04_mrv_validation.ipynb

These can be created using Jupyter, VSCode, or Databricks.

⸻
