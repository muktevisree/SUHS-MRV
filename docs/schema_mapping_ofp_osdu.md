# Schema Mapping: OFP & OSDU Alignment for SUHS-MRV
Version: v2.0  
Last Updated: 2025-11-30  

The SUHS-MRV dataset aligns with:  
- **OFP (OpenFootprint™)** — ESG/MRV reporting  
- **OSDU™ Well-Known Schemas (WKS)** — subsurface & facility data  

All mappings below follow the updated OSDU standard (WKS-only, no WKE).

---

## 1. Facility Metadata Mapping

| SUHS Field | Description | OFP Field | OSDU WKS Field |
|-----------|-------------|-----------|----------------|
| facility_id | Unique facility ID | ofp:Facility.facilityId | master-data–Facility:id |
| country_code | ISO code | ofp:Facility.countryCode | master-data–Facility:country |
| reservoir_type | Cavern / Porous | N/A | master-data–Facility:facilityType |
| pore_volume_m3 | Effective pore volume | ofp:Storage.capacity | master-data–Facility:storageVolume |
| depth_m | Storage depth | N/A | master-data–Facility:depth |
| base_temperature_c | Surface temp | N/A | master-data–Facility:temperatureBase |
| temperature_gradient_c_per_km | Gradient | N/A | master-data–Facility:tempGradient |
| pressure_min_mpa | Minimum operational pressure | ofp:OperatingEnvelope.minPressure | master-data–Facility:pressureMin |
| pressure_max_mpa | Max operational pressure | ofp:OperatingEnvelope.maxPressure | master-data–Facility:pressureMax |
| working_gas_capacity_kg | Max working gas | ofp:Storage.capacityMass | N/A |

---

## 2. Time-Series Mapping

| SUHS Field | Description | OFP Field | OSDU WKS Field |
|-----------|-------------|-----------|----------------|
| timestamp | Time index | ofp:Observation.observedAt | common:Timestamp |
| temperature_c | Reservoir temp | ofp:Observation.temperature | work-products–Measurement:temperature |
| pressure_mpa | Reservoir pressure | ofp:Observation.pressure | work-products–Measurement:pressure |
| working_gas_kg | Mass in storage | ofp:Inventory.mass | productionData:massInStorage |
| h2_injected_kg | Injected hydrogen | ofp:Flow.inletMass | productionData:injectionMass |
| h2_withdrawn_kg | Withdrawn hydrogen | ofp:Flow.outletMass | productionData:withdrawalMass |
| static_losses_kg | Leakage/static losses | ofp:Loss.staticLoss | measurement:lossStatic |
| dynamic_losses_kg | Cycling losses | ofp:Loss.dynamicLoss | measurement:lossDynamic |
| inlet_purity_pct | Input purity | ofp:Composition.inletPurity | fluidSample:purityIn |
| outlet_purity_pct | Output purity | ofp:Composition.outletPurity | fluidSample:purityOut |
| working_purity_pct | Purity of stored gas | ofp:Composition.massFraction | fluidSample:purityWorking |
| mrv_residual_frac | Mass-balance residual | ofp:Verification.massBalanceResidual | N/A |

---

## 3. Cycle Summary Mapping

| SUHS Field | Description | OFP Field | OSDU WKS Field |
|------------|-------------|-----------|----------------|
| cycle_index | Cycle number | ofp:Cycle.index | operations:cycleNumber |
| h2_injected_kg | Injection total | ofp:Flow.inletMass | productionData:injectionMass |
| h2_withdrawn_kg | Withdrawal total | ofp:Flow.outletMass | productionData:withdrawalMass |
| dynamic_losses_kg | Dynamic losses | ofp:Loss.dynamicLoss | measurement:lossDynamic |
| static_losses_kg | Static losses | ofp:Loss.staticLoss | measurement:lossStatic |
| working_purity_pct | Avg purity | ofp:Composition.massFraction | fluidSample:purityWorking |
| outlet_purity_pct | Purity at withdrawal | ofp:Composition.outletPurity | fluidSample:purityOut |
| mrv_residual_frac | Residual | ofp:Verification.massBalanceResidual | N/A |

---

## 4. Notes on Alignment

### OSDU:
- Conforms **exclusively** to modern WKS (no deprecated WKE).  
- Measurement and Production schemas follow SCCS-MRV IEEE paper structure.  
- Metadata cleanly maps to master-data–Facility.

### OFP:
- All MRV fields aligned with OpenFootprint™ Measurement Reporting standard.  
- Mass balance, losses, purity and flows map 1:1.

---

## 5. Summary

This mapping ensures SUHS-MRV is fully compatible with:  
- ESG reporting engines  
- OSDU subsurface data platforms  
- Digital twins  
- MRV pipelines  

