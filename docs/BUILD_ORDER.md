# Aetherra Build Order

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: Active Build Dashboard

This document defines the current build sequence for Aetherra. It exists to
protect the project from uncontrolled pivots, duplicated systems, and unclear
completion claims.

The Master Roadmap explains why the project is moving this way. This file
answers the simpler operational question:

**What gets built next?**

## Build Rule

A system is not complete just because code exists.

Before a system can move out of active build focus, it must satisfy the
Understanding Rule:

- What it does.
- Why it exists.
- What authority it owns.
- What authority it does not own.
- How it fails.
- How it interacts with other systems.

It must also have a current system document, clear safety boundaries, and
focused validation appropriate to its authority.

## Current Build Sequence

| Order | System or Milestone | Target State | Current Status |
| --- | --- | --- | --- |
| 1 | Security | Functional complete | Complete |
| 2 | Guardian | Functional complete | Complete |
| 3 | Homeostasis | Functional foundation complete | Complete |
| 4 | Self-Improvement | Functional foundation complete | Complete |
| 5 | Maintenance | Functional foundation complete | Complete |
| 6 | Self-Incorporation | Functional foundation complete | Complete |
| 7 | Memory | Functional foundation complete | Complete |
| 8 | Consciousness | Functional foundation complete | Complete |
| 9 | Agent System | Functional foundation complete | Complete |
| 10 | Aether Script | Functional foundation complete | Complete |
| 11 | Integration Validation | Functional foundation complete | Complete |
| 12 | Runtime UI | Functional foundation complete | Complete |
| 13 | Kernel | Functional foundation complete | Complete |
| 14 | Hub | Functional foundation complete | Complete |
| 15 | Lyrixa | Functional foundation complete | Complete |
| 16 | Engine | Functional complete | Complete |
| 17 | Artificial Intelligence | Functional foundation complete | Complete |
| 18 | Chat | Functional foundation complete | Complete |
| 19 | Coding | Functional foundation complete | Complete |
| 20 | AI Trainer | Functional foundation complete | Complete |
| 21 | Internal Alpha | Safe internal alpha gate | Active |
| 22 | Beta Hardening | CI, security, stability, and UX maturity | Planned |
| 23 | Production Readiness | Operational maturity and release discipline | Planned |

## Active Focus

The active build focus is supervised internal alpha on the verified Windows
source-runtime profile.

Primary references:

- `docs/ALPHA_READINESS_CHECKLIST.md`
- `docs/ALPHA_OPERATOR_RUNBOOK.md`
- `docs/ALPHA_READINESS_DECISION.md`
- `docs/ACTIVE_SYSTEMS.md`
- `docs/SYSTEM_INDEX.md`
- `docs/MASTER_ROADMAP.md`

## Alpha Entry Conditions

Internal alpha requires:

- Functional complete Security, Guardian, and Engine systems.
- Functional foundation complete supporting systems.
- A known runtime boot path.
- A bounded Runtime UI Observatory surface.
- Non-destructive Integration Validation.
- Clean repository structure with generated artifacts excluded.
- Passing docs, quality, security, import, script, and size gates.
- An operator runbook that a fresh operator can follow.
- An explicit alpha readiness decision.

## Current Next Work

PR #327 is merged and its desktop blockers are resolved for the documented
Windows/Python 3.13 source-runtime profile. Fresh installation/audits, 3,136
passing default-suite tests (40 skips, 5 passing subtests), 87 clean-main
regressions, normal CLI/live-model checks and browser verification pass.
All 12 main validation workflows pass. Signed `v0.5.0-beta.6` completed, with
its approved-key signature and artifact hashes independently verified.

**GO for supervised internal alpha on this profile.** Stage 21 remains active
for bounded internal-alpha operation; Beta Hardening and Production Readiness
remain Planned. Optional graphs, other platforms, wheel-only installs and
unattended/production use require separate evidence before extending the decision.
See `docs/ALPHA_READINESS_DECISION.md` and the operator runbook.

| Priority | Work | Required Outcome |
| --- | --- | --- |
| 1 | Supervised internal alpha | Review/integrate Phase A core readiness, responsiveness and effective-mode verification; then Phase B observation/maintenance |
| 2 | Regression preservation | Retain the default suite, continuity, browser and truthful readiness checks |
| 3 | Signing and governance | Keep approved-key signing, Guardian/Security and observation boundaries enforced |
| 4 | Broader acceptance | Verify additional installation graphs and operating modes before extending GO |

The first exercise on merged PR #328 (`ff359b02`) completed ten minutes plus
five minutes after restart, with 16 gpt-4o turns and no fallback. Correct recall,
truthful unknown detail, browser stop/reconnect and governance observations pass.
Initial disclosure acknowledgments exposed a prompt defect; its focused repair
integrated through PR #347. A 63.603-second total cold recall interrupted
status polling before the second steady window. Retain that limitation and the
failed observations; this is not a continuous-responsiveness or soak-test pass.
See [the decision](ALPHA_READINESS_DECISION.md) and
[exercise evidence](evidence/supervised_alpha_2026-11-22.json).

The 2026-11-23 Phase A candidate adds actual-core readiness, bounded concurrent
Hub observation, disabled Self-Incorporation enforcement and a disposable full-CLI
restart smoke. Its offline and seven-turn gpt-4o checks preserve evidence IDs,
honest unknowns and storage separation. The
[decision addendum](ALPHA_READINESS_DECISION.md#phase-a-core-integration-candidate)
records final verification and unmerged-candidate boundaries. Phase B is the
bounded observation/maintenance loop; Phase C owns optional cognitive activation
and experimental-module quarantine. Stage 21 remains active.

## Change Rule

When this file changes:

1. Update `docs/MASTER_ROADMAP.md` if milestone order or status changed.
2. Update `docs/ACTIVE_SYSTEMS.md` and `docs/SYSTEM_INDEX.md` if a system status
   changed.
3. Update the affected system document if completion claims changed.
4. Run `python tools\verify_docs_consistency.py`.
5. Run `git diff --check`.

Do not create additional roadmap files. Update this build dashboard and the
Master Roadmap instead.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
