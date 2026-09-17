$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Installing MCore UAV Rapid Sizer dependencies..."

if (-not (Test-Path ".venv")) {
    py -3.12 -m venv .venv
}

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt

Write-Host "Running regression tests..."
$env:QT_QPA_PLATFORM = "offscreen"
& $Python -m pytest -q

Write-Host "Installation complete. Launch with: .\launch.ps1"
