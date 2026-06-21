# Aetherra Self-Incorporation System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: v0.1 Functional Foundation Complete

The Aetherra Self-Incorporation System is the controlled execution layer for
approved system changes. It discovers, classifies, plans, applies, rolls back,
and audits integrations only after the required governance path has been
satisfied.

Self-Incorporation exists to answer one question:

**How can an approved change be applied safely, reversibly, and observably?**

It is not the proposal engine. It is not the approval authority. It is not the
policy owner. Its authority is execution.

Core rule:

```text
Self-Improvement proposes.
Guardian decides.
Security enforces.
Self-Incorporation executes.
Homeostasis verifies.
Maintenance records the cycle.
```

## Purpose and Scope

Self-Incorporation gives Aetherra a controlled path for incorporating code,
plugins, agents, workflows, scripts, utilities, documentation, and approved
runtime integration plans.

It must not create a closed self-modification loop. A change may be applied only
when it has passed through the proper upstream authority path:

1. A proposal or operator request exists.
2. Guardian allows, allows with limits, or consumes a valid approval.
3. Security enforces capabilities, sandbox, signing, network, and audit policy.
4. Self-Incorporation applies the approved plan.
5. Homeostasis verifies the outcome.
6. Maintenance records the result.

Strict foundation rule:

**Self-Incorporation executes approved changes. It does not decide whether those
changes should exist.**

## Trust Milestones

Self-Incorporation is organized around four trust milestones.

### Milestone 1: Trustworthy Discovery

Goal: find and understand candidates without changing the runtime.

Discovery, classification, and risk analysis are read-oriented. They may update
Self-Incorporation's own index and audit metadata, but they must not activate,
integrate, execute, or register discovered candidates.

### Milestone 2: Trustworthy Planning

Goal: create a plan that is complete enough to review.

Every executable plan must answer:

- What changes?
- Why does the change exist?
- What is the risk?
- What rollback path exists?
- What dependencies are involved?
- What benefit is expected?

If a plan cannot answer those questions, it is not executable.

### Milestone 3: Trustworthy Execution

Goal: apply exactly what was approved and nothing else.

Before Guardian review, Self-Incorporation attaches an approved-scope lock to
the plan. The lock records the action count and a deterministic hash of the
execution-relevant action scope. The core integrator validates that lock before
dispatching any action. If the action list changes after approval, execution
fails closed with `scope_mismatch`.

Scope expansion is not allowed. A plan approved for one plugin must not execute
that plugin plus unrelated updates, registrations, or runtime mutations.

### Milestone 4: Trustworthy Rollback

Goal: make every non-dry-run integration reversible or block it before mutation.

Rollback is more important than integration during the foundation milestone.
Non-dry-run mutation must have a truthful rollback path before execution. HMR
actions require token rollback support from the controller. Locally reversible
actions must emit bounded rollback tokens and audit records. Unsupported
rollback claims fail closed instead of reporting success.

## Authority Ownership

| Authority | Owning System | Self-Incorporation Behavior |
| --- | --- | --- |
| Observe health | Homeostasis | Consumes health signals for canary and rollback checks |
| Diagnose issue | Self-Improvement | Receives proposals or plan inputs |
| Propose improvement | Self-Improvement | Does not generate proposals as its primary authority |
| Approve or deny | Guardian | Requires Guardian intent evaluation for privileged paths |
| Enforce capability/security policy | Security | Uses capability, signing, sandbox, network, and audit controls |
| Execute approved change | Self-Incorporation | Applies, stages, quarantines, rolls back, and audits |
| Verify outcome | Homeostasis | Exposes execution result for verification |
| Coordinate lifecycle | Maintenance | Reports execution result and rollback tokens to Maintenance |

## Current Implementation Surfaces

Implemented files and surfaces:

- `aetherra_self_incorporation.py`
- `aetherra_hub/blueprints/self_incorporation.py`
- `Aetherra/homeostasis/self_incorporation_security.py`
- `Aetherra/homeostasis/self_incorporation_metrics_bridge.py`
- `docs/selfinc/README.md`
- `docs/SELFINC_PRODUCTION_READINESS.md`
- `docs/issues/selfinc_v1_backlog.md`

Implemented service registration:

- Launcher key: `self_incorporation`
- Registry service: `self_incorporation`
- Maintenance visibility: `GET /api/maintenance/status`

Implemented Hub endpoints:

- `GET /api/selfinc/status`
- `POST /api/selfinc/scan`
- `POST /api/selfinc/apply`
- `POST /api/selfinc/rollback`
- `GET /api/selfinc/audit`
- `GET /api/selfinc/metrics`
- `GET /api/selfinc/ethics/overview`
- `POST /api/selfinc/ethics/evaluate`
- `GET /api/selfinc/ethics/audit/<trace_id>`

## System Flow

```text
Input request or approved proposal
↓
Discovery / scan
↓
Classification
↓
Policy and risk evaluation
↓
Integration plan
↓
Guardian review
↓
Security enforcement
↓
Dry-run / canary / apply
↓
Audit + rollback token
↓
Homeostasis verification
↓
Maintenance outcome record
```

