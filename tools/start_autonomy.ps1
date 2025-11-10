#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Aetherra OS Autonomy Quick-Start Script

.DESCRIPTION
    Automated bring-up sequence for Aetherra OS autonomy mode.
    Follows the MAB (Minimum Autonomy Baseline) framework.

    Stages:
    1. Hub + Security
    2. Memory (QFAC + STORM shadow)
    3. Maintenance System (Homeostasis + Self-Improvement + Self-Incorporation)
    4. Agent Orchestrator
    5. Consciousness Loop (Suggest mode)
    6. Coding Autopilot (Test-gated)

.PARAMETER Profile
    Environment profile: 'staging' or 'production'

.PARAMETER SkipTokenCheck
    Skip token validation (for testing only)

.PARAMETER QuickHealth
    Run quick health check only, don't start services

.EXAMPLE
    .\start_autonomy.ps1 -Profile staging

.EXAMPLE
    .\start_autonomy.ps1 -Profile production -QuickHealth
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('staging', 'production')]
    [string]$Profile = 'staging',

    [Parameter(Mandatory = $false)]
    [switch]$SkipTokenCheck,

    [Parameter(Mandatory = $false)]
    [switch]$QuickHealth
    ,
    [Parameter(Mandatory = $false)]
    [switch]$StartRegistry,

    [Parameter(Mandatory = $false)]
    [switch]$StartGUI,

    [Parameter(Mandatory = $false)]
    [switch]$StartOS
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Colors for output
$ColorBrand = "Green"
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

function Write-Banner {
    Write-Host ""
    Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor $ColorBrand
    Write-Host "    AETHERRA OS - AUTONOMY ACTIVATION" -ForegroundColor $ColorBrand
    Write-Host "    Profile: $Profile | Mode: $(if($QuickHealth){'Health Check'}else{'Full Bring-Up'})" -ForegroundColor $ColorBrand
    Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor $ColorBrand
    Write-Host ""
}

function Write-StepHeader {
    param([string]$Step, [string]$Description)
    Write-Host ""
    Write-Host "> $Step - $Description" -ForegroundColor $ColorInfo
    Write-Host ("-" * 60)
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor $ColorSuccess
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  [WARNING] $Message" -ForegroundColor $ColorWarning
}

function Write-Failure {
    param([string]$Message)
    Write-Host "  [ERROR] $Message" -ForegroundColor $ColorError
}

function Test-Prerequisites {
    Write-StepHeader "PRE-FLIGHT" "Checking prerequisites"

    $allGood = $true

    # Python version
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.(\d+)") {
            $minor = [int]$matches[1]
            if ($minor -ge 11) {
                Write-Success "Python $pythonVersion"
            }
            else {
                Write-Failure "Python 3.11+ required, found $pythonVersion"
                $allGood = $false
            }
        }
    }
    catch {
        Write-Failure "Python not found or not in PATH"
        $allGood = $false
    }

    # Config files
    $configFile = "config.autonomy.$Profile.json"
    if (Test-Path $configFile) {
        Write-Success "Config file found: $configFile"
    }
    else {
        Write-Failure "Config file missing: $configFile"
        $allGood = $false
    }

    # Env file
    $envFile = ".env.autonomy.$Profile"
    if (Test-Path $envFile) {
        Write-Success "Environment file found: $envFile"
    }
    else {
        Write-Warning "Environment file not found: $envFile"
        Write-Host "    Copy from .env.autonomy.$Profile.template and configure tokens" -ForegroundColor $ColorInfo
    }

    # Virtual environment
    if (Test-Path ".venv/Scripts/Activate.ps1") {
        Write-Success "Virtual environment found"
    }
    else {
        Write-Warning "Virtual environment not found at .venv"
    }

    # Disk space
    $drive = (Get-Location).Drive
    $freeSpace = (Get-PSDrive $drive.Name).Free / 1GB
    if ($freeSpace -gt 10) {
        Write-Success "Disk space: $([math]::Round($freeSpace, 2)) GB free"
    }
    else {
        Write-Warning "Low disk space: $([math]::Round($freeSpace, 2)) GB free (recommend 10GB+)"
    }

    return $allGood
}

