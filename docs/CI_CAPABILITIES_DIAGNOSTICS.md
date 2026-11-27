# Capability CI diagnostics

The normal CI capability step retains evidence for
[DEV-CI-001](DEVELOPMENT_ISSUES.md#dev-ci-001--capabilities-job-timeout-before-a-result-summary)
and [GitHub #381](https://github.com/AetherraLabs/Aetherra/issues/381).
The complete `tests/capabilities` selection and five-minute workflow timeout
remain enforced. Diagnostic output does not establish a cause by itself.

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
  python -m pytest -q -o addopts= tests/unit/test_ci_capabilities_diagnostics.py
python -m tools.ci_capabilities_diagnostics \
  --output "$diagnostic_root/evidence" \
  --sampler "$diagnostic_root/sampler/bin/py-spy" \
  -- -vv -o addopts= -o faulthandler_timeout=60 tests/capabilities
```

The supervisor sets `AETHERRA_CI_DIAGNOSTICS` only for the launched test process.
Neither diagnostic variable is a runtime profile or persistence setting.
The sampler regression is Linux-only and requires `AETHERRA_CI_STACK_SAMPLER`;
other environments report that test as skipped, not as verified stack capture.

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
- `supervisor.jsonl`: start, watchdog and exit/reap result.

The watchdog fails with exit 124 at 290 seconds and attempts bounded cleanup
before the outer five-minute limit. Otherwise pytest's exit status is preserved.
The `capabilities-diagnostics` Actions artifact is uploaded even after a failed
capability step. Missing diagnostics cannot turn a pytest failure into success.

These are synthetic CI diagnostics, not runtime conversation logging. Detached
processes outside the launched session are not sampled or terminated. Thread
stacks do not enumerate suspended asyncio tasks; an idle selector alone does
not identify an awaited operation. Keep original failures and distinguish a
reproduced cause from passing reruns or uninstrumented historical incidents.
