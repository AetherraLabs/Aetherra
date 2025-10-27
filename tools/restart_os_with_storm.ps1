# Restart Aetherra OS with STORM enabled
# This script stops the current OS and restarts it with STORM shadow mode

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  STORM-Enabled OS Restart Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "[OK] .env file found" -ForegroundColor Green

    # Verify STORM settings
    $stormEnabled = Select-String -Path ".env" -Pattern "AETHERRA_MEMORY_STORM=1" -Quiet
    $shadowMode = Select-String -Path ".env" -Pattern "AETHERRA_STORM_SHADOW_MODE=1" -Quiet

    if ($stormEnabled -and $shadowMode) {
        Write-Host "[OK] STORM configuration found in .env" -ForegroundColor Green
        Write-Host "     AETHERRA_MEMORY_STORM=1" -ForegroundColor Gray
        Write-Host "     AETHERRA_STORM_SHADOW_MODE=1" -ForegroundColor Gray
    }
    else {
        Write-Host "[WARN] STORM settings not found in .env" -ForegroundColor Yellow
        Write-Host "Expected:`n  AETHERRA_MEMORY_STORM=1`n  AETHERRA_STORM_SHADOW_MODE=1" -ForegroundColor Gray

        $continue = Read-Host "`nContinue anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "[ABORT] Restart cancelled" -ForegroundColor Red
            exit 1
        }
    }
}
else {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Create .env with STORM settings first:" -ForegroundColor Yellow
    Write-Host "  AETHERRA_MEMORY_STORM=1" -ForegroundColor Gray
    Write-Host "  AETHERRA_STORM_SHADOW_MODE=1" -ForegroundColor Gray
    exit 1
}

Write-Host "`n[INFO] Stopping any running OS instances..." -ForegroundColor Yellow
# Try to find and kill aetherra_os_launcher.py processes
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*aetherra_os_launcher*"
}

if ($processes) {
    Write-Host "[INFO] Found $($processes.Count) OS process(es)" -ForegroundColor Yellow
    $processes | ForEach-Object {
        Write-Host "  Stopping PID $($_.Id)..." -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "[OK] Previous OS stopped" -ForegroundColor Green
}
else {
    Write-Host "[INFO] No running OS instances found" -ForegroundColor Gray
}

Write-Host "`n[START] Launching Aetherra OS with STORM enabled..." -ForegroundColor Green
Write-Host "----------------------------------------`n" -ForegroundColor Cyan

# Start OS with verbose output
Write-Host "[CMD] python aetherra_os_launcher.py`n" -ForegroundColor Cyan

# Run OS in foreground
python aetherra_os_launcher.py

Write-Host "`n[EXIT] OS process ended" -ForegroundColor Yellow
