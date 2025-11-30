SUHS–MRV Dataset

Modeling & Simulation Overview

Version: v2.0
Last Updated: 2025-11-30
Author: Sreekanth Muktevi

This document describes the physics-based modeling framework used to generate the SUHS-MRV (Synthetic Underground Hydrogen Storage – Measurement, Reporting & Verification) dataset. It expands the modeling published in the IEEE Data Descriptions SCCS-MRV paper and adapts the same rigor for hydrogen.

The framework covers:
	1.	Thermodynamic model
	2.	Pressure–volume–temperature behavior
	3.	Temperature noise model
	4.	Static and dynamic losses
	5.	Purity evolution model
	6.	MRV mass-balance validation
	7.	Injection/withdrawal cycle simulation
	8.	Alignment with OFP & OSDU schemas

⸻

1. Thermodynamic Model

1.1 Temperature

Temperature at depth is computed using:

Tc = T_base + (depth_km × gradient_C_per_km) + noise

Where:
	•	T_base = surface reference temperature
	•	depth_km = reservoir or cavern depth
	•	gradient = geothermal gradient
	•	noise = Gaussian perturbation from YAML config

This ensures realistic vertical and temporal variation.

1.2 Pressure

A linearized PVT model is used:

Pressure_MPa = P_min + (P_max − P_min) × (working_gas_mass / working_capacity)

This captures monotonic mass–pressure behavior without requiring a full EOS.

⸻

2. Working Gas Evolution

Working gas mass over time evolves as:

m_next = m_current + injection − withdrawal − static_losses − dynamic_losses

Model constraints:
	•	Mass never becomes negative
	•	Mass never exceeds working capacity
	•	Per-cycle injection/withdrawal ≤ 25% of capacity

These constraints ensure realistic cycle behavior.

⸻

3. Temperature Noise Model

Temperature noise follows:

Gaussian(mean=0, sigma=T_noise_sigma)

Effects:
	•	Slight pressure variability
	•	Small influence on purity changes
	•	Improves realism in cycle-to-cycle variation

Noise parameters come from YAML configuration.

⸻

4. Loss Models

4.1 Static Losses

Represent steady leakage or interaction with reservoir/cushion gas:

static_loss = k_static × working_mass

Where k_static is sampled from YAML (typically 0.01–0.05% of mass per time-step).

4.2 Dynamic Losses

Dynamic losses represent pressure and temperature cycling effects:

dynamic_loss = compute_cycle_losses_kg(working_mass, loss_fraction)

Loss fraction comes from YAML and simulates:
	•	Valve/line-pack disturbances
	•	Rapid pressure changes
	•	Mixing inefficiencies
	•	Thermal cycling effects

⸻

5. Purity Tracking Model

UHS purity evolves due to mixing, operational cycles, and inflow/outflow purity differences.

5.1 Inlet purity

Sampled using:
sample_inlet_purity_pct(cfg, rng)

5.2 Outlet purity

Outlet purity depends on:
	•	Working gas purity
	•	Inlet purity
	•	Injected and withdrawn mass
	•	Temperature and pressure

Logic is implemented via:
update_purity_out_pct(working, inlet, injected, withdrawn, cfg)

5.3 Working gas purity update

Working purity is updated as a weighted mixture of prior purity and inlet purity.
This produces impurity buildup over long-term storage cycles.

⸻

6. MRV Mass-Balance Validation

The mass-balance residual is:

residual = (actual_mass_change − expected_mass_change) / working_capacity

Typical values:
	•	1e-6 to 1e-4 → stable normal operations
	•	1e-3 → anomalies introduced for realism

Residuals appear in timeseries under MRV fields.

⸻

7. Injection/Withdrawal Cycle Simulation

7.1 Cycle modes

Three cycle modes are used:
	•	injection_heavy
	•	withdrawal_heavy
	•	balanced

7.2 Cycle fraction dynamics

Rules enforced:
	•	Random-walk evolution
	•	Cycle fraction constrained between 0.1 and 0.9
	•	Per-cycle injection/withdrawal ≤ 25% capacity

7.3 Time resolution

Configured via YAML:

weekly  → W
daily   → D
monthly → MS

Mapped internally as:
{“weekly”:“W”, “daily”:“D”, “monthly”:“MS”}

⸻

8. Alignment with OFP & OSDU

8.1 OFP (Open Footprint)

Dataset fields aligned with OFP include:
	•	Working gas mass
	•	Losses
	•	Purity
	•	MRV residual

8.2 OSDU

The dataset aligns with OSDU Well-Known Schemas (WKS / WKE):
	•	master-data–Facility
	•	master-data–Asset
	•	Wellbore / Well
	•	ProductionData
	•	Measurement

This enables seamless ingestion into:
	•	OSDU data platforms
	•	Digital twins
	•	ESG reporting systems
	•	OFP MRV engines

⸻

End of Document
