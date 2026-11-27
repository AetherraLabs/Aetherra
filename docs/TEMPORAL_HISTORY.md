# Temporal history and runtime observer

The optional Temporal observer reads numeric evidence from the most recently
completed Core tick. It uses the existing profile Memory database and publishes
cached status through the Consciousness inspector.

## Retention and meaning

The accepted policy is to retain changes observed at five-second sampling points
plus session/gap markers, with no automatic deletion. The observer samples on a five-second monotonic cadence; Memory rejects unchanged ordinary observations and validates boundaries.
The Temporal engine's bounded analysis window is separate from this durable archive.
C2b recovery checkpoint retention cannot delete these records.

Records contain only opaque IDs, numeric counts and source/capture clocks. They
do not contain chat text, intention descriptions or focus labels. Ordering follows
Memory's committed ordinal, even when the wall clock moves backwards.

A restart gap denotes a resumed Temporal writer. It does not establish how long
the computer was offline. A session-end marker closes the collector and anchors
to its exact last durable source; it does not prove the OS exited. Markers are
evidence about observation boundaries, not invented experiences.

## Memory interface

Core Memory, advanced Memory and the normal launcher's MemoryAdapter expose:

- submit_acquire_temporal_history: explicit create or resume; resume fences the
  previous writer and fails on missing/corrupt history.
- submit_append_temporal_history: atomically append a bounded batch against the
  exact expected head, returning record IDs, digests and signed-audit reference.
- submit_read_temporal_history: validate a page of at most 64 records within an
  exact selected head.
- submit_inspect_temporal_append: resolve an original request under a newer fenced
  epoch; a missing receipt alone is not evidence of rollback.
- temporal_history_pending and drain_temporal_history: report and retain work
  until it actually settles.

These methods use frozen types from
[Aetherra/aetherra_core/memory/temporal_history.py](../Aetherra/aetherra_core/memory/temporal_history.py)
and the existing local-only StreamJob polling protocol. Before applying selected
evidence, a consumer explicitly rechecks authority through check_restore_policy;
polling itself never performs policy or storage I/O.

The dedicated lazy worker uses a separate connection and slot in the same Memory
database. SQLite still has one writer. Short transactions keep external policy
and audit I/O outside its write lock. The signed audit ledger also shares a lock;
shared storage or authority failure can still prevent
either lane from saving. Timeout does not prove rollback. Core close retains its
existing one-second total drain budget and prioritizes C2b. The legacy
close_connection entry point uses the same drain. Engine shutdown awaits real
Core cleanup off the asyncio loop, retaining the original attempt through
cancellation and retry; legacy thread-affine closers keep their original behavior.

No production policy grants are added by this slice. Strict Guardian, Security,
filesystem capabilities and signed audit remain required. The pretransaction
authority check is the permit boundary; revocation racing SQL may leave a committed
but unacknowledged result, reported as uncertain and recovered by exact inspection
after explicit fencing. No automatic ownership reacquisition occurs.

Concurrent processes share Guardian's existing OS lock around signed-audit key
selection, tail validation and append. The signing format and release controls
are unchanged. Read-only verification does not create directories or sidecars;
exports without a sidecar validate captured signed bytes and fail on incomplete
data. A blocked lock remains a reported failure, never unsigned success.

Isolation is by distinct local Memory data directories. This is storage isolation,
not an account/user authorization system. Acquisition checks the selected head
batch; restoring a page validates that page and its boundaries, not the entire
indefinitely retained archive.

## Reproducible checks

From the repository root, using the supported Python environment:

```powershell
python -m pytest -q -o addopts= `
  tests/unit/test_temporal_history_store.py `
  tests/unit/test_memory_temporal_history.py `
  tests/unit/test_temporal_history_c2b_isolation.py `
  tests/integration/test_temporal_history_restart.py
```

The restart test creates isolated synthetic profiles, runs separate interpreter
processes through real Memory, compares exact record IDs/digests, checks signed
audit integrity and verifies absence in a separate profile. Its temporary
history-restart-trace.json is inspectable evidence. It does not claim restoration
into the Temporal engine or normal-launch/browser verification.

Run the configured repository suite with `python -m pytest -q`; keep the existing
coverage floor and signing checks. The
[contract](superpowers/specs/2026-11-26-temporal-memory-history.md)
defines corruption, ownership, uncertainty and shutdown invariants.

## Memory foundation verification on 2026-11-26

The configured full suite passed **4,239 tests with 38 skips** and
**45.29% coverage**, against the unchanged 22% floor. The final focused
Guardian, Security, Memory, C2b isolation, restart and engine checks passed
215 tests. The fixed Python quality baseline passed with zero new or edited
violations. These overlapping runs are not additive.

The [verification receipt](evidence/temporal_memory_history_2026-11-26.json)
binds the base revision and reviewed source hashes, commands, skip reasons and
synthetic process traces. Record `55555555555555555555555555555555` at ordinal 3
retained its exact digest across a process restart from writer epoch 1 to 2.
The receipt also links its append to the signed audit and records absence in a
separate profile. Its consumer is the typed Memory page, not the Temporal engine.

