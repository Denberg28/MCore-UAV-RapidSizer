import math

import pytest

from app.engineering.wing_sizing import (
    calculate_aspect_ratio,
    calculate_wing_area,
    calculate_wing_loading,
    calculate_wing_sizing,
)


def test_wing_area():
    area = calculate_wing_area(
        wing_span_m=1.20,
        mean_chord_m=0.20,
    )

    assert math.isclose(area, 0.24, rel_tol=1e-9)


def test_aspect_ratio():
    aspect_ratio = calculate_aspect_ratio(
        wing_span_m=1.20,
        wing_area_m2=0.24,
    )

    assert math.isclose(aspect_ratio, 6.0, rel_tol=1e-9)


def test_wing_loading():
    mass_loading, force_loading = calculate_wing_loading(
        aircraft_mass_kg=1.20,
        wing_area_m2=0.24,
    )

    assert math.isclose(mass_loading, 5.0, rel_tol=1e-9)
    assert math.isclose(force_loading, 49.05, rel_tol=1e-9)


def test_complete_wing_sizing():
    result = calculate_wing_sizing(
        wing_span_m=1.20,
        mean_chord_m=0.20,
        aircraft_mass_kg=1.20,
    )

    assert math.isclose(result.wing_area_m2, 0.24, rel_tol=1e-9)
    assert math.isclose(result.aspect_ratio, 6.0, rel_tol=1e-9)
    assert math.isclose(result.wing_loading_kg_m2, 5.0, rel_tol=1e-9)
    assert math.isclose(result.wing_loading_n_m2, 49.05, rel_tol=1e-9)


@pytest.mark.parametrize(
    "span, chord",
    [
        (0, 0.20),
        (-1.20, 0.20),
        (1.20, 0),
        (1.20, -0.20),
    ],
)
def test_invalid_wing_geometry(span, chord):
    with pytest.raises(ValueError):
        calculate_wing_area(span, chord)


def test_invalid_mass():
    with pytest.raises(ValueError):
        calculate_wing_loading(
            aircraft_mass_kg=0,
            wing_area_m2=0.24,
        )
