import pytest

from app.engineering.mass_properties import calculate_mass_properties
from app.models.mass_properties import MassItem


def test_mass_properties_engineering_tracks_source_and_uncertainty():
    items = [
        MassItem("Motor", 0.2, 0.1, 0.0, 0.0, "MEASURED", 0.002),
        MassItem("Wing", 0.3, 0.3, 0.0, 0.0, "ESTIMATED", 0.010),
    ]

    result = calculate_mass_properties(items)

    assert result.total_mass_kg == pytest.approx(0.5)
    assert result.cg_x_m == pytest.approx(0.22)
    assert result.measured_mass_kg == pytest.approx(0.2)
    assert result.estimated_mass_kg == pytest.approx(0.3)
    assert result.measured_mass_fraction == pytest.approx(0.4)
    assert result.total_uncertainty_kg_rss == pytest.approx((0.002**2 + 0.010**2) ** 0.5)


def test_mass_properties_engineering_rejects_negative_mass():
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_mass_properties(
            [MassItem("Invalid", -0.1, 0.0, 0.0, 0.0)]
        )
