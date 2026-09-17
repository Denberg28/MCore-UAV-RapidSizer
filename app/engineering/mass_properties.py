"""Deterministic mass-properties calculations for MCore."""

from dataclasses import dataclass
from typing import Iterable

from app.models.mass_properties import MassItem


@dataclass(frozen=True)
class MassPropertiesResult:
    """Calculated aircraft mass-properties result."""

    total_mass_kg: float
    total_moment_x_kg_m: float
    total_moment_y_kg_m: float
    total_moment_z_kg_m: float
    cg_x_m: float
    cg_y_m: float
    cg_z_m: float
    item_count: int
    measured_mass_kg: float
    estimated_mass_kg: float
    total_uncertainty_kg_rss: float

    @property
    def measured_mass_fraction(self) -> float:
        if self.total_mass_kg == 0.0:
            return 0.0
        return self.measured_mass_kg / self.total_mass_kg

    @property
    def estimated_mass_fraction(self) -> float:
        if self.total_mass_kg == 0.0:
            return 0.0
        return self.estimated_mass_kg / self.total_mass_kg


def calculate_mass_properties(
    items: Iterable[MassItem],
) -> MassPropertiesResult:
    """Calculate component mass moments and three-axis center of gravity."""

    item_list = list(items)

    for item in item_list:
        if item.mass_kg < 0:
            raise ValueError(
                f"Mass for '{item.name}' cannot be negative."
            )
        if item.uncertainty_kg < 0:
            raise ValueError(
                f"Uncertainty for '{item.name}' cannot be negative."
            )

    total_mass_kg = sum(item.mass_kg for item in item_list)
    total_moment_x = sum(item.mass_kg * item.x_m for item in item_list)
    total_moment_y = sum(item.mass_kg * item.y_m for item in item_list)
    total_moment_z = sum(item.mass_kg * item.z_m for item in item_list)

    if total_mass_kg == 0.0:
        cg_x = cg_y = cg_z = 0.0
    else:
        cg_x = total_moment_x / total_mass_kg
        cg_y = total_moment_y / total_mass_kg
        cg_z = total_moment_z / total_mass_kg

    measured_mass_kg = sum(
        item.mass_kg
        for item in item_list
        if item.source.strip().upper() == "MEASURED"
    )
    estimated_mass_kg = total_mass_kg - measured_mass_kg
    total_uncertainty_kg_rss = sum(
        item.uncertainty_kg**2 for item in item_list
    ) ** 0.5

    return MassPropertiesResult(
        total_mass_kg=total_mass_kg,
        total_moment_x_kg_m=total_moment_x,
        total_moment_y_kg_m=total_moment_y,
        total_moment_z_kg_m=total_moment_z,
        cg_x_m=cg_x,
        cg_y_m=cg_y,
        cg_z_m=cg_z,
        item_count=len(item_list),
        measured_mass_kg=measured_mass_kg,
        estimated_mass_kg=estimated_mass_kg,
        total_uncertainty_kg_rss=total_uncertainty_kg_rss,
    )
