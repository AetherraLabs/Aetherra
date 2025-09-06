# Alpha Test & Failure Injection Strategy

> Maintained and officially operated by **Aetherra Labs**. **Powered by Aetherra Labs.**

## Goals

1. Prove core subsystems boot & cooperate (smoke / headless boot)
2. Prevent regressions on published capability claims (capabilities suite)
3. Exercise failure paths (memory offline, plugin timeout, HMR rollback)
4. Provide a fast regression bundle developers can run before commit
5. Establish baseline coverage & enforce **no-drop** gate
6. Enable deterministic test profile (AETHERRA_PROFILE=test)

## Test Layers

| Layer             | Scope                                 | Trigger                     | Target Duration |
| ----------------- | ------------------------------------- | --------------------------- | --------------- |
| Smoke             | Headless boot & core services present | pre-commit / CI quick       | <10s            |
| Capabilities      | Public claims / feature contracts     | CI                          | <60s            |
| Failure Injection | Critical degraded-mode paths          | CI nightly / on-demand      | <30s            |
| Full Suite        | All tests (including slower)          | nightly / release candidate | variable        |

## Failure Injection Coverage (Initial)

| Scenario        | Mechanism                              | Expected Behavior                                         |
| --------------- | -------------------------------------- | --------------------------------------------------------- |
| Memory offline  | monkeypatch `recall_memories` to raise | Engine/chat handles gracefully (future: fallback payload) |
| Plugin timeout  | monkeypatch invoke to sleep > timeout  | Kernel marks timeout / continues processing               |
| HMR reload fail | enqueue bogus `hmr_reload`             | Safe failure (audit or ignored)                           |

(Tests currently assert presence / non-crash; TODOs note future specific assertions as metrics/APIs stabilize.)

## Deterministic Profile

Set by `AETHERRA_PROFILE=test` or `--profile test` flag (see `tools/os_smoke.py`). Ensures seeds & reproducible ordering for memory, clustering, reasoning mocks.

## Regression Runner

`tools/run_regression_suite.py` executes fast sets and writes `regression_report.json` with counts + coverage excerpt.

Usage:

```bash
python tools/run_regression_suite.py            # fast (capabilities + failure injection)
python tools/run_regression_suite.py --full     # include broad test target(s)
```

## Coverage No-Drop

`tools/quality_gates.py` maintains `.coverage-baseline`. CI should run it after regression runner; commit raising coverage updates the baseline.

## Next Enhancements

- Assert structured fallback payload on memory/offline path once implemented
- Expose kernel timeout/CB counters → assert increments
- HMR audit counter exposure → assert rollback/gated metrics
- Flaky detector: re-run failed tests up to N times (separate script)
- Nightly profile triggers extended reflections/memory maintenance and then runs full suite

## Runbook (CI ordering)

1. `python tools/os_smoke.py --profile test`
2. `python tools/run_regression_suite.py`
3. `python tools/quality_gates.py` (enforces no-drop)
4. (Nightly) full: `python tools/run_regression_suite.py --full`

## Ownership

Quality & failure-injection strategy is stewarded by Aetherra Labs; contributions must not weaken gates (OWNERSHIP.md). Pending changes should expand assertions, not remove them without justification.
