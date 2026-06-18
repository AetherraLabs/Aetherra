<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Aetherra

> A safety-first cognitive operating layer for agentic AI systems.

[![License](https://img.shields.io/badge/License-GPLv3-0891b2)](LICENSE)
![Language](https://img.shields.io/badge/Language-Python%20%2B%20Aetherra-8b5cf6)
![Status](https://img.shields.io/badge/Status-Alpha%20Foundation-2563eb)
![Safety](https://img.shields.io/badge/Safety-Guardian%20Mediated-22c55e)

Aetherra is an experimental AI operating layer built around modular systems,
auditable decisions, persistent memory, service orchestration, and controlled
self-improvement. It is currently in an Alpha/Foundation phase: the focus is
not broad autonomy, but making each core system functional, bounded, testable,
and safe before expanding capability.

The project direction is deliberately conservative:

1. Observe before acting.
2. Propose before modifying.
3. Route privileged actions through Guardian and Security.
4. Record decisions and outcomes for review.
5. Keep autonomous execution disabled until the safety architecture is ready.

## Current Foundation Status

| System | Status | Notes |
| --- | --- | --- |
| Security | Functional foundation complete | Capability checks, audit ledger, signing, sandbox and policy surfaces. |
| Guardian | Functional foundation complete | Intent evaluation, risk assessment, approval, containment, audit integration, performance policy. |
| Homeostasis | Functional foundation complete | Observation, diagnosis, recommendations, Guardian-mediated controlled actions. |
| Self-Improvement | Functional Alpha/Foundation complete | Proposal-only loop, Guardian-mediated execution delegation, bounded learning outcomes. |
| Other systems | In progress | Systems are being completed one at a time to the same standard. |

See the system documents in [`docs/`](docs/) for current implementation status.

## What Aetherra Is

Aetherra is not a single chatbot, plugin runner, or automation script. It is a
layered runtime for AI-native operations:

- **Aetherra Kernel**: service coordination, event routing, and runtime lifecycle.
- **Aetherra Hub**: local APIs, metrics, and control-plane endpoints.
- **Lyrixa**: assistant and interface layer.
- **Security System**: capability, sandbox, signing, audit, and policy controls.
- **Guardian System**: intent evaluation and risk mediation for privileged actions.
- **Homeostasis System**: health observation, diagnosis, and controlled recovery recommendations.
- **Self-Improvement System**: safe proposal generation and outcome learning without direct mutation.
- **Aether Script**: intent-oriented workflow language for controlled automation.
- **Memory Systems**: persistent and experimental memory layers.
- **Plugin System**: extensibility with policy and capability boundaries.

## Safety Model

Aetherra is designed for powerful behavior, so the foundation assumes privileged
actions are dangerous until proven safe.

Core safety principles:

- Self-Improvement does not directly modify the system.
- Guardian evaluates privileged intent before execution.
- Security enforces capabilities, sandboxing, signing, and audit policy.
- Homeostasis recommends before it acts.
- Controlled execution paths must support rollback or explicit approval.
- Downstream errors and execution payloads are minimized before reaching clients.
- Generated observations, results, and metadata are bounded before persistence.

## Repository State

This repository is under active cleanup. Some generated artifacts, historical
reports, packaged builds, local databases, and legacy root-level scripts are
still present in the tracked tree. They are being handled deliberately to avoid
removing useful project history or breaking current workflows.

Cleanup tracking:

- [`docs/REPOSITORY_CLEANUP_PLAN.md`](docs/REPOSITORY_CLEANUP_PLAN.md)
- [`docs/AETHERRA_SECURITY_SYSTEM.md`](docs/AETHERRA_SECURITY_SYSTEM.md)
- [`docs/AETHERRA_GUARDIAN_SYSTEM.md`](docs/AETHERRA_GUARDIAN_SYSTEM.md)
- [`docs/AETHERRA_HOMEOSTASIS_SYSTEM.md`](docs/AETHERRA_HOMEOSTASIS_SYSTEM.md)
- [`docs/AETHERRA_SELF-IMPROVEMENT_SYSTEM.md`](docs/AETHERRA_SELF-IMPROVEMENT_SYSTEM.md)

## Quick Start

Requirements:

- Python 3.11+
- Git
- A virtual environment is strongly recommended

Install dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-ci.lock
```

Run focused system tests:

```bash
python -m pytest -q -o addopts= \
  tests/capabilities/test_self_improvement_metrics.py \
  tests/capabilities/test_self_maintenance_services.py \
  tests/unit/test_hub_self_improvement_guardian.py \
  tests/unit/test_optimization_executor_guardian.py \
  tests/unit/test_selfinc_integration_guardian.py \
  tests/unit/test_selfinc_proposal_consumer.py
```

Run a basic smoke check:

```bash
python tools/os_smoke.py
```

Start the local Hub:

```bash
python tools/run_hub_ai_api.py --port 3001
```

Then inspect:

```bash
curl http://localhost:3001/api/health
curl http://localhost:3001/metrics
```

## Important Paths

| Path | Purpose |
| --- | --- |
| [`Aetherra/`](Aetherra/) | Primary package and runtime systems. |
| [`aetherra_hub/`](aetherra_hub/) | Hub API blueprints and local service surfaces. |
| [`docs/`](docs/) | System documentation and implementation status. |
| [`tests/`](tests/) | Unit, capability, integration, and acceptance tests. |
| [`tools/`](tools/) | Verification, smoke, maintenance, and developer utilities. |
| [`requirements/`](requirements/) | Additional dependency inputs. |
| [`scripts/`](scripts/) | Operational and maintenance scripts. |

## Development Notes

- Keep changes scoped to the system being completed.
- Do not add direct autonomous mutation paths.
- Prefer bounded structured data over raw payload persistence.
- Add tests for safety boundaries, not just happy paths.
- Keep generated logs, databases, build outputs, and local state out of commits.
- Use system docs in `docs/` as the source of truth for system completion.

## License

Aetherra is licensed under the GNU General Public License v3.0 or later. See
[`LICENSE`](LICENSE), [`NOTICE`](NOTICE), and [`COPYRIGHT`](COPYRIGHT).
