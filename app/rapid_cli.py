"""Agent-friendly command-line interface for MCore UAV Rapid Sizer."""

import argparse
import json

from app.services.project_io import load_aircraft, save_aircraft
from app.services.rapid_design import apply_recommended_wing, assess_rapid_design
from app.services.reporting import save_markdown_report


def _assessment_dict(aircraft, assessment):
    sizing = assessment.sizing
    mass = assessment.mass_properties
    return {
        "project": aircraft.name,
        "status": assessment.overall_status,
        "current_geometry": {
            "span_m": aircraft.geometry.wing_span_m,
            "mean_chord_m": aircraft.geometry.mean_chord_m,
            "area_m2": aircraft.geometry.wing_area_m2,
            "stall_speed_m_s": assessment.actual_stall_speed_m_s,
        },
        "recommended_wing": {
            "area_m2": sizing.required_wing_area_m2,
            "span_m": sizing.recommended_span_m,
            "mean_chord_m": sizing.recommended_mean_chord_m,
        },
        "tail_reference": {
            "tail_arm_m": sizing.tail_arm_m,
            "horizontal_tail_area_m2": sizing.horizontal_tail_area_m2,
            "horizontal_tail_span_m": sizing.horizontal_tail_span_m,
            "horizontal_tail_mean_chord_m": sizing.horizontal_tail_mean_chord_m,
            "vertical_tail_area_m2": sizing.vertical_tail_area_m2,
            "vertical_tail_height_m": sizing.vertical_tail_height_m,
            "vertical_tail_mean_chord_m": sizing.vertical_tail_mean_chord_m,
        },
        "power_energy": {
            "cruise_power_w": sizing.electrical_cruise_power_w,
            "climb_power_w": sizing.electrical_climb_power_w,
            "required_energy_wh": sizing.required_nominal_energy_wh,
            "required_capacity_ah": sizing.required_capacity_ah,
            "predicted_endurance_min": sizing.predicted_endurance_min,
            "required_static_thrust_n": sizing.required_static_thrust_n,
        },
        "mass_properties": {
            "total_mass_kg": mass.total_mass_kg,
            "cg_x_m": mass.cg_x_m,
            "cg_y_m": mass.cg_y_m,
            "cg_z_m": mass.cg_z_m,
            "cg_percent_mac": assessment.cg_percent_mac,
            "measured_mass_fraction": mass.measured_mass_fraction,
        },
        "checks": [
            {
                "name": check.name,
                "status": check.status,
                "message": check.message,
            }
            for check in assessment.checks
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MCore UAV Rapid Sizer v1.3")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze a versioned MCore project.")
    analyze.add_argument("project")
    analyze.add_argument("--json", action="store_true", dest="as_json")

    size = sub.add_parser("size-wing", help="Apply requirements-driven wing sizing.")
    size.add_argument("project")
    size.add_argument("--output", required=True)

    report = sub.add_parser("report", help="Generate a Markdown design report.")
    report.add_argument("project")
    report.add_argument("output")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    aircraft = load_aircraft(args.project)

    if args.command == "analyze":
        assessment = assess_rapid_design(aircraft)
        data = _assessment_dict(aircraft, assessment)
        if args.as_json:
            print(json.dumps(data, indent=2))
        else:
            print(f"Project: {aircraft.name}")
            print(f"Preliminary status: {assessment.overall_status}")
            print(
                "Recommended wing: "
                f"{assessment.sizing.recommended_span_m:.3f} m span x "
                f"{assessment.sizing.recommended_mean_chord_m:.3f} m chord"
            )
            for check in assessment.checks:
                print(f"[{check.status}] {check.name}: {check.message}")

    elif args.command == "size-wing":
        sized = apply_recommended_wing(aircraft)
        save_aircraft(sized, args.output)
        print(f"Sized project saved: {args.output}")

    elif args.command == "report":
        path = save_markdown_report(aircraft, args.output)
        print(f"Report saved: {path}")


if __name__ == "__main__":
    main()
