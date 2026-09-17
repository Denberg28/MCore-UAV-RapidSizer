"""Integrated requirements-to-checks rapid UAV design service."""

from dataclasses import dataclass, replace

from app.engineering.mass_properties import (
    MassPropertiesResult,
    calculate_mass_properties,
)
from app.engineering.mass_properties_verification import (
    MassPropertiesVerificationResult,
    verify_mass_properties,
)
from app.engineering.rapid_sizing import (
    RapidSizingResult,
    calculate_rapid_sizing,
    calculate_stall_speed,
)
from app.models.aircraft import Aircraft, AircraftGeometry


@dataclass(frozen=True)
class DesignCheck:
    name: str
    status: str
    message: str


@dataclass(frozen=True)
class RapidDesignAssessment:
    sizing: RapidSizingResult
    actual_stall_speed_m_s: float
    mass_properties: MassPropertiesResult
    mass_verification: MassPropertiesVerificationResult
    cg_percent_mac: float | None
    checks: tuple[DesignCheck, ...]

    @property
    def overall_status(self) -> str:
        """Preliminary requirement status; never a flight-safety approval."""

        if any(check.status == "FAIL" for check in self.checks):
            return "FAIL"
        if any(check.status in {"CHECK", "NOT CHECKED"} for check in self.checks):
            return "CHECK"
        return "PASS"


def _caap_mass_message(mass_kg: float) -> str:
    if mass_kg < 7.0:
        return "Below the CAAP 7 kg Large-RPA threshold."
    if mass_kg <= 25.0:
        return (
            "At or above the CAAP 7 kg Large-RPA threshold and within the "
            "25 kg Open-category mass ceiling; other operating conditions still apply."
        )
    return (
        "Above the CAAP 25 kg Open-category mass ceiling; a different regulatory "
        "path is required for Philippine operations."
    )


