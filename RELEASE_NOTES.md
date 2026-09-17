# MCore UAV Rapid Sizer v1.5

- Added a compact dimension editor directly below the CAD planform.
- Wing span, MAC, and wing leading-edge X station edit the canonical project inputs.
- Dimension edits participate in the existing global Undo/Redo stack.
- Added live wing area, aspect ratio, tail-arm, CG-arm, %MAC, and absolute CG-target station details.
- Added clean CAD dimension lines for span, MAC, wing-LE datum offset, and CG arm.
- Added a user-defined CG target band on the wing; changing MAC or wing LE translates the target stations and %MAC interpretation immediately.
- Horizontal-tail planform now responds to the tail-volume, tail-arm, and horizontal-tail aspect-ratio assumptions instead of using a fixed cosmetic scale.
- Absolute aircraft CG remains determined only by the component mass inventory. Geometry edits do not invent or move mass.
- Core deterministic engineering and AI-agent contracts remain unchanged.

# MCore UAV Rapid Sizer v1.4

- Added global Undo/Redo history for design parameters and mass inventory.
- Added Ctrl+Z for Undo and Ctrl+Y / Ctrl+Shift+Z for Redo.
- Added visible Undo and Redo buttons plus an Edit menu.
- Added a lower-left CAD-style +X/+Y axis glyph aligned with the engineering coordinate convention.
- Retained the clean single-CG viewer and lower-left live coordinate readout.
- Core deterministic engineering and AI-agent roles are unchanged.

# MCore UAV Rapid Sizer v1.3

- Simplified the aircraft viewer to remove XY grid and individual mass markers.
- Viewer now shows only the resultant full-aircraft CG calculated from mass/location inputs.
- Retained editable mass inventory table and deterministic X/Y/Z CG calculation.
- CG display includes datum X, lateral Y, and percent MAC.
- Core AI-agent roles unchanged.

# MCore UAV Rapid Sizer v1.1 — Release Notes

## v1.1 — Interactive mass-layout update

- added datum-based X/Y rulers and engineering coordinate grid to the top-view viewer
- aligned viewer X coordinates with weight-and-balance station convention: X station increases aft from the datum
- corrected rectangular wing drawing so chord extends aft from the leading edge
- added component mass markers at their stored X/Y coordinates
- mass markers are draggable; release commits X/Y back to the project mass table
- double-clicking a mass marker opens an editor for component name, mass, X/Y/Z, source, and uncertainty
- mass-table edits now refresh the viewer and deterministic CG preview live
- CG marker now displays both X and Y and follows the mass inventory without requiring a full Analyze run
- added GUI regression tests for marker movement, mass/location editing, and live CG summary
- AI-agent contracts are unchanged; this is a GUI/data-entry capability update only

## From prototype to product

The previous foundation already had clean separation between models, engineering calculations, services, GUI, persistence, verification, and tests. v1.0 keeps that architecture and completes the first practical fixed-wing rapid-prototyping workflow.

## Added

- requirements-driven wing sizing from mass, stall speed, CLmax, density, and target AR
- reference horizontal/vertical tail sizing using explicit tail-volume assumptions
- cruise drag and power estimate using an explicit parabolic drag polar
- climb electrical power estimate
- battery reserve, required energy/capacity, predicted endurance, and theoretical current margin
- component mass inventory with measured/estimated provenance and uncertainty
- real X/Y/Z CG and percent-MAC calculation
- independent mass-properties verifier
- mass-budget closure and mass-data-maturity checks
- user-defined CG design target check
- sheet and solid-material mass estimators
- versioned JSON schema with backward loading of legacy projects
- rapid-sizing GUI workflow
- New/Load/Save/Save As/Apply Sized Wing/Analyze/Export Report actions
- live measured-CG marker on aircraft view
- Markdown preliminary design report
- agent-friendly JSON CLI
- CAAP mass-reference information
- engineering-basis and prototype-development-gate documentation
- minimal deterministic-tool contract updates to MCore agent roles

## Deliberately not claimed

v1.0 does not certify airworthiness, validate structural strength, establish a final CG envelope, prove stability/control, or certify a motor/propeller combination. Those are explicit downstream development gates requiring analysis and/or test evidence.

## v1.3 - Clean CAD Viewer

- Added a fixed lower-left CAD-style cursor coordinate display.
- Cursor X uses the same aircraft datum/station reference as mass properties and CG.
- Added a compact top-right full-aircraft CG panel with X, Y, Z, and % MAC.
- Added a compact top-left planform panel for span and MAC.
- Limited planform identifiers to NOSE, DATUM, LE, TE, CL, and CG.
- Removed the synthetic 25% MAC fallback marker; CG is shown only when mass/location inputs produce a calculated aircraft CG.
- Passed CG Z from the mass-properties engine into the viewer summary.
- Core MCore AI-agent roles remain unchanged.
