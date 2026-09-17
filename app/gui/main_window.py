"""Main GUI for MCore UAV Rapid Sizer v1.5."""

import sys
from pathlib import Path
from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.engineering.mass_properties import calculate_mass_properties
from app.gui.aircraft_view import AircraftLayoutView, DimensionEditorBar
from app.models.aircraft import (
    Aircraft,
    AircraftGeometry,
    AircraftMass,
    Battery,
    Propulsion,
)
from app.models.design import DesignRequirements
from app.models.mass_properties import MassItem, MassProperties
from app.services.application import update_project
from app.services.project_io import load_aircraft, save_aircraft
from app.services.rapid_design import (
    apply_recommended_wing,
    assess_rapid_design,
)
from app.services.reporting import save_markdown_report
from app.services.uav_analysis import analyze_aircraft


class EditorSnapshotCommand(QUndoCommand):
    """Undoable snapshot of the user-editable rapid-sizing workspace."""

    def __init__(
        self,
        window: "MainWindow",
        before: dict,
        after: dict,
        description: str,
    ) -> None:
        super().__init__(description)
        self._window = window
        self._before = deepcopy(before)
        self._after = deepcopy(after)

    def undo(self) -> None:
        self._window._restore_editor_state(self._before)

    def redo(self) -> None:
        self._window._restore_editor_state(self._after)


