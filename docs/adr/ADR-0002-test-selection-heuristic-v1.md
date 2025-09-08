# ADR-0002: Test Selection Heuristic v1

Status: Proposed
Date: 2025-09-08

## Context
Full test runs are increasingly costly. Phase 1 introduces a lightweight heuristic to propose a reduced test subset while preserving safety. We need a documented baseline heuristic (deterministic, explainable) that is easy to retire or improve.

## Decision

Adopt a simple file/stem mapping heuristic:

* Directly include any touched paths under `tests/`.
* For touched source files, match tests whose filename contains the source stem + `test` (substring search).
* Provide structured output JSON with `candidates`, `fallback`, `confidence`, and `reason`.
* Only apply subset if confidence >= configurable threshold (default 0.8) and not fallback.

## Confidence Heuristic

* 0.9 if all touched source files map to at least one candidate test.
* 0.6 if >=50% map.
* 0.4 if <50% map.
* 0.5 if only test paths were provided.
* 0.3 if fallback (capabilities suite) used.

## Consequences

* Fast to implement and transparent.
* Low false negative protection: fallback and confidence gating reduce risk.
* Does not leverage dependency graph or symbol indexing (future enhancement).

## Alternatives Considered

1. Static import graph analysis now – rejected (higher complexity, not yet required for Phase 1 exit).
2. Always run full suite – safe but slower; accepted as fallback.

## Migration / Future

Phase 2+ may replace with graph + historical failure data. This ADR will be Superseded when semantic graph selection lands.

## Review

Owner: Coding Lead
Reviewers: QA Lead, DevEx
Decision Date: (pending)
