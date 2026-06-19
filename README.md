<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Aetherra

> A safety-first cognitive operating layer for agentic AI systems.

[![License](https://img.shields.io/badge/License-GPLv3-0891b2)](LICENSE)
![Version](https://img.shields.io/badge/Version-0.5.0--beta.0-0f766e)
![Language](https://img.shields.io/badge/Language-Python%20%2B%20Aetherra-8b5cf6)
![Status](https://img.shields.io/badge/Status-Alpha%20Foundation-2563eb)
![Safety](https://img.shields.io/badge/Safety-Guardian%20Mediated-22c55e)

Version: **0.5.0-beta.0**

Aetherra is an experimental AI operating layer for modular agents, persistent
memory, policy-mediated execution, auditable decisions, and controlled
self-improvement.

The project is in an Alpha/Foundation hardening phase. The current goal is not
unbounded autonomy. The current goal is to complete each core system until it is
functional, testable, bounded, and safe enough to support later alpha testing.

## Maturity and Safety Notice

Aetherra is not production-ready autonomous infrastructure. Treat it as an
active alpha-stage research and engineering codebase.

- Run it in a reviewed development environment.
- Keep Guardian and Security enforcement enabled for privileged paths.
- Do not connect it to sensitive systems without explicit review.
- Expect some systems to be functional foundations rather than final products.
- Prefer manual approval, rollback plans, and audit review for risky actions.

## Current Priorities

1. Keep privileged actions mediated by Guardian and Security.
2. Prefer observation and proposal before autonomous modification.
3. Keep system behavior auditable through signed and structured records.
4. Complete one system at a time to a functional foundation standard.
5. Clean the repository so source, docs, tests, and generated artifacts are easy
   to tell apart.

## System Status

| System | Foundation status | Notes |
| --- | --- | --- |
| Security | Functional foundation complete | Capability checks, sandbox policy, signing, audit, and enforcement surfaces. |
| Guardian | Functional foundation complete | Intent evaluation, risk assessment, approval, containment, audit integration, and performance policy. |
| Homeostasis | Functional foundation complete | Observation, diagnosis, recommendations, and Guardian-mediated controlled action paths. |
| Self-Improvement | Functional foundation complete | Proposal-only loop with Guardian review and execution delegation; no direct mutation in the foundation milestone. |
| Kernel, Hub, Memory, Plugins, Agents, Lyrixa, Aether Script | In progress | These systems are being completed and cleaned up in focused passes. |

Primary system documents live in [`docs/`](docs/), especially:

- [`docs/AETHERRA_SECURITY_SYSTEM.md`](docs/AETHERRA_SECURITY_SYSTEM.md)
- [`docs/AETHERRA_GUARDIAN_SYSTEM.md`](docs/AETHERRA_GUARDIAN_SYSTEM.md)
- [`docs/AETHERRA_HOMEOSTASIS_SYSTEM.md`](docs/AETHERRA_HOMEOSTASIS_SYSTEM.md)
- [`docs/AETHERRA_SELF-IMPROVEMENT_SYSTEM.md`](docs/AETHERRA_SELF-IMPROVEMENT_SYSTEM.md)
- [`docs/SYSTEM_INDEX.md`](docs/SYSTEM_INDEX.md)

## Architecture Shape

Aetherra is not a single chatbot, plugin runner, or automation script. It is a
layered runtime with safety boundaries:

```text
Lyrixa / Interfaces / Tools
        |
Agents, Plugins, Aether Script, Self-Improvement, Homeostasis
        |
Guardian policy and risk mediation
        |
Security enforcement, sandboxing, signing, and audit
        |
Kernel, Hub, service registry, memory, and runtime systems
```

Important design rule: Self-Improvement proposes. Guardian reviews. Security
enforces. Execution is delegated only after policy allows it.

## Quick Start

Requirements:

- Python 3.11+
- Git
- A virtual environment

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run a basic smoke check:

```bash
python tools/os_smoke.py
```

Run focused safety and self-improvement tests:

```bash
python -m pytest -q -o addopts= \
  tests/capabilities/test_self_improvement_metrics.py \
  tests/capabilities/test_self_maintenance_services.py \
  tests/unit/test_hub_self_improvement_guardian.py \
  tests/unit/test_optimization_executor_guardian.py \
  tests/unit/test_selfinc_integration_guardian.py \
  tests/unit/test_selfinc_proposal_consumer.py
```

Run the Phase 5 validation harness quick profile:

```bash
python tools/phase5_validation_harness.py --profile quick --timeout 60
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

## Repository Map

| Path | Purpose |
| --- | --- |
| [`Aetherra/`](Aetherra/) | Primary package and runtime systems. |
| [`aetherra_hub/`](aetherra_hub/) | Hub API blueprints, local services, and control-plane surfaces. |
| [`aetherra_coding/`](aetherra_coding/) | Coding, analysis, verification, and orchestration utilities. |
| [`docs/`](docs/) | Active system documentation, guides, policy docs, and cleanup plans. |
| [`tests/`](tests/) | Unit, integration, capability, acceptance, and legacy standalone tests. |
| [`tools/`](tools/) | Verification, smoke, release, maintenance, and developer utilities. |
| [`scripts/`](scripts/) | Operational and maintenance scripts. |
| [`requirements/`](requirements/) | Dependency input files beyond the root requirements locks. |
| [`.github/workflows/`](.github/workflows/) | Focused CI, security, release, docs, and repository hygiene workflows. |

The repository is still being cleaned. Tracked root-level files are being
limited to public docs, package/config files, compatibility launchers, and
current operational entry points. Generated runtime state, reports, databases,
logs, coverage output, and packaged builds should stay ignored or be published
as release artifacts instead of source.

Cleanup tracking is maintained in:

- [`docs/REPOSITORY_CLEANUP_PLAN.md`](docs/REPOSITORY_CLEANUP_PLAN.md)
- [`docs/ROOT_SCRIPT_WORKFLOW_TRIAGE.md`](docs/ROOT_SCRIPT_WORKFLOW_TRIAGE.md)
- [`docs/FILE_INDEX.md`](docs/FILE_INDEX.md)

## Safety Model

Aetherra assumes powerful actions are dangerous until policy says otherwise.

Core rules:

- Self-Improvement must not directly modify the system during the foundation
  milestone.
- Guardian must evaluate privileged intent before execution.
- Security must enforce capabilities, sandboxing, signing, and audit policy.
- Homeostasis should recommend before taking controlled action.
- Rollback, containment, and approval paths are first-class requirements.
- Exceptions and execution payloads must be sanitized before reaching external
  clients.

This is an active research and engineering project. Do not run it as an
unreviewed autonomous production system.

## Development Rules

- Keep changes scoped to the system being completed.
- Prefer structured models and explicit policy decisions over ad hoc payloads.
- Add tests for safety boundaries, denial paths, and audit behavior.
- Keep generated logs, databases, build outputs, packaged distributions, and
  local state out of commits.
- Update the relevant `docs/AETHERRA_*_SYSTEM.md` document when a system's
  behavior or completion status changes.
- Avoid direct mutation loops. Proposal, review, approval, execution, and
  outcome learning should remain separate concerns.

## License

Aetherra is licensed under the GNU General Public License v3.0 or later. See
[`LICENSE`](LICENSE), [`NOTICE`](NOTICE), and [`COPYRIGHT`](COPYRIGHT).
