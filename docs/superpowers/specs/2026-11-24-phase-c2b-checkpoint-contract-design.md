# Phase C2b: Checkpoint Head and Recovery Contract

Started: 2026-11-24. Approved with clarifications: 2026-11-25 (America/Denver).
**Approved contract; not implemented.** The frequency/history boundary, recovery
visibility, time provenance and writer-loss requirements below incorporate the
user's approval.

The source links below preserve the original trace at
`2767230f851a5c8fe646b21d91ea84cd113fbc0e`. That tree is identical to the
reviewed PR #355 merge `e8975d38f1a3d1acb78bfb8ad85cb4b56ee9c331`. The
implementation starts on the release-only child
`a30277e3cfeb9e80f0605436e366721a548ead6d` (beta.14). The pre-flight interface
comparison applies to that released baseline.

## Intent and prerequisites

Extend C2a's explicit orderly-stop checkpoints with automatic head selection,
periodic saving and bounded retention through existing Memory. Aetherra remains
the persistent cognitive system; Lyrixa remains her user-facing persona.
The observer does not answer chat, acquire action authority or create another
persistence service. The pending Temporal runtime observer is a separate project.

Task 0 verification is recorded in the
[2026-11-25 prerequisite receipt](../../evidence/c2b_prerequisites_2026-11-25.json).
Follow-up integration and supported-profile fresh installation, browser,
live-model and physical-keyboard checks passed in their recorded scopes.
Physical stop receipt acceptance remains unknown. The existing supervised-alpha
GO is unchanged.

