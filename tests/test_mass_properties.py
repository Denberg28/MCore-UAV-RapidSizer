import pytest

from app.models.mass_properties import (
    MassItem,
    MassProperties,
)


def test_mass_item_calculates_moments():
    item = MassItem(
        name="Battery",
        mass_kg=0.2,
        x_m=0.3,
        y_m=0.1,
        z_m=0.05,
    )

    assert item.moment_x_kg_m == pytest.approx(0.06)
    assert item.moment_y_kg_m == pytest.approx(0.02)
    assert item.moment_z_kg_m == pytest.approx(0.01)


def test_mass_properties_calculates_total_mass():
    properties = MassProperties(
        items=[
            MassItem(
                name="Motor",
                mass_kg=0.2,
                x_m=0.1,
                y_m=0.0,
                z_m=0.0,
            ),
            MassItem(
                name="Battery",
                mass_kg=0.3,
                x_m=0.4,
                y_m=0.0,
                z_m=0.0,
            ),
        ]
    )

    assert properties.total_mass_kg == pytest.approx(0.5)


def test_mass_properties_calculates_total_moments():
    properties = MassProperties(
        items=[
            MassItem(
                name="Component A",
                mass_kg=0.2,
                x_m=0.1,
                y_m=-0.1,
                z_m=0.05,
            ),
            MassItem(
                name="Component B",
                mass_kg=0.3,
                x_m=0.4,
                y_m=0.2,
                z_m=0.10,
            ),
        ]
    )

    assert properties.total_moment_x_kg_m == pytest.approx(0.14)
    assert properties.total_moment_y_kg_m == pytest.approx(0.04)
    assert properties.total_moment_z_kg_m == pytest.approx(0.04)


def test_mass_properties_calculates_longitudinal_cg():
    properties = MassProperties(
        items=[
            MassItem(
                name="Motor",
                mass_kg=0.2,
                x_m=0.1,
                y_m=0.0,
                z_m=0.0,
            ),
            MassItem(
                name="Battery",
                mass_kg=0.3,
                x_m=0.4,
                y_m=0.0,
                z_m=0.0,
            ),
        ]
    )

    assert properties.cg_x_m == pytest.approx(0.28)
    assert properties.cg_y_m == pytest.approx(0.0)
    assert properties.cg_z_m == pytest.approx(0.0)


def test_mass_properties_calculates_three_axis_cg():
    properties = MassProperties(
        items=[
            MassItem(
                name="Component A",
                mass_kg=1.0,
                x_m=0.2,
                y_m=-0.1,
                z_m=0.05,
            ),
            MassItem(
                name="Component B",
                mass_kg=1.0,
                x_m=0.4,
                y_m=0.3,
                z_m=0.15,
            ),
        ]
    )

    assert properties.cg_x_m == pytest.approx(0.3)
    assert properties.cg_y_m == pytest.approx(0.1)
    assert properties.cg_z_m == pytest.approx(0.1)


def test_empty_mass_properties_returns_zero_values():
    properties = MassProperties()

    assert properties.total_mass_kg == pytest.approx(0.0)

    assert properties.total_moment_x_kg_m == pytest.approx(0.0)
    assert properties.total_moment_y_kg_m == pytest.approx(0.0)
    assert properties.total_moment_z_kg_m == pytest.approx(0.0)

    assert properties.cg_x_m == pytest.approx(0.0)
    assert properties.cg_y_m == pytest.approx(0.0)
    assert properties.cg_z_m == pytest.approx(0.0)


def test_mass_item_defaults_to_estimated_source():
    item = MassItem(
        name="Wing",
        mass_kg=0.3,
        x_m=0.5,
        y_m=0.0,
        z_m=0.0,
    )

    assert item.source == "ESTIMATED"
    assert item.uncertainty_kg == pytest.approx(0.0)


def test_mass_item_supports_measured_source():
    item = MassItem(
        name="Battery",
        mass_kg=0.245,
        x_m=0.32,
        y_m=0.0,
        z_m=0.04,
        source="MEASURED",
        uncertainty_kg=0.001,
    )

    assert item.source == "MEASURED"
    assert item.uncertainty_kg == pytest.approx(0.001)


def test_mass_properties_supports_symmetric_lateral_distribution():
    properties = MassProperties(
        items=[
            MassItem(
                name="Left Wing",
                mass_kg=0.25,
                x_m=0.35,
                y_m=-0.30,
                z_m=0.0,
            ),
            MassItem(
                name="Right Wing",
                mass_kg=0.25,
                x_m=0.35,
                y_m=0.30,
                z_m=0.0,
            ),
        ]
    )

    assert properties.total_mass_kg == pytest.approx(0.50)
    assert properties.cg_x_m == pytest.approx(0.35)
    assert properties.cg_y_m == pytest.approx(0.0)
    assert properties.cg_z_m == pytest.approx(0.0)
