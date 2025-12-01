
# SUHS-MRV Example Data

This folder contains **tiny illustrative subsets** of the main SUHS-MRV dataset.

These files are optional and exist to support:
- Tutorials  
- Documentation examples  
- Small test cases  
- Workshops or demos  

---

## Suggested Example Files

### **example_facility_timeseries_UHS_001.csv**
A short time slice for a single facility.

### **example_cycle_summary_UHS_001.csv**
First few cycles for the same facility.

### **example_facility_metadata.csv**
Small subset of multiple facility configurations.

---

## How Example Files Should Be Created

Example datasets should be:
- Derived from outputs under `data/generated/`  
- Small enough to inspect quickly  
- Synchronized with schema definitions in:
  - `docs/data_dictionary.md`
  - `docs/schema_mapping_ofp_osdu.md`

These examples are optional but useful for onboarding new users quickly.
