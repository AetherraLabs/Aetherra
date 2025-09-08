<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
# Aetherra

> AI-native development environment (Beta). Version: **0.5.0-beta.0**

![Status](https://img.shields.io/badge/Status-BETA-blue)
![Version](https://img.shields.io/badge/Version-0.5.0--beta.0-0891b2)
![License](https://img.shields.io/badge/License-GPLv3-0891b2)
![Language](https://img.shields.io/badge/Language-Python%20%2B%20Aetherra-8b5cf6)
![Responsible AI](https://img.shields.io/badge/Responsible%20AI-Policies%20Published-22c55e)
![Aether Script Signatures CI](https://github.com/AetherraLabs/Aetherra/actions/workflows/aether-verify-signatures.yml/badge.svg)
![Aether Risk](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/AetherraLabs/Aetherra/main/badge/aether_risk.json)

Aetherra pairs a lightweight Hub (APIs + metrics) with the Lyrixa AI assistant, pluggable memory systems, an intent‑driven workflow language (`.aether`), and first-class observability. Now in **public Beta**: core surfaces are stabilizing while certain subsystems (trainer persistence, federation) remain in-progress. See `BETA_READINESS_REPORT.md` for evidence and `ROADMAP.md` for trajectory.

## What Makes Aetherra Unique

| Dimension              | Aetherra Approach                                | Why It Matters                      |
| ---------------------- | ------------------------------------------------ | ----------------------------------- |
| Integrity              | Signed `.aether` workflows (plugins next)        | Trust & audit trail for automation  |
| Memory                 | Persistent + quantum-augmented (QFAC) layers     | Rich recall & experimentation       |
| Observability          | Prometheus-first metrics for every subsystem     | Debug & capacity planning early     |
| Resilience             | Deterministic fallbacks (offline/local provider) | Predictable under outage/quota      |
| Capability Enforcement | Runtime reinforcement of intelligence flags      | Prevents silent regression          |
| Lifecycle Tests        | 32 capability tests incl. plugin reload          | Evidence-backed stability           |
| Extensibility          | Plugin chain executor (sequential today)         | Composable augmentation surface     |
| Governance             | License policy & ownership memory                | Attribution & compliance continuity |

Quick links: [`INSTALL.md`](INSTALL.md) · [`ROADMAP.md`](ROADMAP.md) · [`CHANGELOG.md`](CHANGELOG.md) · [`SECURITY.md`](SECURITY.md) · [`BETA_READINESS_REPORT.md`](BETA_READINESS_REPORT.md) · [`Developer Onboarding`](docs/DEVELOPER_ONBOARDING.md)

## Table of Contents

1. Overview
1. Core Capabilities (Alpha)
1. Architecture Snapshot
1. Quick Start
1. Metrics & Observability
1. Alpha Limitations & Road to Beta
1. Workflow Language (`.aether`)
1. Development & Tests
1. Contributing & Community
1. License & Notices

---
\n## 1. Overview


**Goal:** Provide an AI-native development surface where code, memory, evaluation, and intelligent assistance unify behind explicit APIs and transparent metrics.

Core design principles:

- Explicit feature gating via environment flags (secure by default)
- Deterministic fallbacks when upstream models are unavailable
- Early instrumentation (Prometheus-first) for every new subsystem
- Human-readable workflow & memory artifacts (auditable evolution)

---
\n## 2. Core Capabilities (Alpha)

Implemented and test-covered today:

| Area                        | Capability                                      | Notes                                               |
| --------------------------- | ----------------------------------------------- | --------------------------------------------------- |
| Chat                        | `/api/lyrixa/chat`, fallback offline generation | Streaming & upstream gated by env flags             |
| Memory Narratives           | `/api/memory/narratives`                        | Stub narrative list (expands in beta)               |
| Trainer/Eval (In‑Memory)    | `/api/trainer/*`                                | Simulated jobs + evals; lifecycle + metrics         |
| Quantum / Coherence Signals | `/metrics`                                      | Gauges & counters for quantum/coherence model stubs |
| Per-Principal Metrics       | Prometheus labels                               | Per-stream gauge & latency surfaces                 |
| Workflow Language           | `.aether` signed workflows                      | Signing & static verification tasks                 |
| Ownership Memory            | Seed + recall tests                             | Ensures identity & attribution continuity           |
| Safety Surface              | Policy snapshot + redactions                    | Headers + DP/flag disclosure                        |

See CHANGELOG for incremental additions.

---
\n## 3. Architecture Snapshot

```text
Hub (Flask) ──► API Routes (chat, trainer, memory, telemetry)
            └─► Metrics Export (/metrics, Prometheus format)

Lyrixa Core ─► Intelligence facade (multi-provider fallback)
            └─► Memory Systems (persistent + quantum/QFAC optional)

Trainer/Eval (alpha stub) ─► In‑memory queues + background simulation

Workflow Layer ─► Signed `.aether` specs → execution / validation tasks

Observability ─► aetherra_trainer_*, chat/per-principal, quantum/coherence series
```

Import conventions: use `aetherra_*` / `lyrixa_*` modules (see `docs/import_map.md`).

---
\n## 4. Quick Start

Prerequisites: Python 3.11+ (recommended), virtual environment activated.

Clone the repository:

`git clone https://github.com/AetherraLabs/Aetherra.git`

```powershell
# Clone
git clone https://github.com/AetherraLabs/Aetherra.git
cd "Aetherra"

# (Optional) create virtual env
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install (placeholder – adjust when pyproject/req file finalized)
pip install -r requirements.txt

# Enable chat + streaming (temporary shell scope) THEN run hub (default port 3001)
$env:AETHERRA_AI_API_ENABLED='1'
$env:AETHERRA_AI_API_STREAM='1'
python aetherra_hub_server.py

# In a second PowerShell, minimal chat call (Invoke-RestMethod handles JSON nicely)
Invoke-RestMethod -Method Post -Uri 'http://localhost:3001/api/lyrixa/chat' -ContentType 'application/json' -Body '{"message":"hello alpha"}'

# (Alternative quick inline Python if you prefer):
python - <<'PY'
import requests;print(requests.post('http://localhost:3001/api/lyrixa/chat',json={'message':'hello alpha'}).json())
PY
```

Ultra-Quick (one command, auto-env + run + sample request):

```powershell
python tools/dev_quickstart.py --auto-chat
```

This helper will:

1. Export chat env flags (if not already set)
2. Start the Hub on port 3001
3. Perform a test POST to `/api/lyrixa/chat` and print the JSON response
4. Remind you how to stream or view metrics

Expected minimal JSON response shape (fields may evolve in alpha):

```json
{
    "ok": true,
    "result": {
        "response": "hello alpha (offline stub)",
        "session_id": "...",
        "timestamp": "2025-09-06T12:34:56.789012",
        "relevant_memories_count": 0,
        "confidence_breakdown": {
            "model": 0.5,
            "grounding": 0.5,
            "coherence": 0.5,
            "safety": 1.0
        }
    }
}
```

Basic streaming (Server-Sent Events) when `AETHERRA_AI_API_STREAM=1`:

```powershell
$env:AETHERRA_AI_API_ENABLED='1'; $env:AETHERRA_AI_API_STREAM='1'
python aetherra_hub_server.py

# In another shell use curl to watch events (Windows curl supports --no-buffer)
curl --no-buffer -X POST -H "Content-Type: application/json" ^
    http://localhost:3001/api/ai/stream ^
    -d '{"message":"test streaming"}'
```

Docker quick start (build dev image, run hub, probe chat + metrics):

```powershell
./tools/docker_quickstart.ps1
```

Minimal docker-compose snippet (future refinement) — save as `docker-compose.yml`:


```yaml
services:
    aetherra:
        build:
            context: .
            target: development
        image: aetherra-dev:local
        environment:
            AETHERRA_AI_API_ENABLED: "1"
            AETHERRA_AI_API_STREAM: "1"
        ports:
            - "3001:3001"
        command: ["python", "aetherra_hub_server.py"]
```

### Demo Endpoint Shapes (Beta Snapshot)

Representative minimal responses (fields may expand):

Chat (`POST /api/lyrixa/chat`):

```json
{"ok": true, "result": {"response": "hello beta (offline stub)", "session_id": "...", "timestamp": "2025-09-07T00:00:00Z"}}
```

Memory Narratives (`GET /api/memory/narratives`):

```json
{"ok": true, "narratives": [{"id":"seed","title":"Seed Narrative","summary":"Narrative stub"}]}
```

Trainer Jobs (`POST /api/trainer/jobs` then `GET /api/trainer/jobs`):

```json
{"ok": true, "job_id": "train_20250907_123456_ab12cd34"}
```

Metrics (excerpt `GET /metrics`):

```text
aetherra_trainer_enabled 0
aetherra_trainer_jobs_total 0
```

Trainer/eval demo (ephemeral):

```powershell
$env:AETHERRA_TRAINER_ENABLED='1'
python - <<'PY'
import requests,time;port=3023
j=requests.post(f'http://localhost:{port}/api/trainer/jobs',json={'task':'sft'}).json();print(j)
time.sleep(1)
print(requests.get(f'http://localhost:{port}/api/trainer/jobs').json())
print('metrics sample:');print('\n'.join(requests.get(f'http://localhost:{port}/metrics').text.splitlines()[:12]))
PY
```

More environment flags and safe defaults: `docs/ALPHA_READINESS.md`.

### Quality Gates & Coverage (New Flags)

| Variable                | Purpose                                                            | Default                   |
| ----------------------- | ------------------------------------------------------------------ | ------------------------- |
| GENERATE_PR_DESCRIPTION | Emit `pr_description.md` (or custom path) summarizing gate results | 0                         |
| PR_DESCRIPTION_PATH     | Output path for generated PR description                           | pr_description.md         |
| COVERAGE_REPORT_JSON    | Path for structured gate report JSON                               | coverage_gate_report.json |
| COVERAGE_FILE_RETENTION | Max per-file snapshot count (`audit/coverage_delta/`)              | 30                        |
| COVERAGE_PRUNE_ORPHANS  | Remove legacy root `coverage.json` when snapshots exist            | 1                         |
| TEST_SELECTION          | Enable heuristic test subset selection (Phase 1)                   | 1                         |
| TEST_SELECTION_MIN_CONF | Min confidence for adopting subset                                 | 0.8                       |

Structured gate report fields (schema_version=1):

- coverage, previous, delta, min_threshold, drop, updated_baseline
- gating_reasons[] (code, severity, message)
- selection (strategy, candidates, confidence, fallback, reason)
- file_deltas[] (path, before, after, delta, changed)
- future (enforce_branch_coverage, enforce_statement_coverage)


---

## 5. Metrics & Observability

Prometheus text endpoint: `/metrics` (Hub).

Key series (alpha):

- `aetherra_trainer_enabled`, `aetherra_trainer_jobs_total`, `aetherra_trainer_evals_total`, `aetherra_trainer_eval_runs_total`, `aetherra_trainer_eval_last_score`
- Chat per-principal gauges & duration histograms
- Quantum/coherence gauges (simulation values unless hardware attached)

Export is intentionally stable in naming, but labels/value semantics may evolve before beta.

---

## 6. Alpha Limitations & Road to Beta

Summary (full detail: `docs/ALPHA_READINESS.md`):

| Aspect             | Current Limitation               | Planned (Beta)                              |
| ------------------ | -------------------------------- | ------------------------------------------- |
| Trainer/Eval       | In-memory only                   | Persistent store + cancel/retry             |
| Evaluation Scoring | Deterministic placeholder (0.9)  | Pluggable metrics + dataset registry        |
| Federation         | Announce/sync return 501 (stubs) | Secure peer handshake + signing enforcement |
| Narratives         | Static stub list                 | Query + enrichment pipeline                 |
| Model Providers    | Fallback mock when unreachable   | Explicit provider status endpoint           |
| Access Control     | No multi-tenant isolation        | Token / principal level quotas & gating     |

---

## 7. Workflow Language (`.aether`)

Workflows define goals, triggers, memory operations, AI tasks and actions. Files are cryptographically signed and can be statically verified. See sample workflows under `workflows/` and signing utility (`tools/sign_aether.py`).

Minimal example:

```aether
goal: nightly memory digest
think "summarize recent memory events"
run trainer if metric.trainer_backlog < 5
export report to path="reports/digest.txt"
```

---

## 8. Development & Tests

Run capability suite (core behaviors + metrics assertions):

```powershell
pytest -q -o addopts= tests/capabilities
```

Other helpful tasks (VS Code → Run Task): *Verify Aetherra OS (Headless Smoke)*, *Update System Index*, *Quality Gates*.

### Continuous Integration (Lyrixa Health Gate)

For pipelines, use the lightweight health script to ensure critical Lyrixa systems (hub + basic chat) are up while allowing non‑critical degradation (e.g., empty registry) without failing the build:

```powershell
./tools/ci_lyrixa_check.ps1
```

Behavior:

- Exit 0: All critical systems pass (or only WARN conditions)
- Exit 1: Critical failure (Hub unreachable or basic chat unusable)


Integrate into GitHub Actions (excerpt):

```yaml
    - name: Lyrixa health check
        shell: pwsh
        run: ./tools/ci_lyrixa_check.ps1
```

The script internally runs `tools/lyrixa_diagnostics.py --skip-advanced` and normalizes exit codes.

---

## 9. Contributing & Community

We welcome focused, test-backed contributions aligned with alpha scope.

1. Open an issue tagged `proposal` or `alpha-feedback`.
2. Keep PRs small; include capability / or metrics delta tests.
3. Follow coding & policy guidelines (see `CODE_OF_CONDUCT.md`, `GOVERNANCE.md`).

Useful docs:

- Architecture: `docs/PROJECT_OVERVIEW.md`
- Safe defaults / flags: `docs/ALPHA_READINESS.md`
- Coverage policy: `docs/COVERAGE_POLICY.md`
- Release process: `docs/RELEASE_PROCESS.md`
- License policy & enforcement: `LICENSE_POLICY.md`
- QFAC modes (quantum memory): `docs/QFAC_MODE_GUIDE.md`
- Changelog: `CHANGELOG.md`
- Override pruning (dry-run): `python tools/prune_license_overrides.py --dry-run` (requires fresh `licenses_report.json`)

Star the repo and join discussions to influence beta priorities.

---

## 10. License & Notices

Licensed under **GPL-3.0-or-later** (see `LICENSE`). All new contributions must retain SPDX headers where present.

Key notices:

- AI outputs may be incomplete or imprecise; review before production use.
- Some features (Discord bot, internal monitoring suites) are intentionally excluded from public builds.
- Trademarks and branding remain property of their respective owners.

Standard disclaimer: Aetherra is provided "AS IS" without warranty (see GPLv3
Sections 15–16). This README is informational and not legal advice. Aetherra is
developed and stewarded by **Aetherra Labs and Contributors**. For attribution
transparency see `NOTICE`; for dependency/license analysis see
`LEGAL_COMPLIANCE.md`.

---
© 2025 Aetherra Labs and Contributors
