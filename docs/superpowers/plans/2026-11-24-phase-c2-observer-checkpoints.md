# Phase C2a Observer Checkpoints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Save one governed observer checkpoint at orderly stop and restore an
explicitly selected checkpoint accurately before ticks in a new normal launch.

**Architecture:** Extend the existing Memory ownership boundary with exact,
bounded checkpoint I/O on its own worker connection to the same SQLite store.
Restore detached validated aggregate state on the observer's Core thread.
Keep chat, telemetry, policy and checkpoint lifecycle independent.

**Tech Stack:** Existing Python, SQLite, concurrent futures, Guardian/Security,
pytest, normal full launcher, Hub and Runtime Observatory; no new dependency.

**Spec:** [C2 observer continuity design](../specs/2026-11-24-phase-c2-observer-continuity-design.md).
Read it first. This is preparation only; no C2 implementation or acceptance is
claimed. C2b automatic selection/interval/retention is explicitly deferred.

## Global Constraints

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

## Review Focus

1. Malformed/future-schema data or clock rollback cannot partially restore state
   or manufacture trust observations (Task 1).
2. Read failure, duplicate handle and uncertain commit cannot become absence,
   overwrite prior rows or cause an automatic retry (Tasks 2 and 3).
3. Blocked audit/SQLite work and stop cancellation cannot block chat's loop,
   lose worker ownership or allow a late success (Tasks 2 and 3).
4. Disabled configuration, foreign registration and revoked policy cannot open
   the checkpoint store or resurrect observer health (Task 3).
5. Checkpoint data cannot reach normal chat evidence, and historical state cannot
   count as a fresh tick or browser/live-model acceptance (Task 4).

---

## Baseline and File Map

Start from C1 `b8719fa22b8bd21ea77b3c4aa721522e312e86ea` or its reviewed
descendant, on an isolated `codex/` branch. Reconcile any C1 review changes before
implementation. Record original/temporal workspace index, status and hashes.

New modules below are helpers inside existing components, not new services.
All signatures below are proposed, not APIs currently available on Memory.

| File | Responsibility |
| --- | --- |
| `Aetherra/consciousness/checkpoint.py` (new) | Versioned aggregate codec |
| `Aetherra/consciousness/self_trust.py` | Exact trust export/import and clock |
| `Aetherra/consciousness/core/consciousness_core.py` | Detached snapshot/apply boundary |
| `Aetherra/aetherra_core/memory/lifecycle_checkpoint.py` (new) | Owned exact I/O and receipt types |
| `Aetherra/aetherra_core/memory/memory_core.py` | Own checkpoint worker and teardown |
| `Aetherra/aetherra_core/memory/aetherra_memory_engine.py` | Delegate narrow checkpoint methods |
| `aetherra_os_launcher.py` | Concrete adapter, config, ownership and stop order |
| `Aetherra/consciousness/runtime_observer.py` | Restore-before-tick and stop-save lifecycle |
| `aetherra_hub/blueprints/consciousness.py` | Cached continuity projection |
| `Aetherra/runtime_ui/snapshot.py` | Bounded Observatory status |
| `tools/alpha_consciousness_smoke.py` | Same-entry restart and failure evidence |

### Task 1: Validated Aggregate State and Exact Trust

**Files:** Create `checkpoint.py`; modify SelfTrust and Core from the map.
Create `tests/unit/test_consciousness_checkpoint.py`; extend
`tests/unit/test_consciousness_observer_core.py`.

**Interfaces:**

- Define frozen `ObserverCheckpoint` and `TrustCheckpoint` value types in
  `checkpoint.py`, containing only the spec fields and immutable containers.
- `encode_checkpoint(state: ObserverCheckpoint) -> dict` and
  `decode_checkpoint(payload: dict) -> ObserverCheckpoint`.
  Serialized byte/depth/duplicate-key limits also apply at the Memory boundary.
- SelfTrust preserves `half_life_s=3600` and adds keyword-only
  `clock: Callable[[], float] = time.time`;
  `export_checkpoint() -> TrustCheckpoint` and
  `restore_checkpoint(state: TrustCheckpoint) -> None`.
- Core adds `export_observer_checkpoint(checkpoint_id: str) -> ObserverCheckpoint`
  and `restore_observer_checkpoint(state: ObserverCheckpoint) -> None`.
  These are called only by the owning observer worker, not HTTP handlers.

- [ ] Add round-trip tests with score 40, nonzero timestamps/history, negative
  valence and all six dimensions. Assert exact trust import, unchanged history,
  zero invented observations and zero restored runtime ticks. At one half-life,
  a subsequent ordinary read moves 40 toward 90 to 65; clock rollback causes no
  decay. Reject invalid bounds, booleans, NaN/Infinity, excess history, extra
  fields and future schema without changing any preexisting Core state.
