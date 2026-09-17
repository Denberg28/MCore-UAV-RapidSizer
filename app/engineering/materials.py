"""Simple traceable material-mass estimators for rapid prototyping."""


def estimate_sheet_mass(
    area_m2: float,
    areal_density_kg_m2: float,
    quantity: float = 1.0,
) -> float:
    """Estimate mass from area and measured/specified areal density."""

    if area_m2 < 0:
        raise ValueError("Area cannot be negative.")
    if areal_density_kg_m2 < 0:
        raise ValueError("Areal density cannot be negative.")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")
    return area_m2 * areal_density_kg_m2 * quantity


def estimate_solid_mass(
    volume_m3: float,
    density_kg_m3: float,
    quantity: float = 1.0,
) -> float:
    """Estimate mass from volume and material density."""

    if volume_m3 < 0:
        raise ValueError("Volume cannot be negative.")
    if density_kg_m3 < 0:
        raise ValueError("Density cannot be negative.")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")
    return volume_m3 * density_kg_m3 * quantity
