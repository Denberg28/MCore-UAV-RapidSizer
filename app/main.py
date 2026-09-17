"""MCore UAV Layout & Sizing command-line application."""

import argparse

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.services.application import create_project
from app.services.project_io import load_aircraft, save_aircraft
from app.services.uav_analysis import analyze_aircraft


def add_aircraft_arguments(parser: argparse.ArgumentParser) -> None:
    """Add aircraft definition arguments to a parser."""

    parser.add_argument("--name", default="MCore UAV")
    parser.add_argument("--span", type=float, required=True)
    parser.add_argument("--chord", type=float, required=True)
    parser.add_argument("--mass", type=float, required=True)
    parser.add_argument("--kv", type=float, required=True)
    parser.add_argument("--prop-diameter", type=float, required=True)
    parser.add_argument("--prop-pitch", type=float, required=True)
    parser.add_argument("--battery", type=int, required=True)
    parser.add_argument("--capacity", type=float, required=True)
    parser.add_argument("--c-rating", type=float, required=True)


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="MCore UAV Layout & Sizing"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    calculate_parser = subparsers.add_parser(
        "calculate",
        help="Create an aircraft from command-line inputs and analyze it.",
    )
    add_aircraft_arguments(calculate_parser)

    save_parser = subparsers.add_parser(
        "save",
        help="Create an aircraft and save it as a JSON project.",
    )
    save_parser.add_argument(
        "path",
        help="Path to the JSON project file.",
    )
    add_aircraft_arguments(save_parser)

    load_parser = subparsers.add_parser(
        "load",
        help="Load an existing JSON project and analyze it.",
    )
    load_parser.add_argument(
        "path",
        help="Path to the JSON project file.",
    )

    project_parser = subparsers.add_parser(
        "project",
        help="Create or inspect an MCore project.",
    )

    project_subparsers = project_parser.add_subparsers(
        dest="project_command",
        required=True,
    )

    create_parser = project_subparsers.add_parser(
        "create",
        help="Create and save a new UAV project.",
    )
    create_parser.add_argument(
        "path",
        help="Path to the JSON project file.",
    )
    add_aircraft_arguments(create_parser)

    info_parser = project_subparsers.add_parser(
        "info",
        help="Display the stored project inputs.",
    )
    info_parser.add_argument(
        "path",
        help="Path to the JSON project file.",
    )

    return parser


def create_aircraft(args: argparse.Namespace) -> Aircraft:
    """Convert command-line inputs into an Aircraft model."""

    return Aircraft(
        name=args.name,
        geometry=AircraftGeometry(
            wing_span_m=args.span,
            mean_chord_m=args.chord,
        ),
        mass=AircraftMass(
            aircraft_mass_kg=args.mass,
        ),
        propulsion=Propulsion(
            motor_kv=args.kv,
            propeller_diameter_in=args.prop_diameter,
            propeller_pitch_in=args.prop_pitch,
        ),
        battery=Battery(
            cell_count=args.battery,
            capacity_ah=args.capacity,
            discharge_c=args.c_rating,
        ),
    )


def print_project_info(aircraft: Aircraft) -> None:
    """Print stored project inputs without performing analysis."""

    print()
    print("=" * 50)
    print("MCORE UAV PROJECT")
    print("=" * 50)

    print(f"\nName: {aircraft.name}")

    print("\nGEOMETRY")
    print(
        f"  Wing span:         "
        f"{aircraft.geometry.wing_span_m:.3f} m"
    )
    print(
        f"  Mean chord:        "
        f"{aircraft.geometry.mean_chord_m:.3f} m"
    )

    print("\nMASS")
    print(
        f"  Aircraft mass:     "
        f"{aircraft.mass.aircraft_mass_kg:.3f} kg"
    )

    print("\nPROPULSION")
    print(
        f"  Motor KV:          "
        f"{aircraft.propulsion.motor_kv:.0f} KV"
    )
    print(
        f"  Propeller:         "
        f"{aircraft.propulsion.propeller_diameter_in:.1f} x "
        f"{aircraft.propulsion.propeller_pitch_in:.1f} in"
    )

    print("\nBATTERY")
    print(
        f"  Configuration:     "
        f"{aircraft.battery.cell_count}S"
    )
    print(
        f"  Capacity:          "
        f"{aircraft.battery.capacity_ah:.2f} Ah"
    )
    print(
        f"  C-rating:          "
        f"{aircraft.battery.discharge_c:.0f}C"
    )

    print("\n" + "=" * 50)


