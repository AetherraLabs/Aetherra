# ADR-0001: Coverage Delta Data Model & Storage

Status: Proposed
Date: 2025-09-08

## Context

Phase 1 requires surfacing coverage regression (no-drop gate) with richer per-file deltas and audit persistence. Current gate only stores a single baseline percent in `.coverage-baseline` and emits a simple JSON summary (`coverage_gate_report.json`). We need a structured file-level history to: (a) explain drops, (b) anchor autonomy risk policy later, (c) feed PR summaries.

## Decision

Introduce a new artifact `audit/coverage_delta/<timestamp>.json` capturing file-level coverage before/after for changed files plus aggregated totals. Maintain lightweight retention (last N = 30) to bound repo size. Enhance `quality_gates.py` to optionally load a previous run snapshot (if present) and compute deltas. Gate still fails on aggregate drop; future phases may add per-critical-file thresholds.

## Data Model

```json
{
  "run_id": "<timestamp or monotonic>",
  "overall": {"before": 41.2, "after": 42.0, "delta": 0.8},
  "files": [
    {"path": "src/module/foo.py", "before": 85.0, "after": 90.0, "delta": 5.0, "lines_changed": 12},
    {"path": "src/module/bar.py", "before": 60.0, "after": 50.0, "delta": -10.0, "lines_changed": 4}
  ],
  "changed_only": true,
  "generated_at": "2025-09-08T12:34:56Z"
}
```

## Consequences

* Enables explanatory gating reasons (which file regressed).
* Provides longitudinal data for risk model (Phase 2+).
* Slight increase in CI artifact footprint.
* Requires stable collection ordering for deterministic commits (profile test).

## Alternatives Considered

1. Single baseline percent only (status quo) – insufficient diagnostics.
2. Full coverage XML diff – heavier compute & storage, more parsing complexity.

## Implementation Notes

* Parse existing coverage data (may extend to use coverage.py JSON/XML in later iteration).
* Changed files list derived from git diff against main (if available) or touched paths env variable.
* Redact paths if future privacy concerns arise (hashing layer placeholder).

## Phase / Scope

Applies to Phase 1 exit + feeds Phase 2 autonomy policy.

## Follow Ups

* Implement artifact retention script.
* Integrate per-file regression highlights into verify output.
* Extend to branch coverage in later iteration (flag experimental).

## Review

Owner: Coding Lead
Reviewers: QA Lead, DevEx
Decision Date: (pending)
