# SUHS–MRV Dataset  
## Modeling & Simulation Overview  
Version: v2.0  
Last Updated: 2025-11-30  
Author: Sreekanth Muktevi

This document describes the physics-based modeling framework used to generate the SUHS-MRV (Synthetic Underground Hydrogen Storage – Measurement, Reporting & Verification) dataset. It includes:

1. Thermodynamic model  
2. Pressure–volume–temperature (PVT) relationships  
3. Temperature noise model  
4. Static & dynamic loss models  
5. Purity tracking model  
6. MRV mass-balance validation  
7. Injection/withdrawal cycle simulation  
8. Notes on alignment with OFP & OSDU schemas  

The modeling logic is identical to the version accepted by _IEEE Data Descriptions_ for SCCS-MRV and adapted for UHS.

---

# 1. Thermodynamic Model

A simplified but physically realistic H₂ storage thermodynamic model is used.

### **Temperature computation**
Temperature evolves as:

\[
T_c = T_\text{base} + (z \cdot \text{gradient}_{C/km}) + \epsilon_t
\]

Where:

- **T_base**: temperature at surface  
- **z**: depth in km  
- **gradient**: geothermal gradient  
- **εₜ**: random temperature perturbation from the noise model  

This ensures temperature varies smoothly across the depth of each facility.

### **Pressure from mass**
Pressure is computed using a linearized PVT model:

\[
P_{\text{MPa}} = P_{\min} + (P_{\max} - P_{\min}) \cdot \frac{m_{\text{working}}}{m_{\text{capacity}}}
\]

This preserves the monotonic relationship of mass ↔ pressure without requiring a full EOS.

---

# 2. PVT Behavior & Working Gas Evolution

The **working gas mass** inside the facility is updated each time-step using:

\[
m_{t+1} = m_t + m_{\text{inj}} - m_{\text{wd}} - L_{\text{static}} - L_{\text{dynamic}}
\]

Key aspects:

- Mass never drops below 0.  
- Mass never exceeds **working_gas_capacity_kg**.  
- Injection/withdrawal rates are capped at **≤25%** of capacity per cycle.

This ensures realistic operational constraints.

---

# 3. Temperature Noise Model

Temperature is perturbed with Gaussian noise:

\[
\epsilon_t \sim \mathcal{N}(0, \sigma_T)
\]

Where **σ_T** comes from YAML config.  
Noise affects:

- Computed pressure  
- Density relationships  
- Purity degradation rates (small effect)
