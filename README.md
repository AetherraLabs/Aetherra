<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
# Aetherra

> AI-native development environment (Alpha). Version: **0.1.0-alpha.2**

![Status](https://img.shields.io/badge/Status-ALPHA-orange)
![Version](https://img.shields.io/badge/Version-0.1.0--alpha.2-0891b2)
![License](https://img.shields.io/badge/License-GPLv3-0891b2)
![Language](https://img.shields.io/badge/Language-Python%20%2B%20Aetherra-8b5cf6)
![Responsible AI](https://img.shields.io/badge/Responsible%20AI-Policies%20Published-22c55e)

Aetherra pairs a lightweight Hub (APIs + metrics) with the Lyrixa AI assistant, pluggable memory systems, intent‑driven workflow language (`.aether`), and observability surfaces designed from day one. This repository is an **early alpha**: interfaces and metrics may change without deprecation. See `docs/ALPHA_READINESS.md` for current scope and limitations.

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

```powershell
# Clone
git clone https://github.com/AetherraLabs/Aetherra.git
cd "Aetherra"

# (Optional) create virtual env
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install (placeholder – adjust when pyproject/req file finalized)
pip install -r requirements.txt

# Run Hub (headless)
python aetherra_hub_server.py

# Enable chat + streaming (temporary shell scope)
$env:AETHERRA_AI_API_ENABLED='1'
$env:AETHERRA_AI_API_STREAM='1'

# Call a chat endpoint
python - <<'PY'
import requests;print(requests.post('http://localhost:3017/api/lyrixa/chat',json={'message':'hello alpha'}).json())
PY
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
