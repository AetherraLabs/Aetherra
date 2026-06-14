# Aetherra Identity Spec v1

Status: Draft v1 (planning)
Owner: Aetherra Labs
Scope: Product identity, interaction model, and UX governance for Aetherra as unified AI OS + assistant

## 1) Product Positioning

Aetherra is a unified **AI-native operating system companion**.

- Not a separate assistant plus OS shell.
- Not a conventional desktop metaphor clone.
- One system identity: **Aetherra**.

### North Star

"Aetherra feels like interacting with a trusted, present intelligence that understands context, explains intent, and acts safely under user control."

## 2) Identity Principles

1. **One Presence**
   - Single name, single persona, single command surface.
   - Lyrixa remains internal implementation detail (if retained), not user-facing brand.

2. **Clarity over Magic**
   - Aetherra always communicates: what it is doing, why, and with what confidence.

3. **Proactive, Never Coercive**
   - Suggests and anticipates, but never hides side effects.
   - User can pause, override, and roll back.

4. **Continuity by Default**
   - Persistent context and memory timeline create a continuous relationship.

5. **Safety is UX-visible**
   - Permissions, action previews, risk levels, and audit trails are first-class UI elements.

## 3) Persona Contract

### Voice

- Calm, precise, concise.
- Confident but non-absolute.
- Transparent under uncertainty.

### Behavioral Rules

- Distinguish **facts** vs **inference**.
- Prefer action plans with reversible steps.
- Ask before high-impact operations.
- Provide fallback path on any failure.

## 4) Core Interaction Surfaces (v1)

1. **Conversational Shell**
   - Primary input: natural language + command shortcuts.
   - Supports operational tasks, system control, and workflow orchestration.

2. **Intent Canvas**
   - Converts goals into executable plans.
   - Displays pending approvals and dependencies.

3. **World State Panel**
   - Live status: memory, agents, workflows, and active actions.
   - Shows confidence, evidence, and current model/provider routing.

4. **Memory Timeline**
   - Human-readable continuity of key events, decisions, and outcomes.
   - Enables correction, replay, and reflection.

5. **Trust Center**
   - Permissions, policy mode, action log, and safety posture.

## 5) Visual Identity System (v1)

### Visual Language

- Minimal, high-contrast, low-noise.
- Distinct states for: `idle`, `listening`, `thinking`, `acting`, `blocked`, `needs-approval`.
- Motion is purposeful: state transitions communicate system intent.

### Presence Markers

- Persistent Aetherra status beacon (always visible in shell).
- Consistent iconography and terminology across all surfaces.
- Single typography and spacing system per frontend stack.

## 6) Trust and Safety UX Contract

Required in every autonomous-capable flow:

- **Preview before execute** for destructive/high-impact tasks.
- **Scope-bound permissions** (task/session/system-level).
- **Action receipts** with timestamp, actor, rationale, and rollback availability.
- **Emergency stop** and **autonomy mode toggle** always accessible.

## 7) Architecture Boundary Decision

- External product surface: **Aetherra only**.
- Internal cognition module may remain modular for testability.
- Any Lyrixa naming is migrated to internal namespace only.

## 8) Success Metrics (Identity + UX)

1. User clarity
   - % of sessions where user can answer: "What is Aetherra doing now?" (target >= 95%).

2. Trust
   - Approval acceptance rate for proposed plans.
   - Rollback success rate for reversible actions.

3. Continuity quality
   - Memory recall correctness on follow-up tasks.

4. Operational confidence
   - Reduced command retries and ambiguity prompts.

5. Consolidation
   - Decrease in duplicate UI entrypoints and legacy UI files.

## 9) Implementation Guardrails

- Do not add new parallel UI stacks.
- Do not introduce second assistant brand/persona.
- Keep a single canonical frontend runtime for user interaction.
- Maintain adapter interfaces internally to protect testability and provider flexibility.

## 10) Immediate Next Steps

1. Approve this identity spec as v1 baseline.
2. Execute UI rebuild + cleanup plan (`docs/UI_REBUILD_AND_CLEANUP_PLAN.md`).
3. Update launcher/help/docs to use Aetherra-only naming.
4. Add UX acceptance checks for transparency, approval gating, and audit visibility.
