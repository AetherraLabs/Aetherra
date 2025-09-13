# Go / No-Go Gates (Fast Deterministic Suite)

This document captures the standardized 8 go-no‑go gates, how to run them quickly (local / CI), expected evidence, residual risk watchlist, and the sign‑off template.

---

## Quick Start (PowerShell / Windows)

```powershell
# Ensure virtualenv active if used
$env:AETHERRA_PROFILE='test'
$env:AETHERRA_QUIET='1'
python tools\run_go_no_go_gates.py --all
```

Artifacts produced:

- `gate_results.json`  (structured machine JSON)
- `gate_sign_off.md`   (markdown sign-off table + summary lines)

Exit code is non‑zero if any mandatory gate fails. HMR gate is marked manual-followup (🔧) unless strict manual is requested.

Strict manual enforcement (fail if any manual gate not fully validated):

```powershell
python tools\run_go_no_go_gates.py --strict-manual
```

Run a subset:

```powershell
python tools\run_go_no_go_gates.py --gates launcher_smoke chat_sse_resume
```

---

## Gate Details

### 1. Launcher Smoke

Validates phased boot and core service registration.

Command (direct):

```powershell
$env:AETHERRA_PROFILE='test'; $env:AETHERRA_QUIET='1'; python tools\os_smoke.py
```

Pass: core services (`memory_system`, `plugin_manager`, `aetherra_engine`) present.

### 2. Chat Transport & SSE v2 Resume

Checks envelope ordering and Last-Event-ID monotonic resume.

Minimal manual check:

```powershell
curl "http://localhost:3012/api/ai/stream?message=ping&scratchpad_policy=redacted"
```

Pass: status → policy (first 2–3), usage before final, resumed stream starts at prior_last_id+1.

### 3. Security Strict Modes

Scripts & .aether signing strict, network policy.

```powershell
$env:AETHERRA_SCRIPT_VERIFY_STRICT='1'; python tools\verify_aether_scripts.py --strict --output aether_static_report.md
```

Optionally set:

```powershell
$env:AETHERRA_NET_STRICT='1'
```

Pass: Unsigned scripts flagged (fail) in strict; disallowed outbound calls denied.

### 4. Memory (Core + QFAC Fallback)

```powershell
$env:AETHERRA_QFAC_MODE='hybrid'
python - <<'PY'
import asyncio, os
from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem
async def main():
  q = QFACMemorySystem('_quick_qfac')
  nid = await q.store_memory({'messages':['Hi'], 'kind':'conversation'})
  data = await q.retrieve_memory(nid)
  status = await q.get_system_status()
  print('node', nid, 'retrieved', type(data).__name__, 'nodes=', status['node_statistics']['total_nodes'])
asyncio.run(main())
PY
```

Pass: store/retrieve success; status node_statistics populated; hybrid gracefully degrades if quantum backend absent.

### 5. Kernel HMR + Quiesce (Manual Follow-Up)

Automation script only verifies controller presence & config metrics. Full validation:

1. Enable HMR env (`AETHERRA_HMR_STRICT=1`, optional `AETHERRA_HMR_ALLOWED_SOURCES`)
2. Enqueue kernel task `{type: 'hmr_reload', data: {target: 'engine', source: 'path_or_module'}}`
3. Inspect `.aetherra/hmr_audit.jsonl` for events: HMR_PREPARE → HMR_SWAP or HMR_ROLLBACK.

Pass: swap event or clean rollback with inflight drained.

### 6. Agents API Posture

Disabled by default; returns 501/403/disabled. Enable with token:

```powershell
$env:AETHERRA_AGENTS_API_ENABLED='1'
$env:AETHERRA_AGENTS_API_REQUIRE_TOKEN='1'
$env:AETHERRA_AGENTS_API_TOKEN='dev'
```

Pass: Disabled path blocked; enabled path returns orchestrator summary with token.

### 7. Quality Gates (Spec→Tests & Coverage No-Drop)

```powershell
pytest -q tests/capabilities
python tools\spec_tests_gate.py
python tools\quality_gates.py
```

Pass: tests succeed; spec gate passes (0 or 2 exit); coverage ≥ baseline & not dropped.

### 8. Policy & Privacy Signals

SSE or ask endpoints emit `X-Aetherra-Policy` header + policy event.

Optional DP flags:

```powershell
$env:AETHERRA_DP_ENABLED='1'
$env:AETHERRA_DP_EPSILON='8.0'
```

Pass: header parseable JSON, policy event present; DP keys appear when enabled.

---

## Residual Risk Watchlist (Abbrev)

