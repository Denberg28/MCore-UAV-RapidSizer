param(
    [string]$Owner = "Denberg28",
    [string]$RepoName = "MCore-UAV-RapidSizer",
    [ValidateSet("private", "public")]
    [string]$Visibility = "private"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. Install it and run this script again."
    }
}

Require-Command "git"
Require-Command "gh"

$Python = "python"
$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $Python = $VenvPython
}

Write-Host "=== MCore pre-publish verification ==="
$env:QT_QPA_PLATFORM = "offscreen"
& $Python -m compileall -q app
& $Python -m pytest -q
& $Python -m app.rapid_cli analyze data\projects\rapid_sizer_example.json --json | Out-Null

Write-Host "=== GitHub authentication ==="
gh auth status

if (-not (Test-Path ".git")) {
    git init -b main
}

# Ensure main is the active branch where possible.
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    git checkout -b main
} elseif ($currentBranch -ne "main") {
    git branch -M main
}

# Refuse to commit when Git identity is missing rather than inventing it.
$userName = git config user.name
$userEmail = git config user.email
if (-not $userName -or -not $userEmail) {
    throw @"
Git identity is not configured.
Run these commands with your preferred commit identity, then rerun this script:

  git config --global user.name "Your Name"
  git config --global user.email "your-github-email@example.com"
"@
}

git add .

# Commit only when there are staged changes.
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Release MCore UAV Rapid Sizer v1.5"
}

$fullRepo = "$Owner/$RepoName"

gh repo view $fullRepo --json nameWithOwner 2>$null | Out-Null
$repoExists = ($LASTEXITCODE -eq 0)

if (-not $repoExists) {
    Write-Host "Creating GitHub repository $fullRepo ($Visibility)..."
    if ($Visibility -eq "private") {
        gh repo create $fullRepo --private --source . --remote origin --push
    } else {
        gh repo create $fullRepo --public --source . --remote origin --push
    }
} else {
    Write-Host "Repository $fullRepo already exists."
    $origin = git remote get-url origin 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $origin) {
        git remote add origin "https://github.com/$fullRepo.git"
    }
    git push -u origin main
}

Write-Host ""
Write-Host "Published: https://github.com/$fullRepo"
Write-Host "GitHub Actions will run automatically after the push."
