# ADR-0005: Exception Suppression & Visibility Policy

Status: Proposed
Date: 2025-09-08

## Context

Pre-remediation code silently suppressed many exceptions (broad except: pass patterns) in adaptive / cognitive subsystems. This obscured defect signals, hindered reliability analysis, and complicated deterministic test assurances. We need a consistent policy to balance resilience (non-critical paths should not crash the OS) with observability (no silent loss of signal) and measurable suppression accounting.

For new deterministic metrics (e.g., Phase 8.3 adapter, SelfImprovementEngine) we added lightweight counters. Formalizing this ensures future modules follow the same standard.

## Decision

Adopt a tiered exception handling strategy:
1. Critical Path (startup sequencing, persistence integrity): Log at ERROR, re-raise unless explicitly recoverable.
2. Degradation-Capable Path (metrics sampling, heuristic enrichment, optional analyzers): Catch, increment suppression counter, log at DEBUG (or INFO on first occurrence), continue.
3. Experimental / Non-Core Features (alpha cognitive loops, speculative analyzers): Catch, count, log at DEBUG trace bucket; upgrade to INFO only if suppression rate threshold exceeded.
4. Fallback Constructors (optional subsystems): Catch and fallback instance (None or stub), log WARNING once, subsequent failures DEBUG only.

## Implementation Rules

- Every suppression site must increment a local or shared counter (e.g., `self._suppressed_exceptions` or adapter metrics map entry) BEFORE continuing.
- First occurrence: log WARNING if the component is expected normally to succeed (initialization). Subsequent identical failures: DEBUG.
- Provide an accessor (`export_internal_metrics()` or `export_metrics()`) exposing suppression counts for test assertions.
- Never swallow KeyboardInterrupt, SystemExit.
- Avoid broad `except Exception:` inside wide scopes; narrow if possible. If wide is necessary (task loop guard), increment counter + minimal contextual message.

## Deterministic Mode Interaction

Deterministic mode (env `AETHERRA_DETERMINISTIC=1`) must not change exception visibility—only the synthesized or blended metric values. Suppression counters function identically in deterministic and non-deterministic runs for comparability.

## Thresholds & Escalation

- Escalate to INFO if a single suppression counter increases by >25 within one process hour (future enhancement: hook metrics service).
- Future: integrate with telemetry to emit structured suppression events for anomaly detection.

## Consequences

Positive:
- Quantifiable visibility into resilience vs failure
- Safer optional feature experimentation
- Enforceable via unit tests (assert counters >0 when simulating faults)

Trade-offs:
- Slight performance overhead for counter increments
- More logs in early failures (mitigated by first-occurrence rule)

## Alternatives Considered

1. Full re-raise everywhere + global crash monitoring – rejected (reduces resilience).
2. Silent logging only (no counters) – rejected (non-measurable suppression).
3. Metrics-only (no logs) – rejected (debugging latency too high).

## Related Work / Links

- ERRORS_WARNINGS_AUDIT.md
- ADR-0004 (Phase 8 Adapter Strategy)
- SelfImprovementEngine counters
- BeyondTranscendenceEngine metrics map

## Phase / Scope

Applies project-wide to new modules and refactors progressively (priority: cognitive/meta/transcendence subsystems, adaptive analyzers, background service loops).

## Review

Owner: Architecture / Reliability
Reviewers: Runtime, Observability, Testing
Decision Date: 2025-09-08
