# Internal Alpha Readiness Decision

Date: 2026-11-25 (America/Denver)

**The existing supervised internal-alpha boundary remains unchanged.**
**NO-GO for unattended or production operation and unverified installation graphs.**

- Decision owner: Aetherra Labs.
- Clean verified merge: [PR #355](https://github.com/AetherraLabs/Aetherra/pull/355)
  at `e8975d38f1a3d1acb78bfb8ad85cb4b56ee9c331`. It incorporates C1 and C2a
  and corrects checkpoint-stop command-error reporting.
- Released main: `a30277e3cfeb9e80f0605436e366721a548ead6d`,
  `v0.5.0-beta.14`. Only release metadata differs from the verified merge.
- Historical desktop, Phase A/B and C1/C2a candidate checkpoints retain their own
  revisions and verification boundaries; they are not current-main substitutes.
- Supported profile: Windows x64, Python 3.13.7 source checkout, Node 22.18.0,
  PowerShell 7.5+, the normal full launcher and React Runtime Observatory.
- All conversations are synthetic. Separate local directories isolate storage;
  account/user isolation is not claimed. Aetherra is the persistent cognitive
  system; Lyrixa is her user-facing persona.

See [the checklist](ALPHA_READINESS_CHECKLIST.md),
[fresh installation commands](DESKTOP_INSTALLATION.md),
[operator commands](ALPHA_OPERATOR_RUNBOOK.md) and historical
[fresh-install evidence](evidence/desktop_alpha_2026-11-22.json) and
[clean-main acceptance](evidence/desktop_alpha_main_2026-11-22.json).

## DEV-CKPT-001 Candidate Follow-Up (2026-11-25)

**Scoped corrections verified for the candidate; operational authority unchanged.**
The product source is `4d9c8f8e455b87624e6918dbcc784577950af4fb`, tree
`de52a848d9e410e5829d4406c8527cd71263e92d`, stacked on the unmerged C2b
candidate `c53cc5524304a6a43688bb683b07f9aa6b467390`. The
[issue record](DEVELOPMENT_ISSUES.md#dev-ckpt-001--extended-run-observer-and-checkpoint-progress-gap)
and [delivery receipt](evidence/dev_ckpt_001_delivery_2026-11-25.json) retain
the original gap, source-specific failures, controlled mechanisms and archive hashes.

The final source passed 4,136 tests with 38 skips and 45.29% coverage against
22%; quality, boot and integration passed. Extended-04 acknowledged 11 periodic
checkpoints in 65 minutes at the default 300-second cadence, continued after
retention needed approval and restored the exact generation-11 head at epoch 2
before any Core tick or event. Both harness SIGINT stops drained, exited zero
and independently closed listeners; retention blocked their stop saves. Ten
actual GPT-4o turns used no fallback. Synthetic write, retrieval and provider
input joined by record ID, and the separate local data directory disclosed no
corresponding fact. This establishes local storage isolation only.

The earlier uninstrumented physical-01 run committed generation 1 and exited
zero, but its last direct owner sample was pending. Its strict gate remains
failed, terminal acknowledgment unknown and second session skipped. R3 is a
separate, reviewed instrumentation result on the same product source: it reads
cached owner status after real stop and Memory drain, before Hub teardown, then
publishes bounded metadata after CLI unwind. Two genuine operator Ctrl+C events
acknowledged generations 1 and 2 around exact same-store restart at epoch 2.
Both phases verified signed/durable joins, zero runtime/redirector exits and
closed listeners. No equivalence claim supplies the missing original decision.

The same browser tab reconnected automatically, displayed the restored row,
advanced from 6 to 21 ticks and cleared current evidence after both exits.
Actions stayed disabled. The 54.23-second host-clock observation gap does not
establish offline duration. Durable prior acceptance and termination remain
unknown, and aggregate status remains incomplete. Cleanup found zero owned
processes and listeners without forced runtime cleanup.

Source and final independent review found zero outstanding Critical or Important
issues. Deferred Minor findings cover ambient signing-key test isolation and
legacy malformed-submission failure-summary completeness; the recorded runner
cleared signing variables, and raw helper evidence remains available with
fail-closed verification. ALPHA-CKPT-001 and DEV-CKPT-001 remain OPEN for their
historical causes. DEV-AUDIT-001 remains OPEN for cold/linear audit limits;
DEV-OBS-001 remains OPEN for aggregate status. The append cache is bounded to
64 paths and 600 seconds, requires matching bytes and effective key, validates
signed suffixes and leaves independent integrity checks cold from genesis.
It does not establish cross-process coordination or large-ledger latency bounds.

Strict Guardian, Security, signing, receipt deadlines, ownership, single-worker
Memory authority and retention approval remain unchanged. C2b remains unmerged;
the existing supervised internal-alpha boundary stands, and unattended or
production operation remains NO-GO. Hosted PR checks belong to the delivered
revision. Production bundle signing and signed-manifest enforcement require a
main push; no new production-signing pass, merge or release is claimed here.

## C2b Prerequisite Checkpoint (2026-11-25)

Independent review found no merge blockers. The PR had 33 successful workflow
jobs and one expected skip. All 11 main-push workflows passed, including actual
production signing and signed-manifest enforcement. Automatic Release published
beta.14. An independent Ed25519 check verified its manifest and both named
distribution hashes. See [CI Quality Gates](https://github.com/AetherraLabs/Aetherra/actions/runs/45571159696)
and [Automatic Release](https://github.com/AetherraLabs/Aetherra/actions/runs/45572771086).

The clean merge passed 3,840 tests, skipped 38, and exited zero with 45.29%
configured coverage. Boot, integration, docs and Python quality also passed.
The verified Python inputs and GUI tree matched the clean merge. A fresh
Python 3.13.7 install passed dependency and lock checks and strict audits of
168 distributions with zero findings. The fresh GUI passed 32 tests, build,
lint and audit.

Live gpt-4o on released main exercised actual provider input, restart recall,
missing information and a separate profile with no fallback. Two actual
operator Ctrl+C shutdowns separately verified exit zero, closed Hub ports,
durable rows and exact selected-row restoration on restart. The live browser
observed fresh read-only status, automatic offline and reconnection, and the
restored row. Final stop receipt acceptance remains **unknown** for both
physical shutdowns. The normal-CLI live exercise correlated public evidence
IDs. Its actual prompt and private history were unobserved.

The [prerequisite receipt](evidence/c2b_prerequisites_2026-11-25.json) binds
these results to their source revisions and scoped checks. This checkpoint
closes the prerequisite verification for starting C2b implementation. It
grants no additional operational authority. [ALPHA-CKPT-001](DEVELOPMENT_ISSUES.md#alpha-ckpt-001--checkpoint-stop-delay)
remains **OPEN, cause unknown**.

## Checkpoint-Stop Follow-Up

Historical baseline and local pre-merge verification (2026-11-24). The current
merged disposition appears in the checkpoint above.

C1 and C2a merged after review and current CI. C2a's final main-target checks
passed 37 entries with one expected skip. All 11 main-push workflows passed.
[CI Quality Gates](https://github.com/AetherraLabs/Aetherra/actions/runs/45546947307)
executed production signing and signed-manifest enforcement successfully; neither
step was skipped. [Automatic Release](https://github.com/AetherraLabs/Aetherra/actions/runs/45548258107)
published beta.13. Published assets were not independently downloaded for local
verification in this checkpoint; actual hosted signing and verification passed.

The clean merged-main Windows suite at `4116f5c6` had **3,830 passed, 38 skipped,
one failure and five passing subtests**, 45.29% coverage against the unchanged
22% requirement, with process exit 1. The failure was
`test_selected_checkpoint_restores_before_ticks_and_stays_out_of_chat`, waiting
for `observer-stopped.json`. Restore before tick zero succeeded; a later row
committed without an accepted stop receipt, and continuity became uncertain.
The original artifacts do not establish which operation exhausted its budget.

An isolated diagnostic and then both unmodified acceptance tests passed on
released main `949312c3`. These passes do not resolve or erase the full-suite
failure. The successful restart restored Memory row
`de2832db1e4d40d38ef7de560afc572f` before tick zero with an exact aggregate match;
all three processes exited zero and verified signed audits. Checkpoints remained
outside chat evidence. The context-derived deterministic responder used no fallback.
GUI 32 tests, install/build/lint, four boot contracts and five integration
contracts also passed. They do not establish a new browser or live-model pass.

The follow-up corrects a confirmed verification defect: an exception in the
background stop/session command task was lost, producing only a missing-file
timeout. It now reports sanitized stage/code failures promptly and consumes the
task exception. Nine focused regressions and 99 existing control tests pass.
A controlled real-SQLite experiment delays completion three seconds after commit:
the original harness reports a generic missing receipt after 15.016 seconds;
the corrected harness reports `stop_observer/consciousness_shutdown_pending`
after 2.035 seconds. Both runs retain one committed row, no accepted receipt,
no retry, uncertain status, drained ownership, verified signed audit and runtime
exit zero. This proves the diagnostic correction, not the original slow operation.

The **uninstrumented full suite passes 3,840 tests, 38 skips and five subtests**,
including both continuity acceptance tests: 1,538.70 seconds pytest time and
1,558.66 seconds through process exit zero, with 45.29% coverage against the
unchanged 22% requirement. Separate instrumented normal-launch
acceptance passed both tests across five processes in 160.77 seconds pytest time
(161.79 seconds through process exit). The source-bound
[follow-up receipt](evidence/checkpoint_stop_followup_2026-11-24.json) records the
pre-commit verification snapshot: `949312c3` base, harness/test changes, exact
commands, results and limits. All 1,552 hashes in the verification manifest match
after the run. In the
uninstrumented full-suite trace, handle `bc1dfbc011b7410d80589d91493aa50d` saved
Memory row `cd1d84e53983413eb3292cc8edfe10c6`; a new process restored that same row
before tick zero with an exact aggregate match. All three processes exited zero,
closed their ports and verified signed audits; checkpoint data stayed outside
chat evidence. No runtime deadline, policy or late-save acceptance rule changed.
The original full-suite failure remains recorded and its slow operation remains
unproven. [ALPHA-CKPT-001](DEVELOPMENT_ISSUES.md#alpha-ckpt-001--checkpoint-stop-delay)
tracks the open investigation and closure criteria. Passing reruns do not
retroactively assign that failure a cause.

**At this historical checkpoint, local diagnostic-fix verification passed.**
The fix had been pushed as `007e6510`. PR review, hosted follow-up CI, merge,
fresh Python installation, current browser and live-model operation, and
physical keyboard shutdown were still pending. The dated receipt retains its
pre-commit snapshot.
Python verification reused the pinned environment. Signing, Guardian/Security
and pending Temporal work remain preserved. C2b selection, periodic saves and
retention remain separate work.

## Phase B Merged-Main Checkpoint

[PR #352](https://github.com/AetherraLabs/Aetherra/pull/352) merged after final
review and 37 passing PR checks (one expected skip). A clean checkout of merge
`42b8f6a7` passed **3,494 tests, 38 skips and 5 passing subtests**, exit zero.
Fresh GUI installation passed all 29 tests, build, lint and type checking.
Two normal full-launch processes each crossed a 215-second observation window,
restored the same proposal/cycle identifiers and retained zero actuation.

All 12 main workflows passed, including required production signing and trusted
key enforcement in [CI Quality Gates](https://github.com/AetherraLabs/Aetherra/actions/runs/45489540011).
The [automatic Release](https://github.com/AetherraLabs/Aetherra/actions/runs/45491286465)
published [v0.5.0-beta.11](https://github.com/AetherraLabs/Aetherra/releases/tag/v0.5.0-beta.11);
its Ed25519 signature and both signed distribution checksums were independently
verified. The released checkout was clean: 1,995 of 1,998 file bytes matched the
merge, with only three version/changelog files changed. Version checks and four
release-version tests passed. Browser and live-model checks were not repeated
for this merge; earlier evidence retains its original scope.

The source-bound merge/release receipt is `main-verification-summary.json` in
the operator's `2026-11-24` PR352 evidence set, SHA-256
`cc3e3a752cb025d9903a3e9af4c0fc16d9bbb3d3f2b535d01d24275b0704a7cf`.
The PR summary records this acceptance. The earlier review checkpoints below
are historical and do not replace this clean-main result.

## Phase C2a Observer Checkpoints

Historical **scoped GO for supervised Windows source-runtime checkpoint operation
and publication review** at `5d8ccecba5ef9f3b9177bbf64063c572f5cf0142` on
`codex/phase-c2-observer-checkpoints`. At that checkpoint, the changed launcher
had targeted verification but no full-suite/browser rerun or hosted/main/release
acceptance. The [merged-main follow-up](#checkpoint-stop-follow-up) supersedes
those pending integration claims and records the later full-suite failure.
This historical decision establishes no unattended, production or action authority.

Publication review found two Important gaps after the original local GO.
On Windows, asyncio Runner's first Ctrl+C cancelled the main task and took the
cleanup-only path without saving a checkpoint. Earlier smoke had independently
stopped the observer before CLI shutdown, so it missed this path. CI also
omitted the new C2 acceptance file. Regression tests reproduced the signal
failure before correction. The launcher now recognizes only its matching
first signal-triggered cancellation as orderly-stop intent; unrelated/additional
cancellation remains cleanup-only, and signal-handler ownership is restored.
The CI workflow now includes C2 acceptance in its existing offline pinned-model
step. Nine platform-portable signal regressions are included in Linux CI
selection; hosted execution was pending at this checkpoint. Windows-specific
CLI acceptance remains platform-specific. Targeted fix review
reported no remaining findings. Signing, policy, the one-second authorization
deadline and CI quality/signing controls were not weakened.

Publication-review checks passed **129 unit/lifecycle tests** and **4 acceptance tests**
in 184.72 seconds (185.82 seconds wall time for acceptance).
Acceptance covers three-process checkpoint isolation, normal Windows CLI-only
shutdown/restart and ask/stream shutdown. Windows processes **21492 and 63284**
both exited zero; no independent observer-stop command was issued. Handle
`0b3fc55c3dec44d289d466ae48e9b3fe` restored exact state from Memory row
`6bf0c95b32514484845b6de5a9f76bcd` before B had any ticks or events. The handle
is distinct from the row ID. This used programmatic SIGINT, not a physical
keyboard interaction. Current boot, Integration Validation, quality and
CI-control checks passed; **1,733 frozen source/control hashes** match the
committed fix. The [publication-review receipt](evidence/integration_phase_c2a_pr_review_2026-11-24.json)
records exact source, gate labels, commands, durations and checkpoint evidence.
The [operator procedure](ALPHA_OPERATOR_RUNBOOK.md#consciousness-checkpoints-phase-c2a)
provides the normal-CLI regression command and recovery contract.

Historical verification at `a10b734e` remains in the
[original receipt](evidence/integration_phase_c2a_2026-11-24.json): **3,821 passes
and 38 skips**, 45.29% configured coverage against the unchanged 22% requirement,
1845.33 seconds pytest/1872.10 seconds wall time. The extended run passed in
761.75 seconds with A/B/C ticks 215/234/0, signed audits, clean exits and exact
restore of row `cfca237a2a5d4c79bb4aa9623fcb0864`; checkpoint data stayed out of
chat evidence/provider input. C1 default-off/deny compatibility passed in
130.84 seconds. Six browser checks and GUI 32 tests/build/lint passed against
that historical source; the GUI tree remains unchanged. These results do not
claim a new full-suite, extended-window or browser pass for the shutdown fix.
Context-derived deterministic generation is not a live-model pass.

Failure history remains part of acceptance. The initial short-run monitor stop
captured no exception type; its cause remains unknown. At `26a28efe`, an
extended restart restored correctly but stopped after 125 ticks with a
1.029709-second status timeout. Two controlled regressions reproduced loop
starvation from Homeostasis's synchronous one-second CPU samples; those samples
now run off-loop with the same measurement window. At `06feac58`, standalone
extended acceptance passed, then the full suite failed with **1 failure,
3,813 passes and 38 skips** (45.29% coverage). That restart stopped at 41 ticks
with a 1.982992-second timeout. Controlled regressions demonstrated prompt
signed authorization followed by health-broadcast starvation of loop delivery.
Fix `a10b734e` yields between recipients and checks the exact original service
registration before dispatch. Six new cases failed before the fix; all seven
broadcast cases and 106 compatibility tests passed afterward. The original
unclassified failure is not retroactively assigned either reproduced cause.

Independent review also corrected cancelled-stop acceptance, generic
consolidation of aged checkpoints, invalid-backend drain calls, callbacks under
lifecycle locks and oversized dictionary allocation. Fifteen regressions
reproduced those findings; the integrated review bundle passed 253 tests.
Those failed/superseded captures remain in the historical receipt. Signing, policy,
the one-second authorization deadline and quality baselines were unchanged.
The broadcast fix does not promise a latency bound for an individually slow
audit or handler.

Existing Memory remains the authority/ownership boundary for immutable
checkpoints. Missing, malformed or denied restore blocks observer ticks and
saves; one save is requested only at explicit orderly stop. Directory separation
verifies storage isolation, not account isolation. C2b automatic latest
selection, periodic saves and retention remain deferred; pending
TemporalConsciousnessEngine work stays preserved. Hosted CI, merged-main and
release outcomes are now recorded in the [follow-up](#checkpoint-stop-follow-up).

## Phase C1 Observer Candidate

Historical **GO for supervised C1 operation on the frozen Windows source-runtime
candidate**, `codex/phase-c-observer`, based on released main `17a833cd`.
At this checkpoint C1 was committed/pushed as `b8719fa2` and not yet merged;
hosted CI, fresh installation, browser and live-model operation were unverified.
The later [merge and follow-up](#checkpoint-stop-follow-up) have separate evidence.
Unattended/production operation and action execution remain NO-GO. The
[source-bound evidence](evidence/integration_phase_c1_2026-11-24.json) records the
exact source hashes, commands, result counts, audit references and limitations.

The baseline component bundle passed 18 tests with one Windows skip. The first
normal-launch failure was an ownership comparison: Memory and Engine adapters
were compared with their registered implementations. The corrected check uses
only concrete adapters. The extended run then exposed a missing owned Engine
heartbeat beyond the 180-second stale threshold. The observer correctly blocked;
the launcher now refreshes only a live, initialized, exactly owned healthy Engine,
rechecking those conditions after audited authorization. The failed captures are
retained in the evidence. Other repairs require reflection audit receipts, bound
history to 64 entries, serialize audit preflight off the chat loop and preserve
foreign registrations. Status reads remain cached and do not evaluate autopilot.

The final default suite passed **3,651 tests, 38 skips and 5 passing subtests**,
with exit zero after 1,469.82 seconds including process exit. Configured coverage
was 45.29%, above the unchanged 22% requirement. Boot validation and Integration
Validation passed. The Python quality gate reports zero new/edited violations
with 954 unchanged legacy files. The final Engine/registry compatibility bundle
passed 166 tests. These results apply to the frozen candidate, not a merged main.

Allowed and denied profiles each ran the normal full launcher for a 215-second
observation window. In the allowed profile, completed ticks advanced **1 → 214**
and measured events **4 → 856**, with fresh Engine and observer registrations.
After independent observer stop, ThinkStream returned HTTP 503, the Observatory
reported offline, and chat still retrieved the saved fact without fallback.
The denied profile stayed blocked with zero completed ticks and no healthy
observer refresh. Both signed audit chains verified cryptographically; both
processes exited zero without force. The observer performed no continuity-file
access or QFAC writes and enabled no Memory consolidation or actuation. Existing
chat Memory and other runtime services retain their independent ownership.

A separate default-disabled run used three fresh processes: write, restart with
empty chat history, and a separate profile. The observer registration was absent
throughout, all processes exited zero and no generation fallback ran. One compact
restart trace is saved record `b53ff4fc40f5dfacaf9867e7380d31f7` in process 40348 →
retrieval of that same ID in process 60896 → the identical provider evidence ID →
the context-derived answer naming aunt Leona. The separate profile lacked that
fact and the unknown attribute remained unknown. These are deterministic
responder checks through real storage, retrieval and HTTP, not live-model passes.
Local directories establish storage isolation, not account isolation.

Follow the [C1 operator procedure](ALPHA_OPERATOR_RUNBOOK.md#consciousness-observer-smoke-phase-c1)
for the short and extended runs and independent signed-ledger check. Actual
Observatory HTTP payloads were verified; no browser or live provider was used.
Harness stop uses trusted local instrumentation and SIGINT, not interactive
keyboard evidence. Historical browser/gpt-4o checks retain their earlier scope.
Signing, Guardian/Security, release controls, original workspaces and pending
temporal work are preserved. The evidence JSON captures the precommit test
snapshot; its uncommitted/index fields describe that point in time. C1 was then
reviewed, committed and pushed as
[b8719fa2](https://github.com/AetherraLabs/Aetherra/commit/b8719fa22b8bd21ea77b3c4aa721522e312e86ea).
The committed Python content matches the verified snapshot after Git newline
normalization. Publication does not add a remote-CI or merged-main claim.

C1 state intentionally resets on restart and attaches no chat Memory consolidator
or SafetyEnvelope actuator. The separate [C2a checkpoint](#phase-c2a-observer-checkpoints)
implements exact trust restoration and immutable Memory checkpoints through
existing interfaces. Automatic selection/periodic saves/retention remain C2b.
The pending TemporalConsciousnessEngine observer is not activated by either milestone.

## Merge Review: Maintenance Restore And Status

Review of PR #352 on 2026-11-24 found two linked blockers: a failed Maintenance
restore could be overwritten by automatic proposal routing/autosave, and the
Observatory could display active/empty records while persistence had failed.
The service now retains a restore-failure guard until a successful explicit
reload. Automatic routing and save retries stop with
`maintenance_restore_failed`, preserving unread or partially restored history.
Ordinary failed-save recovery and valid new/empty stores remain supported.
The Observatory reports a sanitized persistence state, degrades known errors,
and labels cycle evidence as current in-process records.

The new regressions reproduced both defects. The repaired backend passed 234
focused tests; the integrated UI/Maintenance/proposal bundle passed 158 tests.
All 29 GUI tests, type checking, build and lint pass. Final independent review
found no remaining blocker in these repairs. Two import-heading comments added
after the integrated run are bound by exact reconstructed-byte hashes and AST
equivalence; no behavior changed after those tests.

The earlier full-suite/runtime checkpoints below retain their original source
scope. The new head's CI and clean-main verification remain separate gates on
[PR #352](https://github.com/AetherraLabs/Aetherra/pull/352). No execution authority
or broader readiness claim is granted. See
[merge-review evidence](evidence/phase_b_merge_review_2026-11-24.json).

## Phase B PR Review Checkpoint

Final review on 2026-11-24 found one remaining measured-provenance defect:
the real validator's empty defaults and no-input fallback estimates could enter
Self-Improvement's SQLite metric history. The bridge now leaves those summaries
as diagnostic output because they do not declare per-score measurement
provenance. Genuine measured zero values remain supported. Both real-validator
regressions failed before the fix and now pass through the registered intake
and SQLite reload; proposal routing remains intact.

The source at `3ea0df0` passed **3,472 tests, 38 skips and 5 passing subtests** with
default collection, options and coverage in an independent clean source
snapshot. All 1,547 frozen source/control hashes matched that candidate. The focused
provenance/flow bundle passed 87 tests; the unchanged Python quality gate reports
zero new or edited violations.

Two fresh normal full-launch processes again crossed 215 seconds each, restored
the same persisted proposal/cycle records, and exited zero without force.
Real measurements continued reaching both memory and SQLite near the end of
each window; validator effectiveness defaults remained absent. Hub ownership,
HTTP readiness, Guardian enforcement, audit integrity, unchanged tuning and zero
actuator attempts/executions passed. Strict signing flags remained configured.

**GO remains bounded to supervised observe/propose operation.** This checkpoint
supports PR publication; hosted CI and merged-main acceptance remain separate.
Earlier browser/live-model evidence retains its original source scope and was
not repeated for this backend-only repair. Pending temporal work, original
workspaces, historical evidence and signing/release controls are preserved.
See [review evidence](evidence/integration_phase_b_pr_review_2026-11-24.json).

### CI Subprocess Import Follow-Up

The first PR #352 CI Quality Gates run exposed a test-harness dependency: the
blocked-maintenance shutdown subprocess ran from its temporary profile without
an explicit repository import path. The local runner supplied `PYTHONPATH`, so
the default suite above did not expose that dependency. Clearing the inherited
path reproduced the same `ModuleNotFoundError` locally. The test now supplies
its own child import path while retaining the real blocked probe, temporary
profile, shutdown assertions and 15-second deadline. The corrected case and all
90 focused heartbeat/observe-only tests pass, as do all four style checks.

At `ebd216c`, production source was identical to the full-suite/runtime checkpoint above.
The changed harness has focused verification; current hosted CI is recorded on
[PR #352](https://github.com/AetherraLabs/Aetherra/pull/352). The bounded GO decision
and signing controls remain unchanged. See [CI correction evidence](evidence/phase_b_ci_import_isolation_2026-11-24.json).

## Hub Heartbeat Follow-Up

Verification date: 2026-11-24. The initial Phase B stale-Hub concern is repaired
in the same isolated `codex/integration-phase-b` candidate. This checkpoint predates commit and PR publication; it claims no hosted CI or
merged-main acceptance.

The old Flask factory used a removed first-request hook, attached shutdown to
request-context teardown, and could substitute an always-alive dummy Hub.
The normal full launcher's existing lifecycle loop now refreshes only its actual
owned local server while its serving thread is alive. Existing registration
identity, healthy-status and Guardian capability checks remain mandatory.
Factory creation and ordinary requests no longer own a background registry
worker. External/proxy Hubs and direct standalone callers retain their explicit
ownership; no replacement service, timer, status promotion or relaxed expiry
was introduced.

The existing baseline passed 67 tests. New regressions failed for both idle and
request-teardown operation at logical expiry, and for the missing heartbeat
authorization audit. All 15 new cases now pass, including stopped/dead threads,
replacement, absent ownership, unhealthy registrations, shutdown and denial.
The focused 129-test bundle includes Phase B durability and all 13 signing
regressions; boot, Integration Validation and the unchanged quality gate pass.
The first full run passed 3,469 tests with 38 skips and 5 passing subtests,
but one active-stream shutdown test timed out before generation began. Its
real local retrieval model took about 25 seconds to load against a 10-second
setup wait. The child still persisted work and completed shutdown; the same
test passed unchanged in isolation. The acceptance harness now uses its existing
90-second readiness budget and the normal smoke's 120-second HTTP budget.
The one-second stream timeout, 0.15-second drain budget, post-signal deadlines
and all ownership/persistence assertions remain unchanged. A second run exposed a separate legacy alert-test isolation defect: shared
metric history crossed its learning threshold. A private copy with 52 samples
reproduced the failure; empty history passed. Its fixture now supplies fresh
real detector and Lyrixa integration instances, retaining the original assertions.
Both 20-test module sequences passed with seeded and empty histories. No
production alert behavior or shared history was changed.

A third run exposed a legacy workflow benchmark measuring the entire script
call, including Guardian and metadata, against 200 ms. The timeout step itself
remained correct and took less than 0.01 ms in the partitioned check. Its test
now verifies that the fast path schedules no wait or sleep while preserving
the normal script/security path and timeout-result checks. Deliberately disabling
the fast path in a private copy fails this test; slow setup still passes.

The final full suite ran from an independent clean checkout with identical
frozen source, excluding accumulated ignored runtime history. It
passed 3,470 tests with 38 skips and 5 passing subtests, exit zero, using
the default collection, options and coverage. All 1,546 frozen source/control
hashes matched after verification.

Fresh normal full-CLI processes `6072` and `26804` each crossed a 215-second
checkpoint. All 32 samples found the same actual launcher-owned server healthy,
with an advancing heartbeat and measured `hub_connection=1`. Maximum sampled
heartbeat age was 31.028 seconds. HTTP health/readiness passed separately.
The natural proposal contains the measured service-count threshold crossing,
with no false Hub-pressure evidence. Exact proposal and cycle contents survived
restart unchanged. Both processes exited zero without force and closed the Hub
listener. Observe-only mode, unchanged tuning, zero actuator attempts/executions
and enforcing Guardian with intact audit remained in effect.

The documented metrics-snapshot endpoint was also checked against the restarted
Hub. Browser and live-model checks were not repeated for this backend follow-up;
the earlier Phase B evidence retains its recorded source scope. Raw logs and
profiles remain outside source. See [follow-up evidence](evidence/hub_heartbeat_followup_2026-11-24.json)
and [operator checks](ALPHA_OPERATOR_RUNBOOK.md#observation-and-maintenance-smoke-phase-b).

**Decision: GO for bounded supervised observe/propose operation of this local
candidate; the Hub lifecycle concern is resolved on the verified normal
full-launcher path.** The supervised
observe/propose boundary remains unchanged. Serving liveness is not a latency,
throughput or useful-work guarantee. Optional subsystem issues and Phase C remain
separate. Original workspaces, pending temporal work, prior Phase B evidence and
release signing controls are preserved.

## Phase B Observation And Maintenance Candidate

Verification evidence: 2026-11-24 UTC. Candidate branch
`codex/integration-phase-b`, based on released main
`ba3a04ad44f85dbb0fd2b2291142dca40a6562d4` (`v0.5.0-beta.10`). This checkpoint records the
pre-commit isolated candidate. It did not include hosted CI, merge or clean-main
checks for Phase B. The pending temporal observer and original workspace
remain separate and unchanged.

The existing component baseline passed 109 focused tests. Full integration
exposed a bridge expecting wrappers instead of registered instances, absent
proposal routing, observe-only adaptation, profile-relative configuration,
unmeasured defaults appearing as evidence, failed-write retry inconsistency,
and registrations expiring after three minutes. The candidate connects the
existing bridge, Self-Improvement engine and Maintenance coordinator, preserves
measured provenance, persists before publishing proposal updates, blocks
observe-only tuning, and refreshes only owned live Phase B registrations.
The Observatory projects bounded evidence from the real records.

The normal full CLI ran twice in one fresh profile. Both processes crossed a
215-second natural observation checkpoint: accepted observations increased
`1 -> 4`, the same five canonical/alias registrations remained fresh, tuning
stayed unchanged, and actuator attempts/executions/blocks remained zero.
The first process ran 430.92 seconds and the restart wrapper 496.16 seconds;
the latter includes a deliberate pre-launch hold for browser shutdown checks.
Both exited zero without force. These elapsed times are bounded exercise
receipts, not a continuous-health or soak guarantee.

One separately labeled synthetic sample exercised the actual bridge and was
restored immediately afterward. Three `proposed` cycles survived restart.
Full cycle contents and all substantive proposal fields matched across
SQLite/JSONL, the services and Hub. Only the natural proposal's repeated-
observation count and update timestamp advanced. No Guardian decision,
Security enforcement, execution, verification or learning outcome was supplied.

```text
synthetic memory_rtt=900ms -> PID 40652
  proposal si-821a26d1d803d595 -> SQLite
  cycle maint-homeostasis-821a26d1d803d595 -> Maintenance JSONL
exit 0 -> PID 58844, same persisted records -> Hub -> Observatory
  cycle ref a534ccb549f444f6; proposal ref 846b2f703d9efa73
  proposed; no decision, enforcement or execution
```

Actual browser verification passed at desktop and 390x844 widths. The inspector
showed these references, observe-only behavior, enforcing Guardian with verified
audit, and Memory continuity explicitly unverified. It cleared stale evidence
after shutdown and reconnected automatically after restart; no console errors
were observed. The separate continuity smoke passed seven offline and seven
OpenAI/gpt-4o turns through the same full entry point, with real restart/storage,
accurate recall, honest unknowns and a separate empty profile. No live fallback
ran; all six continuity processes exited zero without force.

The final default suite passed **3,455 tests, with 38 skips and 5 passing
subtests**, then exited zero. Default collection/addopts/coverage were retained,
and all 1,544 frozen source/control files still matched. The existing optional
and platform skips are retained, not counted as passes. Focused review passed
116 tests; all 27 GUI tests, build/lint, four boot checks, five Integration Validation checks,
13 signing regressions and the unchanged Python quality gate passed. Source
hashes, exact commands and retained diagnostics are recorded in
[Phase B evidence](evidence/integration_phase_b_2026-11-24.json).

The initial Phase B checkpoint recorded a Hub heartbeat defect: its setup used
`before_first_request`, unavailable in pinned Flask. After expiry,
`hub_connection=0` therefore describes its stale/degraded registration while
concurrent HTTP health/readiness remain successful. This is not evidence of
HTTP connectivity loss. The natural proposal also records service count 30
against the shipped target 8; a threshold crossing is a review trigger, not
proof of a performance fault. Other optional lifecycle degradation remains
visible and outside this focused connection. The [Hub follow-up above](#hub-heartbeat-follow-up)
repairs the stale registration; registry liveness remains distinct from HTTP
connectivity and useful work.

**Decision: GO for the bounded Phase B observation/proposal candidate on the
verified Windows profile; retain the supervised internal-alpha boundary. Do
not advance Stage 22 or grant execution authority.** The records are unsigned coordination evidence, not
approvals. There is no account isolation, interactive ConPTY, fresh installation,
alternate-platform, unattended or production claim. Release signing controls
and approved keys are unchanged. Next: review/integrate this candidate and its
Hub follow-up, then resume the separate Phase C and temporal work.

## Phase A Core Integration Candidate

Original candidate base: `8902e161c728dca50f95555e16bfdfccf5f303b8`, on
`codex/integration-phase-a`. Phase A was integrated through PR #351 at
`da982385d30510f0e7010f33e2cffe2d5cbdc3f6`; the released main baseline for Phase B is
`ba3a04ad44f85dbb0fd2b2291142dca40a6562d4` (`v0.5.0-beta.10`). PR checks, clean-main
verification and the signed release passed. The original candidate evidence
below remains scoped to its recorded revision.

The baseline boot/Integration Validation checks passed, but targeted reproduction
found three integration defects: a startup scan could say ready with Memory and
Engine missing; daemon/file-derived Kernel observations could certify scheduling;
and a single Hub request thread blocked health behind generation. Full startup
also overrode Self-Incorporation disablement. The candidate requires actual core
registration and readiness, discloses provider selection as configuration-only,
retains optional states, honors disabled execution, and adds bounded concurrent
observation with serialized mutation ownership.

The normal full CLI parser/main passed the instrumented headless smoke with
real storage/retrieval and a generation-only offline double, then seven gpt-4o
turns without fallback. Both runs started empty local profiles and stopped/restarted
the runtime; all six processes exited zero without force. The live recall supplied
the original record and content to OpenAI after restart; a color not supplied
remained unknown, and a separate profile returned empty evidence. Live status
probes during chat peaked at 546 ms in the final live rerun (663 ms offline,
with other verification running concurrently). This is bounded responsiveness
evidence, not a throughput or soak guarantee, and does not reduce the cold
semantic-retrieval latency itself.

```text
PID 35000 writes 533780ffd6bf9e383ebe5c4ebf9ce2cf: Leona taught bicycle repair
  exit 0 -> PID 55152, same SQLite, empty conversation context
  retrieved ID = supplied evidence ID = 533780ffd6bf9e383ebe5c4ebf9ce2cf
  openai/gpt-4o: "Your aunt Leona showed you..."; fallback=false
```

Guardian remained enabled/enforcing with intact audit. Homeostasis was
`observe_only` with zero actuator attempts/executions/blocks; Self-Incorporation
reported disabled and Self-Improvement reported no automatic implementation.
Strict capability/network/script/signing settings remained enabled; release
workflows, trust keys and the fixed quality baseline are unchanged.

Independent review additionally reproduced shutdown during active generation
and configured cross-origin busy-response gaps; their focused repairs and final
regressions are recorded with the [Phase A evidence](evidence/integration_phase_a_2026-11-23.json).
The final default suite passed **3,348 tests, with 38 skips and 5 passing subtests**,
then exited zero. It retained default collection, addopts and coverage; all
1,412 Python files match the frozen verification source byte-for-byte. The
existing optional/platform skips and diagnostic failures are recorded in the
evidence, not counted as passes. Boot validation (4 checks), Integration Validation
(5 checks), signing regressions (13 tests), the fixed quality baseline and docs
checks passed. Independent review found no remaining blockers in the candidate.
The initial live attempt was sandbox-network denied and used fallback; it is
retained as a failed attempt, not counted in the seven live turns.

**Decision: retain the bounded supervised internal-alpha GO on the previously
verified profile; do not advance Stage 22 or extend authority.** Phase A
integration and clean-main checks are complete. Phase B observation/maintenance
is the current focused work. The separate pending TemporalConsciousnessEngine
observer is preserved and not absorbed here.

This headless run did not repeat browser/interactive ConPTY verification. External
or shared Hub reuse is unverified. Current optional experimental/cognitive startup
is not quarantined yet; its existing diagnostics can fail independently of the
core and generic registry health is not proof of useful loop work. Phase C owns
that activation-order work. No unattended, production, alternate-platform or
account-isolation claim is made.

## First Supervised Use Exercise

The next Stage 21 step was a bounded **15-minute steady-state exercise** on
`ff359b02b8422ea3ef5132bbad3d241de64f0553` (merged PR #328), using the existing
verified Windows installation, normal full CLI, gpt-4o and a new synthetic local
profile. Ten minutes in PID 52828 and five minutes in PID 55764 completed across
a normal restart. All 32 samples checked 12 JSON endpoints; Hub, Kernel and
Engine readiness stayed ready, Guardian enforced with intact audit, and
Homeostasis stayed `observe_only` with zero actuator attempts/executions/blocks,
unexpected restarts or recoveries. Both processes exited zero without force.

All 16 baseline turns used gpt-4o without fallback. Bicycle and music paraphrases
retrieved the original records after restart with empty chat history; the unknown
piano color was acknowledged and Aetherra/Lyrixa identity remained intact.
The browser showed unavailable after stop and reconnected automatically. Engine
registry degradation and unknown optional services remained visible; these are
distinct from core readiness. No browser console errors were observed.

This exercise also found a real reply defect: new personal statements were saved,
but several initial replies incorrectly said Lyrixa had not been told them.
The current record is deliberately excluded from historical recall; the prompt
applied its missing-evidence rule to both disclosures and recall questions.
The candidate repair distinguishes current disclosures from recall, retains
receipt-only save claims, and does not treat questions/guesses as facts.
Storage, ranking and provider selection are unchanged. Its offline tests capture
actual provider input with a neutral generation double; live wording requires a
separate real-model check.

That separate check passed **13 gpt-4o turns without fallback** in a new profile:
plain disclosures, competing relatives/music, a mixed dog-name statement and
question, unknown bicycle-frame/piano colors, an unconfirmed soup guess and later
unknown-soup recall, and identity. All three positive recalls supplied the saved
record IDs to generation. The soup-guess reply included tentative wording but
did not confirm it; later recall correctly remained unknown with empty evidence.
The candidate process exited zero without force. The 25 focused offline tests
and 80 final Engine/disclosure tests pass (overlapping selections); 13 signing
tests pass. The fixed legacy baseline requires style cleanup of the edited Engine
file; normalized syntax-tree review found only the intended prompt change after
accounting for equivalent best-effort exception/control-flow formatting.

```text
PID 52828 saves 317b9b4ffc69b9a784fee68c0abdd151: Leona taught bicycle repair
  normal stop -> exit 0
PID 55764, same data, empty history: "Who showed me how to repair a puncture...?"
  retrieved ID -> generation evidence ID: 317b9b4ffc69b9a784fee68c0abdd151
  openai/gpt-4o -> "Your aunt Leona..."; fallback=false
```

The 15-minute observations describe unchanged main, not the candidate prompt.
At that checkpoint the prompt candidate had focused offline and live checks;
the correction subsequently integrated through PR #347. The earlier 3,136-test
result below is historical coverage of the prior runtime, not a Phase A pass.

The first post-restart recall took **63.603 seconds** total,
and a concurrent 10-second status probe timed out. It recovered without a runtime
restart or retrying the chat write. The five-minute window began afterward.
A separate earlier sampler attempt failed on a disappearing child process;
its partial samples were retained and the full ten-minute window restarted.
Neither failed attempt counts toward the 15 minutes. This is **not** evidence of
uninterrupted cold-start responsiveness, leak-free operation or soak/load capacity.

**Decision: retain the bounded supervised GO; do not advance Stage 22.** The
disclosure correction is now integrated. The Phase A candidate above addresses
concurrent status responsiveness within Stage 21.
Required signing and the approved key remain unchanged. Detailed outcomes and
artifact digests belong in
[the supervised-use evidence](evidence/supervised_alpha_2026-11-22.json).

## Previous Integration Is Complete

[PR #326](https://github.com/AetherraLabs/Aetherra/pull/326) merged as `382e77ac`.
Its clean-main verification passed 60 focused regressions, boot/integration,
normal launch and three gpt-4o turns without fallback. Main CI and required
production signing passed. The automatic
[v0.5.0-beta.5 release](https://github.com/AetherraLabs/Aetherra/releases/tag/v0.5.0-beta.5)
completed; its manifest signature and wheel/source archive hashes were verified.
That earlier provisioned environment did not establish a fresh desktop install.

## Integrated Acceptance

PR #327's final revision passed 36 checks; optional auto-merge was skipped.
The clean merged-main tree exactly matches that reviewed revision. All 87
focused installation, continuity and signing regressions pass, as do dependency
consistency, exact lock sync, boot, integration, import and hygiene checks.
The complete 3,136-test run covers the unchanged runtime source.

Clean main's normal full launcher completed three more gpt-4o turns with no
fallback, retrieved the original saved record, rejected four expired requests
without storage changes, and exited zero without force. Its first probe arrived
while Homeostasis was initialized but not yet running; the retained observation is separate
from the passing startup/steady samples. Wait for launcher initialization before
assessing steady readiness; an HTTP 200 alone does not establish readiness.

All 12 main validation workflows and the automatic Release workflow passed.
Production CI verified the required signature against the approved repository
public key. Published `v0.5.0-beta.6` manifest signature and wheel/source archive
hashes were independently verified. The release changes only CHANGELOG, README
version text and the project version; the clean released-main badge check passes.
No private key, secret or signing-control change was needed.

## Reproduced Blockers And Repairs

The old 261-package desktop freeze failed pip resolution: `virtualenv==20.31.2`
requires `filelock<4`, while the freeze pins `filelock==4.2.1`. An advisory audit
reported vulnerabilities in 36 packages. Legacy Pyxnat also introduced the
obsolete `pathlib` distribution, and Streamlit constrained Pillow below the
repaired versions. These packages are outside the current source-runtime inputs.

The desktop lock now resolves the declared runtime and quality inputs explicitly,
constrained by compatible CI versions. It contains 167 exact pins, excludes
unrelated ambient packages, and preserves the old lock tool's no-input caller
behavior. Failed resolution leaves the previous lock intact. Tests use real
local wheels and pip, including installed transitives and conflicting constraints.
No source feature is deleted to reduce the audit graph.

Fresh installation exposed an import of removed `pkg_resources` in the existing
maintenance checker. It now reads standard-library distribution metadata.
Newly supported SPDX expressions use exact matching; compound/custom expressions
require review. Guardian report-write gates remain intact. This is a metadata
compatibility repair, not legal clearance for every dependency.

The diagnostic suite exposed two environment-sensitive defects. Dependency
analysis discarded a project if an ancestor directory started with a dot; it now
filters only paths inside the selected project. Metrics tests reused a singleton
listener on conflicting fixed ports; they now own real loopback listeners and
registries and close them after each test. No production metrics semantics,
test skip or quality-baseline allowance was added to hide a failure.

## Historical Desktop Verification (2026-11-22)

| Gate | Result | Evidence / boundary |
| --- | --- | --- |
| Fresh Python installation | PASS | New venv with system-site packages disabled; 167 pins plus pip; dependency consistency and exact lock sync pass. |
| Installed-package audit | PASS | All 168 distributions audited, zero findings and zero skips; separate audit environment. Dated advisory snapshot. |
| Retrieval model | PASS | Pinned MiniLM downloaded into an initially empty cache; remote model code disabled. |
| Default repository suite | PASS | **3,136 passed / 40 skipped**, exit 0; immutable source, default collection/addopts/coverage. |
| Focused regressions | PASS | Resolver 2; metadata/Guardian 9; path/legacy analysis 14; metrics 2 in each order. These selections overlap the full suite. |
| Python quality | PASS | Zero new/edited violations; 978 unchanged legacy files, 55 resolved; baseline unchanged. |
| Hosted Windows installation | PASS | Fresh install/audit; 87 runtime/signing regressions; boot/integration; GUI 18 tests/build/lint. Reviewed runtime has 37 green checks. |
| Runtime Observatory | PASS | Fresh npm install, zero audit findings, 18 tests, build/lint; stop/reconnect verified with zero observed console errors. |
| Normal full CLI | PASS | Two candidate processes plus one clean-main process; 12 JSON endpoints in six samples; every Ctrl+C exit 0 without force. |
| Engine and governance | PASS for observation | No-provider degradation; gpt-4o ready; Guardian enforcing and audit intact; Homeostasis observe_only and zero actions. |
| Live continuity | PASS | Three candidate and three clean-main gpt-4o turns: correct recall, unknown door color and preserved identity; no fallback. |
| Expiry and privacy | PASS | Eight candidate and four clean-main expired requests leave storage unchanged; prompts/replies absent from ordinary runtime logs. |
| Signing | ENFORCED | Existing production workflows, approved key and strict settings unchanged; signature/tampering regressions retained. |
| Integration acceptance | PASS | PR #327 merged; clean-main checks, 12 main workflows, required production signature and published beta.6 signature/hashes pass. |

The completed default run took 1476.39s and exited zero. All 1,395
Python source/test files match before and after execution. Individual skip
reasons and artifact digests are retained in the evidence. The desktop graph
omits the release-publishing SDK; its 14 real Git/CLI bootstrap tests separately
pass in the existing Semantic Release Dry Run job. Existing optional/platform
skips are reported explicitly, not counted as coverage of excluded features.
Five passing subtests are reported separately from the 3,136 passing tests.
The superseded diagnostic attempts do not count as suite passes.

## Fresh-Process Evidence Trace

No memory, retrieval, runtime or generation double was used in this manual check.
The initial no-provider fallback is separate from live-model passes.

```text
normal full CLI PID 35548, new synthetic local profile
  saved f8fa1f3588e240a2e1f57ab624c5f97a: Lantern Room
  saved three newer competitors, including Copper Finch
  explicit no-provider fallback; stop -> exit 0
normal full CLI PID 15600, same persisted directory, empty chat history
  retrieved f8fa1f3588e240a2e1f57ab624c5f97a
  generation evidence f8fa1f3588e240a2e1f57ab624c5f97a
  openai/gpt-4o -> Lantern Room; fallback=false
  unknown door color acknowledged; Aetherra/Lyrixa identity preserved
  browser reconnects automatically; stop -> exit 0
```

The earlier 35-turn/nine-process varied live matrix remains historical evidence.
This fresh-install pass repeats three core live turns. Offline real-storage,
real-retrieval restart tests cover varied paraphrases, missing facts and separate
profiles; their text-generation double reads only supplied evidence.

## Accepted Scope And Remaining Gates

The cleared dependency blockers apply to this Windows source-runtime profile.
Qt plugin GUIs, optional SDKs, quantum, research/export plugins and standalone
Lark grammar modules retain their source but require separate verification.
`pip install .` declares a different Qiskit-containing graph. Wheel-only installs,
other platforms/Python versions, privileged live mutation, soak/load and
unattended operation remain unverified.

Unavailable Security, Maintenance and Integration Validation evidence remains
unknown in the Observatory. Registry freshness is distinct from readiness.
Optional policy denials, relative configuration defaults, watchdog teardown
logging, THREE.Clock deprecation and the GUI bundle warning remain visible.
No all-services-ready or remote-assistance-execution claim is made.

Stage 21 remains the active phase for supervised internal-alpha operation on
this verified profile. Beta Hardening and Production Readiness remain Planned.
Broader profiles and operating authority require their own evidence and decision.
Unrelated staged/unstaged work was preserved throughout installation and acceptance.
