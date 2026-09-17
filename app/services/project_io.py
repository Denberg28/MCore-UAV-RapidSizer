"""Versioned project persistence for MCore UAV Layout & Sizing."""

import json
from pathlib import Path
from typing import Any

from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.models.design import DesignRequirements
from app.models.mass_properties import MassItem, MassProperties

PROJECT_SCHEMA_VERSION = "1.0"


def aircraft_to_dict(aircraft: Aircraft) -> dict[str, Any]:
    """Convert an Aircraft model into a JSON-compatible dictionary."""

    r = aircraft.requirements

    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "name": aircraft.name,
        "geometry": {
            "wing_span_m": aircraft.geometry.wing_span_m,
            "mean_chord_m": aircraft.geometry.mean_chord_m,
        },
        "mass": {
            "aircraft_mass_kg": aircraft.mass.aircraft_mass_kg,
        },
        "propulsion": {
            "motor_kv": aircraft.propulsion.motor_kv,
            "propeller_diameter_in": aircraft.propulsion.propeller_diameter_in,
            "propeller_pitch_in": aircraft.propulsion.propeller_pitch_in,
        },
        "battery": {
            "cell_count": aircraft.battery.cell_count,
            "capacity_ah": aircraft.battery.capacity_ah,
            "discharge_c": aircraft.battery.discharge_c,
        },
        "requirements": {
            "stall_speed_m_s": r.stall_speed_m_s,
            "cruise_speed_m_s": r.cruise_speed_m_s,
            "endurance_min": r.endurance_min,
            "climb_rate_m_s": r.climb_rate_m_s,
            "aspect_ratio_target": r.aspect_ratio_target,
            "cl_max": r.cl_max,
            "cd0": r.cd0,
            "oswald_efficiency": r.oswald_efficiency,
            "propulsive_efficiency": r.propulsive_efficiency,
            "battery_reserve_fraction": r.battery_reserve_fraction,
            "air_density_kg_m3": r.air_density_kg_m3,
            "thrust_to_weight_target": r.thrust_to_weight_target,
            "horizontal_tail_volume_coefficient": r.horizontal_tail_volume_coefficient,
            "vertical_tail_volume_coefficient": r.vertical_tail_volume_coefficient,
            "tail_arm_chord_ratio": r.tail_arm_chord_ratio,
            "horizontal_tail_aspect_ratio": r.horizontal_tail_aspect_ratio,
            "vertical_tail_aspect_ratio": r.vertical_tail_aspect_ratio,
            "wing_le_x_m": r.wing_le_x_m,
            "cg_forward_mac_percent": r.cg_forward_mac_percent,
            "cg_aft_mac_percent": r.cg_aft_mac_percent,
        },
        "mass_properties": {
            "items": [
                {
                    "name": item.name,
                    "mass_kg": item.mass_kg,
                    "x_m": item.x_m,
                    "y_m": item.y_m,
                    "z_m": item.z_m,
                    "source": item.source,
                    "uncertainty_kg": item.uncertainty_kg,
                }
                for item in aircraft.mass_properties.items
            ]
        },
    }


