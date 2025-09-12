# Deterministic Smoke Profile

Use this profile for fast, bounded CI validation without exposing external model APIs.

## Environment Block

Add (PowerShell example):

```powershell
$env:AETHERRA_PROFILE='test'
$env:AETHERRA_QUIET='1'
$env:AETHERRA_LOG_LEVEL='INFO'
$env:AETHERRA_SCRIPT_VERIFY_STRICT='1'
$env:AETHERRA_SIGNING_STRICT='1'
$env:AETHERRA_REQUIRE_CAPABILITIES='1'
$env:AETHERRA_REQUIRE_STRICT='1'
$env:AETHERRA_NET_STRICT='1'
$env:AETHERRA_AI_API_ENABLED='0'
$env:AETHERRA_KERNEL_QSIZE_HIGH='64'
$env:AETHERRA_KERNEL_QSIZE_NORMAL='256'
$env:AETHERRA_KERNEL_QSIZE_BACKGROUND='256'
$env:AETHERRA_KERNEL_DLQ='1'
$env:AETHERRA_KERNEL_TASK_DEFAULT_TTL_SEC='120'
$env:AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC='20'
$env:AETHERRA_PLUGIN_CB_THRESHOLD='3'
$env:AETHERRA_PLUGIN_CB_COOLDOWN_SEC='60'
$env:AETHERRA_HMR_ENABLED='0'
$env:AETHERRA_QFAC_MODE='classical'
```

Then launch:

```powershell
python aetherra_os_launcher.py
```

Validate LLM wiring (keys optional, ensures graceful fallback):

```powershell
python tools/verify_llm_setup.py
```

Run strict .aether verification:

```powershell
python tools/verify_aether_scripts.py --root . --output aether_static_report.md --strict
```

## Expected Determinism

- No external network egress beyond allowlist.
- Stable queue metrics (bounded) even under plugin timeouts.
- Classical QFAC mode ensures memory metrics baseline stability.

## Fail Fast Signals

- Any unsigned workflow present when strict flags enabled.
- Plugin invoke exceeding timeout → circuit breaker after threshold (3) and cooldown (60s).
- Registry reports DEGRADED for stale services per configured thresholds.

Reference: `DEPLOYMENT_TIERS.md` for production escalation.
