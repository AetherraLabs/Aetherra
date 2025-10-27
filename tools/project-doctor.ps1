$ErrorActionPreference = "Stop"
$GLOBAL_LAST_ERROR = 0
$PY_DIRS = "Aetherra"
$FRONTEND_DIR = "frontend"

# Modes: --check, --fix (default), --guarded-fix; optional --security-deep, --fast, --timeout <sec>
$MODE = "fix"
$SECURITY_DEEP = $false
$FAST = $false
$TIMEOUT_SEC = 600

for ($i = 0; $i -lt $args.Count; $i++) {
  $arg = $args[$i]
  switch ($arg) {
    "--check" { $MODE = "check" }
    "--fix" { $MODE = "fix" }
    "--guarded-fix" { $MODE = "guarded-fix" }
    "--security-deep" { $SECURITY_DEEP = $true }
    "--fast" { $FAST = $true }
    "--timeout" {
      if ($i + 1 -lt $args.Count) {
        $i++
        [int]$TIMEOUT_SEC = $args[$i]
      }
    }
  }
}

if ($env:DOCTOR_TIMEOUT_SEC) { [int]$TIMEOUT_SEC = $env:DOCTOR_TIMEOUT_SEC }
Write-Host "[doctor] Mode: $MODE (fast=$FAST) timeout=${TIMEOUT_SEC}s"

# Helper to invoke external tools with a timeout; captures output
function Invoke-CommandWithTimeout {
  param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [Parameter(Mandatory=$true)][string[]]$Arguments,
    [Parameter(Mandatory=$true)][int]$TimeoutSec,
    [string]$WorkingDirectory
  )
  try {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = ($Arguments -join ' ')
    if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    Write-Host "[doctor] RUN> $FilePath $($Arguments -join ' ') (timeout=${TimeoutSec}s)"
    $null = $proc.Start()
    if (-not $proc.WaitForExit($TimeoutSec * 1000)) {
      Write-Host "[doctor][timeout] Exceeded ${TimeoutSec}s; terminating $FilePath" -ForegroundColor Yellow
      try { $proc.Kill() } catch {}
      $script:GLOBAL_LAST_ERROR = 124
      return 124
    }
    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    if ($stdout) { $stdout | Out-Host }
    if ($stderr) { $stderr | Out-Host }
    if ($proc.ExitCode -ne 0) { $script:GLOBAL_LAST_ERROR = $proc.ExitCode }
    return $proc.ExitCode
  } catch {
    Write-Host "[doctor][error] Failed to execute $FilePath : $($_.Exception.Message)" -ForegroundColor Red
    $script:GLOBAL_LAST_ERROR = 1
    return 1
  }
}

function Run-RuffCheck {
  if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] Ruff format --check"
    Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("format","--check",".") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,180)) | Out-Null
    Write-Host "[doctor] Ruff check"
    Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("check",".") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,300)) | Out-Null
  } else { Write-Host "[doctor][warn] ruff not found; skipping format/lint" }
}

function Run-RuffFix {
  if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] Ruff format & fix"
    Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("format",".") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,180)) | Out-Null
    Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("check",".","--fix") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,300)) | Out-Null
  } else { Write-Host "[doctor][warn] ruff not found; skipping format/lint" }
}

