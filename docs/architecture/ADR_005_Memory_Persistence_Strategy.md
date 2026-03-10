# ADR 005: Memory Persistence Strategy

- Status: Accepted
- Date: 2026-03-10
- Owners: Phase 1 Team

## Context

Memory consistency is a production-critical requirement across kernel, engine, and learning loops.

## Decision

Adopt layered persistence with explicit durability classes.

## Durability Classes

- Ephemeral: session scratch data, non-critical.
- Durable: primary memory records and narratives.
- Audit: immutable append-only event trail for governance.

## Rationale

- Aligns storage cost and latency with data criticality.
- Simplifies backup and recovery objectives.

## Consequences

Positive:

- Clear retention and recovery behavior.

Negative:

- Requires strict schema/version discipline.

## Implementation Notes

1. Define schema versioning and migration policy.
2. Validate write paths for idempotency and crash recovery.
3. Add integrity checks in startup health diagnostics.
