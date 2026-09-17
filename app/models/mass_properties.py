"""Mass properties data models for MCore UAV projects."""

from dataclasses import dataclass, field


@dataclass
class MassItem:
    """A physical aircraft component with mass and position."""

    name: str
    mass_kg: float
    x_m: float
    y_m: float
    z_m: float
    source: str = "ESTIMATED"
    uncertainty_kg: float = 0.0

    @property
    def moment_x_kg_m(self) -> float:
        """Return the mass moment about the X datum."""

        return self.mass_kg * self.x_m

    @property
    def moment_y_kg_m(self) -> float:
        """Return the mass moment about the Y datum."""

        return self.mass_kg * self.y_m

    @property
    def moment_z_kg_m(self) -> float:
        """Return the mass moment about the Z datum."""

        return self.mass_kg * self.z_m


@dataclass
class MassProperties:
    """Collection of aircraft mass items and calculated mass properties."""

    items: list[MassItem] = field(default_factory=list)

    @property
    def total_mass_kg(self) -> float:
        """Return the combined mass of all mass items."""

        return sum(
            item.mass_kg
            for item in self.items
        )

    @property
    def total_moment_x_kg_m(self) -> float:
        """Return the total mass moment in the X direction."""

        return sum(
            item.moment_x_kg_m
            for item in self.items
        )

    @property
    def total_moment_y_kg_m(self) -> float:
        """Return the total mass moment in the Y direction."""

        return sum(
            item.moment_y_kg_m
            for item in self.items
        )

    @property
    def total_moment_z_kg_m(self) -> float:
        """Return the total mass moment in the Z direction."""

        return sum(
            item.moment_z_kg_m
            for item in self.items
        )

    @property
    def cg_x_m(self) -> float:
        """Return longitudinal center-of-gravity position."""

        if self.total_mass_kg == 0.0:
            return 0.0

        return (
            self.total_moment_x_kg_m
            / self.total_mass_kg
        )

    @property
    def cg_y_m(self) -> float:
        """Return lateral center-of-gravity position."""

        if self.total_mass_kg == 0.0:
            return 0.0

        return (
            self.total_moment_y_kg_m
            / self.total_mass_kg
        )

    @property
    def cg_z_m(self) -> float:
        """Return vertical center-of-gravity position."""

        if self.total_mass_kg == 0.0:
            return 0.0

        return (
            self.total_moment_z_kg_m
            / self.total_mass_kg
        )
