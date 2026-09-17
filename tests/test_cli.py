"""Tests for the MCore command-line interface."""

from pathlib import Path

from app.main import build_parser, create_aircraft
from app.services.project_io import load_aircraft


def test_parser_has_expected_commands():
    """CLI should expose the core MCore commands."""

    parser = build_parser()

    args = parser.parse_args(
        [
            "project",
            "info",
            "data/projects/mcore_test_uav.json",
        ]
    )

    assert args.command == "project"
    assert args.project_command == "info"
    assert args.path == "data/projects/mcore_test_uav.json"


def test_calculate_parser_creates_aircraft():
    """Calculate command should construct the Aircraft model."""

    parser = build_parser()

    args = parser.parse_args(
        [
            "calculate",
            "--name",
            "Test UAV",
            "--span",
            "1.2",
            "--chord",
            "0.2",
            "--mass",
            "1.2",
            "--kv",
            "1500",
            "--prop-diameter",
            "8",
            "--prop-pitch",
            "6",
            "--battery",
            "3",
            "--capacity",
            "2.2",
            "--c-rating",
            "30",
        ]
    )

    aircraft = create_aircraft(args)

    assert aircraft.name == "Test UAV"
    assert aircraft.geometry.wing_span_m == 1.2
    assert aircraft.geometry.mean_chord_m == 0.2
    assert aircraft.mass.aircraft_mass_kg == 1.2
    assert aircraft.propulsion.motor_kv == 1500
    assert aircraft.battery.cell_count == 3
    assert aircraft.battery.capacity_ah == 2.2


def test_project_file_can_be_loaded():
    """The CLI project fixture should load through the persistence layer."""

    project_path = Path(
        "data/projects/mcore_test_uav.json"
    )

    aircraft = load_aircraft(project_path)

    assert aircraft.name == "MCore Test UAV"
    assert aircraft.geometry.wing_span_m == 1.2
    assert aircraft.geometry.mean_chord_m == 0.2
    assert aircraft.mass.aircraft_mass_kg == 1.2
    assert aircraft.propulsion.motor_kv == 1500
    assert aircraft.battery.cell_count == 3
    assert aircraft.battery.capacity_ah == 2.2
