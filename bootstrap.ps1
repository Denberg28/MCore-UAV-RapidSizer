$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "MCore UAV Rapid Sizer - local bootstrap"

if (-not (Test-Path ".venv")) {
    py -3.12 -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$env:QT_QPA_PLATFORM = "offscreen"
python -m compileall -q app
python -m pytest -q
python -m app.rapid_cli analyze data\projects\rapid_sizer_example.json --json

Write-Host ""
Write-Host "Bootstrap and verification complete."
Write-Host "Launch with: .\launch.ps1"