| Area                            | Impact                    | Suggested Mitigation                      | Priority |
| ------------------------------- | ------------------------- | ----------------------------------------- | -------- |
| Plugin manifest signing partial | Unsigned third-party risk | Enforce Ed25519 & revocation list         | High     |
| Sandbox best-effort             | Escape risk               | Process/container isolation               | High     |
| HMR phase-1 limits              | Mid-flight swap risk      | Keep strict + night-cycle windows         | Med-High |
| Quantum bridge experimental     | Flakiness                 | Default classical in prod                 | Med      |
| Agents quotas absent            | Resource pressure         | Add per-agent budgets & metrics           | Med      |
| Chat no replay                  | Client mismatch           | Document semantics                        | Low-Med  |
| Network policy tuning           | Surprising denies         | Versioned allowlist tests                 | Med      |
| Simple vector recall            | Scale ceiling             | Plan adapter abstraction (pgvector/FAISS) | Low      |

Full rationale: see PR description or security notes.

---

## One-Look Runbook (Condensed)

| Area             | Command / Endpoint                | Expected                               |
| ---------------- | --------------------------------- | -------------------------------------- |
| Kernel status    | GET /api/kernel/status            | running=true, sane queues              |
| Kernel metrics   | GET /metrics                      | inflight & HMR counters                |
| Chat stream      | /api/ai/stream                    | status→policy→usage→final              |
| Lyrixa bridge    | POST /api/lyrixa/chat             | persona default, edit_plan synthesized |
| Security scripts | verify_aether_scripts.py --strict | OK or explicit FAIL lines              |
| Agents API       | /api/agents (off/on)              | disabled → summary w/token             |
| Memory health    | /api/memory/status                | coherence/branches metrics or fallback |

---

## First 24–48h Watch

- Security alerts: `.aetherra/security/alerts.jsonl` quiet
- Kernel DLQ: minimal expired/dropped tasks
- HMR audit rotation within configured caps
- Memory coherence/drift stable

---

## Sign-Off Template

Copy into PR / Release notes (auto-populated in `gate_sign_off.md`):

```text
Launcher smoke: ✅/❌ (log path/link)
Chat SSE v2 + resume: ✅/❌ (last_event_id tested)
Security strict (scripts/plugins/net): ✅/❌ (report link)
Memory (core + QFAC fallback): ✅/❌ (status snapshot)
HMR swap + audit: ✅/❌ (audit excerpt)
Agents API posture: ✅/❌ (off by default; enabled w/ token OK)
Spec→Tests & coverage no‑drop: ✅/❌ (coverage % vs baseline)
Policy/DP surfaced to clients: ✅/❌ (captured policy event)
```

---

## Script Output Schema

`gate_results.json` example shape:

```json
{
  "_meta": {"profile": "test", "ts": 1730000000.123, "all_passed": true},
  "launcher_smoke": {"ok": true, "manual": false, "duration_sec": 2.51, "details": {"services": ["aetherra_engine"], "missing": []}},
  "hmr_quiesce": {"ok": true, "manual": true, "details": {"manual_followup": true, "reason": "hmr_controller not registered"}}
}
```

`gate_sign_off.md` contains a table plus summary lines ready for PR insertion.

---

## FAQ

**Why separate automation vs manual?** HMR correctness depends on live inflight draining & audit semantics—safer to observe manually until strict gating matures.

**Can I fail build on manual gate?** Use `--strict-manual` flag in automation.

**How to add a new gate?** Extend `GATES` list in `tools/run_go_no_go_gates.py` with `(name, async_func)` returning `(ok, details)`.

---
Maintainers: Keep this file aligned with any gate evolution. Update residual risk table as mitigations land.

---

## Workflow Stability Toolkit (Parse & Migration)

These helper tools accelerate remediation of large numbers of failing `.aether` workflows without blocking main go/no‑go execution.

### 1. Parse-Only Fast Check (`--check`)

Added to `aether.py` to validate syntax/structure *without executing* side‑effects:

```powershell
python aether.py --check path\to\workflow.aether
```

Exit codes:

- 0: Parse OK
- 1: Structural / basic parse issue (line diagnostics printed)


Use in bulk (PowerShell example):

```powershell
Get-ChildItem -Recurse -Filter *.aether | ForEach-Object { python aether.py --check $_.FullName | Out-Null }
```

### 2. Failure Classifier (`tools/classify_aether_workflow_failures.py`)

Generates machine + human summaries of failing workflows, preferring `--check` first, then executing for runtime issues.


Artifacts:

