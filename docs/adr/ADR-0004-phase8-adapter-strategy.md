# ADR-0004: Phase 8 Adapter Strategy (Namespaced Beyond Transcendence Engine)

Status: Proposed
Date: 2025-09-08

## Context

Legacy Phase 8.3 (Beyond Transcendence) engine code existed only as a root-level module. Import paths were inconsistent and produced launch warnings. Direct stubbing risked silent behavioral drift and made deterministic testing harder. A scalable approach was required to:
- Provide a stable canonical implementation location (namespaced under `Aetherra.consciousness.transcendence`)
- Maintain backward compatibility for existing imports without breaking tests or tooling
- Introduce deterministic baseline logic and lightweight metrics without mutating legacy import semantics
- Allow future removal of the shim after migration completion

Constraints:
- Avoid breaking existing launcher/tests referencing `beyond_transcendence_engine` at repo root
- Keep adapter logic self-contained; no deep cross-phase coupling
- Must operate when MetaCognitionSystem is degraded/unavailable

## Decision

Introduce a namespaced `BeyondTranscendenceEngine` as the canonical implementation and retain a thin root-level shim that re-exports it while logging a deprecation notice. Embed deterministic coverage blending and in-memory metrics (coverage_reads, suppressed_exceptions, transcendence_level_last) in the namespaced adapter. Root shim contains no business logic.

## Details

Key elements:
- Canonical file: `Aetherra/consciousness/transcendence/beyond_transcendence_engine.py`
- Root shim: `beyond_transcendence_engine.py` (logs deprecation + re-export)
- Determinism: If `AETHERRA_DETERMINISTIC=1`, coverage value blended (25% live, 75% baseline) using optional `AETHERRA_TRANSCENDENCE_BASELINE` (default 0.72)
- Metrics: Adapter tracks suppressed exceptions and coverage read counts; exported via `export_metrics()`
- Graceful degradation: If MetaCognitionSystem import fails, adapter still initializes and logs warning

Deprecation path:
1. Phase 1 (current): Shim present, logs on import
2. Phase 2: Telemetry counts legacy imports, publish migration notice
3. Phase 3: Fail tests on new legacy imports (allowlist existing)
4. Phase 4: Remove shim after two minor releases

## Consequences

Positive:
- Clear canonical path reduces ambiguity
- Deterministic mode improves reproducibility
- Metrics enable observability and test assertions

Trade-offs / Risks:
- Slight duplication (two files) until shim removal
- Potential unnoticed reliance on side effects in legacy module (mitigated via logging)

## Alternatives Considered
1. Direct in-place modification of root module (no shim) – rejected: hard migration, no telemetry window
2. New adapter with immediate hard failure on legacy import – rejected: disruptive
3. Symbol-level re-export inside package `__init__` only – rejected: less explicit; still breaks direct import lines

## Related Work / Links
- ERRORS_WARNINGS_AUDIT.md (original warning notes)
- Deterministic profile tests

## Phase / Scope
Applies to: Phase 8 (Transcendence) integration & launcher import resolution

## Review
Owner: Architecture
Reviewers: Core Runtime, Testing, Observability
Decision Date: 2025-09-08
