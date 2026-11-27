# Temporal source projection implementation plan

> Historical implementation record: delivery restrictions and pending-work statements below describe this slice when it was executed. The source, Memory foundation and runtime integration are now combined in the Temporal milestone; current operation and verification limits are documented in [Temporal history](../../TEMPORAL_HISTORY.md).

> **For agentic workers:** Use superpowers:executing-plans for the independent
> source slice; use a fresh whole-change review before delivery.

**Goal:** Expose safe completed-tick numeric evidence for the approved opt-in
Temporal integration without coupling Core progress to a Temporal consumer.

**Architecture:** The existing Core owner captures a small scalar snapshot after
a fully accepted tick. An opt-in read method returns a detached fresh snapshot.
No callback, Temporal worker, persistence or launcher activation is introduced.

**Tech stack:** Existing Python/threading Core, pytest and strict-policy fixtures.

**Spec:** [Resumption contract](../specs/2026-11-26-temporal-runtime-resumption-design.md).

## Global constraints

- Default disabled; require a real boolean to opt in.
- Preserve current callers, C2b authority/schema/receipts, Guardian/Security and signing.
- Only three numeric counts and source time/identity metadata; no private text.
- Existing pending Temporal and alpha changes remain untouched.
- This slice is not completion of the runtime observer or durable-history milestone.

## Review focus

- An in-flight tick is interrupted after producing a UI snapshot.
- Local readiness disappears before acceptance.
- A wall-clock rollback cannot make stale data look fresh.
- A consumer mutates a returned mapping.
- Disabled capture never creates a Temporal engine, worker or storage write.

## Task 1: Completed numeric source projection

**Files:**
- Modify: `Aetherra/consciousness/runtime_observer.py`.
- Test: `tests/unit/test_consciousness_observer_lifecycle.py`.

**Interfaces:**
- Consumes the owner thread's accepted `ConsciousnessCore` tick.
- Adds optional constructor argument `temporal_observation_enabled: bool = False`.
- Produces `get_temporal_observation() -> dict[str, Any] | None` with the exact
  eight fields specified in the contract. Counts use Core working_memory,
  active_intents and last completed focuses; never scrape narrative/UI strings.

- [x] Reproduce absent API/opt-in and interrupted-tick requirements: five failures.
- [x] Implement capture after tick acceptance and a detached cached getter.
- [x] Reproduce monotonic freshness and nonboolean-configuration requirements:
      four failures.
- [x] Complete focused lifecycle/Core/continuity/Hub regression run.
- [x] Run configured suite and relevant Python quality/docs/signing checks.
- [x] Obtain fresh review: readiness invalidation during checkpoint export,
      delayed clock capture and explicit local-owner refusal were reproduced.
      Four corrected-fixture failures became passing regressions; 164 adjacent
      tests passed after repairs.
- [x] Record source-bound evidence and exact protected-work comparison.

Verification:
```powershell
python -m pytest -q -o addopts= `
  tests/unit/test_consciousness_observer_lifecycle.py `
  tests/unit/test_consciousness_observer_core.py `
  tests/unit/test_consciousness_observer_continuity.py `
  tests/unit/test_hub_consciousness_observer.py
```

This command
must exit zero. The configured suite uses `python -m pytest -q`, retaining the
22% coverage floor. The task-specific external runner isolates credentials,
dotenv, cache and temporary paths and stores complete outputs.

## Dependent next slices

These are sequencing constraints, not executable tasks with undefined APIs:

1. History density accepted: sampled changes plus session/gap markers, without automatic deletion.
2. Completed locally: reviewed and implemented Memory-owned typed append/read,
   ordering, ownership, uncertainty and retention interfaces. See the
   [Memory slice evidence](../../evidence/temporal_memory_history_2026-11-26.json).
3. Integrate the existing Temporal engine on its optional worker with bounded
   admission, restoration and flush; prove blocked-consumer isolation.
4. Wire normal launcher and cached Observatory status; run real process restart,
   separate-profile, browser, privacy and authority acceptance checks.

The original 2026-11-23 plan remains preserved as historical prototype evidence.
Do not mark its checks as current-main verification or apply its broad replacement
API. No automatic commit, push, merge or release is part of this source slice.

## Completed local evidence

The baseline passed 265 selected tests. The repaired adjacent suite passed 164;
the complete configured suite passed 4,171 with 38 documented skips, exit zero,
and 45.29% coverage against the unchanged 22% floor. All 13 new cases passed again
after a comment-only import-formatting correction. The fixed Python quality
baseline and docs consistency checks passed. Existing signing controls and all
28 pending Temporal/alpha files, including their three worktree indexes, remained
unchanged. See [the source-bound receipt](../../evidence/temporal_resumption_2026-11-26.json).

The source slice is complete locally. It is not committed or published.
The durable-history choice is accepted. The dependent Memory slice is also implemented and verified locally; see [its plan](2026-11-26-temporal-memory-history.md). Runtime integration remains pending.
