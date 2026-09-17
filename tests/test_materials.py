import pytest

from app.engineering.materials import estimate_sheet_mass, estimate_solid_mass


def test_sheet_mass_estimator():
    assert estimate_sheet_mass(0.5, 0.8, 2) == pytest.approx(0.8)


def test_solid_mass_estimator():
    assert estimate_solid_mass(0.001, 1200.0) == pytest.approx(1.2)
