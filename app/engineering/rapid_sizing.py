"""Requirements-driven preliminary fixed-wing UAV sizing.

The equations in this module are deterministic conceptual/preliminary-design
relations. They support rapid prototyping and trade studies; they do not
replace aerodynamic analysis, propulsion test data, structural substantiation,
or flight testing.
"""

from dataclasses import dataclass
from math import pi, sqrt

from app.models.design import DesignRequirements

GRAVITY_M_S2 = 9.80665


@dataclass(frozen=True)
class RapidSizingResult:
    """Calculated rapid-sizing outputs for a conventional fixed-wing UAV."""

    required_wing_area_m2: float
    recommended_span_m: float
    recommended_mean_chord_m: float
    wing_loading_n_m2: float
    wing_loading_kg_m2: float
    cruise_dynamic_pressure_pa: float
    cruise_cl: float
    induced_drag_factor: float
    cruise_cd: float
    cruise_drag_n: float
    aerodynamic_cruise_power_w: float
    electrical_cruise_power_w: float
    electrical_climb_power_w: float
    cruise_current_a: float
    climb_current_a: float
    required_nominal_energy_wh: float
    required_capacity_ah: float
    available_usable_energy_wh: float
    predicted_endurance_min: float
    required_static_thrust_n: float
    battery_theoretical_current_margin_a: float
    tail_arm_m: float
    horizontal_tail_area_m2: float
    horizontal_tail_span_m: float
    horizontal_tail_mean_chord_m: float
    vertical_tail_area_m2: float
    vertical_tail_height_m: float
    vertical_tail_mean_chord_m: float


def _require_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")


def _require_fraction(name: str, value: float) -> None:
    if not 0 < value <= 1:
        raise ValueError(f"{name} must be greater than 0 and at most 1.")


def validate_requirements(requirements: DesignRequirements) -> None:
    """Validate preliminary design requirements and assumptions."""

    _require_positive("Stall speed", requirements.stall_speed_m_s)
    _require_positive("Cruise speed", requirements.cruise_speed_m_s)
    _require_positive("Endurance", requirements.endurance_min)
    _require_positive("Climb rate", requirements.climb_rate_m_s)
    _require_positive("Aspect ratio target", requirements.aspect_ratio_target)
    _require_positive("CLmax", requirements.cl_max)
    _require_positive("CD0", requirements.cd0)
    _require_fraction("Oswald efficiency", requirements.oswald_efficiency)
    _require_fraction(
        "Propulsive efficiency",
        requirements.propulsive_efficiency,
    )
    _require_positive("Air density", requirements.air_density_kg_m3)
    _require_positive(
        "Thrust-to-weight target",
        requirements.thrust_to_weight_target,
    )
    _require_positive("Horizontal tail volume coefficient", requirements.horizontal_tail_volume_coefficient)
    _require_positive("Vertical tail volume coefficient", requirements.vertical_tail_volume_coefficient)
    _require_positive("Tail arm/chord ratio", requirements.tail_arm_chord_ratio)
    _require_positive("Horizontal tail aspect ratio", requirements.horizontal_tail_aspect_ratio)
    _require_positive("Vertical tail aspect ratio", requirements.vertical_tail_aspect_ratio)

    if not 0 <= requirements.battery_reserve_fraction < 1:
        raise ValueError(
            "Battery reserve fraction must be at least 0 and less than 1."
        )

    if requirements.cruise_speed_m_s <= requirements.stall_speed_m_s:
        raise ValueError("Cruise speed must be greater than stall speed.")

    if not (
        0 <= requirements.cg_forward_mac_percent
        < requirements.cg_aft_mac_percent
        <= 100
    ):
        raise ValueError(
            "CG target range must satisfy 0 <= forward < aft <= 100 percent MAC."
        )


def calculate_required_wing_area(
    aircraft_mass_kg: float,
    stall_speed_m_s: float,
    cl_max: float,
    air_density_kg_m3: float = 1.225,
) -> float:
    """Size wing area from the level-flight stall relation.

    S = 2 W / (rho * Vs^2 * CLmax)
    """

    _require_positive("Aircraft mass", aircraft_mass_kg)
    _require_positive("Stall speed", stall_speed_m_s)
    _require_positive("CLmax", cl_max)
    _require_positive("Air density", air_density_kg_m3)

    weight_n = aircraft_mass_kg * GRAVITY_M_S2
    return (2.0 * weight_n) / (
        air_density_kg_m3 * stall_speed_m_s**2 * cl_max
    )


def calculate_rectangular_wing_geometry(
    wing_area_m2: float,
    aspect_ratio: float,
) -> tuple[float, float]:
    """Return span and mean chord for a rectangular reference wing."""

    _require_positive("Wing area", wing_area_m2)
    _require_positive("Aspect ratio", aspect_ratio)

    span_m = sqrt(aspect_ratio * wing_area_m2)
    mean_chord_m = wing_area_m2 / span_m
    return span_m, mean_chord_m


def calculate_stall_speed(
    aircraft_mass_kg: float,
    wing_area_m2: float,
    cl_max: float,
    air_density_kg_m3: float = 1.225,
) -> float:
    """Calculate 1-g stall speed for the supplied wing and CLmax."""

    _require_positive("Aircraft mass", aircraft_mass_kg)
    _require_positive("Wing area", wing_area_m2)
    _require_positive("CLmax", cl_max)
    _require_positive("Air density", air_density_kg_m3)

    weight_n = aircraft_mass_kg * GRAVITY_M_S2
    return sqrt(
        (2.0 * weight_n)
        / (air_density_kg_m3 * wing_area_m2 * cl_max)
    )


