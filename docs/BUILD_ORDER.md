# Build Order

This file defines the active build sequence for Aetherra. Its purpose is to
protect the project from uncontrolled pivots by making the next system explicit.

Build order rule: finish a functional foundation, document its boundaries, add
focused tests or verification, then move to the next system.

## Current Sequence

| Order | System | Target State | Status |
| --- | --- | --- | --- |
| 1 | Security | Functional complete | Complete |
| 2 | Guardian | Functional complete | Complete |
| 3 | Homeostasis | Functional foundation complete | Complete |
| 4 | Self-Improvement | Functional foundation complete | Complete |
| 5 | Maintenance | Umbrella loop foundation | Complete |
| 6 | Self-Incorporation | Functional foundation complete | Complete |
| 7 | Memory Refinement | Functional foundation complete | Complete |
| 8 | Consciousness Refinement | Functional foundation complete | Complete |
| 9 | Agent System | Functional foundation complete | Complete |
| 10 | Aether Script | Runtime validation foundation | Complete |
| 11 | Integration Validation | Cross-system alpha readiness foundation | Complete |
| 12 | Runtime UI | Cognitive Observatory foundation | Complete |
| 13 | Kernel | Runtime readiness foundation | Complete |
| 14 | Hub | API integration readiness foundation | Complete |
| 15 | Lyrixa | Guided interaction foundation | Complete |
| 16 | Artificial Intelligence | Engine readiness foundation | Complete |
| 17 | Chat | Transport readiness foundation | Complete |
| 18 | Coding | Proposal and verification foundation | Complete |
| 19 | AI Trainer | Training readiness foundation | Complete |
| 20 | Public Alpha | Controlled alpha release | Pending |

## Near-Term Focus

The next build target should be selected from the first pending item unless a
security, Guardian, or repository hygiene issue blocks progress.

Current next candidate:

1. Public Alpha readiness planning.
2. Repository or CI stabilization if a merge, release, or CI gate requires
   immediate stabilization.

Primary reference for the current target:

- `docs/BUILD_ORDER.md`
- `docs/ACTIVE_SYSTEMS.md`
- `docs/ALPHA_READINESS_CHECKLIST.md`

## Completion Checklist

A system can move from pending to complete when it has:

- A system document in `docs/`.
- A bounded implementation path with clear safety limits.
- Guardian and Security integration for privileged actions.
- Focused tests or verification scripts for the core behavior.
- Audit, logging, or observability appropriate to the system risk.
- Clear routing for proposal, approval, execution, and verification when the
  system participates in the Maintenance loop.
- A README, dashboard, or index update that reflects the new state.

## Pivot Rule

New ideas go into the relevant system document or backlog first. They should not
interrupt the build order unless they fix a safety issue, unblock the current
system, or prevent repository/CI breakage.
