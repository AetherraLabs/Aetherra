$ErrorActionPreference = "Stop"
$GLOBAL_LAST_ERROR = 0
$PY_DIRS = "Aetherra"
$FRONTEND_DIR = "frontend"

# Force UTF-8 encoding to handle Unicode in logs
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

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

# Result tracking for final summary
$STEP_RESULTS = [System.Collections.Generic.List[PSCustomObject]]::new()
function Add-StepResult {
  param([string]$Step, [int]$Code, [string]$Note = "")
  $status = if ($Code -eq 0) { "OK" } elseif ($Code -eq 124) { "TIMEOUT" } elseif ($Code -eq -1) { "SKIP" } else { "FAIL" }
  $script:STEP_RESULTS.Add([PSCustomObject]@{ Step = $Step; Status = $status; Code = $Code; Note = $Note })
}

# Helper to invoke external tools with a timeout; streams output safely
function Invoke-CommandWithTimeout {
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [Parameter(Mandatory = $true)][string[]]$Arguments,
    [Parameter(Mandatory = $true)][int]$TimeoutSec,
    [string]$WorkingDirectory,
    [bool]$AllowFailure = $false
  )
  try {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = ($Arguments -join ' ')
    if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8

    # Resolve wrappers on Windows (.cmd/.bat/.ps1)
    $resolvedCmd = Get-Command $FilePath -ErrorAction SilentlyContinue
    if ($resolvedCmd) {
      $ext = [System.IO.Path]::GetExtension($resolvedCmd.Source).ToLower()
      if ($ext -in @('.cmd', '.bat')) {
        $psi.FileName = "cmd.exe"
        $psi.Arguments = "/c `"$($resolvedCmd.Source)`" $($Arguments -join ' ')"
      }
      elseif ($ext -eq '.ps1') {
        $psi.FileName = "powershell.exe"
        $psi.Arguments = "-ExecutionPolicy Bypass -File `"$($resolvedCmd.Source)`" $($Arguments -join ' ')"
      }
      else {
        $psi.FileName = $resolvedCmd.Source
      }
    }

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    Write-Host "[doctor] RUN> $($psi.FileName) $($psi.Arguments) (timeout=${TimeoutSec}s)"
    $null = $proc.Start()

    # Start asynchronous read before waiting to avoid pipe deadlocks
    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()

    if (-not $proc.WaitForExit($TimeoutSec * 1000)) {
      Write-Host "[doctor][timeout] Exceeded ${TimeoutSec}s; terminating $FilePath" -ForegroundColor Yellow
      try { $proc.Kill() } catch {}
      try { $null = $stdoutTask.Wait(5000) } catch {}
      try { $null = $stderrTask.Wait(5000) } catch {}
      $script:GLOBAL_LAST_ERROR = 124
      return 124
    }

    $stdout = $stdoutTask.Result
    $stderr = $stderrTask.Result
    if ($stdout) { $stdout | Out-Host }
    if ($stderr) { $stderr | Out-Host }
    if ($proc.ExitCode -ne 0 -and -not $AllowFailure) { $script:GLOBAL_LAST_ERROR = $proc.ExitCode }
    return $proc.ExitCode
  }
  catch {
    Write-Host "[doctor][error] Failed to execute $FilePath : $($_.Exception.Message)" -ForegroundColor Red
    $script:GLOBAL_LAST_ERROR = 1
    return 1
  }
}

function Run-RuffCheck {
  if ($FAST) {
    Write-Host "[doctor][info] Fast mode: skipping ruff format/check"
    Add-StepResult "ruff-format" -1 "fast"
    Add-StepResult "ruff-check" -1 "fast"
    return
  }
  if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] Ruff format --check"
    $rc1 = Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("format", "--check", ".") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 180))
    Add-StepResult "ruff-format" $rc1
    Write-Host "[doctor] Ruff check"
    $rc2 = Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("check", ".") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300))
    Add-StepResult "ruff-check" $rc2
  }
  else {
    Write-Host "[doctor][warn] ruff not found; skipping format/lint"
    Add-StepResult "ruff" -1 "not installed"
  }
}

function Run-RuffFix {
  if ($FAST) {
    Write-Host "[doctor][info] Fast mode: skipping ruff format/fix"
    Add-StepResult "ruff-format" -1 "fast"
    Add-StepResult "ruff-fix" -1 "fast"
    return
  }
  if (Get-Command ruff -ErrorAction SilentlyContinue) {
    Write-Host "[doctor] Ruff format & fix"
    $rc1 = Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("format", ".") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 180))
    Add-StepResult "ruff-format" $rc1
    # In --fix mode, apply all safe auto-fixes but don't fail just because
    # non-fixable lint debt remains in the repository.
    $rc2 = Invoke-CommandWithTimeout -FilePath "ruff" -Arguments @("check", ".", "--fix", "--exit-zero") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300))
    Add-StepResult "ruff-fix" $rc2
  }
  else {
    Write-Host "[doctor][warn] ruff not found; skipping format/lint"
    Add-StepResult "ruff" -1 "not installed"
  }
}

