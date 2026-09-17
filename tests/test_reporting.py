from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.services.reporting import build_markdown_report


def test_report_contains_traceability_sections():
    aircraft = Aircraft(
        "Report UAV",
        AircraftGeometry(1.2, 0.2),
        AircraftMass(1.2),
        Propulsion(1500, 8, 6),
        Battery(3, 2.2, 30),
    )

    report = build_markdown_report(aircraft)

    assert "# MCore UAV Rapid Sizing Report" in report
    assert "Design requirements and assumptions" in report
    assert "Mass properties and CG" in report
    assert "Verification and development gates" in report
    assert "not an airworthiness approval" in report
