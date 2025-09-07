# Aetherra Roadmap

## Beta (0.2.x) Objectives (Current Phase)

- Stabilize Hub APIs (chat, trainer, memory narratives) with minimal breaking changes.
- Add persistent trainer/eval storage + cancellation and retry semantics.
- Expand plugin chain tests (parallel, conditional, failure injection, timeout handling).
- Introduce migration layer for plugin execution SQLite schema.
- Diagnostics: formal JSON output mode + contract test.
- Coverage: raise fail-under target proposal (evaluate raising from 70% → 75–80%).
- Federation: design finalized; announce/sync endpoint contract drafted (still returns 501 until Stable).

## Stable (0.3.x) Targets

- Federation secure peer handshake + signing enforcement and peer registry cache.
- Persistent evaluation datasets + pluggable scoring metrics.
- Advanced memory narratives enrichment pipeline (summarization + clustering signals).
- Provider status endpoint (explicit health per model/provider + fallback reason codes).
- Workflow language enhancements: conditional branches, loop constructs (bounded), safe sandbox policies.
- Plugin marketplace prototype (signed distribution manifests + integrity verification).
- Performance profiling surfaces (p95 chat latency, memory recall timing histograms).

## Future (0.4.x and Beyond)

- Multi-tenant access controls with per-principal quotas & isolation boundaries.
- Differential privacy configurable modes for memory export & analytics.
- Hardware quantum integration path (beyond simulator) with capability negotiation.
- Declarative evaluation suites referencing dataset registry + auto scheduling.
- Cross-instance federation meshes (selective memory graph sync, trust scoring).
- Visual workflow builder (graph editing of `.aether` specs) and inline signing UI.
- Policy-driven auto-remediation (license, security, and ethical rule triggers).

## Guiding Principles

- Transparent instrumentation before feature expansion.
- Graceful and deterministic fallbacks (never silent failure paths).
- Signed artifacts (workflows, plugins) as integrity baseline.
- Incremental hardening: ship minimal slice with metrics + tests before broadening.

## Recently Completed (Beta Cut)

- 32 test capability suite including plugin reload lifecycle.
- Memory & intelligence stability improvements + capability reinforcement hook.
- Plugin system documentation and lifecycle validation.
- Beta readiness report publication.

Contributions aligned with near-term objectives are prioritized. Open issues labeled `roadmap-proposal` for discussion.