function Run-TypesAndTests {
  Write-Host "[doctor] MyPy (strict-ish)"
  if (Get-Command mypy -ErrorAction SilentlyContinue) { Invoke-CommandWithTimeout -FilePath "mypy" -Arguments @($PY_DIRS) -TimeoutSec $([Math]::Min($TIMEOUT_SEC,300)) | Out-Null } else { Write-Host "[doctor][warn] mypy not found; skipping" }

  Write-Host "[doctor] Pyright (optional)"
  if (-not $FAST -and (Get-Command pyright -ErrorAction SilentlyContinue)) { Invoke-CommandWithTimeout -FilePath "pyright" -Arguments @() -TimeoutSec $([Math]::Min($TIMEOUT_SEC,300)) | Out-Null } else { Write-Host "[doctor][info] pyright not installed or fast mode" }

  # Prefer fast, reliable checks over full suite during local doctor runs
  # 1) Headless OS smoke
  Write-Host "[doctor] Smoke: tools/os_smoke.py"
  if (Get-Command python -ErrorAction SilentlyContinue) {
    $env:AETHERRA_QUIET = "1"
    $rc = Invoke-CommandWithTimeout -FilePath "python" -Arguments @("tools/os_smoke.py") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,180))
    if ($rc -ne 0) {
      Write-Host "[doctor][error] Smoke test failed"
      $script:GLOBAL_LAST_ERROR = $rc
    }
  } else { Write-Host "[doctor][warn] python not found; skipping smoke" }

  # 2) Capabilities slice (faster than full test run)
  if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] PyTest (capabilities slice)"
    $env:AETHERRA_QUIET = "1"
    $pytestArgs = @("-m","pytest","-q","-o","addopts=","tests/capabilities")
    $rc2 = Invoke-CommandWithTimeout -FilePath "python" -Arguments $pytestArgs -TimeoutSec $([Math]::Min($TIMEOUT_SEC,600))
    if ($rc2 -ne 0) {
      Write-Host "[doctor][error] Capabilities tests failed"
      $script:GLOBAL_LAST_ERROR = $rc2
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
    $rc = Invoke-CommandWithTimeout -FilePath $gitleaksExe -Arguments @("detect","--no-banner","--redact","--report-path","tools/gitleaks_report.json") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,180))
    if ($rc -ne 0) { Write-Host "[doctor] gitleaks found issues (report saved)" }
  } else {
    Write-Host "[doctor][warn] gitleaks not found; install via Chocolatey (choco install gitleaks) or Scoop (scoop install gitleaks)"
  }
}

function Run-SecurityDeep {
  if ($SECURITY_DEEP) {
    Write-Host "[doctor] Security deep: bandit & pip-audit"
    if (Get-Command python -ErrorAction SilentlyContinue) {
      $null = Invoke-CommandWithTimeout -FilePath "python" -Arguments @("-m","bandit","-q","-r",$PY_DIRS,"-f","json","-o","tools/bandit_report.json") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,300))
    } else { Write-Host "[doctor][info] python not found for bandit" }
    if (Get-Command python -ErrorAction SilentlyContinue) {
      $null = Invoke-CommandWithTimeout -FilePath "python" -Arguments @("-m","pip_audit","-f","json","-o","tools/pip_audit_report.json") -TimeoutSec $([Math]::Min($TIMEOUT_SEC,300))
    } else { Write-Host "[doctor][info] python not found for pip-audit" }
  }
}

function Run-Frontend {
  if (Test-Path "$FRONTEND_DIR/package.json") {
    Write-Host "[doctor] Frontend: lint & format"
    if (-not $FAST -and (Get-Command npm -ErrorAction SilentlyContinue)) {
      Push-Location $FRONTEND_DIR
      $null = Invoke-CommandWithTimeout -FilePath "npm" -Arguments @("run","lint","--silent") -TimeoutSec [Math]::Min($TIMEOUT_SEC,300)
      $null = Invoke-CommandWithTimeout -FilePath "npm" -Arguments @("run","format","--silent") -TimeoutSec [Math]::Min($TIMEOUT_SEC,180)
      $null = Invoke-CommandWithTimeout -FilePath "npm" -Arguments @("run","typecheck","--silent") -TimeoutSec [Math]::Min($TIMEOUT_SEC,300)
      Pop-Location
    } else { Write-Host "[doctor][warn] npm not found or fast mode; skipping frontend checks" }
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
      $null = Invoke-CommandWithTimeout -FilePath "pytest" -Arguments @("-q","--maxfail=1","--disable-warnings") -TimeoutSec [Math]::Min($TIMEOUT_SEC,600)
      if ($GLOBAL_LAST_ERROR -ne 0) {
        if (Get-Command git -ErrorAction SilentlyContinue) { Write-Host "[doctor] Tests failed; reverting changes via git reset --hard"; git reset --hard }
        exit $GLOBAL_LAST_ERROR
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
