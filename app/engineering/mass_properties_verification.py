"""Independent verification for MCore mass-properties calculations."""

from dataclasses import dataclass, field
from math import isclose
from typing import Iterable

from app.engineering.mass_properties import MassPropertiesResult
from app.models.mass_properties import MassItem


@dataclass(frozen=True)
class MassPropertiesVerificationResult:
    status: str
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


def verify_mass_properties(
    items: Iterable[MassItem],
    result: MassPropertiesResult,
    rel_tol: float = 1e-9,
    abs_tol: float = 1e-12,
) -> MassPropertiesVerificationResult:
    """Independently recalculate the principal mass-properties outputs."""

    item_list = list(items)
    errors: list[str] = []

    expected_mass = sum(item.mass_kg for item in item_list)
    mx = sum(item.mass_kg * item.x_m for item in item_list)
    my = sum(item.mass_kg * item.y_m for item in item_list)
    mz = sum(item.mass_kg * item.z_m for item in item_list)

    if expected_mass == 0.0:
        cgx = cgy = cgz = 0.0
    else:
        cgx = mx / expected_mass
        cgy = my / expected_mass
        cgz = mz / expected_mass

    expected_measured = sum(
        item.mass_kg
        for item in item_list
        if item.source.strip().upper() == "MEASURED"
    )
    expected_estimated = expected_mass - expected_measured

    checks = (
        ("Total mass", result.total_mass_kg, expected_mass),
        ("X moment", result.total_moment_x_kg_m, mx),
        ("Y moment", result.total_moment_y_kg_m, my),
        ("Z moment", result.total_moment_z_kg_m, mz),
        ("CG X", result.cg_x_m, cgx),
        ("CG Y", result.cg_y_m, cgy),
        ("CG Z", result.cg_z_m, cgz),
        ("Measured mass", result.measured_mass_kg, expected_measured),
        ("Estimated mass", result.estimated_mass_kg, expected_estimated),
    )

    for name, actual, expected in checks:
        if not isclose(actual, expected, rel_tol=rel_tol, abs_tol=abs_tol):
            errors.append(
                f"{name} verification failed: expected {expected}, got {actual}."
            )

    if result.item_count != len(item_list):
        errors.append(
            "Item count verification failed: "
            f"expected {len(item_list)}, got {result.item_count}."
        )

    return MassPropertiesVerificationResult(
        status="PASS" if not errors else "FAIL",
        errors=errors,
    )
