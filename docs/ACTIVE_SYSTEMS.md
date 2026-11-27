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

Integrated alpha baseline (updated 2026-11-26): Phase A/B, C1, C2a,
C2b (PRs #356-#360 and #362-#367), and progress follow-up #368 are merged.
Released main is `56623003675bc99f9e3dfadf15b6254beb183b59`
(`v0.5.0-beta.22`). The preceding merge `592c46224425` passed its full suite
(4,158 passed, 38 skipped), GUI checks and enforced production signing;
released-main boot/integration and the bounded automated continuity/restart
checks passed. These distinct revision bindings and limitations are recorded
in the [resumption evidence](evidence/temporal_resumption_2026-11-26.json).

The local opt-in Temporal observer samples completed Core ticks every five seconds.
It saves changes and session/gap markers through typed Memory, restores up to 256
records into the existing engine, and publishes cached evidence in the
Consciousness inspector. See the [operator guide](TEMPORAL_HISTORY.md) and
[local runtime receipt](evidence/temporal_runtime_integration_2026-11-26.json)
for the commands, source hashes and scope. Local final-source verification recorded 4,319 passed, 38 skipped and 45.29% coverage against the unchanged 22% floor.

The existing supervised-alpha GO is unchanged. ALPHA-CKPT-001 and DEV-CKPT-001
remain OPEN; the original slow operation remains unexplained. Normal shutdown
also retains the pre-existing Homeostasis watchdog error, with no claim that
every outstanding operation settled. Fresh Python installation, current browser,
live-model and physical keyboard checks were not rerun for released main;
earlier evidence retains its own source revision. No unattended readiness,
production readiness, account isolation or new action authority is claimed.

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
