# Phase C1: Governed Consciousness Observer

**Goal:** Start the existing ConsciousnessCore as an explicit opt-in observer after core activation,
report real tick/lifecycle evidence, and stop it independently of chat.

**Architecture:** Reuse ConsciousnessCore, PerceptionBus, Guardian reflection intents, ThinkStream,
service registry, Hub, and Observatory. A small lifecycle adapter owns one bounded observer worker;
no alternate chat or memory service. The launcher starts it only after core services and enforcing
policy are ready.

**Spec:** User integration plan, Phase C (2026-11-23 attachment), narrowed to C1. Aetherra remains
the persistent entity and Lyrixa its persona.

## Global Constraints

- Preserve pending TemporalConsciousnessEngine work and all unrelated staged/unstaged files.
- Signing, Guardian/Security enforcement, CI, release, dependencies, and authority ownership remain
  unchanged.
- Disabled by default. Only explicit `consciousness_enabled: true` or
  `AETHERRA_CONSCIOUSNESS_ENABLED=1` opts in. C1 accepts only observe; never translate suggest to
  assist.
- C1 uses bounded in-process state: no continuity-file reads/writes, QFAC writes, Memory
  consolidator or actuator. Existing standalone callers retain their behavior.
- Reflection remains Guardian-gated. Default-deny policy blocks the observer honestly; no fabricated
  healthy ticks.
- No broad host sensors or experimental quantum/cosmic/temporal imports in this launch path. Events
  contain bounded measured registry/core health, not conversations.
- No push/PR/merge in this task; leave focused changes reviewable on the isolated branch.

## Tasks

### Task 1: Reproduce current activation and persistence defects

- Run existing Consciousness/Guardian/perception lifecycle tests with isolated data.
- Write failing behavior tests for disabled normal launch, observer construction without shared file
  reads, blocked first tick, completed-vs-attempted ticks, and independent stop.
- Expected: existing tests pass; new tests fail because C1 contracts are absent.

### Task 2: Bound the existing core for observation

- Modify Core with keyword-only `observer_only=False`; preserve legacy defaults. Observer rejects
  actuator/consolidator injection, owns its ThinkStream, bypasses no Guardian decisions,
  reads/writes no ContinuityMemory/QFAC store, and returns read-only status without autopilot
  evaluation.
- ContinuityMemory accepts an explicit disabled path for this mode; persistence attempts fail
  closed.
- ThinkStream adds optional exact event count and effective-mode inputs while preserving old
  callers.
- Tests prove genuine events advance state, allow/deny remain audited, private data is absent from
  ordinary output, and disabled persistence never touches disk.

### Task 3: Own lifecycle on the normal launcher

- Add ConsciousnessObserver lifecycle adapter with one worker, bounded stop, no overlapping
  ticks/restarts, sanitized failure codes, immutable bounded status snapshots.
- Start after registry/kernel/Hub/Memory/Engine and enforcing valid policy readiness; refresh only
  its actual owned live instance. Preserve legacy explicit helpers.
- On denied/failed ticks stop locally and show blocked/failed; do not restart or grant capabilities.
  Slow/blocked tick must not block the main event loop or claim stopped early.
- Feed only measured internal health through PerceptionBus. Keep Engine chat callable after observer
  stop/failure.

### Task 4: Expose truthful status and verify the normal path

- Hub reads the owned observer snapshot when present; failed/stopped/stale snapshots cannot look
  live. Preserve authenticated legacy POST/update interfaces.
- Observatory projects only bounded lifecycle/tick/event/authority fields, with no raw narrative or
  paths.
- Run focused regressions, alpha_boot_validation, integration_validation, full suite, quality/docs
  checks, and disposable normal-launch observer allow/deny/stop checks with offline context-derived
  chat generation.
- Document exact commands and evidence, in-process-only limit, and C2 continuity follow-up. A live
  provider check is conditional on intentionally configured credentials; never call fallback a live
  pass.

## Review Focus

1. Opt-out and malformed config must not create the core, adapters, shared-state reads, or worker.
2. Guardian/policy failure after startup must stop further ticks and prevent successful-tick claims.
3. A slow tick must not block chat or let a stale snapshot look running; stop must report a
   still-owned worker honestly.
4. Instance isolation must not change standalone defaults or leak private/global ThinkStream state.
5. No hidden authority increase through suggest/assist aliases, ambient auto mode, callbacks or
   persistence.

## Decisions

C1 defers durable consciousness continuity because baseline load corruption can overwrite history
and trust restoration is inaccurate. It does not defer storage isolation: C1 performs no persistent
continuity read/write. Cost: observer state intentionally resets after restart until C2.

The current integration plan and request authorize focused implementation; use native execution with
parallel bounded components/review where useful. Record results below and in task-local evidence. Do
not commit or publish before the requested review handoff.

## Verification Outcome

C1 is implemented and verified as an unmerged local candidate based on
`17a833cd0653556b50d869be1f22b989d5633cb4`. The frozen implementation passed
3,651 tests, with 38 skips and 5 passing subtests; the test process exited zero.
The unchanged quality baseline, boot and integration checks passed.

Two normal-launch profiles each crossed a 215-second observation window.
Allowed reflection advanced real ticks and events; denied reflection completed
zero ticks. Both signed audit chains verified. Stopping the observer preserved
ordinary chat and evidence-backed recall. A separate three-process default-off
smoke verified persisted recall, an unknown detail and separate-profile absence,
with zero fallback and clean exits throughout.

The real launch checks exposed adapter/implementation ownership mismatch and
missing Engine heartbeat renewal. Both were reproduced and repaired. Review
also closed audit-receipt, retention, configuration, foreign-ownership and
bounded concurrent-audit gaps. Superseded failed runs remain inspectable and
are not counted as passes.

See the [source-bound evidence](../../evidence/integration_phase_c1_2026-11-24.json)
and [operator procedure](../../ALPHA_OPERATOR_RUNBOOK.md#consciousness-observer-smoke-phase-c1).
Browser, live-model and remote CI checks were not performed for this candidate.
C2 remains the next persistence milestone; pending temporal work is preserved.
No commit, push, PR or merge was performed in this task.
