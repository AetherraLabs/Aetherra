# Temporal Runtime Integration Implementation Plan

> Historical implementation record: delivery restrictions and pending-work statements below describe this slice when it was executed. The source, Memory foundation and runtime integration are now combined in the Temporal milestone; current operation and verification limits are documented in [Temporal history](../../TEMPORAL_HISTORY.md).

> **For agentic workers:** Use superpowers:subagent-driven-development. Keep changes uncommitted; review the delta against the archived Memory foundation.

**Goal:** Connect the opt-in Temporal collector to real Core, Memory, engine and Observatory without changing action authority or chat.

**Architecture:** One optional daemon owns the existing engine and sampled source. Existing typed Memory history is authoritative; engine and HTTP snapshots are bounded derived views.

**Tech Stack:** Existing Python/threading/asyncio, SQLite Memory/Guardian/Security, pytest, React/Vite.

**Spec:** [runtime design](../specs/2026-11-26-temporal-runtime-integration-design.md), constrained by the existing resumption and Memory contracts.

## Global Constraints

- Default disabled; fixed five-second monotonic sampling; no automatic deletion.
- Replay at most 256 records, in pages of at most 64; per-Memory-attempt bound one second.
- Existing Core stop budget remains two seconds; Temporal has a separate one-second stop budget after Core.
- No generic replacement checkpoint, independent persistence authority, private text, forecasts or autonomous actions.
- Preserve exact original Memory ownership through pending work, strict Guardian/Security and signing.
- Do not commit, push, publish or alter protected worktrees.

## Review Focus

- A clock rollback must not reorder/evict newer committed observations.
- An unchanged source must not conceal a writer takeover indefinitely.
- A delayed engine or policy callback must not publish state after stop/ownership loss.
- A short/empty/marker-ending history must restore exactly, never fabricate an observation.
- Repeated shutdown and service replacement must retain original outstanding Memory work.

### Task 1: Exact engine import

**Files:** Modify `Aetherra/consciousness/quantum/temporal_consciousness_system.py`; create `tests/unit/test_temporal_history_engine.py`.

**Interfaces:** Produce synchronous `import_history_window(records: tuple, *, history_id: str, selected_head: HistoryHead, authorize: Callable[[], None], publication_guard=None) -> dict` and detached `get_history_status() -> dict` on TemporalConsciousnessEngine. Input/output semantics are specified in the design; consumer uses this for both restart and live receipts. Status keys: history_id, head_ordinal, head_record_id, head_digest, retained_records, retained_observations, partial_window, last_observation_record_id. Metadata access for tests may use a detached bounded `history_provenance` property. Import returns that same status shape. Use existing revision checks; never legacy heuristic processing. Validate/build and authorize outside the optional local-only publication guard; acquire it only around final revision check and assignment. The guard defaults to nullcontext for standalone component tests. Runtime supplies a gate that excludes publication after cancellation/deadline, without implying atomic cross-process epoch ownership.

- [x] Write failing tests for exact IDs/ordinal order including rollback, markers excluded, raw clocks retained, bounded suffix, empty history, invalid/inconsistent/oversized inputs, late authority denial, blocked authorization followed by closed publication gate, and reentrant conflict; preserve standalone tests.
- [x] Run red tests with task runner and unique labels.
- [x] Implement minimal atomic import and prevent mixing runtime imported state with standalone mutating/checkpoint APIs.
- [x] Run new + existing Temporal functional/Guardian/restart tests and task review.

### Task 2: Governed collector lifecycle

**Files:** Create `Aetherra/consciousness/temporal_observer.py`, `tests/unit/test_temporal_runtime_observer.py`, `tests/integration/test_temporal_runtime_restart.py`.

