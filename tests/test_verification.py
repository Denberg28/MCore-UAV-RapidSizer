"""Tests for deterministic engineering verification."""

from dataclasses import replace

from app.engineering.propulsion import analyze_battery
from app.engineering.verification import (
    verify_battery,
    verify_wing_sizing,
)
from app.engineering.wing_sizing import calculate_wing_sizing


def test_wing_verification_passes():
    """Correct wing results should pass independent verification."""

    result = calculate_wing_sizing(
        wing_span_m=1.2,
        mean_chord_m=0.2,
        aircraft_mass_kg=1.2,
    )

    verification = verify_wing_sizing(
        wing_span_m=1.2,
        mean_chord_m=0.2,
        aircraft_mass_kg=1.2,
        result=result,
    )

    assert verification.status == "PASS"
    assert all(check.passed for check in verification.checks)


def test_wing_verification_detects_error():
    """An intentionally incorrect result must fail verification."""

    result = calculate_wing_sizing(
        wing_span_m=1.2,
        mean_chord_m=0.2,
        aircraft_mass_kg=1.2,
    )

    incorrect_result = replace(
        result,
        wing_area_m2=0.30,
    )

    verification = verify_wing_sizing(
        wing_span_m=1.2,
        mean_chord_m=0.2,
        aircraft_mass_kg=1.2,
        result=incorrect_result,
    )

    assert verification.status == "FAIL"
    assert verification.checks[0].passed is False


def test_battery_verification_passes():
    """Correct battery results should pass independent verification."""

    result = analyze_battery(
        cell_count=3,
        capacity_ah=2.2,
        discharge_c=30,
    )

    verification = verify_battery(
        cell_count=3,
        capacity_ah=2.2,
        discharge_c=30,
        result=result,
    )

    assert verification.status == "PASS"
    assert all(check.passed for check in verification.checks)


def test_battery_verification_detects_error():
    """An intentionally incorrect battery result must fail verification."""

    result = analyze_battery(
        cell_count=3,
        capacity_ah=2.2,
        discharge_c=30,
    )

    incorrect_result = replace(
        result,
        nominal_energy_wh=30.0,
    )

    verification = verify_battery(
        cell_count=3,
        capacity_ah=2.2,
        discharge_c=30,
        result=incorrect_result,
    )

    assert verification.status == "FAIL"
    assert verification.checks[1].passed is False
