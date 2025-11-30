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

---

# 4. Loss Models

Underground hydrogen storage experiences two major categories of losses:

## **4.1 Static Losses**
Represent persistent micro-leakage or cushion gas interactions.

Model:

\[
L_{\text{static}} = k_s \cdot m_{\text{working}}
\]

- **k_s** sampled from YAML distribution  
- Represents 0.01–0.05% of mass per time-step typically  
- More important for long-term storage

## **4.2 Dynamic Losses**
Generated during pressure/temperature cycling.

Model:

\[
L_{\text{dynamic}} = f(m_{\text{working}}, \Delta P, \Delta T)
\]

Implemented via:

```python
dynamic_losses_kg = compute_cycle_losses_kg(working_gas_kg, loss_fraction)

Loss fraction sampled from YAML to emulate:
	•	Valves
	•	Line-pack disturbances
	•	Mixing inefficiencies
	•	Temperature swings

**5. Purity Tracking Model**

Purity in/out is computed using a dual-process model:

Inlet purity

Randomly sampled: inlet_purity = sample_inlet_purity_pct(cfg, rng)

Outlet purity

Outlet purity depends on:
	•	Current working gas purity
	•	Inlet purity
	•	Injection/withdrawal ratio
	•	Temperature & pressure

Model:

[
\text{purity}{\text{out}} = f(\text{purity}{\text{working}}, m_{\text{inj}}, m_{\text{wd}})
]

Implemented as:
outlet_purity = update_purity_out_pct(
    working_purity_pct,
    inlet_purity_pct,
    injected_mass_kg,
    withdrawn_mass_kg,
    cfg
)

Working gas purity update

After each cycle:

[
\text{working_purity}_{t+1} =
\text{weighted mean of (previous purity, inlet purity)}
]

This ensures impurity buildup over cycles, matching actual UHS behavior.

**6. MRV: Mass-Balance Validation**

The MRV residual quantifies model accuracy:

[
\text{residual} =
\frac{m_{t+1} - (m_t + m_{\text{inj}} - m_{\text{wd}} - L_s - L_d)}{m_{\text{capacity}}}
]

Values are normally in:
	•	10⁻⁶ – 10⁻⁴ range for stable operations
	•	Any value > 1e-3 indicates anomaly conditions (kept for realism)

---


**# 7. Injection/Withdrawal Cycle Simulation**

Each facility is simulated across multiple cycles.

### **7.1 Cycle direction modes**

- injection_heavy  
- withdrawal_heavy  
- balanced  

### **7.2 Cycle fraction dynamics**

The engine enforces:

- Random walk variations  
- Hard caps: **0.1 ≤ cycle_fraction ≤ 0.9**  
- Maximum per-cycle injection/withdrawal ≤ **25% capacity**

### **7.3 Time resolution**

Configured in YAML:

frequency: weekly → W
frequency: daily  → D
frequency: monthly → MS

Converted via:

```python
FREQ_MAP = {"weekly": "W", "daily": "D", "monthly": "MS"}

**8. Alignment with OFP & OSDU**

Every field is aligned to:

✔ OFP (Open Footprint)
	•	Working gas mass
	•	Losses
	•	Purity
	•	MRV residuals

✔ OSDU WKS/WKE
	•	Facility metadata
	•	Reservoir parameters
	•	Temperature & pressure
	•	Production + injection records

This ensures interoperability with:
	•	OSDU Core Services
	•	OFP MRV Engines
	•	Digital twins
	•	ESG reporting pipelines

⸻

✔ End of Document
