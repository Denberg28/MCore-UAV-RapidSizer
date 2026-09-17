$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Python = "python"
$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $Python = $VenvPython
}

& $Python -m app.gui.main_window
exit $LASTEXITCODE
