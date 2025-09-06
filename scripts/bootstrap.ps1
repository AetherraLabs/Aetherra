<#
.SYNOPSIS
  Aetherra Alpha bootstrap (Windows PowerShell).
.DESCRIPTION
  Creates virtual environment, installs project (editable), runs smoke & regression fast tests.
.PARAMETERS
  -Version <string> (optional) override version env AETHERRA_VERSION.
.EXAMPLE
  ./scripts/bootstrap.ps1 -Version 0.1.0-alpha.1
#>
[CmdletBinding()]
param(
    [string]$Version = ""
)

Write-Host "[BOOTSTRAP] Starting Aetherra bootstrap (PowerShell)" -ForegroundColor Cyan

# Ensure python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { Write-Error "python not found in PATH"; exit 2 }

# Virtual env
if (-not (Test-Path .venv)) {
    Write-Host "[BOOTSTRAP] Creating virtual environment .venv" -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-Error "venv creation failed"; exit 2 }
}
. .\.venv\Scripts\Activate.ps1

Write-Host "[BOOTSTRAP] Upgrading pip/setuptools/wheel" -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel >$null

Write-Host "[BOOTSTRAP] Installing project (editable) + dev extras" -ForegroundColor Yellow
python -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) { Write-Error "install failed"; exit 2 }

if ($Version) { $env:AETHERRA_VERSION = $Version }

Write-Host "[BOOTSTRAP] Running smoke test" -ForegroundColor Yellow
python tools/os_smoke.py --profile test
if ($LASTEXITCODE -ne 0) { Write-Error "smoke failed"; exit 3 }

Write-Host "[BOOTSTRAP] Running regression fast set" -ForegroundColor Yellow
python tools/run_regression_suite.py
if ($LASTEXITCODE -ne 0) { Write-Error "regression failed"; exit 4 }

Write-Host "[BOOTSTRAP] Running quality gates" -ForegroundColor Yellow
python tools/quality_gates.py
if ($LASTEXITCODE -ne 0) { Write-Error "quality gates failed"; exit 5 }

Write-Host "[BOOTSTRAP] Success" -ForegroundColor Green