function Test-NpmScript {
  param(
    [Parameter(Mandatory = $true)][string]$PackageJsonPath,
    [Parameter(Mandatory = $true)][string]$ScriptName
  )
  if (-not (Test-Path $PackageJsonPath)) { return $false }
  try {
    $pkg = Get-Content $PackageJsonPath -Raw | ConvertFrom-Json
    return ($null -ne $pkg.scripts -and $null -ne $pkg.scripts.$ScriptName)
  }
  catch {
    return $false
  }
}

function Run-TypesAndTests {
  Write-Host "[doctor] MyPy (strict-ish)"
  if ($FAST) {
    Write-Host "[doctor][info] Fast mode: skipping mypy"
    Add-StepResult "mypy" -1 "fast"
  }
  elseif (Get-Command mypy -ErrorAction SilentlyContinue) {
    $mypySoftFail = ($MODE -eq "fix")
    $rcMypy = Invoke-CommandWithTimeout -FilePath "mypy" -Arguments @("--no-incremental", $PY_DIRS) -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300)) -AllowFailure $mypySoftFail
    if ($mypySoftFail -and $rcMypy -ne 0) {
      Write-Host "[doctor][warn] mypy reported issues (non-blocking in --fix mode)" -ForegroundColor Yellow
      Add-StepResult "mypy" -1 "non-blocking in --fix"
    }
    else {
      Add-StepResult "mypy" $rcMypy
    }
  }
  else {
    Write-Host "[doctor][warn] mypy not found; skipping"
    Add-StepResult "mypy" -1 "not installed"
  }

  Write-Host "[doctor] Pyright (optional)"
  if (-not $FAST -and (Get-Command pyright -ErrorAction SilentlyContinue)) {
    $rcPy = Invoke-CommandWithTimeout -FilePath "pyright" -Arguments @() -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300))
    Add-StepResult "pyright" $rcPy
  }
  else {
    Write-Host "[doctor][info] pyright not installed or fast mode"
    Add-StepResult "pyright" -1 "skipped"
  }

  Write-Host "[doctor] Smoke: tools/os_smoke.py"
  if (Get-Command python -ErrorAction SilentlyContinue) {
    $env:AETHERRA_QUIET = "1"
    $rcSmoke = Invoke-CommandWithTimeout -FilePath "python" -Arguments @("tools/os_smoke.py") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 180))
    Add-StepResult "smoke" $rcSmoke
    if ($rcSmoke -ne 0) { Write-Host "[doctor][error] Smoke test failed" }
  }
  else {
    Write-Host "[doctor][warn] python not found; skipping smoke"
    Add-StepResult "smoke" -1 "python missing"
  }

  if (-not $FAST) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
      Write-Host "[doctor] PyTest (capabilities slice)"
      $env:AETHERRA_QUIET = "1"
      $pytestArgs = @("-m", "pytest", "-q", "-o", "addopts=", "--tb=short", "tests/capabilities")
      $rcTests = Invoke-CommandWithTimeout -FilePath "python" -Arguments $pytestArgs -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 600))
      Add-StepResult "capabilities" $rcTests
      if ($rcTests -ne 0) { Write-Host "[doctor][error] Capabilities tests failed" }
    }
    else {
      Write-Host "[doctor][warn] python not found; skipping tests"
      Add-StepResult "capabilities" -1 "python missing"
    }
  }
  else {
    Write-Host "[doctor][info] Fast mode: skipping pytest capabilities slice"
    Add-StepResult "capabilities" -1 "fast"
  }
}

function Get-GitleaksExe {
  $cmd = Get-Command gitleaks -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  if ($env:VIRTUAL_ENV) {
    $candidate = Join-Path $env:VIRTUAL_ENV "Scripts\gitleaks.exe"
    if (Test-Path $candidate) { return $candidate }
  }
  $here = Resolve-Path "."
  $localCandidate = Join-Path $here ".venv\Scripts\gitleaks.exe"
  if (Test-Path $localCandidate) { return $localCandidate }
  return $null
}

function Run-SecretsScan {
  Write-Host "[doctor] Gitleaks scan"
  $gitleaksExe = Get-GitleaksExe
  if ($gitleaksExe) {
    $rcGl = Invoke-CommandWithTimeout -FilePath $gitleaksExe -Arguments @("detect", "--no-banner", "--redact", "--report-path", "tools/gitleaks_report.json") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 180))
    Add-StepResult "gitleaks" $rcGl
    if ($rcGl -ne 0) { Write-Host "[doctor] gitleaks found issues (report saved to tools/gitleaks_report.json)" }
  }
  else {
    Write-Host "[doctor][warn] gitleaks not found; install via Chocolatey (choco install gitleaks) or Scoop (scoop install gitleaks)"
    Add-StepResult "gitleaks" -1 "not installed"
  }
}

