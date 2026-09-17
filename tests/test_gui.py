"""Tests for the MCore UAV Layout & Sizing GUI."""

import os

os.environ.setdefault(
    "QT_QPA_PLATFORM",
    "offscreen",
)

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow
from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)


@pytest.fixture(scope="session")
def qapp():
    """Create one QApplication for the GUI test session."""

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


@pytest.fixture
def window(qapp):
    """Create a fresh MCore main window."""

    test_window = MainWindow()

    yield test_window

    test_window.close()


def make_test_aircraft() -> Aircraft:
    """Create a known-valid aircraft for GUI tests."""

    return Aircraft(
        name="GUI Test UAV",
        geometry=AircraftGeometry(
            wing_span_m=1.2,
            mean_chord_m=0.2,
        ),
        mass=AircraftMass(
            aircraft_mass_kg=1.2,
        ),
        propulsion=Propulsion(
            motor_kv=1500,
            propeller_diameter_in=8,
            propeller_pitch_in=6,
        ),
        battery=Battery(
            cell_count=3,
            capacity_ah=2.2,
            discharge_c=30,
        ),
    )


def populate_valid_inputs(window):
    """Populate the GUI with a known-valid configuration."""

    window.span_input.setText("1.5")
    window.chord_input.setText("0.2")
    window.mass_input.setText("1.4")

    window.kv_input.setText("1500")
    window.prop_diameter_input.setText("8")
    window.prop_pitch_input.setText("6")

    window.cell_count_input.setText("3")
    window.capacity_input.setText("2.2")
    window.c_rating_input.setText("30")


def test_gui_builds_aircraft_from_inputs(window):
    """GUI inputs should convert into an Aircraft model."""

    window.current_aircraft = make_test_aircraft()

    populate_valid_inputs(window)

    result = window._build_aircraft_from_inputs()

    assert isinstance(result, Aircraft)
    assert result.name == "GUI Test UAV"

    assert result.geometry.wing_span_m == 1.5
    assert result.geometry.mean_chord_m == 0.2

    assert result.mass.aircraft_mass_kg == 1.4

    assert result.propulsion.motor_kv == 1500
    assert result.propulsion.propeller_diameter_in == 8
    assert result.propulsion.propeller_pitch_in == 6

    assert result.battery.cell_count == 3
    assert result.battery.capacity_ah == 2.2
    assert result.battery.discharge_c == 30


def test_gui_build_aircraft_rejects_invalid_numeric_input(window):
    """Invalid numeric GUI input should fail conversion."""

    window.current_aircraft = make_test_aircraft()

    populate_valid_inputs(window)

    window.span_input.setText("not-a-number")

    with pytest.raises(ValueError):
        window._build_aircraft_from_inputs()


def test_gui_save_requires_loaded_project(window):
    """Save should require a loaded project."""

    assert window.current_project is None
    assert window.current_aircraft is None


def test_gui_populate_inputs_matches_aircraft(window):
    """GUI fields should reflect the Aircraft model."""

    aircraft = Aircraft(
        name="Populate Test UAV",
        geometry=AircraftGeometry(
            wing_span_m=1.35,
            mean_chord_m=0.22,
        ),
        mass=AircraftMass(
            aircraft_mass_kg=1.55,
        ),
        propulsion=Propulsion(
            motor_kv=1250,
            propeller_diameter_in=9,
            propeller_pitch_in=6,
        ),
        battery=Battery(
            cell_count=4,
            capacity_ah=3.0,
            discharge_c=40,
        ),
    )

    window._populate_inputs(aircraft)

    assert window.span_input.text() == "1.35"
    assert window.chord_input.text() == "0.22"
    assert window.mass_input.text() == "1.55"

    assert window.kv_input.text() == "1250"
    assert window.prop_diameter_input.text() == "9"
    assert window.prop_pitch_input.text() == "6"

    assert window.cell_count_input.text() == "4"
    assert window.capacity_input.text() == "3.0"
    assert window.c_rating_input.text() == "40"


