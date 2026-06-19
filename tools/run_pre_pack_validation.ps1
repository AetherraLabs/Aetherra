# Aetherra Pre-Pack Validation Quick Start
# PowerShell script to run comprehensive validation

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("dev", "test", "prod", "production")]
    [string]$Profile = "test",

    [Parameter(Mandatory = $false)]
    [switch]$Verbose,

    [Parameter(Mandatory = $false)]
    [switch]$SetProdFlags,

    [Parameter(Mandatory = $false)]
    [switch]$RunSmokeTests,

    [Parameter(Mandatory = $false)]
    [switch]$CheckEndpoints,

    [Parameter(Mandatory = $false)]
    [switch]$Full
)

Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host " Aetherra & Lyrixa Pre-Pack Validation Suite" -ForegroundColor Cyan
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ReportFile = Join-Path $ProjectRoot "pre_pack_validation_report.json"
$TrackingFile = Join-Path $ProjectRoot "docs\prepack\PRE_PACK_CHECKLIST_TRACKING.md"

# Helper Functions
function Write-Step {
    param([string]$Message)
    Write-Host "`nðŸ”¹ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  âœ… $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  âš ï¸  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "  âŒ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  â„¹ï¸  $Message" -ForegroundColor Gray
}

# Set Production Flags if requested
if ($SetProdFlags -or ($Profile -in @("prod", "production"))) {
    Write-Step "Setting Production Environment Flags"

    # Critical security flags
    $env:AETHERRA_PROFILE = "prod"
    $env:AETHERRA_SIGNING_STRICT = "1"
    $env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
    $env:AETHERRA_REQUIRE_STRICT = "1"
    $env:AETHERRA_REQUIRE_CAPABILITIES = "1"
    $env:AETHERRA_NET_STRICT = "1"

    # Network policy
    if (-not $env:AETHERRA_NETWORK_ALLOWLIST) {
        $env:AETHERRA_NETWORK_ALLOWLIST = "localhost,127.0.0.1,.aetherra.dev"
        Write-Warning "Set default network allowlist: $env:AETHERRA_NETWORK_ALLOWLIST"
    }

    # API security
    $env:AETHERRA_AI_API_REQUIRE_TOKEN = "1"
    if (-not $env:AETHERRA_AI_API_TOKEN) {
        Write-Error "AETHERRA_AI_API_TOKEN not set! This is REQUIRED for production."
    }

    # Disable experimental features
    $env:AETHERRA_HMR_ENABLED = "0"
    $env:AETHERRA_QFAC_MODE = "disabled"
    $env:AETHERRA_MEMORY_STORM = "0"
    $env:AETHERRA_TRAINER_ENABLED = "0"

    # Production settings
    $env:AETHERRA_QUIET = "1"

    Write-Success "Production flags set"
    Write-Info "Profile: $env:AETHERRA_PROFILE"
    Write-Info "Signing Strict: $env:AETHERRA_SIGNING_STRICT"
    Write-Info "Network Strict: $env:AETHERRA_NET_STRICT"
    Write-Info "HMR Enabled: $env:AETHERRA_HMR_ENABLED"
}

# Run Main Validation Suite
Write-Step "Running Automated Validation Suite"

$args = @(
    "tools\pre_pack_validation.py",
    "--profile", $Profile,
    "--output", $ReportFile
)

if ($Verbose) {
    $args += @("--verbose")
}

$result = & python $args
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Success "Validation suite completed successfully"
}
else {
    Write-Error "Validation suite failed with exit code: $exitCode"
}

# Check if report was generated
if (Test-Path $ReportFile) {
    Write-Success "Report generated: $ReportFile"

    # Parse and display summary
    try {
        $report = Get-Content $ReportFile | ConvertFrom-Json
        $summary = $report.summary

        Write-Host ""
        Write-Host "  Validation Summary:" -ForegroundColor Cyan
        Write-Host ("     Total Checks: {0}" -f $report.metadata.total_checks)
        Write-Host ("     Passed:       {0}" -f $summary.passed) -ForegroundColor Green
        Write-Host ("     Failed:       {0}" -f $summary.failed) -ForegroundColor Red
        Write-Host ("     Warnings:     {0}" -f $summary.warned) -ForegroundColor Yellow
        Write-Host ("     Skipped:      {0}" -f $summary.skipped) -ForegroundColor Gray
    }
    catch {
        Write-Warning "Could not parse report file"
    }
}
else {
    Write-Warning "Report file not found: $ReportFile"
}

