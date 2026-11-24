# Phase B Observe and Propose Implementation Plan

> **Scope:** A focused candidate for observation and proposals. Preserve the separate temporal work and signing controls. The original implementation scope was local; review, commit, push and PR publication were authorized on 2026-11-24. Merge remains a separate step.

**Goal:** Connect real Homeostasis observations to Self-Improvement proposals and durable Maintenance records without granting execution authority.

**Architecture:** The existing Homeostasis metrics bridge resolves the actual registered instances, builds the existing read-only observation report, and sends `selfimprovement.observe_homeostasis`. The launcher adapter delegates diagnosis and proposal generation to the existing Self-Improvement engine. Maintenance records a stable, deduplicated `PROPOSED` cycle; the Observatory shows a safe projection of that real record.

**Tech Stack:** Python asyncio, the existing Registry/Hub, SQLite proposal storage, Maintenance record storage, React Runtime UI.

**Spec:** The user's authorized Phase B observation/maintenance scope, with authority contracts in [Maintenance](../../AETHERRA_MAINTENANCE_SYSTEM.md), [Self-Improvement](../../AETHERRA_SELF-IMPROVEMENT_SYSTEM.md), and the [operator runbook](../../ALPHA_OPERATOR_RUNBOOK.md). [Phase A design](../specs/2026-11-23-core-integration-design.md) remains the core-runtime baseline.

## Global Constraints

- Guardian decides; Security enforces; Self-Incorporation executes approved locked plans. This change stops before those decision/enforcement/execution steps.
- Homeostasis remains `observe_only`; automatic implementation, Self-Incorporation and HMR stay disabled. Observe-only operation must not tune thresholds or weights.
- Use the normal full launcher and real Hub/Registry/Observatory. Preserve strict signing, audit and existing ingress authorization.
- Preserve the pending temporal candidate, original worktree, signing controls and release configuration. Stage 21 stays active; Phase C/D and unattended operation remain outside scope.
- Keep profiles, databases, logs and harness artifacts outside source. Never interpret synthetic pressure as actual runtime degradation.

## Review Focus

- Direct Registry instances and compatibility wrappers must both resolve correctly; a missing producer or consumer remains explicitly unavailable.
- Repeated observations and process restart must preserve stable proposal/cycle identity rather than duplicating records.
- Missing, malformed, stale or nominal observations must not invent evidence or report successful proposal routing.
- A proposed cycle must contain no Guardian decision, security-enforced flag, execution, verification or outcome.
- UI projections must preserve provenance/IDs while omitting raw metric context, private exception details and provider inputs.

## Task 1: Connect observation, diagnosis and durable proposal routing

**Files:** `Aetherra/homeostasis/self_improvement_metrics_bridge.py`, `Aetherra/aetherra_core/engine/self_improvement_engine.py`, and the `SelfImprovementAdapter` in `aetherra_os_launcher.py`.

**Interfaces:** `_forward_metrics()` retains accepted metric forwarding and emits `selfimprovement.observe_homeostasis`; the adapter delegates to `propose_from_homeostasis(observation)`. Existing observation, diagnosis/recommendation and proposal-persistence implementations remain the owners of their work. `get_improvement_status()['homeostasis_flow']` reports observation/proposal/routing counts and last cycle IDs.

- [x] Add focused regressions for direct Registry instances, invalid or absent observations, genuine proposal persistence, repeated-observation deduplication and restart recovery.
- [x] Resolve Registry service objects without requiring a nonexistent `.instance` wrapper; forward only fresh, explicitly measured snapshot fields and count only accepted intake. Dataclass defaults and failed producers must not become pressure evidence or scalar metrics.
- [x] Generate proposals with the existing Self-Improvement diagnosis/recommendation path, persist them in its own database, and route stable cycle IDs through `MaintenanceService.route_proposal`.
- [x] Assert Maintenance status stays `proposed`, with no decision, enforcement, execution, verification or learning result.
- [x] Run the flow regressions and existing Self-Improvement/Maintenance/Guardian tests; retain exact commands, revisions and receipts.

## Task 2: Preserve observation-only behavior and truthful Observatory data

