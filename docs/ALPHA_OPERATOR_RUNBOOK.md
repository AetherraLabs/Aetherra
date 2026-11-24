# Alpha Operator Runbook

Updated: 2026-11-24

**Current decision: GO for supervised internal alpha on the documented Windows
source-runtime profile.** At the 2026-11-22 desktop checkpoint, PR #327 was
merged and clean main and the signed `v0.5.0-beta.6` release passed acceptance.
Unattended/production operation and
unverified installation graphs remain NO-GO. See
[the decision](ALPHA_READINESS_DECISION.md),
[fresh evidence](evidence/desktop_alpha_2026-11-22.json) and
[clean-main evidence](evidence/desktop_alpha_main_2026-11-22.json).

Fresh installation: 167 locked packages plus pip, no inherited system packages,
zero broken requirements, exact lock sync, and zero findings/skips across all
168 audited distributions. Fresh GUI: 18 tests, build/lint and zero audit findings.
At that desktop checkpoint, normal-launcher stop/restart, three gpt-4o turns
without fallback, and browser reconnection passed. Its default suite passed:
**3,136 passed / 40 skipped**, exit 0. Current candidate results and limits are
recorded in [the Phase A addendum](ALPHA_READINESS_DECISION.md#phase-a-core-integration-candidate).

The current integrated baseline is PR #352 and signed `v0.5.0-beta.11`; see the
[clean-main checkpoint](ALPHA_READINESS_DECISION.md#phase-b-merged-main-checkpoint).
Phase C1 has local GO for supervised operation of the frozen Windows candidate;
it is committed and pushed as `b8719fa2`, still unmerged. Hosted CI,
fresh installation, browser and live-model checks are unverified for C1. See the
[C1 evidence](evidence/integration_phase_c1_2026-11-24.json). The desktop counts
above remain a historical installation checkpoint.

## Operating Boundary

Guardian decides; Security enforces; Self-Incorporation executes approved
locked plans; Homeostasis verifies; Maintenance records. Do not connect this
candidate to production credentials, private user data, payment systems,
external automation targets or unattended networked control surfaces.

Keep signing, capability and Guardian enforcement enabled. Do not grant broad
capabilities or turn off signing to make a smoke check pass. Local profile
directories separate storage; they do not implement user/account authentication.

## Prerequisites And Preflight

Follow [DESKTOP_INSTALLATION.md](DESKTOP_INSTALLATION.md) in a new checkout and
virtual environment. Activate that venv in every command shell below:

```powershell
. .venv/Scripts/Activate.ps1
$env:HF_HOME = Join-Path (Get-Location) '.aetherra/model-cache'
python -m pip check
python tools/enforce_lock_sync.py --lock requirements.lock
```

Retain the same pinned-model cache path used during provisioning. The recorded
Windows run uses Python 3.13.7, Node 22.18.0 and a new model download. It does not
inherit shared packages. Other platforms, wheel-only installs and optional
plugin graphs require separate verification. Use the exact quality-tool versions
in the lock; keep the fixed baseline unchanged.

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
Default collection no longer stops on legacy imports. The current full default-suite result is recorded in the decision/evidence;
the following full-suite command is separate from the scoped selections.

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

The 2026-11-22 fresh-install suite used an immutable source copy and verified
pytest's `rootdir` against it. All 1,395 Python source/test files matched that
reviewed candidate byte-for-byte. Its result, log digest and skip reasons are
in the desktop evidence. Phase A uses 1,412 matching Python files and records
its results separately in [Phase A evidence](evidence/integration_phase_a_2026-11-23.json).
Diagnostic desktop attempts exposed metadata compatibility,
ancestor-path filtering and metrics listener isolation defects. A snapshot
assertion also caught Git's line-ending normalization before tests started;
the task harness now overlays exact source bytes. Superseded attempts do not
count as completed suite passes.

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
effect: verify Homeostasis `observe_only` and Self-Incorporation
`status=disabled`, `config_enabled=false`, `running=false`. Full launch now
defaults Self-Incorporation off and honors explicit enablement/configuration.
The generic registry's registration health is separate from effective mode.
No policy grants are added here; optional
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

## Integration Smoke (Phase A)

The supported alpha entry remains
`aetherra_os_launcher.py --mode full --no-gui --config PROFILE/launcher.json`.
The source-runtime verifier below calls that same CLI parser/main with those
arguments. It observes startup without replacing lifecycle work; offline mode
replaces only text generation with a responder that reads supplied evidence.
Memory, semantic retrieval, Guardian/Security, HTTP and process restart are real.
The public embedding model must already be provisioned in `HF_HOME`; no model
download is allowed during the offline check.

Run from the source checkout in the provisioned, credential-free environment:

```powershell
$integrationOutput = Join-Path $env:TEMP ('aetherra-integration-' + [guid]::NewGuid().ToString('N'))
python tools/alpha_integration_smoke.py --output $integrationOutput
Get-Content (Join-Path $integrationOutput 'summary.json')
```

The output directory must not exist. It contains synthetic prompts/provider
inputs, startup and final readiness/mode snapshots, SQLite records, Guardian
audit, runtime logs, exit receipts and probe timings. This is disposable test
data; do not adapt the recorder to private conversations. The verifier starts
three separate processes: write several competing facts, restart the same local
profile for paraphrased recall and an unknown attribute, then query a separate
empty profile. It binds the original opaque receipt to the persisted content,
retrieval IDs and actual generator input. It never retries chat writes.

For a live check, intentionally supply the approved `OPENAI_API_KEY` in the
current process through your secret mechanism, then use a **different new** output
directory:

```powershell
$liveOutput = Join-Path $env:TEMP ('aetherra-integration-live-' + [guid]::NewGuid().ToString('N'))
python tools/alpha_integration_smoke.py --live --output $liveOutput
Get-Content (Join-Path $liveOutput 'summary.json')
```

This forwards only that provider credential, selects gpt-4o and grants the
existing governed SDK caller access to `api.openai.com`. Other ambient credentials,
endpoint overrides and authority flags are removed; dotenv loading is disabled.
Guardian enforcement, strict capabilities/network policy and script/signing
checks remain enabled. Missing credentials, provider failure or fallback fail the
live gate. `generation.status=configured` proves selection only, not API success.

For a manually running full launcher, the exact core observation checks are
below. The ready Engine expectations assume a configured provider. The earlier
manual no-provider procedure should instead report degraded Engine readiness
and unavailable/not-selected generation; its fallback cannot pass a live gate.

```powershell
Read-AlphaJson '/health'                 # status=healthy: liveness only
Read-AlphaJson '/api/hub/readiness'       # readiness.readiness=ready; readiness.safe_for_clients=true
Read-AlphaJson '/api/kernel/readiness'    # readiness.readiness=ready; readiness.safe_to_schedule=true
Read-AlphaJson '/api/ai/status'           # readiness.readiness=ready; readiness.safe_for_requests=true
Read-AlphaJson '/api/guardian/status' $alphaHeaders # enabled/enforcing; audit.integrity_ok=true
Read-AlphaJson '/api/selfinc/status'     # disabled; config_enabled=false; running=false
Read-AlphaJson '/api/selfimprove/status' # autonomous_implementation_enabled=false
Read-AlphaJson '/api/homeostasis/status' # controller.mode=observe_only; zero actuator counters
```

Repeat these after initialization and restart. The smoke additionally polls the
four core routes **during** each chat, recording each response and latency.
Its `*-boot.json` records the launcher's component-level `core_readiness` and
separate `optional_services`; this is not a replacement authorization decision.
An inferred daemon/metrics Kernel status cannot certify scheduling. Starting,
missing or unselected core services cannot produce a ready startup announcement.
Optional registry health does not prove that an experimental loop has completed
useful work.

The compatibility Hub has eight bounded request workers. Only GET/HEAD on the
four exact core paths can overlap application work. Other routes, including
additional chat, may return retryable `503 hub_busy` with `Retry-After: 1`;
non-allowlisted read routes may therefore be temporarily unavailable. Transport
saturation before HTTP parsing attempts a best-effort `hub_saturated` response,
without a request trace; an ordinary client can instead see a connection reset
on Windows before reading it. Parsed `hub_busy` replies retain the configured
CORS policy and do not consume request IDs or read the prompt.
Only a matched Flask automatic OPTIONS response can pass busy admission;
custom OPTIONS handlers remain busy and are not dispatched.
There is no queued replay. Socket input/output stalls have a five-second limit;
this is not a five-second generation deadline. SSE disconnect/soft timeout does
not release mutation ownership while its generation worker remains active.

Shutdown stops admission and gives owned requests/workers five seconds to drain.
A missed budget is a failure, with resources retained. The normal CLI continues
waiting for admitted work, then completes teardown and exits **1** to report the
missed budget; it does not label that a clean bounded stop. A second explicit
force interruption can abandon work and is not a passing shutdown check.

The automated stop uses a harness SIGINT and checks process exit, shutdown
completion and persisted evidence. It does not claim interactive ConPTY
keyboard or browser verification. Use the browser procedure below if exercising
the Observatory. Local data directories provide storage isolation, not enforced
accounts. A fresh local port excludes external/shared-Hub reuse; those setups
remain unverified. Optional cognitive startup and experimental-module quarantine
remain Phase C work; no autonomous authority is enabled by this smoke.

Focused deterministic checks, in addition to the governance/continuity/signing
selections above:

```powershell
python -m pytest -q -o addopts= tests/unit/test_launcher_readiness.py tests/unit/test_kernel_readiness_sources.py tests/unit/test_engine_generation_readiness.py tests/unit/test_launcher_selfinc_modes.py tests/unit/test_hub_request_responsiveness.py tests/tools/test_alpha_integration_smoke.py tests/acceptance/test_launcher_active_shutdown.py
python tools/alpha_boot_validation.py
python -m Aetherra.integration_validation
python tools/verify_docs_consistency.py
```

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

## Supervised Use Exercise

Stage 21's next step after installation/launch acceptance is a repeatable period
of supervised use. Start with **15 observed minutes**: ten minutes in the first
process, a controlled stop/restart, then five minutes in the second process.
Startup, shutdown and failed observation attempts do not count toward that total.
This is a bounded exercise, not a load test or proof of long-running stability.

Use the verified installation and normal full-launch procedure above, a fresh
synthetic profile, and the scoped live-model policy. Record the source revision,
provider/model, process IDs and observation times. Stay present throughout; stop
on a safety-boundary failure, unexpected restart, failed core readiness, or a
configured-model fallback. Keep unavailable/degraded optional evidence visible.

1. Save the bicycle and music facts and their competitors from
   `tests/acceptance/test_personal_continuity.py` through `/api/ai/ask`.
   Inspect the initial acknowledgments as well as the storage receipts.
2. Verify both paraphrases and their retrieved/generation evidence IDs. Do not
   supply the store or prior conversation as additional prompt history.
3. Observe ten minutes. Ask an unsupplied-attribute question around the midpoint;
   a storage receipt for a question does not establish the detail it asks about.
4. Stop normally and verify exit zero and port closure. In the browser, verify
   unavailable state replaces the previous live state.
5. Start a new process with the same data directory and empty chat history. Ask
   both paraphrases, the unknown attribute and the Aetherra/Lyrixa identity question.
6. Observe five more minutes, repeat a recall near the end, then stop normally.
   Verify browser reconnection, ordinary-log privacy and unchanged source files.

In the observing PowerShell terminal, set the profile path to the disposable
directory created above. The default origin is port 3001; use 13301 for the
recorded alternate-port setup. This sampler writes only status, not dialogue:

```powershell
$alphaOrigin = 'http://127.0.0.1:3001'
$alphaHeaders = @{ 'X-Aetherra-Token' = 'synthetic-alpha-control' }
function Watch-AlphaWindow([int]$Seconds, [string]$Label) {
  $timer = [Diagnostics.Stopwatch]::StartNew()
  $paths = @('/health', '/api/hub/readiness', '/api/kernel/readiness',
    '/api/runtime-ui/status', '/api/homeostasis/status', '/api/guardian/status',
    '/api/ai/status')
  do {
    $data = @{}
    foreach ($path in $paths) {
      $data[$path] = Invoke-RestMethod ($alphaOrigin + $path) `
        -Headers $alphaHeaders -TimeoutSec 10
    }
    $h = $data['/api/homeostasis/status']
    $g = $data['/api/guardian/status'].guardian
    if (-not $h.orchestrator.initialized -or -not $h.orchestrator.running -or
        $h.controller.mode -ne 'observe_only' -or
        $h.actuators.actions_attempted -ne 0 -or
        $h.actuators.actions_executed -ne 0 -or
        $h.actuators.actions_blocked -ne 0 -or
        $h.orchestrator.restart_count -ne 0 -or
        $h.orchestrator.error_recovery_count -ne 0 -or
        -not $g.enabled -or $g.mode -ne 'enforcing' -or
        -not $g.audit.integrity_ok) { throw 'Stop: governance/lifecycle changed' }
    foreach ($path in @('/api/hub/readiness', '/api/kernel/readiness', '/api/ai/status')) {
      if ($data[$path].readiness.readiness -ne 'ready') {
        throw ('Stop: core readiness changed at ' + $path)
      }
    }
    $sample = [ordered]@{ label=$Label; elapsed_s=$timer.Elapsed.TotalSeconds;
      utc=[DateTimeOffset]::UtcNow.ToString('o'); guardian='enforcing';
      audit_intact=$true; homeostasis='observe_only'; actuator_actions=0 }
    $sample | ConvertTo-Json -Compress | Add-Content `
      (Join-Path $alphaProfile 'supervised-status.jsonl') -Encoding utf8
    if ($timer.Elapsed.TotalSeconds -ge $Seconds) { break }
    Start-Sleep -Milliseconds ([int][Math]::Min(30000,
      [Math]::Max(1, $Seconds * 1000 - $timer.Elapsed.TotalMilliseconds)))
  } while ($true)
}
Watch-AlphaWindow 600 'before-restart'
```

Complete the controlled stop, verify exit zero and port closure, then start a
new process with the same profile. Finish the restart conversation checks and
wait for initialized, running Homeostasis before executing the second window:

```powershell
Watch-AlphaWindow 300 'after-restart'
```

Resource observations are descriptive: record which process IDs were sampled,
RSS, threads and handles, and explicitly note short-lived children that exit
during sampling. A changing child-process set can change aggregate resource
totals. A short interval on a shared workstation cannot establish a leak-free
runtime or a performance SLA. Preserve incomplete/failed observations separately;
do not count them as completed windows.

The first recorded exercise completed 600 + 300 steady-state seconds with 12
JSON endpoints per sample (the seven above plus bootstrap, Maintenance,
Self-Incorporation status/audit and Security policy). A first cold recall after
restart took 63.603 seconds and interrupted status polling. Preserve such an
attempt separately, investigate before resuming, and never retry a timed-out
chat write automatically. Successful later samples do not erase that interruption.
Initial saved-fact acknowledgments also failed; check those replies in addition
to later recall. See [the decision](ALPHA_READINESS_DECISION.md) and
[recorded evidence](evidence/supervised_alpha_2026-11-22.json).

For the disclosure correction, run these focused offline checks using the
credential-free environment above and the provisioned local retrieval model:

```powershell
python -m pytest -q -o addopts= tests/unit/test_chat_disclosure_prompt.py tests/unit/test_chat_memory_retrieval.py tests/acceptance/test_personal_continuity.py
```

The new test captures actual generator input but returns a neutral sentinel;
it cannot establish natural-language behavior. For the separate live recheck,
post the exercise's disclosures through the same full-launch `/api/ai/ask` route
with gpt-4o configured. Also post `My dog's name is Luna. Can you remember that?`,
`My bicycle has a silver bell. What color is its frame?`, and
`Is my favorite soup lentil?`, then ask the dog's name and favorite soup.
Require a real acknowledgment, an unknown frame color, Luna recall, and no
promotion of the soup guess to a fact. Verify IDs, `llm.used=true` and
`llm.fallback=false`; manually inspect the wording. The recorded candidate
check used a separate fresh profile and 13 turns, not another 15-minute window.

Record findings and evidence in the existing readiness decision/checklist and
build dashboard. Keep Stage 21 active until its bounded use work is accepted;
do not advance Beta Hardening or extend authority merely because this exercise
passes.

## Observation And Maintenance Smoke (Phase B)

Use the same full launcher, disposable profile, scoped policy and strict flags
above. Keep `AETHERRA_HOMEOSTASIS_MODE=observe_only`, Self-Incorporation and HMR
disabled, and automatic implementation off. Default Homeostasis thresholds now
resolve from the package, so an empty profile does not need copied YAML files.
Aetherra remains the persistent system and Lyrixa her user-facing persona.

After startup, allow the existing 60-second metrics bridge to collect a fresh
sample. Inspect the ordinary Hub routes; these reads do not approve or execute:

```powershell
$homeostasis = Read-AlphaJson '/api/homeostasis/status'
$flow = (Read-AlphaJson '/api/selfimprove/status').homeostasis_flow
$maintenance = (Read-AlphaJson '/api/maintenance/status').maintenance
$inspector = (Read-AlphaJson '/api/runtime-ui/subsystems/maintenance').subsystem
$homeostasis.controller.mode
$homeostasis.actuators
$flow
$maintenance.service
$maintenance.recent_cycles | Select-Object cycle_id, proposal_id, status,
  observations, has_diagnosis, guardian_status, guardian_audit_id,
  security_enforced, can_execute, execution_status, verification_status
$inspector.metrics
```

Require `observe_only`, unchanged tuning parameters, zero actuator attempts and
executions, `homeostasis_flow.actions_enabled=false`, Self-Incorporation disabled,
and Guardian enabled/enforcing with intact audit. Inspect `status` and `reason`:
`nominal` means valid evidence did not warrant a proposal; missing producers or
failed delivery/storage must not be interpreted as successful routing. Registry
health and plugin/Hub service availability are registry-derived observations;
they are not measured request latency, WebSocket connectivity or GUI response
speed. Only finite fields actually collected in the fresh snapshot are eligible
for this proposal path. Historical numeric defaults remain compatible but are
excluded from new observation evidence by `measured_metrics` metadata.

The Hub heartbeat follow-up repairs the false stale registration observed in
the initial Phase B run. The full launcher now refreshes its actual local Hub
while that server's serving thread remains alive. Repeated requests and app
context teardown do not terminate heartbeat ownership; stopped, replaced,
external/proxy or unhealthy registrations receive no false refresh. Guardian
still authorizes each heartbeat. See [Hub lifecycle ownership](AETHERRA_HUB_API_REFERENCE.md#registry-heartbeat-ownership).

At the initial, 30-second and >210-second checkpoints, also inspect:

```powershell
$hubHealth = Read-AlphaJson '/health'
$hubReadiness = Read-AlphaJson '/api/hub/readiness'
$snapshot = (Read-AlphaJson '/api/homeostasis/metrics/snapshot').snapshot
$hubHealth.status
$hubReadiness.readiness.readiness
$hubReadiness.readiness.safe_for_clients
$snapshot.timestamp
$snapshot.hub_connection
$snapshot.raw_data.measured_metrics
```

For the verified local full-launcher profile, require fresh measured
`hub_connection=1`, continuing observation counts, HTTP health `healthy`,
readiness `ready` and `safe_for_clients=true`. The outer response `ok` is not
a readiness decision. A missing measurement is unknown. Registry liveness is still
separate from measured request latency or useful work. Other optional degraded
services remain visible; this change does not promote their status or renew
external Hubs. Repeat the same checks after restart in the same profile.

Validator effectiveness summaries can contain defaults or fallback estimates.
They remain visible through the existing validation status interface but are
excluded from Self-Improvement scalar history; they are not measured pressure.
Explicitly measured zero values are retained.

For a resulting Phase B cycle, require `status=proposed`, an observation,
diagnosis and genuine Self-Improvement proposal ID, `can_execute=false`, no
Guardian decision/audit ID, `security_enforced=false`, and no execution or
verification record. The Maintenance service must have its store configured,
autosave enabled and no persistence error before claiming restart durability.
If `service.load_failed` is true, stop the supervised exercise and preserve the
profile. Diagnose storage access or recover a known-good record file before
restarting through the normal launcher; embedded callers can explicitly call
`load_records()` after recovery. Failed restore blocks `save_records()` and
automatic proposal routing until reload succeeds. Repeated observations are
not recovery, and must not overwrite the original store. A failed save after a
successful load remains retryable through the existing proposal path.
Records are local coordinator evidence, not signed Guardian approvals. Its
existing JSONL file is under the profile's
`artifacts/maintenance/maintenance_cycles.jsonl`; the proposal is also persisted
in the profile's Self-Improvement database. Compare actual IDs, not only counts.

In the Observatory, Maintenance persistence must show `autosave_enabled` for the
configured profile; this describes configuration, not proven durability.
`error` makes status degraded. `autosave_disabled`, `no_store`, and `unknown`
remain distinct. Cycle counts and the latest cycle are explicitly in-process
evidence, including when a failed load leaves none visible. No raw store path
or exception detail is projected.

In the Observatory select Homeostasis, Maintenance, Guardian and Memory. Verify
mode and counters, the latest real cycle and proposal references, actual Guardian
configuration/integrity, and the explicit limit that continuity is not verified
by registry presence. The cycle/proposal/audit references are SHA-256 of each
actual ID, truncated to 16 hex characters. A missing record is distinct from an
unknown source. The inspector remains read-only and scrolls independently.

Repeat after at least 30 seconds and again beyond 210 seconds after startup.
The 30-second read may retain the same count with a 60-second bridge interval.
Require accepted-observation counts to increase across a full bridge interval
and by the later checkpoint. Require fresh registry heartbeats for Homeostasis,
Self-Improvement and Maintenance, including their aliases, plus the actual
launcher-owned `aetherra_hub` registration.
Then follow the browser stop/restart procedure below using the same profile.
Require a new process, preserved cycle/proposal IDs, no duplicate cycle for
repeated identical evidence, no authority increase, and unavailable/unknown UI
evidence while the runtime is stopped. A natural
threshold crossing is a recommendation trigger; it is not proof of a diagnosed
performance defect or successful remediation.

Run deterministic synthetic-pressure, failure, restart-deduplication and UI
checks from a fresh regression shell, without inheriting the live profile's
Guardian or runtime environment:

```powershell
python -m pytest -q -o addopts= tests/unit/homeostasis/test_launcher_hub_heartbeat.py tests/unit/homeostasis/test_launcher_observation_heartbeats.py tests/unit/homeostasis/test_proposal_flow.py tests/unit/homeostasis/test_measured_metrics.py tests/unit/homeostasis/test_profile_config.py tests/unit/homeostasis/test_observe_only_enforcement.py tests/unit/test_maintenance_cycle.py tests/unit/test_maintenance_service.py tests/unit/test_maintenance_store.py tests/unit/test_runtime_ui_maintenance.py
```

These tests use the real bridge, registry, launcher adapter, proposal database
and Maintenance store. Synthetic samples explicitly declare measured fields;
malformed, stale and unmeasured inputs are separate negative cases. They add no
special HTTP route or execution permission. The bounded full-launch acceptance
probe separately labels synthetic pressure, restores the previous snapshot and
correlates real records through Hub and Observatory. Retain its source, input,
HTTP snapshots, record IDs, process receipts and source hashes as evidence.
Run the existing offline and intentional live-provider continuity smoke as a
separate regression gate; a no-provider fallback cannot pass a live-model check.

## Consciousness Observer Smoke (Phase C1)

C1 has local GO for supervised operation on the frozen Windows candidate,
committed and pushed as `b8719fa2`, still unmerged. The
[acceptance evidence](evidence/integration_phase_c1_2026-11-24.json) records the
full suite (3,651 passed, 38 skipped, 5 passing subtests), boot/integration and
quality gates, two 215-second observer profiles and a three-process default
restart/profile check. Both signed audit chains pass; all processes exit zero
without force or generation fallback. Browser and live-model checks are
unverified for C1. Use synthetic data and the provisioned offline embedding model.
From the checkout, in the isolated regression environment, run:

```powershell
$observerOutput = Join-Path $env:TEMP ('aetherra-consciousness-' + [guid]::NewGuid().ToString('N'))
python tools/alpha_consciousness_smoke.py --output $observerOutput --observe-seconds 20
Get-Content (Join-Path $observerOutput 'summary.json')
```

The 20-second run is a quick check. For the extended gate, use a separate new
output directory and cross the registry's default 180-second stale threshold:

```powershell
$observerExtended = Join-Path $env:TEMP ('aetherra-consciousness-extended-' + [guid]::NewGuid().ToString('N'))
python tools/alpha_consciousness_smoke.py --output $observerExtended --observe-seconds 215
Get-Content (Join-Path $observerExtended 'summary.json')
```

After the smoke processes have exited, verify both signed audit ledgers from
this checkout. For the extended run, first set `$observerOutput = $observerExtended`.
The check uses each disposable profile's existing local audit key, removes only
inherited audit-secret overrides from its Python process, and prints no key or
ledger contents. A nonzero exit means verification failed.

```powershell
@'
import os
import sys
from pathlib import Path
from Aetherra.security.audit_ledger import SecurityAuditLedger

for name in ("AETHERRA_SECURITY_AUDIT_SECRET", "AETHERRA_SECURITY_STATE_SECRET"):
    os.environ.pop(name, None)
root = Path(sys.argv[1]).resolve()
for label in ("allowed", "denied"):
    ledger = SecurityAuditLedger(root / label / ".aetherra/security/audit.jsonl")
    if not ledger.verify_integrity(require_signed_records=True):
        raise SystemExit(1)
print("Signed audit verification passed for allowed and denied profiles.")
'@ | python - $observerOutput
```

The helper accepts 5–300 observation seconds. Require fresh owned Engine and
observer registry heartbeats and increasing completed ticks through the end of
the 215-second window; a short successful start does not pass this extended gate.
The accepted allowed window advanced completed ticks 1 → 214 and measured
events 4 → 856; the denied profile remained blocked at zero completed ticks.
After observer stop, ThinkStream was unavailable and Observatory status offline,
while ordinary chat still retrieved its saved evidence. Reproduce these checks
against the exact source under review; earlier receipts do not certify new edits.

The output directory must not exist. This invokes the real full-launcher CLI
with allowed and default-denied reflection profiles. Only text generation is
replaced with a deterministic context-derived responder. Retain source hashes,
policy/audit records, bounded endpoint snapshots, opaque memory evidence IDs and
process-exit receipts. Raw captured conversation data is synthetic test evidence,
not a pattern for ordinary private-conversation logging. This command verifies
Observatory HTTP payloads; it is not a browser or live-provider pass.

For manual launch, use the disposable alpha environment and an existing valid
scoped policy as in the integration smoke. Merge these root keys into that
profile's `launcher.json` while preserving its other settings:

```json
{
  "consciousness_enabled": true,
  "consciousness_mode": "observe",
  "consciousness_tick_hz": 1
}
```

Enablement is a JSON boolean, or `AETHERRA_CONSCIOUSNESS_ENABLED=1` when the root
key is absent. It defaults off. Only `observe` is accepted; `suggest`, `assist`
and `autopilot` do not grant observer authority. The rate must be finite and
between 0.1 and 5 Hz, default 1 Hz. Keep `AETHERRA_GUARDIAN_ENABLED=1`,
`AETHERRA_GUARDIAN_MODE=enforcing`, `AETHERRA_GUARDIAN_REQUIRE_POLICY=1`,
`AETHERRA_REQUIRE_CAPABILITIES=1`, `AETHERRA_SIGNING_STRICT=1`,
`AETHERRA_SCRIPT_VERIFY_STRICT=1` and `AETHERRA_AUDIT=1`; retain the alpha network
policy and other observe-only flags. These settings do not replace successful
core activation or a valid policy. Readiness must match the registry's actual
Memory and Engine implementations through their concrete launcher adapters;
foreign registrations are preserved, not replaced to make the observer ready.

The observer's status monitor keeps unchanged live heartbeats at 30-second
intervals by default, coalescing repeated updates while still handling lifecycle
transitions. Authorization uses one daemon worker slot per registry and requires
an audit receipt. Concurrent requests wait asynchronously for that slot; slot
acquisition and authorization share one total one-second deadline. Mutation and
broadcast remain on the calling event loop after ownership revalidation;
cancellation or timeout discards late results. A stuck worker retains its slot
instead of creating more workers. The post-authorization `apply_if` guard can
only refuse mutation, never replace permission.

The normal launcher refreshes its Engine on the existing 30-second lifecycle
cadence only while the concrete adapter's implementation is initialized, its
owned Kernel and linked local task are live, and the exact Engine and Kernel
registrations remain healthy. The same conditions are checked after audit before
mutation. Stopped, cancelled, replaced, mock or unhealthy owners receive no false
refresh. Verify freshness beyond 180 seconds separately from Engine generation
readiness; a heartbeat does not establish live-model availability. These repairs
do not grant authority or bypass Guardian and signing checks.

The allowed synthetic profile adds only these reflection rules to its existing
`allow` array; retain its registry, chat and shutdown rules and default deny:

```json
[
  {
    "requester": "consciousness:core",
    "subsystem": "consciousness",
    "action": "consciousness.micro_reflection_update",
    "target": "reflection:micro"
  },
  {
    "requester": "consciousness:core",
    "subsystem": "consciousness",
    "action": "consciousness.macro_reflection_update",
    "target": "reflection:macro"
  }
]
```

Missing permission or an unavailable signed-audit receipt must block reflection;
never disable enforcement to obtain a running status. No QFAC, continuity-save,
consolidation or actuation permission is added. The ordinary entry point is:

```powershell
Push-Location $alphaProfile
& $alphaPython (Join-Path $alphaRepo 'aetherra_os_launcher.py') --mode full --no-gui --config (Join-Path $alphaProfile 'launcher.json')
Pop-Location
```

Read the existing endpoints with the runbook's `Read-AlphaJson` helper:

```powershell
$think = Read-AlphaJson '/api/consciousness/state'
$observer = (Read-AlphaJson '/api/runtime-ui/subsystems/consciousness').subsystem
$think.runtime
$observer.metrics
```

For a running allowed observer require `runtime_state=running`, `running=true`,
`thread_alive=true`, `freshness=fresh`, increasing `ticks_completed`,
`ticks_attempted >= ticks_completed` and real `events_processed`.
`autonomy_mode=observe`; `persistence_enabled`, `qfac_persistence_enabled` and
`action_execution_enabled` must all be false. `readiness_verified=false` is
intentional: these counters do not certify cognition or broader alpha readiness.
The inspector exposes these bounded fields, not raw narrative, filesystem paths
or exception text. The ThinkStream endpoint contains the bounded current internal
health snapshot and never uses a previous pushed snapshot to hide an unavailable
owned observer. Blocked, failed, stale, stopping and stopped owners are not live;
the ThinkStream route returns HTTP 503 when unavailable.

The smoke's trusted local launcher instrumentation stops only its owned observer,
then verifies ordinary chat, actual retrieved IDs and generator input. It adds
no public stop route. Normal operator shutdown remains Ctrl+C in the launcher
terminal. Follow the browser procedure below to inspect Consciousness and compare
its metrics with HTTP, then verify unavailable state after stop. No browser pass
is implied by unit tests or successful HTTP reads.

C1 performs no persistent continuity read/write and has fixed 64-entry windows
for working events, narrative moments and active intents. State resets on restart.
C2 must implement safe isolated restore/write and accurate trust restoration;
the separate pending temporal observer is not activated. An intentional live
provider continuity check remains the separate Phase A procedure above; report
that evidence separately from this offline observer check. Signing stays strict.

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
Ctrl+C and stop the GUI dev server separately. The two fresh-install runtime processes exited 0 without force. Any teardown
warnings must be distinguished from the actual child process exit receipt.
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
The chat/legacy repairs are merged via PR #326; desktop repairs and clean-main
acceptance are complete via PR #327. Use the recorded source revision and locked
installation graph. Main passed 87 focused regressions, three additional live
gpt-4o turns, required production signing and published beta.6 signature/hash
verification. Wait for launcher initialization before running readiness probes;
HTTP availability can precede Homeostasis entering its running state.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
