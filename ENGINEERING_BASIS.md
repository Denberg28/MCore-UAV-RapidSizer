# MCore UAV Rapid Sizer v1.0 — Engineering Basis

## Purpose

MCore v1.0 supports rapid conceptual/preliminary fixed-wing UAV sizing. It adopts industry-style engineering practices: explicit requirements, SI units, traceable assumptions, deterministic calculations, measured-vs-estimated data, configuration persistence, independent checks, and progressive replacement of estimates by test evidence.

It does **not** claim certification compliance merely because the software returns PASS.

## 1. Wing sizing

The reference wing is sized from the 1-g level-flight stall relation:

`S = 2 W / (rho * Vs^2 * CLmax)`

A rectangular reference geometry is then obtained from target aspect ratio:

`b = sqrt(AR * S)`

`c = S / b`

This is appropriate for fast preliminary sizing. Final geometry may be tapered, swept, twisted, or otherwise optimized after higher-fidelity aerodynamic and structural work.

## 2. Cruise drag and power

MCore uses a parabolic drag polar:

`CD = CD0 + k CL^2`

`k = 1 / (pi * e * AR)`

`D = q S CD`

`Paero = D V`

Electrical power is estimated by dividing mechanical/aerodynamic power by the user-supplied propulsive efficiency. This is a preliminary energy model; it does not replace measured motor/propeller performance data.

## 3. Climb power

Preliminary climb power adds the potential-energy rate `W * ROC` to the cruise aerodynamic power before applying the propulsive-efficiency assumption.

## 4. Battery energy

Nominal battery energy is `Vnom * Ah`. The mission model reserves the user-defined battery fraction and reports required nominal energy/capacity. C-rating current is treated as a theoretical capability, not guaranteed continuous real-world output.

## 5. Mass properties and CG

MCore uses component mass, datum arm, and moment. The three-axis center of gravity is:

`Xcg = sum(m*x) / sum(m)`

and similarly for Y and Z.

This follows conventional aircraft weight-and-balance practice. FAA-H-8083-1B describes determining total weight and total moment from weighing points and dividing total moment by total weight to obtain CG from the datum. MCore applies the same physical moment principle at component level during design.

Reference:
- FAA Weight & Balance Handbook, FAA-H-8083-1B: https://www.faa.gov/sites/faa.gov/files/2023-09/Weight_Balance_Handbook.pdf

## 6. CG target

MCore reports CG as percent MAC using the project datum and wing-leading-edge coordinate. The default 20–30% MAC range is only an editable starting design target. It is **not** asserted as a universal certified envelope. The final permissible CG range must come from stability/control analysis and test evidence for the actual aircraft.

## 7. Material mass estimation

Two estimators are provided:

- sheet/laminate-like material: `mass = area * areal_density`
- solid material: `mass = volume * density`

These remain `ESTIMATED` inputs. When a component can be weighed, the `MEASURED` value should replace the estimate.

## 8. Philippine / CAAP regulatory reference

For Philippine projects, the software displays mass information based on current CAAP RPAS references. CAAP defines Large RPA at 7 kg and above in PCAR Part 1. Current PCAR Part 11 material describes the Open-category mass ceiling as 25 kg or less, subject to additional operational conditions.

References:
- CAAP RPAS Regulations: https://www.caap.gov.ph/rpas-regulations/
- CAAP PCAR Part 1: https://www.caap.gov.ph/pcar-part-1/
- CAAP PCAR Part 11, July 2025 edition: https://www.caap.gov.ph/wp-content/uploads/2025/07/PART-11-Aerial-Work-and-Operating-Limitations-for-Non-Type-Certificated-Aircraft.pdf

The application displays this only as a reference; it does not determine operational approval.

## 9. Higher-assurance UAS context

For higher-risk UAS operations, current EASA material emphasizes design evidence, configuration control, safety assessment, development assurance, and experimental flight testing. ASTM F3269-21 addresses run-time-assurance architectures for aircraft systems containing complex functions. These are useful architectural references as MCore evolves toward AI-assisted engineering and complex/autonomous functions, but v1.0 does not claim compliance with either framework.

References:
- EASA UAS SAIL III design MoC: https://www.easa.europa.eu/en/document-library/product-certification-consultations/means-compliance-moc-design-uas-operated-sail
- EASA UAS rules: https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-unmanned-aircraft-systems
- ASTM F3269-21: https://store.astm.org/f3269-21.html

## 10. AI-agent engineering contract

The MCore agents should:

1. obtain or clarify requirements;
2. use the deterministic engine for calculations when a capability exists;
3. preserve assumptions and uncertainty;
4. request independent verification for material decisions;
5. identify missing measured/manufacturer data;
6. propose the next analysis or experiment;
7. never convert a preliminary PASS into a claim of flight safety or certification.

The recommended machine interface is:

`python -m app.rapid_cli analyze <project.json> --json`
