# Quick Fix Script for Pre-Pack Validation
# Applies the final 3 environment variable fixes

Write-Host "`n" -NoNewline
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " Aetherra Pre-Pack: Quick Fix Application" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Disable QFAC experimental mode
Write-Host "[FIX 1/3] Disabling QFAC experimental mode..." -ForegroundColor Yellow
$env:AETHERRA_QFAC_MODE = "disabled"
Write-Host "   [OK] AETHERRA_QFAC_MODE = disabled" -ForegroundColor Green

# 2. Disable STORM experimental mode
Write-Host "`n[FIX 2/3] Disabling STORM experimental mode..." -ForegroundColor Yellow
$env:AETHERRA_MEMORY_STORM = "0"
Write-Host "   [OK] AETHERRA_MEMORY_STORM = 0" -ForegroundColor Green

# 3. Generate and set master key for secrets encryption
Write-Host "`n[FIX 3/3] Generating master key for secrets encryption..." -ForegroundColor Yellow
$masterKeyBytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Fill($masterKeyBytes)
$masterKey = [System.Convert]::ToBase64String($masterKeyBytes)
$env:AETHERRA_KEYS_MASTER = $masterKey
Write-Host "   [OK] AETHERRA_KEYS_MASTER = [generated]" -ForegroundColor Green

# Save master key to secure file
$keyFile = Join-Path $PSScriptRoot ".." ".aetherra" "master_key_backup.txt"
$keyDir = Split-Path $keyFile -Parent
if (!(Test-Path $keyDir)) {
    New-Item -ItemType Directory -Path $keyDir -Force | Out-Null
}
$masterKey | Out-File -FilePath $keyFile -Encoding UTF8
Write-Host "   [SAVED] Master key backed up to: .aetherra/master_key_backup.txt" -ForegroundColor Gray
Write-Host "   [WARNING] KEEP THIS FILE SECURE!" -ForegroundColor Yellow

# Display final status
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " All Fixes Applied Successfully!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[STATUS] Current Production Configuration:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Environment Profile:" -ForegroundColor White
Write-Host "    AETHERRA_PROFILE = $env:AETHERRA_PROFILE" -ForegroundColor Gray
Write-Host ""
Write-Host "  Security Flags:" -ForegroundColor White
Write-Host "    AETHERRA_SIGNING_STRICT = $env:AETHERRA_SIGNING_STRICT" -ForegroundColor Gray
Write-Host "    AETHERRA_NET_STRICT = $env:AETHERRA_NET_STRICT" -ForegroundColor Gray
Write-Host "    AETHERRA_AI_API_REQUIRE_TOKEN = $env:AETHERRA_AI_API_REQUIRE_TOKEN" -ForegroundColor Gray
Write-Host ""
Write-Host "  Feature Flags:" -ForegroundColor White
Write-Host "    AETHERRA_HMR_ENABLED = $env:AETHERRA_HMR_ENABLED" -ForegroundColor Gray
Write-Host "    AETHERRA_TRAINER_ENABLED = $env:AETHERRA_TRAINER_ENABLED" -ForegroundColor Gray
Write-Host "    AETHERRA_QFAC_MODE = $env:AETHERRA_QFAC_MODE" -ForegroundColor Gray
Write-Host "    AETHERRA_MEMORY_STORM = $env:AETHERRA_MEMORY_STORM" -ForegroundColor Gray
Write-Host ""
Write-Host "  Secrets:" -ForegroundColor White
Write-Host "    AETHERRA_KEYS_MASTER = <set>" -ForegroundColor Gray
Write-Host ""

Write-Host "[OK] Ready for next validation step!" -ForegroundColor Green
Write-Host ""
Write-Host "[NEXT] Run capability tests and verify .aether signatures" -ForegroundColor Cyan
Write-Host "Command: pytest -q -o addopts= tests/capabilities" -ForegroundColor Gray
Write-Host ""
