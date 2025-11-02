# Aetherra OS - Windows Launch Helper
# Opens the Aetherra OS executable and automatically opens the web interface

param(
    [string]$Mode = "full",
    [switch]$Verbose,
    [switch]$NoBrowser
)

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Aetherra AI Operating System - Windows Launcher" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if executable exists
$exePath = ".\AetherraOS.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "[ERROR] AetherraOS.exe not found in current directory" -ForegroundColor Red
    Write-Host "Please run this script from the AetherraOS-1.0.0-beta.1-Windows-x64 directory" -ForegroundColor Yellow
    exit 1
}

# Build command arguments
$args = @("--mode", $Mode, "--gui")
if ($Verbose) {
    $args += "--verbose"
}

Write-Host "[1/3] Starting Aetherra OS..." -ForegroundColor Yellow
Write-Host "  Mode: $Mode" -ForegroundColor Cyan
Write-Host "  Command: $exePath $($args -join ' ')" -ForegroundColor Gray
Write-Host ""

# Start the executable in a new window
$processArgs = @{
    FilePath     = $exePath
    ArgumentList = $args
    PassThru     = $true
    NoNewWindow  = $false
}

try {
    $process = Start-Process @processArgs

    Write-Host "[2/3] Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Check if process is still running
    if ($process.HasExited) {
        Write-Host "[ERROR] Aetherra OS exited unexpectedly" -ForegroundColor Red
        Write-Host "Exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor Yellow
        Write-Host "  1. Check aetherra_os.log for errors" -ForegroundColor Gray
        Write-Host "  2. Try running with --verbose flag: .\$($MyInvocation.MyCommand.Name) -Verbose" -ForegroundColor Gray
        Write-Host "  3. Ensure all files in _internal\ are present" -ForegroundColor Gray
        exit 1
    }

    Write-Host "  [OK] Aetherra OS is running (PID: $($process.Id))" -ForegroundColor Green
    Write-Host ""

    # Open browser if not disabled
    if (-not $NoBrowser) {
        Write-Host "[3/3] Opening web interface..." -ForegroundColor Yellow

        $lyrixaUrl = "http://localhost:3001"  # Hub serves Lyrixa UI at root

        Write-Host "  Lyrixa UI & API: $lyrixaUrl" -ForegroundColor Cyan
        Write-Host ""

        # Wait a bit more for Hub to start
        Start-Sleep -Seconds 3

        # Open Lyrixa UI (served by Hub at root)
        try {
            Start-Process $lyrixaUrl
            Write-Host "  [OK] Opened Lyrixa UI in browser" -ForegroundColor Green
        }
        catch {
            Write-Host "  [WARN] Could not open browser automatically" -ForegroundColor Yellow
            Write-Host "  Please open $lyrixaUrl manually" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "[3/3] Skipping browser launch (--NoBrowser specified)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Access the system at:" -ForegroundColor Cyan
        Write-Host "  Lyrixa UI: http://localhost:3001" -ForegroundColor Gray
        Write-Host "  API Endpoints: http://localhost:3001/api/*" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "====================================================" -ForegroundColor Green
    Write-Host " Aetherra OS is ONLINE!" -ForegroundColor Green
    Write-Host "====================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The system is running in the background." -ForegroundColor Cyan
    Write-Host "To stop: Close the Aetherra OS window or use Task Manager" -ForegroundColor Gray
    Write-Host ""

}
catch {
    Write-Host "[ERROR] Failed to start Aetherra OS: $_" -ForegroundColor Red
    exit 1
}
