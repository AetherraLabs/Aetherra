# CLI: aether selfinc {scan|plan|apply|rollback|audit}

Labels: phase:1, area:dx, type:feature
Milestone: Self-Incorporation v1

## Description

Introduce a CLI command group to manage the self-incorporation lifecycle.

## Acceptance Criteria

- Commands: scan, plan, apply, rollback, audit
- Each command has help text and examples
- Exit codes: 0 success; non-zero on failure
- Unit tests for command parsing and basic flows
