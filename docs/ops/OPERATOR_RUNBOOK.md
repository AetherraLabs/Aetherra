# Aetherra Operator Runbook (Alpha)

This runbook summarizes day-2 operations for Aetherra during the Alpha window.

## Locations: snapshots, DLQ, HMR audit

- Kernel tasks snapshot: `.aetherra/kernel_tasks.json` (override with `AETHERRA_KERNEL_TASKS_PATH`)
- Hub chat DLQ (fallback): `hub_chat_dlq.jsonl` in the working directory
- Security ledger (if enabled): path from `AETHERRA_SECURITY_LEDGER_PATH` (default `.aetherra/security_ledger.jsonl`)
- HMR Audit (Hot Module Reload): `.aetherra/hmr_audit.jsonl` (override via `AETHERRA_HMR_AUDIT_PATH`)

## 3‑command triage


- Health: curl <http://localhost:3001/health>
- Stats: curl <http://localhost:3001/api/stats> | jq .
- Metrics: curl <http://localhost:3001/metrics> | head -n 50

## Restart procedures

- Graceful restart (preferred):
  1) Request kernel drain to flush inflight work
  2) Stop the launcher or process manager
  3) Start the launcher again

- Emergency restart (only if hung):
  1) Terminate the process (SIGKILL/Task Manager)
  2) Start the launcher again

Notes:

- Graceful path minimizes DLQ growth and incomplete tasks.
- If you use the Hub control plane endpoints, ensure `AETHERRA_HUB_CONTROL_TOKEN` is set; then POST to `/api/kernel/control/*` as needed.

## HMR (Hot Module Reload) Phase‑2: Safe reload procedures

### Night cycle scheduling (TZ safety)

- In prod/staging, night‑cycle jobs are blocked unless a timezone is explicitly set.
- Set one of:
  - `$env:AETHERRA_NIGHT_TZ = "UTC"`  # or any IANA TZ like "America/Los_Angeles"
  - `$env:AETHERRA_NIGHT_UTC = "1"`   # pin scheduling to UTC
- Optional per‑service staggering: `$env:AETHERRA_NIGHT_STAGGER_MAX_SEC = "900"`  # up to 15m jitter inside window
- Window: `$env:AETHERRA_NIGHT_START_HOUR`/`$env:AETHERRA_NIGHT_END_HOUR` (defaults 2–4)


Use HMR to swap components in‑process without a full restart. Phase‑2 adds source gating, in‑flight drain, and audit logging.

Prerequisites:

- Enable HMR: `$env:AETHERRA_HMR_ENABLED = "1"`
- Gate sources (required in Phase‑2):
  - `$env:AETHERRA_HMR_ALLOWED_SOURCES = "Aetherra.lyrixa, Aetherra/aetherra_core, plugins/core"`
  - Accepts module names or path prefixes (comma‑separated). Only matches are eligible for reload.
- Optional audit rotation:
  - `$env:AETHERRA_HMR_AUDIT_PATH = ".aetherra/hmr_audit.jsonl"`
  - `$env:AETHERRA_HMR_AUDIT_MAX_BYTES = "5242880"  # 5 MiB`
  - `$env:AETHERRA_HMR_AUDIT_MAX_BACKUPS = "3"`

Recommended sequence (engine/adapters/chat):

1. Quiesce target work

- Prefer draining queues (use `/api/kernel/control/drain` if exposed), or schedule during night cycle.

1. Trigger reload task

- HMR is initiated inside the process via a kernel task (`{"type":"hmr_reload", "data": {"target":"engine|adapter:memory|adapter:plugin|lyrixa_chat", "source":"<module or path>", "mode":"safe|force"}}`).
- See code example in `docs/AETHERRA_KERNEL_SYSTEM.md` (HMR usage examples).

1. Verify swap

- Check Hub `/metrics` for HMR counters and kernel in‑flight gauges.
- Tail the audit file for `HMR_SWAP` (and ensure no `post_swap_failed`).

1. Rollback if needed

- A failed probe or post‑swap emits `HMR_ROLLBACK`; investigate audit and logs, then retry.

Allowed‑sources examples:

- Modules: `Aetherra.lyrixa`, `my_project.engine_impl`
- Paths: `Aetherra/aetherra_core/engine`, `plugins/core/`

Audit quick commands (PowerShell):

