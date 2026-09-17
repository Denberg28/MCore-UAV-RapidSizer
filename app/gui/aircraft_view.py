"""Clean CAD-style aircraft planform, dimensions, and full-aircraft CG view."""

from __future__ import annotations

from math import sqrt

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QWidget,
)

from app.models.aircraft import Aircraft


class AxisIndicator(QWidget):
    """Compact CAD-style aircraft X/Y axis glyph for the viewport."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(76, 70)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setToolTip(
            "Aircraft axes: +X station is aft; +Y follows the planform lateral axis."
        )

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt API name
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(Qt.GlobalColor.lightGray, 2)
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.GlobalColor.lightGray))

        # Nose is to the right. Weight-and-balance X stations increase aft,
        # therefore +X is visually left. Scene +Y is visually downward.
        origin = QPointF(52.0, 16.0)
        x_tip = QPointF(12.0, 16.0)
        y_tip = QPointF(52.0, 56.0)

        painter.drawLine(origin, x_tip)
        painter.drawLine(origin, y_tip)

        painter.drawPolygon(
            QPolygonF(
                [
                    x_tip,
                    QPointF(20.0, 11.0),
                    QPointF(20.0, 21.0),
                ]
            )
        )
        painter.drawPolygon(
            QPolygonF(
                [
                    y_tip,
                    QPointF(47.0, 48.0),
                    QPointF(57.0, 48.0),
                ]
            )
        )

        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(2, 12, "+X")
        painter.drawText(57, 66, "+Y")
        painter.drawEllipse(origin, 2.5, 2.5)


class DimensionEditorBar(QWidget):
    """Compact CAD-style dimension editor with derived CG interpretation."""

    dimensionEdited = Signal(str, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dimensionEditorBar")
        self.setStyleSheet(
            "QWidget#dimensionEditorBar {"
            " background-color: rgba(28, 28, 28, 230);"
            " border: 1px solid rgba(150, 150, 150, 100);"
            " border-radius: 5px;"
            "}"
            "QLabel { color: #dddddd; }"
            "QDoubleSpinBox { min-width: 105px; padding: 3px; }"
        )

        layout = QGridLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(4)

        title = QLabel("DIMENSION EDITOR")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title, 0, 0)

        self.span_input = self._make_spinbox(0.05, 20.0)
        self.chord_input = self._make_spinbox(0.01, 5.0)
        self.wing_le_x_input = self._make_spinbox(-10.0, 20.0)

        layout.addWidget(QLabel("Span"), 0, 1)
        layout.addWidget(self.span_input, 0, 2)
        layout.addWidget(QLabel("MAC"), 0, 3)
        layout.addWidget(self.chord_input, 0, 4)
        layout.addWidget(QLabel("Wing LE X"), 0, 5)
        layout.addWidget(self.wing_le_x_input, 0, 6)

        self.geometry_details = QLabel("Area --   AR --   Tail arm --")
        self.geometry_details.setStyleSheet(
            "font-family: Consolas, 'Courier New', monospace; color: #cfcfcf;"
        )
        layout.addWidget(self.geometry_details, 1, 0, 1, 4)

        self.cg_details = QLabel("CG X --   Arm --   -- %MAC")
        self.cg_details.setStyleSheet(
            "font-family: Consolas, 'Courier New', monospace; color: #cfcfcf;"
        )
        layout.addWidget(self.cg_details, 1, 4, 1, 3)

        self.cg_target_details = QLabel("CG target --")
        self.cg_target_details.setStyleSheet(
            "font-family: Consolas, 'Courier New', monospace; color: #cfcfcf;"
        )
        layout.addWidget(self.cg_target_details, 2, 0, 1, 7)

        self.span_input.editingFinished.connect(
            lambda: self.dimensionEdited.emit("span", self.span_input.value())
        )
        self.chord_input.editingFinished.connect(
            lambda: self.dimensionEdited.emit("chord", self.chord_input.value())
        )
        self.wing_le_x_input.editingFinished.connect(
            lambda: self.dimensionEdited.emit("wing_le_x", self.wing_le_x_input.value())
        )

    @staticmethod
    def _make_spinbox(minimum: float, maximum: float) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(minimum, maximum)
        box.setDecimals(4)
        box.setSingleStep(0.01)
        box.setSuffix(" m")
        box.setKeyboardTracking(False)
        return box

    def set_design_context(
        self,
        *,
        span_m: float,
        chord_m: float,
        wing_le_x_m: float,
        tail_arm_ratio: float,
        cg_x_m: float | None,
        cg_y_m: float = 0.0,
        cg_z_m: float = 0.0,
        cg_forward_mac_percent: float = 20.0,
        cg_aft_mac_percent: float = 30.0,
    ) -> None:
        """Synchronize editable dimensions and derived geometry/CG details."""

        for box, value in (
            (self.span_input, span_m),
            (self.chord_input, chord_m),
            (self.wing_le_x_input, wing_le_x_m),
        ):
            box.blockSignals(True)
            try:
                box.setValue(value)
            finally:
                box.blockSignals(False)

        wing_area = span_m * chord_m
        aspect_ratio = span_m**2 / wing_area if wing_area > 0.0 else 0.0
        tail_arm = max(0.0, tail_arm_ratio * chord_m)
        self.geometry_details.setText(
            f"Area {wing_area:.4f} m²   AR {aspect_ratio:.2f}   "
            f"Tail arm {tail_arm:.3f} m"
        )

        forward_x = wing_le_x_m + chord_m * cg_forward_mac_percent / 100.0
        aft_x = wing_le_x_m + chord_m * cg_aft_mac_percent / 100.0

        if cg_x_m is None or chord_m <= 0.0:
            self.cg_details.setText("CG X --   Arm --   -- %MAC")
            self.cg_target_details.setText(
                f"CG target X {forward_x:.3f}–{aft_x:.3f} m   "
                f"({cg_forward_mac_percent:.1f}–{cg_aft_mac_percent:.1f}% MAC)"
            )
            self.cg_target_details.setStyleSheet(
                "font-family: Consolas, 'Courier New', monospace; color: #cfcfcf;"
            )
            return

        cg_arm = cg_x_m - wing_le_x_m
        cg_percent = cg_arm / chord_m * 100.0
        in_target = forward_x <= cg_x_m <= aft_x
        status = "IN TARGET" if in_target else "OUTSIDE TARGET"
        status_color = "#76d275" if in_target else "#f2c94c"

        self.cg_details.setText(
            f"CG X {cg_x_m:.3f} m   Arm {cg_arm:.3f} m   "
            f"{cg_percent:.1f}% MAC   Y {cg_y_m:+.3f}   Z {cg_z_m:+.3f}"
        )
        self.cg_target_details.setText(
            f"CG target X {forward_x:.3f}–{aft_x:.3f} m   "
            f"({cg_forward_mac_percent:.1f}–{cg_aft_mac_percent:.1f}% MAC)   "
            f"{status}"
        )
        self.cg_target_details.setStyleSheet(
            "font-family: Consolas, 'Courier New', monospace; "
            f"color: {status_color}; font-weight: bold;"
        )


class AircraftLayoutView(QGraphicsView):
    """Top view with CAD coordinates, dimensions, target band, and aircraft CG."""

    SCALE = 500.0

    def __init__(self) -> None:
        super().__init__()
        self.setScene(QGraphicsScene())

        self._aircraft: Aircraft | None = None
        self._cg_x_m: float | None = None
        self._cg_y_m: float = 0.0
        self._cg_z_m: float = 0.0
        self._cg_measured = False

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )
        self.setMinimumHeight(500)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

        self._geometry_overlay = self._make_overlay_label()
        self._cg_overlay = self._make_overlay_label()
        self._coordinate_overlay = self._make_overlay_label()
        self._axis_indicator = AxisIndicator(self.viewport())
        self._axis_indicator.show()

        self._geometry_overlay.setText("PLANFORM\nSPAN --\nMAC --\nAREA --\nAR --")
        self._cg_overlay.setText("FULL-AIRCRAFT CG\nX --\nY --\nZ --\n-- % MAC")
        self._coordinate_overlay.setText("X --   Y --")

        self._position_overlays()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set_aircraft(self, aircraft: Aircraft) -> None:
        """Set the aircraft and redraw the planform."""

        self._aircraft = aircraft
        self._redraw()

    def set_cg(
        self,
        cg_x_m: float | None,
        cg_y_m: float = 0.0,
        measured: bool = False,
        cg_z_m: float = 0.0,
    ) -> None:
        """Set resultant CG in local wing-reference drawing coordinates.

        ``cg_x_m`` is relative to the wing leading edge in scene coordinates.
        Aft-of-leading-edge locations are negative because aircraft station +X
        points aft while scene +X points forward.
        """

        self._cg_x_m = cg_x_m
        self._cg_y_m = cg_y_m
        self._cg_z_m = cg_z_m
        self._cg_measured = measured
        self._redraw()

    def set_cg_x(
        self,
        cg_x_m: float | None,
        measured: bool = False,
    ) -> None:
        """Backward-compatible single-axis CG setter."""

        self.set_cg(cg_x_m, 0.0, measured)

    def clear_aircraft(self) -> None:
        """Clear the aircraft layout and reset the overlays."""

        self._aircraft = None
        self._cg_x_m = None
        scene = self.scene()
        if scene is not None:
            scene.clear()

        self._geometry_overlay.setText("PLANFORM\nSPAN --\nMAC --\nAREA --\nAR --")
        self._cg_overlay.setText("FULL-AIRCRAFT CG\nX --\nY --\nZ --\n-- % MAC")
        self._coordinate_overlay.setText("X --   Y --")
        self._refresh_overlay_sizes()

    def scene_to_aircraft_coordinates(
        self,
        scene_point: QPointF,
    ) -> tuple[float, float] | None:
        """Convert a scene position to absolute aircraft datum X and lateral Y."""

        if self._aircraft is None:
            return None

        wing_le_x_m = self._aircraft.requirements.wing_le_x_m
        local_x_m = scene_point.x() / self.SCALE
        lateral_y_m = scene_point.y() / self.SCALE

        aircraft_x_m = wing_le_x_m - local_x_m
        return aircraft_x_m, lateral_y_m

    # ------------------------------------------------------------------
    # Qt events / fixed CAD overlays
    # ------------------------------------------------------------------

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt API name
        """Update the fixed lower-left CAD coordinate readout."""

        if self._aircraft is not None:
            scene_point = self.mapToScene(event.position().toPoint())
            coordinates = self.scene_to_aircraft_coordinates(scene_point)
            if coordinates is not None:
                x_m, y_m = coordinates
                self._coordinate_overlay.setText(
                    f"X {x_m:+.3f} m   Y {y_m:+.3f} m"
                )
                self._coordinate_overlay.adjustSize()
                self._position_overlays()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802 - Qt API name
        self._coordinate_overlay.setText("X --   Y --")
        self._coordinate_overlay.adjustSize()
        self._position_overlays()
        super().leaveEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().resizeEvent(event)
        self._position_overlays()

    def _make_overlay_label(self) -> QLabel:
        label = QLabel(self.viewport())
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        label.setStyleSheet(
            "QLabel {"
            " background-color: rgba(20, 20, 20, 205);"
            " color: #f2f2f2;"
            " border: 1px solid rgba(160, 160, 160, 120);"
            " border-radius: 4px;"
            " padding: 6px 8px;"
            " font-family: Consolas, 'Courier New', monospace;"
            " font-size: 11px;"
            "}"
        )
        label.show()
        return label

    def _refresh_overlay_sizes(self) -> None:
        for overlay in (
            self._geometry_overlay,
            self._cg_overlay,
            self._coordinate_overlay,
        ):
            overlay.adjustSize()
        self._position_overlays()

    def _position_overlays(self) -> None:
        margin = 10
        viewport = self.viewport()

        self._geometry_overlay.adjustSize()
        self._cg_overlay.adjustSize()
        self._coordinate_overlay.adjustSize()

        self._geometry_overlay.move(margin, margin)
        self._cg_overlay.move(
            max(margin, viewport.width() - self._cg_overlay.width() - margin),
            margin,
        )
        axis_y = max(
            margin,
            viewport.height() - self._axis_indicator.height() - margin,
        )
        self._axis_indicator.move(margin, axis_y)
        self._coordinate_overlay.move(
            margin + self._axis_indicator.width() + 6,
            max(
                margin,
                viewport.height() - self._coordinate_overlay.height() - margin,
            ),
        )

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _add_arrowhead(
        self,
        tip: QPointF,
        direction: str,
        pen: QPen,
        brush: QBrush,
        size: float = 6.0,
    ) -> None:
        scene = self.scene()
        if scene is None:
            return

        if direction == "left":
            points = [tip, QPointF(tip.x() + size, tip.y() - size / 2), QPointF(tip.x() + size, tip.y() + size / 2)]
        elif direction == "right":
            points = [tip, QPointF(tip.x() - size, tip.y() - size / 2), QPointF(tip.x() - size, tip.y() + size / 2)]
        elif direction == "up":
            points = [tip, QPointF(tip.x() - size / 2, tip.y() + size), QPointF(tip.x() + size / 2, tip.y() + size)]
        else:  # down
            points = [tip, QPointF(tip.x() - size / 2, tip.y() - size), QPointF(tip.x() + size / 2, tip.y() - size)]

        item = QGraphicsPolygonItem(QPolygonF(points))
        item.setPen(pen)
        item.setBrush(brush)
        scene.addItem(item)

    def _add_dimension_line(
        self,
        start: QPointF,
        end: QPointF,
        text: str,
        *,
        orientation: str,
        color: QColor | Qt.GlobalColor = Qt.GlobalColor.lightGray,
    ) -> None:
        """Add a lightweight two-headed CAD dimension with centered text."""

        scene = self.scene()
        if scene is None:
            return

        pen = QPen(color, 1)
        brush = QBrush(color)
        line = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
        line.setPen(pen)
        scene.addItem(line)

        if orientation == "horizontal":
            left, right = (start, end) if start.x() <= end.x() else (end, start)
            self._add_arrowhead(left, "right", pen, brush)
            self._add_arrowhead(right, "left", pen, brush)
            label = self._add_label(text, 0.0, 0.0, point_size=8, bold=False, brush=color)
            if label is not None:
                bounds = label.boundingRect()
                label.setPos(
                    (start.x() + end.x()) / 2.0 - bounds.width() / 2.0,
                    start.y() - bounds.height() - 3.0,
                )
        else:
            top, bottom = (start, end) if start.y() <= end.y() else (end, start)
            self._add_arrowhead(top, "down", pen, brush)
            self._add_arrowhead(bottom, "up", pen, brush)
            label = self._add_label(text, 0.0, 0.0, point_size=8, bold=False, brush=color)
            if label is not None:
                bounds = label.boundingRect()
                label.setPos(
                    start.x() + 4.0,
                    (start.y() + end.y()) / 2.0 - bounds.height() / 2.0,
                )

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _redraw(self) -> None:
        scene = self.scene()
        if scene is None:
            return

        scene.clear()
        if self._aircraft is None:
            self._refresh_overlay_sizes()
            return

        geometry = self._aircraft.geometry
        propulsion = self._aircraft.propulsion
        requirements = self._aircraft.requirements

        span = geometry.wing_span_m
        chord = geometry.mean_chord_m
        wing_area = span * chord
        aspect_ratio = span**2 / wing_area if wing_area > 0.0 else 0.0
        wing_le_x_m = requirements.wing_le_x_m
        prop_diameter = propulsion.propeller_diameter_in * 0.0254
        scale = self.SCALE

        def s(value: float) -> float:
            return value * scale

        # Horizontal-tail planform is derived from the user's volume/arm/AR
        # assumptions so the view changes with engineering inputs instead of a
        # purely cosmetic scale factor.
        tail_arm = max(requirements.tail_arm_chord_ratio * chord, chord * 1.5)
        htail_area = (
            requirements.horizontal_tail_volume_coefficient
            * wing_area
            * chord
            / tail_arm
        )
        htail_span = sqrt(
            max(requirements.horizontal_tail_aspect_ratio * htail_area, 1e-12)
        )
        htail_chord = htail_area / htail_span if htail_span > 0.0 else chord * 0.4

        wing_qc_x = -0.25 * chord
        tail_qc_x = wing_qc_x - tail_arm
        tail_le_x = tail_qc_x + 0.25 * htail_chord
        tail_te_x = tail_le_x - htail_chord

        fuselage_length = max(chord * 4.5, abs(tail_te_x) + chord * 1.4, 0.8)
        fuselage_width = max(chord * 0.22, 0.035)

        half_span = span / 2.0
        half_tail_span = htail_span / 2.0
        nose_x = max(fuselage_length * 0.42, wing_le_x_m + chord * 0.55)
        rear_x = min(-fuselage_length * 0.55, tail_te_x - chord * 0.1)
        half_fuselage = fuselage_width / 2.0
        datum_scene_x = wing_le_x_m

        structure_pen = QPen(Qt.GlobalColor.white, 2)
        structure_brush = QBrush(Qt.GlobalColor.lightGray)
        reference_pen = QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine)
        datum_pen = QPen(Qt.GlobalColor.yellow, 1, Qt.PenStyle.DashLine)
        cg_pen = QPen(Qt.GlobalColor.green, 2)
        cg_brush = QBrush(Qt.GlobalColor.green)
        target_color = QColor(80, 190, 170, 165)
        target_pen = QPen(target_color, 1, Qt.PenStyle.DashLine)

        # Main wing: scene x=0 is LE; chord extends aft (-X).
        wing = QGraphicsPolygonItem(
            [
                QPointF(0.0, s(-half_span)),
                QPointF(s(-chord), s(-half_span)),
                QPointF(s(-chord), s(half_span)),
                QPointF(0.0, s(half_span)),
            ]
        )
        wing.setPen(structure_pen)
        wing.setBrush(structure_brush)
        scene.addItem(wing)

        # User-defined CG target band, expressed as % MAC.
        target_forward_x = -chord * requirements.cg_forward_mac_percent / 100.0
        target_aft_x = -chord * requirements.cg_aft_mac_percent / 100.0
        target_left = min(target_forward_x, target_aft_x)
        target_width = abs(target_aft_x - target_forward_x)
        target_band = QGraphicsRectItem(
            s(target_left),
            s(-half_span),
            s(target_width),
            s(span),
        )
        target_band.setPen(QPen(Qt.PenStyle.NoPen))
        target_band.setBrush(QBrush(QColor(80, 190, 170, 38)))
        scene.addItem(target_band)

        for target_x in (target_forward_x, target_aft_x):
            target_line = QGraphicsLineItem(
                s(target_x), s(-half_span), s(target_x), s(half_span)
            )
            target_line.setPen(target_pen)
            scene.addItem(target_line)

        tail = QGraphicsPolygonItem(
            [
                QPointF(s(tail_le_x), s(-half_tail_span)),
                QPointF(s(tail_te_x), s(-half_tail_span)),
                QPointF(s(tail_te_x), s(half_tail_span)),
                QPointF(s(tail_le_x), s(half_tail_span)),
            ]
        )
        tail.setPen(structure_pen)
        tail.setBrush(structure_brush)
        scene.addItem(tail)

        fuselage = QGraphicsPolygonItem(
            [
                QPointF(s(nose_x), 0.0),
                QPointF(s(nose_x * 0.72), s(-half_fuselage)),
                QPointF(s(rear_x), s(-half_fuselage * 0.65)),
                QPointF(s(rear_x), s(half_fuselage * 0.65)),
                QPointF(s(nose_x * 0.72), s(half_fuselage)),
            ]
        )
        fuselage.setPen(structure_pen)
        fuselage.setBrush(QBrush(Qt.GlobalColor.white))
        scene.addItem(fuselage)

        centerline = QGraphicsLineItem(s(rear_x), 0.0, s(nose_x), 0.0)
        centerline.setPen(reference_pen)
        scene.addItem(centerline)

        datum_half_height = max(half_fuselage * 2.4, 0.055)
        datum_line = QGraphicsLineItem(
            s(datum_scene_x),
            s(-datum_half_height),
            s(datum_scene_x),
            s(datum_half_height),
        )
        datum_line.setPen(datum_pen)
        scene.addItem(datum_line)

        prop_radius = prop_diameter / 2.0
        prop_disk = QGraphicsEllipseItem(
            s(nose_x - prop_radius),
            s(-prop_radius),
            s(prop_diameter),
            s(prop_diameter),
        )
        prop_disk.setPen(reference_pen)
        prop_disk.setBrush(Qt.BrushStyle.NoBrush)
        scene.addItem(prop_disk)

        # Lightweight CAD dimensions outside the planform.
        dim_color = QColor(180, 180, 180, 210)
        span_dim_x = s(0.07)
        for wing_tip_y in (-half_span, half_span):
            extension = QGraphicsLineItem(
                0.0,
                s(wing_tip_y),
                span_dim_x,
                s(wing_tip_y),
            )
            extension.setPen(QPen(dim_color, 1))
            scene.addItem(extension)
        self._add_dimension_line(
            QPointF(span_dim_x, s(-half_span)),
            QPointF(span_dim_x, s(half_span)),
            f"SPAN {span:.3f} m",
            orientation="vertical",
            color=dim_color,
        )

        chord_dim_y = s(-half_span - 0.065)
        for chord_x in (0.0, -chord):
            extension = QGraphicsLineItem(
                s(chord_x),
                s(-half_span),
                s(chord_x),
                chord_dim_y,
            )
            extension.setPen(QPen(dim_color, 1))
            scene.addItem(extension)
        self._add_dimension_line(
            QPointF(s(-chord), chord_dim_y),
            QPointF(0.0, chord_dim_y),
            f"MAC {chord:.3f} m",
            orientation="horizontal",
            color=dim_color,
        )

        if abs(wing_le_x_m) > 1e-6:
            datum_dim_y = s(half_span + 0.065)
            for x_value in (0.0, datum_scene_x):
                extension = QGraphicsLineItem(
                    s(x_value),
                    s(half_span),
                    s(x_value),
                    datum_dim_y,
                )
                extension.setPen(QPen(Qt.GlobalColor.yellow, 1))
                scene.addItem(extension)
            self._add_dimension_line(
                QPointF(0.0, datum_dim_y),
                QPointF(s(datum_scene_x), datum_dim_y),
                f"LE X {wing_le_x_m:.3f} m",
                orientation="horizontal",
                color=Qt.GlobalColor.yellow,
            )

        # Minimal planform identifiers.
        self._add_label("NOSE", s(nose_x + 0.015), s(-0.035), point_size=8)
        self._add_label(
            "DATUM",
            s(datum_scene_x + 0.008),
            s(datum_half_height + 0.008),
            point_size=8,
            brush=Qt.GlobalColor.yellow,
        )
        self._add_label("LE", s(0.008), s(-half_span + 0.015), point_size=8)
        self._add_label("TE", s(-chord + 0.008), s(-half_span + 0.015), point_size=8)
        self._add_label(
            "CL",
            s(rear_x + 0.025),
            s(0.012),
            point_size=8,
            brush=Qt.GlobalColor.gray,
        )
        self._add_label(
            "CG TARGET",
            s(target_left),
            s(half_span + 0.01),
            point_size=7,
            bold=False,
            brush=target_color,
        )

        if self._cg_x_m is not None:
            cg_x = self._cg_x_m
            cg_y = self._cg_y_m
            cg_radius = max(chord * 0.055, 0.014)
            cross_size = max(chord * 0.12, 0.025)

            cg_cross_x = QGraphicsLineItem(
                s(cg_x - cross_size),
                s(cg_y),
                s(cg_x + cross_size),
                s(cg_y),
            )
            cg_cross_y = QGraphicsLineItem(
                s(cg_x),
                s(cg_y - cross_size),
                s(cg_x),
                s(cg_y + cross_size),
            )
            cg_cross_x.setPen(cg_pen)
            cg_cross_y.setPen(cg_pen)
            scene.addItem(cg_cross_x)
            scene.addItem(cg_cross_y)

            cg = QGraphicsEllipseItem(
                s(cg_x - cg_radius),
                s(cg_y - cg_radius),
                s(cg_radius * 2.0),
                s(cg_radius * 2.0),
            )
            cg.setPen(cg_pen)
            cg.setBrush(cg_brush)
            scene.addItem(cg)

            self._add_label(
                "CG",
                s(cg_x + cg_radius + 0.010),
                s(cg_y - 0.020),
                point_size=9,
                brush=Qt.GlobalColor.green,
            )

            cg_abs_x = wing_le_x_m - cg_x
            cg_arm = cg_abs_x - wing_le_x_m
            cg_percent_mac = cg_arm / chord * 100.0 if chord > 0.0 else 0.0
            source_line = "MASS INPUTS" if self._cg_measured else "CALCULATED"
            self._cg_overlay.setText(
                "FULL-AIRCRAFT CG\n"
                f"X {cg_abs_x:.3f} m\n"
                f"Y {self._cg_y_m:+.3f} m\n"
                f"Z {self._cg_z_m:+.3f} m\n"
                f"ARM {cg_arm:.3f} m  |  {cg_percent_mac:.1f}% MAC\n"
                f"{source_line}"
            )

            # CG-arm dimension from LE to calculated CG.
            if abs(cg_x) > 1e-6:
                cg_dim_y = s(half_span + 0.12)
                self._add_dimension_line(
                    QPointF(s(cg_x), cg_dim_y),
                    QPointF(0.0, cg_dim_y),
                    f"CG ARM {cg_arm:.3f} m / {cg_percent_mac:.1f}% MAC",
                    orientation="horizontal",
                    color=Qt.GlobalColor.green,
                )
        else:
            self._cg_overlay.setText(
                "FULL-AIRCRAFT CG\n"
                "X --\nY --\nZ --\n"
                "Enter mass/location data"
            )

        self._geometry_overlay.setText(
            "PLANFORM\n"
            f"SPAN {span:.3f} m\n"
            f"MAC  {chord:.3f} m\n"
            f"AREA {wing_area:.4f} m²\n"
            f"AR   {aspect_ratio:.2f}"
        )

        x_min = min(rear_x, tail_te_x, -chord) - 0.18
        x_max = max(nose_x + prop_radius, datum_scene_x, 0.07) + 0.18
        extra_y = 0.20 if self._cg_x_m is not None else 0.13
        y_min = -max(half_span, prop_radius) - 0.14
        y_max = max(half_span, prop_radius) + extra_y

        scene.setSceneRect(
            s(x_min),
            s(y_min),
            s(x_max - x_min),
            s(y_max - y_min),
        )
        self.resetTransform()
        self.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._refresh_overlay_sizes()

    def _add_label(
        self,
        text: str,
        x: float,
        y: float,
        *,
        point_size: int = 9,
        bold: bool = True,
        brush: QColor | Qt.GlobalColor = Qt.GlobalColor.white,
    ) -> QGraphicsSimpleTextItem | None:
        """Add a small planform identifier and return it for optional positioning."""

        scene = self.scene()
        if scene is None:
            return None

        label = QGraphicsSimpleTextItem(text)
        label.setBrush(QBrush(brush))
        font = QFont()
        font.setPointSize(point_size)
        font.setBold(bold)
        label.setFont(font)
        label.setPos(x, y)
        scene.addItem(label)
        return label