At this foundation verification checkpoint, the work was local and uncommitted.
Hosted CI, normal-launch Temporal sampling, engine restoration, Observatory/browser
checks and live-model checks had not been performed for that slice. Runtime
verification is recorded below; existing alpha incident and readiness limits
remain unchanged.

## Run the observer

Supply an existing full-launch profile with an enabled observe-only Core and
strict Guardian, capability and signing configuration. A minimal launcher
configuration for a new history is:

```json
{
  "consciousness_enabled": true,
  "consciousness_mode": "observe",
  "consciousness_tick_hz": 1,
  "temporal_observer": {
    "enabled": true,
    "history_id": "e9c59d354ae34525b43b6248f832be2d",
    "start_mode": "create"
  }
}
```

Choose a fresh 32-character lowercase hexadecimal history ID for each history.
In the profile's normal runtime environment, run
`python path/to/aetherra_os_launcher.py --mode full --no-gui --config path/to/launcher.json`.
For a new process on the same profile, retain the database and history ID and
change `start_mode` to `resume`. Missing history blocks collection. Omit
`temporal_observer` or use `{"enabled": false}` to disable it.

The disposable acceptance profile grants `consciousness:core` the Guardian
actions `consciousness.temporal_history_acquire`, `consciousness.temporal_history_append`,
`consciousness.temporal_history_read` and `consciousness.temporal_history_inspect`
for subsystem `consciousness` and target `memory:core`. Its capability policy
allows `consciousness:write`, `memory:read`, `memory:write`, `fs:read` and
`fs:write`. The independent C2b stream uses its existing acquire, advance,
inspect and prune actions. Irreversible pruning requires one exact Guardian
approval through [supervised checkpoint retention](CHECKPOINT_RETENTION.md).

From the source checkout, run the normal-launch acceptance helper with
`python tools/alpha_temporal_smoke.py --output path/to/new-disposable-directory`,
or run `python -m pytest tests/acceptance/test_temporal_runtime_launch.py`.
The helper creates synthetic profiles, uses loopback-only launcher workers,
and supplies a deterministic generation provider. It shuts down each process
through a harness interrupt and checks the original owners. A browser session
can use `--browser-hold-seconds 300` with port 3001 free. In each phase
directory, wait for `browser-ready.json`, inspect Consciousness in Observatory,
then create an empty `browser-release` file. The isolated profile shows missing
history. After its process exits, the still-open inspector can show loss of
transport. Browser observation is recorded separately from CLI acceptance.

The strict normal-launch check restored four observation IDs into the real
engine before its first sample. The supervised C2b prune advanced its watermark
from zero to one while all six Temporal envelopes retained their original bytes.
A fresh profile using the same history ID reported missing history and created
no Temporal tables. All three launcher processes exited with their original
Core, Temporal and Memory work settled.

The [runtime receipt](evidence/temporal_runtime_integration_2026-11-26.json)
records local verification. Existing alpha incidents and the previously
observed Homeostasis watchdog shutdown exception remain open.

## Final local runtime verification

Local final-source verification recorded 4,319 passed, 38 skipped and 45.29% coverage against the unchanged 22% floor. The configured command was `python -m pytest -q`. It included
the normal-launch acceptance test using the final frozen code. The earlier full
run recorded 4,308 passes, 38 skips and ten Git fixture setup errors. The
supervised retention harness now isolates its environment in a child process. A second
run stopped at 23% after an independent secret scan flagged a synthetic test
fixture. The third run used the corrected fixture and unchanged scanner. The runtime receipt
contains the exact interpreter command, skip reasons and source hashes.

In the live Consciousness inspector, creation showed Running and Saved at epoch 1.
Restart showed epoch 2 and the restored head. An isolated profile showed Missing
and cleared prior IDs. Closing the Hub cleared live values in the same tab. The
browser ran before the final five-file runtime fix, the harness isolation repair and the synthetic scanner-fixture correction. Its renderer hash matches the final
source. The browser harness command was
`python tools/alpha_temporal_smoke.py --output <new-directory> --browser-hold-seconds 600`.
All three owned launchers exited zero. The verification tab and owned development
server were closed. The synthetic generation and harness interrupt qualify local
numeric observation only. Existing incidents and supervised-alpha scope continue.

## PR verification boundary

The three verification receipts preserve their pre-publication snapshots. The
[delivery mapping](evidence/temporal_observer_delivery_2026-11-26.json) records reversible
CRLF-to-LF normalization for six new files, including one historical JSON receipt;
all 34 verified runtime/test files retain identical canonical content. The existing
CI Quality Gates offline-continuity step now also selects
`tests/acceptance/test_temporal_runtime_launch.py`; its production signing steps,
permissions and requirements remain unchanged. Current hosted results belong to the
PR checks and do not retroactively change the earlier local or browser evidence.
