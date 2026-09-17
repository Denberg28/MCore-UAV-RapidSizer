"""Tests for UAV project persistence."""

from math import isclose

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.services.project_io import (
    aircraft_from_dict,
    aircraft_to_dict,
    load_aircraft,
    save_aircraft,
)


def create_test_aircraft() -> Aircraft:
    """Create a representative test aircraft."""

    return Aircraft(
        name="MCore Test UAV",
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


def test_aircraft_to_dict():
    """Aircraft should convert to the expected dictionary structure."""

    aircraft = create_test_aircraft()
    data = aircraft_to_dict(aircraft)

    assert data["name"] == "MCore Test UAV"
    assert data["geometry"]["wing_span_m"] == 1.2
    assert data["geometry"]["mean_chord_m"] == 0.2
    assert data["mass"]["aircraft_mass_kg"] == 1.2
    assert data["propulsion"]["motor_kv"] == 1500
    assert data["battery"]["cell_count"] == 3
    assert data["battery"]["capacity_ah"] == 2.2
    assert data["battery"]["discharge_c"] == 30


def test_aircraft_round_trip():
    """Aircraft should survive dictionary serialization and reconstruction."""

    original = create_test_aircraft()

    data = aircraft_to_dict(original)
    restored = aircraft_from_dict(data)

    assert restored.name == original.name
    assert isclose(
        restored.geometry.wing_span_m,
        original.geometry.wing_span_m,
    )
    assert isclose(
        restored.geometry.mean_chord_m,
        original.geometry.mean_chord_m,
    )
    assert isclose(
        restored.mass.aircraft_mass_kg,
        original.mass.aircraft_mass_kg,
    )
    assert restored.propulsion.motor_kv == original.propulsion.motor_kv
    assert (
        restored.propulsion.propeller_diameter_in
        == original.propulsion.propeller_diameter_in
    )
    assert (
        restored.propulsion.propeller_pitch_in
        == original.propulsion.propeller_pitch_in
    )
    assert restored.battery.cell_count == original.battery.cell_count
    assert isclose(
        restored.battery.capacity_ah,
        original.battery.capacity_ah,
    )
    assert isclose(
        restored.battery.discharge_c,
        original.battery.discharge_c,
    )


def test_save_and_load(tmp_path):
    """Aircraft should survive a JSON file save/load round trip."""

    original = create_test_aircraft()

    project_path = tmp_path / "test_uav.json"

    save_aircraft(
        original,
        project_path,
    )

    assert project_path.exists()

    restored = load_aircraft(project_path)

    assert restored.name == original.name
    assert isclose(
        restored.geometry.wing_span_m,
        original.geometry.wing_span_m,
    )
    assert isclose(
        restored.geometry.mean_chord_m,
        original.geometry.mean_chord_m,
    )
    assert isclose(
        restored.mass.aircraft_mass_kg,
        original.mass.aircraft_mass_kg,
    )
    assert restored.propulsion.motor_kv == original.propulsion.motor_kv
    assert restored.battery.cell_count == original.battery.cell_count
    assert isclose(
        restored.battery.capacity_ah,
        original.battery.capacity_ah,
    )


def test_save_creates_parent_directory(tmp_path):
    """Saving should create missing project directories."""

    aircraft = create_test_aircraft()

    project_path = (
        tmp_path
        / "projects"
        / "nested"
        / "test_uav.json"
    )

    save_aircraft(
        aircraft,
        project_path,
    )

    assert project_path.exists()

    restored = load_aircraft(project_path)

    assert restored.name == aircraft.name
