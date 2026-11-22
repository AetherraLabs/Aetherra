# Capability process shutdown

The capability suite boots the real OS in its QFAC and self-maintenance tests.
Cancelling those boots before the operation loop previously bypassed graceful
shutdown. Python could report passing assertions and then wait indefinitely for
the non-daemon Homeostasis watchdog. The launcher also discarded its perception
adapters; idle journal followers were never terminated or reaped.

## Evidence

- [Unchanged-main diagnostic run](https://github.com/AetherraLabs/Aetherra/actions/runs/45059067768/job/137320686085):
  `165 passed, 4 skipped in 40.80s`, followed by Python blocked in
  `threading._shutdown`, a live `HomeostasisWatchdog`, a registry child, and two
  shell/journalctl trees. The bounded diagnostic exited 124 after 120 seconds.
- [Fixed-runtime diagnostic run](https://github.com/AetherraLabs/Aetherra/actions/runs/45059946411/job/137323406657):
  `170 passed, 4 skipped in 43.01s`; `PYTEST_PROCESS_EXIT 0` about four seconds
  later, with no non-daemon worker or leaked child. The subsequent SSE step
  completed (`8 passed`). This run preceded the additional syslog-fallback
  regression. Temporary diagnostic instrumentation is removed from the final
  patch; [PR #324](https://github.com/AetherraLabs/Aetherra/pull/324) records the
  final normal-command CI results.

Shutdown now runs from the launcher's outer `finally`, including startup failure
and cancellation. The launcher retains and stops its perception adapters and
awaits its consciousness task. The journal adapter owns its follower directly,
terminates/reaps it even without another log line, joins its reader, and retains
syslog fallback when journald is absent or fails. Both OS capability tests await
teardown even on a skip or assertion failure.

## Reproduce

Use a disposable clean checkout and a separate environment: these tests boot
runtime components and create local state. From the checkout root on Linux:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt pytest pytest-asyncio
pytest -q -o addopts= tests/capabilities
printf 'pytest exit: %s\n' "$?"
```

Success requires process exit 0, not merely a passing pytest summary. CI runs
this unchanged pytest command with a five-minute step limit that fails the job
if shutdown regresses; it does not convert a timeout into success. The following
focused regressions are offline and use real watchdogs, sockets, child processes,
and pipe readers; only host telemetry sources and external boot setup are replaced:

```sh
python -m pytest -q -o addopts= \
  tests/capabilities/test_launcher_shutdown.py \
  tests/capabilities/test_perception_shutdown.py
```

The SIGTERM-ignore case runs on Linux and is skipped on Windows, where terminate
does not deliver SIGTERM. Release-signing keys, required signing checks, security
policies, and the fixed legacy style baseline are unchanged.
