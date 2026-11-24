# Phase A core integration implementation plan

> **For agentic workers:** Continue in this session with scoped implementation
> ownership and independent review of each task, then a whole-change review.

**Goal:** Make the full-launcher core path truthful, responsive and reproducible.

**Architecture:** Existing readiness assessors describe actual service evidence;
bounded Hub observation concurrency preserves mutation ownership; an isolated
smoke harness drives the normal launcher and existing chat endpoint.

**Tech stack:** Python asyncio/threads, Flask/Werkzeug, SQLite Memory, existing
Guardian/Security, Windows source-runtime environment.

**Spec:** `docs/superpowers/specs/2026-11-23-core-integration-design.md`.

## Global constraints

- Main baseline: `8902e161c728dca50f95555e16bfdfccf5f303b8`.
- Preserve original work and the separate pending temporal observer candidate.
- Keep signing and existing Guardian/Security controls enforced.
- Use the normal full launcher; no new chat route or memory/provider service.
- Keep tests offline and deterministic; generation is the only permitted smoke double.
- Keep Phase B/C/D activation separate and Stage 21 active.

## Review focus

- Missing, starting or stale observations cannot become authoritative readiness.
- A configured provider is not a verified API response; absent optional legacy
  status fields must preserve existing caller contracts.
- Busy, expired and denied work must leave storage and retryable IDs untouched.
- SSE response completion does not prove its generation worker has stopped.
- Shutdown failure must retain ownership and avoid teardown beneath active writes.

## Task 1: Readiness contracts

Files: launcher startup scan/announcement, Kernel readiness, Hub registry client,
Engine status/readiness and focused unit tests.

- [x] Reproduce missing-core and stale-Kernel false-ready results.
- [x] Add failing provenance, freshness, component/provider and compatibility cases.
- [x] Require live Kernel evidence, actual Memory registration and configured
      Engine evidence; expose `core_readiness` separately from `optional_services`.
- [x] Preserve Hub liveness/standalone semantics and remove unconditional startup claims.
- [x] Run focused tests and independent review; record evidence.

## Task 2: Responsive observation with bounded ownership

Files: `aetherra_hub/compat.py`, a focused request-ownership/transport helper,
`aetherra_hub/services/ai_stream.py`, and scoped Hub responsiveness tests.

- [x] Reproduce a health timeout while real Engine generation is paused.
- [x] Cover all four observation routes during ask and SSE, saturation,
      busy/expiry/idempotency, disconnect, worker retention and drain failure.
- [x] Implement bounded observation concurrency and explicit retryable rejection;
      retain mutation ownership until actual worker completion.
- [x] Verify shared Engine caller compatibility and graceful resource ordering.
- [x] Run focused tests and independent concurrency review.

## Task 3: Effective alpha modes

Files: launcher service configuration, relevant existing service status/mode
interfaces and focused mode tests; exact changes follow reproduced behavior.

- [x] Reproduce requested versus effective Self-Incorporation enablement.
- [x] Honor explicit disablement and report effective Homeostasis/Self-Improvement
      modes through their existing status surfaces without granting authority.
- [x] Verify disabled execution paths and existing enabled callers; review the diff.

## Task 4: Reproducible integration smoke and documentation

Files: focused smoke tool/tests; existing alpha runbook, checklist, decision,
roadmap/system references and synthetic evidence.

- [x] Drive the normal launcher in a fresh local profile; capture readiness JSON,
      effective modes, audit, process exits and bounded latency measurements.
- [x] Prove real Memory receipt/retrieval/generation evidence across process restart,
      competing facts, unknown attributes and separate profiles.
- [x] Run the same entry with an intentionally configured live provider when
      available; record fallback status and distinguish missing live evidence.
- [x] Run boot/Integration Validation, focused governance/continuity checks,
      fixed quality baseline, docs checks and the full default suite.
- [x] Update readiness decision with remaining limits; preserve raw artifacts
      outside reviewed source and verify both protected workspaces unchanged.
- [x] Obtain whole-change review and resolve implementation blockers.

## Rulings and progress

- User-approved phased plan is the design authority; execute Phase A now.
- Preserve narrow endpoint meanings; coherent-runtime aggregation belongs to
  the existing launcher scan, not standalone Hub liveness.
- Preserve pending temporal changes in their independent clone; do not absorb
  them into this branch or claim their optional integration is merged.
- Use external pytest cache/temp paths and preserve all `GIT_CONFIG_*` tuples to
  avoid the already diagnosed Windows test-harness isolation failures.
- Independent review reproduced and repaired active-turn CLI shutdown and CORS
  busy-response regressions; the final independent selection passed 59 tests.
- Raw pre-parse saturation is best-effort; parsed busy admission has explicit
  retry metadata and configured CORS. Automatic OPTIONS is the only busy-path
  response exception; custom handlers do not execute.
- Final full-suite verification uses an isolated frozen D: snapshot. All 1,412
  Python files match the candidate byte-for-byte. Source equivalence is recorded
  with the evidence. Diagnostic iterations remain separate from acceptance.
- The final default suite exited zero: 3,348 passed, 38 skipped and five passing
  subtests. Both final seven-turn offline/live smokes passed with three clean
  process exits each; gpt-4o used the saved record after restart without fallback.
- Phase A is locally verified and remains an unmerged candidate. Hosted CI
  and integration are separate gates before proceeding to Phase B.