function Set-AutonomyEnvironment {
    Write-StepHeader "ENVIRONMENT" "Loading configuration"

    # Set profile
    $env:AETHERRA_PROFILE = $Profile
    $env:AETHERRA_CONFIG_PATH = "config.autonomy.$Profile.json"
    Write-Success "Profile: $Profile"

    # Load env file
    $envFile = ".env.autonomy.$Profile"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
        Write-Success "Environment variables loaded from $envFile"
    }
    else {
        Write-Warning "No environment file found, using defaults"
    }

    # Defaults and key settings
    if (-not $env:AETHERRA_HUB_PORT -or $env:AETHERRA_HUB_PORT -eq "") { $env:AETHERRA_HUB_PORT = "3001" }
    if (-not $env:AETHERRA_REGISTRY_URL -or $env:AETHERRA_REGISTRY_URL -eq "") { $env:AETHERRA_REGISTRY_URL = "http://127.0.0.1:3030" }
    if (-not $env:AETH_LOG_REQUESTS -or $env:AETH_LOG_REQUESTS -eq "") { $env:AETH_LOG_REQUESTS = "0" }
    Write-Host ""
    Write-Host "  Configuration:" -ForegroundColor $ColorInfo
    Write-Host "    Autonomy Mode: $env:AETHERRA_AUTONOMY_MODE"
    Write-Host "    Safety Envelope: $env:AETHERRA_SAFETY_ENVELOPE_ENABLED"
    Write-Host "    QFAC Enabled: $env:AETHERRA_ENABLE_QFAC"
    Write-Host "    Hub Port: $env:AETHERRA_HUB_PORT"
    Write-Host "    Registry: $env:AETHERRA_REGISTRY_URL"
    Write-Host "    Request Logs: $env:AETH_LOG_REQUESTS"
}

function Test-TokenConfiguration {
    Write-StepHeader "SECURITY" "Validating tokens"

    if ($SkipTokenCheck) {
        Write-Warning "Token validation skipped (not recommended)"
        return $true
    }

    $allGood = $true

    # Token checks respect dev toggles: skip failure if require_token=0
    $aiRequire = ($env:AETHERRA_AI_API_REQUIRE_TOKEN -eq "1")
    $agentsRequire = ($env:AETHERRA_AGENTS_API_REQUIRE_TOKEN -eq "1")

    # Check Hub token (only if required)
    if ($aiRequire) {
        if ($env:AETHERRA_AI_API_TOKEN -and $env:AETHERRA_AI_API_TOKEN -ne "<GENERATE_STAGING_TOKEN>" -and $env:AETHERRA_AI_API_TOKEN -ne "<GENERATE_PRODUCTION_TOKEN_256BIT>") {
            Write-Success "Hub API token configured"
        }
        else {
            Write-Failure "Hub API token not configured (AETHERRA_AI_API_REQUIRE_TOKEN=1)"
            Write-Host "    Generate: python -c 'import secrets; print(secrets.token_urlsafe(32))'" -ForegroundColor $ColorInfo
            $allGood = $false
        }
    }
    else {
        if ($env:AETHERRA_AI_API_TOKEN) { Write-Success "Hub API token present (not required in dev)" } else { Write-Warning "Hub API token not required (dev)" }
    }

    # Check Agents token (only if required)
    if ($agentsRequire) {
        if ($env:AETHERRA_AGENTS_API_TOKEN -and $env:AETHERRA_AGENTS_API_TOKEN -ne "<GENERATE_STAGING_TOKEN>" -and $env:AETHERRA_AGENTS_API_TOKEN -ne "<GENERATE_PRODUCTION_TOKEN_256BIT>") {
            Write-Success "Agents API token configured"
        }
        else {
            Write-Failure "Agents API token not configured (AETHERRA_AGENTS_API_REQUIRE_TOKEN=1)"
            Write-Host "    Generate: python -c 'import secrets; print(secrets.token_urlsafe(32))'" -ForegroundColor $ColorInfo
            $allGood = $false
        }
    }
    else {
        if ($env:AETHERRA_AGENTS_API_TOKEN) { Write-Success "Agents token present (not required in dev)" } else { Write-Warning "Agents API token not required (dev)" }
    }

    return $allGood
}

function Start-RegistryDaemon {
    Write-StepHeader "PHASE 0" "Starting Registry Daemon"

    $uri = "http://127.0.0.1:3030/api/registry/status"
    # Quick health-only path
    if ($QuickHealth) {
        try {
            $r = Invoke-WebRequest -Uri $uri -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($r.StatusCode -eq 200) { Write-Success "Registry is running"; return $true }
        }
        catch {}
        Write-Warning "Registry not responding"
        return $false
    }

    # If already running, skip
    try {
        $r = Invoke-WebRequest -Uri $uri -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { Write-Success "Registry already running"; return $true }
    }
    catch {}

    Write-Host "  Starting Registry on 127.0.0.1:3030..." -ForegroundColor $ColorInfo
    $cmd = "python aetherra_registry_daemon.py --host 127.0.0.1 --port 3030"
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $cmd | Out-Null

    # Wait for readiness
    $maxRetries = 15
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $r = Invoke-WebRequest -Uri $uri -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($r.StatusCode -eq 200) { Write-Success "Registry is healthy"; return $true }
        }
        catch {}
        Start-Sleep -Seconds 1
    }
    Write-Failure "Registry failed to start"
    return $false
}