def assess_rapid_design(aircraft: Aircraft) -> RapidDesignAssessment:
    """Evaluate geometry, mission energy, battery, mass budget, and CG."""

    sizing = calculate_rapid_sizing(
        aircraft_mass_kg=aircraft.mass.aircraft_mass_kg,
        battery_nominal_voltage_v=aircraft.battery.nominal_voltage_v,
        battery_capacity_ah=aircraft.battery.capacity_ah,
        battery_theoretical_max_current_a=(
            aircraft.battery.theoretical_max_current_a
        ),
        requirements=aircraft.requirements,
    )

    actual_stall_speed = calculate_stall_speed(
        aircraft_mass_kg=aircraft.mass.aircraft_mass_kg,
        wing_area_m2=aircraft.geometry.wing_area_m2,
        cl_max=aircraft.requirements.cl_max,
        air_density_kg_m3=aircraft.requirements.air_density_kg_m3,
    )

    mass_result = calculate_mass_properties(aircraft.mass_properties.items)
    mass_verification = verify_mass_properties(
        aircraft.mass_properties.items,
        mass_result,
    )

    checks: list[DesignCheck] = []

    checks.append(
        DesignCheck(
            name="Stall-speed requirement",
            status=(
                "PASS"
                if actual_stall_speed <= aircraft.requirements.stall_speed_m_s
                else "CHECK"
            ),
            message=(
                f"Calculated {actual_stall_speed:.2f} m/s vs target "
                f"{aircraft.requirements.stall_speed_m_s:.2f} m/s."
            ),
        )
    )

    checks.append(
        DesignCheck(
            name="Mission endurance energy",
            status=(
                "PASS"
                if sizing.predicted_endurance_min
                >= aircraft.requirements.endurance_min
                else "CHECK"
            ),
            message=(
                f"Predicted {sizing.predicted_endurance_min:.1f} min vs target "
                f"{aircraft.requirements.endurance_min:.1f} min using the stated "
                "reserve and efficiency assumptions."
            ),
        )
    )

    checks.append(
        DesignCheck(
            name="Battery current capability",
            status=(
                "PASS"
                if sizing.battery_theoretical_current_margin_a >= 0
                else "CHECK"
            ),
            message=(
                f"Theoretical C-rating margin at calculated climb power: "
                f"{sizing.battery_theoretical_current_margin_a:.1f} A. "
                "Validate with measured voltage/current/temperature data."
            ),
        )
    )

    cg_percent_mac: float | None = None
    if mass_result.total_mass_kg > 0:
        mass_difference = (
            mass_result.total_mass_kg - aircraft.mass.aircraft_mass_kg
        )
        relative_difference = abs(mass_difference) / aircraft.mass.aircraft_mass_kg
        checks.append(
            DesignCheck(
                name="Mass budget closure",
                status="PASS" if relative_difference <= 0.05 else "CHECK",
                message=(
                    f"Inventory {mass_result.total_mass_kg:.3f} kg vs design mass "
                    f"{aircraft.mass.aircraft_mass_kg:.3f} kg; delta "
                    f"{mass_difference:+.3f} kg."
                ),
            )
        )

        cg_percent_mac = (
            (mass_result.cg_x_m - aircraft.requirements.wing_le_x_m)
            / aircraft.geometry.mean_chord_m
            * 100.0
        )
        cg_ok = (
            aircraft.requirements.cg_forward_mac_percent
            <= cg_percent_mac
            <= aircraft.requirements.cg_aft_mac_percent
        )
        checks.append(
            DesignCheck(
                name="CG target envelope",
                status="PASS" if cg_ok else "CHECK",
                message=(
                    f"CG {cg_percent_mac:.1f}% MAC vs user target "
                    f"{aircraft.requirements.cg_forward_mac_percent:.1f}–"
                    f"{aircraft.requirements.cg_aft_mac_percent:.1f}% MAC. "
                    "This is a design target, not a certified envelope."
                ),
            )
        )
        checks.append(
            DesignCheck(
                name="Mass-data maturity",
                status=(
                    "PASS"
                    if mass_result.measured_mass_fraction >= 0.80
                    else "CHECK"
                ),
                message=(
                    f"Measured mass covers "
                    f"{mass_result.measured_mass_fraction * 100:.1f}% of the inventory. "
                    "Target at least 80% measured mass before advanced prototype testing."
                ),
            )
        )
    else:
        checks.append(
            DesignCheck(
                name="Mass budget closure",
                status="NOT CHECKED",
                message="Add component mass items to close the mass budget.",
            )
        )
        checks.append(
            DesignCheck(
                name="CG target envelope",
                status="NOT CHECKED",
                message=(
                    "Add component mass/position data using the same datum as "
                    "wing_le_x_m."
                ),
            )
        )
        checks.append(
            DesignCheck(
                name="Mass-data maturity",
                status="NOT CHECKED",
                message="No component mass inventory is available.",
            )
        )

    checks.append(
        DesignCheck(
            name="Mass-properties verification",
            status=mass_verification.status,
            message=(
                "Independent moment/CG recalculation completed."
                if mass_verification.passed
                else "; ".join(mass_verification.errors)
            ),
        )
    )

    checks.append(
        DesignCheck(
            name="Philippines / CAAP mass reference",
            status="INFO",
            message=_caap_mass_message(aircraft.mass.aircraft_mass_kg),
        )
    )

    return RapidDesignAssessment(
        sizing=sizing,
        actual_stall_speed_m_s=actual_stall_speed,
        mass_properties=mass_result,
        mass_verification=mass_verification,
        cg_percent_mac=cg_percent_mac,
        checks=tuple(checks),
    )


def apply_recommended_wing(aircraft: Aircraft) -> Aircraft:
    """Return a copy using the sizing engine's rectangular reference wing."""

    assessment = assess_rapid_design(aircraft)
    geometry = AircraftGeometry(
        wing_span_m=assessment.sizing.recommended_span_m,
        mean_chord_m=assessment.sizing.recommended_mean_chord_m,
    )
    return replace(aircraft, geometry=geometry)
