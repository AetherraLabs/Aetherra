# Governed Temporal history in existing Memory

> Historical implementation record: delivery restrictions and pending-work statements below describe this slice when it was executed. The source, Memory foundation and runtime integration are now combined in the Temporal milestone; current operation and verification limits are documented in [Temporal history](../../TEMPORAL_HISTORY.md).

Status: implementation contract, 2026-11-26. The user accepted changes at five-second sampling points plus session/gap markers, with no automatic deletion. This is the next Memory slice after the locally verified source projection. It does not activate a runtime observer or change Lyrixa's answers.

## Authority and scope

Use the existing profile Memory database, through core Memory, advanced Memory and the launcher's exact-instance MemoryAdapter. A separate lazy serialized daemon owns its connection and single outstanding job; C2b retains its own worker and slot. No new service, independent database, generic replacement/deletion API or widened C2b payload. Existing standalone Temporal engine APIs remain unchanged. Distinct data directories provide storage isolation, not account isolation.

Typed owner/scope are fixed to consciousness:temporal and temporal_history:v1. Opaque history IDs, operation IDs and record IDs are 32 lowercase hexadecimal characters. Epochs and ordinals are positive bounded integers; an empty head is ordinal zero with null record ID/digest. Ordering is by committed ordinal, never wall time.

## Closed data model

TemporalSource contains exactly the eight scalar fields from the accepted Core projection: source session ID, session start Unix seconds, sequence, observation Unix seconds, monotonic observation uptime, and the three numeric counts. Reject booleans as numbers, nonfinite/negative times, invalid IDs, nonpositive sequences, negative or excessive counts and unknown fields. It contains no labels, prompts, conversations or arbitrary metadata.

TemporalEvent contains record_id, kind, source, captured_at_unix_s and reason. Kinds/reasons are closed:
- session_start: created or resumed;
- observation: null;
- gap: restart, source_unavailable or source_changed;
- session_end: orderly_stop.

Every marker is anchored to a supplied verified source observation. A marker does not invent another numerical moment or an experience during a gap. Session end means this collector closed, not that the operating system exited. Capture wall time and source wall time may move backwards; preserve both without sorting by them or claiming exact offline duration.

An append has an immutable tuple of one to three events, at most 4 KiB canonical UTF-8 per event. Canonical JSON rejects duplicate keys and noncanonical bytes on read. Stored envelopes include schema version, history ID, ordinal, writer epoch, operation ID, prior record digest, event and digest. A SHA-256 chain detects accidental modification, not an adversarial database rewrite or a substitute for signed governance audit.

## Admission and typed API

New submit methods on the three existing Memory layers:
- submit_acquire_temporal_history(key, start_mode=create|resume, control)
- submit_append_temporal_history(request, control)
- submit_read_temporal_history(token, selected_head, after_ordinal, limit, control)
- submit_inspect_temporal_append(token, request, control)

Use the existing CheckpointJobControl and StreamJob/StreamCompletion local polling protocol. Admission validates and freezes bounded types before starting work. Polling, cancellation and pending status run no Guardian, audit, SQLite or external ownership callback. Each attempt has at most the existing one-second bound. A closed acceptance window never reopens. Late jobs remain owned until actual settlement. Callback cancellation or terminal worker failure settles and wakes the admitted job; a dead worker cannot report drained with an outstanding slot or accept more work. Release per-job ownership references before idle waiting. Drain is bounded and reports unfinished work truthfully.

HistoryKey, HistoryToken, HistoryHead, TemporalSource, TemporalEvent, AppendRequest, HistoryRecord, HistorySelection, AppendReceipt, HistoryPage and AppendInspection are frozen typed values. The append request identifies token, exact expected head, operation ID and canonical events; its digest covers all of them. Receipts carry that request digest, exact stored records, resulting head and audit ID. Read pages have at most 64 records, the exact selected head and a next ordinal. No API attaches the full archive to a prompt.

## Transactions and recovery invariants

Dedicated tables hold heads, immutable records and exact append receipts. They are outside generic chat memory and outside checkpoint pruning. There is no automatic deletion or retention setting. Schema or row corruption fails closed; missing storage is never created by resume.

Create atomically establishes an explicitly empty history and epoch 1; existing history conflicts. Resume validates the durable head and its exact batch/receipt, then atomically increments its epoch. Takeover may fence a still-live process. There is no automatic reacquisition. Every append/read/inspection checks the current token epoch. An old writer cannot commit after a newer acquisition commits.

Append is one bounded transaction: compare the epoch and exact expected head, validate transition, insert all events and exact receipt, then advance the head. No partial batch or acknowledged row without a head. Identical operation replay by the current epoch returns the original receipt; changed bytes with that operation ID conflict. After takeover, the old request can only be inspected by a newer epoch.

