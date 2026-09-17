"""End-to-end integration tests for the MCore UAV backend."""

from math import isclose

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.services.application import create_project
from app.services.project_io import load_aircraft
from app.services.uav_analysis import analyze_aircraft


def make_integration_aircraft() -> Aircraft:
    """Create a known-valid aircraft for integration testing."""

    return Aircraft(
        name="Integration Test UAV",
        geometry=AircraftGeometry(
            wing_span_m=1.2,
            mean_chord_m=0.2,
        ),
        mass=AircraftMass(
            aircraft_mass_kg=1.2,
        ),
        propulsion=Propulsion(
            motor_kv=1500,
            propeller_diameter_in=8,
            propeller_pitch_in=6,
        ),
        battery=Battery(
            cell_count=3,
            capacity_ah=2.2,
            discharge_c=30,
        ),
    )


def test_complete_backend_workflow(tmp_path):
    """The complete backend workflow should operate end to end."""

    aircraft = make_integration_aircraft()
    project_path = tmp_path / "integration_uav.json"

    # 1. Create and validate project.
    creation = create_project(
        aircraft=aircraft,
        path=project_path,
    )

    assert creation.created is True
    assert creation.validation.valid is True
    assert project_path.exists()

    # 2. Load the persisted project.
    loaded = load_aircraft(project_path)

    assert loaded.name == aircraft.name
    assert loaded.geometry.wing_span_m == 1.2
    assert loaded.geometry.mean_chord_m == 0.2
    assert loaded.mass.aircraft_mass_kg == 1.2

    # 3. Analyze the loaded project.
    analysis = analyze_aircraft(loaded)

    assert isclose(
        analysis.wing.wing_area_m2,
        0.24,
    )

    assert isclose(
        analysis.wing.aspect_ratio,
        6.0,
    )

    assert isclose(
        analysis.battery.nominal_voltage_v,
        11.1,
    )

    # 4. Verify engineering calculations.
    assert analysis.wing_verification.status == "PASS"
    assert analysis.battery_verification.status == "PASS"
    assert analysis.overall_verification_status == "PASS"