- Tail audit: `Get-Content $env:AETHERRA_HMR_AUDIT_PATH -Tail 20`
- Filter last events: `Get-Content $env:AETHERRA_HMR_AUDIT_PATH -Tail 200 | Where-Object { $_ -match 'HMR_(PREPARE|SWAP|ROLLBACK)' }`
- Parse last line as JSON: `Get-Content $env:AETHERRA_HMR_AUDIT_PATH -Tail 1 | ConvertFrom-Json | Format-List`

## Safe shutdown

- Graceful shutdown:
  - Ensure queues are drained and `/api/stats` shows 0 inflight
  - Stop launcher process (CTRL+C) or service manager stop

- Emergency shutdown:
  - Use process kill; on next boot check DLQ and audit logs

## Rolling diagnostics

- HTTP checks:
  - GET /health
  - GET /api/stats
  - GET /metrics (Prometheus text)

- Kernel and Agents snapshots:
  - GET /api/kernel/status
  - GET /api/agents/metrics

## Policy snapshot & differential privacy flags

- Response header `X-Aetherra-Policy` carries the current policy snapshot
- SSE policy event includes the same snapshot
- DP toggles surfaced when set:
  - `AETHERRA_DP_ENABLED=1`
  - `AETHERRA_DP_EPSILON=<float>`

## Known environment flags (ops‑relevant)

- AETHERRA_AI_API_REQUIRE_TOKEN=1
- AETHERRA_AI_API_TOKEN (or AETHERRA_HUB_CONTROL_TOKEN)
- AETHERRA_KERNEL_DLQ=1
- AETHERRA_SECURITY_LEDGER=1; AETHERRA_SECURITY_LEDGER_PATH
- AETHERRA_HMR_AUDIT_PATH; AETHERRA_HMR_AUDIT_MAX_BYTES; AETHERRA_HMR_AUDIT_MAX_BACKUPS
- AETHERRA_QFAC_MODE=classical|quantum
- AETHERRA_DP_ENABLED; AETHERRA_DP_EPSILON

## Quick links

- Chat system: docs/AETHERRA_CHAT_SYSTEM.md
- Kernel system: docs/AETHERRA_KERNEL_SYSTEM.md
- Memory system: docs/AETHERRA_MEMORY_SYSTEM.md
- Hub control token: docs/ops/HUB_CONTROL_TOKEN.md

## Run sample workflows (.aether)

Use the Aether CLI to execute the signed sample workflows.

- From repo root (Windows PowerShell):

```powershell
# Parallel branches demo
python .\aether.py .\workflows\parallel_workflow_demo.aether

# On-error fallback chain demo
python .\aether.py .\workflows\on_error_chain_demo.aether

# Plugin chain demo
python .\aether.py .\workflows\plugin_chain_demo.aether
```

Notes:

- If `AETHERRA_AI_API_REQUIRE_TOKEN=1` is set for Hub APIs, CLI workflows still run locally via the Aether interpreter.
- Outputs may reference memory or logs; check recent logs and `/api/stats` if workflows touch services.

## Re‑sign and verify workflows

After editing any `.aether` file, re‑sign it and run strict verification:

```powershell
# Re‑sign the modified file (embeds HMAC signature)
python .\tools\sign_aether.py .\workflows\parallel_workflow_demo.aether

# Verify all .aether scripts (strict signatures + static risk)
python .\tools\verify_aether_scripts.py --root . --output aether_static_report.md --strict
```

Troubleshooting:

- Signature mismatch: re‑run the sign step on the edited file.
- Static risk > 0: open `aether_static_report.md` and address the flagged findings, then re‑verify.
- Gate runs in CI: use the “Quality Gates (Tests + Coverage No‑Drop)” task to exercise the same checks locally.

## Enable auto‑signing Git hook

Install the local hook so edits to `.aether` files are auto‑signed on commit:

```powershell
# One‑time per clone
git config core.hooksPath .githooks

# Optional: enforce strict verify during commit
$env:PRECOMMIT_AETHER_VERIFY = "1"
```

Notes:

- The hook signs any staged `.aether` files and re‑adds them to the index.
- With `PRECOMMIT_AETHER_VERIFY=1`, a strict verification runs and blocks the commit on failure.

## VS Code tasks shortcuts

From the VS Code “Run Task…” menu you can run:

- Run workflow: Parallel/On‑error/Plugin chain demos
- Aether: Re‑sign edited workflows
- Aether Verify (Strict Signatures)
- Run all sample workflows (sequence)
- Aether: Re‑sign and Strict verify (sequence)

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
