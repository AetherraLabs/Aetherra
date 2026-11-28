# Capability CI diagnostics

The normal CI capability step retains evidence for
[DEV-CI-001](DEVELOPMENT_ISSUES.md#dev-ci-001--capabilities-job-timeout-before-a-result-summary)
and [GitHub #381](https://github.com/AetherraLabs/Aetherra/issues/381).
The complete `tests/capabilities` selection and five-minute workflow timeout
remain enforced. Diagnostic output does not establish a cause by itself.

## Retained observations

The [2026-11-27 capture receipt](evidence/dev_ci_001_linux_capture_2026-11-27.json)
records two initial standalone capability passes: 171 passed / 4 skipped in 45.67 and
47.39 seconds. Both used Python `-u` and pytest `-vv`, plus diagnostic hooks;
they changed buffering and verbosity from the original `-q` invocation and may
have affected timing. Their approximately 30-second samples captured short,
completed analytics fixture teardowns, not an established stalled boundary.
The first build-test job failed later at documentation consistency; the second
build-test job passed, while its separate strict quality job timed out.

That strict pytest command exceeded its existing 900-second limit and returned
124. Its last output contained 145 progress dots (17%, 35%, then one dot), with
no named active node, stack or final summary. The receipt retains the exact
command, job link and source-log SHA-256. Its locked dependencies, coverage and
broader selection differ from the standalone job; a shared cause is unknown.

Head `99bec98fdd9665be2ba945a9e60dda5e14905da2` restored buffered interpreter
streams and pytest `-q`, retaining diagnostic hooks and sampling. The third
capture and its one unchanged build-test repeat each completed with 171 passed /
4 skipped (47.88 and 41.75 seconds); both Linux diagnostic regression steps
passed all 38 tests. Both observed zero live owned processes before cleanup.
Their analytics teardown samples completed in 0.395 and 0.338 seconds. Artifact
digests, source-log hashes and exact job identities are retained in the receipt.

The third capture's strict job failed separately with 1 failed / 307 passed /
5 skipped in 95.71 seconds. An inherited diagnostic flag made a nested quality
runner import `tools.ci_capabilities_phase` from a temporary repository where
`tools` was unavailable. This is a diagnostic import regression, not the
historical timeout. A local source-checkout guard now limits plugin injection:
its regressions first reported 2 failed / 4 passed, then the selected Windows
suite passed all 55 tests. This local correction has no Linux result recorded
here. The historical timeout causes remain unknown; passing captures and the
diagnostic correction do not establish broader readiness.

## Controlled Homeostasis correction

The [cancellation receipt](evidence/dev_ci_001_homeostasis_cancellation_2026-11-27.json)
retains the source job, hashes and one compact process/await trace. On Linux
Python 3.11.18, all six pre-fix cases failed at `1d325080`: cancellation consumed
by a dependency, including a real `asyncio.wait_for` completion race, left
component run intent open and shutdown waiting on a sleeping worker. This is a
controlled reproduction, not attribution of the historical capability timeout.
That job's normal capability selection passed 171 tests with four skips.

Commit `b9ab95880d4cbec5b06db3e3b2a441b5da82f84d` closes component run intent
before cancellation/draining and rechecks it after controller steps/actions and
supervisor cycles. It preserves asynchronous teardown order and authority checks.
Seven local regressions pass, including a normal two-cycle controller case;
234 Homeostasis/Guardian/observation/integration checks passed before the positive
case was added. Source hashes distinguish pre-commit working-tree verification
from the recorded base HEAD. Consult [PR #387](https://github.com/AetherraLabs/Aetherra/pull/387)
for final exact-head CI results; this receipt does not assert corrected Linux
verification or broader readiness.

Run the focused regression in the supported installed test environment:

```bash
python -m pytest -q -o addopts= tests/unit/test_homeostasis_shutdown_cancellation.py
```

## Linux reproduction

Use a disposable checkout and the same Python/dependency profile as the CI job.
Keep sampler installation and output outside the checkout because the capability
security test scans repository files. On GitHub-hosted Linux, the sampler uses
passwordless `sudo` for scoped process attachment; it does not change ptrace
settings or elevate pytest.

```bash
diagnostic_root=$(mktemp -d)
python -m venv "$diagnostic_root/sampler"
"$diagnostic_root/sampler/bin/python" -m pip install 'py-spy==0.4.4'
AETHERRA_CI_STACK_SAMPLER="$diagnostic_root/sampler/bin/py-spy" \
  python -m pytest -q -o addopts= tests/unit/test_ci_capabilities_diagnostics.py \
    tests/unit/test_ci_async_diagnostics.py
python -m tools.ci_capabilities_diagnostics \
  --output "$diagnostic_root/evidence" \
  --sampler "$diagnostic_root/sampler/bin/py-spy" \
  -- -q -o addopts= -o faulthandler_timeout=60 tests/capabilities
```

The supervisor sets `AETHERRA_CI_DIAGNOSTICS` only for the launched test process.
Neither diagnostic variable is a runtime profile or persistence setting.
The sampler regression is Linux-only and requires `AETHERRA_CI_STACK_SAMPLER`;
other environments report that test as skipped, not as verified stack capture.

## Strict quality capture

The existing strict quality job also runs capability tests, using
`requirements-ci.lock` and coverage. Its reproduced 900-second pytest timeout
is separate evidence; the standalone captures do not establish its cause.
The job uses the same supervisor around `tools/quality_gates.py`, with snapshots
every minute and a 1,500-second outer watchdog to retain evidence before the
existing 30-minute job limit. The original `TEST_TIMEOUT=900` remains enforced;
the standalone capability step still has its five-minute limit.

The phase plugin is added to the quality runner's direct pytest invocation only
when `AETHERRA_CI_DIAGNOSTICS` is set and its current directory resolves to its
own source checkout. An inherited flag therefore does not inject the plugin
into quality runs from temporary repositories. It is not loaded through
`PYTEST_ADDOPTS` or `PYTEST_PLUGINS`. The artifact is named
`strict-quality-diagnostics-<attempt>`. Signing jobs and policy are unchanged.

## Evidence and limits

- `phases.jsonl`: active node and setup/call/teardown lifecycle, collection and
  session completion, plus allowlisted nonsecret configuration flags.
- `processes.jsonl`: processes in the launched session, start identity, parent,
  state and thread count. Unrelated sessions are excluded.
- `stacks.jsonl`: bounded samples of owned Python processes at approximately
  30, 90, 180 and 260 seconds. Frames omit locals, arguments, command lines,
  thread names and external path prefixes. Nonblocking samples can be partial;
  sampler failures remain visible as sanitized status values.
- `environment.jsonl`: selected package versions and Python version.
- `supervisor.jsonl`: start, watchdog, direct-child exit and any live owned
  descendants before cleanup, then the final exit/reap result. A successful
  wrapper exit does not by itself prove the tested process left no descendants.
- `async-stacks.jsonl`: bounded await-chain frames from marked pytest processes
  after 90 seconds, when a main-thread asyncio loop can service the diagnostic
  callback. No task names, locals or results are collected.

The standalone watchdog fails with exit 124 at 290 seconds and attempts bounded
cleanup before the outer five-minute limit. Otherwise pytest's exit status is
preserved.
The `capabilities-diagnostics-<attempt>` Actions artifact is uploaded even after
a failed capability step. Missing diagnostics cannot turn a pytest failure into
success.

These are synthetic CI diagnostics, not runtime conversation logging. Detached
processes outside the launched session are not sampled or terminated. The
optional asyncio capture uses `SIGUSR1` only in the dedicated pytest process,
respects an existing custom handler, and ignores late delivery after pytest
unconfigures when it still owns the handler. It does not cover event loops in
other threads or a loop blocked in synchronous code. An idle selector without corresponding await-chain
evidence does not identify an awaited operation. Keep original failures and
distinguish a reproduced cause from passing reruns or uninstrumented historical
incidents.
