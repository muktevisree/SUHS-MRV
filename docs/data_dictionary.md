# SUHS–MRV Dataset — Complete Data Dictionary  
Version: v2.0  
Last Updated: 2025-11-30  
Author: Sreekanth Muktevi

This document provides a unified, reviewer-ready data dictionary for all files generated in the SUHS-MRV v2.0 dataset:

- `facility_metadata.csv`
- `facility_timeseries.csv`
- `cycle_summary.csv`

All fields follow:
- **SI units**
- **CSVs encoded in UTF-8**
- **OFP–OSDU mapping** (where applicable)

---

# 1. facility_metadata.csv

| Column | Description | Units | Example | OFP/OSDU Mapping |
|--------|-------------|--------|---------|-------------------|
| facility_id | Unique identifier for facility | string | UHS_001 | WKS:master-data–Facility.id |
| name | Human readable facility name | string | “UHS Salt Cavern 1” | WKS:master-data–Facility.name |
| country_code | ISO 3166 country code | string | US | WKS:master-data–Facility.country |
| lat | Latitude | decimal degrees | 29.76 | WKS:master-data–Facility.lat |
| lon | Longitude | decimal degrees | -95.36 | WKS:master-data–Facility.lon |
| facility_type | One of: `salt_cavern`, `depleted_reservoir`, `aquifer`, `porous_reservoir` | string | salt_cavern | WKE:Reservoir.type |
| porosity | Effective porosity (reservoir only) | fraction | 0.18 | WKE:Reservoir.porosity |
| permeability_mD | Permeability | mD | 65 | WKE:Reservoir.permeability |
| depth_m | Storage depth | meters | 900 | WKE:Well.depth |
| cavern_volume_m3 / pore_volume_m3 / reservoir_volume_m3 | Total usable storage volume | m³ | 450000 | WKE:Storage.volume |
| pressure_min_mpa | Minimum operating pressure | MPa | 5.0 | OSDU:PressureRange.min |
| pressure_max_mpa | Maximum operating pressure | MPa | 13.0 | OSDU:PressureRange.max |
| base_temperature_c | Temperature at reference depth | °C | 25 | OSDU:Temperature.base |
| temperature_gradient_c_per_km | Geothermal gradient | °C/km | 22 | OSDU:Temperature.gradient |
| working_gas_capacity_kg | Maximum usable H₂ storage | kg | 1.2e7 | OFP:workingGas.capacity |
| working_gas_fraction_of_pore_volume | Operational working gas fraction | fraction | 0.65 | — |
| darcy_injectivity | Injectivity index | kg/s/MPa | 2.8 | WKE:Injectivity.index |

---

# 2. facility_timeseries.csv

Each facility has a full time-series simulation of pressure, temperature, purity, and mass balance.

| Column | Description | Units | Example |
|--------|-------------|-------|---------|
| timestamp | ISO8601 timestamp | datetime | 2025-01-01T00:00:00Z |
| facility_id | FK to facility_metadata | — | UHS_001 |
| pressure_mpa | Storage pressure | MPa | 8.4 |
| temperature_c | Computed temperature | °C | 42 |
| working_gas_kg | Current H₂ mass in reservoir | kg | 4200000 |
| h2_injected_kg | Injected H₂ during this time step | kg | 12,500 |
| h2_withdrawn_kg | Withdrawn H₂ | kg | 9,500 |
| static_losses_kg | Per-period static losses | kg | 50 |
| dynamic_losses_kg | Cycle-related dynamic losses | kg | 35 |
| inlet_purity_pct | Purity of incoming hydrogen | % | 99.97 |
| outlet_purity_pct | Purity of delivered hydrogen | % | 99.92 |
| mass_balance_residual | Residual fraction from MRV mass-balance check | fraction | 0.00027 |

---

# 3. cycle_summary.csv

Summarizes every injection/withdrawal cycle for each facility.

| Column | Description | Units | Example |
|--------|-------------|--------|---------|
| facility_id | FK to facility_metadata | — | UHS_001 |
| cycle_id | Unique cycle identifier | integer | 14 |
| cycle_start | Start timestamp | datetime | 2025-02-01T00:00:00Z |
| cycle_end | End timestamp | datetime | 2025-02-07T00:00:00Z |
| injected_mass_kg | Total injected mass for cycle | kg | 52,000 |
| withdrawn_mass_kg | Total withdrawn mass | kg | 47,200 |
| max_pressure_mpa | Peak pressure in cycle | MPa | 9.8 |
| min_pressure_mpa | Minimum pressure | MPa | 7.1 |
| max_temperature_c | Peak temperature | °C | 46 |
| min_temperature_c | Minimum temperature | °C | 37 |
| cycle_static_losses_kg | Static losses accumulated | kg | 410 |
| cycle_dynamic_losses_kg | Pressure/temperature cycling losses | kg | 360 |
| avg_inlet_purity_pct | Average purity of injected H₂ | % | 99.96 |
| avg_outlet_purity_pct | Average outlet purity | % | 99.91 |
| mass_balance_residual | Overall MRV mass-balance deviation | fraction | 0.00033 |

---

# Notes on Validation

- All columns have been validated for missing data, correct units, and expected value ranges.
- All mass-balance fields are computed using the IEEE Data Descriptions–accepted `mass_balance_residual_fraction` logic.
- No columns have been removed or renamed from v1.0 to maintain backward compatibility.

---

# End of Document
