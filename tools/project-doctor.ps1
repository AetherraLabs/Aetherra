$ErrorActionPreference = "Stop"
$PY_DIRS = "Aetherra"
$FRONTEND_DIR = "frontend"

Write-Host "[doctor] Python: Ruff format & fix"
if (Get-Command ruff -ErrorAction SilentlyContinue) {
  ruff format .
  ruff check . --fix
} else {
  Write-Host "[doctor][warn] ruff not found; skipping format/lint"
}

Write-Host "[doctor] Python: MyPy (strict-ish)"
if (Get-Command mypy -ErrorAction SilentlyContinue) {
  mypy $PY_DIRS
} else {
  Write-Host "[doctor][warn] mypy not found; skipping type check"
}

Write-Host "[doctor] Python: Pyright (optional)"
if (Get-Command pyright -ErrorAction SilentlyContinue) {
  pyright; if ($LASTEXITCODE -ne 0) { Write-Host "[doctor][info] pyright reported issues" }
} else {
  Write-Host "[doctor][info] pyright not installed; VS Code extension can provide feedback"
}

Write-Host "[doctor] Python: PyTest (quick)"
if (Get-Command pytest -ErrorAction SilentlyContinue) {
  pytest -q --maxfail=1 --disable-warnings
} else {
  Write-Host "[doctor][warn] pytest not found; skipping tests"
}

Write-Host "[doctor] Security: Gitleaks scan"
if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
  gitleaks detect --no-banner --redact --report-path tools/gitleaks_report.json; if ($LASTEXITCODE -ne 0) { Write-Host "[doctor] gitleaks found issues (report saved)" }
} else {
  Write-Host "[doctor][warn] gitleaks not found; install 'gitleaks' (native) or 'gitleaks-bin' via pip"
}

if (Test-Path "$FRONTEND_DIR/package.json") {
  Write-Host "[doctor] Frontend: lint & format"
  if (Get-Command npm -ErrorAction SilentlyContinue) {
    Push-Location $FRONTEND_DIR
    npm run lint --silent; npm run format --silent; npm run typecheck --silent
    Pop-Location
  } else {
    Write-Host "[doctor][warn] npm not found; skipping frontend checks"
  }
}

Write-Host "[doctor] Done ✓"
