# MCore Development and Release Workflow

MCore uses AI agents for coordination and interpretation while deterministic Python modules remain the numerical engineering authority.

## 1. Start from a clean main branch

```powershell
git switch main
git pull
python -m pytest -q
```

Do not begin a feature from a failing baseline.

## 2. Create a feature branch

```powershell
git switch -c feature/<short-name>
```

Examples:

```powershell
git switch -c feature/rc-plane-validation
git switch -c feature/propulsion-test-map
```

## 3. Use the MCore agent boundary

```text
Human objective
    ↓
Orchestrator
    ↓
Aerospace / Propulsion / Software specialist
    ↓
Deterministic engineering modules
    ↓
Verification agent + automated tests
    ↓
Human engineering decision
```

Agent rules:

- Never replace an implemented deterministic calculation with an LLM estimate.
- Preserve measured vs estimated data provenance.
- State assumptions and uncertainty.
- Use `python -m app.rapid_cli analyze <project.json> --json` as the preferred machine-readable engineering interface.
- Treat software tests as implementation verification, not airworthiness approval.

## 4. Local verification

Run:

```powershell
python -m compileall -q app
python -m pytest -q
python -m app.rapid_cli analyze data\projects\rapid_sizer_example.json --json
.\launch.ps1
```

Perform a GUI smoke test for New, Load, Save, dimension editing, CG, Undo/Redo, Analyze, and report export.

## 5. Commit and push

```powershell
git add .
git status
git commit -m "Describe the engineering change"
git push -u origin HEAD
```

## 6. GitHub CI

Every push/pull request runs the complete Windows/Python 3.12 test suite and a deterministic CLI smoke test. A failing CI run blocks release.

## 7. Release gate

Release only when:

- deterministic tests pass locally;
- GitHub CI passes;
- GUI smoke test passes;
- engineering assumptions and limitations are documented;
- changed equations are independently checked;
- the reference/sample project still analyzes successfully;
- real-aircraft validation evidence is updated when the affected model has physical test coverage.

## 8. Tag a release

```powershell
git switch main
git pull
git tag -a v1.5.0 -m "MCore UAV Rapid Sizer v1.5.0"
git push origin v1.5.0
```

Do not tag a release from an unverified feature branch.