- [ ] Run `python -m pytest tests/unit/test_consciousness_checkpoint.py -q`;
  expect failure for the absent checkpoint API.
- [ ] Implement the spec's 64 KiB, 64 subsystem and 64-history limits. Build all
  replacement state first, then swap on the owner thread. Preserve normal
  SelfTrust behavior and leave legacy file loading disabled in observer mode.
  Do not replay intents or modify the standalone persistence format.
- [ ] Run the new file plus
  `tests/unit/test_consciousness_observer_core.py` and `tests/capabilities/test_consciousness_phase3.py` and
  `tests/unit/test_health_checks_guardian.py`; expect all selected tests to pass.
- [ ] Review and commit only this task's codec/Core/trust changes and tests.

### Task 2: Exact Checkpoint I/O Owned by Existing Memory

**Files:** Create the mapped Memory helper; modify Core Memory and Advanced.
Create `tests/unit/test_memory_lifecycle_checkpoint.py`.

**Interfaces:**

- Define `LifecycleCheckpoint(record_id: str, checkpoint_id: str, payload: dict)`
  and `CheckpointError(code: str)`. Codes distinguish busy, denied, audit_failed,
  missing, ambiguous, invalid, unavailable, cancelled and uncertain outcomes.
- Define `CheckpointJobControl(cancelled: threading.Event, deadline: float,`
  `still_owned: Callable[[], bool])`. Deadline is monotonic, capped at one
  second or remaining stop budget. The predicate can refuse only; cancellation
  or expiry irreversibly closes result acceptance, including after audit starts.
- Core Memory and Advanced expose:
  `submit_load_lifecycle_checkpoint(*, owner: str, scope: str,
  checkpoint_id: str, control: CheckpointJobControl) -> Future[LifecycleCheckpoint]`;
  `submit_store_lifecycle_checkpoint(*, owner: str, scope: str,
  checkpoint_id: str, payload: dict, control: CheckpointJobControl)`
  `-> Future[LifecycleCheckpoint]`.
- The helper owns the connection and one outstanding slot. Submission returns
  promptly; completed error futures report rejected admission. Worker shutdown
  stops admission, retains outstanding ownership and reports whether it drained.
  Preserve existing Memory `close()` callers without closing a worker's active
  connection from another thread.

- [ ] Write real temporary-SQLite tests for exact immutable round trips and
  distinct handle/row IDs; ambiguous/missing/malformed rows; duplicate handles
  across two Memory instances; unsupported database forms; foreign owner/scope;
  denied and missing-audit operations before any checkpoint DB open.
  Pin no access-stat mutation on exact load and no broad recall fallback.
- [ ] Add synchronization-based tests for blocked audit, SQLite lock contention,
  admission while busy, caller payload mutation during blocked audit,
  pre-transaction cancellation and cancellation during commit. Assert one slot/worker, bounded return, no automatic retry, no false
  rollback claim and prior rows unchanged. Avoid timing-only sleep assertions.
- [ ] Run `python -m pytest tests/unit/test_memory_lifecycle_checkpoint.py -q`;
  expect failure for absent APIs.
- [ ] Implement the spec's existing-database-only connection and atomic
  check-and-insert, using the exact memory type and existing Guardian/Security
  interfaces. Enforce allowed plus audit receipt before database access.
  Freeze validated payload bytes before admission and recheck the frozen content
  before insert; return detached receipts. A running Future alone is not a
  cancellation token. No changes to generic chat retrieval, dependency locks
  or policy defaults.
- [ ] Rerun the new file and `tests/unit/test_memory_core_guardian.py`;
  expect all tests to pass and all worker connections to close.
- [ ] Review and commit only this task's Memory changes and tests.

### Task 3: Governed Restore and Orderly Stop Save

**Files:** Modify launcher, observer, Hub and Runtime UI from the map.
Create `tests/unit/test_consciousness_observer_continuity.py`; extend
`tests/unit/test_consciousness_observer_lifecycle.py`,
`tests/unit/test_hub_consciousness_observer.py` and
`tests/unit/test_runtime_ui_consciousness.py`.

**Interfaces:**

- Add the spec's `consciousness_continuity` config object. Concrete MemoryAdapter
  delegates Task 2 methods only to its exactly owned initialized implementation.
- Add optional checkpoint dependency/settings to ConsciousnessObserver with
  defaults preserving C1. Use Task 1 state and Task 2 futures directly from the
  owned observer worker; no shared SQLite connection or event loop per tick.
- Extend cached `get_runtime_status()` with the spec's continuity fields.
  Preserve `stop(*, timeout=2.0)` callers with a new keyword-only
  `save_checkpoint=False`. Only an explicit orderly launcher/harness stop
  passes true, once. Include persistence in that total budget; create a separate
  Task 2 control token so stopping reflection does not itself cancel an explicitly
  requested save. Failed startup/replacement/monitor cleanup keeps the default.

