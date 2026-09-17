from math import isclose

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.services.uav_analysis import (
    UAVAnalysisResult,
    analyze_aircraft,
)


def make_test_aircraft() -> Aircraft:
    """Create a known-valid aircraft for analysis tests."""

    return Aircraft(
        name="Test UAV",
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


def test_complete_uav_analysis():
    """The complete UAV analysis should calculate and verify correctly."""

    aircraft = make_test_aircraft()

    result = analyze_aircraft(aircraft)

    assert isclose(
        result.wing.wing_area_m2,
        0.24,
    )

    assert isclose(
        result.wing.aspect_ratio,
        6.0,
    )

    assert isclose(
        result.battery.nominal_voltage_v,
        11.1,
    )

    assert isclose(
        result.battery.nominal_energy_wh,
        24.42,
    )

    assert isclose(
        result.battery.theoretical_max_current_a,
        66.0,
    )

    assert result.wing_verification.status == "PASS"
    assert result.battery_verification.status == "PASS"
    assert result.overall_verification_status == "PASS"


def test_analysis_returns_service_result():
    """The analysis service should return its defined result type."""

    aircraft = make_test_aircraft()

    result = analyze_aircraft(aircraft)

    assert isinstance(result, UAVAnalysisResult)


def test_analysis_result_contains_calculation_and_verification():
    """The service result should expose calculations and verification."""

    aircraft = make_test_aircraft()

    result = analyze_aircraft(aircraft)

    assert result.wing is not None
    assert result.battery is not None
    assert result.wing_verification is not None
    assert result.battery_verification is not None
