import pytest

from app.engineering.rapid_sizing import (
    calculate_rapid_sizing,
    calculate_required_wing_area,
    calculate_stall_speed,
)
from app.models.design import DesignRequirements


def test_required_wing_area_inverts_stall_equation():
    area = calculate_required_wing_area(
        aircraft_mass_kg=1.2,
        stall_speed_m_s=10.0,
        cl_max=1.2,
        air_density_kg_m3=1.225,
    )

    stall = calculate_stall_speed(
        aircraft_mass_kg=1.2,
        wing_area_m2=area,
        cl_max=1.2,
        air_density_kg_m3=1.225,
    )

    assert area == pytest.approx(0.16010857142857143)
    assert stall == pytest.approx(10.0)


def test_rapid_sizing_reference_case():
    result = calculate_rapid_sizing(
        aircraft_mass_kg=1.2,
        battery_nominal_voltage_v=11.1,
        battery_capacity_ah=2.2,
        battery_theoretical_max_current_a=66.0,
        requirements=DesignRequirements(),
    )

    assert result.recommended_span_m == pytest.approx(1.0586595298)
    assert result.recommended_mean_chord_m == pytest.approx(0.1512370757)
    assert result.cruise_cl == pytest.approx(0.5333333333)
    assert result.electrical_cruise_power_w == pytest.approx(26.05436944)
    assert result.required_nominal_energy_wh == pytest.approx(10.85598726)
    assert result.predicted_endurance_min == pytest.approx(44.98899898)


def test_rapid_sizing_rejects_cruise_below_stall():
    requirements = DesignRequirements(
        stall_speed_m_s=10.0,
        cruise_speed_m_s=9.0,
    )

    with pytest.raises(ValueError, match="Cruise speed"):
        calculate_rapid_sizing(
            aircraft_mass_kg=1.2,
            battery_nominal_voltage_v=11.1,
            battery_capacity_ah=2.2,
            battery_theoretical_max_current_a=66.0,
            requirements=requirements,
        )
