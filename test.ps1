$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Python = "python"
$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $Python = $VenvPython
}

$env:QT_QPA_PLATFORM = "offscreen"
& $Python -m pytest -q
exit $LASTEXITCODE
