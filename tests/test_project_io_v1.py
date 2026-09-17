from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.models.mass_properties import MassItem, MassProperties
from app.services.project_io import load_aircraft, save_aircraft


def test_v1_project_persists_requirements_and_mass_inventory(tmp_path):
    aircraft = Aircraft(
        name="V1 Project",
        geometry=AircraftGeometry(1.1, 0.18),
        mass=AircraftMass(1.0),
        propulsion=Propulsion(1400, 8, 5),
        battery=Battery(4, 2.5, 35),
        mass_properties=MassProperties(
            items=[MassItem("Battery", 0.25, 0.12, 0.0, 0.02, "MEASURED", 0.001)]
        ),
    )
    aircraft.requirements.endurance_min = 35.0

    path = tmp_path / "v1.json"
    save_aircraft(aircraft, path)
    restored = load_aircraft(path)

    assert restored.requirements.endurance_min == 35.0
    assert len(restored.mass_properties.items) == 1
    assert restored.mass_properties.items[0].source == "MEASURED"
