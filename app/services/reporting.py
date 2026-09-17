"""Engineering report generation for MCore rapid UAV sizing."""

from datetime import datetime, timezone
from pathlib import Path

from app.models.aircraft import Aircraft
from app.services.rapid_design import RapidDesignAssessment, assess_rapid_design


def build_markdown_report(
    aircraft: Aircraft,
    assessment: RapidDesignAssessment | None = None,
) -> str:
    """Create a traceable preliminary design report in Markdown."""

    result = assessment or assess_rapid_design(aircraft)
    req = aircraft.requirements
    sizing = result.sizing
    mass = result.mass_properties
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cg_text = (
        f"{result.cg_percent_mac:.1f}% MAC"
        if result.cg_percent_mac is not None
        else "Not available"
    )

    check_lines = "\n".join(
        f"- **{check.status} — {check.name}:** {check.message}"
        for check in result.checks
    )

    mass_lines = "\n".join(
        f"| {item.name} | {item.mass_kg:.4f} | {item.x_m:.4f} | "
        f"{item.y_m:.4f} | {item.z_m:.4f} | {item.source} | "
        f"{item.uncertainty_kg:.4f} |"
        for item in aircraft.mass_properties.items
    ) or "| _No mass items entered_ | | | | | | |"

    return f"""# MCore UAV Rapid Sizing Report

**Project:** {aircraft.name}  
**Generated:** {generated}  
**Preliminary status:** {result.overall_status}

> Conceptual/preliminary engineering output for rapid prototyping. This report is
> not an airworthiness approval, type design approval, or flight-safety release.
> Aerodynamic assumptions, propulsion performance, structures, controls, loads,
> flutter, EMI/EMC, software assurance, and flight behavior require appropriate
> analysis and testing before operational use.

## 1. Design requirements and assumptions

| Parameter | Value |
|---|---:|
| Design mass | {aircraft.mass.aircraft_mass_kg:.3f} kg |
| Target stall speed | {req.stall_speed_m_s:.2f} m/s |
| Target cruise speed | {req.cruise_speed_m_s:.2f} m/s |
| Target endurance | {req.endurance_min:.1f} min |
| Target climb rate | {req.climb_rate_m_s:.2f} m/s |
| Target aspect ratio | {req.aspect_ratio_target:.2f} |
| CLmax assumption | {req.cl_max:.3f} |
| CD0 assumption | {req.cd0:.4f} |
| Oswald efficiency | {req.oswald_efficiency:.3f} |
| Propulsive efficiency | {req.propulsive_efficiency:.3f} |
| Battery reserve | {req.battery_reserve_fraction * 100:.1f}% |
| Air density | {req.air_density_kg_m3:.3f} kg/m³ |
| Thrust-to-weight target | {req.thrust_to_weight_target:.2f} |
| Horizontal tail volume coefficient | {req.horizontal_tail_volume_coefficient:.3f} |
| Vertical tail volume coefficient | {req.vertical_tail_volume_coefficient:.3f} |
| Tail arm / wing chord | {req.tail_arm_chord_ratio:.2f} |
| User CG target | {req.cg_forward_mac_percent:.1f}–{req.cg_aft_mac_percent:.1f}% MAC |

## 2. Current geometry

| Parameter | Value |
|---|---:|
| Wing span | {aircraft.geometry.wing_span_m:.3f} m |
| Mean chord | {aircraft.geometry.mean_chord_m:.3f} m |
| Wing area | {aircraft.geometry.wing_area_m2:.4f} m² |
| Calculated stall speed | {result.actual_stall_speed_m_s:.2f} m/s |

## 3. Requirements-driven wing recommendation

| Parameter | Value |
|---|---:|
| Required wing area | {sizing.required_wing_area_m2:.4f} m² |
| Recommended rectangular span | {sizing.recommended_span_m:.3f} m |
| Recommended mean chord | {sizing.recommended_mean_chord_m:.3f} m |
| Wing loading | {sizing.wing_loading_kg_m2:.2f} kg/m² |

### Tail-volume reference sizing

| Parameter | Value |
|---|---:|
| Tail arm | {sizing.tail_arm_m:.3f} m |
| Horizontal tail area | {sizing.horizontal_tail_area_m2:.4f} m² |
| Horizontal tail span | {sizing.horizontal_tail_span_m:.3f} m |
| Horizontal tail mean chord | {sizing.horizontal_tail_mean_chord_m:.3f} m |
| Vertical tail area | {sizing.vertical_tail_area_m2:.4f} m² |
| Vertical tail height | {sizing.vertical_tail_height_m:.3f} m |
| Vertical tail mean chord | {sizing.vertical_tail_mean_chord_m:.3f} m |

These tail values are volume-coefficient-based reference geometry and require stability/control validation.

## 4. Cruise, power, and energy estimate

| Parameter | Value |
|---|---:|
| Cruise CL | {sizing.cruise_cl:.3f} |
| Cruise CD | {sizing.cruise_cd:.4f} |
| Cruise drag | {sizing.cruise_drag_n:.2f} N |
| Electrical cruise power | {sizing.electrical_cruise_power_w:.1f} W |
| Electrical climb power | {sizing.electrical_climb_power_w:.1f} W |
| Cruise current | {sizing.cruise_current_a:.1f} A |
| Climb current | {sizing.climb_current_a:.1f} A |
| Required nominal battery energy | {sizing.required_nominal_energy_wh:.1f} Wh |
| Required capacity at current voltage | {sizing.required_capacity_ah:.2f} Ah |
| Predicted endurance with current battery | {sizing.predicted_endurance_min:.1f} min |
| Required static thrust target | {sizing.required_static_thrust_n:.1f} N |

**Important propulsion limitation:** required thrust and power are design targets.
Motor/propeller suitability must be checked against measured test-stand or reliable
manufacturer data for the exact motor, propeller, voltage, ESC, and operating point.

## 5. Mass properties and CG

**Inventory mass:** {mass.total_mass_kg:.4f} kg  
**Measured mass fraction:** {mass.measured_mass_fraction * 100:.1f}%  
**CG X/Y/Z:** {mass.cg_x_m:.4f}, {mass.cg_y_m:.4f}, {mass.cg_z_m:.4f} m  
**CG relative to MAC:** {cg_text}  
**RSS mass uncertainty:** {mass.total_uncertainty_kg_rss:.4f} kg

| Item | Mass kg | X m | Y m | Z m | Source | Uncertainty kg |
|---|---:|---:|---:|---:|---|---:|
{mass_lines}

## 6. Design checks

{check_lines}

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
"""


def save_markdown_report(
    aircraft: Aircraft,
    path: str | Path,
    assessment: RapidDesignAssessment | None = None,
) -> Path:
    """Write the preliminary design report to disk."""

    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_markdown_report(aircraft, assessment),
        encoding="utf-8",
    )
    return report_path