def print_result(aircraft: Aircraft) -> None:
    """Print the engineering analysis and verification result."""

    result = analyze_aircraft(aircraft)

    print()
    print("=" * 50)
    print("MCORE UAV LAYOUT & SIZING")
    print("=" * 50)

    print(f"\nAircraft: {aircraft.name}")

    print("\nWING")
    print(
        f"  Span:              "
        f"{aircraft.geometry.wing_span_m:.3f} m"
    )
    print(
        f"  Mean chord:        "
        f"{aircraft.geometry.mean_chord_m:.3f} m"
    )
    print(
        f"  Area:              "
        f"{result.wing.wing_area_m2:.3f} m²"
    )
    print(
        f"  Aspect ratio:      "
        f"{result.wing.aspect_ratio:.2f}"
    )
    print(
        f"  Wing loading:      "
        f"{result.wing.wing_loading_kg_m2:.2f} kg/m²"
    )
    print(
        f"  Wing loading:      "
        f"{result.wing.wing_loading_n_m2:.2f} N/m²"
    )

    print("\nPROPULSION")
    print(
        f"  Motor KV:           "
        f"{aircraft.propulsion.motor_kv:.0f} KV"
    )
    print(
        f"  Propeller:          "
        f"{aircraft.propulsion.propeller_diameter_in:.1f} x "
        f"{aircraft.propulsion.propeller_pitch_in:.1f} in"
    )

    print("\nBATTERY")
    print(
        f"  Configuration:      "
        f"{aircraft.battery.cell_count}S"
    )
    print(
        f"  Capacity:           "
        f"{aircraft.battery.capacity_ah:.2f} Ah"
    )
    print(
        f"  C-rating:           "
        f"{aircraft.battery.discharge_c:.0f}C"
    )
    print(
        f"  Nominal voltage:    "
        f"{result.battery.nominal_voltage_v:.2f} V"
    )
    print(
        f"  Nominal energy:     "
        f"{result.battery.nominal_energy_wh:.2f} Wh"
    )
    print(
        f"  Theoretical max:    "
        f"{result.battery.theoretical_max_current_a:.1f} A"
    )

    print("\nVERIFICATION")
    print(
        f"  Wing calculations:  "
        f"{result.wing_verification.status}"
    )
    print(
        f"  Battery analysis:   "
        f"{result.battery_verification.status}"
    )
    print(
        f"  Overall status:     "
        f"{result.overall_verification_status}"
    )

    print(
        "\n* Theoretical maximum current is based "
        "on the stated C-rating."
    )
    print(
        "* It is not a guarantee of continuous "
        "real-world battery output."
    )
    print(
        "* Verification uses independent "
        "deterministic recalculation."
    )

    print("\n" + "=" * 50)


def handle_calculate(args: argparse.Namespace) -> None:
    """Create and analyze an aircraft from command-line inputs."""

    aircraft = create_aircraft(args)
    print_result(aircraft)


def handle_save(args: argparse.Namespace) -> None:
    """Create an aircraft and save it as a JSON project."""

    aircraft = create_aircraft(args)

    save_aircraft(
        aircraft,
        args.path,
    )

    print(f"Project saved: {args.path}")
    print(f"Aircraft: {aircraft.name}")


def handle_load(args: argparse.Namespace) -> None:
    """Load an aircraft project and analyze it."""

    aircraft = load_aircraft(args.path)

    print(f"Project loaded: {args.path}")
    print_result(aircraft)


def handle_project_create(args: argparse.Namespace) -> None:
    """Create a new MCore UAV project through the application service."""

    aircraft = create_aircraft(args)

    result = create_project(
        aircraft=aircraft,
        path=args.path,
    )

    if not result.created:
        print("Project validation failed:")
        print()
        print(f"  {result.validation.summary}")
        print()

        for error in result.validation.errors:
            print(f"  - {error}")

        return

    print(f"Project created: {result.path}")
    print(f"Aircraft: {aircraft.name}")
    print(result.validation.summary)


def handle_project_info(args: argparse.Namespace) -> None:
    """Load a project and display its stored inputs."""

    aircraft = load_aircraft(args.path)

    print(f"Project loaded: {args.path}")
    print_project_info(aircraft)


def main() -> None:
    """Application entry point."""

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "calculate":
        handle_calculate(args)

    elif args.command == "save":
        handle_save(args)

    elif args.command == "load":
        handle_load(args)

    elif args.command == "project":
        if args.project_command == "create":
            handle_project_create(args)

        elif args.project_command == "info":
            handle_project_info(args)


if __name__ == "__main__":
    main()
