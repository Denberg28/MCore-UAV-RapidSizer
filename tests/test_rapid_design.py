import pytest

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.models.mass_properties import MassItem, MassProperties
from app.services.rapid_design import apply_recommended_wing, assess_rapid_design


def make_aircraft(items=None):
    return Aircraft(
        name="Rapid Test UAV",
        geometry=AircraftGeometry(1.2, 0.2),
        mass=AircraftMass(1.2),
        propulsion=Propulsion(1500, 8, 6),
        battery=Battery(3, 2.2, 30),
        mass_properties=MassProperties(items=items or []),
    )


def test_assessment_requires_mass_inventory_for_closure_and_cg():
    result = assess_rapid_design(make_aircraft())

    assert result.overall_status == "CHECK"
    assert result.cg_percent_mac is None
    assert any(check.status == "NOT CHECKED" for check in result.checks)


def test_assessment_closes_mass_and_cg_with_measured_inventory():
    items = [
        MassItem("Structure", 0.6, 0.05, 0.0, 0.0, "MEASURED"),
        MassItem("Battery", 0.3, 0.05, 0.0, 0.0, "MEASURED"),
        MassItem("Payload", 0.3, 0.05, 0.0, 0.0, "MEASURED"),
    ]
    result = assess_rapid_design(make_aircraft(items))

    assert result.cg_percent_mac == pytest.approx(25.0)
    assert result.mass_properties.total_mass_kg == pytest.approx(1.2)
    assert result.overall_status == "PASS"


def test_apply_recommended_wing_matches_sizing_result():
    aircraft = make_aircraft()
    assessment = assess_rapid_design(aircraft)
    sized = apply_recommended_wing(aircraft)

    assert sized.geometry.wing_span_m == pytest.approx(
        assessment.sizing.recommended_span_m
    )
    assert sized.geometry.mean_chord_m == pytest.approx(
        assessment.sizing.recommended_mean_chord_m
    )
