# Spec→Tests Gate in Integrator

Labels: phase:3, area:quality, type:feature
Milestone: Self-Incorporation v1

## Description

Enforce presence of tests for runtime-impacting self-incorporation changes during
integration.

## Acceptance Criteria

- Gate detects changes in integrator paths and requires tests present in PR
- Failing tests allowed during development, but gate blocks merge without tests
- Documentation for exemptions and overrides
- Unit test(s) for gate logic with sample diffs
