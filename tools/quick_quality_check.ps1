Param(
    [switch]$Fix
)

Write-Host "== Aetherra Quick Quality Check ==" -ForegroundColor Cyan
$ErrorActionPreference = 'Stop'

function Invoke-Step($Name, $ScriptBlock) {
    Write-Host "-- $Name" -ForegroundColor Yellow
    try {
        & $ScriptBlock
        if ($LASTEXITCODE -ne 0) { throw "Step failed: $Name (exit $LASTEXITCODE)" }
        Write-Host "OK: $Name" -ForegroundColor Green
    }
    catch {
        Write-Host "FAIL: $Name -> $_" -ForegroundColor Red
        $script:FAILED = $true
    }
}

# Note: Versioning is automated via python-semantic-release. Do not manually edit version strings;
# use Conventional Commit messages (feat:, fix:, perf:, refactor:, chore:, docs:, ci:, test:, revert:) to drive releases.

# 1. Ruff (lint)
Invoke-Step "ruff lint" { ruff check . }

# 2. Ruff format (idempotence)
if (-not $Fix) { Invoke-Step "ruff format (dry)" { ruff format --check . } } else { Invoke-Step "ruff format (apply)" { ruff format . } }

# 3. Black
if (-not $Fix) { Invoke-Step "black --check" { black --line-length 100 --check . } } else { Invoke-Step "black (apply)" { black --line-length 100 . } }

# 4. isort
if (-not $Fix) { Invoke-Step "isort --check-only" { isort --profile black --line-length 100 --check-only . } } else { Invoke-Step "isort (apply)" { isort --profile black --line-length 100 . } }

# 5. Minimal tests (single fast file if exists)
$test = "tests/capabilities/test_lyrixa_chat_bridge_schema.py"
if (Test-Path $test) {
    Invoke-Step "pytest minimal" { pytest -q -o addopts= $test::test_edit_plan_mirrors_suggestions_and_confidence_defaults }
}

# 6. Parse baseline sample
Invoke-Step "parse baseline sample" { python tools/generate_parse_baseline.py --limit 10 --output parse_baseline_sample.json > $null }

# 7. Classifier sample
Invoke-Step "classifier sample" { python tools/classify_aether_workflow_failures.py --limit 10 --output wf_sample.json --markdown wf_sample.md > $null }

# 7b. Fingerprint summary (if classifier output present)
if (Test-Path wf_sample.json) {
    try {
        $data = Get-Content wf_sample.json -Raw | ConvertFrom-Json
        if ($data.workflows) {
            $groups = $data.workflows | Where-Object { -not $_.ok -and $_.fingerprint } |
            Group-Object fingerprint | Sort-Object Count -Descending | Select-Object -First 5
            Write-Host "Top failure fingerprints:" -ForegroundColor Cyan
            foreach ($g in $groups) {
                $sample = ($g.Group | Select-Object -First 1)
                $cat = $sample.category
                Write-Host ("  {0}  count={1}  cat={2}  file={3}" -f $g.Name, $g.Count, $cat, $sample.path)
            }
        }
    }
    catch {
        Write-Host "Fingerprint summary error: $_" -ForegroundColor Yellow
    }
}

if ($FAILED) {
    Write-Host "One or more checks failed" -ForegroundColor Red
    exit 1
}
else {
    Write-Host "All quick checks passed" -ForegroundColor Green
}
