# Alpha Operator Runbook

Updated: 2026-11-22

**Current decision: Go for supervised synthetic verification; no-go for broader
internal alpha.** Candidate `codex/alpha-chat-contracts` integrates main
`86982cc5` (`v0.5.0-beta.4`). ALPHA-07 and the original nine legacy failures are
fixed, along with the remaining reproduced suite/readiness defects. Candidate
CI passes; merge/clean-main acceptance is pending at this evidence checkpoint,
with results to be recorded in PR #326. Desktop dependency disposition remains.
See [the decision](ALPHA_READINESS_DECISION.md) and
[fresh evidence](evidence/internal_alpha_integration_2026-11-22.json).

Latest default suite: **3,135 passed / 40 skipped**, process exit 0 from a frozen source
copy with default collection/addopts/coverage. GUI: 18 tests plus build/lint;
Python quality: zero new violations against the unchanged baseline. Fresh
normal-launcher verification: three gpt-4o turns after restart with no fallback.
The earlier 35-turn/nine-process matrix remains historical evidence.

## Operating Boundary

Guardian decides; Security enforces; Self-Incorporation executes approved
locked plans; Homeostasis verifies; Maintenance records. Do not connect this
candidate to production credentials, private user data, payment systems,
external automation targets or unattended networked control surfaces.

Keep signing, capability and Guardian enforcement enabled. Do not grant broad
capabilities or turn off signing to make a smoke check pass. Local profile
directories separate storage; they do not implement user/account authentication.

## Prerequisites And Preflight

Use a clean isolated checkout and a provisioned Python environment. The recorded
Windows run used Python 3.13.7, existing runtime dependencies and the cached,
pinned MiniLM model described in [PERSONAL_CONTINUITY.md](PERSONAL_CONTINUITY.md).
It did not prove a fresh dependency install. The legacy desktop dependency
findings in [BUILD_REPRODUCIBILITY.md](BUILD_REPRODUCIBILITY.md) remain open.
The provisioned environment also reports a missing `pathlib` distribution required
by legacy `pyxnat 1.6.3`; a green suite does not resolve dependency metadata or
security debt. Use Ruff 0.17.6, Black 26.10.1 and isort 9.0.2 as pinned in CI;
check the actual CLI versions as well as installed metadata. The verification
used a task-local tool environment and did not modify shared environments.

From the repository root:

```powershell
python tools\alpha_boot_validation.py
python -m Aetherra.integration_validation
python tools\verify_docs_consistency.py
python tools\ci_verify_no_website_artifacts.py
git diff --check
```

Expect four boot-contract checks and five integration-contract checks to pass.
These checks do not start the full runtime. The docs command writes
`docs/DOCS_CONSISTENCY_REPORT.md`; preserve any pre-existing local version and
keep generated report changes separate from reviewed source work.

The exact focused selection used for the 194-test alpha regression run:

```powershell
$alphaTests = @(
  'test_alpha_boot_validation.py', 'test_integration_validation.py',
  'test_selfinc_integration_guardian.py', 'test_self_incorporation_security.py',
  'test_guardian_approval.py', 'test_guardian_policy_engine.py',
  'test_guardian_preauthorization.py', 'test_guardian_containment.py',
  'test_prod_security_guard.py', 'test_prod_security_defaults.py',
  'test_hub_ingress_security.py', 'test_hub_kernel_guardian.py',
  'test_hub_self_improvement_guardian.py', 'test_hub_guardian_api.py',
  'test_security_audit_ledger.py', 'test_security_ledger_disabled.py',
  'test_stdlib_executor_security.py', 'test_service_registry_guardian.py',
  'test_kernel_direct_guardian.py', 'test_homeostasis_integration_guardian.py'
) | ForEach-Object { "tests/unit/$_" }
$alphaTests += @(Get-ChildItem tests/unit/test_runtime_ui_*.py |
  ForEach-Object { $_.FullName })
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_safety @alphaTests
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_continuity tests/acceptance/test_personal_continuity.py
```

Homeostasis/UI regression command (112 tests at the earlier checkpoint;
the directory selection also includes new follow-up tests and overlaps the
selection above):

