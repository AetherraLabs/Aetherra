# PowerShell CI helper for Lyrixa basic health
# Usage (PowerShell):  pwsh tools/ci_lyrixa_check.ps1
# Exits non-zero only if critical systems fail (diagnostics exit code 1)
# Allows degraded (exit 2) to pass but prints warning.

Write-Host "[Lyrixa CI] Running diagnostics (skip advanced)" -ForegroundColor Cyan
python tools/lyrixa_diagnostics.py --skip-advanced
$code = $LASTEXITCODE
if ($code -eq 0) {
    Write-Host "[Lyrixa CI] All critical systems PASS" -ForegroundColor Green
    exit 0
}
elseif ($code -eq 2) {
    Write-Host "[Lyrixa CI] Degraded: non-critical components failed (continuing)" -ForegroundColor Yellow
    exit 0
}
else {
    Write-Host "[Lyrixa CI] CRITICAL FAILURE" -ForegroundColor Red
    exit 1
}
