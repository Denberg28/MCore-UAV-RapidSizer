import math

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)


def test_aircraft_geometry():
    geometry = AircraftGeometry(
        wing_span_m=1.20,
        mean_chord_m=0.20,
    )

    assert math.isclose(geometry.wing_area_m2, 0.24, rel_tol=1e-9)


def test_battery():
    battery = Battery(
        cell_count=3,
        capacity_ah=2.2,
        discharge_c=30,
    )

    assert math.isclose(battery.nominal_voltage_v, 11.1, rel_tol=1e-9)
    assert math.isclose(battery.nominal_energy_wh, 24.42, rel_tol=1e-9)
    assert math.isclose(battery.theoretical_max_current_a, 66.0, rel_tol=1e-9)


def test_aircraft():
    aircraft = Aircraft(
        name="MCore Test UAV",
        geometry=AircraftGeometry(1.20, 0.20),
        mass=AircraftMass(1.20),
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

    assert math.isclose(aircraft.geometry.wing_area_m2, 0.24, rel_tol=1e-9)
    assert math.isclose(aircraft.mass.aircraft_mass_kg, 1.20, rel_tol=1e-9)
