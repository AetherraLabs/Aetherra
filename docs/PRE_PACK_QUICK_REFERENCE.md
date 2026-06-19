# Pre-Pack Validation - Quick Reference Card

## 🚀 Quick Commands

### Run Validation

```powershell
# Basic test
python tools/pre_pack_validation.py --profile test

# Production check
python tools/pre_pack_validation.py --profile prod --verbose

# Full automated suite (PowerShell)
.\tools\run_pre_pack_validation.ps1 -Profile prod -SetProdFlags -Full
```

### VS Code Tasks

Press `Ctrl+Shift+P` → "Tasks: Run Task" → Select:

- **Pre-Pack Validation (Test Profile)** - Quick validation
- **Pre-Pack Validation (Production Profile)** - Prod validation
- **Pre-Pack Validation (Full Suite - PowerShell)** - Complete suite
- **Pre-Pack: Complete Validation + Tests** - Everything (sequential)

## 🔴 Critical Pre-Production Flags

**Copy-paste this into your terminal before packaging:**

```powershell
# === CRITICAL SECURITY FLAGS (MUST SET) ===
$env:AETHERRA_PROFILE = "prod"
$env:AETHERRA_SIGNING_STRICT = "1"
$env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
$env:AETHERRA_REQUIRE_STRICT = "1"
$env:AETHERRA_REQUIRE_CAPABILITIES = "1"
$env:AETHERRA_NET_STRICT = "1"
$env:AETHERRA_AI_API_REQUIRE_TOKEN = "1"

# === REQUIRED: Set these to actual values ===
$env:AETHERRA_AI_API_TOKEN = "YOUR-SECURE-TOKEN-HERE"
$env:AETHERRA_NETWORK_ALLOWLIST = "localhost,127.0.0.1,.aetherra.dev"
$env:AETHERRA_KEYS_MASTER = "YOUR-MASTER-KEY-HERE"

# === MUST DISABLE ===
$env:AETHERRA_HMR_ENABLED = "0"
$env:AETHERRA_TRAINER_ENABLED = "0"

# === RECOMMENDED DISABLE (Experimental) ===
$env:AETHERRA_QFAC_MODE = "disabled"
$env:AETHERRA_MEMORY_STORM = "0"

# === PRODUCTION SETTINGS ===
$env:AETHERRA_QUIET = "1"
$env:AETHERRA_AI_API_ENABLED = "1"
$env:AETHERRA_AI_API_STREAM = "1"
```

## 📋 Pre-Package Checklist (30-Second Version)

```
[ ] All critical flags set (see above)
[ ] python tools/pre_pack_validation.py --profile prod → 0 failures
[ ] pytest -q tests/smoke → all pass
[ ] pytest -q tests/capabilities → all pass
[ ] python tools/verify_aether_scripts.py --strict → 100% signed
[ ] Start system, run for 5 min, no crashes
[ ] Review pre_pack_validation_report.json → no FAIL status
```

**IF ANY FAIL → DO NOT PACKAGE**

## 🎯 Status Indicators

| Symbol | Status           | Action                    |
| ------ | ---------------- | ------------------------- |
| 🟢      | Ready            | Good to go                |
| 🟡      | Testing needed   | Run validation            |
| 🔴      | Critical blocker | MUST FIX                  |
| ✅      | Pass             | Check passed              |
| ❌      | Fail             | Must fix before packaging |
| ⚠️      | Warning          | Review before production  |

## 📊 Where to Look

### After Running Validation

1. **Console output** - Immediate pass/fail results
2. **`pre_pack_validation_report.json`** - Detailed results
3. **`docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md`** - Full tracking document
4. **`aether_static_report.md`** - Script signing report

### Current Status

Check the dashboard in `docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md`:

```markdown
| Category | Status | Blockers | Notes    |
| -------- | ------ | -------- | -------- |
| Security | 🔴      | 6        | CRITICAL |
```

## 🛠️ Common Fixes

### "Token not set"

```powershell
$env:AETHERRA_AI_API_TOKEN = (New-Guid).ToString()
```

### "Unsigned scripts"

```powershell
python tools/sign_aether.py workflows/*.aether
```

### "Module not found"

```powershell
pip install -r requirements.txt
```

### "HMR enabled"

```powershell
$env:AETHERRA_HMR_ENABLED = "0"
```

## 📞 Documentation

- **Full Guide:** `docs/PRE_PACK_VALIDATION_GUIDE.md`
- **Tracking:** `docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md`
- **Summary:** `docs/prepack/PRE_PACK_VALIDATION_SUMMARY.md`
- **This Card:** `docs/PRE_PACK_QUICK_REFERENCE.md`

## 🎬 Complete Workflow (5 Minutes)

```powershell
# 1. Set flags (copy from "Critical Flags" section above)

# 2. Run validation
.\tools\run_pre_pack_validation.ps1 -Profile prod -SetProdFlags

# 3. Check result
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Ready for packaging" -ForegroundColor Green
} else {
    Write-Host "❌ Fix failures first" -ForegroundColor Red
}

# 4. If needed, run tests
pytest -q tests/smoke

# 5. Review report
Get-Content pre_pack_validation_report.json | ConvertFrom-Json |
    Select-Object -ExpandProperty results |
    Where-Object { $_.status -eq "FAIL" }

# 6. Sign off and package
```

## ⚡ Emergency Pre-Pack Check

**Less than 2 minutes - absolute minimum:**

```powershell
# Set critical flags
$env:AETHERRA_SIGNING_STRICT = "1"
$env:AETHERRA_NET_STRICT = "1"
$env:AETHERRA_HMR_ENABLED = "0"
$env:AETHERRA_TRAINER_ENABLED = "0"

# Run quick validation
python tools/pre_pack_validation.py --profile prod

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Error "FAILED - DO NOT PACKAGE"
    exit 1
}
```

## 🎯 Success Criteria

**Green light to package when:**

- ✅ Validation script exits with code 0
- ✅ Zero FAIL results in report
- ✅ All critical security flags set
- ✅ Smoke tests pass
- ✅ No unsigned scripts

**DO NOT PACKAGE if:**

- ❌ Any validation FAIL status
- ❌ Critical flags not set
- ❌ Unsigned .aether scripts exist
- ❌ Security warnings present
- ❌ HMR or Trainer enabled

---

**Keep this handy during your packaging process!**

**Last Updated:** 2025-10-31
**Quick Access:** Bookmark this file in your editor
