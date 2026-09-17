"""Tests for MCore aircraft input validation."""

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.services.validation import (
    ValidationResult,
    validate_aircraft,
)


def make_valid_aircraft() -> Aircraft:
    """Create a known-valid aircraft fixture."""

    return Aircraft(
        name="Validation Test UAV",
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


def test_valid_aircraft_has_no_validation_errors():
    """A physically positive aircraft should pass validation."""

    aircraft = make_valid_aircraft()

    result = validate_aircraft(aircraft)

    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert result.errors == []
    assert result.error_count == 0
    assert result.summary == "Validation passed."


def test_negative_geometry_is_rejected():
    """Negative wing dimensions should be rejected."""

    aircraft = make_valid_aircraft()
    aircraft.geometry.wing_span_m = -1.0

    result = validate_aircraft(aircraft)

    assert result.valid is False
    assert result.error_count == 1
    assert "Wing span must be greater than 0 m." in result.errors


def test_zero_mass_is_rejected():
    """Zero aircraft mass should be rejected."""

    aircraft = make_valid_aircraft()
    aircraft.mass.aircraft_mass_kg = 0

    result = validate_aircraft(aircraft)

    assert result.valid is False
    assert "Aircraft mass must be greater than 0 kg." in result.errors


def test_invalid_battery_is_rejected():
    """Invalid battery parameters should be rejected."""

    aircraft = make_valid_aircraft()

    aircraft.battery.cell_count = 0
    aircraft.battery.capacity_ah = -1
    aircraft.battery.discharge_c = 0

    result = validate_aircraft(aircraft)

    assert result.valid is False
    assert result.error_count == 3

    assert "Battery cell count must be at least 1S." in result.errors
    assert "Battery capacity must be greater than 0 Ah." in result.errors
    assert "Battery C-rating must be greater than 0." in result.errors


def test_all_invalid_inputs_are_reported():
    """All invalid aircraft inputs should be reported together."""

    aircraft = Aircraft(
        name="Invalid UAV",
        geometry=AircraftGeometry(
            wing_span_m=-1,
            mean_chord_m=0,
        ),
        mass=AircraftMass(
            aircraft_mass_kg=0,
        ),
        propulsion=Propulsion(
            motor_kv=-1500,
            propeller_diameter_in=0,
            propeller_pitch_in=-6,
        ),
        battery=Battery(
            cell_count=0,
            capacity_ah=-2,
            discharge_c=0,
        ),
    )

    result = validate_aircraft(aircraft)

    assert result.valid is False
    assert result.error_count == 9

    assert len(result.errors) == 9


def test_validation_summary_reports_error_count():
    """Invalid projects should report the number of errors."""

    aircraft = make_valid_aircraft()
    aircraft.geometry.wing_span_m = -1
    aircraft.mass.aircraft_mass_kg = 0

    result = validate_aircraft(aircraft)

    assert result.summary == "Validation failed with 2 error(s)."
