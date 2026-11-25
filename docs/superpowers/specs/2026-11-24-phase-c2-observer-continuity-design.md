# Phase C2: Observer Continuity Design

Prepared: 2026-11-24. Status: proposed; no C2 runtime behavior is implemented.

C1 implementation is committed and pushed as
[b8719fa2](https://github.com/AetherraLabs/Aetherra/commit/b8719fa22b8bd21ea77b3c4aa721522e312e86ea)
on `codex/phase-c-observer`; it is not merged. Its
[source-bound evidence](../../evidence/integration_phase_c1_2026-11-24.json)
is the precommit verification checkpoint. Publishing does not establish hosted
CI, fresh-install, browser or live-model acceptance.

## Goal and boundary

The user's Phase C plan calls for governed continuity of the optional
Consciousness sidecar without taking over chat. The next focused milestone,
**C2a**, will save one bounded aggregate checkpoint at an orderly observer stop
and restore an explicitly selected checkpoint before the first tick of a new
process. Storage belongs to the existing Memory system.

C2a establishes the codec, authority, ownership and recovery contract first.
**C2b** will add automatic checkpoint selection, configurable periodic saves and
retention, after defining atomic head advancement and recovery from an uncertain
write. Completing C2a alone does not complete all Phase C continuity requirements.
No automatic latest selection, pruning, legacy-file migration or new public
checkpoint endpoint is included in C2a.

## Global constraints

- Aetherra remains the persistent cognitive system; Lyrixa is her persona.
- Preserve pending temporal runtime work and unrelated staged/unstaged changes.
- Preserve signing, Guardian/Security enforcement and existing caller behavior.
- Keep the normal full launcher as the entry point. Observer and persistence
  remain separate opt-ins, disabled by default; autonomy stays observe-only.
- No new memory service, observer-owned database, chat answering path, actuator,
  consolidation, QFAC write, experimental import or autonomous execution.
- Local data directories establish storage isolation, not account isolation.
- Ordinary logs contain only opaque receipts and sanitized status/error codes.
- Do not weaken CI, quality baselines, audit checks or release signing.

## Findings that constrain the design

The normal launcher's `MemoryAdapter.impl` is
`AetherraMemoryEngineAdvanced`, whose `core_memory` is
`LyrixaMemorySystem`. Neither adapter nor Advanced has a durable checkpoint API.
The private Engine wrapper's generic store/recall methods are a different
interface. Advanced's compatibility `store/retrieve` methods are in-memory.

Core `store_memory(...)` commits a Memory row and returns its opaque ID, or
`""` on failure. `recall_memories(...)` uses optional exact type filtering but
returns `[]` on both failure and absence; reads also update access statistics.
It is unsuitable as an unqualified exact checkpoint/recovery API.

These async methods perform synchronous SQLite operations. The shared connection
has `check_same_thread=False`, with no transaction serialization. C1 owns its
Core on one daemon thread. Scheduling existing SQLite calls on chat's event loop,
or using that shared connection from the observer thread, is not an acceptable
checkpoint bridge.

Legacy `ContinuityMemory.load()` empties its buffer after corrupt input; a later
save can overwrite the unread data. Legacy Core restoration calls
`SelfTrust.observe("ok"/"warn")` using a 0.7 threshold although scores are 0–100:
a saved score of 40 becomes approximately 100 and gains an invented observation.
C2a must not activate this legacy file path. Exact trust import should be reusable
by that path later; broad standalone file-persistence repair is outside C2a.

Normal personal recall and conversation summaries filter `memory_type` to
`conversation`; checkpoint rows must never enter this evidence. The Engine
wrapper has a broader fallback if `core_memory` is absent. C2a requires the real
owned backend and fails closed instead of using that fallback.

Temporal's immutable checkpoint handles and Maintenance's failed-load save guard
are useful precedents. Temporal is a separate component; Maintenance persists
JSONL, not Memory. Neither supplies the required normal-launch checkpoint bridge.

## Proposed checkpoint contract

All interfaces and configuration in this section are proposed additions.

Use the existing Memory SQLite `memories` table with an immutable row, generated
32-lowercase-hex checkpoint handle and separate opaque Memory row ID.
The exact type is `consciousness_observer_checkpoint:<handle>`, with context
owner `consciousness:observer`, scope `observer_continuity:v1` and schema `1`.
Load by exact type and verify owner, scope, row ID and embedded handle/schema.
Reject missing, duplicate, malformed or incompatible rows; do not choose another
record by similarity, recency, importance or an empty-history fallback.
Owner/scope fields are provenance constraints, not authentication.

Payloads are UTF-8 JSON limited to 64 KiB and eight nesting levels. Check stored
byte length before parsing or allocating an unbounded payload. Store only schema, handle, owner,
scope, capture timestamp, six qualia dimensions, trust half-life and bounded
trust records. Qualia dimensions are exactly valence [-1, 1] and arousal,
certainty, curiosity, care and fatigue [0, 1]. Trust uses at most 64 subsystem
entries with names matching `[A-Za-z0-9_.:-]{1,64}`, scores/history in [0, 100],
at most 64 historical scores per subsystem, nonnegative timestamps and a finite
positive half-life. Reject booleans as numbers, nonfinite values, duplicate JSON
keys, oversized data, unknown fields and future schema versions.

Do not persist conversations, paths, raw events, narrative text, focuses, active
intents, pending actions, permissions, service health, running state or tick
freshness. Runtime tick counters start at zero after restore.

Decode the whole payload into detached state before changing Core. Exact trust
import preserves scores, timestamps and history without calling `observe()`.
Inject a clock into SelfTrust while preserving its existing constructor defaults.
Import itself does not decay or add an event; the next ordinary trust read uses
the existing decay rule with `dt = max(0, now - last_event_ts)`. Pin both equal
time and elapsed-time behavior in tests. Qualia resumes from the stored vector
and follows normal per-tick decay. Historical trust is not present health.

## Proposed Memory I/O boundary

Add a small checkpoint helper owned by the existing Core Memory instance, exposed
through Advanced and the concrete launcher adapter. One lazy daemon worker per
Memory instance owns its own connection to that instance's existing file-backed
SQLite database. No caller-supplied database path, shared chat connection, new
database, unbounded queue or worker-per-request. Reject in-memory/unsupported
database forms explicitly in C2a; test the real file-backed profile.

Submission takes an owned job control object with a cancellation Event, a
monotonic deadline and a pure ownership predicate that can only refuse work.
Set each attempt's deadline to one second from submission, or the caller's
remaining stop budget if shorter. Future.cancel() alone is insufficient once
audit/I/O is running. Expiry or caller abandonment irreversibly closes result
acceptance; do not later acknowledge the future as success.

Freeze validated submission bytes before admission so caller mutation during
audit cannot alter what is authorized or stored. Revalidate that representation
before insert and return detached receipts, never a mutable queued payload.

Submission returns a `concurrent.futures.Future`; the observer can wait on its
own worker while chat's loop stays free. Permit one outstanding job, including
audit work, with no queue; busy is explicit. Use an existing-database-only open,
a 250 ms SQLite busy timeout and short transactions. Validate inputs before
submission, authorize before opening/reading/writing, and insert without replace.
Duplicate handles must fail under concurrent writers using one atomic
check-and-insert transaction. Return a receipt only after commit.

Use existing Guardian intent evaluation, Security capability checks and signed
audit ledger. Proposed actions are `consciousness.continuity_restore` with
`consciousness:write`, `memory:read`, `fs:read`, and
`consciousness.continuity_save` with `consciousness:write`, `memory:write`,
`fs:read`, `fs:write`. Both require allowed plus a nonblank audit receipt.
Use the runtime principal and actual policy; owner strings grant no capabilities.
The exact checkpoint read does not mutate access counters. Audit metadata uses
handles/IDs and sanitized operation details, never checkpoint contents or keys.

Timeout/cancellation is not proof that a write rolled back. Recheck cancellation,
lifecycle ownership and policy before transaction entry; cancellation during
commit can still leave an unacknowledged row. Keep the outstanding slot owned
until actual completion, report uncertainty and forbid automatic retry. A late
result cannot apply state or become an acknowledged successful save. Subsequent
inspection uses the exact handle; no destructive rollback or replacement row.

## Proposed launcher lifecycle

Use a root config object `consciousness_continuity` with `enabled: false`
by default and `restore_checkpoint_id: null` by default. Validate strict booleans,
known keys and a null or 32-lowercase-hex handle. Enabled persistence requires the
enabled observer, enforcing policy and the exact owned Memory implementation.

An enabled fresh start with a null handle deliberately creates a new lineage;
it does not read or overwrite another lineage. With a selected handle, restore
must finish and validate before the first tick. Missing/unreadable/invalid/denied
restore blocks this observer and all checkpoint writes for that instance.
Recovery in C2a is an explicit new launch with a valid selected handle or an
explicit fresh lineage. There is no implicit recovery or fallback.

After at least one fully completed tick, an explicitly requested orderly stop
may save exactly one checkpoint copied from the last completed tick.
Extend stop with keyword-only `save_checkpoint=False` while preserving
`timeout=2.0`. Only the explicit orderly launcher/harness path requests
`save_checkpoint=True`; startup failure, replacement, monitor failure and
emergency cleanup retain the no-save default. A request is not authorization. Failed,
denied, stale, aborted or incomplete ticks never produce a checkpoint. Restore,
status, repeated stop calls and emergency cleanup cannot trigger extra saves.
Keep policy, registration ownership and Memory alive through the save attempt.

The caller's existing bounded stop budget includes checkpoint work. A stuck
worker stays owned; expose pending/uncertain state rather than reporting a clean
stop. Drain it before Memory teardown or report failed shutdown, with no forced
success. Runtime status and continuity status are separate: stopped reflection
does not imply a checkpoint succeeded. Saved receipt fields are published only
after an acknowledged commit. GET status remains cached and side-effect-free.

Expose bounded continuity fields: configured enabled flag, state
(disabled/fresh/restoring/restored/saving/saved/blocked/failed/uncertain),
selected handle, restored row ID, saved handle/row ID, outstanding-work flag and
sanitized error code. Hub and Observatory must not show historical state as a
live tick or expose payloads. Keep the existing no-action status assertions.

## Acceptance and next gate

Use real Memory, governance and separate processes through the normal full
launcher. A generation double may derive chat answers from supplied context;
it cannot replace checkpoint persistence or retrieval. Prove:

- One saved handle and Memory row ID in process A become the exact restored
  handle/row in process B before any completed tick; profile C cannot load them.
- Nontrivial trust scores, timestamps/history and qualia restore accurately.
  Malformed/duplicate/foreign/future-schema records cause no partial mutation.
- Missing or failed restore inhibits saves and preserves all prior rows.
- Denied or unaudited operations perform no checkpoint database access.
- Slow/cancelled/failed I/O stays bounded, preserves chat responsiveness and
  cannot restart workers, replay writes, apply late state or claim false success.
- Checkpoint sentinel data is absent from normal personal retrieval and the
  actual generation prompt; personal recall and honest unknowns still pass.
- Signed audit chains verify, every process exits honestly and all relevant
  tests, full suite, boot/integration, quality and documentation gates pass.

Verify actual Observatory HTTP status and browser rendering separately. Repeat
intentional live-provider personal continuity when credentials are available;
otherwise record it unverified. C1's deterministic result is not a live pass.
Do not extend the current GO decision until C2 evidence exists. Hosted review
and CI for C1 remain separate from this preparatory document.
