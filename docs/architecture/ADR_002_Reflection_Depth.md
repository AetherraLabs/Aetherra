# ADR 002: Reflection Depth Strategy

- Status: Accepted
- Date: 2026-03-10
- Owners: Phase 1 Team

## Context

The roadmap requires production reflector implementation while balancing speed, determinism, and runtime safety.

## Decision

Use AST-first reflection as the mandatory baseline, with optional runtime introspection only for explicitly allowed diagnostic modes.

## Rationale

- AST analysis is deterministic and side-effect free.
- Runtime introspection can execute import-time code paths and introduce risk.
- AST-first supports CI and offline analysis consistency.

## Consequences

Positive:

- Faster and safer default analysis behavior.
- Easier cacheability and reproducibility.

Negative:

- Some dynamic runtime constructs require optional secondary probes.

## Implementation Notes

1. Implement reflector core over `ast.parse` and static symbol extraction.
2. Add a guarded runtime-probe mode behind explicit policy flag.
3. Ensure production profile keeps runtime probes disabled by default.