# Run Smoke Tests if requested
if ($RunSmokeTests -or $Full) {
    Write-Step "Running Smoke Tests"

    $result = & pytest -q -o addopts= tests/smoke
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Smoke tests passed"
    }
    else {
        Write-Error "Smoke tests failed"
    }
}

# Check Endpoints if requested (requires running Hub)
if ($CheckEndpoints -or $Full) {
    Write-Step "Checking API Endpoints"

    $baseUrl = "http://localhost:3001"
    $endpoints = @(
        "/health",
        "/status",
        "/api/stats",
        "/api/kernel/status",
        "/api/memory/status"
    )

    foreach ($endpoint in $endpoints) {
        try {
            $url = "$baseUrl$endpoint"
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Success "$endpoint OK"
            }
            else {
                Write-Warning "$endpoint returned $($response.StatusCode)"
            }
        }
        catch {
            Write-Warning "$endpoint not accessible (Hub may not be running)"
        }
    }
}

# Additional Checks
Write-Step "Running Additional Checks"

# Check for unsigned .aether scripts
Write-Info "Verifying .aether scripts..."
$verifyResult = & python tools\verify_aether_scripts.py --root . --output aether_static_report.md 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success ".aether scripts verified"
}
else {
    Write-Error ".aether script verification failed"
}

# Check for LLM setup
if (Test-Path "tools\verify_llm_setup.py") {
    Write-Info "Verifying LLM setup..."
    $llmResult = & python tools\verify_llm_setup.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "LLM setup verified"
    }
    else {
        Write-Warning "LLM setup verification failed"
    }
}

# Final Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Validation Complete" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

if (Test-Path $ReportFile) {
    Write-Host ""
    Write-Host "[REPORT] Full report: $ReportFile" -ForegroundColor Gray
}

if (Test-Path $TrackingFile) {
    Write-Host "[TRACKING] Tracking document: $TrackingFile" -ForegroundColor Gray
}

Write-Host ""

# Critical Blockers Check
if ($Profile -in @("prod", "production")) {
    Write-Host "SECURITY: CRITICAL SECURITY CHECKLIST:" -ForegroundColor Yellow
    Write-Host ""

    $criticalChecks = @(
        @{Name = "AETHERRA_SIGNING_STRICT"; Required = "1"; Current = $env:AETHERRA_SIGNING_STRICT },
        @{Name = "AETHERRA_SCRIPT_VERIFY_STRICT"; Required = "1"; Current = $env:AETHERRA_SCRIPT_VERIFY_STRICT },
        @{Name = "AETHERRA_NET_STRICT"; Required = "1"; Current = $env:AETHERRA_NET_STRICT },
        @{Name = "AETHERRA_AI_API_REQUIRE_TOKEN"; Required = "1"; Current = $env:AETHERRA_AI_API_REQUIRE_TOKEN },
        @{Name = "AETHERRA_HMR_ENABLED"; Required = "0"; Current = $env:AETHERRA_HMR_ENABLED },
        @{Name = "AETHERRA_TRAINER_ENABLED"; Required = "0"; Current = $env:AETHERRA_TRAINER_ENABLED }
    )

    $allPass = $true
    foreach ($check in $criticalChecks) {
        $currentValue = $check.Current
        if ($check.Current -eq $check.Required) {
            Write-Host ("  OK: {0} = {1}" -f $check.Name, $currentValue) -ForegroundColor Green
        }
        else {
            Write-Host ("  FAIL: {0} = {1} (Expected: {2})" -f $check.Name, $currentValue, $check.Required) -ForegroundColor Red
            $allPass = $false
        }
    }

    Write-Host ""
    if ($allPass) {
        Write-Host "OK: ALL CRITICAL SECURITY FLAGS CONFIGURED" -ForegroundColor Green
        Write-Host "   Ready for production packaging" -ForegroundColor Green
    }
    else {
        Write-Host "FAIL: CRITICAL SECURITY FLAGS NOT PROPERLY SET" -ForegroundColor Red
        Write-Host "   DO NOT PACKAGE FOR PRODUCTION" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review the validation report: $ReportFile"
Write-Host "  2. Address any FAILED checks"
Write-Host "  3. Review WARNINGS for production deployment"
Write-Host "  4. Update tracking document: $TrackingFile"
Write-Host "  5. Run with -Full flag for complete validation"
Write-Host ""

# Return appropriate exit code
if ($exitCode -ne 0) {
    exit $exitCode
}

exit 0
