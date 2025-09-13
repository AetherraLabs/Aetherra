<#
.SYNOPSIS
  Local security scan helper (Bandit + pip-audit) producing SARIF artifacts.

.DESCRIPTION
  Runs Bandit over the codebase and pip-audit against dependencies, ensuring
  SARIF files (bandit.sarif, pipaudit.sarif) always exist (stubbed if tool fails)
  so they can be uploaded or inspected locally.

.PARAMETER Path
  Optional path (root of project). Defaults to script parent parent directory.

.EXAMPLE
  pwsh tools/security_scan.ps1

.EXAMPLE
  pwsh tools/security_scan.ps1 -Path .

#>
param(
    [string]$Path = (Resolve-Path (Join-Path $PSScriptRoot ".." )).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

Write-Host "[security-scan] Root: $Path"
Push-Location $Path

function Test-PythonModule {
    param([Parameter(Mandatory)][string]$Name)
    $testCode = "import importlib,sys; sys.exit(0 if importlib.util.find_spec('$Name') else 1)"
    $temp = New-TemporaryFile
    try {
        Set-Content -Path $temp -Value $testCode -Encoding utf8
        python $temp 2>$null
        return ($LASTEXITCODE -eq 0)
    }
    finally {
        Remove-Item $temp -ErrorAction Ignore
    }
}

function Install-PackageIfMissing {
    param([Parameter(Mandatory)][string]$Pkg, [string]$ModuleName)
    if (-not (Test-PythonModule -Name ($ModuleName ? $ModuleName : $Pkg))) {
        Write-Host "[security-scan] Installing $Pkg" -ForegroundColor Cyan
        pip install --quiet $Pkg | Out-Null
    }
}

Write-Host "[security-scan] Upgrading pip" -ForegroundColor Cyan
python -m pip install --upgrade pip > $null 2>&1

# Core tools
Install-PackageIfMissing -Pkg bandit -ModuleName bandit
Install-PackageIfMissing -Pkg pip-audit -ModuleName pip_audit
Install-PackageIfMissing -Pkg bandit-sarif-formatter -ModuleName bandit_sarif_formatter

# Bandit scan
$banditOut = Join-Path $Path 'bandit.sarif'
Write-Host "[security-scan] Running Bandit -> $banditOut" -ForegroundColor Cyan
if (bandit -r Aetherra -f sarif -o $banditOut) {
    Write-Host "[security-scan] Bandit SARIF generated" -ForegroundColor Green
}
else {
    Write-Warning "Bandit failed – writing stub SARIF"
    '{"version":"2.1.0","$schema":"https://json.schemastore.org/sarif-2.1.0","runs":[]}' | Set-Content $banditOut -Encoding utf8
}

# pip-audit
$pipAuditOut = Join-Path $Path 'pipaudit.sarif'
Write-Host "[security-scan] Running pip-audit -> $pipAuditOut" -ForegroundColor Cyan
if (Test-Path requirements.txt) {
    pip-audit -r requirements.txt --format sarif --output $pipAuditOut --progress-spinner off 2>$null
}
else {
    pip-audit --format sarif --output $pipAuditOut --progress-spinner off 2>$null
}
if (-not (Test-Path $pipAuditOut)) {
    Write-Warning "pip-audit failed – writing stub SARIF"
    '{"version":"2.1.0","$schema":"https://json.schemastore.org/sarif-2.1.0","runs":[]}' | Set-Content $pipAuditOut -Encoding utf8
}
else {
    Write-Host "[security-scan] pip-audit SARIF generated" -ForegroundColor Green
}

# Summary table
Get-Item $banditOut, $pipAuditOut | Select-Object Name, Length, LastWriteTime | Format-Table

Pop-Location
Write-Host "[security-scan] Complete" -ForegroundColor Green
