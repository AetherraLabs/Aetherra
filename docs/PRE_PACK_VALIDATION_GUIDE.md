# Pre-Pack Validation Guide

This guide helps you systematically validate Aetherra & Lyrixa before building the production `.exe` package.

## Quick Start

### Option 1: Run Automated Validation (Recommended)

```powershell
# For development/test validation
.\tools\run_pre_pack_validation.ps1 -Profile test -Verbose

# For production validation (sets all security flags)
.\tools\run_pre_pack_validation.ps1 -Profile prod -SetProdFlags -Full

# Quick smoke test only
.\tools\run_pre_pack_validation.ps1 -RunSmokeTests
```

### Option 2: Run Python Validation Script Directly

```powershell
# Basic validation
python tools/pre_pack_validation.py --profile test

# Production validation with verbose output
python tools/pre_pack_validation.py --profile prod --verbose --output validation_report.json
```

## What Gets Checked

### Automated Validation Suite

The `pre_pack_validation.py` script checks:

1. ✅ **Kernel System** - Loop, queues, HMR config
2. ✅ **AI Engine** - Session management, coordinator
3. ✅ **Agent System** - Registry, task submission
4. ✅ **Chat System** - Endpoints, blueprints
5. ✅ **Memory System** - Core, Advanced, QFAC, STORM
6. ✅ **Security** - Signing strict, network policy, secrets
7. ✅ **Aether Scripts** - Verification, signing
8. ✅ **Lyrixa Studio** - Components, modules
9. ✅ **Homeostasis** - Health monitoring, self-healing
10. ✅ **Lyrixa Bridge** - Chat integration
11. ✅ **AI Trainer** - Disabled check (must be OFF for prod)

### Manual Checks Required

Some validations require a running system:

```powershell
# 1. Start the stack
python aetherra_registry_daemon.py
python tools/run_hub_ai_api.py --port 3001
python aetherra_os_launcher.py --mode full -v

# 2. Run endpoint checks
.\tools\run_pre_pack_validation.ps1 -CheckEndpoints

# 3. Run full test suite
pytest -q tests/

# 4. Run capability tests
pytest -q tests/capabilities

# 5. Run Go-NoGo gates
python tools/run_go_no_go_gates.py --all
```

## Critical Pre-Production Checks

### Security Flags (MUST BE SET)

```powershell
# Set these environment variables before packaging:
$env:AETHERRA_PROFILE = "prod"
$env:AETHERRA_SIGNING_STRICT = "1"
$env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
$env:AETHERRA_REQUIRE_STRICT = "1"
$env:AETHERRA_NET_STRICT = "1"
$env:AETHERRA_AI_API_REQUIRE_TOKEN = "1"
$env:AETHERRA_AI_API_TOKEN = "<your-secure-token>"
$env:AETHERRA_NETWORK_ALLOWLIST = "localhost,127.0.0.1,.aetherra.dev"
$env:AETHERRA_KEYS_MASTER = "<your-master-key>"
```

### Features to Disable

```powershell
# MUST be disabled for production:
$env:AETHERRA_HMR_ENABLED = "0"
$env:AETHERRA_TRAINER_ENABLED = "0"

# Recommended to disable (experimental):
$env:AETHERRA_QFAC_MODE = "disabled"
$env:AETHERRA_MEMORY_STORM = "0"
```

## Understanding Results

### Exit Codes

- `0` - All checks passed or warnings only
- `1` - Critical failures detected, DO NOT PACKAGE

### Result Status Types

- `PASS` ✅ - Check passed successfully
- `FAIL` ❌ - Critical failure, must fix
- `WARN` ⚠️ - Warning, review before packaging
- `SKIP` ⏭️ - Check skipped (optional feature)

### Report Files

After validation, check these files:

1. **`pre_pack_validation_report.json`** - Detailed JSON report with all results
2. **`docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md`** - Master tracking document with status
3. **`aether_static_report.md`** - Aether script verification report

## Step-by-Step Pre-Package Workflow

### Step 1: Initial Validation

```powershell
# Run validation with current settings
python tools/pre_pack_validation.py --profile test --verbose
```

Review output for any `FAIL` status checks.

### Step 2: Fix Issues

Address all failures before proceeding. Common issues:

- Missing module imports → Install dependencies
- Security flags not set → Set environment variables
- Unsigned scripts → Run signing tools

### Step 3: Set Production Flags

