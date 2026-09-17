# MCore UAV Rapid Sizing Report

**Project:** MCore Rapid Prototype Example  
**Generated:** 2026-09-17 00:41 UTC  
**Preliminary status:** CHECK

> Conceptual/preliminary engineering output for rapid prototyping. This report is
> not an airworthiness approval, type design approval, or flight-safety release.
> Aerodynamic assumptions, propulsion performance, structures, controls, loads,
> flutter, EMI/EMC, software assurance, and flight behavior require appropriate
> analysis and testing before operational use.

## 1. Design requirements and assumptions

| Parameter | Value |
|---|---:|
| Design mass | 1.200 kg |
| Target stall speed | 10.00 m/s |
| Target cruise speed | 15.00 m/s |
| Target endurance | 20.0 min |
| Target climb rate | 2.00 m/s |
| Target aspect ratio | 7.00 |
| CLmax assumption | 1.200 |
| CD0 assumption | 0.0350 |
| Oswald efficiency | 0.800 |
| Propulsive efficiency | 0.650 |
| Battery reserve | 20.0% |
| Air density | 1.225 kg/m³ |
| Thrust-to-weight target | 0.60 |
| Horizontal tail volume coefficient | 0.500 |
| Vertical tail volume coefficient | 0.040 |
| Tail arm / wing chord | 3.00 |
| User CG target | 20.0–30.0% MAC |

## 2. Current geometry

| Parameter | Value |
|---|---:|
| Wing span | 1.200 m |
| Mean chord | 0.200 m |
| Wing area | 0.2400 m² |
| Calculated stall speed | 8.17 m/s |

## 3. Requirements-driven wing recommendation

| Parameter | Value |
|---|---:|
| Required wing area | 0.1601 m² |
| Recommended rectangular span | 1.059 m |
| Recommended mean chord | 0.151 m |
| Wing loading | 7.49 kg/m² |

### Tail-volume reference sizing

| Parameter | Value |
|---|---:|
| Tail arm | 0.454 m |
| Horizontal tail area | 0.0267 m² |
| Horizontal tail span | 0.327 m |
| Horizontal tail mean chord | 0.082 m |
| Vertical tail area | 0.0149 m² |
| Vertical tail height | 0.164 m |
| Vertical tail mean chord | 0.091 m |

These tail values are volume-coefficient-based reference geometry and require stability/control validation.

## 4. Cruise, power, and energy estimate

| Parameter | Value |
|---|---:|
| Cruise CL | 0.533 |
| Cruise CD | 0.0512 |
| Cruise drag | 1.13 N |
| Electrical cruise power | 26.1 W |
| Electrical climb power | 62.3 W |
| Cruise current | 2.3 A |
| Climb current | 5.6 A |
| Required nominal battery energy | 10.9 Wh |
| Required capacity at current voltage | 0.98 Ah |
| Predicted endurance with current battery | 45.0 min |
| Required static thrust target | 7.1 N |

**Important propulsion limitation:** required thrust and power are design targets.
Motor/propeller suitability must be checked against measured test-stand or reliable
manufacturer data for the exact motor, propeller, voltage, ESC, and operating point.

## 5. Mass properties and CG

**Inventory mass:** 1.2000 kg  
**Measured mass fraction:** 49.2%  
**CG X/Y/Z:** 0.3429, 0.0000, 0.0091 m  
**CG relative to MAC:** 21.5% MAC  
**RSS mass uncertainty:** 0.0222 kg

| Item | Mass kg | X m | Y m | Z m | Source | Uncertainty kg |
|---|---:|---:|---:|---:|---|---:|
| Motor + Prop | 0.1200 | 0.0500 | 0.0000 | 0.0000 | MEASURED | 0.0020 |
| Battery | 0.2200 | 0.3000 | 0.0000 | 0.0200 | MEASURED | 0.0020 |
| Wing | 0.2800 | 0.3500 | 0.0000 | 0.0000 | ESTIMATED | 0.0150 |
| Fuselage | 0.2500 | 0.4000 | 0.0000 | 0.0000 | ESTIMATED | 0.0150 |
| Avionics | 0.1000 | 0.3200 | 0.0000 | 0.0200 | MEASURED | 0.0020 |
| Tail | 0.0800 | 0.7500 | 0.0000 | 0.0000 | ESTIMATED | 0.0050 |
| Payload | 0.1500 | 0.3300 | 0.0000 | 0.0300 | MEASURED | 0.0020 |

## 6. Design checks

- **PASS — Stall-speed requirement:** Calculated 8.17 m/s vs target 10.00 m/s.
- **PASS — Mission endurance energy:** Predicted 45.0 min vs target 20.0 min using the stated reserve and efficiency assumptions.
- **PASS — Battery current capability:** Theoretical C-rating margin at calculated climb power: 60.4 A. Validate with measured voltage/current/temperature data.
- **PASS — Mass budget closure:** Inventory 1.200 kg vs design mass 1.200 kg; delta +0.000 kg.
- **PASS — CG target envelope:** CG 21.5% MAC vs user target 20.0–30.0% MAC. This is a design target, not a certified envelope.
- **CHECK — Mass-data maturity:** Measured mass covers 49.2% of the inventory. Target at least 80% measured mass before advanced prototype testing.
- **PASS — Mass-properties verification:** Independent moment/CG recalculation completed.
- **INFO — Philippines / CAAP mass reference:** Below the CAAP 7 kg Large-RPA threshold.

## 7. Verification and development gates

1. Re-weigh the assembled aircraft with calibrated/checked scales and close the mass budget.
2. Confirm CG from measured component locations or whole-aircraft weighing geometry.
3. Validate motor/propeller/ESC/battery current, voltage sag, thrust, RPM, and temperature on a test stand.
4. Validate aerodynamic assumptions with analysis, simulation, or controlled flight-test data.
5. Perform structural load-path, control-authority, flutter, and fail-safe reviews appropriate to the prototype.
6. Freeze configuration and record changes before each test campaign.
7. Check the applicable CAAP operational/certification path for the intended mission and aircraft mass.

## 8. Engineering basis

MCore uses SI units internally, deterministic calculations, independent verification,
explicit assumptions, measured-vs-estimated source tagging, versioned project data,
and traceable design checks. See `ENGINEERING_BASIS.md` for scope and references.
