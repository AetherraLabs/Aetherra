$ErrorActionPreference = "Stop"
$GLOBAL_LAST_ERROR = 0
$PY_DIRS = "Aetherra"
$FRONTEND_DIR = "frontend"

# Modes: --check, --fix (default), --guarded-fix; optional --security-deep
$MODE = "fix"
$SECURITY_DEEP = $false
foreach ($arg in $args) {
  switch ($arg) {
    "--check" { $MODE = "check" }
    "--fix" { $MODE = "fix" }
    "--guarded-fix" { $MODE = "guarded-fix" }
    "--security-deep" { $SECURITY_DEEP = $true }
  }
}

Write-Host "[doctor] Mode: $MODE"

function Run-RuffCheck {
  if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] Ruff format --check"
    ruff format --check . | Out-Host
    Write-Host "[doctor] Ruff check"
    ruff check . | Out-Host
  } else { Write-Host "[doctor][warn] ruff not found; skipping format/lint" }
}

function Run-RuffFix {
  if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] Ruff format & fix"
    ruff format .
    ruff check . --fix
  } else { Write-Host "[doctor][warn] ruff not found; skipping format/lint" }
}

function Run-TypesAndTests {
  Write-Host "[doctor] MyPy (strict-ish)"
  if (Get-Command mypy -ErrorAction SilentlyContinue) { mypy $PY_DIRS | Out-Host } else { Write-Host "[doctor][warn] mypy not found; skipping" }

  Write-Host "[doctor] Pyright (optional)"
  if (Get-Command pyright -ErrorAction SilentlyContinue) { pyright | Out-Host } else { Write-Host "[doctor][info] pyright not installed" }

  # Prefer fast, reliable checks over full suite during local doctor runs
  # 1) Headless OS smoke
  Write-Host "[doctor] Smoke: tools/os_smoke.py"
  if (Get-Command python -ErrorAction SilentlyContinue) {
    python tools/os_smoke.py
    if ($LASTEXITCODE -ne 0) {
      Write-Host "[doctor][error] Smoke test failed"
      $script:GLOBAL_LAST_ERROR = $LASTEXITCODE
    }
  } else { Write-Host "[doctor][warn] python not found; skipping smoke" }

  # 2) Capabilities slice (faster than full test run)
  if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] PyTest (capabilities slice)"
    python -m pytest -q -o addopts= tests/capabilities
    if ($LASTEXITCODE -ne 0) {
      Write-Host "[doctor][error] Capabilities tests failed"
      $script:GLOBAL_LAST_ERROR = $LASTEXITCODE
    }
  } else {
    Write-Host "[doctor][warn] python not found; skipping tests"
  }
}

function Get-GitleaksExe {
  # Try PATH first
  $cmd = Get-Command gitleaks -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  # Try venv Scripts if active
  if ($env:VIRTUAL_ENV) {
    $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\gitleaks.exe"
    if (Test-Path $candidate) { return $candidate }
  }
  # Try local .venv Scripts
  $here = Resolve-Path "."
  $localCandidate = Join-Path $here ".venv\Scripts\gitleaks.exe"
  if (Test-Path $localCandidate) { return $localCandidate }
  return $null
}

function Run-SecretsScan {
  Write-Host "[doctor] Gitleaks scan"
  $gitleaksExe = Get-GitleaksExe
  if ($gitleaksExe) {
    & $gitleaksExe detect --no-banner --redact --report-path tools/gitleaks_report.json
    if ($LASTEXITCODE -ne 0) { Write-Host "[doctor] gitleaks found issues (report saved)" }
  } else {
    Write-Host "[doctor][warn] gitleaks not found; install via Chocolatey (choco install gitleaks) or Scoop (scoop install gitleaks)"
  }
}

function Run-SecurityDeep {
  if ($SECURITY_DEEP) {
    Write-Host "[doctor] Security deep: bandit & pip-audit"
    if (Get-Command python -ErrorAction SilentlyContinue) {
      python -m bandit -q -r $PY_DIRS -f json -o tools/bandit_report.json | Out-Null
    } else { Write-Host "[doctor][info] python not found for bandit" }
    if (Get-Command python -ErrorAction SilentlyContinue) {
      python -m pip_audit -f json -o tools/pip_audit_report.json | Out-Null
    } else { Write-Host "[doctor][info] python not found for pip-audit" }
  }
}

function Run-Frontend {
  if (Test-Path "$FRONTEND_DIR/package.json") {
    Write-Host "[doctor] Frontend: lint & format"
    if (Get-Command npm -ErrorAction SilentlyContinue) {
      Push-Location $FRONTEND_DIR
      npm run lint --silent; npm run format --silent; npm run typecheck --silent
      Pop-Location
    } else { Write-Host "[doctor][warn] npm not found; skipping frontend checks" }
  }
}

switch ($MODE) {
  "check" {
    Run-RuffCheck
    Run-TypesAndTests
    Run-SecretsScan
    Run-SecurityDeep
    Run-Frontend
  }
  "fix" {
    Run-RuffFix
    Run-TypesAndTests
    Run-SecretsScan
    Run-SecurityDeep
    Run-Frontend
  }
  "guarded-fix" {
    if (Get-Command git -ErrorAction SilentlyContinue) {
      $status = git status --porcelain
      if ($status) { Write-Host "[doctor][error] Guarded fix requires a clean git working tree. Commit or stash changes first."; exit 2 }
    } else { Write-Host "[doctor][warn] git not found; guarded-fix cannot guarantee safety" }

    Run-RuffFix

    if (Get-Command pytest -ErrorAction SilentlyContinue) {
      pytest -q --maxfail=1 --disable-warnings
      if ($LASTEXITCODE -ne 0) {
        if (Get-Command git -ErrorAction SilentlyContinue) { Write-Host "[doctor] Tests failed; reverting changes via git reset --hard"; git reset --hard }
        exit $LASTEXITCODE
      }
    }

    Run-TypesAndTests
    Run-SecretsScan
    Run-SecurityDeep
    Run-Frontend
  }
  default { Write-Host "[doctor][error] Unknown mode: $MODE"; exit 2 }
}
if ($GLOBAL_LAST_ERROR -ne 0) {
  Write-Host "[doctor] Completed with errors (exit=$GLOBAL_LAST_ERROR)"
  exit $GLOBAL_LAST_ERROR
}
Write-Host "[doctor] Done"
