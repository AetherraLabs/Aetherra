# Aetherra Integration Validation System

Updated: 2026-06-20

## Purpose

Integration Validation proves that Aetherra's functional foundations cooperate
through their current safety contracts. It is not a full alpha certification
suite and it does not perform destructive actions.

The validation layer answers:

- Can Guardian and Security mediate privileged intent?
- Can Homeostasis observe and diagnose without acting?
- Can Maintenance coordinate proposal flow without owning action authority?
- Can Aether Script execution be gated before parsing or execution?

## Status

Functional foundation complete.

Primary implementation:

- `Aetherra/integration_validation.py`
- `tests/unit/test_integration_validation.py`

## Authority Boundaries

Integration Validation does not own production authority. It verifies authority
routing:

| Authority | Owner | Validation Expectation |
| --- | --- | --- |
| Approve, deny, contain | Guardian | Intent evaluation happens before privileged paths |
| Enforce capabilities | Security | Strict-mode callers without grants are denied |
| Observe, diagnose, verify | Homeostasis | Reports remain read-only and action-free |
| Coordinate | Maintenance | Proposals route only after Guardian and Security |
| Execute | Self-Incorporation | Validation records dry-run outcome only; no mutation |
| Script execution | Aether Script | Runtime gate fires before interpreter mutation |

## Validation Checks

The current runner performs four non-destructive checks:

1. `guardian_security_chain`
   - Guardian allows an internal script runtime intent.
   - Security denies an external strict-mode caller missing `script:run`.

2. `homeostasis_observation_diagnosis`
   - Builds a degraded observation report.
   - Produces bounded causal diagnosis.
   - Confirms actions remain disabled.

3. `maintenance_coordination_chain`
   - Routes a dry-run proposal through Maintenance.
   - Uses Guardian decision state and Security enforcement state.
   - Records dry-run execution, Homeostasis verification, and learning outcome.

4. `aether_script_runtime_gate`
   - Executes a benign internal validation script.
   - Blocks an external strict-mode script before interpreter mutation.

## Running

```powershell
python -m Aetherra.integration_validation
```

The module uses a temporary workspace by default and restores environment
variables after the run.

Focused tests:

```powershell
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_integration_validation.py
```

## Functional Foundation Criteria

This system is foundation-complete because:

- It has a bounded executable validation runner.
- It exercises multiple completed foundations in one chain.
- It validates both allow and deny behavior.
- It avoids destructive actions, network calls, real self-modification, and UI
  dependencies.
- It is covered by focused tests and a CLI smoke path.

## Non-Goals

Integration Validation does not yet prove:

- Full public alpha readiness.
- Long-running runtime stability.
- UI/operator workflow quality.
- End-to-end live Hub behavior.
- Production sandbox isolation.
- Performance under load.

Those belong to later alpha-readiness, runtime UI, and release-candidate gates.

## Next Refinements

- Add a live Hub route validation profile once Hub startup is stabilized.
- Add Kernel/service-registry boot validation once Kernel refinement is complete.
- Add signed `.aether` workflow validation profile for release candidates.
- Add an integration report artifact for CI.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