def test_gui_clear_analysis_display(window):
    """Clearing analysis should reset displayed results."""

    window.aspect_ratio_value.setText("6.00")
    window.wing_loading_value.setText("5.00 kg/m²")
    window.analysis_status_value.setText("PASS")

    window._clear_analysis_display()

    assert window.aspect_ratio_value.text() == "-"
    assert window.wing_loading_value.text() == "-"
    assert window.analysis_status_value.text() == "-"



def test_gui_mass_dialog_edits_mass_and_location(qapp):
    """Viewer edit dialog should return edited engineering mass data."""

    from app.gui.main_window import MassItemEditDialog
    from app.models.mass_properties import MassItem

    dialog = MassItemEditDialog(
        MassItem(
            name="Payload",
            mass_kg=0.15,
            x_m=0.33,
            y_m=0.0,
            z_m=0.03,
        )
    )
    dialog.mass_input.setText("0.18")
    dialog.x_input.setText("0.41")
    dialog.y_input.setText("0.06")
    dialog.z_input.setText("0.04")
    dialog.source_input.setCurrentText("MEASURED")

    edited = dialog.mass_item()

    assert edited.mass_kg == 0.18
    assert edited.x_m == 0.41
    assert edited.y_m == 0.06
    assert edited.z_m == 0.04
    assert edited.source == "MEASURED"
    dialog.close()


def test_gui_live_mass_summary_updates_from_inventory(window):
    """Mass-table edits should feed the deterministic CG preview."""

    from app.models.design import DesignRequirements
    from app.models.mass_properties import MassItem, MassProperties

    aircraft = make_test_aircraft()
    aircraft.requirements = DesignRequirements(wing_le_x_m=0.30)
    aircraft.mass_properties = MassProperties(
        items=[
            MassItem("Motor", 0.20, 0.10, 0.00, 0.00, "MEASURED"),
            MassItem("Battery", 0.30, 0.40, 0.10, 0.00, "MEASURED"),
        ]
    )
    window.current_aircraft = aircraft
    window._populate_inputs(aircraft)

    assert window.inventory_mass_value.text() == "0.5000 kg"
    assert "0.2800 / 0.0600 / 0.0000 m" == window.cg_xyz_value.text()
    # Viewer shows the single resultant CG, not component markers.
    assert window.aircraft_view._cg_x_m == pytest.approx(0.02)
    assert window.aircraft_view._cg_y_m == pytest.approx(0.06)


def test_aircraft_view_converts_scene_to_datum_coordinates(qapp):
    """CAD cursor coordinates should use the engineering datum reference."""

    from PySide6.QtCore import QPointF

    from app.gui.aircraft_view import AircraftLayoutView
    from app.models.design import DesignRequirements

    aircraft = make_test_aircraft()
    aircraft.requirements = DesignRequirements(wing_le_x_m=0.30)

    view = AircraftLayoutView()
    view.set_aircraft(aircraft)

    x_m, y_m = view.scene_to_aircraft_coordinates(QPointF(0.0, 0.0))
    assert x_m == pytest.approx(0.30)
    assert y_m == pytest.approx(0.0)

    # 0.10 m aft of the LE is station X=0.40 m.
    x_m, y_m = view.scene_to_aircraft_coordinates(
        QPointF(-0.10 * view.SCALE, 0.05 * view.SCALE)
    )
    assert x_m == pytest.approx(0.40)
    assert y_m == pytest.approx(0.05)
    view.close()


def test_aircraft_view_cg_overlay_reports_full_aircraft_cg(qapp):
    """The clean CG overlay should report X/Y/Z and percent MAC."""

    from app.gui.aircraft_view import AircraftLayoutView
    from app.models.design import DesignRequirements

    aircraft = make_test_aircraft()
    aircraft.requirements = DesignRequirements(wing_le_x_m=0.30)

    view = AircraftLayoutView()
    view.set_aircraft(aircraft)
    view.set_cg(
        -0.05,
        0.02,
        measured=True,
        cg_z_m=0.04,
    )

    summary = view._cg_overlay.text()
    assert "FULL-AIRCRAFT CG" in summary
    assert "X 0.350 m" in summary
    assert "Y +0.020 m" in summary
    assert "Z +0.040 m" in summary
    assert "25.0% MAC" in summary
    assert "MASS INPUTS" in summary
    view.close()