Transition rules:
- First append of a newly created empty history: session_start(created), observation.
- First append in a resumed writer epoch: session_start(resumed), gap(restart), observation when history is nonempty; start(resumed), observation when still empty.
- Within an epoch: observation; gap plus observation; or session_end. No append after session_end without explicit resume.
- Marker and observation in the same batch share the same source. A new observation in the same source session must keep the exact session-start timestamp, increase sequence and nondecrease monotonic uptime, including across writer takeover. Within an epoch a changed source session requires gap(source_changed); gap(source_unavailable) is same-session resumption with a new verified observation. Reject reactivation of a previous source session after a different source session replaced it. Reserve gap(restart) for the resumed-epoch opening batch; it denotes collector takeover/restart, not proof of a Core/OS restart.
- Ordinary observation requires at least one changed count; reject unchanged with an explicit unchanged result code and no write. A first/gap observation may repeat counts. Session_end anchors to the exact complete last durable source; changed final observations must be saved before ending.
- The future consumer tracks sampled-but-unchanged source sequences in RAM. Memory does not claim unsaved samples as durable observations or enforce a sampling scheduler.

Read a bounded contiguous page within an exact selected committed head, validate envelope/digests and predecessor links, and reject corruption. Acquisition checks the head batch, not every historical row; pages check their records and boundary links. Consumers must validate every page restored and label a bounded tail as a partial history window. No full-archive scan occurs under a one-second acquisition. Concurrent later appends do not change the selected prefix. Selection/read never silently substitute another head or an empty archive. A later engine restoration adapter must preserve IDs and ordinal order; calling process_temporal_moment to replay would invent IDs and recompute causal associations, so that integration is deferred.

An expired/failed acknowledgement after commit starts is uncertain, never proof of rollback. The same lane must settle before reuse; a new process/lane can recover after its explicit resume transaction fences the old epoch, even if an old process is blocked before SQL. After this fence, inspection compares the complete original request identity with stored receipt and records, returning committed_current, committed_superseded, not_committed or conflict/corrupt. A different request is never accepted merely because it has the same operation ID. Missing receipt alone is not proof of not_committed: validate the expected predecessor and inspect the proposed ordinal range, operation ID and all event IDs. A missing expected predecessor is corrupt. Return not_committed only if none exists and the head has not occupied the range. A different valid operation occupying it is conflict; missing receipts for present records, holes below the head, partial batches or contradictory IDs are corrupt.

## Guardian, Security and shared SQLite

Use the existing strict policy and signed audit helpers; require the current effective principal (default consciousness:core), capabilities consciousness:write, memory:read and fs:read for every operation, plus memory:write and fs:write for acquire/append, and specific Guardian actions consciousness.temporal_history_acquire, consciousness.temporal_history_append, consciousness.temporal_history_read and consciousness.temporal_history_inspect. This slice adds no policy grants. Missing/denied policy, capability, containment or audit fails closed. The shared signed audit boundary serializes competing processes through Guardian's existing OS sidecar lock, preserving key identity, chain format and signing. Read-only verification never creates sidecars/directories; an export without one validates captured signed bytes and rejects an incomplete snapshot.

Authorize/audit and recheck policy plus exact Memory ownership immediately before entering SQL. Recheck after the transaction before sealing a successful result. Never invoke external policy, audit or ownership callbacks while holding the SQLite transaction, queue lock or receipt lock. Inside SQL use only bounded work and local deadline/cancellation/closing checks, including a progress handler.

The pretransaction authority check is the permit boundary. Revocation racing the bounded transaction may leave a committed but unacknowledged result; the postcommit check reports uncertainty and cannot roll it back. Do not claim policy revocation and SQLite commit are one atomic operation. A failed pretransaction check has no durable effect.

SQLite has one writer even with separate connections. Use short transactions and a bounded busy timeout. The signed Security audit ledger also has a shared path lock. A disk, SQLite or signed-audit stall can still affect both lanes; this contract cannot guarantee C2b saves succeed during shared storage/authority failure. It must preserve C2b's existing deadlines, independent admission, prompt/cached-status responsiveness and truthful failed/uncertain/pending outcomes. Core Memory close closes Temporal admission immediately, gives C2b its existing priority, and shares the existing total one-second drain budget; retain the core connection if either lane remains outstanding. Ordinary close_connection callers use this same drain; forced disposal after a failed rollback remains separate. The engine awaits the real Core drain off its event loop and retains the exact pending cleanup through cancellation/retry, without changing legacy thread-affine closers.

## Verification and delivery limits

Use real SQLite/core Memory, real strict Guardian/capability/signed-audit fixtures, adapter identity checks and separate OS processes. Prove exact IDs/digests after restart, separate-profile exclusion, atomic rollback, uncertainty inspection after fencing, stale writer rejection, missing/corrupt/denied cases, immutable payloads, bounded pages, change suppression, marker boundaries, clock rollback, blocked audit without a SQLite write lock, bounded busy/drain and independent C2b slot/pruning.

Keep ordinary logs free of event content. This is storage evidence only: engine restoration, five-second runtime sampling, launcher activation, Observatory/browser status and end-to-end runtime checks are later slices. Existing signing controls, pending Temporal prototype, alpha drafts and unresolved issue records remain unchanged. No commit/push/publication is part of this slice.