**Files:** `Aetherra/homeostasis/homeostasis_integration.py` and its existing tuning collaborators; the existing operation loop in `aetherra_os_launcher.py`; `aetherra_hub/blueprints/maintenance.py`; Runtime UI service projection and Observatory inspector files.

**Interfaces:** Runtime metrics remain measured inputs; existing Maintenance canonical/alias registrations resolve to the same service. The inspector consumes a bounded read-only projection of actual Maintenance records and observation-flow status.

- [x] Add a regression proving observe-only cycles leave controller thresholds and weights unchanged.
- [x] Suppress automatic threshold/weight adaptation while observing, preserving ordinary observation collection and explicit non-observe modes.
- [x] Resolve default Homeostasis configuration from its package when the launcher runs in a disposable working directory; preserve explicit custom paths and test both cases.
- [x] Refresh Phase B registrations from the launcher's existing lifecycle loop only for the exact owned instances with live tasks or a bounded responsive passive-status read. Cover canonical names and aliases; stopped, failed, replaced or denied services must not receive false liveness, status upgrades or relaxed freshness thresholds.
- [x] Add UI/API tests for canonical Maintenance aliases, actual cycle/proposal references, unavailable state, and excluded sensitive details.
- [x] Verify read-only rendering and truthful unavailable/reconnected states in the browser against the running full launcher.

## Task 3: Verify the normal runtime and record bounded operator evidence

**Files:** Task-local `evidence/phase_b_runtime_probe.py`; this plan; updates to `docs/ALPHA_OPERATOR_RUNBOOK.md`, system/status documents and evidence records.

**Interfaces:** The probe invokes the existing CLI `--mode full --no-gui` entrypoint with only observation and stop instrumentation. HTTP observations use the real `/api/homeostasis/status`, `/api/selfimprove/status`, `/api/selfimprove/proposals`, `/api/maintenance/status` and Runtime UI APIs.

- [x] Launch in a fresh disposable profile with enforcing Guardian, strict signing, audit, offline model cache, no provider credentials and no automated execution. Do not copy configuration into the profile to mask default-path defects.
- [x] Record a natural baseline after Homeostasis and its bridge are running, repeat at 30 seconds, then cross the 180-second stale window with a 215-second checkpoint in both first and restarted processes. Require continuing observation delivery and fresh registrations for the same owned instances; preserve unavailable/degraded values without relabeling them healthy.
- [x] If needed, run the authorized bounded synthetic-pressure diagnostic: replace only the existing `current_snapshot`, invoke the actual bridge once, and restore the previous snapshot in `finally`. Record the diagnostic separately from the natural baseline.
- [x] Compare proposal/cycle IDs across the in-process service, SQLite/record storage, Hub and Observatory projection. Require real persisted proposals and `proposed` cycles without authority/execution fields.
- [x] Leave the runtime available for browser inspection; record the actual Hub/UI ports and browser evidence separately.
- [x] Stop only the owned child through the CLI shutdown path, verify exit zero and listener closure, then restart the same profile in a new process and verify the persisted IDs remain visible.
- [x] Run boot/integration, focused safety, Python/UI quality and appropriate full-suite checks. Verify unchanged source/signing controls and original/temporal workspaces.
- [x] Update operator documentation with observed results and limitations only after the evidence is available. A plan checkbox or diagnostic sample is not a passing acceptance claim.

## Operator Verification

