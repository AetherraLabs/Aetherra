# Aetherra Self-Improvement System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: v0.1 Functional Proposal Foundation Complete

The Aetherra Self-Improvement System observes system behavior, analyzes recurring issues, forms hypotheses,
simulates expected impact, and produces structured improvement proposals. It does not directly modify the
system in the foundation milestone.

Self-Improvement exists to answer one question:

**What should Aetherra consider improving, and why?**

Actual modification belongs to controlled execution paths after Guardian review, Security enforcement,
approval when required, rollback validation, and audit recording.

## Purpose and scope

Self-Improvement is not an autonomous patching engine. It is the scientific feedback layer for Aetherra's
evolution. It studies metrics and outcomes, identifies improvement opportunities, and emits evidence-backed
proposals for review.

The strict foundation rule is:

**Self-Improvement does not modify. Self-Improvement proposes.**

This avoids a closed loop where the same subsystem identifies problems, decides the solution, and applies the
solution. Closed improvement loops can drift. Aetherra instead separates observation and proposal from
application.

Self-Improvement acts as:

- **Observer**: detects inefficiencies, failures, bottlenecks, contradictions, and recurring issues.
- **Analyst**: explains likely causes and improvement opportunities.
- **Scientist**: estimates impact, confidence, risk, testability, and rollback feasibility.
- **Proposal Author**: creates structured improvement requests for Guardian and operators.
- **Learning Surface**: records outcomes from approved changes so future proposals can improve.

## Completion strategy

Self-Improvement must mature in strict phases:

1. **Observation**: detect inefficiencies, failures, bottlenecks, contradictions, and recurring issues. No recommendations.
2. **Hypothesis**: connect issue, potential cause, and possible improvement. No modification.
3. **Simulation**: estimate expected impact, testability, reversibility, and rollback guarantees.
4. **Proposal**: generate a structured improvement plan with reason, change, expected benefit, risk, and rollback.
5. **Guardian**: submit the proposal to Guardian for allow, deny, approval required, or containment.
6. **Execution**: execute only through controlled downstream systems after approval and policy enforcement.

Current completion focus: **Phase 6 - Controlled Execution Delegation**

Completion status: **Functional foundation complete; advanced simulation and adaptive learning remain future work.**

## Architecture overview

The Self-Improvement System is split across four cooperating layers:

- **Metrics Intake**: receives health and performance signals from Homeostasis, Lyrixa, chat, maintenance,
  observability, and other systems.
- **Analysis Engine**: identifies trends, anomalies, recurring patterns, and degradation signals.
- **Proposal Engine**: converts high-confidence observations into structured improvement proposals.
- **Controlled Application Bridge**: routes approved proposals to Self-Incorporation, HMR, or manual execution
  paths after Guardian review.

Core flow:

1. Homeostasis and runtime systems emit metrics.
2. `SelfImprovementEngine` records metrics and analyzes trends.
3. The engine creates active proposals, not direct modifications.
4. Operators or UI surfaces inspect status, trends, and proposals.
5. Applying a proposal calls `/api/selfimprove/apply` or `/batch-apply`.
6. Guardian evaluates rollback, evidence, capabilities, containment, approvals, and risk.
7. Approved execution is delegated to Self-Incorporation, HMR, or manual application.
8. Outcomes are reported back for future learning.

## Guardian enforcement

Self-Improvement is Guardian-sensitive because it can lead to self-modification.

Critical and privileged actions:

- Proposal application through `/api/selfimprove/apply`
- Batch proposal application through `/api/selfimprove/batch-apply`
- HMR-based code reload from improvement proposals
- Self-Incorporation plan execution caused by improvement proposals
- Optimization executor file or configuration mutation
- Rollback or restore operations after failed optimization

Required behavior:

- Read-only status, trends, and proposal listing do not call Guardian directly.
- Proposal application declares a `self.apply_proposal` Guardian intent.
- HMR-backed proposals require `self:modify`, `code:modify`, and `system:reload`.
- Reversible proposals must provide rollback metadata.
- Proposals without rollback can require approval or be denied depending on Guardian mode and policy.
- Approved Guardian approval IDs are consumed once and bound to the matching intent.
- Active containment of the `self_improvement` subsystem blocks proposal application.
- Raw proposal code snippets, file contents, and sensitive payloads must not be written to Guardian audit metadata.

## Implemented foundation

Implemented files:

- `Aetherra/aetherra_core/engine/self_improvement_engine.py`
- `Aetherra/homeostasis/self_improvement_metrics_bridge.py`
- `Aetherra/homeostasis/self_incorporation_metrics_bridge.py`
- `Aetherra/homeostasis/self_incorporation_security.py`
- `aetherra_hub/blueprints/self_improvement.py`
- `aetherra_hub/blueprints/self_incorporation.py`
- `aetherra_self_incorporation.py`
- `Aetherra/aetherra_core/system/optimization_executor.py`