function Start-HubService {
    Write-StepHeader "PHASE 1" "Starting Hub API + Security"

    if ($QuickHealth) {
        # Just check if it's already running
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($env:AETHERRA_HUB_PORT)/metrics" -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "Hub is already running on port $($env:AETHERRA_HUB_PORT)"
                return $true
            }
        }
        catch {
            Write-Warning "Hub not responding on port $($env:AETHERRA_HUB_PORT)"
            return $false
        }
    }

    Write-Host "  Starting Hub on port $($env:AETHERRA_HUB_PORT)..." -ForegroundColor $ColorInfo
    Write-Host "  (This will open in a new terminal window)" -ForegroundColor $ColorInfo

    # Start Hub in new window
    $hubCommand = "python tools/run_hub_ai_api.py --port $($env:AETHERRA_HUB_PORT)"
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $hubCommand

    # Wait for Hub to start
    Write-Host "  Waiting for Hub to initialize..." -ForegroundColor $ColorInfo
    Start-Sleep -Seconds 5

    # Health check
    $maxRetries = 10
    $retryCount = 0
    while ($retryCount -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($env:AETHERRA_HUB_PORT)/metrics" -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                Write-Success "Hub is healthy and responding"
                return $true
            }
        }
        catch {
            $retryCount++
            Write-Host "  Retry $retryCount/$maxRetries..." -ForegroundColor $ColorInfo
            Start-Sleep -Seconds 2
        }
    }

    Write-Failure "Hub failed to start or is not responding"
    return $false
}

function Start-Frontend {
    Write-StepHeader "PHASE 1b" "Starting Lyrixa Frontend (dev)"
    # Try known launcher; fail gracefully
    $scriptPath = Join-Path $PSScriptRoot "start_lyrixa_dev.ps1"
    if (Test-Path $scriptPath) {
        try {
            Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-File", $scriptPath, "-FrontendOnly" | Out-Null
            Write-Success "Frontend launch initiated"
            return $true
        }
        catch {
            Write-Warning "Frontend launch failed: $($_.Exception.Message)"
            return $false
        }
    }
    else {
        Write-Warning "Frontend launcher not found (tools/start_lyrixa_dev.ps1)"
        return $false
    }
}

