# Temporal runtime resumption after C2b

> Historical implementation record: delivery restrictions and pending-work statements below describe this slice when it was executed. The source, Memory foundation and runtime integration are now combined in the Temporal milestone; current operation and verification limits are documented in [Temporal history](../../TEMPORAL_HISTORY.md).

Status: integration contract draft, 2026-11-26. The user previously approved an
opt-in runtime observer using existing Memory, and resumed that work after C2b.
This document reconciles the preserved 2026-11-23 prototype with current main
`56623003675bc99f9e3dfadf15b6254beb183b59`; it does not declare a completed
runtime integration. The user accepted the history-density recommendation below.

## Current scope and first deliverable

Aetherra remains the persistent cognitive system; Lyrixa is its persona.
Observe completed numeric Core state without changing answers or action authority.
The first independently testable deliverable, now verified locally, is an opt-in cached numeric source
projection from the owned `ConsciousnessObserver`. It is disabled by default,
is not enabled by the launcher yet, and creates no Temporal engine, worker,
Memory record, policy grant, or HTTP endpoint.

`get_temporal_observation() -> dict | None` returns a detached scalar mapping:
`session_id`, `session_started_at_unix_s`, `sequence`,
`observed_at_unix_s`, `observed_uptime_s`, `working_memory_count`,
`active_intention_count`, `focus_count`. The producer is the Core owner thread,
after successful tick completion and existing stop/readiness checks. Timestamps
are captured there, not invented by a later poller. Repeated reads are the same
source observation, identified by session and sequence.

Only `temporal_observation_enabled=True` enables capture; non-booleans are
invalid. Disabled, unstarted, stopped, failed, blocked or stale sources return
None. Freshness uses monotonic elapsed time, with the existing observer tolerance
`max(3 * tick_interval, 3)` seconds. A backwards wall clock does not fabricate
freshness or offline experience. The reader copies only eight scalars under the
existing short lock; it invokes no callbacks, policy, engine or storage work.
It is an internal source interface, not authorization to use its data: the
eventual consumer must recheck its own policy and ownership.

## Source trace and prototype disposition

| Responsibility | Current source | Reconciliation |
| --- | --- | --- |
| Normal startup | `aetherra_os_launcher.py::_start_consciousness_observer` | Extend the owned post-activation path; do not revive legacy Core startup |
| Completed tick | `Aetherra/consciousness/runtime_observer.py::ConsciousnessObserver._run` | Publish numeric projection only after tick acceptance |
| Temporal analysis | `Aetherra/consciousness/quantum/temporal_consciousness_system.py` | Reuse existing engine and bounded working set; preserve standalone callers |
| Memory ownership | `MemoryAdapter._checkpoint_backend` and existing advanced/core Memory | Preserve exact instance checks; no independent memory service or database |
| C2b streams | `memory/checkpoint_stream.py` and `memory/lifecycle_checkpoint.py` | Core-specific owner/scope/schema stay closed to Temporal payloads |
| Observatory | `Aetherra/runtime_ui/snapshot.py`, owned Hub state, `SubsystemEvidence.tsx` | Add sanitized cached status through these existing surfaces |

The old prototype's numeric schema and failure tests are useful source material.
Its generic `store_memory(replace_type=True)`, shared SQLite connection access,
global ThinkStream callback and profile-local Core continuity JSON do not fit
current main. Do not port them. Its direct-method restart harness is component
evidence, not a full-launch verification.

## Durable-history decision

The user accepted retaining changes observed at five-second sampling points in the three numeric counts plus session/gap markers, with no automatic deletion. The next focused slice is [governed typed Memory history](2026-11-26-temporal-memory-history.md); runtime sampling and engine restoration remain separate dependent work.

The engine's bounded moment window is an analysis cache, not long-term history.
C2b recovery checkpoint retention (default ten) must never prune Temporal history.
If a separate recovery snapshot is later needed to speed replay, it is derivative
of authoritative Memory history and must not become a second persistence authority.
No forecasts, causal conclusions, experiences while offline, conversation text,
intention descriptions or focus labels belong in this numeric-history milestone.

## Required integration boundaries

These are constraints for the next implementation slices, not delivered behavior:

