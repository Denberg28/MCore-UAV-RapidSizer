"""Preliminary UAV propulsion calculations.

All internal electrical calculations use SI-compatible units.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BatteryAnalysis:
    """Calculated battery properties."""

    nominal_voltage_v: float
    nominal_energy_wh: float
    theoretical_max_current_a: float


def calculate_nominal_voltage(
    cell_count: int,
    cell_nominal_voltage_v: float = 3.7,
) -> float:
    """Calculate nominal battery voltage."""

    if cell_count <= 0:
        raise ValueError("Cell count must be greater than zero.")

    if cell_nominal_voltage_v <= 0:
        raise ValueError("Cell nominal voltage must be greater than zero.")

    return cell_count * cell_nominal_voltage_v


def calculate_battery_energy(
    nominal_voltage_v: float,
    capacity_ah: float,
) -> float:
    """Calculate nominal battery energy.

    E = V × Ah
    """

    if nominal_voltage_v <= 0:
        raise ValueError("Nominal voltage must be greater than zero.")

    if capacity_ah <= 0:
        raise ValueError("Battery capacity must be greater than zero.")

    return nominal_voltage_v * capacity_ah


def calculate_theoretical_max_current(
    capacity_ah: float,
    discharge_c: float,
) -> float:
    """Calculate theoretical current from capacity and C-rating.

    I = Ah × C
    """

    if capacity_ah <= 0:
        raise ValueError("Battery capacity must be greater than zero.")

    if discharge_c <= 0:
        raise ValueError("Discharge C-rating must be greater than zero.")

    return capacity_ah * discharge_c


def calculate_electrical_power(
    voltage_v: float,
    current_a: float,
) -> float:
    """Calculate electrical input power.

    P = V × I
    """

    if voltage_v <= 0:
        raise ValueError("Voltage must be greater than zero.")

    if current_a < 0:
        raise ValueError("Current cannot be negative.")

    return voltage_v * current_a


def analyze_battery(
    cell_count: int,
    capacity_ah: float,
    discharge_c: float,
    cell_nominal_voltage_v: float = 3.7,
) -> BatteryAnalysis:
    """Calculate the primary battery properties."""

    voltage = calculate_nominal_voltage(
        cell_count,
        cell_nominal_voltage_v,
    )

    energy = calculate_battery_energy(
        voltage,
        capacity_ah,
    )

    max_current = calculate_theoretical_max_current(
        capacity_ah,
        discharge_c,
    )

    return BatteryAnalysis(
        nominal_voltage_v=voltage,
        nominal_energy_wh=energy,
        theoretical_max_current_a=max_current,
    )
