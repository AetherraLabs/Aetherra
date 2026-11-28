# Shutdown cancellation follow-up

Record: [DEV-SELFINC-002](DEVELOPMENT_ISSUES.md#dev-selfinc-002--startup-ownership-and-opt-in),
[GitHub #42](https://github.com/AetherraLabs/Aetherra/issues/42). Reviewed 2026-11-28.
This correction addresses the shutdown escape path; the startup-owner/opt-in defect remains OPEN.

## Established cause

On baseline `9c2e7708adc6c3eaa9d78388b0f92627855a0800`, a Windows SIGINT can request
cancellation while the main task is executing synchronous code between suspensions.
The launcher's `cancelling()` guards manually raised `CancelledError`. That exception
changed control flow but did not deliver the cancellation still queued by `Task.cancel()`.
The operation loop consequently returned an orderly-stop result with delivery pending.
The queued cancellation then arrived at the first asynchronous cleanup suspension,
`_stop_presence_resources` awaiting the owned Hub stop. Kernel, registry and individual
system shutdown were skipped. The non-daemon Homeostasis watchdog kept the process alive.

Boundary instrumentation and one real CLI `_thread.interrupt_main()` at the end of
`_write_os_status` reproduced this sequence. The child wrote a worker exit-zero receipt,
but its process needed termination at the 70-second diagnostic outer limit. Its 50-second
stack dump retained `threading._shutdown`, the watchdog, scheduler and Hub server waits.
No second signal was sent. This establishes a concrete cause with the same retained
symptoms; it does not retroactively identify every earlier hang's initiating event.

The fix yields once at each of the six existing cancellation guards before the explicit
raise. Asyncio delivers any queued cancellation inside the existing cancellation handler,
before cleanup starts. The explicit raise still handles a dependency that consumed the
original exception. Cancellation counts, orderly checkpoint eligibility, startup cleanup,
second-interrupt behavior, Guardian and Security remain unchanged. No `uncancel()`, private
task field, blanket cancellation suppression, daemonization or longer timeout is used in
production. Private pending-delivery state was inspected only by the disposable diagnostic.

## Additional CI shutdown boundary

The documentation revision `3822a021` captured a Linux capability timeout in
`test_qfac_optional_service_registration`: the test awaited its cancelled boot task,
which awaited Homeostasis shutdown and its controller's in-flight kernel action. Three
async snapshots retained that chain. The existing five-minute gate failed with exit 124;
the failed job and artifact hashes remain in the compact evidence.

Two controlled regressions showed the remaining batch gap: closing controller run intent
left unstarted actions queued. If an action consumed cancellation, the batch could dispatch
another action during shutdown and wait through its timeout. `HomeostasisController.stop()`
now clears that unstarted queue before its owner cancels and awaits the worker. This adds
no action authority and preserves normal dispatch, observation-only and Guardian gates.
The corrected combined set passes **113 tests**, including both new batch regressions.
Three fresh normal profiles and the controlled CLI check also exit 0 after both corrections.

This extends [DEV-CI-001 / #381](https://github.com/AetherraLabs/Aetherra/issues/381)
with a captured shutdown wait and a controlled correction. Historical failures stay OPEN;
the new evidence does not identify every historical initiating event. Final-head capability
and CI results are recorded in the PR after completion.

## Verification evidence

[Compact source-bound evidence](evidence/shutdown_cancellation_2026-11-28.json) retains the
before/after traces, source hashes, child receipts and raw-log hashes. Original P0 failures
remain in [the P0 trace](RUNTIME_EVIDENCE_P0_TRACE.md) and #42.

- Unchanged baseline: existing cancellation tests passed; an ordinary three-profile run
  also passed. Neither pass ruled out the timing defect.
- New deterministic regression: **18 failures before correction**, each at owned cleanup;
  covers six startup/operation boundaries and unmarked, single marked, repeated cancellation.
- Corrected focused set: **65 passed**. This includes existing first/second SIGINT,
  checkpoint intent, consumed cancellation and Homeostasis teardown coverage.
- Identical controlled real-CLI signal after correction: process exited 0 in about nine
  seconds, with launcher cleanup completing and no pending cancellation delivery.
- Two unchanged normal probes: **six process exits 0**, with Self-Incorporation unset,
  explicitly enabled and explicitly disabled; the original 60-second stop limit is intact.
- Full default Windows suite before the additional queue correction: **4444 passed,
  49 skipped, 5 subtests passed**. The command
  exited **3** after the tests because coverage aggregation mixed branch and statement
  data. This is not a clean full-command pass. The unchanged nested-pytest diagnostic
  test independently reproduces the reporting error. Both datasets remain retained;
  reporting from the original parent branch dataset succeeds at **45%**, above the
  unchanged **22%** threshold. No coverage or timeout policy was relaxed.
- Implementation commit `370952e8`: **37 CI checks passed**, with one expected
  Dependabot-only skip. CI Quality Gates passed **3235 tests, 9 skipped**, plus the
  separate **58 signing regressions, 5 subtests**. Production signing steps run on
  main pushes and are intentionally skipped for a PR. The PR records current-head CI.

Successful process exits still log the pre-existing Homeostasis watchdog error
`Event loop stopped before Future completed`, also present in baseline runs. This is
[DEV-HOMEOSTASIS-001](DEVELOPMENT_ISSUES.md#dev-homeostasis-001--watchdog-shutdown-lifecycle),
[GitHub #373](https://github.com/AetherraLabs/Aetherra/issues/373), which remains OPEN.
A process exit is not evidence that its separate cooperative-shutdown contract is
complete. Likewise, this fix does not resolve #42's startup ownership/opt-in mismatch.

The coverage reporting limitation is in the unchanged nested-pytest path in
`tests/tools/test_quality_gate_diagnostics.py`: its statement-only child inherits the
parent's `COVERAGE_FILE`, while the parent collects branch coverage. The original
exit-3 receipt is retained alongside the recovered report; this focused launcher PR
makes no change to that test infrastructure.

## Repeat the supported checks

From a checkout with the supported development dependencies installed:

```powershell
$shutdownTests = @(
  "tests/unit/test_launcher_operation_cancellation.py"
  "tests/unit/test_launcher_startup_cancellation.py"
  "tests/unit/test_launcher_windows_sigint.py"
  "tests/unit/test_homeostasis_shutdown_cancellation.py"
)
python -m pytest -q -o addopts= $shutdownTests
python tools/inspect_runtime_evidence_p0.py --output "$env:TEMP/aetherra-shutdown-check-$([guid]::NewGuid().ToString('N'))"
python -m pytest
```

The normal probe requires a new output directory and uses isolated synthetic profiles,
the real launcher/Hub/Engine/Memory, existing offline generation double and strict guards.
Its receipts check process exit rather than trusting worker return codes. The deterministic
unit regression supplies cancellation without suspension; no timing lottery or physical
keyboard is needed to catch this source defect. No live-model, browser or physical-keyboard
pass is claimed. This is not a new alpha GO or a closure of #42's remaining ownership work.
The five-minute capability-test CI timeout, release signing and style baseline are unchanged.
