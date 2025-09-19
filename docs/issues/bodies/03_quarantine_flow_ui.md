# Quarantine → Escalate → Release flow (UI hooks)

Labels: phase:1, area:ui, type:feature
Milestone: Self-Incorporation v1

## Description

Provide a user-visible flow to manage quarantined items with actionable remediation
and release.

## Acceptance Criteria

- UI lists quarantined items with reason and fix hints (sign/reduce caps/sandbox)
- Release action triggers integrator re-apply
- Events/Audit entries written for quarantine, escalate, release
- Minimal e2e or integration test covering flow
