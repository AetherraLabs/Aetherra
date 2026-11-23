# TemporalConsciousnessEngine contract and verification

Status: bounded experimental component, hardened on 2026-11-23. Aetherra remains
the persistent cognitive system; Lyrixa remains her user-facing persona.

## Scope and callers

Implementation: `Aetherra/consciousness/quantum/temporal_consciousness_system.py`.
Existing Phase 7.3 `QuantumMemoryTemporalIntegration` and
`MultidimensionalStateEngine` callers retain their no-argument initialization,
async methods, result keys and metrics. The global initializer accepts optional
configuration on its first call; trying to reconfigure an existing singleton
raises `RuntimeError`. Explicit instances are preferable for separate
profiles and tests.

This is a temporal analysis component. It is not the main Consciousness Core,
the normal chat Engine, or personal-continuity retrieval. The normal launcher
does not directly initialize it. This milestone does not activate it in chat,
change autonomous goals, or advance the pending supervised-alpha decision.

## Supported behavior

- `process_temporal_moment(state, timestamp=None)` owns a deep JSON snapshot and
  returns a unique opaque moment ID, including for simultaneous timestamps.
- Event times are normalized to aware UTC. Legacy naive timestamps mean local
  host time. Supply aware timestamps for portable callers. Backfill is supported;
  links only run from strictly earlier to later events. Future-dated records are
  excluded from current integration, pattern detection and forecast evidence.
- `predict_future_state(target_time, context)` accepts strictly future targets
  within the configured horizon (six hours by default). It uses up to five
  chronological observations from the previous two hours. Only observed numeric
  top-level fields are projected; booleans and categorical/nested values retain
  their supplied context. Linear changes are capped at half the larger of the
  current absolute value and one. Scores are finite, bounded heuristics; the
  uncertainty weights sum to one. They are not calibrated probabilities.
- `temporal_memory_integration(query_time, context)` combines up to ten recent
  positive-weight historical records within the temporal window. Numeric fields
  use a single weighted mean; nested objects recurse; other values come from the
  highest-weight source (current context wins ties). Every contributing record
  ID is reported, with the actual count. A valid empty history returns the input
  context and zero strength; operational failures raise instead.
- `detect_temporal_patterns(window)` reports coherence trends, large state
  transitions, and exact repeated state suffixes with at least three repetitions
  and two distinct states. Cycle periods range from 2 to 16 observations and are
  measured in observations, not elapsed time.
  Legacy `causal_sequence`, causal-chain and `quantum_probability` names remain
  for compatibility. These are correlation/similarity heuristics, with no claim
  of established causation, quantum effects or subjective consciousness.
- `validate_prediction_accuracy(id, actual_state)` records typed-state similarity.
  Revalidation replaces the retained prediction's score. An unknown ID raises
  `KeyError`; it does not report a zero score as if validation succeeded.

Inputs are JSON objects with string keys, JSON scalar/list/object values,
finite numbers between -1e12 and 1e12, nesting depth at most 12, at most 256
entries per container, and at most 32 KiB of UTF-8 JSON per state. Invalid data
raises `TemporalValidationError` without changing history. NaN, infinity,
non-JSON objects and cyclic structures are rejected.

Default capacities are 256 moments, 128 predictions and 512 links; each can be
configured from 1 to 4096. Moments evict by oldest event time, with insertion
order breaking ties. Predictions and links evict by insertion order. Eviction
removes dangling references. Backfill older than an already-full retained set is
rejected. Coherence and accuracy histories hold at most 100 and 50 scores;
counters remain cumulative. The 24-hour default temporal window bounds queries,
not durable storage lifetime. `current_temporal_state` is a compatibility label,
not an inferred psychological state.

Public dictionaries remain compatible inspection surfaces for trusted Python
callers. They are not a security boundary: mutate state through the async API.
An engine is confined to one event loop; cross-thread access is unsupported.

## Durable history through existing Memory

Use the existing file-backed `LyrixaMemorySystem`. Its default `:memory:` database
does not survive restart. The temporal engine neither owns nor closes Memory.
For example, from a repository checkout with runtime dependencies installed:

```python
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from Aetherra.consciousness.quantum.temporal_consciousness_system import (
    TemporalConsciousnessEngine,
)

async def save(profile):
    profile.mkdir(parents=True, exist_ok=True)
    memory = LyrixaMemorySystem(str(profile / "memory.db"))
    try:
        engine = TemporalConsciousnessEngine(memory_system=memory)
        await engine.process_temporal_moment(
            {"attention": 0.6, "activity": "reading"},
            datetime.now(timezone.utc),
        )
        handle = await engine.save_checkpoint()
        (profile / "temporal-checkpoint.txt").write_text(handle, encoding="utf-8")
    finally:
        memory.close()

asyncio.run(save(Path("local-temporal-profile")))
```

In a new process, construct Memory with that same database path and a new engine,
read the saved handle, then call `await engine.restore_checkpoint(handle)`.
The result includes `status`, `checkpoint_id`, `memory_id`, `moments_restored` and
`predictions_restored`. Restoration includes UTC timestamps, state, links,
predictions, validated accuracy, histories, counters and analysis settings.
Local capacity limits are not enlarged by a checkpoint; oversized histories fail.