1. A separate optional Temporal worker polls the bounded completed-tick projection
   and owns the existing engine. Sample at most once per five monotonic seconds,
   deduplicate session/sequence, and report skipped source sequences accurately.
   Temporal work must not occupy chat/Core execution or C2b's job slot and local
   receipt/deadline processing. Shared SQLite or signed-audit failure can prevent
   checkpoint acknowledgement; report failure/uncertainty without extending C2b's
   budgets. Prove both independent-lane progress and truthful shared-failure behavior.
2. Memory owns governed Temporal I/O in the same profile database, using its own
   serialized connection/lane rather than concurrent use of raw core_memory.conn.
   Do not occupy C2b's single outstanding job slot. Define the exact typed history
   and selection/restore interface before adding methods; no generic replacement
   or deletion primitive and no generalization of C2b's accepted payloads.
3. Restore exact validated durable evidence before admitting new observations.
   Distinguish explicitly created empty history from missing, corrupt, ambiguous,
   denied or unavailable storage. Do not select by wall-clock timestamp alone.
   Do not silently replace a failed restore with an empty history.
4. Define single-writer ownership, atomic ordered append, exact receipt identity,
   duplicate-attempt inspection and uncertain-commit recovery in Memory. Old writers
   must not commit after takeover. Lost ownership is visible and never automatically
   reacquired. A timeout is not proof of rollback; keep outstanding work owned.
5. Require the existing strict Guardian/Security policy and signed-audit controls.
   Recheck containment and local ownership before durable effects and accepting
   receipts. The standalone engine's internal capability shortcut is not sufficient
   runtime authorization. Failed policy/audit access fails closed for Temporal.
6. Keep source session, sequence, UTC observation time, monotonic uptime, capture
   time and last verified observation. Label cross-session elapsed wall time as an
   estimate and clock rollback as inconsistent. True time offline remains unknown
   without adequate shutdown/start evidence; do not fill gaps with synthetic moments.
7. On shutdown close observation admission immediately. C2b retains its existing
   deadline and priority. Temporal flush/drain is independently bounded; outstanding
   work remains owned and visible through cleanup. Missing acknowledgements never
   become a healthy/stopped persistence claim.
8. Expose bounded cached status: source freshness, accepted/skipped observations,
   last saved/restored record identifiers, persistence and ownership states, error
   codes and gap interpretation. HTTP reads must not run engine, Guardian or I/O.
   Disabled remains the default. Actual launcher settings and operator commands
   are added only with implemented validated integration.

## Acceptance evidence

- Real completed Core ticks; disabled capture; failed/interrupted/unowned ticks;
  stale data, clock rollback and caller mutation cannot alter the cached source.
- Block Temporal execution/I/O while chat, Core and C2b progress; unchanged stop budget.
- Real Memory in two separate processes: same opaque committed observation ID
  selected after restart and applied to the existing engine before new observations.
- Separate local profile exclusion; no account-isolation claim.
- Policy denial, missing capabilities/audit, late containment, service replacement,
  uncertain writes and takeover cannot fabricate durability or overwrite history.
- C2b pruning leaves Temporal records intact, and Temporal cannot change Core heads.
- Sentinel private text absent from new records, status, logs and normal chat context.
- Exact normal-launch commands, source revision, intervals and stop/restart evidence;
  browser verification of added Observatory status. Numeric observation needs no model;
  no deterministic test is labeled a live-model pass.
- Existing Temporal, Core, Memory, Hub and signing regressions plus configured suite
  and relevant quality/docs checks, with skips and remaining issues reported.

## Roadmap and retained limitations

C2b and #368 are merged. This is the next separate integration in Stage 21,
supervised internal alpha, not Temporal reasoning/evolution or Phase D agency.
The original prototype and eleven unpublished alpha draft files remain untouched.

ALPHA-CKPT-001 and DEV-CKPT-001 remain OPEN: the original runtime delay and extended
causal chain are unexplained. DEV-AUDIT-001 and DEV-OBS-001 also retain their
recorded limits. The pre-existing Homeostasis watchdog shutdown error remains
a real lifecycle defect; process exit alone does not prove all work settled.
No new unattended/production GO or fresh-install/live-model/physical-check pass
is inferred from this resumption. Signing enforcement is unchanged.
