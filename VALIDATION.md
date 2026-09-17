# Validation — MCore UAV Rapid Sizer v1.5

## Build-environment validation

- Python source compilation: PASS
- Backend/non-GUI regression suite: **70 passed**
- GUI regression tests included: **15**
- Expected complete suite on Windows with PySide6 installed: **85 tests**

## v1.5 additions covered

- Existing global Ctrl+Z Undo and Ctrl+Y / Ctrl+Shift+Z Redo retained.
- Lower-left CAD-style +X/+Y axis and live datum-coordinate readout retained.
- Dimension editor synchronization with canonical wing span, MAC, and wing-LE station inputs.
- Dimension edits use the same global Undo/Redo history as the rest of the project.
- Live derived wing area, aspect ratio, tail arm, CG arm, %MAC, and absolute target stations.
- CAD planform dimensions for span, MAC, wing-LE datum offset, and calculated CG arm.
- User-defined CG target band translated from forward/aft %MAC settings.
- Horizontal-tail planform responds to tail-volume, tail-arm, and horizontal-tail aspect-ratio inputs.
- Absolute aircraft CG remains calculated from component mass/location inputs.

PySide6 is not installed in the build sandbox, so GUI tests cannot execute here. Run `python -m pytest -q` on the Windows MCore installation to execute the full suite.
