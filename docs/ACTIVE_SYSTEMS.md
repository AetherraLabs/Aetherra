# Active Systems

This is the project dashboard for systems that currently define Aetherra. It
tracks what exists, what state each system is in, and which document should be
treated as the primary reference.

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
| Artificial Intelligence | In progress | `docs/AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md` |
| Consciousness | Functional foundation complete | `docs/AETHERRA_CONSCIOUSNESS_SYSTEM.md` |
| Coding | In progress | `docs/AETHERRA_CODING_SYSTEM.md` |
| Chat | In progress | `docs/AETHERRA_CHAT_SYSTEM.md` |
| AI Trainer | Planned | `docs/AETHERRA_AI_TRAINER_SYSTEM.md` |

## Governance Rule

Security, Guardian, Homeostasis, Self-Improvement, Maintenance,
Self-Incorporation, Memory, Kernel, Hub, Lyrixa, Consciousness, Agent System,
Aether Script, and Integration Validation are the current safety and
operations foundation. New systems should integrate with those foundations
instead of bypassing them.

When a system reaches a functional milestone, update this file, the system
document, and `docs/BUILD_ORDER.md` in the same change.
