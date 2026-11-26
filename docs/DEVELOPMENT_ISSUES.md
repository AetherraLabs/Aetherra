# Development Issue Register

Established: 2026-11-25. This is Aetherra's standing development issue practice,
across components and roadmap stages. It records unresolved defects, regressions,
uncertain failures and limitations that affect validation or readiness. Alpha
records retain their original identifiers; promotion to another stage does not
close or renumber them.

This is not an accepted-risk register, a runtime incident database, or a source
of runtime authority. Recording an issue does not accept its risk, expand a GO
decision, authorize workarounds or weaken Guardian, Security or signing.

## Record and review practice

- Create or update a stable record when a failure or limitation remains unresolved,
  recurs, or affects a readiness claim. Link it from the relevant PR, design,
  evidence and readiness decision. A GitHub issue may coordinate work, but links
  and summaries must agree about the observed problem and current disposition.
- Preserve initial failures and conflicting observations. Append dated findings
  and source-bound evidence; do not replace a failed run with a later pass.
- Separate established facts, candidate explanations and unknowns. A corrected
  symptom, better diagnostic or successful rerun does not establish root cause.
- Assign an owner role or named maintainer and a concrete next step or review
  gate. Review affected records during relevant PRs, milestone decisions and
  releases; no progress percentage or release version closes an issue implicitly.
- Store compact, inspectable evidence with commands, source revisions, environment
  and actual outcomes. Use opaque identifiers and sanitized codes in ordinary
  logs; keep secrets and raw private conversations out of records and artifacts.
- Never close an unknown-cause record merely because the failure stopped
  reproducing. Describe a narrower correction separately and preserve remaining
  uncertainty and operating limits.

## Required fields

Each record includes:

| Field | Required content |
| --- | --- |
| Identity and state | Stable ID, title, opened/updated dates and explicit status |
| Ownership and scope | Owner, affected subsystem/profile, review gate and current impact |
| Observed versus expected | Concrete behavior and the contract that was not met; uncertainty remains explicit |
| Reproduction and evidence | Exact source revision, environment/config, commands or linked receipt, actual exits and links to retained failures/passes |
| Established versus hypothesized | Proven findings, competing hypotheses and what remains unknown |
| Containment | Current operating restrictions or mitigations and their verified limits; no implied risk acceptance |
| Next action | A concrete investigation, correction or dated review trigger with an owner |
| Closure or disposition | Evidence required for resolution, or an explicitly reviewed deferral/acceptance with scope, rationale and review trigger |

Use a stable `DEV-<component>-<number>` ID for new project-wide records and check
for collisions before assigning it. Retain existing IDs such as `ALPHA-CKPT-001`.
Do not reuse closed identifiers. Compact entries may combine fields into prose
when every required fact remains clear.

## Lifecycle and closure

`OPEN` means unresolved; `INVESTIGATING` means active work; `MITIGATED` means
containment is supported by evidence but the defect or uncertainty remains.
All three remain unresolved for readiness purposes unless that decision explicitly
accepts the documented limit.

`DEFERRED` requires a recorded reviewer/owner, date, rationale, scope and next
review trigger; deferral is not a fix or acceptance by default. Explicit risk
acceptance is a separate reviewed disposition, linked to its applicable risk
record and readiness decision with approving owner, date, scope and review/expiry
condition. Acceptance must not be described as causal resolution.

`RESOLVED` requires the record's closure criteria: a supported explanation and
source-bound correction/verification, or an evidenced external cause with tested
containment and reviewed disposition where appropriate. Record the resolving
revision, verification and review. Keep the record and initial failure evidence.
Reopen it when contradictory evidence or recurrence invalidates the disposition.

Do not modify historical accepted-risk records or silently accept a new risk merely
to satisfy a development issue's fields. Where an approval is absent, state that
it is pending and keep the issue open at its existing scope.

## Development issues and runtime incidents

Development issues describe defects or unresolved engineering questions across
versions. A future runtime incident system should record individual occurrences,
including observation time, runtime identity, evidence, recovery and outcome,
under its own identifiers and retention policy. It may link one or more related
development issues; several incidents can relate to the same defect.