function Run-SecurityDeep {
  if ($SECURITY_DEEP) {
    Write-Host "[doctor] Security deep: bandit & pip-audit"
    if (Get-Command python -ErrorAction SilentlyContinue) {
      $rcBandit = Invoke-CommandWithTimeout -FilePath "python" -Arguments @("-m", "bandit", "-q", "-r", $PY_DIRS, "-f", "json", "-o", "tools/bandit_report.json") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300))
      Add-StepResult "bandit" $rcBandit
    }
    else {
      Write-Host "[doctor][info] python not found for bandit"
      Add-StepResult "bandit" -1 "python missing"
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
      $rcAudit = Invoke-CommandWithTimeout -FilePath "python" -Arguments @("-m", "pip_audit", "-f", "json", "-o", "tools/pip_audit_report.json") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300))
      Add-StepResult "pip-audit" $rcAudit
    }
    else {
      Write-Host "[doctor][info] python not found for pip-audit"
      Add-StepResult "pip-audit" -1 "python missing"
    }
  }
}

function Run-Frontend {
  if (Test-Path "$FRONTEND_DIR/package.json") {
    Write-Host "[doctor] Frontend: lint & format"
    if (-not $FAST -and (Get-Command npm -ErrorAction SilentlyContinue)) {
      $pkgPath = Join-Path $FRONTEND_DIR "package.json"
      $hasLint = Test-NpmScript -PackageJsonPath $pkgPath -ScriptName "lint"
      $hasFormat = Test-NpmScript -PackageJsonPath $pkgPath -ScriptName "format"
      $hasTypecheck = Test-NpmScript -PackageJsonPath $pkgPath -ScriptName "typecheck"
      Push-Location $FRONTEND_DIR
      try {
        if ($hasLint) {
          $rcLint = Invoke-CommandWithTimeout -FilePath "npm" -Arguments @("run", "lint", "--silent") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300))
          Add-StepResult "frontend-lint" $rcLint
        }
        else {
          Write-Host "[doctor][info] frontend script missing: lint (skipping)"
          Add-StepResult "frontend-lint" -1 "missing script"
        }

        if ($hasFormat) {
          $rcFmt = Invoke-CommandWithTimeout -FilePath "npm" -Arguments @("run", "format", "--silent") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 180))
          Add-StepResult "frontend-format" $rcFmt
        }
        else {
          Write-Host "[doctor][info] frontend script missing: format (skipping)"
          Add-StepResult "frontend-format" -1 "missing script"
        }

        if ($hasTypecheck) {
          $rcTc = Invoke-CommandWithTimeout -FilePath "npm" -Arguments @("run", "typecheck", "--silent") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 300))
          Add-StepResult "frontend-typecheck" $rcTc
        }
        else {
          Write-Host "[doctor][info] frontend script missing: typecheck (skipping)"
          Add-StepResult "frontend-typecheck" -1 "missing script"
        }
      }
      finally {
        Pop-Location
      }
    }
    else {
      Write-Host "[doctor][warn] npm not found or fast mode; skipping frontend checks"
      Add-StepResult "frontend" -1 "skipped"
    }
  }
  else {
    Add-StepResult "frontend" -1 "no package.json"
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
      if ($status) {
        Write-Host "[doctor][error] Guarded fix requires a clean git working tree. Commit or stash changes first."
        exit 2
      }
    }
    else {
      Write-Host "[doctor][warn] git not found; guarded-fix cannot guarantee safety"
    }

    Run-RuffFix

    if (Get-Command python -ErrorAction SilentlyContinue) {
      $rcGuard = Invoke-CommandWithTimeout -FilePath "python" -Arguments @("-m", "pytest", "-q", "-o", "addopts=", "--maxfail=1", "--disable-warnings", "--tb=short") -TimeoutSec $([Math]::Min($TIMEOUT_SEC, 600))
      if ($rcGuard -ne 0) {
        if (Get-Command git -ErrorAction SilentlyContinue) {
          Write-Host "[doctor] Tests failed; reverting changes via git reset --hard"
          git reset --hard
        }
        exit $rcGuard
      }
    }

    Run-TypesAndTests
    Run-SecretsScan
    Run-SecurityDeep
    Run-Frontend
  }
  default {
    Write-Host "[doctor][error] Unknown mode: $MODE"
    exit 2
  }
}

Write-Host ""
Write-Host "=== DOCTOR SUMMARY ==" -ForegroundColor Cyan
foreach ($r in $STEP_RESULTS) {
  $color = switch ($r.Status) {
    "OK" { "Green" }
    "SKIP" { "DarkGray" }
    "TIMEOUT" { "Yellow" }
    default { "Red" }
  }
  $noteStr = if ($r.Note) { "  ($($r.Note))" } else { "" }
  Write-Host ("  {0,-28} {1}{2}" -f $r.Step, $r.Status, $noteStr) -ForegroundColor $color
}
Write-Host ""

if ($GLOBAL_LAST_ERROR -ne 0) {
  Write-Host "[doctor] Completed with errors (exit=$GLOBAL_LAST_ERROR)" -ForegroundColor Red
  exit $GLOBAL_LAST_ERROR
}
Write-Host "[doctor] Done" -ForegroundColor Green
