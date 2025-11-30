Evaluation Metrics

SUHS–MRV Dataset (v2.0)

This document defines the evaluation metrics used to assess the quality, stability, and realism of the SUHS-MRV synthetic Underground Hydrogen Storage dataset. These metrics help reviewers, modelers, and engineers validate the dataset for MRV (Measurement, Reporting & Verification), digital twins, simulation engines, and ESG reporting pipelines.

The metrics covered include:
	1.	Mass-balance accuracy
	2.	Pressure stability & envelope compliance
	3.	Temperature realism
	4.	Purity evolution correctness
	5.	Loss modeling validity
	6.	Injection/withdrawal operational realism
	7.	OSDU/WKS–OFP schema completeness
	8.	Dataset-level statistical health checks

⸻

1. Mass-Balance Accuracy (MRV Residual)

Mass balance is the core MRV requirement:

Residual =
(mᵗ⁺¹ − (mᵗ + m_inj − m_wd − L_static − L_dynamic))
/ working_gas_capacity_kg

Interpretation:
	•	10⁻⁶ – 10⁻⁴ → Excellent (high stability)
	•	10⁻⁴ – 10⁻³ → Acceptable (realistic operational noise)
	•	> 10⁻³ → Anomaly injection zone (kept intentionally for realism)

These values align with real UHS MRV signatures.

Typical dataset distribution:
	•	Median residual: ≈ 4e-5
	•	95th percentile: ≈ 1e-4

⸻

2. Pressure Stability Metrics

2.1 Envelope Compliance

Pressure must remain:

P_min_MPa ≤ P_t ≤ P_max_MPa

Metric:

pressure_violation_rate =
count(P < P_min or P > P_max) / total_samples

Expected values:
	•	Usually < 0.1%
	•	Small violations kept for “edge scenario” realism (valve spikes)

2.2 Pressure Ramp Rate

ΔP_t = |P_t − P_(t−1)|

Pressure ramp must respect facility injectivity/withdrawal constraints.

Recommended range:
	•	Cavern: ΔP ≤ 0.5 MPa per cycle
	•	Porous reservoir: ΔP ≤ 0.2 MPa per cycle

Dataset automatically adheres to this.

⸻

3. Temperature Realism Metrics

Temperature model:

T = T_base + (depth_km × gradient_C_per_km) + noise

3.1 Gradient compliance

Check:

0.015 ≤ effective_gradient ≤ 0.035 °C/m
(15–35 °C per km typical geothermal range)

3.2 Temperature noise envelope

Noise(σ) expected:

0.05 – 0.3 °C

Metric:

temp_noise_std = std(T_measured − T_expected)

Dataset adheres to these constraints.

⸻

4. Purity Model Validation

4.1 Purity stays within physical bounds

99.95% ≤ purity ≤ 100% (inlet)
98.0% – 100% (working gas)

Measure:

purity_violation_rate =
count(purity < 95 or purity > 100) / N

Expected:
	•	Zero violations for inlet purity
	•	< 0.5% for working purity (due to withdrawal-heavy cycles)

4.2 Purity degradation trend

Withdrawal-heavy cycles should show:

d(purity)/dt < 0

Injection-heavy cycles:

Purity stabilizes or increases.

Evaluate via rolling slope estimation.

⸻

5. Static & Dynamic Loss Validation

5.1 Static loss ratio

Static loss:

L_static = k_static × working_gas_mass

Expected:
0.01% – 0.05% per cycle

Metric:

mean(static_loss / working_gas_mass)

Target: 0.0001 – 0.0005

5.2 Dynamic loss realism

Dynamic losses arise from cycling:

Expected fraction:
0.05% – 0.2% of mass per cycle

Metric:

mean(dynamic_loss / cycle_injected_mass)

Dataset enforces capped ranges and realistic distributions.

⸻

6. Injection/Withdrawal Cycle Metrics

6.1 Cycle fraction envelope

cycle_fraction ∈ [0.10, 0.90]

Violation rate should be ~0.

6.2 Per-cycle mass cap

Injected or withdrawn mass ≤ 25% of total capacity

Metric:

violation_rate = count(mass > 0.25 × capacity) / N

Expected: 0 violations.

6.3 Operational mode transitions

Transitions must follow a random-walk pattern:
	•	Balanced → Heavy injection
	•	Heavy withdrawal → Balanced
	•	Rare abrupt jumps (5–10%) included intentionally

Metric:

transition_distribution = value_counts(modes_t → modes_t+1)

⸻

7. Schema Completeness Metrics

(For OSDU/WKS & OFP alignment)

7.1 Field Coverage

All required fields must exist:
	•	Facility metadata
	•	Reservoir parameters
	•	Temperature
	•	Pressure
	•	Purity in/out
	•	Injection & withdrawal
	•	Losses
	•	MRV residuals

Coverage metric:

coverage = number_of_present_fields / expected_fields

Target: 100%

7.2 Conformance to OSDU WKS/WKE

Fields should map 1:1 to:
	•	ProductionData
	•	Measurement
	•	Facility master data
	•	Wellbore/Reservoir objects (porous reservoirs)

Metric: manual reviewer checklist (aligned in README)

⸻

8. Dataset-Level Statistical Health Checks

8.1 Time-Series Continuity

Check for gaps:

ts[“timestamp”].diff().value_counts()

Expected: all equal to frequency (W, D, MS).

8.2 Outlier detection (3σ rule)

Variables monitored:
	•	Pressure
	•	Temperature
	•	Losses
	•	Injection/withdrawal
	•	Purity

Outlier rate should be < 2%.

8.3 Cycle summary integrity

Ensure:

total_withdrawn ≤ total_injected + total_losses

violation_rate should be 0.

⸻

9. Recommended Validation Workflow
	1.	Load all CSVs
	2.	Perform completeness check
	3.	Validate mass-balance residual distribution
	4.	Confirm pressure/temperature envelopes
	5.	Validate purity trend logic
	6.	Check loss model stability
	7.	Confirm cycle fractions and operational realism
	8.	Run OSDU/OFP schema alignment checks
	9.	Export or visualize results
