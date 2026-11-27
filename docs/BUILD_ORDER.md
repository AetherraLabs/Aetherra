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

Phases A/B, C1/C2a, C2b and the bounded runtime follow-up are merged.
The C2b merge is `592c4622` (PR #368); beta.22 is `56623003`. The
[phase status table](MASTER_ROADMAP.md#current-priority-internal-alpha),
[current evidence review](ALPHA_READINESS_DECISION.md#c2b-merged-main-evidence-review-2026-11-26)
and [receipt](evidence/c2b_merged_main_review_2026-11-26.json) distinguish the
4,158-pass/38-skip merge suite and 660-second offline released-main continuity
from earlier candidate live/browser/physical evidence. Original failures remain.

**Stage 21 remains active, with the existing supervised internal-alpha GO
unchanged.** Stage 22 Beta Hardening and Stage 23 Production Readiness remain
Planned; a beta package version does not advance them. C2b is implemented within
its recorded limits; Phase D optional agency remains deferred.

| Priority | Work | Required Outcome |
| --- | --- | --- |
| 1 | Review evidence and investigate OPEN development records | Apply the six [records' owner and closure gates](DEVELOPMENT_ISSUES.md#current-records); preserve causes still unknown, retained failures and unverified boundaries. Delegated Codex documentation review accepted the reconciliation; final pushed-revision checks remain required. |
| Separate pending work | Temporal runtime observer, PR #380 | Review and verify pending integration separately from merged C2b/checkpoint work. |

Keep signing, Guardian/Security, checkpoint ownership and observe/propose-only
authority limits enforced. Broader installation graphs, unattended/production
use and autonomous actions require separate acceptance.

Historical reference: the [2026-11-22 desktop verification](ALPHA_READINESS_DECISION.md#historical-desktop-verification-2026-11-22)
and [first supervised exercise](evidence/supervised_alpha_2026-11-22.json)
remain tied to their recorded revisions. The latter ran 600 + 300 steady-state
seconds with 16 gpt-4o turns and no fallback, but its 63.603-second cold recall
interrupted status polling. PR #347 later repaired disclosure acknowledgments.
Those passes do not replace current installation, browser or live-model checks
and do not establish continuous responsiveness or a soak-test pass.

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