def test_aircraft_view_without_mass_data_has_no_synthetic_cg(qapp):
    """The viewer should not invent a 25%-MAC CG when no mass data exists."""

    from app.gui.aircraft_view import AircraftLayoutView

    view = AircraftLayoutView()
    view.set_aircraft(make_test_aircraft())
    view.set_cg(None)

    assert view._cg_x_m is None
    assert "Enter mass/location data" in view._cg_overlay.text()
    view.close()


def test_gui_global_undo_redo_restores_parameter(window):
    """Ctrl-style global history should restore design parameter edits."""

    window._set_default_project()
    original = window.span_input.text()
    window.span_input.setText("1.600")
    window._commit_history("Edit wing span")

    assert window.undo_stack.canUndo()
    window.undo_stack.undo()
    assert window.span_input.text() == original

    assert window.undo_stack.canRedo()
    window.undo_stack.redo()
    assert window.span_input.text() == "1.600"


def test_aircraft_view_has_cad_axis_indicator(qapp):
    """Lower-left viewport should expose an engineering X/Y axis glyph."""

    from app.gui.aircraft_view import AircraftLayoutView

    view = AircraftLayoutView()
    assert view._axis_indicator.width() > 0
    assert view._axis_indicator.height() > 0
    assert "+X" in view._axis_indicator.toolTip()
    view.close()


def test_dimension_editor_reports_geometry_and_cg(qapp):
    """Dimension editor should translate geometry into CG/MAC details."""

    from app.gui.aircraft_view import DimensionEditorBar

    editor = DimensionEditorBar()
    editor.set_design_context(
        span_m=1.2,
        chord_m=0.2,
        wing_le_x_m=0.30,
        tail_arm_ratio=3.0,
        cg_x_m=0.35,
        cg_y_m=0.01,
        cg_z_m=0.02,
        cg_forward_mac_percent=20.0,
        cg_aft_mac_percent=30.0,
    )

    assert "Area 0.2400 m²" in editor.geometry_details.text()
    assert "AR 6.00" in editor.geometry_details.text()
    assert "Tail arm 0.600 m" in editor.geometry_details.text()
    assert "CG X 0.350 m" in editor.cg_details.text()
    assert "Arm 0.050 m" in editor.cg_details.text()
    assert "25.0% MAC" in editor.cg_details.text()
    assert "CG target X 0.340–0.360 m" in editor.cg_target_details.text()
    assert "IN TARGET" in editor.cg_target_details.text()
    editor.close()


def test_dimension_editor_updates_canonical_input_and_undo(window):
    """Viewer dimension edits should use canonical inputs and global history."""

    window._set_default_project()
    original = window.span_input.text()

    window.dimension_editor.dimensionEdited.emit("span", 1.55)

    assert float(window.span_input.text()) == pytest.approx(1.55)
    assert window.undo_stack.canUndo()

    window.undo_stack.undo()
    assert window.span_input.text() == original

    window.undo_stack.redo()
    assert float(window.span_input.text()) == pytest.approx(1.55)


def test_aircraft_view_draws_clean_engineering_dimensions(qapp):
    """Planform should expose span, MAC, LE station, CG arm, and CG target."""

    from PySide6.QtWidgets import QGraphicsSimpleTextItem

    from app.gui.aircraft_view import AircraftLayoutView
    from app.models.design import DesignRequirements

    aircraft = make_test_aircraft()
    aircraft.requirements = DesignRequirements(
        wing_le_x_m=0.30,
        cg_forward_mac_percent=20.0,
        cg_aft_mac_percent=30.0,
    )

    view = AircraftLayoutView()
    view.set_aircraft(aircraft)
    view.set_cg(-0.05, 0.0, measured=True, cg_z_m=0.02)

    labels = {
        item.text()
        for item in view.scene().items()
        if isinstance(item, QGraphicsSimpleTextItem)
    }

    assert "SPAN 1.200 m" in labels
    assert "MAC 0.200 m" in labels
    assert "LE X 0.300 m" in labels
    assert "CG TARGET" in labels
    assert "CG ARM 0.050 m / 25.0% MAC" in labels
    view.close()
