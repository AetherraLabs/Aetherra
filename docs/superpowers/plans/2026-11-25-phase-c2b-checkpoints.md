# Phase C2b Checkpoints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or
> superpowers:executing-plans to implement this plan task by task. Steps use
> checkbox (`- [ ]`) syntax. Contract approval is recorded; prerequisite gates
> remain outstanding. No implementation or test pass is claimed by this plan.

**Goal:** Recover an explicitly configured observer stream through Memory's
atomic head, preserve honest failure/time evidence, save periodically without
blocking observation, and bound recovery snapshots without deleting history.

**Architecture:** Extend the single existing Memory checkpoint worker with
transaction helpers and a nonblocking result handoff. Add one owner-thread
session helper to the existing observer; it is neither a service nor a persistence
authority. Project cached recovery, clock provenance and ownership through the
existing Hub and Observatory.

**Tech Stack:** Python 3.13 supported source profile, existing SQLite and
Guardian/Security/audit interfaces, pytest; existing React/TypeScript Observatory
and Node 22.18.0. No new runtime dependency or provider is required.

**Spec:** [Approved C2b contract](../specs/2026-11-24-phase-c2b-checkpoint-contract-design.md),
approved with the user's four clarifications on 2026-11-25.

## Global constraints

- Preserve pending Temporal and unrelated work; isolate changes on a `codex/` branch.
- Preserve Aetherra/Lyrixa identity and the normal full-launcher chat path.
- Existing Memory is the only durable authority; preserve C2a APIs/defaults and
  payload schema v1. No implicit adoption or deletion of legacy/C2a records.
- Defaults: 300-second interval (strict integer 30-86400), retain 10 (2-100),
  64 KiB payload, eight nesting levels, 4 KiB metadata, one-second attempt,
  250 ms SQLite busy timeout and unchanged two-second orderly-stop budget.
- One owned worker/slot, no queue, no automatic retry/reacquisition, no extra
  persistence threads/services. Actual completion owns the slot through drain.
- Checkpoints are recovery state, not temporal history; independent histories
  and future runtime incidents retain separate records/policies under Memory.
- Guardian/Security, signed audit, release signing, CI baselines and privacy
  rules stay enforced. Directory storage isolation is not account isolation.
