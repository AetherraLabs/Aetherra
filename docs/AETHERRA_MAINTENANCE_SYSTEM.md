# Aetherra Maintenance System

The Aetherra Maintenance System is the umbrella loop that keeps Aetherra
observable, correctable, auditable, and capable of safe evolution. It is not one
giant autonomous subsystem. It coordinates existing systems and preserves their
authority boundaries.

Core rule:

```text
Self-Improvement proposes.
Self-Incorporation executes.
Guardian decides.
Security enforces.
Homeostasis verifies.
```

This keeps Aetherra autonomous in thought, but governed in action.

## Authority Ownership

Each layer owns a specific authority. Maintenance coordinates the loop, but it
does not inherit the authority of the systems it coordinates.

| System | Owned Authority |
| --- | --- |
| Homeostasis | Observe and verify |
| Self-Improvement | Diagnose and propose |
| Guardian | Approve, deny, and contain |
| Security | Enforce permissions, sandboxing, signing, network policy, and audit |
| Self-Incorporation | Execute approved changes |
| Maintenance | Coordinate cycle state, routing, and outcome records |

Ownership rule: if a Maintenance action needs an authority that belongs to
another system, Maintenance must call that system instead of duplicating the
authority locally.

## System Role

Maintenance answers four operational questions:

1. What is happening?
2. Why is it happening?
3. What should be done?
4. Did the approved change help?

Maintenance may observe, diagnose, report, and propose. It must not bypass
Guardian, Security, or approval rules to mutate the system.

## Umbrella Loop

