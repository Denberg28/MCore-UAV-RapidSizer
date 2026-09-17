"""Validation utilities for MCore UAV projects."""

from dataclasses import dataclass, field

from app.models.aircraft import Aircraft


@dataclass
class ValidationResult:
    """Structured result of aircraft input validation."""

    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """Return True when no validation errors exist."""

        return len(self.errors) == 0

    @property
    def error_count(self) -> int:
        """Return the number of validation errors."""

        return len(self.errors)

    @property
    def summary(self) -> str:
        """Return a human-readable validation summary."""

        if self.valid:
            return "Validation passed."

        return (
            f"Validation failed with "
            f"{self.error_count} error(s)."
        )


def validate_aircraft(aircraft: Aircraft) -> ValidationResult:
    """Validate an Aircraft and return a structured result."""

    errors: list[str] = []

    geometry = aircraft.geometry
    mass = aircraft.mass
    propulsion = aircraft.propulsion
    battery = aircraft.battery
    requirements = aircraft.requirements

    # ---------------------------------------------------------
    # GEOMETRY
    # ---------------------------------------------------------

    if geometry.wing_span_m <= 0:
        errors.append(
            "Wing span must be greater than 0 m."
        )

    if geometry.mean_chord_m <= 0:
        errors.append(
            "Mean chord must be greater than 0 m."
        )

    # ---------------------------------------------------------
    # MASS
    # ---------------------------------------------------------

    if mass.aircraft_mass_kg <= 0:
        errors.append(
            "Aircraft mass must be greater than 0 kg."
        )

    # ---------------------------------------------------------
    # PROPULSION
    # ---------------------------------------------------------

    if propulsion.motor_kv <= 0:
        errors.append(
            "Motor KV must be greater than 0."
        )

    if propulsion.propeller_diameter_in <= 0:
        errors.append(
            "Propeller diameter must be greater than 0 in."
        )

    if propulsion.propeller_pitch_in <= 0:
        errors.append(
            "Propeller pitch must be greater than 0 in."
        )

    # ---------------------------------------------------------
    # BATTERY
    # ---------------------------------------------------------

    if battery.cell_count < 1:
        errors.append(
            "Battery cell count must be at least 1S."
        )

    if battery.capacity_ah <= 0:
        errors.append(
            "Battery capacity must be greater than 0 Ah."
        )

    if battery.discharge_c <= 0:
        errors.append(
            "Battery C-rating must be greater than 0."
        )


    # ---------------------------------------------------------
    # RAPID-DESIGN REQUIREMENTS
    # ---------------------------------------------------------

    if requirements.stall_speed_m_s <= 0:
        errors.append("Target stall speed must be greater than 0 m/s.")

    if requirements.cruise_speed_m_s <= requirements.stall_speed_m_s:
        errors.append("Cruise speed must be greater than target stall speed.")

    if requirements.endurance_min <= 0:
        errors.append("Target endurance must be greater than 0 min.")

    if requirements.climb_rate_m_s <= 0:
        errors.append("Target climb rate must be greater than 0 m/s.")

    if requirements.aspect_ratio_target <= 0:
        errors.append("Target aspect ratio must be greater than 0.")

    if requirements.cl_max <= 0:
        errors.append("CLmax must be greater than 0.")

    if requirements.cd0 <= 0:
        errors.append("CD0 must be greater than 0.")

    if not 0 < requirements.oswald_efficiency <= 1:
        errors.append("Oswald efficiency must be greater than 0 and at most 1.")

    if not 0 < requirements.propulsive_efficiency <= 1:
        errors.append("Propulsive efficiency must be greater than 0 and at most 1.")

    if not 0 <= requirements.battery_reserve_fraction < 1:
        errors.append("Battery reserve fraction must be at least 0 and less than 1.")

    if requirements.air_density_kg_m3 <= 0:
        errors.append("Air density must be greater than 0 kg/m^3.")

    if requirements.thrust_to_weight_target <= 0:
        errors.append("Thrust-to-weight target must be greater than 0.")

    if requirements.horizontal_tail_volume_coefficient <= 0:
        errors.append("Horizontal tail volume coefficient must be greater than 0.")

    if requirements.vertical_tail_volume_coefficient <= 0:
        errors.append("Vertical tail volume coefficient must be greater than 0.")

    if requirements.tail_arm_chord_ratio <= 0:
        errors.append("Tail arm/chord ratio must be greater than 0.")

    if requirements.horizontal_tail_aspect_ratio <= 0:
        errors.append("Horizontal tail aspect ratio must be greater than 0.")

    if requirements.vertical_tail_aspect_ratio <= 0:
        errors.append("Vertical tail aspect ratio must be greater than 0.")

    if not (
        0 <= requirements.cg_forward_mac_percent
        < requirements.cg_aft_mac_percent
        <= 100
    ):
        errors.append("CG target range must satisfy 0 <= forward < aft <= 100 percent MAC.")

    for item in aircraft.mass_properties.items:
        if item.mass_kg < 0:
            errors.append(f"Mass item '{item.name}' cannot have negative mass.")
        if item.uncertainty_kg < 0:
            errors.append(f"Mass item '{item.name}' cannot have negative uncertainty.")

    return ValidationResult(errors=errors)