Each save writes an immutable schema-1 record through `store_memory`, with exact
`memory_type="temporal_checkpoint:" + handle`. A nonblank Memory receipt is
required before returning the handle. Restore uses `recall_memories` with that
exact type and a limit of two, requires exactly one matching record, checks the
embedded handle/schema, all record bounds and references, then commits the fully
validated candidate. It never searches arbitrary conversation text for a handle.
Snapshots larger than 16 MiB are rejected before writing/restoring.

Checkpoint saving is explicit, not automatic after every moment or on shutdown.
The caller must retain the handle and choose when to save. History accepted since
the last completed save is not durable. There is no automatic latest-checkpoint
discovery. The database and handle are private local data, not credentials or
account authorization. Separate database paths provide **storage isolation**;
there is no new account-isolation claim.

Memory owns checkpoint retention. Its existing consolidation/deletion operations
can remove checkpoints; retain required backups and handles. To undo replacement
of a live history, save its checkpoint first and restore that handle. To remove an
unwanted checkpoint, retrieve its exact type and use the returned row ID with
Memory's existing guarded `delete_memory(id)` operation. Do not delete by a broad
text match. No automatic database cleanup or private-key handling is introduced.

## Failure, concurrency and Guardian behavior

Guardian authorization runs before temporal mutation or checkpoint Memory access.
Existing internal principal `consciousness:temporal` keeps its existing scoped
capabilities. External principals must satisfy the existing policy. New audited
actions are `consciousness.temporal_detect_patterns` (memory read),
`consciousness.temporal_save_checkpoint` (consciousness write and memory write),
and `consciousness.temporal_restore_checkpoint` (consciousness write, memory read
and memory write). Restore needs write because Memory updates access statistics.
No Guardian, Security, signing or release policy is relaxed.

Unexpected engine failures raise a generic `temporal_operation_failed` error;
ordinary engine logs contain operation names, not supplied state or exception
payloads. Existing audit metadata retains field names, counts and hashes rather
than raw state values; callers must use non-sensitive schema keys. Checkpoint
handles are hashed in audit metadata. Memory retains its existing diagnostics.

Store failures and blank receipts raise `TemporalPersistenceError`. Existing
Memory returns an empty list for both missing records and some read failures, so
restore explicitly reports `temporal_checkpoint_missing_unreadable_or_ambiguous`;
it does not pretend to distinguish those cases. Corrupt checkpoints fail closed
without partially replacing history. `PermissionError` and cancellation propagate.

Restore checks the engine revision after the awaited Memory read. A concurrently
accepted moment, forecast or validation causes `TemporalConflictError`, preserving
the newer work. No automatic retry discards it. Save snapshots the state at call
time; turns accepted while a write awaits belong to a later checkpoint. Cancellation
after a durable write may leave an unacknowledged row. Neither cancellation nor
restore rolls back Memory access statistics. Rollback is explicit, not a claim of
distributed transactionality.

## Verification

Run from the repository root in the project environment (offline; no model needed):

```powershell
$env:AETHERRA_SKIP_DOTENV = '1'
$env:AETHERRA_SIGNING_STRICT = '1'
$env:AETHERRA_SCRIPT_VERIFY_STRICT = '1'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
python -m pytest -q -o addopts= `
  tests/unit/test_temporal_consciousness_functional.py `
  tests/integration/test_temporal_memory_restart.py `
  tests/unit/test_temporal_consciousness_guardian.py `
  tests/unit/test_memory_temporal_integration_guardian.py `
  tests/unit/test_multidimensional_state_guardian.py `
  tests/unit/test_phase74_integration_guardian.py
```

The restart test uses separate interpreter processes, real SQLite Memory and
enforcing Guardian, with no store, retrieval or model doubles. It compares the
checkpoint digest, opaque IDs, timestamps, predictions, links and counters after
restart; integrates restored evidence; continues processing; rejects a missing
checkpoint from a separate database; and rejects an unreadable real database.
Unit doubles additionally exercise failure/cancellation paths.

Baseline: the existing 16 Guardian/integration tests passed. Thirty new behavioral
cases failed before the implementation: second-resolution ID collisions, aliased
state, reversed chronological trends, invalid horizons, swallowed failures,
inaccurate contributor counts, unbounded histories, missing cycle detection and
absent checkpoint operations. Verification results and a synthetic opaque-ID trace
are recorded in [the hardening evidence](evidence/temporal_hardening_2026-11-23.json).

Final result: **149 passed, one skipped** (Windows symlink support), including 59
new temporal cases, adjacent Guardian/integration tests and release/script/plugin
signing tests. The fixed Python quality baseline reports zero new or edited
violations. The source-snapshot docs consistency check and new-guide Markdown
check pass; the overview's 43 pre-existing Markdown findings remain unchanged.
All 58 protected pending-work/signing/configuration files and the Git index match
the pre-edit snapshot. Code review findings have regression coverage and no
implementation blockers remain for this bounded component contract.

This verifies the supported temporal component contract. Live-model/browser
alpha verification and automatic normal-launch lifecycle wiring are separate work;
they are not implied by these deterministic tests.