Use the existing [disposable full-runtime procedure](../../ALPHA_OPERATOR_RUNBOOK.md#start-the-full-runtime-in-a-disposable-profile), preserving its strict flags and scoped policy. Keep the profile outside the checkout and record HEAD plus source hashes before starting.

Inspect Homeostasis initialized/running state, bridge forwarding/observation counts, and Self-Improvement `homeostasis_flow`. Read Maintenance `recent_cycles` and proposal IDs from the ordinary Hub routes. A cycle at `proposed` is awaiting the existing governance chain; it is not an approved or executable change. Zero new proposals under nominal input is an honest observation, not a failed producer.

For the explicitly synthetic diagnostic, record the chosen metric/value and timestamp in external evidence, declare only those fields in `raw_data['measured_metrics']`, verify the original snapshot is restored, and compare only the resulting IDs/status/provenance through the Hub and UI. Do not add a diagnostic HTTP route, fabricated service, broad capability grant, or execution approval. Preserve the natural baseline separately and report absent or failed metric producers as unavailable, never as measured degradation.

In the Observatory, select Maintenance and compare its cycle/proposal references with the JSON evidence. Confirm the panel remains read-only. During shutdown it must become unavailable; after restarting the same profile it must reconnect and show the persisted records. Distinguish API evidence from actual browser observations.

Acceptance requires recorded zero child exits, successful restart identity checks, no controller tuning or actuator execution, Guardian enforcing with intact audit, strict signing, Self-Incorporation disabled and automatic implementation off. Preserve failed attempts separately. This exercise establishes one Windows source-runtime profile, not account isolation, unattended operation, an installation matrix or a long-duration stability claim.

## Observed Runtime Checkpoint — 2026-11-24

The external `runtime-04` normal-launch probe completed with exit zero. Both fresh and restarted processes passed natural 30-second and 215-second checkpoints: Homeostasis observations advanced from one to four, all five Phase B canonical/alias registrations resolved to the same live owned instances with fresh heartbeats, tuning parameters stayed unchanged, and actuator attempts/executions/blocks stayed zero. Guardian remained enforcing with intact audit; automatic implementation and Self-Incorporation remained disabled.

The real registry count produced one natural review proposal against the configured service-count target; this is not a claim of runtime degradation. One separately labeled synthetic-pressure snapshot exercised the actual bridge once and was restored. Three `proposed` cycles persisted across restart without decision, enforcement, execution, verification or learning records. Both checkpoint verifiers matched every serialized proposal field against SQLite and Hub, and every full cycle against JSONL. Across restart all full cycles and proposal evidence/content remained identical; only the natural proposal's occurrence count and update timestamp advanced with repeated observations.

Browser verification separately observed the real Observatory before shutdown, its unavailable state with stale references removed, and reconnection to the same records after restart. Browser evidence remains in the separate `browser-observations.json` receipt. Both owned runtime processes exited zero without forced termination, and Hub port 13401 closed after each shutdown. The owned UI server on port 13400 was stopped after final browser verification; both task ports are now closed.

Evidence lives outside source at `D:\Aetherra Labs\.codex-integration-phase-b-20261123\evidence\runtime-04`: `summary.json`, both baseline/215-second, HTTP and content-verification receipts, and `restart-continuity-content.json`. Preserve `runtime-01` through `runtime-03` as superseded diagnostics, not acceptance runs. This verifies one Windows source-runtime profile using bounded SIGINT instrumentation; it does not verify interactive ConPTY shutdown, account isolation, unattended operation or a deployment matrix. Memory continuity remains “Not verified” in this Observatory session.

Status: bounded local Phase B verification passed. The default suite passed 3,455 tests with 38 skips and 5 passing subtests, exit zero; 1,544 frozen source/control hashes match. Focused safety, Python/GUI quality, signing, boot/integration, offline and gpt-4o continuity, and original/temporal preservation checks pass. At this checkpoint the candidate was uncommitted, without hosted CI or merged-main acceptance. See the [decision](../../ALPHA_READINESS_DECISION.md#phase-b-observation-and-maintenance-candidate) and [evidence](../../evidence/integration_phase_b_2026-11-24.json), including the original Hub registration-heartbeat limitation. The later [Hub follow-up](../../ALPHA_READINESS_DECISION.md#hub-heartbeat-follow-up) records its repair and separate verification. No execution authority or broader readiness claim is granted.

## Final PR Review — 2026-11-24

Backend, Observatory/evidence and publication-scope reviews are complete. The
remaining validator scalar-provenance defect was reproduced with real validator
states and fixed without changing its diagnostic interface. The final default
suite passes 3,472 tests with 38 skips and 5 passing subtests; 87 focused flow
regressions, Python quality and two extended normal-launch processes also pass.
All 1,547 source/control hashes match the verification snapshot. See the
[review checkpoint](../../ALPHA_READINESS_DECISION.md#phase-b-pr-review-checkpoint)
and [evidence](../../evidence/integration_phase_b_pr_review_2026-11-24.json).
Commit/push/PR publication is authorized; merge and merged-main acceptance are
separate. Pending temporal work and signing controls remain unchanged.