```powershell
# Use the helper script to set all flags
.\tools\run_pre_pack_validation.ps1 -Profile prod -SetProdFlags
```

Or set manually (see Critical Pre-Production Checks above).

### Step 4: Full Validation

```powershell
# Run complete validation with production profile
.\tools\run_pre_pack_validation.ps1 -Profile prod -Full
```

### Step 5: Runtime Validation

```powershell
# Start the system
python aetherra_os_launcher.py --mode full -v

# In another terminal, run endpoint checks
.\tools\run_pre_pack_validation.ps1 -CheckEndpoints

# Run smoke tests
pytest -q tests/smoke
```

### Step 6: Sign-Off

Check `docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md` and verify:

- [ ] All critical blockers resolved
- [ ] Security flags properly set
- [ ] All tests passing
- [ ] Runtime stability confirmed
- [ ] No memory leaks
- [ ] All scripts signed

### Step 7: Package

Only proceed with `.exe` building after all checks pass!

## Common Issues & Solutions

### Issue: "Module not found" errors

**Solution:** Install dependencies
```powershell
pip install -r requirements.txt
```

### Issue: "AETHERRA_AI_API_TOKEN not set"

**Solution:** Generate and set a secure token
```powershell
# Generate a random token
$token = [System.Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
$env:AETHERRA_AI_API_TOKEN = $token
```

### Issue: "Unsigned .aether scripts detected"

**Solution:** Sign all scripts
```powershell
python tools/sign_aether.py workflows/*.aether
```

### Issue: "HMR enabled in production"

**Solution:** Disable HMR
```powershell
$env:AETHERRA_HMR_ENABLED = "0"
```

### Issue: "Network policy not configured"

**Solution:** Set allowlist
```powershell
$env:AETHERRA_NET_STRICT = "1"
$env:AETHERRA_NETWORK_ALLOWLIST = "localhost,127.0.0.1,.aetherra.dev"
```

## Advanced Usage

### Running Specific Sections

The validation script checks all sections by default. To focus on specific areas, modify the script or review the report:

```powershell
# Generate report
python tools/pre_pack_validation.py --profile prod -o report.json

# Parse report for specific section
$report = Get-Content report.json | ConvertFrom-Json
$report.results | Where-Object { $_.section -like "6-Security*" }
```

### Custom Environment Configuration

Create a `.env.prod` file:

```bash
AETHERRA_PROFILE=prod
AETHERRA_SIGNING_STRICT=1
AETHERRA_SCRIPT_VERIFY_STRICT=1
AETHERRA_NET_STRICT=1
AETHERRA_HMR_ENABLED=0
# ... more settings
```

Load and validate:

```powershell
# Load .env.prod (requires dotenv or manual parsing)
Get-Content .env.prod | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# Run validation
python tools/pre_pack_validation.py --profile prod
```

### Integration with CI/CD

```yaml
# Example GitHub Actions workflow
- name: Pre-pack validation
  run: |
    python tools/pre_pack_validation.py --profile prod --output validation_report.json

- name: Upload validation report
  uses: actions/upload-artifact@v3
  with:
    name: validation-report
    path: validation_report.json

- name: Check for failures
  run: |
    $report = Get-Content validation_report.json | ConvertFrom-Json
    if ($report.summary.failed -gt 0) {
      Write-Error "Validation failed!"
      exit 1
    }
```

## Getting Help

### Documentation

- **Full checklist:** See original document in the prompt
- **Tracking:** `docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md`
- **Scripts:** `tools/pre_pack_validation.py` (well-commented)

### Support

If you encounter issues:

1. Check the validation report for detailed error messages
2. Review `docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md` for context
3. Ensure all dependencies are installed
4. Verify Python environment is activated
5. Check that required services are running (for endpoint tests)

## Maintenance

### Updating the Validation Suite

To add new checks:

1. Edit `tools/pre_pack_validation.py`
2. Add a new validation method (follow existing patterns)
3. Call it from `run_all_validations()`
4. Update `docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md` with the new check
5. Test thoroughly

### Updating the Tracking Document

`docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md` should be updated as you progress:

- Mark items complete: ✅
- Update status indicators: 🟢 🟡 🔴
- Add notes in the Progress Log section
- Update blocker counts in the dashboard

---

**Last Updated:** 2025-10-31
**Version:** 1.0
**Maintained by:** Aetherra Labs
