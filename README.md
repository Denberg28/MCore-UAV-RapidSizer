# MCore UAV Rapid Sizer v1.5

MCore UAV Rapid Sizer is a requirements-driven fixed-wing UAV conceptual/preliminary design tool for rapid prototyping.

It is built around a strict engineering boundary:

**Human / AI objective → deterministic engineering engine → independent checks → traceable result → prototype/test evidence**

AI agents coordinate, interpret, and explain. They do not replace deterministic sizing equations or measured engineering data.

## Product workflow

1. Create or load a project.
2. Enter design mass, battery, and propulsion reference data.
3. Enter mission requirements and aerodynamic assumptions.
4. Use **Apply Sized Wing** to size a rectangular reference wing from stall speed, CLmax, mass, air density, and target aspect ratio.
5. Build the component mass inventory using measured or estimated values and datum coordinates. The top-view viewer shows only the resultant full-aircraft CG calculated from those inputs.
6. Run **Analyze**.
7. Review stall, power, energy, battery-current, mass-budget, CG, and verification checks.
8. Export the Markdown preliminary design report.
9. Replace assumptions with measured/test data as the prototype matures.

## Main engineering capabilities

- SI-unit engineering core
- Requirements-driven stall-based wing sizing
- Wing area, aspect ratio, and wing loading
- Parabolic drag-polar cruise estimate
- Cruise and climb electrical power estimates
- Battery energy, reserve, capacity, and C-rating current checks
- Static-thrust design target from T/W
- Component mass inventory
- X/Y/Z mass moments and CG
- CAD-style datum X/Y cursor coordinates and axis glyph
- clean full-aircraft CG marker plus user-defined CG target band
- editable mass inventory for mass, X/Y/Z, source, and uncertainty
- top-view coordinate convention: X station increases aft from the project datum; +Y is starboard
- CG as percent MAC against a **user-defined design target**
- integrated dimension editor for wing span, MAC, and wing LE datum station
- live derived wing area, aspect ratio, tail arm, CG arm, %MAC, and absolute CG target stations
- CAD dimension lines for span, MAC, wing-LE station, and calculated CG arm
- Measured vs estimated mass-source tracking
- RSS mass uncertainty summary
- Sheet material mass: area × areal density
- Solid material mass: volume × density
- Versioned JSON project persistence with legacy v0.1 loading
- Independent deterministic mass-property verification
- Markdown design-report export
- Agent-friendly JSON CLI
- CAAP mass-reference information for Philippine projects

## Install on Windows PowerShell

```powershell
cd C:\MCore\PROJECTS\UAV-Layout-Sizing
python -m pip install -r requirements.txt
```

## Launch GUI

```powershell
.\launch.ps1
```

or:

```powershell
python -m app.gui.main_window
```

## Run tests

```powershell
.\test.ps1
```

or:

```powershell
python -m pytest -q
```

## Agent / CLI interface

Analyze a project and return machine-readable JSON:

```powershell
python -m app.rapid_cli analyze data\projects\rapid_sizer_example.json --json
```

Apply requirements-driven wing sizing and write a new project:

```powershell
python -m app.rapid_cli size-wing data\projects\rapid_sizer_example.json --output data\projects\rapid_sizer_sized.json
```

Generate a report:

```powershell
python -m app.rapid_cli report data\projects\rapid_sizer_example.json data\projects\rapid_sizer_report.md
```

## Engineering status language

- **PASS** — the checked preliminary requirement is satisfied by the current model/data.
- **CHECK** — a preliminary requirement is not satisfied or needs engineering attention.
- **NOT CHECKED** — required data is missing.
- **INFO** — informational classification/reference only.

A PASS is **not** a flight-safety approval or airworthiness certification.

## Product scope

v1.5 is intended for conventional fixed-wing rapid prototyping and early design trades. It is not a substitute for:

- detailed CFD/aerodynamic validation
- stability derivatives and full neutral-point analysis
- structural loads/stress/buckling/fatigue analysis
- aeroelastic/flutter analysis
- validated propeller/motor test maps
- control-authority and actuator-load analysis
- EMI/EMC, software/hardware assurance, reliability, or safety assessment
- configuration-controlled ground and flight test programs
- regulatory approval

See `ENGINEERING_BASIS.md` and `DEVELOPMENT_GATES.md`.


## Clean CAD-style CG viewer

The planform viewer is intentionally minimal. It shows the aircraft outline, the engineering datum, a single calculated full-aircraft CG marker, a compact planform summary, a compact X/Y/Z CG summary, and a lower-left live cursor coordinate readout. Cursor X uses the same datum/station convention as the mass-properties inventory. No component markers or full XY grid are drawn.

## AI-agent development workflow

The repository includes the MCore orchestrator and specialist role definitions under both `.opencode/agents/` and `AGENTS/` for portability. The intended boundary is:

```text
Human engineering objective
        ↓
Orchestrator
        ↓
Aerospace / Propulsion / Software agent
        ↓
Deterministic app.engineering / app.services
        ↓
Verification + pytest
        ↓
Human decision / physical test
```

For an existing project, agents should prefer the deterministic JSON interface:

```powershell
python -m app.rapid_cli analyze data\projects\rapid_sizer_example.json --json
```

See `docs/DEVELOPMENT_WORKFLOW.md`.

## GitHub and CI

This repository includes `.github/workflows/tests.yml`. GitHub Actions runs the complete Windows/Python 3.12 test suite and a deterministic CLI smoke test on pushes and pull requests to `main`.

To prepare a fresh development machine:

```powershell
.\bootstrap.ps1
```

To create/publish the repository from a standalone checkout after authenticating GitHub CLI:

```powershell
gh auth login
.\PUBLISH_GITHUB.ps1
```

The publisher defaults to a **private** `Denberg28/MCore-UAV-RapidSizer` repository and refuses to invent a Git commit identity.

For physical validation, copy `docs/RC_PLANE_VALIDATION_TEMPLATE.md` for each tested aircraft/configuration.
