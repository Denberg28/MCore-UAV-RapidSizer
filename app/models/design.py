"""Requirements and result-neutral data models for rapid UAV sizing."""

from dataclasses import dataclass


@dataclass
class DesignRequirements:
    """User-controlled preliminary design requirements and assumptions.

    Values are intentionally explicit so the sizing result is traceable.
    Defaults are starting assumptions for a small conventional fixed-wing UAV,
    not certification limits and not universal design rules.
    """

    stall_speed_m_s: float = 10.0
    cruise_speed_m_s: float = 15.0
    endurance_min: float = 20.0
    climb_rate_m_s: float = 2.0
    aspect_ratio_target: float = 7.0
    cl_max: float = 1.2
    cd0: float = 0.035
    oswald_efficiency: float = 0.80
    propulsive_efficiency: float = 0.65
    battery_reserve_fraction: float = 0.20
    air_density_kg_m3: float = 1.225
    thrust_to_weight_target: float = 0.60
    horizontal_tail_volume_coefficient: float = 0.50
    vertical_tail_volume_coefficient: float = 0.04
    tail_arm_chord_ratio: float = 3.0
    horizontal_tail_aspect_ratio: float = 4.0
    vertical_tail_aspect_ratio: float = 1.8
    wing_le_x_m: float = 0.0
    cg_forward_mac_percent: float = 20.0
    cg_aft_mac_percent: float = 30.0

    @property
    def usable_battery_fraction(self) -> float:
        return 1.0 - self.battery_reserve_fraction
