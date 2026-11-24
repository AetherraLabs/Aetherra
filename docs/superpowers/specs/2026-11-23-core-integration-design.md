# Phase A: coherent core runtime

The user supplied the phased integration plan and selected execution of Phase A
as focused changes. Aetherra remains the persistent cognitive system; Lyrixa is
her user-facing persona. Stage 21 remains the supervised internal alpha boundary.

## Intent and scope

Make the normal `aetherra_os_launcher.py --mode full --no-gui` path truthful and
responsive for an operator using a disposable Windows source-runtime profile.
Reuse Kernel, Registry, Hub, Engine, Memory, Guardian and Security. Preserve
existing callers, personal-continuity receipts, signing and unknown answers.

The existing temporal observer candidate stays separate, unchanged and opt-in.
Phase B observation/maintenance, Phase C governed cognitive activation and
Phase D optional agency remain later integration milestones. In particular,
the current launcher still loads experimental cognition before the Hub/Kernel;
this work must not describe the proposed core-first activation order as shipped.

## Baseline and selected approach

The existing four boot checks and five Integration Validation checks pass.
They do not catch three reproduced gaps: startup claims ready with missing
Memory/Engine; stale diagnostic Kernel records permit scheduling readiness;
and a blocked real chat generation prevents the single-thread Hub from serving
`/health`. The runbook also records requested-disabled Self-Incorporation as
enabled; the effective mode contract must be inspected and repaired.

Use shared readiness assessors and explicit observation provenance, preserving
the narrower standalone Hub liveness/readiness contracts. Do not perform model
network requests or storage writes to answer readiness. Provider configuration
and selection evidence is distinct from a successful live model request.

For responsiveness, allow concurrent HTTP observation only for the four core
GET/HEAD routes: `/health`, `/api/hub/readiness`, `/api/kernel/readiness`, and
`/api/ai/status`. Bound request workers and retain exclusive ownership of other
application requests. Busy requests fail explicitly and are never replayed.
An SSE worker retains ownership until generation actually finishes, including
after response timeout/disconnection. Generic Engine callers keep their existing
overlapping-turn contract. Shutdown stops admission and drains owned work before
Memory teardown; failed drain is a failure, not a clean stop.

Alternatives considered: prewarming alone cannot prevent provider latency from
blocking status; unrestricted threaded serving expands unreviewed mutation
concurrency. Narrow concurrency preserves the existing mutation boundary but
means other routes can return retryable busy responses during chat. Eight request
workers is the initial bounded transport choice, to be verified with saturation
and shutdown tests. This is an implementation choice, not a user-specified limit.

## Authority and effective modes

Guardian decides, Security enforces, and only explicitly approved execution may
reach Self-Incorporation. Preserve all existing ingress authorization. Keep
Homeostasis observation-only, Self-Improvement automatic implementation off, and
Self-Incorporation disabled in the alpha exercise; their status must report
effective values. Denied/expired/busy work must not write personal facts or
consume retryable message IDs. Audit and failure metadata exclude raw prompts,
credentials and private exception payloads.

## Evidence and acceptance

Add a reusable disposable-profile smoke procedure using the same launcher and
HTTP endpoints. Offline tests may replace generation only; storage, retrieval,
context assembly, governance and separate-process restart use real code. Require
selected record IDs to reach generation, accurate paraphrase recall, honest
unknowns, no false provider success, and both process exits zero. A live mode
accepts only deliberately supplied provider credentials and records provider and
fallback status; absence of credentials is unverified, never a live pass.

Inspect all four core endpoints during blocked generation, verify configured and
unconfigured-provider readiness, inspect effective modes and audit status, and
preserve the normal signing/Guardian/continuity regressions. Extend the existing
runbook checks rather than creating a second alpha launch path. Record latency
as measured; the prior 63.603-second turn did not separate retrieval from provider
time. Local profile directories provide storage isolation, not account isolation.

Keep original and temporal worktree HEAD, index, worktree content and signing
controls unchanged. No release publishing, broad autonomy, provider training,
new memory service, default cognitive activation or multi-platform claim belongs
to this Phase A change.
