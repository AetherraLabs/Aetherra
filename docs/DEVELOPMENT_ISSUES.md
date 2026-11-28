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
| [DEV-AUDIT-001](#dev-audit-001--signed-audit-scalability) | OPEN | Security/Runtime maintainers | What are measured cold/warm and concurrent-writer limits? |
| [DEV-OBS-001](#dev-obs-001--aggregate-observatory-status) | OPEN | Runtime UI/Observability maintainers | Which aggregate and prior-session states can be established? |
| [DEV-HOMEOSTASIS-001](#dev-homeostasis-001--watchdog-shutdown-lifecycle) | OPEN | Homeostasis/Runtime maintainers | Which outstanding await causes the shutdown watchdog error? |
| [DEV-STORM-001](#dev-storm-001--skipped-persistence-lifecycle-check) | OPEN | Memory/STORM maintainers | Why did the lifecycle recall return no results? |
| [DEV-CI-001](#dev-ci-001--capabilities-job-timeout-before-a-result-summary) | OPEN | CI/Runtime maintainers | Which operation prevented the Linux capability job from completing? |
| [DEV-CI-002](#dev-ci-002--personal-continuity-write-session-http-503) | OPEN | Hub/Engine and CI maintainers | Why did a personal-continuity write turn return HTTP 503? |
| [DEV-QFAC-001](#dev-qfac-001--validator-metric-provenance) | OPEN | Hub/QFAC and Runtime maintainers | Why do full-mode validator metrics discard source values and availability? |
| [DEV-SELFINC-001](#dev-selfinc-001--verification-and-planning-trust) | OPEN | Security/Runtime maintainers | How will strict artifact evidence govern persisted planning trust? |
| [DEV-SELFINC-002](#dev-selfinc-002--startup-ownership-and-opt-in) | OPEN | Runtime/Kernel maintainers | Which configured instance owns Self-Incorporation startup and status? |

## ALPHA-CKPT-001 — Checkpoint stop delay

**Status: OPEN — original slow operation and cause unknown.**
Owner role: Runtime/Memory maintainers. Opened: 2026-11-24.
Last reviewed: 2026-11-26 (traceability only). GitHub: [#369](https://github.com/AetherraLabs/Aetherra/issues/369).
Review gate: checkpoint changes, recurrence and readiness reviews;
completed C2a/C2b integration does not close this record. Maintainers must
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

Next action: Runtime/Memory maintainers retain this issue through subsequent
checkpoint/readiness reviews, collecting discriminating evidence on any
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
Owner role: Runtime/Memory maintainers. Opened: 2026-11-25
(America/Denver); traceability reviewed: 2026-11-26.
GitHub: [#370](https://github.com/AetherraLabs/Aetherra/issues/370). Review gate: supervised full-launch continuity verification.
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
Their standalone records below preserve these limits; this documentation review
does not resolve them.

Strict Guardian, Security, signing, existing deadlines, N=10 retention approval,
64 KiB payload cap and single-worker Memory authority remain unchanged. No late
receipt acceptance, automatic checkpoint retry, reacquisition or pruning approval
is introduced. At the 2026-11-25 candidate checkpoint C2b was unmerged.
The [merged-main evidence review](ALPHA_READINESS_DECISION.md#c2b-merged-main-evidence-review-2026-11-26)
records subsequent integration without resolving the original causes. The
existing supervised internal-alpha boundary stands; unattended and production
operation remain NO-GO.

## DEV-AUDIT-001 — Signed audit scalability

**Status: OPEN — cold/linear costs and cross-process limits uncharacterized.**
Owner: Security/Runtime maintainers. Opened: 2026-11-25; reviewed: 2026-11-26.
GitHub: [#371](https://github.com/AetherraLabs/Aetherra/issues/371).
Review gate: audit-path changes and any scale/readiness claim.

Observed at candidate `4d9c8f8e455b87624e6918dbcc784577950af4fb`
(Windows x64, Python 3.13.7, signed synthetic full-launch profiles): append can
reuse a verified prefix only with matching bytes and effective signing key;
64 paths and an absolute 600-second expiry bound the process-local cache.
Every append still reads/hashes the full file; cold validation, expiry, eviction,
replacement and key changes can require genesis verification. Independent
integrity checks always start at genesis. Expected: measured supported limits
without weakening signature verification or claiming constant latency.

The [delivery receipt](evidence/dev_ckpt_001_delivery_2026-11-25.json) preserves
parent `3897c5a6`'s two expected assertion failures and 30 committed focused
passes at `4d9c8f8e` (exit 0), plus the 537-test affected precommit selection.
These verify the bounded cache correction, not large-ledger performance or
cross-process serialization. Audit cost is not established as the original
checkpoint failure's cause; that uncertainty remains in the CKPT records.

Containment: retain supervised operation, independent genesis checks, signing,
existing deadlines and explicit uncertainty; no performance risk acceptance.
Next action/closure gate: owner benchmarks cold/warm paths, expiry/replacement
and concurrent writers with ledger size, keys/configuration, command, source,
latency distributions and actual failures retained. Resolve only after supported
limits or a correction are verified and maintainer disposition is recorded.
Reviewer approval and engineering closure remain pending.

## DEV-OBS-001 — Aggregate Observatory status

**Status: OPEN — aggregate status and durable prior-session facts incomplete.**
Owner: Runtime UI/Observability maintainers. Opened: 2026-11-25;
reviewed: 2026-11-26. GitHub: [#372](https://github.com/AetherraLabs/Aetherra/issues/372).
Review gate: status aggregation changes and restart/disconnect readiness claims.

At candidate `4d9c8f8e455b87624e6918dbcc784577950af4fb`, the Windows source-runtime
R3 physical pair used reviewed external instrumentation and two genuine operator
Ctrl+C events. The [delivery receipt](evidence/dev_ckpt_001_delivery_2026-11-25.json)
links source, configuration, commands/archives and signed/durable joins: both
runtime/redirector exits were zero with closed listeners. The same browser tab
reconnected, showed the restored row, advanced ticks 6 to 21 and cleared current
evidence after both exits; actions stayed disabled. The observed 54.23-second
host-clock gap is not verified offline duration. Durable prior acceptance,
prior termination and a complete aggregate runtime state remain unknown.
The earlier uninstrumented physical-01 failed its strict terminal gate and
skipped session two; R3 does not supply its missing acknowledgment.

Expected: aggregate views distinguish established, unknown, stale and offline
facts across restart/disconnect/shutdown. Cause of the incomplete aggregation
has not been diagnosed. Containment: keep actions disabled and unknown fields
explicit; do not infer acceptance or termination from a disconnected browser.
Next action/closure gate: owner defines evidence-backed aggregation and verifies
restart, disconnect and shutdown, including clearing stale state and preserving
unknowns, without enabling control actions. Maintainer review of those receipts
is required; no risk acceptance or engineering closure is recorded.

## DEV-HOMEOSTASIS-001 — Watchdog shutdown lifecycle

**Status: OPEN — outstanding await and shutdown cause unknown.**
Owner: Homeostasis/Runtime maintainers. Opened/reviewed: 2026-11-26.
GitHub: [#373](https://github.com/AetherraLabs/Aetherra/issues/373).
Review gate: normal-launch shutdown changes and any lifecycle acceptance claim.

At released main `56623003675bc99f9e3dfadf15b6254beb183b59`, all three Windows
Python 3.13.7 full-launch processes in the 660-second automatic continuity run
logged `Event loop stopped before Future completed.` as a fatal watchdog-thread
error during harness SIGINT shutdown. Each process nevertheless exited zero,
closed its listener and needed no cleanup kill. Expected: bounded cooperative
settlement without orphan work or a watchdog error; process exit alone does not
prove that contract. The outstanding await and causal sequence are unidentified.

The [sanitized review receipt](evidence/c2b_merged_main_review_2026-11-26.json)
records the exact smoke command, revision, synthetic profile, exit outcomes and
hashes of retained logs/receipts. This is archived evidence review, not a fresh
reproduction or physical keyboard test. Checkpoint acknowledgments in that run
do not resolve the watchdog error or either historical CKPT cause.

Containment: preserve supervised operation and existing checkpoint/security
contracts; no workaround or risk acceptance is established. Next action/closure
gate: owner captures the pending await on normal-launch shutdown, establishes
cause, verifies bounded cooperative settlement and absence of orphan work or
watchdog errors, and obtains maintainer review with retained failures. Status
stays OPEN until that evidence and disposition exist.

## DEV-STORM-001 — Skipped persistence lifecycle check

**Status: OPEN — empty recall observed; underlying cause unproven.**
Owner: Memory/STORM maintainers. Opened/reviewed: 2026-11-26.
GitHub: [#374](https://github.com/AetherraLabs/Aetherra/issues/374).
Review gate: STORM persistence/recall changes and any affected readiness claim.

Merged main `592c462244252abe5626b825e642f3977f84a431`'s Windows Python 3.13.7
full suite exited zero with 4,158 passed and 38 skipped. One retained skip is
`tests/capabilities/test_storm_acceptance.py::TestSTORMProductionReadiness::test_storm_full_lifecycle`
(line 306): `Memory system not returning results - persistence issue`.
The test stores four synthetic memories, checks non-null remember results,
then skips on empty `storm_hybrid` recall items. Its fixture isolates temporary
storage paths and closes handles. The recorded skip does not establish a general
Memory failure, a persistence root cause or the complete effective STORM config.
Expected: the supported lifecycle configuration reaches its recall/quality
assertions, or an evidenced scope limitation is explicitly reviewed.

The [sanitized review receipt](evidence/c2b_merged_main_review_2026-11-26.json)
binds the exact suite command, source, skip and actual outcome to retained log
hashes. No new reproduction or corrective run was performed in this review.
Containment: preserve the skip and distinguish it from the two separate
`STORM not enabled` skips; do not count this lifecycle as verified.
Next action/closure gate: owner records effective supported configuration,
reproduces or explains the empty recall, adds a regression for an established
correction and documents scope with maintainer review. A passing rerun or silently
removing the skip cannot close this unknown-cause record; no risk acceptance.

## DEV-CI-001 — Capabilities job timeout before a result summary

**Status: OPEN — operation-loop cancellation defect captured; historical attribution remains limited.**
Owner: CI/Runtime maintainers. First retained observation: 2026-11-25
(America/Denver); registered: 2026-11-26; reviewed: 2026-11-27. Severity unknown.
GitHub: [#381](https://github.com/AetherraLabs/Aetherra/issues/381).
Review gate: recurrence, capability-test lifecycle/CI changes and affected
verification claims. This consolidates the unresolved observation already
preserved in PR #368 and the similar visible timeout in PR #379.

The [four-log receipt](evidence/ci_capabilities_timeout_2026-11-26.json) retains
exact head/base/merge-checkout revisions, links and SHA-256 hashes. Both Linux
jobs ran `pytest -q -o addopts= tests/capabilities` on Ubuntu 26.04 image
`20261116.202.1`, Python 3.11.18, pytest 9.2.0 and pytest-asyncio 1.5.0,
with `AETHERRA_QUIET=1` and test defaults. The workflow dynamically installs
pytest/pytest-asyncio and requirements.txt; identical inputs do not establish
identical effective environments. Expected: complete the selected tests and
exit normally within the existing five-minute step limit.

| Source-bound observation | Actual outcome |
| --- | --- |
| PR #368, checkout `ce7a5e023d8740fa4aa482b8d856eaeff2b2bc47`, [failed job](https://github.com/AetherraLabs/Aetherra/actions/runs/45756195270/job/139695259592) | Last visible progress 82%, then five-minute timeout without a final summary, active node or stack. Runner terminated pytest and a Python process. |
| Same checkout, [retry](https://github.com/AetherraLabs/Aetherra/actions/runs/45756195270/job/139698660686) | 171 passed / 4 skipped in 45.98 seconds; subsequent SSE 8 passed. Original failure remains unexplained. |
| PR #379 head `6a1b978a`, checkout `398604181ca866b0cb0f0a218dbbf16738f0ac9f`, [failed job](https://github.com/AetherraLabs/Aetherra/actions/runs/45937143595/job/140302854422) | Last visible progress 82%, then five-minute timeout without a final summary, active node or stack. Runner terminated pytest and a Python process. |
| Same checkout, [bounded retry](https://github.com/AetherraLabs/Aetherra/actions/runs/45937143595/job/140306021904) | 171 passed / 4 skipped in 62.42 seconds; subsequent SSE 8 passed in 32.76 seconds. Original failure remains unexplained. |

The blocked test/teardown, pending work and cause are unidentified. Percentages
do not identify STORM. PR #324's diagnosed post-summary interpreter-shutdown
hang is historical comparison, not an established mechanism here. The Windows
watchdog error (#373) and STORM empty-recall skip (#374) remain separate records.
PR #379's runtime, tests, dependency manifests and workflows match its main
base, but that does not prove documentation irrelevant: the static-security
capability test scans repository contents. Neither retry establishes a fix,
shared cause, accepted risk or broader readiness.

The [2026-11-27 diagnostic receipt](evidence/dev_ci_001_linux_capture_2026-11-27.json)
records PR #387 heads `3a1cea7ed9ae43b897a611a07ce4d33f11ea156a` and
`1031ab4dd179006ac1044ec71c996c7af25bee3e`: each standalone capability selection
completed with 171 passed / 4 skipped (45.67 and 47.39 seconds). Both used Python
`-u` and pytest `-vv`, changing buffering and verbosity as well as adding
instrumentation. Their 30-second samples showed short, completed analytics
fixture teardowns; neither identifies the historical blocked boundary. The
first build-test job failed later at docs consistency; the second build-test
job passed. Selected environment versions matched, but retained install lines
show filelock 4.3.1 versus 4.3.2; this drift has no established causal role.

The second head's [strict quality job](https://github.com/AetherraLabs/Aetherra/actions/runs/46079599000/job/140775316625)
failed separately: pytest exceeded `TEST_TIMEOUT=900` and exited 124. The final
output had 145 progress dots (17%, 35%, then one dot), with no active node,
stack or result summary. The diagnostic receipt retains its exact command and
source-log hash. This gate uses `requirements-ci.lock`, coverage and a broader
test selection; a common cause with the five-minute capability timeout is not
established. The overall CI run failed despite its successful build-test job.

A [controlled Homeostasis cancellation receipt](evidence/dev_ci_001_homeostasis_cancellation_2026-11-27.json)
records six failures on Python 3.11.18 at `1d325080`: both an explicitly consumed
cancellation and a genuine `asyncio.wait_for` completion race left controller or
supervisor run intent open while `stop()` awaited the worker. The worker then
slept; the controller-step case also entered action processing after stop began.
The same Linux job completed the normal capabilities selection: 171 passed /
4 skipped in 44.77 seconds, with no live owned processes before cleanup.

Commit `b9ab95880d4cbec5b06db3e3b2a441b5da82f84d` adds twelve runtime lines:
close component run intent before task draining and recheck it after awaited
controller steps/actions and supervisor cycles. Asynchronous resource teardown
order and Guardian/actuator checks are unchanged. Seven local shutdown/positive
loop regressions pass; an earlier selection of six shutdown cases plus existing
Homeostasis, Guardian, observation and integration checks passed all 234 tests.
The receipt binds those pre-commit working-tree checks to the committed runtime
source hashes. Final exact-head CI evidence belongs to
[PR #387](https://github.com/AetherraLabs/Aetherra/pull/387).

The separate full Quality Gates workflow remained active on `1031ab4d` and
`e76f8baf` after the narrower selections completed. Those unfinished observations
have no active-node evidence; elapsed time alone does not establish a cause.
The same diagnostic supervisor now covers that formerly unbounded pytest
invocation, with a new 900-second pytest deadline and a 1,500-second outer budget.
Production signing/source/public-key verification steps are unchanged.

The [registry-cleanup receipt](evidence/dev_ci_001_registry_cleanup_2026-11-27.json)
retains the first instrumented full-gate result at `49b28741`: 3,177 passed /
9 skipped, but one live registry daemon survived the quality command. PID 6083's
Linux stack identified the Flask/Werkzeug registry server; its creation overlapped
the HMR metrics test, which lacked cleanup. A real-spawn regression against that
exact test body reproduced the leak on both normal and assertion-failure paths.
The test now releases its owned presence resources and registry in `finally`.
The supervisor also fails a zero-exit command if owned descendants remain alive
after a short natural-exit grace; its subsequent cleanup cannot mask the leak.
This is a separately established lifecycle defect, not proof of the original
five-minute timeout's cause. The same source's seven Linux Homeostasis regression
cases and strict gate (414 passed / 5 skipped) passed. Final exact-head results
remain linked from PR #387.

The [captured strict stall at `b5867797`](evidence/dev_ci_001_strict_stall_2026-11-27.json)
failed with pytest exit 124 at the unchanged 900-second deadline. The active call
was `test_self_maintenance_services_registration_and_basic_ops`; fourteen async
samples show it awaiting its canceled boot task at line 78. The bounded task
sample omitted that boot task, leaving its own awaited operation unresolved.
The same head's standalone capabilities passed 171 / four skips and had no live
owned survivors. The natural strict failure remains a blocker; background
Homeostasis stacks alone do not establish its cause or historical attribution.
The same head's full gate reached the same join and timed out at 900 seconds.
The [controlled launcher correction](evidence/dev_ci_001_launcher_cancellation_2026-11-27.json)
checks pending startup cancellation before announcement/operation, preserving
cleanup-only checkpoint intent. Four failing cases became passing cases; the
23-case selection includes normal orderly SIGINT and existing shutdown controls.
Awaited-Task links improve the bounded capture. Neither this controlled result
nor a future passing rerun proves the missing natural await or closes historical
uncertainty.

The [5c1a3806 capability capture](evidence/dev_ci_001_operation_cancellation_2026-11-27.json)
then identifies a concrete continuation defect for that attempt: the directly
captured boot task had cancelling=1 while sleeping inside the operation loop in
three samples spanning 170 seconds. The test phase remained self-maintenance.
The runtime did not recheck cancellation after awaited heartbeat/status work.
Nine owner-loop lines now perform those checks, routing through the existing
ordinary/first-SIGINT/repeated-interruption policy. Regression RED was 10 failed /
9 passed; GREEN was 19 passed, with 132 lifecycle/heartbeat controls passing.
The exact cancellation-consuming dependency remains unsampled; earlier absent
stacks are not retroactively attributed. Source hashes, job/artifact digests,
trace limits and final PR verification references remain in the receipt.

A separate [full-suite Temporal test-clock assertion](evidence/ci_temporal_test_clock_2026-11-27.json)
was reproduced with a fixed monotonic seed and corrected in test scheduling.
Real Memory/Guardian/registry assertions remain; no runtime timing changed.
It is retained separately and is not assigned the launcher-stall cause.
The next full run exposed an [incomplete continuity test double](evidence/ci_continuity_test_api_2026-11-27.json);
its test-only API correction preserves the runtime cancellation guard and all
checkpoint-intent assertions.

Post-merge Windows verification exposed a separate [nested-pytest coverage reporting timeout](evidence/ci_windows_diagnostic_coverage_2026-11-27.json).
Its synthetic test and teardown completed before the 30-second deadline;
subsequent probes identified expensive repository-wide coverage reporting.
The test-only correction measures the diagnostic module, asserts the real report
scope, and preserves production coverage checks and all existing deadlines.
The original timeout stack remains unavailable. This correction does not resolve
historical runtime attribution or close DEV-CI-001 based on passing reruns.

Containment retains the five-minute capability limit, existing 900-second strict
pytest deadline, original failures and separate capture outcomes. This controlled
correction does not establish the historical blocked node or a shared cause.
Continue the [bounded Linux diagnostics](CI_CAPABILITIES_DIAGNOSTICS.md); close
this record only with supported historical attribution or an evidenced external
cause and explicit reviewed disposition. Passing reruns alone do not close it.
Supervised-alpha limits, Guardian/Security, signing and approval boundaries remain
unchanged.

Shutdown follow-up: [PR #391](https://github.com/AetherraLabs/Aetherra/pull/391)
retains a new [Linux capture and controlled batch regression](SHUTDOWN_CANCELLATION_FOLLOWUP.md#additional-ci-shutdown-boundary)
on `3822a021`. The QFAC capability test awaited cancelled boot cleanup, blocked on the
Homeostasis controller's kernel action wait. Closing run intent left unstarted actions
queued; a consumed cancellation could enter another action wait during stop. Clearing
that pending queue is covered by two red/green regressions and fresh launch checks.
This does not close the historical record or prove every timeout shared this cause.
The five-minute gate remains enforced; see the PR for final-head CI and limitations.

## DEV-CI-002 — Personal continuity write-session HTTP 503

**Status: OPEN — cause and severity unknown.**
Owner: Hub/Engine and CI maintainers. First observed/registered/reviewed:
2026-11-26 (America/Denver). GitHub: [#382](https://github.com/AetherraLabs/Aetherra/issues/382).
Review gate: recurrence, affected Hub/Engine/test-lifecycle changes and continuity
verification claims. This HTTP assertion failure is separate from DEV-CI-001's
capability timeouts and the original six C2b records.

[Failed CI Quality Gates job](https://github.com/AetherraLabs/Aetherra/actions/runs/45939281664/job/140309611225)
ran head `9f3f97dbf2fdf431906cb9bbc0eae5f0b5a5dced`, merge checkout
`7e8e8d9597c799b69cc10e75e5ff7641818876a0` into main `5662300`.
The [original-failure receipt](evidence/ci_personal_continuity_503_2026-11-26.json)
records the exact command, configuration and retained job-log hash: Ubuntu 26.04
image `20261116.202.1`, Python 3.11.18, requirements-ci.lock, pytest 9.1.0,
pytest-asyncio 1.4.0 and coverage 7.14.1; pinned embedding model provisioned,
offline flags and a synthetic enforcing full-runtime profile.

Expected: each sequential write turn returns HTTP 200 before restart/recall
assertions. Observed: `test_personal_fact_survives_full_runtime_restart` failed
at line 201 while checking its write-session results (caller line 209). One of
six `POST /api/ai/ask` responses was 503; the ordinal and response reason are
unknown. The child returned zero; empty initial history and `stopped` assertions
passed. That flag alone does not establish settlement of every subsystem.
The selection ended with **1 failed, 4 passed, 1 skipped in 272.09 seconds,
exit 1**. Restart/recall in this test was not reached; this was not a timeout.

Artifact publication was skipped and the run's artifact list was empty at
inspection. Configured upload paths also omit the temporary child result/runtime
files. The published log cannot establish response body/error code, request
lease/queue state, readiness at failure or cause. PR #351's intentional busy
responses and PR #368's separate strict-architecture 503/controlled `hub_busy`
race do not identify this failure. No connection to DEV-CI-001, STORM or checkpoint
failures is established. Unchanged runtime/test/workflow content does not prove
documentation or environment effects irrelevant.

Containment: preserve the failing assertion, existing deadlines, fail-closed
responses and supervised-alpha limits; no runtime fix, automatic retry or gate
change is introduced by this documentation. Next action: owner captures a
bounded reproduction with sanitized request ordinal/status/error code, readiness
and lease/queue state, monotonic timing, dependency/configuration, child exit and
artifact hashes. Keep later observations on #382 separate from the immutable
original-failure receipt. Close only with a supported cause and verified focused
correction/regression, or an evidenced external cause with tested containment
and explicit reviewed disposition. A passing rerun alone cannot close this
record or establish risk acceptance or broader GO. Guardian, Security, signing
and approval boundaries remain unchanged.

## DEV-QFAC-001 — Validator metric provenance

**Status: OPEN — full-launch override and missing-data ambiguity reproduced.**
Owner: Hub/QFAC and Runtime maintainers. Opened/reviewed: 2026-11-27.
GitHub: [#389](https://github.com/AetherraLabs/Aetherra/issues/389); inventory RI-012.
Review gate: P1 metric truthfulness correction and any QFAC readiness claim.

At main `3253893604a5cf3fb0417f95de3acf51131650f1`, Windows Python 3.13.7 full-launch
strict-flags test profiles set `VALIDATOR_FAKE=1` and clear override counts. Real Hub
HTTP metrics replaced a labeled registry fixture's 17/4 counts with 0/0; changing
only the override to zero restored 17/4. Missing/throwing sources also exported 0/0.
Expected: preserve source observations and distinguish unavailable from measured zero.
[Trace, exact commands and receipts](RUNTIME_EVIDENCE_P0_TRACE.md) retain profiles,
source, before/control outputs, exits and limitations. No real validator was registered
at boot or owned producer found; loss of actual backend measurements is unverified.

Cause of the fixture override is established in launcher/consumer source and controlled
runtime observation. External metric consumers and optional profiles remain unknown.
Containment: do not use these counters as validation/readiness evidence; no runtime
workaround or acceptance is granted. Next: owner adds normal-launch negative tests,
corrects override/availability semantics with truthful compatible output, and reviews
strict/missing/failing/optional profiles. Closure requires reviewed source-bound
before/after evidence, not schema presence or a passing rerun. Five-minute CI timeout,
Guardian, Security, signing and Memory remain unchanged.

## DEV-SELFINC-001 — Verification and planning trust

**Status: OPEN — strict artifact evidence is not established by legacy planning trust.**
Owner: Security/Runtime maintainers. Opened/reviewed: 2026-11-27.
GitHub: existing [#67](https://github.com/AetherraLabs/Aetherra/issues/67); inventory RI-013.
Review gate: P1 authority correction before P2 migration or an incorporation readiness claim.

At the same main revision and isolated Windows environment recorded in the
[P0 trace](RUNTIME_EVIDENCE_P0_TRACE.md), real discovery, explicit classification and
evaluation persisted an unsigned utility as TRUSTED and planned a high-priority action.
Native Windows reported `verified=false`; a POSIX path-string model returned true while
reporting no signature. The latter is not native Linux execution. Reopening SafetyIndex
retained the decision; another evaluation skipped it. Expected: strict artifact trust
and verification claims derive from current supported verification evidence, not paths.

Established: path-based legacy evaluation feeds SQLite/planning; the separate security
helper is not invoked on that path. Startup discovery alone does not call the evaluator.
Tested unauthenticated Hub, disclosure and unapproved Guardian requests were denied,
with zero execute calls. A universal authorization bypass is **not established**; approved
policies, artifact classes, native Linux and stale-policy handling require review.
Release signing is a separate authority. Detailed sensitive findings follow SECURITY.md.

Containment: retain explicit-disable supervised profiles, fail-closed action authority
and existing #67 requirements; do not treat a trust tier as cryptographic proof. Next:
owner reuses existing verifiers, reviews persisted-decision freshness and adds native
caller/unsigned/invalid/valid-signature tests plus denial before mutation. Closure needs
reviewed evidence for supported artifact types, persistence and action boundaries.
No passing rerun, fallback, planning success or release signature closes this record.

## DEV-SELFINC-002 — Startup ownership and opt-in

**Status: OPEN — launcher and kernel opt-in defaults disagree.**
Owner: Runtime/Kernel maintainers. Opened/reviewed: 2026-11-27.
GitHub: existing [#42](https://github.com/AetherraLabs/Aetherra/issues/42); additional RI-013 finding.
Review gate: normal-launch configuration/registration/shutdown and alpha reviews.

The [P0 trace and receipts](RUNTIME_EVIDENCE_P0_TRACE.md) bind main
`3253893604a5cf3fb0417f95de3acf51131650f1` to Windows Python 3.13.7 full-launch runs.
With the enable flag unset, the launcher-held object was disabled while a different
kernel-created registered instance was enabled, scanned and reported healthy via Hub.
Explicit 0 retained one disabled instance; explicit 1 had one enabled identity at
observation after replacement. Expected: one configured owner with consistent opt-in,
registry identity and truthful status. Earlier launcher-only static review in #42 is
preserved; the runtime result adds the missing kernel path.

The default mismatch/re-registration cause is source-confirmed. Separately, an
explicit-disable diagnostic completed its observations and wrote worker exit 0 but
failed to terminate within the 60-second stop limit; the harness killed it (exit 1).
A later repeat exited cleanly. The original shutdown cause remains unknown; no common
cause with DEV-HOMEOSTASIS-001, DEV-CI-001 or CKPT failures is established. This is a
retained lifecycle limitation under investigation, not proof that disabling causes hangs.

Containment: explicit 0 prevented discovery in the measured profile, while action gates
remained enforced; no new GO follows. Next: owner reconciles kernel/launcher service
ownership and unset/0/1 semantics, tests identity/scan/status/settlement, and captures
stacks if the shutdown delay recurs. Close only after focused correction and reviewed
lifecycle evidence; disposition of the retained unknown delay must remain explicit.

Publication review observation (2026-11-27): probe-04 reproduced the shutdown timeout
with the enable flag unset; explicit 1 and 0 exited cleanly. At the 50-second dump,
the main thread waited in `threading._shutdown`; other stacks showed the Homeostasis
watchdog event loop, stdlib scheduler loop and Hub `serve_forever`/selector. These
are observed stacks, not proof of the initiating cause or individual responsibility.
The profile-specific hypothesis is unsupported. Retain both timeouts and their
separate receipts; do not mark this lifecycle limitation resolved by clean siblings.

Shutdown follow-up (2026-11-28): [controlled before/after evidence](SHUTDOWN_CANCELLATION_FOLLOWUP.md)
now establishes one cancellation escape path on main `9c2e7708`: a manual
`CancelledError` raised from `cancelling()` left the actual task cancellation queued.
It was then delivered during Hub teardown, skipping later owned shutdown and leaving
the non-daemon watchdog alive. An identical real-CLI signal reproduced the hang before
correction and completed teardown after a yield at the existing guards; 18 deterministic
regression cases failed before and pass afterward. This is a focused correction supported
by intervention, not closure from a passing rerun. Historical failures remain retained;
no common cause with older Homeostasis/CI/checkpoint records is asserted. The startup-owner
and opt-in mismatch remains OPEN, with the same Runtime/Kernel review gate. See the linked
report and follow-up PR for complete suite/CI results and remaining verification limits.