- [ALPHA-CKPT-001](../../DEVELOPMENT_ISSUES.md#alpha-ckpt-001--checkpoint-stop-delay)
  remains OPEN, cause unknown. No passing rerun or C2b milestone closes it.

## Review focus

1. Stale worker still in audit when a new runtime acquires: fencing must precede
   absence proof, and malformed/current/future epoch descriptors must fail (Tasks 1-2).
2. Lost receipt and pruning at capacity or lower configured N: no replay, false
   absence or recovery deadlock (Tasks 2 and 4).
3. Blocked final policy callback and stop racing periodic completion: ticks/status
   remain responsive, acceptance expires permanently, work remains owned (Task 3).
4. Monday-to-Friday restore, backwards clock and absent exit witness: no invented
   offline duration, event time, clean exit or crash cause (Tasks 1, 2 and 5).
5. Takeover while chat/ticks continue: visibly degraded persistence stays latched;
   old saved receipts do not make it healthy and no reacquisition occurs (Tasks 3, 5).

## Task 0: Close prerequisites and bind the implementation baseline

**Files:** Current follow-up evidence, readiness checklist/decision and this plan.
No C2b product edits during this task.

- [x] Review/publish the checkpoint-stop follow-up, inspect final diff and hosted
  CI, merge if clear and verify a clean main checkout. Record the exact SHA;
  do not reuse the old branch's suite as clean-main evidence.
- [x] Complete supported-profile fresh Python installation, current browser,
  intentional configured live-model and actual physical-keyboard shutdown checks
  from `docs/ALPHA_OPERATOR_RUNBOOK.md`. A programmatic SIGINT or deterministic
  responder does not satisfy the last two. Record unverified gates honestly.
- [x] Keep ALPHA-CKPT-001 open and the existing GO scope unchanged unless its
  separate closure/evidence requirements are met. Approval of this design is
  not an approval of new readiness claims.
- [x] Compare source interfaces with the contract trace at `2767230f`; record
  divergences before coding. Snapshot protected workspaces/index/files/controls.
  Create the isolated implementation branch and use the established isolated
  execution environment so tests cannot inherit credentials or modify user data.

Task 0 verification is recorded in the
[2026-11-25 prerequisite receipt](../../evidence/c2b_prerequisites_2026-11-25.json).
The isolated implementation branch is based on released main `a30277e3`.
All seven traced source files match `2767230f` with no interface divergences.
The receipt links the archived original and pending Temporal workspace
comparisons of HEAD, index, status, files and controls, plus the fresh Python
profile and credential-filtered isolated runner evidence for the checked
pre-flight step. Both actual Ctrl+C runs exited zero, closed their Hub ports
and produced durable rows.
Restart restored the selected row. Physical receipt acceptance remains unknown
for both shutdowns. Task 0 preparation makes no C2b product changes.

## File and interface map

| File | Responsibility |
| --- | --- |
| `Aetherra/aetherra_core/memory/checkpoint_stream.py` (new) | Frozen request/result types, metadata validation and Memory-owned SQL helpers; no worker/service |
| `Aetherra/aetherra_core/memory/lifecycle_checkpoint.py` | Existing worker admits stream jobs, authorizes and seals results while preserving legacy Futures |
| `Aetherra/aetherra_core/memory/memory_core.py` | Expose narrow stream submissions on its existing worker |
| `Aetherra/aetherra_core/memory/aetherra_memory_engine.py` | Exact owned Core forwarding |
| `aetherra_os_launcher.py` | Exact adapter forwarding, settings and orderly lifecycle |
| `Aetherra/consciousness/checkpoint_session.py` (new) | Owner-thread automatic stream state, scheduling, receipt consumption and cached status |
| `Aetherra/consciousness/runtime_observer.py` | Integrate optional session, capture verified tick metadata and apply restore before tick zero |
| `Aetherra/runtime_ui/snapshot.py`, `aetherra_hub/blueprints/consciousness.py` | Strict bounded cached projection, independent runtime and continuity health |
| `Aetherra/lyrixa/gui/src/SubsystemEvidence.tsx` | Recovery/ownership/time labels in the existing read-only Observatory |
| `tools/alpha_consciousness_continuity_smoke.py`, `tools/alpha_consciousness_smoke.py` | Same-launcher multi-process evidence, retaining C1/C2a modes |

All types below live in `checkpoint_stream.py` unless stated otherwise. Use
frozen dataclasses and detached immutable bytes. Numeric booleans are rejected.

- `StreamKey(owner: str, scope: str, stream_id: str)` fixes existing owner/scope.
- `StreamHead(generation: int, checkpoint_id: str | None, record_id: str | None,
  payload_digest: str | None, metadata_digest: str | None)` is wholly null except
  generation at zero; otherwise every member is validated.
- `StreamToken(key: StreamKey, writer_epoch: int)` is a fencing token, not authority.
- `SnapshotMetadata` has exactly the eight fields and bounds in the spec's time
  section: schema, session ID, session start, observation/capture wall times,
  observation/capture elapsed durations and trigger. Canonical serialized form
  is at most 4 KiB; reject extra keys. `schema` is integer 1.
- `AttemptDescriptor(token: StreamToken, expected_head: StreamHead,
  operation_id: str, checkpoint_id: str, payload_digest: str, metadata_digest: str)`
  determines proposed generation as expected + 1; retains all recovery identity.
- `AdvanceRequest(attempt: AttemptDescriptor, payload_bytes: bytes,
  metadata_bytes: bytes)` is frozen/validated before admission; hashes must match.
- `AcquiredStream(token: StreamToken, head: StreamHead,
  checkpoint: LifecycleCheckpoint | None, metadata: SnapshotMetadata | None,
  retention_needed: bool)` returns exact detached state, never a fallback.
- `AdvanceReceipt(attempt: AttemptDescriptor, head: StreamHead, audit_id: str)`;
  `InspectionResult(outcome: str, head: StreamHead, matched_record_id: str | None)`;
  `PruneResult(head: StreamHead, deleted_count: int, pruned_through: int,
  retained_count: int)` use the spec's closed outcomes and bounded IDs/counts.
- `StreamCompletion[T](value: T | None, error_code: str | None)` has exactly one
  outcome. `StreamJob[T].poll(*, local_owned: bool) -> StreamCompletion[T] | None`
  returns pending or the detached completion without external callbacks/I/O;
  consumption enforces the original deadline and local token under its short
  lock. `admitted` records actual admission, `acceptance_closed` records irreversible
  closure of receipt acceptance (including through `cancel()`), and `outstanding`
  tracks owned work through actual completion. Legacy `Future.result()` semantics
  are unchanged.

## Task 1: Governed stream acquisition, atomic advancement and time metadata

**Files:** First five files in the map, new
`tests/unit/test_memory_checkpoint_stream.py`; retain
`tests/unit/test_memory_lifecycle_checkpoint.py` and codec/Core tests.

**Interfaces produced on Core/Advanced/adapter (keyword-only):**

- `submit_acquire_checkpoint_stream(key: StreamKey, start_mode: str,
  retain_checkpoints: int, control: CheckpointJobControl) -> StreamJob[AcquiredStream]`
- `submit_advance_checkpoint_stream(request: AdvanceRequest,
  control: CheckpointJobControl) -> StreamJob[AdvanceReceipt]`

- [ ] Add failing real-SQLite tests `test_stream_create_resume_and_conflicts`,
  `test_advance_is_payload_catalog_head_atomic`, `test_competing_writers_cas`,
  `test_acquire_fences_delayed_old_worker`, and
  `test_denied_or_unaudited_stream_operation_never_opens_database`. Assert exact
  generation/row IDs, no loose-row adoption, one winner and zero unrelated writes.
  Cover transactional capacity refusal for direct advance calls at the acquired
  epoch's validated N, including after a lower-N acquisition.
- [ ] Add `test_metadata_freezes_and_round_trips`, rejecting >4096 bytes, unknown
  keys, boolean/nonfinite/negative times, invalid monotonic order and hash mismatch.
  Mutation during blocked audit must not alter authorized bytes. Keep wall-clock
  rollback representable without rewriting times; metadata capture equals payload.
- [ ] Run `python -m pytest tests/unit/test_memory_checkpoint_stream.py -q` and
  retain expected absent-API failures before implementation.
- [ ] Implement `checkpoint_stream_heads` and `checkpoint_stream_commits` in the
  existing Memory DB with keys/uniqueness, schema validation, generation/epoch
  monotonicity, restore pin and pruning watermark from the spec. Persist validated
  `retain_checkpoints` with the acquired epoch. Store the canonical exact
  predecessor-head digest in each immutable catalog entry. Authorize before
  any schema/database access. Reuse the existing worker connection/slot, not
  generic store/recall or a second executor. Keep legacy `_authorize` behavior;
  add stream authorization returning both intent and nonblank audit reference.
- [ ] Implement acquisition and advance under `BEGIN IMMEDIATE`, the strict
  identity/digest joins and final policy/control checks. Enforce capacity in initial
  advance using N from the current epoch's stream row. No replace/upsert,
  generation reset or auto retry. Seal C2b results on the Memory worker; poll is
  in-memory only. Do not hold admission/control locks during callbacks.
- [ ] Run the new file plus `tests/unit/test_memory_lifecycle_checkpoint.py`,
  `tests/unit/test_memory_core_guardian.py`, `tests/unit/test_consciousness_checkpoint.py`
  and `tests/unit/test_consciousness_observer_core.py`; require exit zero.
- [ ] Review only Task 1 diff, verify controls/preserved work and commit the
  implementation/tests together, with code activation still opt-in/unwired.

## Task 2: Exact recovery and automatic selection before tick zero

**Files:** Memory stream helper/worker/forwarders, new session helper, observer
and launcher; new `tests/unit/test_checkpoint_session.py`; extend
`tests/unit/test_consciousness_observer_continuity.py`.

**Interfaces:** Add `submit_inspect_checkpoint_stream(token: StreamToken,
  attempt: AttemptDescriptor, control: CheckpointJobControl)
  -> StreamJob[InspectionResult]` to the same forwarding chain.
`ObserverCheckpointSession(memory, automatic, *, wall_clock, monotonic_clock,
 still_owned)` is created/used only by the observer owner thread. It exposes
`begin_start()`, `poll(*, local_owned: bool)`,
`take_restore() -> AcquiredStream | None` (once), and `get_cached_status() -> dict`.
Clock and ownership arguments are callables; all external authorization/ownership
callbacks for I/O run on Memory's worker. `poll` cannot initiate reacquisition.
Observer adds optional `automatic: dict | None = None` and
`recovery_attempt: AttemptDescriptor | None = None`; existing callers retain
defaults. The launcher validates optional `consciousness_continuity.recovery_attempt`
outside the closed `automatic` object and forwards it for enabled automatic resume
of the same stream only.

- [ ] Add failures for every recovery-table outcome: current/superseded commit,
  conflict, fenced absence, expired history and corrupt join. Reject current or
  future epoch descriptors and changed payload/metadata or predecessor-head digests.
  Cover exact retained-operation matching after its predecessor has been pruned.
  Inspect in one
  transaction with a still-current accepted fence; no writes or legacy save replay.
- [ ] Add config tests for absent/false automatic preserving C2a, strict interval
  and N bounds, create-existing/resume-missing errors, and mixed explicit/automatic
  rejection. Cover malformed descriptors, foreign streams, invalid modes and denied
  inspection. Missing/corrupt metadata blocks ticks and writes without fallback.
- [ ] Add `test_resume_restores_exact_state_before_tick_zero` and
  `test_monday_friday_gap_is_not_offline_experience`: retain old verified-observation
  time, zero fresh counters, current monotonic uptime starts at zero, no new trust
  observations, gap labelled host-clock estimate and offline duration null.
  Negative gap is null/clock_inconsistent; missing C2a metadata remains unknown.
- [ ] Run the new session file and affected observer tests; retain expected failures.
- [ ] Implement the spec's config/start sequence and exact inspection using the
  retained canonical predecessor-head digest. Run any requested inspection after
  confirmed acquire and before startup pruning. Capture
  current session times separately from restored metadata. Call Core's existing
  detached import only once on its owner thread, after final before-apply policy
  and ownership checks. Acquisition uncertainty cannot yield a guessed token.
  No already-ticking Core is rehydrated by later inspection.
- [ ] Rerun new/affected files plus C2a lifecycle/Core/Guardian regressions;
  require exit zero and no personal-recall namespace changes.
- [ ] Review and commit this slice; keep periodic scheduling off until Task 3 passes.

## Task 3: Nonblocking periodic saves and bounded stop arbitration

**Files:** Session helper, observer, worker handoff and launcher;
`tests/unit/test_checkpoint_session.py`,
`tests/unit/test_consciousness_observer_continuity.py`,
`tests/unit/test_launcher_windows_sigint.py`.

**Interfaces:** Session adds
`on_completed_tick(state: ObserverCheckpoint, *, observation_wall: float,
 observation_uptime: float, capture_uptime: float) -> None`,
`begin_stop(*, deadline: float, save_checkpoint: bool) -> None`, and `cancel()`.
Its `poll` consumes results/schedules at most one eligible job. Capture times are
recorded after the completed tick and final ownership check, before its snapshot;
use one owner-thread snapshot so the two monotonic durations are ordered.

- [ ] Write barrier/clock-driven failures: one save per due new completed tick;
  no queue/catch-up; unchanged or stale candidate skipped; metadata frozen during
  later ticks. Block audit, commit and final policy callback independently and
  prove ticks, chat heartbeat, status and stop remain responsive.
- [ ] Test policy revocation observed at the final callback rejects the result;
  a later policy change does not erase historical evidence. Deadline/cancellation
  or local-owner loss before consumption rejects late results. Keep the slot
  owned through final callbacks; no policy I/O occurs in `poll` or GETs.
- [ ] Test timely completion during the 0.1 Hz profile's ten-second inter-tick
  wait, expiry at the acceptance deadline and stop wakeups, with the tick schedule
  unchanged. Distinguish pre-admission busy skips from admitted jobs whose
  acceptance closes while work still needs to drain.
- [ ] Test stop during pending/uncertain/accepted periodic work: total two seconds,
  at most one final newer-tick save if budget allows, no retention at stop,
  repeated stop/second interrupt cannot extend or duplicate. Real drain remains
  required before Memory teardown.
- [ ] Run targeted session/observer/signal tests and retain pre-fix failures.
- [ ] Implement monotonic due scheduling, latches and shared stop deadline.
  Use one owner-thread wake `Event` signaled by worker completion and stop, with
  waits bounded by the next tick and open acceptance deadline. Keep the tick
  schedule independent of wakeups and use existing threads. Skip only known busy
  refusals before admission, and drain actual outstanding work. Do
  not reuse blocking `_checkpoint_exchange` for periodic work. `writer_fenced`
  latches ownership lost, disables saves/pruning and never reacquires, even if
  observation remains policy-allowed and chat continues.
- [ ] Rerun targeted tests and C2a smoke-helper regressions; require exit zero,
  original no-save cleanup and legacy receipt checks unchanged.
- [ ] Review and commit this slice without claiming physical-keyboard coverage.

## Task 4: Bounded retention with recovery-safe capacity handling

**Files:** Stream helper/worker/forwarders/session;
`tests/unit/test_memory_checkpoint_stream.py`, `tests/unit/test_checkpoint_session.py`.

**Interface:** `submit_prune_checkpoint_stream(token: StreamToken,
 expected_head: StreamHead, retain_checkpoints: int,
 control: CheckpointJobControl) -> StreamJob[PruneResult]` on the same chain.

- [ ] Add failures for exact member deletion, head/predecessor/restore-pin protection,
  pruning during restore, uncertain runtime refusal, revocation/unaudited denial,
  metadata inconsistency and concurrent takeover. Preserve unrelated/C2a/Temporal
  rows, including history referencing a deleted checkpoint; no cascade deletion.
- [ ] Test crash/restart at N+2 and lowering N=100 to N=2: confirmed acquisition
  may separately authorize pre-save pruning after any requested exact inspection.
  No new save is needed to unlock it. Test startup ordering with an inspectable
  retained operation that would otherwise be pruned.
  New saves remain paused until capacity fits. Increasing N recreates nothing.
- [ ] Test retained-old-entry lookup before watermark, pruned history_expired
  versus corrupt unpruned gaps, maximum 128 deletions and failed pruning retaining
  the acknowledged save. No failure can turn pruned evidence into absent history.
- [ ] Run targeted tests, retaining expected failures before adding pruning.
- [ ] Implement one authorized short transaction that validates exact rows, deletes
  payload/catalog members and advances watermark atomically. Use the acquired
  epoch's stored N for maintenance and require the request's N to match it.
  Never prune on GET,
  shutdown or still-uncertain runtime. Schedule pre-save cleanup when capacity
  requires it, and surface retention_blocked/capacity without unbounded growth.
- [ ] Rerun stream/session tests and consolidation exclusion regression
  `tests/unit/test_memory_lifecycle_checkpoint.py`; require exit zero.
- [ ] Review and commit only the retention slice and its focused tests.

## Task 5: Truthful Observatory and end-to-end evidence

**Files:** Snapshot/Hub/GUI/smoke files in the map;
`tests/unit/test_runtime_ui_consciousness.py`,
`tests/unit/test_hub_consciousness_observer.py`,
`Aetherra/lyrixa/gui/tests/evidence.test.mjs`,
`tests/acceptance/test_consciousness_continuity.py`; operator/checklist/decision
and Consciousness/active-system docs plus a dated compact evidence receipt.

**Interfaces:** Preserve existing status fields. Add the spec's closed recovery,
shutdown-evidence, save-trigger/acceptance, ownership, continuity-health and time
fields to the session cache and bounded scalar projection; no new HTTP route.
Map to existing `continuity_` metrics for the GUI. Raw payloads stay excluded.

- [ ] Add projection/renderer failures for ownership lost with live ticks, pending
  periodic save with healthy observer, current acknowledged stop vs prior unknown
  acceptance, corrupt restore, clock inconsistency and unavailable legacy metadata.
  Assert exact operator labels from the spec and unknown prior termination;
  no missing-receipt-to-crash inference or historical tick freshness.
- [ ] Verify repeated status reads trigger zero audit, database work, save,
  reacquisition or trust decay. Ensure `snapshot.py` no longer hides legitimate
  periodic saving/saved observer states while degraded continuity remains visible.
- [ ] Run Python projection tests and GUI `npm test`, retain expected failures,
  then implement the cached projection and existing-panel display. Rerun those
  tests plus `npm run build` and `npm run lint`; require exit zero.
- [ ] Extend the existing smoke CLI with `--automatic-stream` (requires
  `--continuity`), preserving default C1/C2a behavior. Use the normal full launcher,
  real Memory/governance and separate process profiles; no demonstration route.
  Raise only automatic-stream mode's `--observe-seconds` maximum to 1800 seconds.
  Keep the existing 300-second maximum for C1/C2a and cover these mode-specific
  limits. Update smoke source-hash coverage for the new helper files.
- [ ] Add real process crash cuts before insert, after insert, after head update
  before commit and after commit before acceptance. Confirm old-or-new complete
  transaction, exact generation/row IDs after fencing, no replay/late acceptance,
  orderly and forced stops truthfully distinguished in evidence. Use test barriers
  in the harness, not production environment flags or weakened budgets.
- [ ] Exercise takeover between two live runtimes while chat continues, visible
  ownership-loss latch and zero later writes/reacquisition; fresh-profile denial;
  Monday/Friday synthetic timestamps without invented experiences; separate
  Temporal-type sentinel surviving pruning. Real history/reasoning is not activated.
- [ ] Prove checkpoints and metadata stay out of actual personal-recall context;
  competing personal facts and honest unknowns pass through a context-derived
  offline responder. Repeat with an intentionally configured real provider for
  live evidence; fallback/doubles never count as a live-model pass.
- [ ] Run `python -m pytest tests/acceptance/test_consciousness_continuity.py tests/acceptance/test_personal_continuity.py -q`, then the unchanged full suite,
  `python tools/alpha_boot_validation.py`, `python -m Aetherra.integration_validation`,
  `python tools/python_quality.py`, `python tools/verify_docs_consistency.py`, and
  `git diff --check`. Record actual exits/skips; restore generated reports after
  archiving evidence, not by including unrelated output in the implementation.
- [ ] Use the existing smoke command with a fresh disposable directory:
  `python tools/alpha_consciousness_smoke.py --output C2B_EVIDENCE --observe-seconds 660 --continuity --automatic-stream`.
  Prove at least two eligible 300-second periodic saves and restart at the exact
  head. Tests may inject clocks, but this default-interval evidence must preserve
  production scheduling and attempt deadlines.
- [ ] Capture separate real retention evidence with an N=2 at-capacity fixture starting from generation zero.
  Verify the third save is acknowledged, observe an actual eligible older
  payload/catalog deletion, and check the retained count, pruning watermark,
  head/predecessor/restore-pin protection and unrelated-row preservation.
- [ ] Verify browser recovery/ownership/clock labels, stop/reconnect, intentional
  live-model conversation and physical keyboard shutdown on the final supported
  revision. If any cannot run, keep that gate unverified; do not broaden GO.
- [ ] Review and commit only implementation/tests/docs; inspect hosted CI, merge
  only when authorized/clear, then verify clean main and release signing. Preserve
  original/pending work hashes and ALPHA-CKPT-001's unresolved causal status.

## Plan disposition

The contract is approved. Task 0 prerequisites are verified within the receipt's
recorded scope. Tasks 1–5 remain open. Runtime incident tracking,
long-term Temporal history and temporal reasoning remain separate later work.