- [ ] Write tests for default-off/no-I/O, malformed config, null-handle fresh
  lineage, restore-before-first-tick and zero initial counters. Missing/corrupt
  restore must block ticks and all writes; a later stop must preserve old rows.
  Policy denial/revocation and foreign/replaced Memory must fail closed.
- [ ] Add tests for exactly one acknowledged save from the last fully completed
  tick on explicit orderly stop; ordinary stop without the new flag, startup
  cleanup, replacement, repeated stops, failed/incomplete ticks and emergency
  shutdown cannot save. Block audit/DB work while servicing an asyncio heartbeat
  and chat double; require bounded stop, retained ownership, truthful
  pending/uncertain state and no late apply/false success. Cache-only repeated
  GETs must cause no audit, read, write or trust decay.
- [ ] Run the new continuity file; expect failure for absent config/lifecycle.
- [ ] Implement staged restore and a latched failure state on the owner worker.
  At stop, hold policy/registration/Memory ownership until bounded save/drain
  completes. Do not overwrite checkpoint errors in a generic stopped-state
  finalizer. A shutdown that cannot drain must not claim clean success.
- [ ] Run all four affected lifecycle/Hub/UI files plus observer Core tests;
  expect passing allow/deny/failure cases with no action/QFAC/consolidation.
- [ ] Review and commit only this task's lifecycle, projection and tests.

### Task 4: Restart Evidence and Operator Contract

**Files:** Extend the mapped smoke helper and
`tests/acceptance/test_personal_continuity.py`; add
`tests/acceptance/test_consciousness_continuity.py`.
Update `docs/AETHERRA_CONSCIOUSNESS_SYSTEM.md`,
`docs/ACTIVE_SYSTEMS.md`, `docs/ALPHA_OPERATOR_RUNBOOK.md`,
`docs/ALPHA_READINESS_CHECKLIST.md` and
`docs/ALPHA_READINESS_DECISION.md`.
Add a dated compact receipt in `docs/evidence/`.

**Interfaces:**

- Extend existing smoke CLI with proposed `--continuity`, retaining C1 defaults.
  Use the same normal full-launch entry and trusted local harness; no new route.
- Capture checkpoint handle, committed row ID, restore row ID, audit references,
  source hashes, fresh counters, statuses, provider/fallback identity and exits.
  Do not put raw checkpoint/private content or signing keys in ordinary logs.

- [ ] Add failing three-process tests: A saves a nontrivial aggregate; B selects
  that exact handle with empty chat history; C uses a distinct database and
  cannot restore it. Check state before the first tick via the existing trusted
  harness, not by marking historical ticks as current success.
- [ ] Seed a valid checkpoint-only sentinel and competing personal facts. Exercise
  normal HTTP chat/retrieval/context assembly and assert the checkpoint row ID
  and sentinel never reach the responder. Verify correct personal recall,
  honest unknowns and no fallback after independent observer stop.
- [ ] Run the two affected acceptance files; expect missing C2 behavior to fail,
  then implement the smoke extension and rerun until both pass.
- [ ] Freeze implementation hashes. Run `python -m pytest -q`,
  `python tools/alpha_boot_validation.py`,
  `python -m Aetherra.integration_validation`, `python tools/python_quality.py` and
  `python tools/verify_docs_consistency.py`. Require exit zero, preserve
  generated-report baselines and distinguish expected skips from passes.
- [ ] Run the following proposed command after implementing its flag, with a
  new disposable output directory and the existing isolated environment:

  `python tools/alpha_consciousness_smoke.py --output C2_EVIDENCE --observe-seconds 215 --continuity`

  Require save/restart/profile evidence, verified signed audits, independent
  chat and clean exits. Repeat C1 default-off/deny checks unchanged.
- [ ] Verify Observatory browser status and intentional live-provider personal
  recall using the existing operator procedures. If unavailable, record the
  exact boundary as unverified; never count an offline responder as a model pass.
- [ ] Document exact final commands/config, receipt versus handle semantics,
  explicit restore selection, uncertainty/recovery and C2b remaining work.
  Record a scoped go/no-go with evidence; do not imply unattended readiness.
- [ ] Review and commit only this task's tests/helper/docs. Before any requested
  publication, compare protected workspaces and signing controls with baseline.

## Preparation Outcome

The four tasks cover codec, storage, lifecycle and observable evidence without
activating the legacy continuity file or consuming pending temporal work.
All tests and new flags above are planned, not executed or already supported.
C1 review/hosted CI and merge remain separate gates; the next implementation
step is Task 1, followed by the real Memory boundary in Task 2.