Implemented endpoints:

- `GET /api/selfimprove/status`
- `GET /api/selfimprove/proposals`
- `GET /api/selfimprove/trends`
- `POST /api/selfimprove/apply`
- `POST /api/selfimprove/batch-apply`
- `GET /api/selfinc/status`
- `POST /api/selfinc/scan`
- `POST /api/selfinc/apply`
- `POST /api/selfinc/rollback`
- `GET /api/selfinc/audit`
- `GET /api/selfinc/metrics`

## Phase 1 - Observation

Implemented behavior:

- Homeostasis forwards stability metrics to the Self-Improvement Engine.
- Runtime systems can record performance metrics with name, value, unit, and context.
- The engine tracks metric history and exposes read-only status.
- `GET /api/selfimprove/status` reports activity, proposal counts, tracked metrics, analysis cycles, and whether
  autonomous implementation is enabled.

Observation is read-only. It does not apply proposals, modify files, reload modules, change policies, or update
capabilities.

## Phase 2 - Hypothesis

Implemented behavior:

- The engine analyzes metric patterns and metric statistics.
- It can identify trend direction, correlation patterns, cyclical behavior, and degradation signals.
- It converts high-confidence findings into active proposals instead of executing them.
- `GET /api/selfimprove/trends` exposes read-only metric trends.

Hypothesis work remains bounded to explaining what might be wrong and what might help.

## Phase 3 - Simulation

Implemented foundation:

- Proposals include expected benefit, implementation cost, risk level, affected components, and success criteria.
- Guardian application paths require reversibility metadata or explicit approval.
- Optimization execution supports validation, backup, rollback, and metrics comparison.
- HMR paths distinguish applied, manual, unavailable, and failed outcomes with `restart_required`.

Remaining simulation work:

- Add deterministic dry-run estimators for each proposal type.
- Attach structured simulation reports to proposals before Guardian review.
- Expand rollback feasibility scoring beyond current rollback-plan presence and executor backup support.

## Phase 4 - Proposal

Implemented behavior:

- High-confidence proposals are stored with `active` status by default.
- Default operation does not self-implement generated proposals.
- `GET /api/selfimprove/proposals` returns active proposals for UI/operator review.
- Proposal application remains an explicit control-plane action.

Example proposal shape:

```json
{
  "proposal_id": "SI-42",
  "reason": "Memory retrieval latency is increasing",
  "proposed_change": "Optimize the memory index configuration",
  "expected_benefit": "15% retrieval improvement",
  "risk": "low",
  "rollback": "available"
}
```

## Phase 5 - Guardian

Implemented behavior:

- `/api/selfimprove/apply` and `/batch-apply` evaluate Guardian intent before application.
- Proposals can require approval when rollback is missing or risk exceeds policy.
- Approved Guardian approval IDs are consumed and cannot be replayed.
- Containment blocks proposal application until cleared.
- Guardian decisions are written to the signed Security audit ledger.

## Phase 6 - Execution

Execution is intentionally delegated:

- Self-Incorporation consumes improvement proposals and handles integration planning.
- HMR applies safe reloads when available.
- Manual application remains a valid outcome when automated execution is unavailable or undesirable.
- Optimization Executor handles file/config changes with Guardian preflight, backup, verification, and rollback.

Self-Improvement should never bypass these execution paths.

## Completion criteria

Self-Improvement is complete for the current foundation milestone when:

- observation reports engine state and tracked metrics without side effects
- hypothesis/trend inspection explains likely improvement opportunities without mutation
- active proposals can be listed through a read-only API
- generated proposals remain recommendations by default
- proposal application requires Hub control authorization
- proposal application routes through Guardian before Self-Incorporation, HMR, or manual execution
- rollback requirements, approval consumption, containment, and audit are enforced
- execution outcomes can be reported back for future learning
- future autonomous implementation stays disabled unless explicitly enabled and Guardian-gated

## Tests

Key tests:

- `tests/capabilities/test_self_improvement_metrics.py`
- `tests/capabilities/test_self_maintenance_services.py`
- `tests/unit/test_hub_self_improvement_guardian.py`
- `tests/unit/test_optimization_executor_guardian.py`
- `tests/unit/test_selfinc_integration_guardian.py`
- `tests/unit/test_selfinc_proposal_consumer.py`
- `tests/acceptance/test_maintenance_e2e_flow.py`

## Related documentation

- `docs/AETHERRA_SELF_IMPROVEMENT_API.md`
- `docs/AETHERRA_GUARDIAN_SYSTEM.md`
- `docs/AETHERRA_HOMEOSTASIS_SYSTEM.md`
- `docs/AETHERRA_MAINTENANCE_SYSTEM.md`
- `docs/selfinc/README.md`
- `docs/SELFINC_PRODUCTION_READINESS.md`