- `workflow_failures.json` (includes per-file category & signature/risk data)
- `workflow_failures.md` (category table)


Key categories (heuristic): ParseError, SignatureMissing, RuntimeError, Timeout, NotImplemented, Other.

Sample run (limited to first 300 for speed):

```powershell
python tools\classify_aether_workflow_failures.py --limit 300 --output workflow_failures.json --markdown workflow_failures.md
```

CI: A lightweight GitHub Actions workflow (`workflow-classifier.yml`) runs a capped sample and uploads artifacts (no hard fail yet).

### 3. Legacy Syntax Migration (`tools/migrate_legacy_aether.py`)

Normalizes older forms (e.g., `intent:` → `goal:`) and cleans whitespace.


Dry-run with unified diffs:

```powershell
python tools\migrate_legacy_aether.py path\to\workflows --dry-run
```

Apply in-place:

```powershell
python tools\migrate_legacy_aether.py path\to\workflows --apply
```

Produces `migration_report.md` when multiple files are processed.

### Recommended Remediation Loop

1. Run classifier → capture top categories & counts.
2. Run migration (dry-run) → apply if high % convertible.
3. Re-run classifier → note delta in failure rate.
4. Bulk sign remaining unsigned (`tools/sign_aether.py file1.aether ...`).
5. Address remaining ParseError patterns (extend parser or add transforms).
6. Introduce suppression list only for intentional experimental scripts.


### Future Enhancements (Planned)

- Interpreter emits structured error codes (E_PARSE_UNBALANCED, E_RUNTIME_SERVICE_MISSING) for deterministic bucketing.
- Parallel classifier execution with concurrency limits.
- Historical trend snapshots under `.aetherra/workflow_classify_history/`.

---

## Structured Error Codes & Baselines (NEW)

The interpreter now supports structured machine-friendly reporting for both parse-only and full execution paths.

Flags:

```powershell
python aether.py --check --emit-error-code --json-status path\to\workflow.aether
```

Output additions:

- Stderr line: `AETHER_ERROR_CODE:<int>` (when `--emit-error-code` supplied)
- JSON line (stdout): `{ "ok": bool, "code": int, "code_name": "PARSE_ERROR", "file": "...", "phase": "parse|execute", "message": "...", "line": n }` when `--json-status`

Current code table:

| Code | Name                | Meaning                         |
| ---- | ------------------- | ------------------------------- |
| 0    | SUCCESS             | Parsed / executed successfully  |
| 1    | GENERIC_FAILURE     | Legacy generic failure          |
| 20   | PARSE_ERROR         | Structural / syntax issue       |
| 21   | RUNTIME_ERROR       | Execution failed (uncaught)     |
| 22   | SIGNATURE_ERROR     | (Reserved) signature validation |
| 23   | TIMEOUT_ERROR       | (Reserved) internal timeout     |
| 24   | UNSUPPORTED_FEATURE | Feature not yet implemented     |
| 25   | VALIDATION_ERROR    | Semantic / pre-exec validation  |
| 26   | IO_ERROR            | File read / access issue        |
| 27   | INTERNAL_ERROR      | Unexpected interpreter crash    |

### Updated Classifier Capabilities

`tools/classify_aether_workflow_failures.py` now:

- Requests structured JSON/ codes automatically.
- Falls back to heuristics if interpreter lacks flags.
- Supports concurrency: `--jobs N` (default = CPU count).
- Persists historical snapshots: `--history-dir .aetherra/workflow_history` (default).
- Generates rolling `trends.json` (last 20 snapshots) for regression tracking.

Example (parallel run with history):

```powershell
python tools\classify_aether_workflow_failures.py --jobs 8 --output workflow_failures.json --markdown workflow_failures.md
```

Historical artifacts:

```text
.aetherra/workflow_history/
  20250912T101500_classification.json
  20250912T111500_classification.json
  trends.json
```

`trends.json` excerpt:

```json
[
  {"file": "20250912T101500_classification.json", "timestamp": "2025-09-12T10:15:00Z", "failed": 1820, "total": 2700},
  {"file": "20250912T111500_classification.json", "timestamp": "2025-09-12T11:15:10Z", "failed": 1755, "total": 2700}
]
```

### Parse Baseline Script

`tools/generate_parse_baseline.py` provides a fast snapshot of parse health only:

```powershell
python tools\generate_parse_baseline.py --output parse_baseline.json
```

Produces:

```json
{
  "timestamp": "...Z",
  "total": 2700,
  "by_code": {"SUCCESS": 900, "PARSE_ERROR": 1800},
  "failure_rate": 0.6667,
  "files": [ {"path": "...", "code_name": "PARSE_ERROR", "line": 12, "message": "Parse error (assignment)..." } ]
}
```

