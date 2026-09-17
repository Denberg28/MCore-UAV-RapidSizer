"""Deterministic verification of UAV engineering results."""

from dataclasses import dataclass
from math import isclose

from app.engineering.propulsion import BatteryAnalysis
from app.engineering.wing_sizing import WingSizingResult


@dataclass(frozen=True)
class VerificationCheck:
    """Result of one independent verification check."""

    name: str
    expected: float
    actual: float
    passed: bool


@dataclass(frozen=True)
class VerificationResult:
    """Combined verification result."""

    status: str
    checks: tuple[VerificationCheck, ...]


def verify_value(
    name: str,
    actual: float,
    expected: float,
    relative_tolerance: float = 1e-9,
) -> VerificationCheck:
    """Compare an engineering result against an independently calculated value."""

    passed = isclose(
        actual,
        expected,
        rel_tol=relative_tolerance,
        abs_tol=1e-12,
    )

    return VerificationCheck(
        name=name,
        expected=expected,
        actual=actual,
        passed=passed,
    )


def verify_wing_sizing(
    wing_span_m: float,
    mean_chord_m: float,
    aircraft_mass_kg: float,
    result: WingSizingResult,
) -> VerificationResult:
    """Independently verify the primary wing-sizing results."""

    expected_area = wing_span_m * mean_chord_m
    expected_aspect_ratio = (wing_span_m ** 2) / expected_area
    expected_mass_loading = aircraft_mass_kg / expected_area
    expected_force_loading = (
        aircraft_mass_kg * 9.81
    ) / expected_area

    checks = (
        verify_value(
            "Wing area",
            result.wing_area_m2,
            expected_area,
        ),
        verify_value(
            "Aspect ratio",
            result.aspect_ratio,
            expected_aspect_ratio,
        ),
        verify_value(
            "Mass wing loading",
            result.wing_loading_kg_m2,
            expected_mass_loading,
        ),
        verify_value(
            "Force wing loading",
            result.wing_loading_n_m2,
            expected_force_loading,
        ),
    )

    status = "PASS" if all(check.passed for check in checks) else "FAIL"

    return VerificationResult(
        status=status,
        checks=checks,
    )


def verify_battery(
    cell_count: int,
    capacity_ah: float,
    discharge_c: float,
    result: BatteryAnalysis,
    cell_nominal_voltage_v: float = 3.7,
) -> VerificationResult:
    """Independently verify the primary battery results."""

    expected_voltage = cell_count * cell_nominal_voltage_v
    expected_energy = expected_voltage * capacity_ah
    expected_current = capacity_ah * discharge_c

    checks = (
        verify_value(
            "Nominal voltage",
            result.nominal_voltage_v,
            expected_voltage,
        ),
        verify_value(
            "Nominal energy",
            result.nominal_energy_wh,
            expected_energy,
        ),
        verify_value(
            "Theoretical maximum current",
            result.theoretical_max_current_a,
            expected_current,
        ),
    )

    status = "PASS" if all(check.passed for check in checks) else "FAIL"

    return VerificationResult(
        status=status,
        checks=checks,
    )