function Start-OSLauncher {
    Write-StepHeader "PHASE 1c" "Starting OS Launcher"
    try {
        $cmd = "python -u aetherra_os_launcher.py --mode full -v"
        Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $cmd | Out-Null
        Write-Success "OS launch initiated"
        return $true
    }
    catch {
        Write-Warning "OS launch failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-MemorySystem {
    Write-StepHeader "PHASE 2" "Memory System (QFAC + STORM Shadow)"

    # Check memory status via Hub API
    try {
        $useHeaders = $false
        $headers = @{}
        if ($env:AETHERRA_AI_API_REQUIRE_TOKEN -eq "1" -and $env:AETHERRA_AI_API_TOKEN) {
            $headers = @{ "Authorization" = "Bearer $env:AETHERRA_AI_API_TOKEN" }
            $useHeaders = $true
        }
        $url = "http://localhost:$($env:AETHERRA_HUB_PORT)/api/memory/status"
        $response = if ($useHeaders) { Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 5 } else { Invoke-RestMethod -Uri $url -TimeoutSec 5 }

        if ($response.engine) { Write-Success "Memory engine: $($response.engine)" }
        if ($response.qfac_enabled -ne $null) { Write-Success "QFAC enabled: $($response.qfac_enabled)" }
        if ($response.shadow_mode -ne $null) { Write-Success "STORM shadow_mode: $($response.shadow_mode)" }

        if ($response.shadow_mode -eq $true) { Write-Success "STORM running in safe shadow mode" }

        return $true
    }
    catch {
        Write-Warning "Memory status unavailable: $($_.Exception.Message)"
        Write-Host "    This is OK if memory service hasn't been initialized yet" -ForegroundColor $ColorInfo
        return $false
    }
}

function Test-MaintenanceSystem {
    Write-StepHeader "PHASE 3" "Maintenance System (Homeostasis + Self-Improvement)"

    # Check homeostasis status
    try {
        $useHeaders = $false
        $headers = @{}
        if ($env:AETHERRA_AI_API_REQUIRE_TOKEN -eq "1" -and $env:AETHERRA_AI_API_TOKEN) {
            $headers = @{ "Authorization" = "Bearer $env:AETHERRA_AI_API_TOKEN" }
            $useHeaders = $true
        }
        $url = "http://localhost:$($env:AETHERRA_HUB_PORT)/api/homeostasis/status"
        $response = if ($useHeaders) { Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 5 } else { Invoke-RestMethod -Uri $url -TimeoutSec 5 }

        Write-Success "Homeostasis status: $($response.status)"
        Write-Success "Controller mode: $($response.controller.mode)"
        Write-Success "Emergency stop: $($response.controller.emergency_stop)"

        if ($response.controller.emergency_stop -eq $true) {
            Write-Warning "Emergency stop is active - reset if this is unexpected"
        }

        return $true
    }
    catch {
        Write-Warning "Homeostasis status unavailable: $($_.Exception.Message)"
        return $false
    }
}

function Test-AgentOrchestrator {
    Write-StepHeader "PHASE 4" "Agent Orchestrator"

    try {
        $useHeaders = $false
        $headers = @{}
        if ($env:AETHERRA_AGENTS_API_REQUIRE_TOKEN -eq "1" -and $env:AETHERRA_AGENTS_API_TOKEN) {
            $headers = @{ "X-Aetherra-Token" = $env:AETHERRA_AGENTS_API_TOKEN }
            $useHeaders = $true
        }
        $url = "http://localhost:$($env:AETHERRA_HUB_PORT)/api/agents"
        $response = if ($useHeaders) { Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 5 } else { Invoke-RestMethod -Uri $url -TimeoutSec 5 }

        Write-Success "Total agents: $($response.orchestrator.total_agents)"
        Write-Success "Pending tasks: $($response.orchestrator.pending_tasks)"
        Write-Success "Tick Hz: $($response.orchestrator.tick_hz)"

        if ($response.orchestrator.total_agents -gt 0) {
            Write-Success "Agent orchestrator is operational"
        }
        else {
            Write-Warning "No agents registered yet"
        }

        return $true
    }
    catch {
        Write-Warning "Agent orchestrator unavailable: $($_.Exception.Message)"
        return $false
    }
}

function Test-ConsciousnessLoop {
    Write-StepHeader "PHASE 5" "Consciousness Loop"

    try {
        $useHeaders = $false
        $headers = @{}
        if ($env:AETHERRA_AI_API_REQUIRE_TOKEN -eq "1" -and $env:AETHERRA_AI_API_TOKEN) {
            $headers = @{ "Authorization" = "Bearer $env:AETHERRA_AI_API_TOKEN" }
            $useHeaders = $true
        }
        $url = "http://localhost:$($env:AETHERRA_HUB_PORT)/api/consciousness/status"
        $response = if ($useHeaders) { Invoke-RestMethod -Uri $url -Headers $headers -TimeoutSec 5 -ErrorAction SilentlyContinue } else { Invoke-RestMethod -Uri $url -TimeoutSec 5 -ErrorAction SilentlyContinue }

        Write-Success "Consciousness mode: $($response.mode)"
        Write-Success "Safety envelope: $($response.safety_envelope_enabled)"
        Write-Success "QFAC enabled: $($response.qfac_enabled)"

        if ($response.mode -eq "suggest") {
            Write-Success "Operating in SAFE suggest mode (no auto-execution)"
        }
        elseif ($response.mode -eq "auto") {
            Write-Warning "Operating in AUTO mode - ensure metrics are green!"
        }

        return $true
    }
    catch {
        Write-Warning "Consciousness status unavailable (may not be implemented yet)"
        return $false
    }
}

function Test-InteractiveLyrixa {
    Write-StepHeader "BONUS" "Interactive Lyrixa Emotion System"

    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$($env:AETHERRA_HUB_PORT)/api/interactive/status" -TimeoutSec 5

        Write-Success "Interactive system running: $($response.system_status.running)"
        Write-Success "Current emotion: $($response.current_emotion)"
        Write-Success "Current expression: $($response.current_expression)"

        return $true
    }
    catch {
        Write-Warning "Interactive Lyrixa unavailable (optional feature)"
        return $false
    }
}