class MassItemEditDialog(QDialog):
    """Edit a mass item from the aircraft layout viewer."""

    def __init__(self, item: MassItem, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Edit Mass Item — {item.name}")

        layout = QFormLayout(self)
        self.name_input = QLineEdit(item.name)
        self.mass_input = QLineEdit(str(item.mass_kg))
        self.x_input = QLineEdit(str(item.x_m))
        self.y_input = QLineEdit(str(item.y_m))
        self.z_input = QLineEdit(str(item.z_m))
        self.source_input = QComboBox()
        self.source_input.addItems(["MEASURED", "ESTIMATED"])
        source = item.source.strip().upper()
        self.source_input.setCurrentText(
            source if source in {"MEASURED", "ESTIMATED"} else "ESTIMATED"
        )
        self.uncertainty_input = QLineEdit(str(item.uncertainty_kg))

        layout.addRow("Component:", self.name_input)
        layout.addRow("Mass (kg):", self.mass_input)
        layout.addRow("X from Datum (m):", self.x_input)
        layout.addRow("Y from Centerline (m):", self.y_input)
        layout.addRow("Z (m):", self.z_input)
        layout.addRow("Source:", self.source_input)
        layout.addRow("Uncertainty (kg):", self.uncertainty_input)

        note = QLabel(
            "Enter component location using the project datum. The aircraft viewer shows "
            "only the resultant full-aircraft CG calculated from all mass inputs."
        )
        note.setWordWrap(True)
        layout.addRow(note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def mass_item(self) -> MassItem:
        """Return the edited mass item."""

        name = self.name_input.text().strip() or "Component"
        mass_kg = float(self.mass_input.text())
        uncertainty_kg = float(self.uncertainty_input.text())
        if mass_kg < 0.0:
            raise ValueError("Mass cannot be negative.")
        if uncertainty_kg < 0.0:
            raise ValueError("Mass uncertainty cannot be negative.")
        return MassItem(
            name=name,
            mass_kg=mass_kg,
            x_m=float(self.x_input.text()),
            y_m=float(self.y_input.text()),
            z_m=float(self.z_input.text()),
            source=self.source_input.currentText(),
            uncertainty_kg=uncertainty_kg,
        )


class MainWindow(QMainWindow):
    """Requirements-driven rapid UAV sizing and mass-properties workspace."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MCore — UAV Rapid Sizer v1.5")
        self.resize(1450, 900)

        self.current_project: Path | None = None
        self.current_aircraft: Aircraft | None = None
        self.current_analysis = None
        self.current_rapid_assessment = None

        self._history_restoring = False
        self._history_snapshot: dict | None = None
        self.undo_stack = QUndoStack(self)
        self.undo_action = self.undo_stack.createUndoAction(self, "Undo")
        self.undo_action.setShortcuts([QKeySequence("Ctrl+Z")])
        self.undo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self.redo_action = self.undo_stack.createRedoAction(self, "Redo")
        self.redo_action.setShortcuts([QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")])
        self.redo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)

        self._build_ui()
        self._history_snapshot = self._capture_editor_state()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)

        title = QLabel("MCore — UAV Rapid Sizer v1.5")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; padding: 8px;"
        )
        subtitle = QLabel(
            "Requirements → sizing → mass/CG → power/energy → checks → report"
        )
        subtitle.setStyleSheet("padding-left: 8px; color: #aaaaaa;")
        root.addWidget(title)
        root.addWidget(subtitle)

        controls = QHBoxLayout()
        for text, slot in (
            ("New Project", self.new_project),
            ("Load Project", self.load_project),
            ("Save", self.save_project),
            ("Save As", self.save_project_as),
        ):
            button = QPushButton(text)
            button.clicked.connect(slot)
            controls.addWidget(button)

        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo_action.trigger)
        self.undo_button.setEnabled(False)
        controls.addWidget(self.undo_button)

        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.redo_action.trigger)
        self.redo_button.setEnabled(False)
        controls.addWidget(self.redo_button)

        self.undo_stack.canUndoChanged.connect(self.undo_button.setEnabled)
        self.undo_stack.canRedoChanged.connect(self.redo_button.setEnabled)

        for text, slot in (
            ("Apply Sized Wing", self.apply_sized_wing),
            ("Analyze", self.analyze_project),
            ("Export Report", self.export_report),
        ):
            button = QPushButton(text)
            button.clicked.connect(slot)
            controls.addWidget(button)
        controls.addStretch()
        root.addLayout(controls)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)

        workspace = QHBoxLayout()

        view_group = QGroupBox("Aircraft Layout — Full-Aircraft CG")
        view_layout = QVBoxLayout(view_group)
        self.aircraft_view = AircraftLayoutView()
        view_layout.addWidget(self.aircraft_view)

        self.dimension_editor = DimensionEditorBar()
        self.dimension_editor.dimensionEdited.connect(
            self._on_dimension_editor_changed
        )
        view_layout.addWidget(self.dimension_editor)
        workspace.addWidget(view_group, 3)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_current_design_tab(), "Current Design")
        self.tabs.addTab(self._build_requirements_tab(), "Requirements")
        self.tabs.addTab(self._build_mass_tab(), "Mass & CG")
        self.tabs.addTab(self._build_results_tab(), "Rapid Results")
        workspace.addWidget(self.tabs, 2)

        root.addLayout(workspace)
        self.setCentralWidget(central)

        for widget in (
            self.span_input,
            self.chord_input,
            self.prop_diameter_input,
            self.wing_le_x_input,
            self.cg_forward_input,
            self.cg_aft_input,
            self.ht_volume_input,
            self.tail_arm_ratio_input,
            self.ht_aspect_ratio_input,
        ):
            widget.textChanged.connect(self._update_live_view)

        for widget in self._history_line_edits():
            widget.editingFinished.connect(self._on_parameter_edit_finished)

        self.statusBar().showMessage("Ready")

    def _build_current_design_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        geometry_group = QGroupBox("Geometry / Design Mass")
        geometry_layout = QFormLayout(geometry_group)
        self.span_input = QLineEdit()
        self.chord_input = QLineEdit()
        self.mass_input = QLineEdit()
        geometry_layout.addRow("Wing Span (m):", self.span_input)
        geometry_layout.addRow("Mean Chord (m):", self.chord_input)
        geometry_layout.addRow("Design Mass / MTOM (kg):", self.mass_input)
        layout.addWidget(geometry_group)

        propulsion_group = QGroupBox("Propulsion Reference")
        propulsion_layout = QFormLayout(propulsion_group)
        self.kv_input = QLineEdit()
        self.prop_diameter_input = QLineEdit()
        self.prop_pitch_input = QLineEdit()
        propulsion_layout.addRow("Motor KV:", self.kv_input)
        propulsion_layout.addRow("Propeller Diameter (in):", self.prop_diameter_input)
        propulsion_layout.addRow("Propeller Pitch (in):", self.prop_pitch_input)
        layout.addWidget(propulsion_group)

        battery_group = QGroupBox("Battery")
        battery_layout = QFormLayout(battery_group)
        self.cell_count_input = QLineEdit()
        self.capacity_input = QLineEdit()
        self.c_rating_input = QLineEdit()
        battery_layout.addRow("Cell Count (S):", self.cell_count_input)
        battery_layout.addRow("Capacity (Ah):", self.capacity_input)
        battery_layout.addRow("Discharge Rating (C):", self.c_rating_input)
        layout.addWidget(battery_group)

        analysis_group = QGroupBox("Legacy Deterministic Analysis")
        analysis_layout = QFormLayout(analysis_group)
        self.aspect_ratio_value = QLabel("-")
        self.wing_loading_value = QLabel("-")
        self.analysis_status_value = QLabel("-")
        analysis_layout.addRow("Aspect Ratio:", self.aspect_ratio_value)
        analysis_layout.addRow("Wing Loading:", self.wing_loading_value)
        analysis_layout.addRow("Verification:", self.analysis_status_value)
        layout.addWidget(analysis_group)
        layout.addStretch()
        return tab

    def _build_requirements_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        mission = QGroupBox("Mission Requirements")
        form = QFormLayout(mission)
        self.stall_speed_input = QLineEdit()
        self.cruise_speed_input = QLineEdit()
        self.endurance_input = QLineEdit()
        self.climb_rate_input = QLineEdit()
        self.aspect_ratio_target_input = QLineEdit()
        self.thrust_to_weight_input = QLineEdit()
        self.ht_volume_input = QLineEdit()
        self.vt_volume_input = QLineEdit()
        self.tail_arm_ratio_input = QLineEdit()
        self.ht_aspect_ratio_input = QLineEdit()
        self.vt_aspect_ratio_input = QLineEdit()
        form.addRow("Target Stall Speed (m/s):", self.stall_speed_input)
        form.addRow("Cruise Speed (m/s):", self.cruise_speed_input)
        form.addRow("Endurance (min):", self.endurance_input)
        form.addRow("Climb Rate (m/s):", self.climb_rate_input)
        form.addRow("Aspect Ratio Target:", self.aspect_ratio_target_input)
        form.addRow("Thrust / Weight Target:", self.thrust_to_weight_input)
        form.addRow("Horizontal Tail Volume Coeff.:", self.ht_volume_input)
        form.addRow("Vertical Tail Volume Coeff.:", self.vt_volume_input)
        form.addRow("Tail Arm / Wing Chord:", self.tail_arm_ratio_input)
        form.addRow("Horizontal Tail Aspect Ratio:", self.ht_aspect_ratio_input)
        form.addRow("Vertical Tail Aspect Ratio:", self.vt_aspect_ratio_input)
        layout.addWidget(mission)

        assumptions = QGroupBox("Aerodynamic / Energy Assumptions")
        aform = QFormLayout(assumptions)
        self.clmax_input = QLineEdit()
        self.cd0_input = QLineEdit()
        self.oswald_input = QLineEdit()
        self.prop_eff_input = QLineEdit()
        self.reserve_input = QLineEdit()
        self.air_density_input = QLineEdit()
        aform.addRow("CLmax:", self.clmax_input)
        aform.addRow("CD0:", self.cd0_input)
        aform.addRow("Oswald Efficiency:", self.oswald_input)
        aform.addRow("Propulsive Efficiency:", self.prop_eff_input)
        aform.addRow("Battery Reserve Fraction:", self.reserve_input)
        aform.addRow("Air Density (kg/m³):", self.air_density_input)
        layout.addWidget(assumptions)

        cg = QGroupBox("CG Reference / Design Target")
        cform = QFormLayout(cg)
        self.wing_le_x_input = QLineEdit()
        self.cg_forward_input = QLineEdit()
        self.cg_aft_input = QLineEdit()
        cform.addRow("Wing LE X from Datum (m):", self.wing_le_x_input)
        cform.addRow("Forward CG Target (% MAC):", self.cg_forward_input)
        cform.addRow("Aft CG Target (% MAC):", self.cg_aft_input)
        layout.addWidget(cg)

        note = QLabel(
            "Defaults are preliminary assumptions, not universal limits. "
            "Replace them with project-specific aerodynamic/test data as it becomes available."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(note)
        layout.addStretch()
        return tab

    def _build_mass_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.mass_table = QTableWidget(0, 7)
        self.mass_table.setHorizontalHeaderLabels(
            ["Component", "Mass kg", "X m", "Y m", "Z m", "Source", "Unc. kg"]
        )
        header = self.mass_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mass_table.itemChanged.connect(self._on_mass_table_changed)
        layout.addWidget(self.mass_table)

        buttons = QHBoxLayout()
        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_mass_item)
        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_selected_mass_item)
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_mass_item)
        use_mass_button = QPushButton("Use Inventory Mass")
        use_mass_button.clicked.connect(self.use_inventory_mass)
        buttons.addWidget(add_button)
        buttons.addWidget(edit_button)
        buttons.addWidget(delete_button)
        buttons.addWidget(use_mass_button)
        layout.addLayout(buttons)

        summary = QGroupBox("Mass Properties")
        form = QFormLayout(summary)
        self.inventory_mass_value = QLabel("-")
        self.cg_xyz_value = QLabel("-")
        self.cg_mac_value = QLabel("-")
        self.measured_fraction_value = QLabel("-")
        form.addRow("Inventory Mass:", self.inventory_mass_value)
        form.addRow("CG X / Y / Z:", self.cg_xyz_value)
        form.addRow("CG (% MAC):", self.cg_mac_value)
        form.addRow("Measured Mass Fraction:", self.measured_fraction_value)
        layout.addWidget(summary)

        note = QLabel(
            "Enter component mass and X/Y/Z location here. MCore calculates the resultant "
            "full-aircraft CG and shows only that CG in the aircraft viewer. Replace "
            "ESTIMATED mass values with measured values as the prototype matures."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(note)
        return tab

    def _build_results_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.rapid_status_value = QLabel("Not analyzed")
        self.rapid_status_value.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.rapid_status_value)
        layout.addWidget(self.results_text)
        return tab

    # ------------------------------------------------------------------
    # Project state
    # ------------------------------------------------------------------

    def _default_aircraft(self) -> Aircraft:
        return Aircraft(
            name="New MCore UAV",
            geometry=AircraftGeometry(1.2, 0.2),
            mass=AircraftMass(1.2),
            propulsion=Propulsion(1500, 8.0, 6.0),
            battery=Battery(3, 2.2, 30.0),
        )

    def _set_default_project(self) -> None:
        self.current_project = None
        self.current_aircraft = self._default_aircraft()
        self.current_analysis = None
        self.current_rapid_assessment = None
        self._populate_inputs(self.current_aircraft)
        self._clear_analysis_display()
        self._reset_history()

    def new_project(self) -> None:
        self._set_default_project()
        self.statusBar().showMessage("New unsaved project")

    def load_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open MCore UAV Project",
            str(Path("data/projects")),
            "MCore Project (*.json)",
        )
        if not path:
            return
        try:
            aircraft = load_aircraft(path)
        except (OSError, ValueError, KeyError, TypeError) as error:
            QMessageBox.critical(self, "Project Load Error", str(error))
            return

        self.current_project = Path(path)
        self.current_aircraft = aircraft
        self.current_analysis = None
        self.current_rapid_assessment = None
        self._populate_inputs(aircraft)
        self._clear_analysis_display()
        self._reset_history()
        self.statusBar().showMessage(f"Loaded: {aircraft.name}")

    def _populate_inputs(self, aircraft: Aircraft) -> None:
        self.span_input.setText(str(aircraft.geometry.wing_span_m))
        self.chord_input.setText(str(aircraft.geometry.mean_chord_m))
        self.mass_input.setText(str(aircraft.mass.aircraft_mass_kg))
        self.kv_input.setText(str(aircraft.propulsion.motor_kv))
        self.prop_diameter_input.setText(str(aircraft.propulsion.propeller_diameter_in))
        self.prop_pitch_input.setText(str(aircraft.propulsion.propeller_pitch_in))
        self.cell_count_input.setText(str(aircraft.battery.cell_count))
        self.capacity_input.setText(str(aircraft.battery.capacity_ah))
        self.c_rating_input.setText(str(aircraft.battery.discharge_c))

        r = aircraft.requirements
        self.stall_speed_input.setText(str(r.stall_speed_m_s))
        self.cruise_speed_input.setText(str(r.cruise_speed_m_s))
        self.endurance_input.setText(str(r.endurance_min))
        self.climb_rate_input.setText(str(r.climb_rate_m_s))
        self.aspect_ratio_target_input.setText(str(r.aspect_ratio_target))
        self.thrust_to_weight_input.setText(str(r.thrust_to_weight_target))
        self.ht_volume_input.setText(str(r.horizontal_tail_volume_coefficient))
        self.vt_volume_input.setText(str(r.vertical_tail_volume_coefficient))
        self.tail_arm_ratio_input.setText(str(r.tail_arm_chord_ratio))
        self.ht_aspect_ratio_input.setText(str(r.horizontal_tail_aspect_ratio))
        self.vt_aspect_ratio_input.setText(str(r.vertical_tail_aspect_ratio))
        self.clmax_input.setText(str(r.cl_max))
        self.cd0_input.setText(str(r.cd0))
        self.oswald_input.setText(str(r.oswald_efficiency))
        self.prop_eff_input.setText(str(r.propulsive_efficiency))
        self.reserve_input.setText(str(r.battery_reserve_fraction))
        self.air_density_input.setText(str(r.air_density_kg_m3))
        self.wing_le_x_input.setText(str(r.wing_le_x_m))
        self.cg_forward_input.setText(str(r.cg_forward_mac_percent))
        self.cg_aft_input.setText(str(r.cg_aft_mac_percent))

        self._populate_mass_table(aircraft.mass_properties.items)
        self._update_live_view()

    def _populate_mass_table(self, items: list[MassItem]) -> None:
        self.mass_table.blockSignals(True)
        try:
            self.mass_table.setRowCount(0)
            for item in items:
                row = self.mass_table.rowCount()
                self.mass_table.insertRow(row)
                values = (
                    item.name,
                    item.mass_kg,
                    item.x_m,
                    item.y_m,
                    item.z_m,
                    item.source,
                    item.uncertainty_kg,
                )
                for column, value in enumerate(values):
                    self.mass_table.setItem(
                        row, column, QTableWidgetItem(str(value))
                    )
        finally:
            self.mass_table.blockSignals(False)

    def _mass_items_from_table(self) -> list[MassItem]:
        items: list[MassItem] = []
        for row in range(self.mass_table.rowCount()):
            def cell(column: int, default: str = "") -> str:
                item = self.mass_table.item(row, column)
                return item.text().strip() if item else default

            name = cell(0, f"Item {row + 1}") or f"Item {row + 1}"
            items.append(
                MassItem(
                    name=name,
                    mass_kg=float(cell(1, "0")),
                    x_m=float(cell(2, "0")),
                    y_m=float(cell(3, "0")),
                    z_m=float(cell(4, "0")),
                    source=cell(5, "ESTIMATED") or "ESTIMATED",
                    uncertainty_kg=float(cell(6, "0")),
                )
            )
        return items

    def _build_aircraft_from_inputs(self) -> Aircraft:
        if self.current_aircraft is None:
            raise ValueError("No project is currently loaded.")

        current_req = self.current_aircraft.requirements

        def req_float(widget: QLineEdit, fallback: float) -> float:
            text = widget.text().strip()
            return float(text) if text else fallback

        requirements = DesignRequirements(
            stall_speed_m_s=req_float(self.stall_speed_input, current_req.stall_speed_m_s),
            cruise_speed_m_s=req_float(self.cruise_speed_input, current_req.cruise_speed_m_s),
            endurance_min=req_float(self.endurance_input, current_req.endurance_min),
            climb_rate_m_s=req_float(self.climb_rate_input, current_req.climb_rate_m_s),
            aspect_ratio_target=req_float(self.aspect_ratio_target_input, current_req.aspect_ratio_target),
            cl_max=req_float(self.clmax_input, current_req.cl_max),
            cd0=req_float(self.cd0_input, current_req.cd0),
            oswald_efficiency=req_float(self.oswald_input, current_req.oswald_efficiency),
            propulsive_efficiency=req_float(self.prop_eff_input, current_req.propulsive_efficiency),
            battery_reserve_fraction=req_float(self.reserve_input, current_req.battery_reserve_fraction),
            air_density_kg_m3=req_float(self.air_density_input, current_req.air_density_kg_m3),
            thrust_to_weight_target=req_float(self.thrust_to_weight_input, current_req.thrust_to_weight_target),
            horizontal_tail_volume_coefficient=req_float(self.ht_volume_input, current_req.horizontal_tail_volume_coefficient),
            vertical_tail_volume_coefficient=req_float(self.vt_volume_input, current_req.vertical_tail_volume_coefficient),
            tail_arm_chord_ratio=req_float(self.tail_arm_ratio_input, current_req.tail_arm_chord_ratio),
            horizontal_tail_aspect_ratio=req_float(self.ht_aspect_ratio_input, current_req.horizontal_tail_aspect_ratio),
            vertical_tail_aspect_ratio=req_float(self.vt_aspect_ratio_input, current_req.vertical_tail_aspect_ratio),
            wing_le_x_m=req_float(self.wing_le_x_input, current_req.wing_le_x_m),
            cg_forward_mac_percent=req_float(self.cg_forward_input, current_req.cg_forward_mac_percent),
            cg_aft_mac_percent=req_float(self.cg_aft_input, current_req.cg_aft_mac_percent),
        )

        return Aircraft(
            name=self.current_aircraft.name,
            geometry=AircraftGeometry(
                wing_span_m=float(self.span_input.text()),
                mean_chord_m=float(self.chord_input.text()),
            ),
            mass=AircraftMass(aircraft_mass_kg=float(self.mass_input.text())),
            propulsion=Propulsion(
                motor_kv=float(self.kv_input.text()),
                propeller_diameter_in=float(self.prop_diameter_input.text()),
                propeller_pitch_in=float(self.prop_pitch_input.text()),
            ),
            battery=Battery(
                cell_count=int(self.cell_count_input.text()),
                capacity_ah=float(self.capacity_input.text()),
                discharge_c=float(self.c_rating_input.text()),
            ),
            requirements=requirements,
            mass_properties=MassProperties(items=self._mass_items_from_table()),
        )

    # ------------------------------------------------------------------
    # Undo / redo history
    # ------------------------------------------------------------------

    def _history_line_edits(self) -> tuple[QLineEdit, ...]:
        """Return every scalar design input covered by global undo/redo."""

        return (
            self.span_input, self.chord_input, self.mass_input,
            self.kv_input, self.prop_diameter_input, self.prop_pitch_input,
            self.cell_count_input, self.capacity_input, self.c_rating_input,
            self.stall_speed_input, self.cruise_speed_input,
            self.endurance_input, self.climb_rate_input,
            self.aspect_ratio_target_input, self.thrust_to_weight_input,
            self.ht_volume_input, self.vt_volume_input, self.tail_arm_ratio_input,
            self.ht_aspect_ratio_input, self.vt_aspect_ratio_input,
            self.clmax_input, self.cd0_input, self.oswald_input,
            self.prop_eff_input, self.reserve_input, self.air_density_input,
            self.wing_le_x_input, self.cg_forward_input, self.cg_aft_input,
        )

    def _history_field_names(self) -> tuple[str, ...]:
        """Attribute names corresponding to the undoable scalar inputs."""

        return (
            "span_input", "chord_input", "mass_input",
            "kv_input", "prop_diameter_input", "prop_pitch_input",
            "cell_count_input", "capacity_input", "c_rating_input",
            "stall_speed_input", "cruise_speed_input",
            "endurance_input", "climb_rate_input",
            "aspect_ratio_target_input", "thrust_to_weight_input",
            "ht_volume_input", "vt_volume_input", "tail_arm_ratio_input",
            "ht_aspect_ratio_input", "vt_aspect_ratio_input",
            "clmax_input", "cd0_input", "oswald_input",
            "prop_eff_input", "reserve_input", "air_density_input",
            "wing_le_x_input", "cg_forward_input", "cg_aft_input",
        )

    def _capture_editor_state(self) -> dict:
        """Capture an immutable-style snapshot of inputs and mass inventory."""

        fields = {
            name: getattr(self, name).text()
            for name in self._history_field_names()
        }
        mass_rows: list[list[str]] = []
        for row in range(self.mass_table.rowCount()):
            mass_rows.append([
                self.mass_table.item(row, column).text()
                if self.mass_table.item(row, column) is not None
                else ""
                for column in range(self.mass_table.columnCount())
            ])
        return {"fields": fields, "mass_rows": mass_rows}

    def _restore_editor_state(self, state: dict) -> None:
        """Restore a snapshot without creating another undo command."""

        self._history_restoring = True
        try:
            for name, value in state["fields"].items():
                widget = getattr(self, name)
                widget.blockSignals(True)
                try:
                    widget.setText(value)
                finally:
                    widget.blockSignals(False)

            self.mass_table.blockSignals(True)
            try:
                self.mass_table.setRowCount(0)
                for values in state["mass_rows"]:
                    row = self.mass_table.rowCount()
                    self.mass_table.insertRow(row)
                    for column, value in enumerate(values):
                        self.mass_table.setItem(row, column, QTableWidgetItem(value))
            finally:
                self.mass_table.blockSignals(False)

            self._history_snapshot = deepcopy(state)
            self._update_live_view()
        finally:
            self._history_restoring = False

    def _commit_history(self, description: str) -> None:
        """Commit the current workspace state to the global undo stack."""

        if self._history_restoring:
            return
        current = self._capture_editor_state()
        if self._history_snapshot is None:
            self._history_snapshot = deepcopy(current)
            return
        if current == self._history_snapshot:
            return
        command = EditorSnapshotCommand(
            self, self._history_snapshot, current, description
        )
        self.undo_stack.push(command)
        self._history_snapshot = deepcopy(current)

    def _reset_history(self) -> None:
        """Start a fresh undo history at the current project state."""

        self.undo_stack.clear()
        self._history_snapshot = self._capture_editor_state()

    def _on_parameter_edit_finished(self) -> None:
        self._update_live_view()
        self._commit_history("Edit design parameter")

    def _on_dimension_editor_changed(
        self,
        field: str,
        value: float,
    ) -> None:
        """Apply a CAD dimension-bar edit to the canonical project inputs."""

        mapping = {
            "span": (self.span_input, "Edit wing span dimension"),
            "chord": (self.chord_input, "Edit wing MAC dimension"),
            "wing_le_x": (self.wing_le_x_input, "Edit wing LE station"),
        }
        if field not in mapping:
            return

        widget, description = mapping[field]
        widget.blockSignals(True)
        try:
            widget.setText(f"{value:.6f}")
        finally:
            widget.blockSignals(False)

        self._update_live_view()
        self._commit_history(description)
        self.statusBar().showMessage(
            f"Dimension updated: {field} = {value:.4f} m"
        )

    # ------------------------------------------------------------------
    # Editing helpers
    # ------------------------------------------------------------------

    def add_mass_item(self) -> None:
        row = self.mass_table.rowCount()
        self.mass_table.blockSignals(True)
        try:
            self.mass_table.insertRow(row)
            defaults = (
                f"Component {row + 1}",
                "0.0",
                "0.0",
                "0.0",
                "0.0",
                "ESTIMATED",
                "0.0",
            )
            for column, value in enumerate(defaults):
                self.mass_table.setItem(row, column, QTableWidgetItem(value))
        finally:
            self.mass_table.blockSignals(False)
        self.mass_table.selectRow(row)
        self._update_live_view()
        self._commit_history("Add mass item")

    def edit_selected_mass_item(self) -> None:
        """Edit the first selected mass-table row."""

        rows = sorted({index.row() for index in self.mass_table.selectedIndexes()})
        if not rows:
            QMessageBox.information(
                self,
                "Mass Item",
                "Select a mass item in the table.",
            )
            return
        self._on_mass_marker_edit_requested(rows[0])

    def _on_mass_marker_edit_requested(self, row: int) -> None:
        """Open the mass/location editor for the selected table row."""

        try:
            items = self._mass_items_from_table()
        except ValueError as error:
            QMessageBox.warning(self, "Mass Table Error", str(error))
            return
        if row < 0 or row >= len(items):
            return

        dialog = MassItemEditDialog(items[row], self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            edited = dialog.mass_item()
        except ValueError as error:
            QMessageBox.warning(self, "Mass Item Error", str(error))
            return

        values = (
            edited.name,
            edited.mass_kg,
            edited.x_m,
            edited.y_m,
            edited.z_m,
            edited.source,
            edited.uncertainty_kg,
        )
        self.mass_table.blockSignals(True)
        try:
            for column, value in enumerate(values):
                table_item = self.mass_table.item(row, column)
                if table_item is None:
                    table_item = QTableWidgetItem()
                    self.mass_table.setItem(row, column, table_item)
                table_item.setText(str(value))
        finally:
            self.mass_table.blockSignals(False)
        self.mass_table.selectRow(row)
        self._update_live_view()
        self._commit_history("Edit mass item")
        self.statusBar().showMessage(f"Updated mass item: {edited.name}")

    def _on_mass_marker_moved(
        self,
        row: int,
        x_m: float,
        y_m: float,
    ) -> None:
        """Commit a dragged marker position to the mass table."""

        if row < 0 or row >= self.mass_table.rowCount():
            return
        self.mass_table.blockSignals(True)
        try:
            for column, value in ((2, x_m), (3, y_m)):
                table_item = self.mass_table.item(row, column)
                if table_item is None:
                    table_item = QTableWidgetItem()
                    self.mass_table.setItem(row, column, table_item)
                table_item.setText(f"{value:.4f}")
        finally:
            self.mass_table.blockSignals(False)
        self.mass_table.selectRow(row)
        self._update_live_view()
        self.statusBar().showMessage(
            f"Mass item moved: X={x_m:.4f} m, Y={y_m:.4f} m"
        )

    def _on_mass_table_changed(self, _item: QTableWidgetItem) -> None:
        """Recalculate CG and record direct mass-table edits."""

        self._update_live_view()
        self._commit_history("Edit mass inventory")

    def delete_mass_item(self) -> None:
        rows = sorted(
            {index.row() for index in self.mass_table.selectedIndexes()},
            reverse=True,
        )
        self.mass_table.blockSignals(True)
        try:
            for row in rows:
                self.mass_table.removeRow(row)
        finally:
            self.mass_table.blockSignals(False)
        self._update_live_view()
        self._commit_history("Delete mass item")

    def use_inventory_mass(self) -> None:
        try:
            total = sum(item.mass_kg for item in self._mass_items_from_table())
        except ValueError as error:
            QMessageBox.warning(self, "Mass Table Error", str(error))
            return
        if total <= 0:
            QMessageBox.information(self, "Mass Inventory", "Inventory mass must be greater than zero.")
            return
        self.mass_input.setText(f"{total:.4f}")
        self._update_live_view()
        self._commit_history("Use inventory mass")
        self.statusBar().showMessage("Design mass updated from mass inventory")

    def apply_sized_wing(self) -> None:
        try:
            aircraft = self._build_aircraft_from_inputs()
            sized = apply_recommended_wing(aircraft)
        except (ValueError, TypeError, ArithmeticError) as error:
            QMessageBox.warning(self, "Sizing Error", str(error))
            return
        self.current_aircraft = sized
        self.span_input.setText(f"{sized.geometry.wing_span_m:.6f}")
        self.chord_input.setText(f"{sized.geometry.mean_chord_m:.6f}")
        self._update_live_view()
        self._commit_history("Apply sized wing")
        self.statusBar().showMessage("Requirements-driven wing geometry applied")

    def _update_live_view(self) -> None:
        if self.current_aircraft is None:
            return
        try:
            aircraft = self._build_aircraft_from_inputs()
            mass = calculate_mass_properties(aircraft.mass_properties.items)
        except (ValueError, TypeError):
            return

        self.aircraft_view.set_aircraft(aircraft)

        cg_abs_x = mass.cg_x_m if mass.total_mass_kg > 0.0 else None
        self.dimension_editor.set_design_context(
            span_m=aircraft.geometry.wing_span_m,
            chord_m=aircraft.geometry.mean_chord_m,
            wing_le_x_m=aircraft.requirements.wing_le_x_m,
            tail_arm_ratio=aircraft.requirements.tail_arm_chord_ratio,
            cg_x_m=cg_abs_x,
            cg_y_m=mass.cg_y_m if mass.total_mass_kg > 0.0 else 0.0,
            cg_z_m=mass.cg_z_m if mass.total_mass_kg > 0.0 else 0.0,
            cg_forward_mac_percent=(
                aircraft.requirements.cg_forward_mac_percent
            ),
            cg_aft_mac_percent=aircraft.requirements.cg_aft_mac_percent,
        )

        if mass.total_mass_kg > 0.0:
            cg_relative_x = mass.cg_x_m - aircraft.requirements.wing_le_x_m
            cg_view_x = -cg_relative_x
            self.aircraft_view.set_cg(
                cg_view_x,
                mass.cg_y_m,
                measured=True,
                cg_z_m=mass.cg_z_m,
            )
            self.inventory_mass_value.setText(f"{mass.total_mass_kg:.4f} kg")
            self.cg_xyz_value.setText(
                f"{mass.cg_x_m:.4f} / {mass.cg_y_m:.4f} / {mass.cg_z_m:.4f} m"
            )
            chord = aircraft.geometry.mean_chord_m
            cg_percent = (cg_relative_x / chord * 100.0) if chord > 0.0 else 0.0
            self.cg_mac_value.setText(f"{cg_percent:.1f}%")
            self.measured_fraction_value.setText(
                f"{mass.measured_mass_fraction * 100.0:.1f}%"
            )
        else:
            self.aircraft_view.set_cg(None, 0.0, measured=False)
            self.inventory_mass_value.setText("0.0000 kg")
            self.cg_xyz_value.setText("-")
            self.cg_mac_value.setText("-")
            self.measured_fraction_value.setText("-")

    # ------------------------------------------------------------------
    # Persistence/reporting
    # ------------------------------------------------------------------

    def save_project(self) -> None:
        if self.current_project is None:
            self.save_project_as()
            return
        try:
            aircraft = self._build_aircraft_from_inputs()
        except (ValueError, TypeError) as error:
            QMessageBox.warning(self, "Input Error", str(error))
            return

        result = update_project(aircraft=aircraft, path=self.current_project)
        if not result.updated:
            QMessageBox.warning(
                self,
                "Validation Failed",
                result.validation.summary + "\n\n" + "\n".join(result.validation.errors),
            )
            return

        self.current_aircraft = aircraft
        self.statusBar().showMessage(f"Saved: {result.path}")

    def save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save MCore UAV Project",
            str(Path("data/projects/new_uav.json")),
            "MCore Project (*.json)",
        )
        if not path:
            return
        try:
            aircraft = self._build_aircraft_from_inputs()
            save_aircraft(aircraft, path)
        except (OSError, ValueError, TypeError) as error:
            QMessageBox.warning(self, "Save Error", str(error))
            return
        self.current_project = Path(path)
        self.current_aircraft = aircraft
        self.statusBar().showMessage(f"Saved: {path}")

    def export_report(self) -> None:
        try:
            aircraft = self._build_aircraft_from_inputs()
            assessment = assess_rapid_design(aircraft)
        except (ValueError, TypeError, ArithmeticError) as error:
            QMessageBox.warning(self, "Report Error", str(error))
            return

        suggested = (
            self.current_project.with_suffix(".report.md")
            if self.current_project
            else Path("data/projects/mcore_uav_report.md")
        )
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Preliminary Design Report",
            str(suggested),
            "Markdown (*.md)",
        )
        if not path:
            return
        save_markdown_report(aircraft, path, assessment)
        self.statusBar().showMessage(f"Report exported: {path}")

    # ------------------------------------------------------------------
    # Analysis/results
    # ------------------------------------------------------------------

    def analyze_project(self) -> None:
        try:
            aircraft = self._build_aircraft_from_inputs()
            analysis = analyze_aircraft(aircraft)
            rapid = assess_rapid_design(aircraft)
        except (ValueError, TypeError, ArithmeticError) as error:
            QMessageBox.warning(self, "Input or Analysis Error", str(error))
            return

        self.current_aircraft = aircraft
        self.current_analysis = analysis
        self.current_rapid_assessment = rapid

        self.aspect_ratio_value.setText(f"{analysis.wing.aspect_ratio:.2f}")
        self.wing_loading_value.setText(
            f"{analysis.wing.wing_loading_kg_m2:.2f} kg/m²"
        )
        self.analysis_status_value.setText(analysis.overall_verification_status)

        mass = rapid.mass_properties
        self.inventory_mass_value.setText(f"{mass.total_mass_kg:.4f} kg")
        self.cg_xyz_value.setText(
            f"{mass.cg_x_m:.4f} / {mass.cg_y_m:.4f} / {mass.cg_z_m:.4f} m"
        )
        self.cg_mac_value.setText(
            "-" if rapid.cg_percent_mac is None else f"{rapid.cg_percent_mac:.1f}%"
        )
        self.measured_fraction_value.setText(
            f"{mass.measured_mass_fraction * 100:.1f}%"
        )

        if mass.total_mass_kg > 0:
            cg_relative = mass.cg_x_m - aircraft.requirements.wing_le_x_m
            self.aircraft_view.set_cg(
                -cg_relative,
                mass.cg_y_m,
                measured=True,
                cg_z_m=mass.cg_z_m,
            )
        else:
            self.aircraft_view.set_cg(None, 0.0, measured=False)

        s = rapid.sizing
        lines = [
            f"PRELIMINARY STATUS: {rapid.overall_status}",
            "",
            "REQUIREMENTS-DRIVEN WING",
            f"Required area: {s.required_wing_area_m2:.4f} m²",
            f"Recommended span: {s.recommended_span_m:.3f} m",
            f"Recommended mean chord: {s.recommended_mean_chord_m:.3f} m",
            f"Current-geometry stall speed: {rapid.actual_stall_speed_m_s:.2f} m/s",
            "",
            "TAIL-VOLUME REFERENCE",
            f"Tail arm: {s.tail_arm_m:.3f} m",
            f"Horizontal tail: {s.horizontal_tail_span_m:.3f} m span x {s.horizontal_tail_mean_chord_m:.3f} m chord",
            f"Vertical tail: {s.vertical_tail_height_m:.3f} m height x {s.vertical_tail_mean_chord_m:.3f} m chord",
            "",
            "POWER / ENERGY",
            f"Cruise electrical power: {s.electrical_cruise_power_w:.1f} W",
            f"Climb electrical power: {s.electrical_climb_power_w:.1f} W",
            f"Required battery energy: {s.required_nominal_energy_wh:.1f} Wh",
            f"Required capacity: {s.required_capacity_ah:.2f} Ah",
            f"Predicted endurance: {s.predicted_endurance_min:.1f} min",
            f"Required static thrust target: {s.required_static_thrust_n:.1f} N",
            "",
            "CHECKS",
        ]
        lines.extend(
            f"[{check.status}] {check.name}: {check.message}"
            for check in rapid.checks
        )
        self.results_text.setPlainText("\n".join(lines))
        self.rapid_status_value.setText(
            f"Preliminary requirement status: {rapid.overall_status}"
        )
        self.tabs.setCurrentWidget(self.results_text.parentWidget())
        self.statusBar().showMessage("Rapid design analysis complete")

    def _clear_analysis_display(self) -> None:
        self.aspect_ratio_value.setText("-")
        self.wing_loading_value.setText("-")
        self.analysis_status_value.setText("-")
        self.inventory_mass_value.setText("-")
        self.cg_xyz_value.setText("-")
        self.cg_mac_value.setText("-")
        self.measured_fraction_value.setText("-")
        self.rapid_status_value.setText("Not analyzed")
        self.results_text.clear()
        self._update_live_view()

    def closeEvent(self, event) -> None:
        event.accept()


def run() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
