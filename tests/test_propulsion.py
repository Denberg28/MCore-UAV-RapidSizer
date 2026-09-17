import math

import pytest

from app.engineering.propulsion import (
    analyze_battery,
    calculate_battery_energy,
    calculate_electrical_power,
    calculate_nominal_voltage,
    calculate_theoretical_max_current,
)


def test_nominal_voltage():
    voltage = calculate_nominal_voltage(3)

    assert math.isclose(voltage, 11.1, rel_tol=1e-9)


def test_battery_energy():
    energy = calculate_battery_energy(
        nominal_voltage_v=11.1,
        capacity_ah=2.2,
    )

    assert math.isclose(energy, 24.42, rel_tol=1e-9)


def test_theoretical_max_current():
    current = calculate_theoretical_max_current(
        capacity_ah=2.2,
        discharge_c=30,
    )

    assert math.isclose(current, 66.0, rel_tol=1e-9)


def test_electrical_power():
    power = calculate_electrical_power(
        voltage_v=11.1,
        current_a=10,
    )

    assert math.isclose(power, 111.0, rel_tol=1e-9)


def test_complete_battery_analysis():
    result = analyze_battery(
        cell_count=3,
        capacity_ah=2.2,
        discharge_c=30,
    )

    assert math.isclose(result.nominal_voltage_v, 11.1, rel_tol=1e-9)
    assert math.isclose(result.nominal_energy_wh, 24.42, rel_tol=1e-9)
    assert math.isclose(
        result.theoretical_max_current_a,
        66.0,
        rel_tol=1e-9,
    )


@pytest.mark.parametrize(
    "cell_count",
    [0, -1],
)
def test_invalid_cell_count(cell_count):
    with pytest.raises(ValueError):
        calculate_nominal_voltage(cell_count)


def test_invalid_capacity():
    with pytest.raises(ValueError):
        calculate_battery_energy(
            nominal_voltage_v=11.1,
            capacity_ah=0,
        )


def test_invalid_c_rating():
    with pytest.raises(ValueError):
        calculate_theoretical_max_current(
            capacity_ah=2.2,
            discharge_c=0,
        )


def test_invalid_current():
    with pytest.raises(ValueError):
        calculate_electrical_power(
            voltage_v=11.1,
            current_a=-1,
        )
