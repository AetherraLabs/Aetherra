# Start Hub with STORM metrics export
# Run this in a separate terminal after starting the OS

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  STORM-Enabled Hub Launcher" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "[OK] .env file found" -ForegroundColor Green
}
else {
    Write-Host "[WARN] .env file not found - using defaults" -ForegroundColor Yellow
}

Write-Host "`n[INFO] Starting Hub on port 3001..." -ForegroundColor Green
Write-Host "----------------------------------------`n" -ForegroundColor Cyan

Write-Host "[CMD] python tools/run_hub_ai_api.py --port 3001`n" -ForegroundColor Cyan
Write-Host "Hub Features:" -ForegroundColor Yellow
Write-Host "  - AI API endpoints" -ForegroundColor Gray
Write-Host "  - STORM status: http://localhost:3001/api/memory/status" -ForegroundColor Gray
Write-Host "  - Prometheus metrics: http://localhost:3001/metrics" -ForegroundColor Gray
Write-Host "  - Auto-registers with OS service registry" -ForegroundColor Gray
Write-Host ""

# Run Hub in foreground
python tools/run_hub_ai_api.py --port 3001

Write-Host "`n[EXIT] Hub process ended" -ForegroundColor Yellow
