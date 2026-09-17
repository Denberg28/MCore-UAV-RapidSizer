"""Application-level UAV analysis service."""

from dataclasses import dataclass

from app.engineering.propulsion import (
    BatteryAnalysis,
    analyze_battery,
)
from app.engineering.verification import (
    VerificationResult,
    verify_battery,
    verify_wing_sizing,
)
from app.engineering.wing_sizing import (
    WingSizingResult,
    calculate_wing_sizing,
)
from app.models.aircraft import Aircraft


@dataclass(frozen=True)
class UAVAnalysisResult:
    """Combined preliminary UAV analysis and verification result."""

    wing: WingSizingResult
    battery: BatteryAnalysis
    wing_verification: VerificationResult
    battery_verification: VerificationResult

    @property
    def overall_verification_status(self) -> str:
        """Return the combined verification status."""

        statuses = (
            self.wing_verification.status,
            self.battery_verification.status,
        )

        if all(status == "PASS" for status in statuses):
            return "PASS"

        return "FAIL"


def analyze_aircraft(aircraft: Aircraft) -> UAVAnalysisResult:
    """Run preliminary engineering analyses and independent verification."""

    wing_result = calculate_wing_sizing(
        wing_span_m=aircraft.geometry.wing_span_m,
        mean_chord_m=aircraft.geometry.mean_chord_m,
        aircraft_mass_kg=aircraft.mass.aircraft_mass_kg,
    )

    battery_result = analyze_battery(
        cell_count=aircraft.battery.cell_count,
        capacity_ah=aircraft.battery.capacity_ah,
        discharge_c=aircraft.battery.discharge_c,
    )

    wing_verification = verify_wing_sizing(
        wing_span_m=aircraft.geometry.wing_span_m,
        mean_chord_m=aircraft.geometry.mean_chord_m,
        aircraft_mass_kg=aircraft.mass.aircraft_mass_kg,
        result=wing_result,
    )

    battery_verification = verify_battery(
        cell_count=aircraft.battery.cell_count,
        capacity_ah=aircraft.battery.capacity_ah,
        discharge_c=aircraft.battery.discharge_c,
        result=battery_result,
    )

    return UAVAnalysisResult(
        wing=wing_result,
        battery=battery_result,
        wing_verification=wing_verification,
        battery_verification=battery_verification,
    )
