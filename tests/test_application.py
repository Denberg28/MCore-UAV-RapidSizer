"""Tests for the MCore application service."""

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.services.application import (
    ProjectCreateResult,
    ProjectUpdateResult,
    create_project,
    update_project,
)
from app.services.project_io import load_aircraft


def make_test_aircraft() -> Aircraft:
    """Create a known-valid aircraft for application tests."""

    return Aircraft(
        name="Application Test UAV",
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


def test_create_project_returns_structured_result(tmp_path):
    """Project creation should return a structured application result."""

    aircraft = make_test_aircraft()
    project_path = tmp_path / "application_test.json"

    result = create_project(
        aircraft=aircraft,
        path=project_path,
    )

    assert isinstance(result, ProjectCreateResult)
    assert result.created is True
    assert result.validation.valid is True
    assert result.path == project_path
    assert project_path.exists()


def test_create_project_rejects_invalid_aircraft(tmp_path):
    """Invalid projects should not be saved by the application workflow."""

    aircraft = make_test_aircraft()
    aircraft.geometry.wing_span_m = -1.0

    project_path = tmp_path / "invalid_application_test.json"

    result = create_project(
        aircraft=aircraft,
        path=project_path,
    )

    assert isinstance(result, ProjectCreateResult)
    assert result.created is False
    assert result.validation.valid is False
    assert result.validation.error_count == 1
    assert project_path.exists() is False


def test_update_project_saves_valid_changes(tmp_path):
    """Valid project changes should be saved by the update workflow."""

    aircraft = make_test_aircraft()
    project_path = tmp_path / "update_test.json"

    first_result = create_project(
        aircraft=aircraft,
        path=project_path,
    )

    assert first_result.created is True

    aircraft.geometry.wing_span_m = 1.5
    aircraft.mass.aircraft_mass_kg = 1.4

    result = update_project(
        aircraft=aircraft,
        path=project_path,
    )

    assert isinstance(result, ProjectUpdateResult)
    assert result.updated is True
    assert result.validation.valid is True
    assert result.path == project_path

    loaded = load_aircraft(project_path)

    assert loaded.geometry.wing_span_m == 1.5
    assert loaded.mass.aircraft_mass_kg == 1.4


def test_update_project_rejects_invalid_changes(tmp_path):
    """Invalid project changes should not overwrite the project."""

    aircraft = make_test_aircraft()
    project_path = tmp_path / "invalid_update_test.json"

    create_result = create_project(
        aircraft=aircraft,
        path=project_path,
    )

    assert create_result.created is True

    aircraft.geometry.wing_span_m = -2.0

    result = update_project(
        aircraft=aircraft,
        path=project_path,
    )

    assert isinstance(result, ProjectUpdateResult)
    assert result.updated is False
    assert result.validation.valid is False
    assert result.path == project_path

    loaded = load_aircraft(project_path)

    assert loaded.geometry.wing_span_m == 1.2
    assert loaded.geometry.mean_chord_m == 0.2
    assert loaded.mass.aircraft_mass_kg == 1.2