Keep these records separate. An incident's recovery does not prove its underlying
defect is fixed; resolving a development issue does not erase prior incidents.
Do not fabricate incident records from inferred activity, merge them into checkpoint
retention, or introduce a second persistence authority. Implementing runtime
incident tracking is future work under existing Memory, Guardian and Security;
this document establishes development practice only.

## Current records

| ID | Status | Owner | Current question |
| --- | --- | --- | --- |
| [ALPHA-CKPT-001](#alpha-ckpt-001--checkpoint-stop-delay) | OPEN | Runtime/Memory maintainers | Which operation caused the original checkpoint-stop delay? |

## ALPHA-CKPT-001 — Checkpoint stop delay

**Status: OPEN — original slow operation and cause unknown.**
Owner role: Runtime/Memory maintainers. Opened: 2026-11-24.
Last reviewed: 2026-11-25. Review gate: C2a verification and C2b integration;
retain the issue until causal evidence supports closure. The reporting fix is a
separate, established correction; this record tracks the unexplained delay.

### Observed and expected behavior

Supported profile: Windows x64, Python 3.13.7 source runtime, normal full launcher
with isolated synthetic data. Evidence remains bound to the revisions below;
this is not a new fresh-install, browser or live-model verification.

Expected: an orderly observer stop either acknowledges its durable checkpoint
within the existing bounded budget or reports the precise failed/pending outcome,
while retaining ownership until work drains. The expected bound is not evidence
that every underlying operation completed within it.

Observed:

On clean merged-main `4116f5c62f72f14275953a2015b05ad71beb2bee`, the full suite
reported 3,830 passes, 38 skips and one failure (five passing subtests, exit 1).
`test_selected_checkpoint_restores_before_ticks_and_stays_out_of_chat` waited for
`observer-stopped.json`. Restore-before-tick had succeeded; a later checkpoint
row committed without an accepted stop receipt and continuity became uncertain.
The original artifacts do not identify which operation exhausted its budget.

### What is established

The stop/session task could lose its exception, hiding the runtime's actual
failure behind a later missing-file timeout. Commit `007e6510` corrects that
reporting defect and tests sanitized errors; it does not change runtime deadlines
or prove the cause of the original delay. A controlled post-commit delay proves
the reporting path, not that the historical failure had the same cause.

The follow-up's uninstrumented suite passed 3,840 tests, 38 skips and five passing
subtests. Instrumented and isolated passes are additional observations, not a
causal diagnosis or grounds to erase the original failure. See the
[readiness decision](ALPHA_READINESS_DECISION.md#checkpoint-stop-follow-up) and
[source-bound receipt](evidence/checkpoint_stop_followup_2026-11-24.json).

### Containment and next investigation

Next action: Runtime/Memory maintainers retain this issue through the follow-up
integration and C2a verification, collecting discriminating evidence on any
recurrence instead of assigning a cause from passing reruns.

- Keep one-second attempt and bounded shutdown budgets, explicit uncertainty,
  no late receipt acceptance or automatic save retry, and owned work until drain.
- Use stage-coded failures from the reporting follow-up. If it recurs, retain the
  source revision, load/config, monotonic stage timings, opaque checkpoint/row IDs,
  commit and acceptance outcomes, outstanding worker/drain state and actual exit.
  Keep raw payloads, conversations, paths and keys out of ordinary logs.
- Distinguish audit/policy delay, queue/admission/SQLite contention, commit latency,
  receipt validation, observer stop and parent receipt handling. These are
  hypotheses to distinguish, not assigned causes.
- C2b's [failure contract](superpowers/specs/2026-11-24-phase-c2b-checkpoint-contract-design.md)
  must preserve this uncertainty and test crash/timeout/recovery cuts. A contract
  review or C2b implementation does not automatically close this issue.

### Closure criteria

Record a reproduced failure or sufficiently discriminating captured recurrence
that identifies the slow stage and supports a causal explanation. Demonstrate a
focused correction with a regression that fails before it and passes afterward,
or a documented external cause with an exercised containment and explicitly
reviewed disposition. Then verify the supported full-launch path under the
relevant conditions and update the readiness decision with source-bound evidence.

Passing reruns alone, relaxing a timeout, or equating the fixed reporting defect
with the unknown runtime delay does **not** meet these criteria. If the cause
cannot be established, leave this issue open with the supervised operating limits.