```powershell
$alphaUiTests = @(Get-ChildItem tests/unit/test_runtime_ui_*.py | ForEach-Object { $_.FullName })
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_final @alphaUiTests tests/unit/homeostasis tests/unit/test_homeostasis_integration_guardian.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_signing tests/tools/test_release_signing.py tests/test_hub_signing.py tests/test_discovery_signing.py
python tools/python_quality.py
```

Signing selection: 13 tests. The fixed style baseline must remain unchanged.
Default collection no longer stops on legacy imports. The final broad default
run finished with 3,135 passed / 40 skipped and process exit 0; the following full-suite
command is separate from the scoped selections.

The combined API, policy, routing, tracing, maintenance and continuity follow-up
command (see the decision for the latest recorded result):

```powershell
$followupTests = @(
  'tests/unit/homeostasis/test_launcher_hub_ownership.py',
  'tests/unit/test_selfinc_audit_api.py', 'tests/unit/test_storm_recall_routing.py',
  'tests/unit/test_memory_persistence_policy.py',
  'tests/tools/test_memory_fragmentation_tracing.py',
  'tests/capabilities/test_memory_fragmentation_metrics.py',
  'tests/acceptance/test_maintenance_security.py',
  'tests/acceptance/test_personal_continuity.py'
)
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_followup_tests @followupTests
```

Run regression commands in a fresh shell, before applying the manual runtime
environment below. Do not impose a shared Guardian state directory on tests
that configure their own workspace. Keep the manual runtime stopped during
HTTP tests so their listeners cannot collide.

