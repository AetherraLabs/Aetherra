# Active Systems

This is the project dashboard for systems that currently define Aetherra. It
tracks what exists, what state each system is in, and which document should be
treated as the primary reference.

For the human-readable identity, authority model, and core lifecycle of the
project, see `docs/WHO_IS_AETHERRA.md`.

For the active build sequence, see `docs/BUILD_ORDER.md`.

Status meanings:

- Functional foundation complete: the system has a working bounded foundation,
  tests or verification surfaces, and documented safety limits.
- Functional complete: the current milestone is complete for the active
  architecture, while future refinement may still happen.
- In progress: the system exists but needs further implementation, cleanup, or
  validation before alpha readiness.
- Planned: the system is described or expected, but not yet implemented as an
  active foundation.

## Core Systems

Personal continuity checkpoint (2026-11-19): the normal full-launcher Hub/Engine
path now retrieves bounded persisted personal evidence across process restart.
Offline and live competing-fact/profile checks and core recall are recorded
in [PERSONAL_CONTINUITY.md](PERSONAL_CONTINUITY.md). This establishes local storage
isolation, not account isolation or full-runtime readiness.

Integrated alpha baseline (2026-11-24): Phase A core readiness and Phase B
observe/propose-only Homeostasis and Maintenance are merged through
[PR #352](https://github.com/AetherraLabs/Aetherra/pull/352), released as
`v0.5.0-beta.11` at `17a833cd0653556b50d869be1f22b989d5633cb4`.
See the [clean-main checkpoint](ALPHA_READINESS_DECISION.md#phase-b-merged-main-checkpoint).

Phase C1 local acceptance (2026-11-24): **GO for supervised Windows operation of
the frozen opt-in ConsciousnessCore observer candidate.** The full suite passed
3,651 tests, 38 skips and 5 passing subtests. Allowed and denied normal-launch
profiles each crossed 215 seconds; real Observatory HTTP status, signed audit
chains, independent observer stop and continued chat passed. C1 is committed and
pushed as `b8719fa2`, still unmerged; hosted CI, browser and live-model
checks are unverified.
See [source-bound evidence](evidence/integration_phase_c1_2026-11-24.json), the
[C1 contract](AETHERRA_CONSCIOUSNESS_SYSTEM.md#phase-c1-normal-runtime-contract)
and [operator procedure](ALPHA_OPERATOR_RUNBOOK.md#consciousness-observer-smoke-phase-c1).
Phase C2a publication-review checkpoint (2026-11-24): **scoped GO for supervised
Windows source-runtime observer checkpoints at `5d8ccecb`.** Review corrected
the normal Windows CLI first-SIGINT save path and added C2 acceptance to CI.
Current targeted checks passed 129 unit/lifecycle tests and 4 acceptance tests,
including CLI-only shutdown and exact pre-tick restore. The full suite,
extended run and browser results at `a10b734e` are historical; the changed launcher
has not had a full-suite or browser rerun. See the
[current decision](ALPHA_READINESS_DECISION.md#phase-c2a-observer-checkpoints) and
[review receipt](evidence/integration_phase_c2a_pr_review_2026-11-24.json).
Hosted CI awaits publication; fresh Python installation, live-model operation
and physical keyboard shutdown remain unverified. C2b automatic selection,
periodic saves and retention are deferred. Pending temporal work is preserved;
no unattended readiness, account isolation or action authority is claimed.

| System | Status | Primary Reference |
| --- | --- | --- |
| Security | Functional complete | `docs/AETHERRA_SECURITY_SYSTEM.md` |
| Guardian | Functional complete | `docs/AETHERRA_GUARDIAN_SYSTEM.md` |
| Homeostasis | Functional foundation complete | `docs/AETHERRA_HOMEOSTASIS_SYSTEM.md` |
| Self-Improvement | Functional foundation complete | `docs/AETHERRA_SELF-IMPROVEMENT_SYSTEM.md` |
| Maintenance | Functional foundation complete | `docs/AETHERRA_MAINTENANCE_SYSTEM.md` |
| Self-Incorporation | Functional foundation complete | `docs/AETHERRA_SELF-INCORPORATION_SYSTEM.md` |
| Memory | Functional foundation complete | `docs/AETHERRA_MEMORY_SYSTEM.md` |
| Kernel | Functional foundation complete | `docs/AETHERRA_KERNEL_SYSTEM.md` |
| Agent System | Functional foundation complete | `docs/AETHERRA_AGENT_SYSTEM.md` |
| Aether Script | Functional foundation complete | `docs/Aether_Script_Language_System.md` |
| Integration Validation | Functional foundation complete | `docs/AETHERRA_INTEGRATION_VALIDATION.md` |
| Runtime UI | Functional foundation complete | `docs/AETHERRA_RUNTIME_UI_SYSTEM.md` |
| Lyrixa | Functional foundation complete | `docs/AETHERRA_LYRIXA_SYSTEM.md` |
| Hub | Functional foundation complete | `docs/AETHERRA_HUB_API_REFERENCE.md` |

## Cognitive And Intelligence Systems

| System | Status | Primary Reference |
| --- | --- | --- |
| Engine | Functional complete | `docs/AETHERRA_ENGINE_SYSTEM.md` |
| Artificial Intelligence | Functional foundation complete | `docs/AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md` |
| Consciousness | Functional foundation complete | `docs/AETHERRA_CONSCIOUSNESS_SYSTEM.md` |
| Coding | Functional foundation complete | `docs/AETHERRA_CODING_SYSTEM.md` |
| Chat | Functional foundation complete | `docs/AETHERRA_CHAT_SYSTEM.md` |
| AI Trainer | Functional foundation complete | `docs/AETHERRA_AI_TRAINER_SYSTEM.md` |

## Governance Rule

Security, Guardian, Homeostasis, Self-Improvement, Maintenance,
Self-Incorporation, Memory, Kernel, Hub, Lyrixa, Consciousness, Agent System,
Aether Script, Coding, AI Trainer, and Integration Validation are the current safety and
operations foundation. New systems should integrate with those foundations
instead of bypassing them.

When a system reaches a functional milestone, update this file, the system
document, and `docs/MASTER_ROADMAP.md` in the same change.
