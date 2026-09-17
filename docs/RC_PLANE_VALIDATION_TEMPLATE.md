# Real RC Aircraft Validation Record

Use one copy of this file per physical aircraft/configuration. Keep raw measurements unchanged and record corrections as new entries.

## Identification

| Field | Value |
|---|---|
| Aircraft / configuration | |
| Airframe revision | |
| Date | |
| Operator / measurer | |
| MCore software version / commit | |
| Project JSON | |

## Datum and coordinate convention

| Item | Value |
|---|---|
| Physical datum | |
| +X direction | Aft from datum |
| +Y direction | Starboard |
| +Z convention | |

## Measured geometry

| Parameter | MCore input | Physical measurement | Difference |
|---|---:|---:|---:|
| Wing span [m] | | | |
| MAC / mean chord [m] | | | |
| Wing LE station X [m] | | | |
| Wing area [m²] | | | |
| Tail arm [m] | | | |

## Mass inventory

| Component | Mass [kg] | X [m] | Y [m] | Z [m] | Source | Instrument / uncertainty |
|---|---:|---:|---:|---:|---|---|
| Motor | | | | | MEASURED | |
| ESC | | | | | MEASURED | |
| Battery | | | | | MEASURED | |
| Receiver / FC | | | | | MEASURED | |
| Servos | | | | | MEASURED | |
| Wing | | | | | MEASURED/ESTIMATED | |
| Fuselage | | | | | MEASURED/ESTIMATED | |
| Tail | | | | | MEASURED/ESTIMATED | |
| Landing gear | | | | | MEASURED | |
| Payload | | | | | MEASURED | |

## Mass and CG validation

| Parameter | MCore calculation | Physical measurement | Error |
|---|---:|---:|---:|
| Total mass [kg] | | | |
| CG X [m] | | | |
| CG Y [m] | | | |
| CG Z [m] | | | |
| CG [% MAC] | | | |

Physical CG measurement method:

- [ ] CG stand / two-point support
- [ ] Multi-scale reaction measurement
- [ ] Other: ____________________

Internal prototype target for longitudinal CG model agreement (not a certification criterion):

- ≤ 5 mm: strong agreement for a small RC prototype
- 5–10 mm: investigate inventory/station uncertainty
- > 10 mm: model or measurement discrepancy requires investigation

## Propulsion bench validation

Record the exact motor, propeller, ESC, battery, and test condition.

| Parameter | MCore / requirement | Measured | Difference |
|---|---:|---:|---:|
| Battery voltage [V] | | | |
| Current [A] | | | |
| Electrical power [W] | | | |
| RPM | | | |
| Static thrust [N] | | | |
| Motor temperature [°C] | | | |
| ESC temperature [°C] | | | |

## Flight validation

| Parameter | Prediction / target | Flight observation / measurement |
|---|---|---|
| Takeoff mass | | |
| CG | | |
| Wind / weather | | |
| Cruise throttle | | |
| Cruise current | | |
| Flight time | | |
| Capacity used [mAh] | | |
| Stall behavior | | |
| Pitch trim | | |
| Pitch stability | | |
| Roll response | | |
| Landing behavior | | |

## Discrepancies and corrective actions

| ID | Discrepancy | Likely cause | Action | Retest required? |
|---|---|---|---|---|
| V-001 | | | | |

## Validation conclusion

- [ ] Software result agrees with physical measurement within the stated internal target.
- [ ] Additional measurement is required.
- [ ] Engineering model requires revision.
- [ ] Configuration changed; previous validation is no longer directly representative.

This record documents prototype validation. It is not an airworthiness approval or flight-safety certification.