## Layer 1: Discovery

Purpose: discover candidate files and integration inputs.

Responsibilities:

- Scan configured roots.
- Index discovered files into Self-Incorporation state.
- Classify candidates by type, including plugins, agents, `.aether` scripts,
  workflows, utilities, and documentation.
- Record scan metrics without applying changes.

Discovery is read-oriented. It may update the Self-Incorporation index, but it
must not activate or integrate discovered items by itself.

## Layer 2: Classification

Purpose: understand what a candidate is and what it could affect.

Responsibilities:

- Extract file type, declared capabilities, risk hints, dependencies, and
  integration target.
- Identify high-risk, unknown, unsigned, or policy-violating candidates.
- Route unsafe candidates to quarantine or review.
- Preserve enough metadata for audit and rollback planning.

Classification should be deterministic and explainable. Operators should be able
to understand why a candidate was staged, rejected, or quarantined.

## Layer 3: Planning

Purpose: create an integration plan without applying it.

Responsibilities:

- Convert approved candidate inputs into structured actions.
- Define dry-run behavior.
- Define rollback requirements.
- Prepare canary or HMR paths when available.
- Produce trace identifiers and audit metadata.

Planning must not bypass Guardian or Security. A plan is not permission to
execute.

## Layer 4: Governance

Purpose: ensure privileged execution is allowed before mutation.

Required governance:

- Guardian intent review for integration, rollback, and canary deployment.
- Security capability enforcement for file writes, runtime integration,
  rollback, signing, sandbox, and network-sensitive behavior.
- Hub control endpoints require centralized control authorization, including
  mutation routes and audit lookup routes that can expose governance evidence.
- Proposal-supplied integration actions must route through the same guarded
  integration preflight as Hub-triggered apply operations.
- Strict mode support for production posture.
- Capability denial before mutation when policy is missing or insufficient.
- Containment respect when Guardian has contained the subsystem.

Privileged paths include:

- Apply integration plan.
- Roll back by token.
- Canary deployment.
- HMR-backed integration.
- Plugin or agent activation.
- Script or workflow registration.
- Any direct file or runtime mutation.

## Layer 5: Execution

Purpose: apply only the change that was approved.

Execution modes:

- Dry run: validate and report without mutation.
- Staged apply: apply bounded integration actions.
- Canary: apply with health comparison and rollback threshold.
- HMR-backed apply: integrate with rollback token and audit trail.
- Quarantine: isolate or hold unsafe candidates.
- Rollback: restore or mark rollback for a previous integration.

Execution requirements:

- Honor the approved plan scope.
- Validate the approved-scope lock before action dispatch.
- Record trace IDs.
- Emit metrics.
- Produce or consume rollback tokens where applicable.
- Return rollback tokens to the authorized caller when an applied action needs
  operator-accessible rollback.
- Block non-dry-run mutation when a truthful rollback path is unavailable.
- Preserve audit evidence.
- Return structured outcome data to callers.

Self-Incorporation should fail closed when required approval, capability, or
rollback guarantees are missing.

Proposal-triggered execution must not call the core integrator directly. It must
construct a plan, run Guardian and Security preflight through the canonical
integration path, and execute only if that path allows the operation.

HMR-routed actions must not silently fall back to direct execution when the HMR
controller is unavailable. Dry-run may proceed without rollback infrastructure
because it does not mutate state. Non-dry-run mutation must return a
`rollback_unavailable` result before execution.

HMR-backed mutation also requires a public token rollback contract on the HMR
controller. A controller is not sufficient by itself; it must expose a callable
rollback method such as `rollback_token`, `rollback_by_token`, or
`rollback_integration`. Controllers that expose action-specific rollback
support must also confirm that the requested action is supported before
mutation. If token rollback or action rollback is unavailable,
Self-Incorporation must fail closed before mutation with an action-specific
`rollback_unavailable` result.

## Layer 6: Audit and Rollback

Purpose: make every integration accountable and reversible where possible.

Current audit surfaces:

- Self-Incorporation audit database.
- HMR audit frames.
- Ethics audit views.
- Hub audit endpoint.
- Guardian audit entries for privileged paths.
- Maintenance cycle outcome records.

Rollback requirements:

- Rollback tokens must be bounded and traceable.
- Rollback must pass Guardian review.
- Rollback cascade limits must prevent unstable repeated rollbacks.
- Rollback results must be audited even when implementation is partial.
- Homeostasis should verify post-rollback health.
- Plan-level audit records should store bounded rollback metadata such as token
  counts or token hashes instead of duplicating raw operator rollback tokens.

Known foundation limitation:

The foundation currently proves token-bound rollback for bounded local workflow
registration, HMR-backed plugin registration, HMR-backed agent registration when
the active orchestrator exposes an unregister/remove API, and Aether Script
load bookkeeping. Unsupported rollback records fail closed with an explicit
unsupported operation result instead of claiming success. HMR-backed plugin
rollback is registered against the plugin manager that applied the plugin and
rolls back through `unload_plugin`. HMR-backed agent rollback is registered
against the orchestrator that applied the agent and rolls back through
`unregister_agent`, `remove_agent`, or `deregister_agent`. Aether Script
rollback currently removes only the Self-Incorporation applied-script marker so
the script can be re-applied; it does not claim to reverse arbitrary side
effects produced by the script body. File-backed restoration remains an
implementation target until Self-Incorporation introduces direct file mutation.

## Layer 7: Verification and Feedback

Purpose: confirm whether the applied change improved or harmed the system.

Responsibilities:

- Expose execution result to Homeostasis.
- Report metrics for accepted, executed, quarantined, integrated, and rolled
  back work.
- Provide rollback token visibility to Maintenance and operator surfaces.
- Send proposal results back to Self-Improvement when execution was triggered
  by an improvement proposal.
- Preserve audit records for learning and future proposal confidence.

Self-Incorporation does not declare success alone. The applied change should be
validated by Homeostasis or a bounded verification path.

## Failure Handling

| Failure Point | Required Behavior |
| --- | --- |
| Discovery fails | Report degraded scan result; no integration occurs |
| Classification fails | Mark candidate unknown or quarantine |
| Planning fails | Return structured error; no execution occurs |
| Guardian denies | Terminate execution path |
| Security blocks | Terminate execution path |
| Dry-run fails | Do not apply |
| Apply fails | Audit failure and preserve rollback information if available |
| Canary health drops | Trigger rollback when possible and audit the event |
| Rollback token invalid | Deny rollback and audit bounded metadata |
| Audit write fails | Do not hide execution status; report degraded audit visibility |
| Verification fails | Escalate to Homeostasis, Guardian, and Maintenance |

## Safety Invariants

- Self-Incorporation must never apply a privileged change without Guardian and
  Security authorization.
- Self-Incorporation must not generate proposals as its core authority.
- Self-Incorporation must not silently expand the scope of an approved plan.
- Strict mode must fail closed for missing capability, signing, or policy
  requirements.
- Quarantine must be safer than automatic release.
- Rollback must be auditable.
- Audit metadata must avoid leaking raw source, sensitive payloads, private
  paths, secrets, or full stack traces.
- Operator APIs must return clear status without exposing private internals.

## Production Configuration

Common environment flags:

- `AETHERRA_SELFINC_ENABLED=1`
- `AETHERRA_SELFINC_STRICT=1`
- `AETHERRA_REQUIRE_CAPABILITIES=1`
- `AETHERRA_NET_STRICT=1`
- `AETHERRA_HMR_ENABLED=1`

Production posture should require:

- strict capability policy
- strict network policy
- signing policy for supported artifacts
- bounded rollback and canary thresholds
- Guardian enforcing mode
- audit availability
- token-gated Hub control endpoints where exposed

## Functional Foundation Criteria

The Self-Incorporation System can be considered functionally complete for the
foundation milestone when:

- The canonical system document exists and matches the implementation.
- Status, scan, apply, rollback, audit, metrics, and ethics endpoints are
  documented and covered by focused tests.
- Apply, rollback, and canary paths are Guardian-gated.
- Security capability enforcement blocks unauthorized mutation.
- Dry-run paths do not mutate.
- Rollback token behavior is explicit and tested.
- At least one safe integration can apply, produce a rollback token, roll back,
  and prove the runtime state returned to its expected pre-apply state.
- Non-dry-run integrations fail closed when rollback infrastructure is missing.
- Quarantine behavior is explicit and tested.
- Maintenance can record execution outcomes.
- Homeostasis can verify or observe execution outcomes.
- Audit records are bounded and do not leak private internals.

## Current Gaps To Review

- Confirm every privileged endpoint consumes Guardian approval and Security
  enforcement consistently.
- Expand truthful rollback beyond bounded workflow registration, HMR-backed
  plugin registration, unregister-capable HMR-backed agent registration, and
  Aether Script marker rollback to file-backed integrations if direct file
  mutation is introduced.
- Add richer script-level rollback only after the Aether Script service exposes
  an explicit side-effect rollback contract.
- Extend endpoint claim tests as additional Hub control actions are introduced.
- Replace placeholder signing paths with actual enforced signing where required.
- Add deterministic tests for scan, plan, dry-run, apply, rollback, quarantine,
  and canary paths.
- Ensure Maintenance receives structured execution and verification records.

## Relationship To Maintenance

Maintenance coordinates the loop. Self-Incorporation performs the execution
step. Maintenance may record that Self-Incorporation applied, rejected,
quarantined, or rolled back an approved change, but Maintenance must not perform
the execution itself.

The intended interaction is:

```text
Maintenance cycle
↓
Self-Improvement proposal
↓
Guardian decision
↓
Security enforcement
↓
Self-Incorporation execution
↓
Homeostasis verification
↓
Maintenance outcome record
```

This keeps autonomous evolution governed, observable, and reversible.