**Consumes:** Task1 engine import; source `get_temporal_observation`; existing submit_acquire/append/read_temporal_history and StreamJob/control.
**Produces:** `temporal_settings(config: dict) -> dict|None`; `TemporalObserver(source, memory, *, settings, local_owned, readiness, engine_factory=None)`; `start()`, `block(code)`, `close_observation_admission()`, async `stop(*, save_history=False, deadline=None)`, cached `get_runtime_status()`/`get_status()` (same shape). `source` is the exact Core observer; callbacks run only on the collector/Memory workers. State includes runtime_state, enabled, thread_alive, source_fresh, accepted_observations, skipped_observations, selected_head_record_id, restored_record_id, saved_record_id, writer_epoch, ownership_state, persistence_state, outstanding, last_error_code, last_verified_observation_at_unix_s, observation_gap_seconds/state, offline_duration_state='unknown'.

- [x] Write red tests for disabled/invalid config, strict failure, restore-before-admission, five-second dedup/change sampling, same-source resume duplicate suppression, pre-append timestamp validation, source gap/change/rollback, unchanged ownership probes, blocked late import, fences, uncertain/pending ownership, no end marker before current-epoch observation, and repeated bounded stop.
- [x] Implement worker/state machine with bounded cached snapshots, real Memory admission and exact receipt application; no silent fallback or automatic reacquisition.
- [x] Real-process tests use actual Memory, strict policy/signed audit and real engine; assert exact durable ID in engine after restart before new observations and absence in another profile.
- [x] Verify focused tests and review before launcher consumption.

### Task 3: Normal launcher and Observatory

**Files:** Modify `aetherra_os_launcher.py`, `Aetherra/runtime_ui/snapshot.py`, `aetherra_hub/services/state.py`, existing Hub Consciousness blueprint, `Aetherra/lyrixa/gui/src/SubsystemEvidence.tsx`, and corresponding lifecycle/Hub/runtime-ui/GUI tests.

**Consumes:** Task2 interfaces. Register `temporal_observer` only after exact-owned Core/Memory activation, preserving foreign services. Expose only allowlisted cached scalar fields through existing Consciousness evidence.

- [x] Add red tests for opt-in/default-disabled, Temporal-only config failure, exact ownership and foreign service replacement, all three shutdown paths plus direct Core monitor stops, retained original instance on exceptions/replacement, suppressed marker on unsuccessful Core drain and unchanged Core budget.
- [x] Wire startup, monitoring and cached status; close Temporal admission before Core stop, then independently stop/drain Temporal preserving original pending work.
- [x] Add HTTP/UI tests for valid cached evidence, malformed/private-field exclusion, uncertain/fenced/blocked distinctions and stale transport clearing.
- [x] Run targeted lifecycle/Hub/UI tests plus GUI build/lint and task review.

### Task 4: Acceptance and evidence

**Files:** Add `tools/alpha_temporal_smoke.py` beside existing alpha smoke and `tests/acceptance/test_temporal_runtime_launch.py`; update `docs/TEMPORAL_HISTORY.md`, runtime specs/plans, ACTIVE_SYSTEMS/BUILD_ORDER/MASTER_ROADMAP, separate source-bound receipt under docs/evidence.

- [x] Run normal launcher with isolated strict synthetic profiles; demonstrate save, new-process restore into real engine, separate-profile exclusion and shutdown without altering existing incidents.
- [x] Verify existing Consciousness inspector in browser while live, restarted and unavailable; no live-model claim.
- [x] Fresh whole-change review/fix wave; run full configured suite and unchanged style/docs checks on final code.
- [x] Archive exact generated test artifacts, check links/diff and compare all protected worktree bytes/indexes/HEADs. Record results, skips and unverified boundaries honestly.

The [runtime receipt](../../evidence/temporal_runtime_integration_2026-11-26.json) tracks local acceptance, browser and final verification independently.

Local final-source verification recorded 4,319 passed, 38 skipped and 45.29% coverage against the unchanged 22% floor. The review and fix review were approved. Final quality, documentation, artifact and protected-worktree checks passed. The work is locally verified. The subsequent delivery request authorizes committing and pushing this milestone and opening a focused PR; merge remains a separate decision.
