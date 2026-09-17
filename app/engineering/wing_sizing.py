"""Preliminary fixed-wing sizing calculations.

All internal dimensions use SI units.
"""

from dataclasses import dataclass


GRAVITY_M_S2 = 9.81


@dataclass(frozen=True)
class WingSizingResult:
    """Calculated preliminary wing-sizing parameters."""

    wing_area_m2: float
    aspect_ratio: float
    wing_loading_kg_m2: float
    wing_loading_n_m2: float


def calculate_wing_area(
    wing_span_m: float,
    mean_chord_m: float,
) -> float:
    """Calculate wing planform area.

    S = b × c
    """

    if wing_span_m <= 0:
        raise ValueError("Wing span must be greater than zero.")

    if mean_chord_m <= 0:
        raise ValueError("Mean chord must be greater than zero.")

    return wing_span_m * mean_chord_m


def calculate_aspect_ratio(
    wing_span_m: float,
    wing_area_m2: float,
) -> float:
    """Calculate wing aspect ratio.

    AR = b² / S
    """

    if wing_span_m <= 0:
        raise ValueError("Wing span must be greater than zero.")

    if wing_area_m2 <= 0:
        raise ValueError("Wing area must be greater than zero.")

    return (wing_span_m ** 2) / wing_area_m2


def calculate_wing_loading(
    aircraft_mass_kg: float,
    wing_area_m2: float,
) -> tuple[float, float]:
    """Calculate mass and force based wing loading.

    Mass loading:
        W/S = m / S

    Force loading:
        W/S = (m × g) / S
    """

    if aircraft_mass_kg <= 0:
        raise ValueError("Aircraft mass must be greater than zero.")

    if wing_area_m2 <= 0:
        raise ValueError("Wing area must be greater than zero.")

    mass_loading = aircraft_mass_kg / wing_area_m2
    force_loading = (aircraft_mass_kg * GRAVITY_M_S2) / wing_area_m2

    return mass_loading, force_loading


def calculate_wing_sizing(
    wing_span_m: float,
    mean_chord_m: float,
    aircraft_mass_kg: float,
) -> WingSizingResult:
    """Calculate the complete preliminary wing-sizing result."""

    area = calculate_wing_area(
        wing_span_m,
        mean_chord_m,
    )

    aspect_ratio = calculate_aspect_ratio(
        wing_span_m,
        area,
    )

    mass_loading, force_loading = calculate_wing_loading(
        aircraft_mass_kg,
        area,
    )

    return WingSizingResult(
        wing_area_m2=area,
        aspect_ratio=aspect_ratio,
        wing_loading_kg_m2=mass_loading,
        wing_loading_n_m2=force_loading,
    )