def calculate_rapid_sizing(
    aircraft_mass_kg: float,
    battery_nominal_voltage_v: float,
    battery_capacity_ah: float,
    battery_theoretical_max_current_a: float,
    requirements: DesignRequirements,
) -> RapidSizingResult:
    """Run the requirements-driven preliminary sizing calculation."""

    _require_positive("Aircraft mass", aircraft_mass_kg)
    _require_positive("Battery nominal voltage", battery_nominal_voltage_v)
    _require_positive("Battery capacity", battery_capacity_ah)
    _require_positive(
        "Battery theoretical maximum current",
        battery_theoretical_max_current_a,
    )
    validate_requirements(requirements)

    weight_n = aircraft_mass_kg * GRAVITY_M_S2

    area_m2 = calculate_required_wing_area(
        aircraft_mass_kg=aircraft_mass_kg,
        stall_speed_m_s=requirements.stall_speed_m_s,
        cl_max=requirements.cl_max,
        air_density_kg_m3=requirements.air_density_kg_m3,
    )
    span_m, chord_m = calculate_rectangular_wing_geometry(
        wing_area_m2=area_m2,
        aspect_ratio=requirements.aspect_ratio_target,
    )

    wing_loading_n_m2 = weight_n / area_m2
    wing_loading_kg_m2 = aircraft_mass_kg / area_m2

    q = (
        0.5
        * requirements.air_density_kg_m3
        * requirements.cruise_speed_m_s**2
    )
    cruise_cl = weight_n / (q * area_m2)
    k = 1.0 / (
        pi
        * requirements.oswald_efficiency
        * requirements.aspect_ratio_target
    )
    cruise_cd = requirements.cd0 + k * cruise_cl**2
    cruise_drag_n = q * area_m2 * cruise_cd
    aerodynamic_cruise_power_w = (
        cruise_drag_n * requirements.cruise_speed_m_s
    )
    electrical_cruise_power_w = (
        aerodynamic_cruise_power_w
        / requirements.propulsive_efficiency
    )

    climb_mechanical_power_w = (
        aerodynamic_cruise_power_w
        + weight_n * requirements.climb_rate_m_s
    )
    electrical_climb_power_w = (
        climb_mechanical_power_w
        / requirements.propulsive_efficiency
    )

    cruise_current_a = (
        electrical_cruise_power_w
        / battery_nominal_voltage_v
    )
    climb_current_a = (
        electrical_climb_power_w
        / battery_nominal_voltage_v
    )

    mission_energy_wh = (
        electrical_cruise_power_w
        * requirements.endurance_min
        / 60.0
    )
    required_nominal_energy_wh = (
        mission_energy_wh
        / requirements.usable_battery_fraction
    )
    required_capacity_ah = (
        required_nominal_energy_wh
        / battery_nominal_voltage_v
    )

    battery_nominal_energy_wh = (
        battery_nominal_voltage_v * battery_capacity_ah
    )
    available_usable_energy_wh = (
        battery_nominal_energy_wh
        * requirements.usable_battery_fraction
    )
    predicted_endurance_min = (
        available_usable_energy_wh
        / electrical_cruise_power_w
        * 60.0
    )

    required_static_thrust_n = (
        requirements.thrust_to_weight_target * weight_n
    )
    battery_theoretical_current_margin_a = (
        battery_theoretical_max_current_a - climb_current_a
    )

    tail_arm_m = requirements.tail_arm_chord_ratio * chord_m
    horizontal_tail_area_m2 = (
        requirements.horizontal_tail_volume_coefficient
        * area_m2
        * chord_m
        / tail_arm_m
    )
    horizontal_tail_span_m = sqrt(
        requirements.horizontal_tail_aspect_ratio
        * horizontal_tail_area_m2
    )
    horizontal_tail_mean_chord_m = (
        horizontal_tail_area_m2 / horizontal_tail_span_m
    )

    vertical_tail_area_m2 = (
        requirements.vertical_tail_volume_coefficient
        * area_m2
        * span_m
        / tail_arm_m
    )
    vertical_tail_height_m = sqrt(
        requirements.vertical_tail_aspect_ratio
        * vertical_tail_area_m2
    )
    vertical_tail_mean_chord_m = (
        vertical_tail_area_m2 / vertical_tail_height_m
    )

    return RapidSizingResult(
        required_wing_area_m2=area_m2,
        recommended_span_m=span_m,
        recommended_mean_chord_m=chord_m,
        wing_loading_n_m2=wing_loading_n_m2,
        wing_loading_kg_m2=wing_loading_kg_m2,
        cruise_dynamic_pressure_pa=q,
        cruise_cl=cruise_cl,
        induced_drag_factor=k,
        cruise_cd=cruise_cd,
        cruise_drag_n=cruise_drag_n,
        aerodynamic_cruise_power_w=aerodynamic_cruise_power_w,
        electrical_cruise_power_w=electrical_cruise_power_w,
        electrical_climb_power_w=electrical_climb_power_w,
        cruise_current_a=cruise_current_a,
        climb_current_a=climb_current_a,
        required_nominal_energy_wh=required_nominal_energy_wh,
        required_capacity_ah=required_capacity_ah,
        available_usable_energy_wh=available_usable_energy_wh,
        predicted_endurance_min=predicted_endurance_min,
        required_static_thrust_n=required_static_thrust_n,
        battery_theoretical_current_margin_a=(
            battery_theoretical_current_margin_a
        ),
        tail_arm_m=tail_arm_m,
        horizontal_tail_area_m2=horizontal_tail_area_m2,
        horizontal_tail_span_m=horizontal_tail_span_m,
        horizontal_tail_mean_chord_m=horizontal_tail_mean_chord_m,
        vertical_tail_area_m2=vertical_tail_area_m2,
        vertical_tail_height_m=vertical_tail_height_m,
        vertical_tail_mean_chord_m=vertical_tail_mean_chord_m,
    )