### CI Integration

Two workflows:

- `workflow-classifier.yml` (sample execution classification artifacts)
- `workflow-parse-baseline.yml` (full parse baseline artifact)

Use artifact diffing in future to hard-fail on regression deltas (e.g., PARSE_ERROR count increase > threshold).

### Next Steps (Recommended)

- Add suppression list for intentional experimental scripts.
- Introduce semantic validation (e.g., unknown function names → VALIDATION_ERROR).
- Gate PRs on *non-increasing* PARSE_ERROR count after stabilization.

---

---

## Semantic Validation, Suppression & Regression Gate (NEW)

Recent hardening adds pre-execution semantic checks, deterministic failure fingerprints, opt-in suppression, and a parse regression gate.

### Semantic Validation (VALIDATION_ERROR / Code 25)

During `--check` the interpreter now detects unknown function calls in:

- Standalone calls: `foo(bar)`
- Assignment expressions: `x: foo(bar)`
- Memory-prefixed calls: `memory: foo(bar)`

If the function name is not a recognized built-in, parse still structurally succeeds but the exit status becomes `VALIDATION_ERROR` with line + message (first unknown only). This separates structural syntax correctness from semantic readiness.

Why: Prevents false "SUCCESS" baselines where workflows would later fail at runtime due to missing functions.

### Failure Fingerprints

Classifier computes a short stable hash (first 16 hex chars of SHA-256) over:

`code_name | line | first_error_message_line`

Example (conceptual):

```text
PARSE_ERROR|12|Parse error (assignment) line 12: goal
 -> fingerprint: a1b2c3d4e5f67890
```

Fingerprints enable de-duplication and persistent suppression without path coupling.

### Suppression List

Optional file: `.aetherra/workflow_suppressions.txt`

Format: one fingerprint per line. Lines starting with `#` ignored; inline comments allowed after whitespace.

Example:

```text
# Experimental quantum workflows under redesign
a1b2c3d4e5f67890  # deprecated goal syntax
deadbeefcafe1234  # awaiting plugin migration
```

Suppressed failures are recategorized as `Suppressed-<OriginalCategory>` and counted separately (`suppressed_failures` field in JSON summary). They still surface in artifacts but can be excluded from gating decisions.

Guidelines:

1. Only suppress when a remediation plan + owner exist.
2. Remove entry immediately after fix merges.
3. Avoid mass suppression (anti-signal). Prefer targeted migrations.

### Regression Gate Script

`tools/parse_baseline_regression_gate.py` compares a new parse baseline vs a reference and fails if both thresholds are exceeded for a targeted code (`PARSE_ERROR`, `VALIDATION_ERROR`):

- Absolute increase > `--abs-threshold` (default 5) AND
- Relative increase > `--rel-threshold` (default 0.10 = 10%)

Usage:

```powershell
python tools\parse_baseline_regression_gate.py --new parse_baseline.json --ref main_parse_baseline.json
```

Sample output:

```json
{
  "ok": false,
  "timestamp": "2025-09-13T10:15:22.123456+00:00",
  "new_counts": {"PARSE_ERROR": 1810, "VALIDATION_ERROR": 42},
  "ref_counts": {"PARSE_ERROR": 1800, "VALIDATION_ERROR": 30},
  "abs_threshold": 5,
  "rel_threshold": 0.1,
  "regressions": [
    {"code": "VALIDATION_ERROR", "old": 30, "new": 42, "delta": 12, "relative_increase": 0.4}
  ]
}
```

Exit codes:

| Code | Meaning                         |
| ---- | ------------------------------- |
| 0    | No regression detected          |
| 1    | Regression (threshold exceeded) |
| 2    | Usage / input error             |

Recommended CI Flow:

1. Generate new baseline (parse-only) → `parse_baseline.json`.
2. Download/reference main branch baseline (artifact cache) → `ref.json`.
3. Run regression gate script.
4. Fail PR if exit code = 1 (after stabilization period).

### Timezone-Aware Timestamps

All new structured outputs use `datetime.now(UTC).isoformat()` eliminating naive `utcnow()` usage for clarity and future DST-safety in analytics.

### Roadmap Additions (Potential)

- Auto-generate suppression template for top N fingerprints lacking coverage.
- Fingerprint aging (auto-expire entries > X days old).
- Enrich semantic validation (unknown variables, reserved keyword misuse).
- Hard fail CI on introduction of any new `INTERNAL_ERROR` code immediately.

---
