"""Core aircraft data models for MCore UAV Layout & Sizing."""

from dataclasses import dataclass, field

from app.models.design import DesignRequirements
from app.models.mass_properties import MassProperties


@dataclass
class AircraftGeometry:
    """Basic aircraft geometry in SI units."""

    wing_span_m: float
    mean_chord_m: float

    @property
    def wing_area_m2(self) -> float:
        return self.wing_span_m * self.mean_chord_m


@dataclass
class AircraftMass:
    """Aircraft design mass in kilograms."""

    aircraft_mass_kg: float


@dataclass
class Battery:
    """Basic battery electrical properties."""

    cell_count: int
    capacity_ah: float
    discharge_c: float

    @property
    def nominal_voltage_v(self) -> float:
        return self.cell_count * 3.7

    @property
    def nominal_energy_wh(self) -> float:
        return self.nominal_voltage_v * self.capacity_ah

    @property
    def theoretical_max_current_a(self) -> float:
        return self.capacity_ah * self.discharge_c


@dataclass
class Propulsion:
    """Basic propulsion configuration."""

    motor_kv: float
    propeller_diameter_in: float
    propeller_pitch_in: float


@dataclass
class Aircraft:
    """Top-level UAV configuration and traceable design state."""

    name: str
    geometry: AircraftGeometry
    mass: AircraftMass
    propulsion: Propulsion
    battery: Battery
    requirements: DesignRequirements = field(default_factory=DesignRequirements)
    mass_properties: MassProperties = field(default_factory=MassProperties)
