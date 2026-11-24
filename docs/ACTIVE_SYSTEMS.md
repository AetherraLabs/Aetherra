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

Phase A integration candidate (2026-11-23): actual-core readiness, bounded Hub
observation during chat and effective disabled Self-Incorporation are under the
normal full-launch verification gate. See the
[decision addendum](ALPHA_READINESS_DECISION.md#phase-a-core-integration-candidate)
and [reproducible smoke](ALPHA_OPERATOR_RUNBOOK.md#integration-smoke-phase-a).
Foundation labels below do not certify optional cognitive-loop behavior or grant
new authority; Phase B/C activation work remains separate.

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
