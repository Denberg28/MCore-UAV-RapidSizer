from dataclasses import replace

from app.engineering.mass_properties import calculate_mass_properties
from app.engineering.mass_properties_verification import verify_mass_properties
from app.models.mass_properties import MassItem


def test_mass_properties_verifier_detects_corrupted_cg():
    items = [MassItem("Battery", 0.2, 0.3, 0.0, 0.0, "MEASURED")]
    result = calculate_mass_properties(items)
    corrupted = replace(result, cg_x_m=result.cg_x_m + 0.1)

    verification = verify_mass_properties(items, corrupted)

    assert verification.status == "FAIL"
    assert any("CG X" in error for error in verification.errors)