Use the standing [development issue practice](../../DEVELOPMENT_ISSUES.md) for
unresolved defects; future runtime incidents remain separate records.
The original slow stop operation remains **OPEN, cause unknown**, tracked as
[ALPHA-CKPT-001](../../DEVELOPMENT_ISSUES.md#alpha-ckpt-001--checkpoint-stop-delay).
Improved error reporting and successful reruns do not resolve that issue.

## Existing path: verified facts

Line numbers below refer to the trace baseline, not a future implementation.
The existing [C2a design](2026-11-24-phase-c2-observer-continuity-design.md)
contains its original acceptance boundaries.

| Step | Source and actual behavior |
| --- | --- |
| Configure and attach | `runtime_observer.py:47-66` accepts only strict enabled/explicit-handle settings. Launcher `2592-2669` supplies the exact owned Memory adapter and registry/policy predicate after core activation. Null handle means a fresh start, never latest. |
| Own storage | Launcher `141-169` verifies the original Advanced/Core objects. Advanced `365-405` delegates to Core `memory_core.py:186-211`, which owns one checkpoint worker. Advanced's default Core file is `lyrixa_memory.db`; the full launcher supplies no account identity. |
| Freeze and admit | `lifecycle_checkpoint.py:302-347` freezes validated payload bytes, binds a deadline of at most one second and admits one job without a queue. A separate owned connection accesses the existing Memory database, not the shared chat connection. |
| Authorize | Worker `192-268,366-388` requires enforcing Guardian, Security capabilities, strict signing/script verification and a nonblank audit receipt before database access; policy/ownership/deadline are rechecked. |
| Commit | Worker `389-430` uses `BEGIN IMMEDIATE`, rejects an existing exact handle, inserts an immutable `memories` row and commits. Handle and Memory row ID are distinct. Identical duplicate saves fail as ambiguous; there is no idempotent save API. |
| Accept receipt | Worker `124-140,430-465` separates committed storage from accepted completion. Expired/cancelled/revoked work can remain committed but uncertain. The outstanding slot stays owned through actual I/O completion. |
| Select and restore | Worker `471-525` loads one exact type, validates bounded content/context, row ID, owner/scope/handle/schema and rejects duplicates. Observer `318-366,421-440` decodes and restores on its owner thread before tick zero. No recency/similarity/older-valid fallback exists. |
| Capture and stop | Observer `467-484` freezes only a completed tick. `368-419` saves once on explicit orderly stop, publishing saved IDs only after acceptance. The attempted handle is not currently exposed on uncertainty. |
| Drain | Observer `227-311` keeps waiting for actual completion after acceptance expires; this is inappropriate for periodic tick-loop use. Launcher `2726-2752,4300-4307` refuses successful teardown while observer/Memory work remains owned. |
| Project | Observer `551-580`, Hub consciousness blueprint and Runtime UI snapshot expose cached bounded fields, not payloads or historical ticks as fresh health. |

Source references: [worker][worker], [observer][observer], [launcher][launcher],
[Core Memory][memory], [Advanced][advanced], [codec][codec], [Core import][core].
These are immutable source links, so the trace can be checked after later edits.

No head, durable writer token, operation catalog, periodic scheduler or checkpoint
retention exists today. Ordinary Memory consolidation excludes checkpoint rows.
Existing tests cover duplicate handles, cancellation around commit, lock failure,
policy revocation, restore-before-tick and ownership through shutdown; they do
not establish the C2b invariants below. No new runtime tests were run for tracing.

## Approach and compatibility

**Approved approach:** immutable payload plus head and bounded commit catalog in one
Memory-owned SQLite transaction, with expected-generation comparison and a
monotonic writer token. This extends the existing worker, not the service graph.

Alternatives considered: a separate head file cannot commit atomically with
Memory; scanning newest rows cannot distinguish a committed orphan, conflict or
uncertain attempt. A two-stage pending/publish protocol adds crash states without
benefit when all durable data can share one transaction. None is recommended.

Keep C2a's public methods, config defaults and duplicate behavior unchanged.
Retain the v1 payload codec, 64 KiB/eight-level bounds, exact trust import and
conversation exclusion. Add separate narrow stream operations through the same
Core/Advanced/launcher adapter. Do not change generic store/recall semantics.
There is no implicit adoption, deletion or migration of C2a or legacy-file rows.

All new behavior remains unimplemented and opt-in. Approved nested settings under
`consciousness_continuity`:

- Existing `enabled` and `restore_checkpoint_id` keep their meanings.
- An absent `automatic` object, or `automatic.enabled: false`, retains C2a.
- `automatic.enabled: true` requires enabled observer/persistence, a nonnull
  32-lowercase-hex `stream_id`, `start_mode: create|resume`, and a null legacy
  `restore_checkpoint_id`. Reject mixed explicit/automatic selection.
- `create` creates only an absent stream; existing means conflict. `resume`
  requires that exact stream; missing means blocked, never implicit fresh start.
  A valid initialized stream at generation zero is explicitly empty and may
  start fresh; a positive generation without its target is corrupt.
- Optional `recovery_attempt` is a `consciousness_continuity` field outside the
  closed `automatic` object. It accepts only a bounded opaque `AttemptDescriptor`
  and requires enabled automatic resume for the same stream. Reject malformed
  descriptors and invalid mode or stream combinations. The descriptor requests
  inspection only. Memory remains the sole persistence and head authority.
- Supervised-alpha defaults: `save_interval_seconds: 300` (strict integer 30-86400),
  `retain_checkpoints: 10` (strict integer 2-100). Unknown keys, booleans in
  numeric fields and invalid combinations fail closed. An interval is a minimum
  scheduling interval, not a durability deadline or promise of wall-clock saves.

An operator creates a named stream once, then uses resume for later launches.
These names are opaque storage selectors, not users, credentials or capabilities.
Selecting/forking an old explicit checkpoint into an automatic stream is deferred;
existing explicit C2a restores remain available. No automatic stream enumeration.

## Checkpoints, temporal history and temporal reasoning

These layers share Memory authority but have different purposes and retention:

| Layer | Scope | Boundary |
| --- | --- | --- |
| 1: Persistent state and recovery | C2a/C2b restore bounded operational state | Short recovery snapshots, exact validation and recovery evidence |
| 2: Temporal history | Separate pending Temporal integration | Meaningful events, transitions, corrections, timestamps and causal evidence; separate record type and retention policy under existing Memory |
| 3: Temporal reasoning and evolution | Future milestone | Patterns, outcomes and predictions over supported history; no fabricated observations |

Ten snapshots spaced 300 seconds apart span about 45 minutes from oldest to
newest. This is an illustrative recovery window, not a history guarantee: saves
can be skipped/delayed and protected pins can be older. Checkpoint retention must
never become temporal history retention. C2b neither implements that history nor
purges it, even when another record refers to a pruned checkpoint. Such a
reference can become unavailable; it must not cascade-delete its history owner.
The approved starting limits remain 64 KiB payload, one-second attempt and
two-second orderly-stop budget. No longer-term event-retention promise follows.

## Durable model and atomicity

Memory owns two versioned metadata tables in its existing database. Exact SQL
names are an implementation detail; the keys and invariants are contractual:

1. **Stream row**, keyed by owner, scope and stream ID: metadata schema version,
   monotonic `writer_epoch`, checkpoint `generation`, nullable current handle/row
   ID/digest, current epoch's restore-pin generation and validated `retain_checkpoints`,
   and `pruned_through` watermark.
2. **Commit catalog**, keyed by stream and generation: immutable operation ID,
   writer epoch, expected predecessor generation and its canonical head digest,
   checkpoint handle, Memory row
   ID, SHA-256 of the frozen payload bytes, frozen time/trigger metadata and its
   digest, and authorization audit reference.
   Enforce handle/row/operation uniqueness for retained entries. Operation identity
   includes stream, proposed generation and random operation ID, so pruning cannot
   allow reuse of an old generation. Do not use capture timestamps for ordering.

Payload remains in the existing exact checkpoint namespace in `memories`.
Metadata schema version is independent of payload schema 1. Metadata contains
no chats, raw events, permissions, action plans, keys or arbitrary paths.
Reject unknown schema, incomplete tables or invalid joins. Initialize/migrate
only after separately authorized Memory write access; disabled C2a performs no
C2b schema I/O. Use transactional creation and validate existing schema rather
than treating malformed/partially present metadata as an empty store.

For each save, freeze the tuple (stream, epoch, expected generation, proposed
next generation, operation ID, checkpoint handle, payload and metadata digests/bytes) before
admission. Inside a short `BEGIN IMMEDIATE` transaction:

1. Recheck policy, job control, exact backend ownership and current writer epoch.
2. Require the expected head generation and exact predecessor tuple to match.
3. Validate absence of conflicting operation/handle/row and enforce bounded
   capacity transactionally with the retention count stored for the acquired epoch.
4. Insert one payload and one catalog entry; compare-and-set the stream head to
   generation + 1. Store the digest of the canonical exact predecessor head in the
   new catalog entry. A zero-row conditional update is a conflict and rolls back all.
5. Recheck the existing cancellation/policy fences, then commit once.

No replace/upsert of payloads, no last-writer-wins save, no head rollback, no retry
with a new UUID on conflict. Any pre-commit error preserves the old head and rows.
After commit entry, failure can be uncertain. A receipt is publishable only after
commit and normal acceptance checks; it proves that historical commit, not
permanent ownership or that another authorized process has not advanced it.

An audit allow entry is authorization evidence, not a commit receipt. Database
commit and the signed audit ledger are not claimed to share an atomic transaction.
Use the retained allow reference plus exact database evidence to inspect outcome.

## Time provenance without invented experience

Keep payload schema v1 and exact restoration unchanged. Its `captured_at` is
retained, but `SelfTrust.last_event_ts` is also updated by ordinary decay reads
(`self_trust.py:99-107`); it is not an immutable event timestamp. The bounded trust
history has no per-event times. Do not reinterpret either as Temporal history.

Freeze a closed, at-most-4-KiB metadata object alongside the payload before
authorization. The immutable catalog and attempt descriptor bind its canonical
bytes/digest as well as the payload digest. Required metadata schema 1 fields:

- `schema`: integer 1, distinct from the unchanged payload schema.
- `session_id`: an opaque 32-lowercase-hex ID for the current observer start.
- `session_started_at_unix_s`: the host UTC wall-clock reading at that start.
- `last_verified_observation_at_unix_s`: wall-clock reading after the fully
  completed, post-ownership-checked tick used for this snapshot.
- `captured_at_unix_s`: exactly the payload's `captured_at`; preserve the original
  value when restoring, not the new startup timestamp.
- `observation_uptime_s` and `capture_uptime_s`: elapsed monotonic durations from
  that session's start, with `0 <= observation_uptime_s <= capture_uptime_s`.
- `save_trigger`: `periodic` or `orderly_stop`; a request reason, not proof of exit.

Reject unknown/duplicate keys, invalid IDs, booleans as numbers, nonfinite or
negative times/durations and inconsistent within-session monotonic ordering.
Wall-clock order can change; do not invent a corrected timestamp. C2a records
lack this metadata and display unavailable provenance rather than guessed values.
No raw monotonic epoch is compared across processes. Operational uptime resets
on restart; persisted elapsed durations describe their original session only.

On startup, retain the raw old observation and new session wall times. Their
nonnegative difference is `observation_gap_seconds`, explicitly labelled a
**host-wall-clock estimate**. A backwards or missing timestamp produces null with
`clock_inconsistent` or `unknown`; positive differences do not certify clock
accuracy. An observation gap includes possible running time after the last
checkpoint and is not exact downtime. `offline_duration_seconds` remains null
with `offline_duration_state: unknown` in C2b unless a later, separate lifecycle
evidence contract supports it. Do not add such a tracker in this milestone.

A Monday-to-Friday restore can report the gap since its last verified observation;
it must restore no invented intervening events, ticks, trust observations or
experiences. Future Temporal integration may interpret retained timestamps under
its own contract. C2b preserves the necessary provenance of each retained state;
it cannot preserve missing event history or give pruned metadata indefinite life.

## Writer fencing, selection and recovery

A fresh C2b startup uses a separately authorized **acquire** operation. Under
`BEGIN IMMEDIATE`, validate/create the exact stream, increment writer epoch,
validate the current head/catalog/payload as one consistent view, pin that head
and persist the validated retention count for this epoch. Commit the acquisition before returning the token and the
detached selected payload. Validate the complete payload before any Core mutation.
A corrupt positive-generation head causes rollback/blocking, not epoch acquisition
followed by a guessed fallback. Apply only after final policy/ownership/deadline
checks, before the first tick, with zero restored live counters.

Acquisition means **explicit takeover for this configured stream**, not a lease
or evidence that the other process is dead. No timer/heartbeat service is needed.
A previously entered write either commits before acquisition or serializes after
it and fails the epoch check. An old process learns that it lost the stream on
its next fenced operation; do not promise immediate notification. It cannot
reacquire automatically. Chat remains independent; observation may continue only
while its existing runtime policy permits it.

Acquisition can itself commit and lose its receipt. Then startup is uncertain
and must not use a guessed token, apply a checkpoint or start writes. A later
explicit launch may acquire a new epoch. There is no automatic reacquire loop.

**Uncertain save:** retain one local attempt descriptor independently of `saved_*`.
Latch uncertainty; reject late acceptance; keep the worker owned until it finishes.
Stop periodic saving and retention for that runtime. Recovery is on a new explicit
launch, through separately authorized acquire/inspection. It never reopens the old
Future, replays its save, or retroactively labels it acknowledged.

A confirmed newer epoch is essential before an inspection can establish absence:
a plain read while an old worker is still in audit could miss its later commit.
Inspect in one consistent transaction, verify that the acquired epoch is still
current, and validate the supplied descriptor: its epoch is strictly older than
the accepted acquisition, proposed generation equals expected generation + 1,
and all identity/payload-digest/metadata-digest fields have their strict bounded formats. Reject current
or future epochs and malformed tuples; they cannot support absence proof.
Compare the descriptor's canonical expected-head digest with the retained
catalog entry's predecessor-head digest so exact matching survives pruning of
the predecessor row. Recover by exact operation descriptor, catalog, head and
payload, not chronology:

| Authoritative outcome after fencing | Recovery result |
| --- | --- |
| Exact retained operation/digest/row equals current head | `committed_current`; it can be restored as newly recovered evidence, not an old accepted receipt |
| Exact retained operation is behind a newer valid head | `committed_superseded`; automatic selection uses the current head; never move backward |
| A retained generation contains a different valid operation | `conflict`; never replay the stale attempt |
| Attempt is beyond the current committed generation, with no matching entry after fencing | `not_committed`; previous writer cannot later commit under its fenced epoch; no automatic replay |
| Missing operation at/below `pruned_through` | `history_expired`; outcome is unknown, not absence |
| Missing catalog within unpruned committed generations, invalid digest/join, or inconsistent identity | `corrupt`; block, preserve evidence and require operator repair |
| Read/acquire denied, busy, cancelled, failed or unacknowledged | Unresolved/blocked; no fallback, guessed epoch or new writes |

Look up an exact retained entry before applying the pruning watermark; protected
older entries can survive below it. Operation inspection is optional diagnostic
input on a later launch. Run any requested inspection after confirmed acquire
and before any startup pruning so maintenance preserves the evidence being
inspected. Unknown prior operation IDs require no input.
Without it, resume validates the authoritative head and reports a new restore;
it makes no claim about the earlier caller's acceptance or missing operation.
Do not reload recovered state into an already-ticking Core.

## Periodic saving and stop arbitration

Use the existing observer owner thread for capture and completion handling and
the existing Memory worker for I/O. A monotonic due time permits one submission
from a new, fully completed, fresh tick. Freeze a detached snapshot; subsequent
ticks cannot mutate the authorized bytes. Skip unchanged snapshots by completed
tick identity, not by applying decay or reading live trust in a status handler.

Do not call C2a's blocking `_checkpoint_exchange()` for periodic work. Poll an
owned Future without blocking ticks, chat or cached status. Retain one outstanding
Memory slot, no queue, no catch-up burst, no executor/thread per save. Expiry closes
acceptance immediately while actual I/O remains owned. Next due time is measured
from an attempt's completion/refusal, preventing a backlog after pauses or clock
rollback. Each attempt keeps the one-second cap and 250 ms SQLite busy timeout.
The owner thread waits on one wake `Event`, bounded by the next tick and any
open acceptance deadline. Worker completion and stop signal that event without
advancing the tick schedule. This handles the 0.1 Hz profile's ten-second tick
spacing within the one-second receipt lifetime using the existing threads.

`StreamJob.admitted` records whether the worker admitted the job.
`acceptance_closed` records irreversible closure of receipt acceptance, while
`outstanding` tracks actual owned work through completion. Only a known busy
refusal before admission can be skipped until the next interval;
there was no write to recover. An admitted denied, failed, conflicted or uncertain
operation disables subsequent persistence for that runtime. Observation can
continue only under existing policy; continuity degradation is visible separately.
Do not perform blocking policy rechecks on the observer/status thread merely
because `Future.done()` is true: current `Future.result()` can run policy/ownership
callbacks. For the new C2b advance API, define an explicit handoff:

1. Keep the Memory slot owned through commit and the final policy/ownership
   callback checks on that worker. A blocked callback is still outstanding work.
2. After those callbacks succeed, atomically seal the immutable result under the
   job control's short lock, checking cancellation/deadline there. Never run an
   external callback under that lock. The final completed callback is the policy
   observation point; sealing linearizes only the local control checks. The
   receipt attests a historical governed commit, not continuing authority.
3. The observer may consume it only before the original deadline and while its
   in-memory cancellation, stop/registration generation and ownership token remain
   valid. Consumption performs no filesystem/policy callback or blocking wait.
   Late consumption is uncertain and cannot populate acknowledged `saved_*`.

Revocation observed by the final callback refuses the handoff. A policy change
after that observation, including the brief window before sealing, does not
erase the historical receipt; timely owner consumption still requires the local
control checks. New acquire/inspect/advance/prune requests independently pass
current policy.
No instantaneous cross-process/global-policy revocation is promised. Preserve
C2a's existing `Future.result()` behavior for its callers. Acquisition/restore
also retains its before-apply policy/readiness check before tick zero; do not use
an acknowledged historical save as permission to apply state or perform an action.
Test both sides of the final policy observation with barriers, plus deadline/ownership
loss between seal and consumption. The implementation plan must make this
handoff a separate explicit API outcome, not silently modify legacy Futures.

On orderly stop: close scheduling; account for the one in-flight job inside the
unchanged total two-second stop budget. If it completes and is accepted, at most
one final save may capture a newer fresh completed tick in the remaining budget.
If unchanged, keep the prior receipt and report that no extra stop save occurred.
Uncertain/pending/conflicted work forbids the final save. No retention at shutdown.
Repeated stop, emergency cleanup and second SIGINT neither reset deadlines nor
submit more work. Memory cannot be detached before actual worker drain; failure
to drain remains an honest failed/pending shutdown, not successful exit evidence.

## Retention and bounded recovery history

Retention is a separate, explicitly authorized transaction after acknowledged
advancement, or after a confirmed new acquisition has validated the current head
and resolved the new runtime's startup uncertainty. Use the same single worker
slot and current epoch/head checks. Allow this startup/pre-save maintenance
after any requested exact inspection and without demanding another save first:
otherwise a crash at capacity deadlocks
recovery. It never runs on a GET, restore-only C2a call or still-uncertain runtime.
It does not turn a successful save into a failed save if pruning fails.

Keep the latest N committed checkpoints (N >= 2 protects head and predecessor),
plus the current epoch's selected restore pin if older. Protect the current
attempt/uncertain target; its transaction either has no row or creates the current
head. Old-epoch pins are released only by a confirmed new acquisition that has
validated/pinned its selected head. There are no arbitrary or unbounded pins.

Delete only exact catalog-member payload rows after identity/digest validation;
delete their catalog entries and advance `pruned_through` in the same transaction.
Never touch conversations, C2a rows, Temporal checkpoints, another stream or an
unregistered orphan. A contradictory reference blocks pruning; do not repair by
broad matching. The current epoch's selected checkpoint cannot disappear between
selection and application. An independent legacy explicit read gets its normal
consistent exact result or a missing error, never a partial payload/fallback.

Bound each transaction to 128 deletions. At most N+2 payload/catalog entries may
exist per stream (N recent, one older restore pin, one transient just-saved entry).
Advance enforces this capacity in its initial implementation, including for
direct callers, using the validated N stored on the acquired epoch.
If pruning is denied/fails or protected capacity cannot fit the next write, pause
new saves with a separate `retention_blocked`/`capacity` status; do not grow forever
or delete protection. Pruning takes precedence over the next save when needed
for capacity. When the operator reduces N, existing rows can temporarily exceed
the new cap; report the pending policy and admit no new saves until separately
authorized bounded pruning reaches it. An increased N does not recreate history.
No full-store scan or VACUUM on the critical runtime path. Retention bounds
logical rows, not physical SQLite file shrinkage. Stream count
is operator-selected; no automatically created stream per restart.

## Governance and observable results

All operations remain under existing Guardian -> Security -> signed audit.
Proposed new intent names: `consciousness.continuity_acquire`,
`consciousness.continuity_inspect`, `consciousness.continuity_advance`,
`consciousness.continuity_prune`. Acquire/advance/prune require
`consciousness:write`, `memory:read`, `memory:write`, `fs:read`, `fs:write`;
inspect requires `consciousness:write`, `memory:read`, `fs:read`.
C2a restore/save intents and callers remain unchanged. Explicit strict-policy
allow plus nonblank signed audit reference is required, including schema creation
and deletion. Add deny/missing-audit cases before enabling any new ingress.

IDs/digests are provenance checks, not authentication. Generic Memory can accept
arbitrary memory types and local SQLite can be edited; owner strings and hashes
do not make the database tamper-proof. Validate exact joins and fail closed on
inconsistency. Separate local data directories provide storage isolation only.
Preserve release signing and strict policies; do not loosen CI or baselines.

Cached status separates: runtime/tick health, configured mode/stream, observed
epoch/generation, selected/restored row, current attempt ID/handle, acknowledged
saved receipt, recovered outcome, outstanding work, retention state and sanitized
error. Label epoch/head as last observed, not a live ownership guarantee. Ordinary
logs/audits contain bounded opaque identifiers, never payloads, private conversation,
keys or filesystem paths. Hub/Observatory GETs cause no audit, I/O, decay or saves.
Checkpoint IDs/content must remain absent from personal retrieval and prompts.

### Observatory recovery and persistence ownership

Project independent cached fields through the existing Hub and Observatory:
`recovery_method`, `recovery_outcome`, `previous_shutdown_evidence`,
`last_save_trigger`, `last_save_acceptance`, `previous_save_acceptance`, `ownership_state`,
`ownership_checked_at_unix_s`, `ownership_lost_at_unix_s`, and the time provenance
above. Recovery method is one of `none`, `new_stream`, `explicit_checkpoint`,
`durable_head`, `exact_inspection`. A new or valid generation-zero stream uses
`new_stream` with `fresh`; it claims no restored observations. Recovery outcome is `not_attempted`, `fresh`,
`restored`, `blocked`, or an exact inspection outcome from the recovery table.
Save acceptance is `none`, `pending`, `acknowledged`, `unacknowledged`, `unknown`;
current-session acceptance uses `last_save_acceptance`; `previous_save_acceptance`
is unknown without independent evidence. Do not mix receipts across sessions.

| Shutdown/continuity condition | Evidence-supported display and action |
| --- | --- |
| Current orderly-stop save acknowledged | Show final checkpoint acknowledged and exact receipt; this alone does not prove the whole runtime subsequently exited cleanly |
| Known unexpected termination | Restore last verified durable head; label unexpected only if independent lifecycle evidence actually establishes it |
| Known interrupted transaction | Recover authoritative committed state; distinguish the inspected result from the cause of interruption |
| Uncertain commit | Show exact inspection after fencing and its outcome; never relabel the old receipt as acknowledged |
| Corrupt selected checkpoint | Block restoration/writes and visibly report failure, with no older/fresh fallback |
| Prior termination not established | Show “Previous termination unknown; restored verified durable head” when restore succeeds |

`previous_shutdown_evidence` is `unknown` for normal C2b restart: the contract
adds no durable exit/acknowledgment protocol. A catalog `orderly_stop` reason
proves a committed stop-request snapshot, not receipt acceptance or clean exit.
Do not infer a crash or interrupted transaction from a missing receipt, a time
gap or the lack of an orderly marker. Future independent lifecycle evidence can
extend the display contract; test-only evidence is not a production classifier.

Ownership states: `disabled`, `not_acquired`, `last_observed_owned`, `lost`,
`uncertain`. A failed epoch comparison latches `lost` with sanitized
`writer_fenced`, records the observation time, disables all further saves/pruning
and visibly says “Persistence ownership lost — checkpoint writes stopped.”
Prior receipts remain historical. The latch survives later ticks, GETs and stops;
no automatic reacquisition. Before detection, label the epoch/check time as last
observed; no immediate cross-process notification is promised.

Keep tick/ThinkStream availability distinct from `continuity_health`
(`disabled`, `pending`, `ok`, `degraded`). Pending startup is pending; last-known
owned with no persistence fault may be ok; lost/uncertain ownership, blocked
restore, failed inspection or blocked retention is degraded. Neither live ticks
nor a prior saved receipt may paint lost continuity green. Periodic saving/saved
states alone must not hide a healthy observer. The current projection accepts
only fresh/restored states as available (`snapshot.py:411-428`); extend that
handling deliberately and retain C2a tests. Every GET stays cached and read-only.

## Verification contract and delivery slices

These are required future tests, not claimed passes. Use real SQLite, actual
Memory/Guardian/Security and the normal full launcher in separate processes.
Offline generation may be doubled only with a responder derived from context.
Use synchronization barriers/fault injection rather than timing-only sleeps.

| Cut or race | Required observation |
| --- | --- |
| Before insert; after payload insert; after catalog/head update but before commit | Restart sees the old complete head; no partial payload/catalog/head transaction |
| After commit, before accepted receipt; crash or lost acquire receipt | One durable generation; old caller remains unacknowledged; new confirmed acquire selects exactly that state or a newer legitimate head |
| Delayed old worker before transaction vs new acquire | Old epoch cannot commit/prune after acquisition; read-before-fence is never accepted as absence proof |
| Two writers from one predecessor; changed payload with same operation identity | At most one advancement; conflict/mismatch preserves prior rows and never silently retries |
| Retained, superseded, expired and contradictory recovery evidence; malformed/current/future-epoch descriptors | Distinct outcomes from one consistent inspection transaction; no replay, head rollback or invented absence |
| Missing/corrupt/future-schema head; duplicate/foreign record; invalid config | Block before tick zero and all subsequent writes; no older-valid/fresh fallback |
| Periodic audit/commit/result-policy callback blocked; revocation before/after final policy observation | Ticks, chat/status responsive; one owned job; observed revocation refused; later policy changes do not erase historical evidence; timely consumption requires local ownership and later operations reauthorize |
| Stop/first and second SIGINT while periodic or retention work exists | Shared stop budget, no overlap/duplicate save, ownership retained to drain; physical-keyboard delivery separately witnessed |
| Retention during selection; revocation/denial; corrupt catalog; capacity or smaller N after restart | Restore pin/head/predecessor safe; atomic pruning; recovery can prune without first saving; paused writes until new cap fits; no unrelated deletion |
| Same stream ID in a separate profile; checkpoint sentinel plus competing chat records | No cross-profile state; actual responder evidence excludes checkpoints; personal recall and honest unknowns preserved |
| Clock rollback, long scheduler pause and no new completed tick | Monotonic spacing, no catch-up burst, no invalid/stale capture or fresh-health claim |
| Automatic-stream smoke and a separate at-capacity fixture | Automatic mode alone permits observations up to 1800 seconds, with the existing 300-second cap for other modes. A 660-second run proves default cadence and exact head restart. A separate real N=2 fixture starts at generation zero, admits a third save at capacity and verifies pruning of a distinct eligible older checkpoint, with protection intact. |
| Monday-to-Friday restore; decay-mutated trust timestamp; legacy record missing provenance | Original verified-observation time retained; gap is an estimate, offline duration unknown; no synthetic events/ticks or reinterpreted event timestamp |
| Committed orderly-stop row without accepted receipt; absent exit evidence | Request trigger shown separately, prior acceptance/termination unknown, no invented clean exit or crash classification |
| Takeover while ticks/chat remain live; later status GET/stop | Ownership loss visibly latched/degraded, saved receipt remains historical, zero reacquisition/additional writes |
| Prune old checkpoints while independent Temporal/history records refer to them | Only exact C2b members removed; history remains unchanged under its own policy |

Task 0 verification is recorded in the
[prerequisite receipt](../../evidence/c2b_prerequisites_2026-11-25.json).
Follow the [implementation plan](../plans/2026-11-25-phase-c2b-checkpoints.md)
in reviewable slices:
(1) Memory schema/acquisition/atomic advance and failure tests;
(2) exact recovery and head selection before tick zero;
(3) nonblocking periodic completion and shutdown arbitration;
(4) bounded retention, cached Observatory projection and full-launch evidence.
Each slice must retain C2a regressions; no runtime activation before its safety
contracts pass. Then run focused tests, full suite, boot/integration/docs/quality,
configured live-model/browser checks, clean-checkout CI and signing verification.
Record source IDs, opaque operation/head/row IDs, authorization references,
provider/fallback identity and actual process exits. Do not reinterpret an
instrumented or deterministic-provider run as live-model/physical-keyboard proof.

The contract deliberately excludes a Temporal framework, leases, distributed
consensus, account isolation, disk-compaction policy, autonomous action and
production readiness. Remaining implementation choices are table/type names and
small module layout; the ordering, bounds, outcomes and authority rules above
are not left to inference. The user approved the defaults and takeover mechanism
with the four clarifications now recorded here. This approval neither closes
ALPHA-CKPT-001 nor passes fresh-install/live/browser/keyboard or merge gates.

[worker]: https://github.com/AetherraLabs/Aetherra/blob/2767230f851a5c8fe646b21d91ea84cd113fbc0e/Aetherra/aetherra_core/memory/lifecycle_checkpoint.py
[observer]: https://github.com/AetherraLabs/Aetherra/blob/2767230f851a5c8fe646b21d91ea84cd113fbc0e/Aetherra/consciousness/runtime_observer.py
[launcher]: https://github.com/AetherraLabs/Aetherra/blob/2767230f851a5c8fe646b21d91ea84cd113fbc0e/aetherra_os_launcher.py
[memory]: https://github.com/AetherraLabs/Aetherra/blob/2767230f851a5c8fe646b21d91ea84cd113fbc0e/Aetherra/aetherra_core/memory/memory_core.py
[advanced]: https://github.com/AetherraLabs/Aetherra/blob/2767230f851a5c8fe646b21d91ea84cd113fbc0e/Aetherra/aetherra_core/memory/aetherra_memory_engine.py
[codec]: https://github.com/AetherraLabs/Aetherra/blob/2767230f851a5c8fe646b21d91ea84cd113fbc0e/Aetherra/consciousness/checkpoint.py
[core]: https://github.com/AetherraLabs/Aetherra/blob/2767230f851a5c8fe646b21d91ea84cd113fbc0e/Aetherra/consciousness/core/consciousness_core.py
