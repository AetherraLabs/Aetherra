# Temporal Memory history slice

> Historical implementation record: delivery restrictions and pending-work statements below describe this slice when it was executed. The source, Memory foundation and runtime integration are now combined in the Temporal milestone; current operation and verification limits are documented in [Temporal history](../../TEMPORAL_HISTORY.md).

Spec: [governed history contract](../specs/2026-11-26-temporal-memory-history.md).

Use the existing isolated codex/temporal-observer-resume-20261126 worktree at main 5662300. The nine-file source slice was archived before this work; its full-suite evidence remains historical and unchanged.

## Tasks

1. Review the concrete contract before implementation. Record any concurrency/authority rulings.
2. TDD the frozen codec and internal transaction store in memory/temporal_history.py and memory/temporal_history_store.py. Real SQLite tests cover schema, transition, ordering, exact receipt replay, epochs, pages and corruption.
3. TDD the governed worker in memory/temporal_history_worker.py and typed forwarding through memory_core.py, aetherra_memory_engine.py and MemoryAdapter. Keep C2b APIs closed and the existing drain budget.
4. Add real-process persistence, profile, governance/uncertainty, lane contention and C2b separation regressions. Use synthetic numeric observations and real implementation; no model calls.
5. Fresh whole-change review, fix important findings with regressions, run adjacent/full configured tests and quality/docs checks. Record source-bound results, skips, limits and protected-work comparison in separate evidence.

No automatic commit, push, merge or release. This completes the Memory slice only; normal runtime/engine/Observatory integration remains pending.

## Completed local evidence

Tasks 1-5 are complete locally. The contract was reviewed before implementation;
store and worker regressions preceded their fixes. A fresh whole-change review
identified four additional issues, all corrected and independently re-reviewed:
concurrent signed-audit writes, cancelled/terminal worker settlement, idle Core
reference retention and corrupt SQLite classification. Earlier reviews also
closed bounded-materialization and ordinary-shutdown drain gaps.

The configured full suite passed 4,239 tests with 38 skips and 45.29%
coverage. The final focused boundary run passed 215 tests; these results overlap.
The unchanged Python style baseline passed with zero new or edited violations.
See the [source-bound receipt](../../evidence/temporal_memory_history_2026-11-26.json)
for final documentation/preservation checks and exact synthetic restart evidence.

All code remains unstaged and uncommitted. The next slice connects the existing
Temporal engine to the completed-Core-tick source and this Memory boundary, then
wires normal-launch lifecycle and cached Observatory status. No five-second
scheduler, engine import or runtime activation is delivered by this Memory slice.
