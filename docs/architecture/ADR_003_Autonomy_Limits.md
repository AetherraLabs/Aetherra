# ADR 003: Consciousness Autonomy Limits

- Status: Accepted
- Date: 2026-03-10
- Owners: Phase 1 Team

## Context

Autonomous decision loops must remain bounded, auditable, and reversible in production.

## Decision

Adopt policy-enforced autonomy limits with fail-closed behavior.

## Policy Baseline

- Max bounded action budget per cycle.
- Risk-scored actions above threshold require approval.
- Forbidden operations remain blocked in autonomous mode.
- Every autonomous action must emit an audit record.

## Rationale

- Prevents runaway behavior and unsafe mutation.
- Supports clear operations and compliance review.

## Consequences

Positive:

- Predictable runtime behavior and incident response.

Negative:

- Additional friction for high-risk autonomous tasks.

## Implementation Notes

1. Centralize autonomy limit checks in governor layer.
2. Enforce profile-aware thresholds.
3. Add capability tests for blocked and allowed paths.
