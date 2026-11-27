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
| [DEV-CKPT-001](#dev-ckpt-001--extended-run-observer-and-checkpoint-progress-gap) | OPEN | Runtime/Memory maintainers | What caused the original extended-run progress gap? |

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

## DEV-CKPT-001 — Extended-run observer and checkpoint progress gap

**Status: OPEN — historical causal chain unproven.**
Owner role: Runtime/Memory maintainers. Opened and reviewed: 2026-11-25
(America/Denver). Review gate: supervised full-launch continuity verification.
The [delivery receipt](evidence/dev_ckpt_001_delivery_2026-11-25.json) records
source revisions, failed and passing observations, exact IDs and archive hashes.
Its archive identifiers name retained material outside Git, not repository links.

### Original observation and expected behavior

At `c53cc5524304a6a43688bb683b07f9aa6b467390`, the Windows x64,
Python 3.13.7 full launcher used isolated synthetic data, a 300-second interval
and N=10 retention. Earlier samples showed fresh ticks and generation 7
acknowledged. Inspection after the reported closure found ten contiguous valid
periodic members, no orderly-stop member and no prune decision. Generation 10
advanced at 18:44:05 UTC; 121 more microreflection decisions followed through
18:46:08 UTC, and registry audit activity continued to about 19:02 UTC.

At generation 10, capacity still permitted the next advance and retention was
not needed. Neither the anticipated eleventh submission nor its retention
boundary was observed. Final observer state, process exit, receipt acceptance
and why periodic progress ended remain unknown. Fresh eligible completed ticks
should permit subsequent periodic attempts. This observation establishes no
retention block, corruption, deadline failure or audit-cost attribution.
[ALPHA-CKPT-001](#alpha-ckpt-001--checkpoint-stop-delay) separately remains OPEN
for its original unexplained stop delay.

### Established mechanisms and bounded corrections

A real-component reproduction on `c53cc552` showed that a registry-owned
status-wait expiry could stop an otherwise healthy observer without a final
save. `32d93be2` tolerates only that owned expiry, preserves normal refresh
coalescing and refuses late heartbeat application. Worker-delivered timeout
errors still propagate; owner replacement and authorization failures still
follow their existing failure paths. The original session lacks the exception
and terminal state needed to attribute its gap to this mechanism.

Controlled signed Core/Memory testing on `32d93be2` separately showed a due
synchronous tick delaying consumption of a timely sealed receipt beyond its
cutoff. The owner correction (`a3da0f00`, fixture updates through `3897c5a6`)
services an already-open receipt window before the next due tick. It preserves
the one-second attempt and two-second stop bounds, stop interruption, timely
acceptance, single-worker capacity and ownership until drain. The failed live
generation-10 seal and decisive owner poll were not captured.

At `4d9c8f8e`, audit append can reuse a verified signed prefix only when the
actual prefix bytes and effective signing-key digest match. Every signed suffix
record is validated. The process-local cache holds at most 64 resolved paths
and expires absolutely 600 seconds after cold validation. Independent integrity
checks always verify from genesis. Every append still reads the complete file
and hashes bytes; cold starts, expiry, eviction, replacement and key changes
can require full validation. Neither constant latency, cross-process ledger
serialization nor arbitrary large-ledger performance is established.

### Retained failures and final verification

| Run and source | Actual result and remaining limit |
| --- | --- |
| Extended-01, `32d93be2` | Failed at 50.5 minutes: generation 10 committed, last acknowledgment 9, continuity uncertain. Observer remained running; no retention or restart gate reached. Harness runtime exited zero; supervisor separately terminated and drained a job with an unidentified remaining process. |
| Extended-02, `3897c5a6` | Create phase passed: 11 acknowledgments over 65 minutes and continued ticks after retention needed approval. Full run failed independent closed-port readback after zero runtime exit; restart did not run. A reproduced Windows probe false negative does not establish the original cause. |
| Extended-03, `3897c5a6` | Create phase and drain passed. Epoch-2 restart selected intact generation 11 but blocked before Core apply with `continuity_restore_failed` and zero attempted ticks. Original refusing guard remains unknown. |
| Disposable recovery probe, `3897c5a6` | Separate copied profile acquired epoch 3, prepared state, then measured deadline expiry during policy recheck; apply and ticks remained blocked. It does not diagnose the original epoch-2 guard. |
| Extended-04, `4d9c8f8e` | Passed at 300-second cadence: 11 timely acknowledgments in 65 minutes; 564 ticks after the retention latch; exact generation-11 restore at epoch 2 before a Core tick or event. Both harness SIGINT stops drained, exited zero and closed listeners; retention blocked both stop saves. |
| Physical-01, `4d9c8f8e` | Uninstrumented real Ctrl+C committed generation 1, verified signed audits and exited zero with a closed listener. Last direct sample was pending; terminal acknowledgment unknown. Strict gate failed and session two was skipped. |
| R3 physical pair, `4d9c8f8e` | Separately instrumented full CLI: two genuine operator Ctrl+C events acknowledged generations 1 and 2, with exact same-store restore at epoch 2, signed/durable joins, zero exits and closed listeners. |

R3 reads existing cached owner state after real stop and Memory drain, before
Hub teardown, and publishes bounded packets after CLI unwind. It establishes
acknowledgment for those new processes only. The same browser tab reconnected
automatically, displayed the restored row, advanced ticks and cleared current
evidence after both stops; actions stayed disabled. Its 54.23-second gap is a
host-clock observation estimate. Durable prior acceptance, prior termination
and offline duration remain unknown; aggregate runtime status is incomplete.
Cleanup found zero owned processes or listeners, without forced runtime cleanup.

Final source `4d9c8f8e455b87624e6918dbcc784577950af4fb`, product tree
`de52a848d9e410e5829d4406c8527cd71263e92d`, passed 4,136 tests with 38 skips,
45.29% coverage against 22%, and quality, boot and integration checks. Ten
actual GPT-4o turns used zero fallback; synthetic record IDs joined write,
restart retrieval and provider input. Two separate local data directories
verified empty retrieval/provider evidence in the other profile, not account
isolation. Checkpoint data stayed outside chat evidence.

### Disposition, next action and closure

Source and final independent reviews found no outstanding Critical or Important
issue. Two Minor findings remain deferred: ambient signing variables can mask
a key-source test fixture (the recorded runner cleared them), and malformed
submissions can omit final observer/shutdown fields in the legacy helper's
failure summary (raw evidence is retained and verification fails closed).

Runtime/Memory maintainers must capture cached observer, ownership and retention
state plus scheduling, admission, authorization, commit, receipt and drain
timings on recurrence. Close only with a supported historical explanation and
source-bound verification, or a separately reviewed bounded disposition.
Passing reruns do not meet that gate. DEV-AUDIT-001 remains OPEN for cold and
linear audit costs; DEV-OBS-001 remains OPEN for aggregate status reporting.
These are separate tracked items, not sections added by this delivery.

Strict Guardian, Security, signing, existing deadlines, N=10 retention approval,
64 KiB payload cap and single-worker Memory authority remain unchanged. No late
receipt acceptance, automatic checkpoint retry, reacquisition or pruning approval
is introduced. At the original verification checkpoint C2b was unmerged.
Update 2026-11-26: the C2b stack and #368 are merged, released at
`56623003675bc99f9e3dfadf15b6254beb183b59`; that merge does not establish the
historical cause or close this issue. The existing supervised internal-alpha
boundary stands; unattended and production operation remain NO-GO.