def _requirements_from_dict(data: dict[str, Any]) -> DesignRequirements:
    values = data.get("requirements", {})
    defaults = DesignRequirements()

    return DesignRequirements(
        stall_speed_m_s=values.get(
            "stall_speed_m_s", defaults.stall_speed_m_s
        ),
        cruise_speed_m_s=values.get(
            "cruise_speed_m_s", defaults.cruise_speed_m_s
        ),
        endurance_min=values.get("endurance_min", defaults.endurance_min),
        climb_rate_m_s=values.get("climb_rate_m_s", defaults.climb_rate_m_s),
        aspect_ratio_target=values.get(
            "aspect_ratio_target", defaults.aspect_ratio_target
        ),
        cl_max=values.get("cl_max", defaults.cl_max),
        cd0=values.get("cd0", defaults.cd0),
        oswald_efficiency=values.get(
            "oswald_efficiency", defaults.oswald_efficiency
        ),
        propulsive_efficiency=values.get(
            "propulsive_efficiency", defaults.propulsive_efficiency
        ),
        battery_reserve_fraction=values.get(
            "battery_reserve_fraction", defaults.battery_reserve_fraction
        ),
        air_density_kg_m3=values.get(
            "air_density_kg_m3", defaults.air_density_kg_m3
        ),
        thrust_to_weight_target=values.get(
            "thrust_to_weight_target", defaults.thrust_to_weight_target
        ),
        horizontal_tail_volume_coefficient=values.get(
            "horizontal_tail_volume_coefficient", defaults.horizontal_tail_volume_coefficient
        ),
        vertical_tail_volume_coefficient=values.get(
            "vertical_tail_volume_coefficient", defaults.vertical_tail_volume_coefficient
        ),
        tail_arm_chord_ratio=values.get(
            "tail_arm_chord_ratio", defaults.tail_arm_chord_ratio
        ),
        horizontal_tail_aspect_ratio=values.get(
            "horizontal_tail_aspect_ratio", defaults.horizontal_tail_aspect_ratio
        ),
        vertical_tail_aspect_ratio=values.get(
            "vertical_tail_aspect_ratio", defaults.vertical_tail_aspect_ratio
        ),
        wing_le_x_m=values.get("wing_le_x_m", defaults.wing_le_x_m),
        cg_forward_mac_percent=values.get(
            "cg_forward_mac_percent", defaults.cg_forward_mac_percent
        ),
        cg_aft_mac_percent=values.get(
            "cg_aft_mac_percent", defaults.cg_aft_mac_percent
        ),
    )


def _mass_properties_from_dict(data: dict[str, Any]) -> MassProperties:
    section = data.get("mass_properties", {})
    raw_items = section.get("items", [])
    items = [
        MassItem(
            name=item["name"],
            mass_kg=float(item["mass_kg"]),
            x_m=float(item["x_m"]),
            y_m=float(item.get("y_m", 0.0)),
            z_m=float(item.get("z_m", 0.0)),
            source=str(item.get("source", "ESTIMATED")),
            uncertainty_kg=float(item.get("uncertainty_kg", 0.0)),
        )
        for item in raw_items
    ]
    return MassProperties(items=items)


def aircraft_from_dict(data: dict[str, Any]) -> Aircraft:
    """Create an Aircraft model from current or legacy project data."""

    return Aircraft(
        name=data["name"],
        geometry=AircraftGeometry(
            wing_span_m=data["geometry"]["wing_span_m"],
            mean_chord_m=data["geometry"]["mean_chord_m"],
        ),
        mass=AircraftMass(
            aircraft_mass_kg=data["mass"]["aircraft_mass_kg"],
        ),
        propulsion=Propulsion(
            motor_kv=data["propulsion"]["motor_kv"],
            propeller_diameter_in=data["propulsion"]["propeller_diameter_in"],
            propeller_pitch_in=data["propulsion"]["propeller_pitch_in"],
        ),
        battery=Battery(
            cell_count=data["battery"]["cell_count"],
            capacity_ah=data["battery"]["capacity_ah"],
            discharge_c=data["battery"]["discharge_c"],
        ),
        requirements=_requirements_from_dict(data),
        mass_properties=_mass_properties_from_dict(data),
    )


def save_aircraft(aircraft: Aircraft, path: str | Path) -> None:
    """Save an Aircraft project as formatted versioned JSON."""

    project_path = Path(path)
    project_path.parent.mkdir(parents=True, exist_ok=True)

    with project_path.open("w", encoding="utf-8") as file:
        json.dump(aircraft_to_dict(aircraft), file, indent=4)


def load_aircraft(path: str | Path) -> Aircraft:
    """Load an Aircraft project from JSON, including legacy v0.1 files."""

    project_path = Path(path)
    with project_path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    return aircraft_from_dict(data)