For the full CI test-directory selection, use a credential-free shell with no
inherited Aetherra/Guardian overrides. On Windows, keep parent and child process
text decoding consistent:

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:AETHERRA_SKIP_DOTENV = '1'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_ci tests/capabilities tests/unit tests/integration
```

This checks the CI test selection, not the complete remote workflow or its
coverage, packaging and release-signing jobs.

For the complete default suite, use the same credential-free, offline shell,
an isolated source copy and no running manual listeners. Do not override
`addopts`, select only CI directories, or attach runtime Guardian state to tests:

```powershell
python -m ruff --version
python -m black --version
python -m isort --version-number
python -m pytest --junitxml .pytest_tmp_alpha_full.xml
```

The recorded final run used a frozen copy and verified pytest's `rootdir`
against it. Runtime source matches the reviewed candidate; the test differs only by two
import-section comments, with identical parsed Python structure. Counts, exit
code, log digest and individual skip reasons are in the integration evidence.
The earlier diagnostic full run was from an editable checkout while repairs
were developed, so it is not an immutable baseline. A wrapper cwd mistake in
an initial final attempt was detected, stopped and corrected before this pass.

Configured advanced-memory redactors are tested at the existing persistence
boundary. Their output is checked against the original caller's authority;
failure prevents storage. This does not enable a redactor by default or add
account isolation. The launcher's direct core-memory adapter is unchanged.

The separate continuity selection passed 3 tests. Its subprocess harness replaces
only text generation; it is distinct from the manual CLI/browser smoke below.

## Build The Observatory

```powershell
Push-Location Aetherra\lyrixa\gui
npm.cmd ci --ignore-scripts --no-audit
npm.cmd run build
npm.cmd test
npm.cmd run lint
Pop-Location
```

The current build has a large-chunk warning. Do not confuse build/unit-test
success with a passing live browser check.

## Start The Full Runtime In A Disposable Profile

Use a new disposable **PowerShell 7.5 or newer** terminal with the provisioned
Python selected. Windows PowerShell 5.1 has different UTF-8 file and empty
environment-variable behavior and is not the shell for this procedure.
The following removes ambient provider credentials from that terminal only and
skips dotenv loading. It deliberately exercises the no-provider behavior.

```powershell
$alphaRepo = (Get-Location).Path
$alphaPython = (Get-Command python).Source
$alphaProfile = Join-Path $alphaRepo ('.pytest_tmp_alpha_' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $alphaProfile | Out-Null
New-Item -ItemType Directory -Path (Join-Path $alphaProfile 'policy') | Out-Null
Get-ChildItem Env: | Where-Object {
  $_.Name -match '^(AETH|LYRIXA|OPENAI|ANTHROPIC|GOOGLE|AZURE|AWS|CLOUDSDK|TEST|GIT_CONFIG_)' -or
  $_.Name -match 'KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PROXY'
} | ForEach-Object { Remove-Item -LiteralPath ("Env:" + $_.Name) }
$env:PYTHONPATH = $alphaRepo
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:TOKENIZERS_PARALLELISM = 'false'
$env:NO_PROXY = '*'
$env:AETHERRA_SKIP_DOTENV = '1'
$env:AETHERRA_PROFILE = 'test'
$env:AETHERRA_GUARDIAN_MODE = 'enforcing'
$env:AETHERRA_REQUIRE_CAPABILITIES = '1'
$env:AETHERRA_SCRIPT_VERIFY_STRICT = '1'
$env:AETHERRA_SIGNING_STRICT = '1'
$env:AETHERRA_AUDIT = '1'
$env:AETHERRA_STATE_DIR = Join-Path $alphaProfile 'state'
$env:AETHERRA_WORKSPACE_ROOT = $alphaProfile
$env:AETHERRA_POLICY_HOME = Join-Path $alphaProfile 'policy'
$env:AETHERRA_GUARDIAN_POLICY = Join-Path $alphaProfile 'policy/guardian.json'
$env:AETHERRA_GUARDIAN_STATE_DIR = Join-Path $alphaProfile 'guardian'
$env:AETHERRA_HUB_PORT = '3001'
$env:AETHERRA_HUB_PORT_AUTOFIX = '0'
$env:AETHERRA_HUB_URL = 'http://127.0.0.1:3001'
$env:AETHERRA_SKIP_LAUNCHER_AI_DEFAULTS = '1'
$env:AETHERRA_AI_API_ENABLED = '1'
$env:AETHERRA_AI_API_STREAM = '1'
$env:AETHERRA_AI_API_REQUIRE_TOKEN = '1'
# Synthetic tokens for this local disposable check only.
$env:AETHERRA_AI_API_TOKEN = 'synthetic-alpha-chat'
$env:AETHERRA_HUB_CONTROL_TOKEN = 'synthetic-alpha-control'
$env:AETHERRA_NET_STRICT = '1'
$env:AETHERRA_HOMEOSTASIS_OBSERVE_ONLY = '1'
$env:AETHERRA_HOMEOSTASIS_MODE = 'observe_only'
$env:AETHERRA_SELFINC_ENABLED = '0'
$env:AETHERRA_HMR_ENABLED = '0'
$env:AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT = '0'
$env:AETHERRA_LYRIXA_FORCE_OFFLINE = '1'
$env:AETHERRA_NO_FAKE_DATA = '1'
$env:AETHERRA_REGISTRY_URL = ''
$alphaConfig = @{ hub_enabled = $true; gui_enabled = $false } | ConvertTo-Json
[IO.File]::WriteAllText((Join-Path $alphaProfile 'launcher.json'), $alphaConfig, [Text.UTF8Encoding]::new($false))
```

Confirm ports 3000 and 3001 are free before starting. Do not stop another
operator's listener. These are requested settings, not proof they all take
effect: Homeostasis now enforces observation-only, but Self-Incorporation
status still reports enabled. No policy grants are added here; optional
operations may be denied. This is a verified bounded observation configuration,
not acceptance of unattended operation or all optional services.

```powershell
Push-Location $alphaProfile
& $alphaPython (Join-Path $alphaRepo 'aetherra_os_launcher.py') --mode full --no-gui --config (Join-Path $alphaProfile 'launcher.json')
Pop-Location
```

This is full launch mode. `AETHERRA_PROFILE=test` is the policy profile and does
not select the launcher's mock `--mode test`. Working in the fresh directory
keeps relative memory/database/log files out of source; some optional relative
configuration files will be absent and use defaults.

`tools/run_hub_ai_api.py` starts a standalone Hub; `tools/os_smoke.py` checks a
smaller lifecycle. Neither proves full-launcher integration. The standalone Hub
helper also overrides token settings unless its token arguments are supplied;
do not substitute it for this authenticated launch.

## Inspect Real Readiness

In a second terminal, require JSON, not merely HTTP 200:

```powershell
function Read-AlphaJson($path, $headers = @{}) {
  $reply = Invoke-WebRequest ("http://127.0.0.1:3001" + $path) -Headers $headers -TimeoutSec 10
  if ($reply.Headers['Content-Type'] -notmatch 'application/json') {
    throw "Expected JSON from $path"
  }
  $reply.Content | ConvertFrom-Json
}
Read-AlphaJson '/health'
Read-AlphaJson '/api/hub/readiness'
Read-AlphaJson '/api/kernel/readiness'
Read-AlphaJson '/api/ai/status'
Read-AlphaJson '/api/runtime-ui/status'
$alphaSnapshot = Read-AlphaJson '/api/runtime-ui/bootstrap?mode=first_launch&user=Alpha&limit=8'
$alphaSnapshot.observatory.subsystems | Where-Object name -eq 'homeostasis' | Select-Object -ExpandProperty metrics
Read-AlphaJson '/api/maintenance/status'
Read-AlphaJson '/api/selfinc/status'
Read-AlphaJson '/api/security/policy'
$alphaHeaders = @{ 'X-Aetherra-Token' = 'synthetic-alpha-control' }
Read-AlphaJson '/api/guardian/status' $alphaHeaders
Read-AlphaJson '/api/homeostasis/status'
Read-AlphaJson '/api/selfinc/audit' $alphaHeaders
Read-AlphaJson '/api/selfinc/audit?action=register_workflow&status=applied&limit=20' $alphaHeaders
```

The fresh candidate check returned Hub/Kernel ready. Engine was degraded
without a provider (four lifecycle events, one problem), and ready with gpt-4o
(three successful events, zero problems; `safe_for_requests=true`). Successful
receipts remain visible without being counted as errors; unknown or malformed
events still degrade readiness. Repeat the snapshot after at least 30 seconds and after process
restart. Require `controller_mode=observe_only`, `observe_only_requested=true`
and all three `actuator_actions_attempted/executed/blocked` counters equal zero.
Null counters mean missing evidence, not a pass. `restart_count` and
`error_recovery_count` should also stay zero. The lifecycle badge `active` means
running; it does not mean the controller is in active mode.

`/api/homeostasis/status` now addresses the full launcher's actual instance.
Require `orchestrator.initialized=true`, `running=true`, controller mode
`observe_only` and zero actuator attempts/executions. It remains usable if the
registry heartbeat is stale and the Observatory honestly reports unknown.

Authenticated `/api/selfinc/audit` now counts statuses among the newest matching
records (default limit 50). No-argument Python service calls retain all-record
totals. Missing credentials return 401; invalid or out-of-range limits return
400. An empty new profile can legitimately have an empty audit summary.

Guardian was enabled/enforcing with audit integrity true. Kernel
controls were disabled. `/api/security/policy` describes chat policy; it does not
prove the effective capability/network enforcement policy. `/api/health` and
`/api/security/status` returned SPA HTML, so are not valid JSON health checks.

For the bounded no-provider chat check, use a synthetic prompt:

```powershell
$alphaBody = @{
  message = 'Hello Lyrixa, this is a synthetic alpha readiness check.'
  scratchpad_policy = 'ephemeral'
} | ConvertTo-Json
$alphaChatHeaders = @{ 'X-Aetherra-Token' = 'synthetic-alpha-chat' }
Invoke-RestMethod http://127.0.0.1:3001/api/ai/ask -Method Post -ContentType 'application/json' -Headers $alphaChatHeaders -Body $alphaBody -TimeoutSec 90
```

Check `result.llm.fallback=true` and `used=false`; this is not a live-model
pass. Cold embedding startup exceeded 30 seconds in the earlier baseline run. A client
timeout does not mean the turn was not saved. Avoid automatic retries of writes.
Use the separate configured-model procedure in
[PERSONAL_CONTINUITY.md](PERSONAL_CONTINUITY.md) when a live-model check is needed.

## Live-Model Recheck With Strict Signing

Use a separate shell with only the approved `OPENAI_API_KEY` supplied through
your existing secret mechanism. Do not paste it into commands, commit it or
print it. These are manual online checks, separate from offline pytest.
The current provider is OpenAI `gpt-4o`; only synthetic facts are sent.

The existing continuity helper starts the same full launcher and `/api/ai/ask`
route, with real storage, retrieval and model generation. Its environment filter
removes ambient Aetherra flags. Use this environment-only wrapper to explicitly
retain strict signing in every child; no service or generation implementation is
replaced. Run from the clean repository root with a new profile directory:

```powershell
$env:AETHERRA_LLM_MODEL = 'gpt-4o'
@'
from pathlib import Path
import runpy, subprocess, sys
root = Path.cwd()
original = subprocess.run
def configured_run(command, *args, **kwargs):
    child = str(root / "tests/acceptance/continuity_runtime.py")
    if isinstance(command, list) and child in command:
        kwargs["env"].update(AETHERRA_SIGNING_STRICT="1",
                             AETHERRA_SCRIPT_VERIFY_STRICT="1")
    return original(command, *args, **kwargs)
subprocess.run = configured_run
sys.argv = [str(root / "tests/acceptance/test_personal_continuity.py"),
            "--live", "--extended", "--profile", ".pytest_tmp_alpha_live_operator"]
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
finally:
    subprocess.run = original
'@ | python -
```

Require all nine child processes to stop, empty initial user histories, all 35
turns using gpt-4o without fallback, and stored/retrieved/provider-input record
IDs and content to match. Inspect the door-color and both negative replies;
empty evidence must produce an honest acknowledgment, not a guessed fact.
Only local data-directory isolation is claimed.

The direct full-CLI live restart was also tested with the preceding disposable
profile, unchanged strict flags and the live helper's scoped policy: default
deny; registry operations, chat ingress, Kernel shutdown, and `core:llm` outbound
inference to `api.openai.com` only. Broad capability grants were not used. A fresh
CLI session recalled the prior persisted fact, acknowledged unknown color and
preserved Aetherra/Lyrixa identity. The matrix above additionally captures the
actual generator input for inspection.

## Chat Contract Recheck

After stopping manual listeners, run the repaired legacy and boundary tests:

```powershell
$legacyTests = @(
  'tests/consciousness/test_active_inference_integration.py',
  'tests/consciousness/test_identity_unified.py',
  'tests/consciousness/test_self_model.py',
  'tests/unit/test_chat_request_contract.py',
  'tests/storm/test_storm_security.py', 'tests/test_headers_and_expiry.py',
  'tests/test_aether_workflow_additional_paths.py'
)
python -m pytest -v -o addopts= @legacyTests
```

The original nine failing cases now pass. The new tests also cover zero
deadlines, negative TTLs, early error headers, unreadable/oversized request
bodies and expired WebSocket idempotency. The identity loader resolves the
shipped source-checkout configuration independently of the profile directory;
explicit paths retain their behavior. STORM assertions inspect reopened storage
and recall, and the ethics test compares each estimate with its own action.

With the full CLI running, check expiry through the same authenticated endpoint:

```powershell
$expired = @{
  message = 'Synthetic expired alpha request.'
  deadline_ts = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - 10
} | ConvertTo-Json
$headers = @{
  'X-Aetherra-Token' = 'synthetic-alpha-chat'
  'X-Aetherra-Trace-Id' = 'synthetic-alpha-expiry'
}
$reply = Invoke-WebRequest 'http://127.0.0.1:3001/api/ai/ask' -Method Post `
  -ContentType 'application/json' -Headers $headers -Body $expired -SkipHttpErrorCheck
if ($reply.StatusCode -ne 409) { throw 'Expired request was not rejected' }
$reply.Headers
$reply.Content
```

Expect `invalid_request` / `Request expired`, chat version `2`, the supplied
trace ID and a JSON policy header. Expired stream POST and GET requests produce
only `error` then `final` SSE events with the same trace. Disabled and
unauthenticated requests retain their existing rejection status. Expired
requests must not reach storage/generation or consume a client message ID.
The `hub_chat_dlq.jsonl` compatibility receipt contains only reason, type and
endpoint; it does not contain the prompt or client identifiers. Malformed
optional deadline values remain ignored; valid nonpositive TTLs expire at admission.

Admission also rechecks the same absolute deadline after safety, Guardian and
registry waits. An expired turn must not produce an offline-success answer or
reach generation. POST/GET streams and WebSocket requests release only their
own message-ID reservation when admission expires, so the same ID can be retried
with a valid deadline. These are admission deadlines: they do not cancel or roll
back generation that already started before expiry.

Run the deterministic timing and retry regressions with:

```powershell
python -m pytest -q -o addopts= tests/unit/test_chat_request_contract.py
```

The broader default command remains a separate check: `python -m pytest`.
Use the decision and evidence for its outcome; a focused pass does not imply
that the default repository-wide run passed.

## Browser Observation And Stop/Restart

With the full launcher still running, from the repository's GUI directory:

```powershell
npm.cmd run dev -- --host 127.0.0.1 --port 3000 --strictPort
```

The 2026-11-22 suite/readiness rerun used Hub `13301` and UI `13300` to avoid
interference from concurrent regression tests. For those exact ports, set
`AETHERRA_HUB_PORT=13301` and `AETHERRA_HUB_URL=http://127.0.0.1:13301` before
the same launcher command, and replace the probe origin accordingly. Instead
of the dev command above, run this from `Aetherra/lyrixa/gui`; it loads the
same Vite configuration and overrides only the server host, ports and proxy:

```powershell
@'
import { createServer } from 'vite';
const server = await createServer({ server: {
  host: '127.0.0.1', port: 13300, strictPort: true,
  proxy: { '/api': { target: 'http://127.0.0.1:13301', changeOrigin: true } }
} });
await server.listen();
server.printUrls();
'@ | node --input-type=module
```

Open `http://127.0.0.1:13300/` for that variant. No runtime service or UI response
is replaced.

Open `http://127.0.0.1:3000/`. This dev server proxies the existing Runtime UI API
to the full-launcher Hub on port 3001. Confirm Cognitive Observatory rendering,
Runtime API source and read-only controls; inspect browser console errors.
Expect no-provider degradation and configured-model Engine readiness to match
the JSON response; unregistered services must remain unknown. Select Engine to
compare its summary with JSON readiness. Inspect the three visible observation
titles; no React list-key error should occur. Registry presence is not measured
subsystem health, and activity should say Not measured.

Press Ctrl+C in the launcher terminal. Confirm the process exits and port 3001
closes, then observe the Observatory while the dev server stays up. The current
patch must show Runtime unavailable, every subsystem unknown, Source
Unavailable, Activity Not measured and an empty event feed. Verify automatic
polling replaces the previous live state, then refresh if desired. The fetch
has an eight-second deadline and the polling interval is fifteen seconds.

Repeat only the launch command block with the same `$alphaProfile`. Confirm a
new process, fresh Kernel cycle count and readiness responses. Stop it with
Ctrl+C and stop the GUI dev server separately. The two recorded runtime
processes exited 0, with a watchdog teardown error logged before completion.
If a process remains, inspect its PID/parent relationship before intervening;
never kill unrelated Python/Node processes.

After verification, inspect `git status --short`. Preserve unrelated staged and
unstaged changes. Keep raw logs, databases, credentials and generated build
outputs out of commits.

## Governance And Rollback Review

Denied actions must fail before mutation; approval-required actions must not
execute without valid approval. Self-Improvement remains proposal-only.
Self-Incorporation must validate approved scope and have truthful rollback
support or fail closed. The recorded integration/unit tests exercise these
contracts. The smoke established bounded Homeostasis observation-only behavior;
it did not authorize real mutation. The operator API findings are fixed in merged main.
The requested chat/legacy repairs pass in the isolated candidate. Evidence
records the reviewed checkpoint and fresh restart checks. Candidate CI passes;
Merge and clean-main acceptance are pending at this checkpoint; their results
will be recorded in PR #326. Resolve or explicitly
disposition desktop dependency limits before wider alpha operation.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