```text
AETHERRA MAINTENANCE SYSTEM
|-- 1. Homeostasis        -> detects instability
|-- 2. Self-Improvement   -> proposes improvements
|-- 3. Guardian           -> decides if change is allowed
|-- 4. Security           -> enforces permissions, sandboxing, and audit
|-- 5. Self-Incorporation -> applies approved changes
`-- 6. Homeostasis        -> verifies outcome
```

Canonical flow:

```text
Observe
Diagnose
Propose
Review
Approve
Apply
Verify
Learn
```

## Layer 1: Observation

Purpose: collect facts without mutation.

Responsibilities:

- Collect system health.
- Collect memory health.
- Collect plugin, agent, kernel, and Hub status.
- Collect repository hygiene and maintenance tool signals.
- Surface metrics through status APIs and reports.

Current implementation surfaces:

- `Aetherra/maintenance/cycle.py`
- `Aetherra/maintenance/paths.py`
- `Aetherra/maintenance/service.py`
- `Aetherra/maintenance/store.py`
- `aetherra_hub/blueprints/maintenance.py`
- `GET /api/maintenance/status`
- `tools/maintenance/`
- Homeostasis health and status providers
- Self-Improvement and Self-Incorporation status providers

Observation must be safe to run repeatedly and should not write outside approved
report/output paths.

If a `maintenance_system` or `aetherra_maintenance` service is registered, the
Hub status endpoint includes its active and recent cycle summaries. If no
coordinator is registered, Maintenance status remains available in degraded
visibility mode through the contract and underlying subsystem summaries.

The Hub status endpoint also reports loop readiness by phase. A phase is ready
when its owning subsystem is visible to the Hub status aggregator. Guardian and
Security readiness are represented as contract-level readiness until deeper
runtime health probes are added. Readiness entries include:

- `runtime`: the owning subsystem is visible through the registry/status path.
- `contract`: the authority is part of the Maintenance contract, but does not
  yet expose a dedicated runtime readiness probe through this endpoint.

The readiness summary includes ready counts and missing phases so operators can
see whether the full loop is available or only partially visible.

Generated Maintenance reports should target approved generated-output paths such
as `data/artifacts/maintenance/` or intentional durable documentation paths such
as `docs/reports/`. Root-level generated reports are not part of the foundation
policy.

## Layer 2: Diagnosis

Purpose: explain what the observations likely mean.

Responsibilities:

- Identify degradation and recurring failures.
- Detect bottlenecks, repeated errors, or unhealthy trends.
- Separate runtime health issues from repository hygiene issues.
- Produce evidence-backed explanations instead of immediate fixes.

Diagnosis output should include:

- issue summary
- affected subsystem
- supporting evidence
- likely cause
- confidence
- severity
- suggested next step

## Layer 3: Proposal

Purpose: create structured improvement proposals without applying them.

Responsibilities:

- Convert diagnoses into improvement proposals.
- Include expected benefit, risk, confidence, and rollback plan.
- Mark whether human approval is required.
- Attach evidence and trace identifiers.

Minimum proposal shape:

```text
proposal_id
source
target_subsystem
issue
evidence
proposed_action
expected_benefit
risk_level
rollback_plan
approval_required
trace_id
```

Self-Improvement owns proposal generation. Maintenance may aggregate, display,
or route proposals, but it does not turn proposals into direct mutation.

The coordinator may create a cycle from a proposal and record the supplied
Guardian and Security results. It does not produce those decisions itself.

Cycle records may be persisted through `Aetherra.maintenance.MaintenanceRecordStore`.
The store writes JSONL coordinator records to approved Maintenance artifact
paths, defaulting to `artifacts/maintenance/maintenance_cycles.jsonl`. This is
record persistence only. It does not approve, execute, or verify maintenance
actions.

Runtime registration may use `Aetherra.maintenance.MaintenanceService`. The
service wraps a coordinator and optional record store so the Hub can report
Maintenance status through `maintenance_system`. It remains a facade: it routes
provided proposals, decisions, security results, execution results, and
verification results without creating those decisions itself.

Use `Aetherra.maintenance.register_maintenance_service()` when bootstrapping the
runtime. It registers the service as `maintenance_system` with metadata that
declares Maintenance authority boundaries and the Hub status endpoint.

## Layer 4: Governance

Purpose: decide whether a proposal is allowed.

Responsibilities:

- Guardian reviews intent, risk, scope, and containment requirements.
- Security checks capabilities, sandbox policy, signing, network policy, and
  audit requirements.
- Risky changes require approval.
- Unsafe paths are denied or contained.

Governance is mandatory for privileged maintenance actions, including:

- file writes
- cleanup operations
- integration or self-incorporation
- dependency changes
- plugin or agent activation
- runtime restart
- rollback or restore operations
- network-enabled maintenance actions

## Layer 5: Execution

Purpose: apply only approved changes.

Responsibilities:

- Self-Incorporation executes approved integration plans.
- Runtime changes use HMR, canary paths, rollback tokens, or other guarded
  mechanisms where available.
- Repository maintenance tools use explicit plans and approved write paths.
- Execution records outcome, trace IDs, and rollback information.

Execution must never happen because Self-Improvement decided alone. It must flow
through Guardian and Security first.

The coordinator may record an execution result returned by Self-Incorporation or
another guarded executor, but only after the cycle already contains a proposal,
a Guardian allow decision, and Security enforcement.

## Layer 6: Verification

Purpose: determine whether the change improved or harmed the system.

Responsibilities:

- Homeostasis compares before and after health.
- Verify target metrics and system stability.
- Detect regressions or failed outcomes.
- Trigger rollback paths when health drops below allowed thresholds.

Verification output should record:

- baseline health
- post-change health
- metric deltas
- regression signals
- rollback status
- final outcome

Maintenance may attach the supplied verification result to the cycle record. It
does not decide health improvement; Homeostasis owns that judgment.

## Layer 7: Learning

Purpose: improve future maintenance decisions from observed outcomes.

Responsibilities:

- Record proposal outcome.
- Track which proposal types succeeded, failed, or regressed.
- Preserve evolution history for later analysis.
- Improve confidence scoring without granting direct mutation authority.

Learning should create an evidence trail, not an unbounded closed loop.

Cycle records emit append-only events for observations, diagnoses, proposals,
Guardian decisions, Security enforcement, execution, verification, learning, and
failures. These events are intentionally in-memory in the foundation slice, but
their shape is suitable for later signed audit or evolution ledger persistence.

Cycle records can be exported and rehydrated as structured data. Persistence is
not performed by the coordinator itself; any durable write must go through an
approved storage, audit, or evolution ledger path.

## Failure Handling

Failure behavior is part of the architecture. Maintenance must fail closed for
mutation and fail degraded for visibility.

| Failure Point | Required Behavior |
| --- | --- |
| Observation fails | Continue operation with degraded visibility and record the missing signal. |
| Diagnosis fails | Do not generate a proposal from incomplete reasoning. |
| Proposal creation fails | No change occurs; record the failed proposal attempt. |
| Guardian denies | Terminate the proposal path and record the denial reason. |
| Guardian contains | Stop execution and apply the containment instruction. |
| Security blocks | Terminate execution and record the violated policy or missing capability. |
| Execution fails | Activate the rollback path when a rollback token or plan exists. |
| Verification fails | Escalate to Homeostasis and Guardian for review or containment. |
| Learning fails | Preserve the raw outcome record and continue without updating confidence. |

No failed maintenance step may silently continue into mutation. If the system
cannot prove approval, enforcement, and rollback readiness, execution must not
begin.

## Functional Foundation Target

Maintenance can be considered functionally complete for the foundation milestone
when the project has:

- A reliable maintenance status API.
- Observation of Homeostasis, Self-Improvement, Self-Incorporation, and core
  runtime health.
- Structured diagnosis and proposal records.
- Guardian review for privileged maintenance actions.
- Security enforcement for filesystem, network, signing, sandbox, and audit
  requirements.
- Approved execution paths through Self-Incorporation or explicit maintenance
  tools.
- Before/after verification through Homeostasis.
- Outcome records suitable for future evolution history.
- Tests for status aggregation, proposal routing, Guardian denial paths,
  Security enforcement, execution handoff, and verification results.

## Non-Goals For The Foundation Milestone

The foundation milestone does not include:

- Fully autonomous self-repair without approval.
- Unreviewed code mutation.
- Direct Self-Improvement execution.
- Background integration of unknown code without Guardian/Security review.
- Claims of production autonomy or zero-touch operation.

Those capabilities require later staged work, stronger evaluation, and explicit
approval policy.

## Current Build Focus

The next Maintenance pass should focus on:

1. Aligning implementation and docs with the umbrella loop.
2. Curating `tools/maintenance/` into safe read/report tools versus guarded
   write/action tools.
3. Ensuring generated maintenance reports are ignored or written to approved
   output locations.
4. Extending `/api/maintenance/status` only where it clarifies the loop.
5. Adding tests around proposal routing, Guardian decisions, Security checks,
   and Homeostasis verification.

## Related Documents

- `docs/ACTIVE_SYSTEMS.md`
- `docs/MASTER_ROADMAP.md`
- `docs/MAINTENANCE_TOOL_INVENTORY.md`
- `docs/AETHERRA_HOMEOSTASIS_SYSTEM.md`
- `docs/AETHERRA_SELF-IMPROVEMENT_SYSTEM.md`
- `docs/AETHERRA_GUARDIAN_SYSTEM.md`
- `docs/AETHERRA_SECURITY_SYSTEM.md`
- `docs/REPOSITORY_STRUCTURE.md`