function Show-QuickStart {
    Write-Host ""
    Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor $ColorBrand
    Write-Host "  NEXT STEPS" -ForegroundColor $ColorBrand
    Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor $ColorBrand
    Write-Host ""
    Write-Host "1. Open Dashboard:" -ForegroundColor $ColorInfo
    Write-Host "   http://localhost:$($env:AETHERRA_HUB_PORT)" -ForegroundColor White
    Write-Host ""
    Write-Host "2. View Metrics:" -ForegroundColor $ColorInfo
    Write-Host "   http://localhost:$($env:AETHERRA_HUB_PORT)/metrics" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Monitor Logs:" -ForegroundColor $ColorInfo
    Write-Host "   Get-Content logs/aetherra.log -Wait -Tail 50" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Emergency Stop:" -ForegroundColor $ColorInfo
    Write-Host "   curl -X POST http://localhost:$($env:AETHERRA_HUB_PORT)/api/homeostasis/emergency_stop \" -ForegroundColor White
    Write-Host "     -H 'Authorization: Bearer <TOKEN>'" -ForegroundColor White
    Write-Host ""
    Write-Host "5. Full Documentation:" -ForegroundColor $ColorInfo
    Write-Host "   docs/AUTONOMY_ACTIVATION_RUNBOOK.md" -ForegroundColor White
    Write-Host ""
}

function Show-Summary {
    param([hashtable]$Results)

    Write-Host ""
    Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor $ColorBrand
    Write-Host "  AUTONOMY STATUS SUMMARY" -ForegroundColor $ColorBrand
    Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor $ColorBrand
    Write-Host ""

    $Results.GetEnumerator() | Sort-Object Name | ForEach-Object {
        $status = if ($_.Value) { "[OK]" } else { "[FAIL]" }
        $color = if ($_.Value) { $ColorSuccess } else { $ColorWarning }
        Write-Host "  $status $($_.Key)" -ForegroundColor $color
    }

    Write-Host ""

    $healthyCount = ($Results.Values | Where-Object { $_ -eq $true }).Count
    $totalCount = $Results.Count
    $healthPercent = [math]::Round(($healthyCount / $totalCount) * 100, 1)

    $healthColor = if ($healthPercent -ge 80) { $ColorSuccess } elseif ($healthPercent -ge 60) { $ColorWarning } else { $ColorError }
    Write-Host "  Overall Health: $healthyCount/$totalCount ($healthPercent%)" -ForegroundColor $healthColor

    if ($healthPercent -ge 90) {
        Write-Host ""
        Write-Host "  SUCCESS: System is ready for autonomy!" -ForegroundColor $ColorSuccess
    }
    elseif ($healthPercent -ge 70) {
        Write-Host ""
        Write-Host "  WARNING: System is partially ready - review warnings above" -ForegroundColor $ColorWarning
    }
    else {
        Write-Host ""
        Write-Host "  ERROR: System needs attention before enabling autonomy" -ForegroundColor $ColorError
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    Write-Banner

    # Pre-flight checks
    $prereqsOk = Test-Prerequisites
    if (-not $prereqsOk) {
        Write-Host ""
        Write-Failure "Prerequisites check failed. Please fix the issues above and try again."
        exit 1
    }

    # Load environment
    Set-AutonomyEnvironment

    # Validate tokens
    $tokensOk = Test-TokenConfiguration
    if (-not $tokensOk -and -not $SkipTokenCheck) {
        Write-Host ""
        Write-Failure "Token validation failed. Generate tokens and update .env file."
        exit 1
    }

    # Results tracker
    $results = @{}

    # Start or check services
    $regOk = $false
    if ($StartRegistry -or -not $QuickHealth) { $regOk = Start-RegistryDaemon } else { $regOk = Start-RegistryDaemon }
    $results["Registry Daemon"] = $regOk

    $results["Hub API"] = Start-HubService

    if ($StartGUI) {
        $results["Frontend (dev)"] = Start-Frontend
    }
    if ($StartOS) {
        $results["OS Launcher"] = Start-OSLauncher
    }

    if ($results["Hub API"]) {
        $results["Memory System"] = Test-MemorySystem
        $results["Maintenance System"] = Test-MaintenanceSystem
        $results["Agent Orchestrator"] = Test-AgentOrchestrator
        $results["Consciousness Loop"] = Test-ConsciousnessLoop
        $results["Interactive Lyrixa"] = Test-InteractiveLyrixa
    }

    # Show summary
    Show-Summary -Results $results

    if (-not $QuickHealth) {
        Show-QuickStart
    }

    Write-Host ""
    Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor $ColorBrand
    Write-Host ""

    # Exit code based on health
    $healthPercent = [math]::Round((($results.Values | Where-Object { $_ -eq $true }).Count / $results.Count) * 100, 1)
    if ($healthPercent -ge 70) {
        exit 0
    }
    else {
        exit 1
    }

}
catch {
    Write-Host ""
    Write-Failure "Fatal error: $($_.Exception.Message)"
    Write-Host $_.ScriptStackTrace -ForegroundColor $ColorError
    exit 1
}

