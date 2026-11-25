# Development Guidelines (Phase 1.2 Baseline)

This document defines implementation and validation standards for production roadmap execution.

## 1. Branch and PR Discipline

- Use short-lived feature branches per task cluster (for example `phase2a-reflector-core`).
- Keep PR scope single-purpose and linked to task IDs from `docs/IMPLEMENTATION_TASKS.md`.
- Require at least one reviewer for code-path changes and one for security/policy changes.

## 2. Coding Rules

- No new placeholder behavior in production paths (`pass`, empty mock returns, silent fallback).
- Use explicit errors with actionable messages when optional dependencies are missing.
- Keep core modules typed for public methods and shared data objects.
- Prefer deterministic behavior over implicit runtime side effects.

## 3. Testing Requirements

- Unit tests for all new core logic.
- Integration tests for subsystem boundaries.
- Capability tests for product claims and policy behavior.
- For critical modules, target `>=90%` line coverage for changed code sections.

## 4. Quality Gates

Before merge, run:

1. `pytest tests/unit -q`
2. `pytest tests/integration -q`
3. `python tools/spec_tests_gate.py`
4. `python tools/quality_gates.py`
5. `python tools/run_go_no_go_gates.py --gates launcher_smoke security_strict memory_core`

If a gate is intentionally deferred, document reason and mitigation in the PR.

## 5. Security and Policy

- Respect strict profile settings for scripts, signing, and network behavior.
- Do not weaken policy defaults to pass tests.
- Any policy change must include tests and docs update.
- Capture risk acceptance explicitly in `docs/RISK_ACCEPTANCE.md` when needed.

## 6. Performance Expectations

- Reflector target: `<100ms` per representative file in benchmark tests.
- Avoid O(n^2) scans in code paths expected to run on large repositories.
- Add lightweight metrics to new critical runtime flows.

## 7. Documentation Requirements

- Update architecture docs when interfaces or dependency directions change.
- Update `docs/SYSTEM_INDEX.md` maturity labels when subsystem readiness shifts.
- Add ADR updates for architecture or policy decisions.

## 8. Release Readiness Checklist (Per Milestone)

- Feature complete for declared tasks.
- Tests and gates green at required scope.
- No critical or high unresolved security findings.
- Operational runbook impact reviewed.
- Evidence artifacts attached (logs, reports, metrics snapshots).

## 9. Development Issues and Evidence

Use the [Development Issue Register](DEVELOPMENT_ISSUES.md) as a permanent
practice across subsystems and roadmap stages. Record unresolved or recurring
failures and readiness limitations with a stable ID, observed/expected behavior,
source revision, environment, evidence, owner, next step and closure criteria.
Link affected PRs and readiness decisions to the record.

Keep established findings separate from hypotheses and unknowns. Preserve failed
observations when later checks pass; a diagnostic correction or successful rerun
does not prove an unexplained cause has been resolved. Record deferral or risk
acceptance only with its explicit reviewed scope and rationale, never implicitly
through a release or passing test. Follow the register's evidence and closure
rules before changing disposition.

Development issues and future runtime incidents are separate records with
cross-links where relevant. Incident recovery does not close a development
defect, and checkpoint retention is not incident or temporal-history retention.
