# Alpha Readiness Decision

Updated: 2026-11-22 (America/Denver)

## Decision

**No-go for broader internal alpha operation pending candidate/CI acceptance.**
ALPHA-01 through ALPHA-06 are fixed locally. The repaired operator APIs pass
fresh-profile launch, steady-state and new-process restart checks. The final
local CI test selection passes with 1,916 passed and 8 skipped. Bounded,
supervised synthetic verification may continue. Broader acceptance still
requires a reproducible reviewed commit and current remote CI results. This
does not reopen personal continuity or accept Beta
Hardening, Production Readiness, or unattended operation.

- Decision owner: Aetherra Labs; technical assessment recorded by Codex at the
  owner's request. Remaining risks have not been accepted on the owner's behalf.
- Tested source: `codex/internal-alpha-verification`, working patch on
  `b1b7ae12ba4272cf630e989e3cf463a1b77b3624` (`v0.5.0-beta.2`). This is not an
  immutable released candidate or a new remote CI pass.
- Environment: Windows, Python 3.13.7 in an existing provisioned environment,
  Node 22.18.0; existing GUI dependencies from the locked install.
- Data: empty synthetic local profile, then the same persisted profile in a new
  process. No provider credentials, runtime doubles, or generation doubles in
  the manual CLI/browser smoke. Local directories provide storage isolation,
  not account isolation. Aetherra is the entity; Lyrixa her user-facing persona.
- Launch: `python aetherra_os_launcher.py --mode full --no-gui --config <profile>/launcher.json`.
  The real CLI, Hub, Kernel, Engine and memory participated. Guardian,
  capability enforcement, script verification and signing remained strict.

See [the checklist](ALPHA_READINESS_CHECKLIST.md) and
[exact operator commands](ALPHA_OPERATOR_RUNBOOK.md).

## Resolved Blockers

| ID | Fix | Retest evidence |
| --- | --- | --- |
| ALPHA-01 | Explicit observation policy wins over active settings; controller promotion, queued/direct actuators, correction, automatic recovery, supervisor restart and rollback honor it. Default active behavior remains available. | Registered live instance reports `observe_only`; attempted/executed/blocked actuator counts and automatic recovery counts remain zero during startup, steady state and restart. Guardian enforcing, audit integrity true. |
| ALPHA-02 | Runtime UI reads bounded existing registry/readiness evidence without starting services. Missing/stale evidence is unknown; health/activity are not invented. GUI rejects stale/malformed responses and expires stalled fetches. | Connected Engine is degraded, Kernel ready, unregistered services unknown; stopped runtime automatically becomes Runtime unavailable, all nodes unknown, Source Unavailable, no activity events. Reconnection restores real evidence. |
| ALPHA-03 | GUI maps canonical `event_type`/timestamp observations into visible titles and unique rendering keys. | Three observation titles render in the actual browser; no application console errors during connected, stopped or restarted states. |
| ALPHA-04 | The launcher uses the existing Homeostasis singleton; public supervisor transitions serialize runlevel enum values explicitly. Observation-only coordination preserves an operator's Disabled mode. | Real initialized/running instance is visible to Hub and registry; both startup orders, repeated load and observation-only coordination preserve the operator's pause. GET status returns HTTP 200 after actual runlevel transitions. |
| ALPHA-05 | The existing ledger/service accept optional action/status filters and limits; the authenticated API validates SQLite integer bounds and forwards all options. | HTTP 200 before/after restart, 401 without credentials, 400 for invalid limits; persisted-ledger regressions verify newest matching records, integrity and unlimited no-argument compatibility. |
| ALPHA-06 | Configured advanced-memory redaction hooks now govern persisted content and fail closed. Original authority and risk annotations remain enforced alongside the actual stored category/tags. | Real reopened SQLite and Fractal records contain transformed text; denied, failed or invalid hook output leaves both stores empty. Hooks cannot replace requester or manufacture trust/signing metadata. |

Status `active` can mean fresh registry presence or observed lifecycle, not a
measured health score. Each subsystem identifies its evidence and limitations.
Homeostasis lifecycle `active` is distinct from controller mode `observe_only`.
Bounded getters time out after 0.5 seconds with at most three status workers;
missing or invalid counters remain null rather than fabricated zero.

## Remaining Acceptance Work

| ID / gate | Observed finding | Required before broader Go |
| --- | --- | --- |
| Broad-suite evidence | Default collection succeeds and the final CI test selection passes (1,916 passed/8 skipped). The broader default execution timed out with 17 observed failures, including legacy contracts outside that selection. | Assess or explicitly accept the documented legacy limitations; do not call the default whole-repository execution a pass. |
| Candidate / CI | The scoped candidate is on `codex/internal-alpha-verification`; prior release checks predate it. | Review the published commit, run current CI and verify the resulting clean checkout before alpha acceptance. |

ALPHA identifiers are local findings, not claims that issues were opened.
Runtime and Self-Incorporation/Hub ownership fixes are complete locally. Release
maintainers own candidate/CI acceptance. No current remote result is implied by
the local regression or launch results.

## Verification Evidence

The full launch/browser and 1,916-test results below describe the preceding
source snapshot. Publication review then found and repaired two further gaps:
controller `start()` directly assigned Active before its first control step,
and malformed scene elements could reach the browser renderer. Execution guards
already blocked observation-only actuation, but the startup mode was incorrect.
Startup now uses the existing policy-aware setter. The browser validates the
scene geometry and rendered text before accepting an API response.

The real startup regression failed six observation cases before the fix and
passed afterward, including component and standalone entry points and the
unchanged active default. The malformed-scene regression reproduced acceptance
of a null scene node before the fix. Fresh publication checks pass: 81 focused
follow-up tests; 124 Homeostasis/Runtime UI/signing tests; and 18 GUI tests,
build and lint. Counts overlap and must not be summed. The earlier browser
smoke is not relabeled as a new browser check of these final review changes;
current commit CI and clean-checkout acceptance remain separate gates.

| Check | Result | Boundary |
| --- | --- | --- |
| Boot validation / Integration Validation | PASS, 4 / 5 checks | Bounded contracts, not substitutes for the full launch. |
| Focused alpha safety selection | PASS, 194 tests | Guardian, Security, ingress, Kernel, registry, integration and Runtime UI. |
| Final Homeostasis + Runtime UI selection | PASS, 112 tests | Includes final mode/counter evidence and review fixes. Overlaps the safety selection; counts are not additive. |
| Homeostasis/Guardian owner selection | PASS, 89 tests | Includes automatic recovery, rollback, retained monitoring and existing active behavior. |
| Personal continuity acceptance | PASS, 3 tests | Real persistence/retrieval/restart; only generation is deterministic. No new live-model claim. |
| Release, Hub and discovery signing | PASS, 13 tests | Signing implementation and enforcement tests; keys/workflows/policy were not changed. |
| GUI tests, build and lint | PASS, 17 tests | Large bundle and THREE.Clock deprecation warnings remain. |
| Full CLI fresh profile and restart | PASS, Hub/Kernel ready, Engine degraded without model | Actual Homeostasis mode/counters sampled at startup and steady state in both processes. |
| Actual browser via Vite 3000 to full Hub 3001 | PASS, connected/degraded, stopped, reconnected | Read-only controls; no application console errors. Expected proxy connection failures during deliberate shutdown. |
| Unauthorized chat / disabled Kernel control | HTTP 403 / 501 | Ingress rejection and disabled control; no live privileged mutation authorized. |
| Authenticated no-provider chat | HTTP 200, `llm.used=false`, `fallback=true`, `llm_unavailable` | Explicit Lyrixa unavailable-model reply. This is not a real-model pass. |
| Python fixed-baseline quality, docs and hygiene | PASS | Zero new/edited Python style violations; legacy baseline unchanged. Docs consistency, Markdown and website-artifact checks pass. |
| Default pytest collection | PASS, 3,093 collected after final follow-up tests | Corrected obsolete Hub import; retired interactive Qt demo; manual STORM probes no longer run or change environment at import. Collection-only coverage output is not execution coverage. |
| Full default execution | INCOMPLETE, timed out after 900 seconds | 1,027 observed passes, 17 observed failures; named below. No complete coverage result. |
| Repaired operator APIs | PASS, 14 ownership/coordination/transition + 18 audit regressions | Real components and SQLite; existing security interfaces remain in use. |
| Maintenance guard fixtures | PASS, 6 tests including policy units | Valid workflow actions and real generated rollback tokens replace unsupported historical fixtures. |
| Isolated signing rerun | PASS, 13 tests | Includes discovery signing; broad-run shared state did not reproduce in isolation. |
| STORM routing/import and adjacent memory regressions | PASS, 53 tests; 3 skipped | Real persisted records for baseline/hybrid/disabled/shadow routes; pure routing is not a claim of successful native STORM retrieval. |
| API/routing/maintenance/continuity checkpoint | PASS, 47 tests | Final token-header fixtures, ownership/transition serialization, real ledger filters, routing and three process-restart continuity cases. Precedes the additional Disabled-mode and policy-hook regressions; overlaps other selections. |
| Allocation tracing lifecycle | PASS, 5 tests | Measurement stops only tracing it started, including on failure; caller-owned traces and the heuristic threshold remain unchanged. |
| Configured memory policy and adjacent regressions | PASS, 52 tests | 21 new persistence/default-compatibility cases plus existing typed/policy, Guardian and recall routing tests. This is not a claim of universal redaction or pure-STORM retrieval. |
| Final combined follow-up | PASS, 81 tests | API ownership/audit, configured policy, recall routing, isolated tracing, maintenance and all three continuity restart cases, on the final source. Overlaps the other selections. |
| Final local CI test selection | PASS, 1,916 tests; 8 skipped | Fresh source-only snapshot, independent test state, consistent UTF-8; `tests/capabilities tests/unit tests/integration`. Python 3.13.7/Windows, not a remote Python 3.11 workflow or coverage/package acceptance. |

### Compact Full-Runtime Trace

```text
working patch on b1b7ae12; empty final-profile; full CLI PID 27280
  07:23:04 UTC: Hub ready; Kernel ready, cycle 19
  registered homeostasis_system: running=true; mode=observe_only
  actuator attempted/executed/blocked = 0/0/0; recoveries/restarts = 0/0
  07:23:57 UTC: steady-state mode/counters unchanged; Kernel cycle 65
  Engine degraded -> browser Degraded systems visible, Source Runtime API
  synthetic chat -> explicit llm_unavailable fallback
  memory record d2121ab46519e89275932177a60cfbfc -> lyrixa_memory.db
  Ctrl+C -> child exit 0; Hub port closes
  browser poll -> Runtime unavailable; every node unknown; event feed empty
same profile; new full CLI PID 18976; empty process chat history
  Hub/Kernel ready; initial Kernel cycle 5; Engine still degraded
  mode observe_only; zero actuator attempts/executions at startup + steady state
  prior opaque memory record still present in SQLite after restart
  browser reconnect -> degraded Engine evidence and three observation titles
  Ctrl+C -> child exit 0; Hub closes
```

The persisted ID above proves storage across this manual restart, not semantic
recall by an unavailable model. The separate three-test continuity acceptance
suite supplies retrieval/answer regression evidence. Raw synthetic artifacts,
HTTP results, console captures and screenshots remain ignored under
`.pytest_tmp_alpha_fix/`; they are not ordinary product logs or release assets.

### Operator API Follow-up Trace

```text
fresh synthetic profile; full CLI PID 41932; loopback port 3021
  07:54:32 UTC -> Homeostasis status 200, initialized=true, running=true
  controller=observe_only; actuator attempted/executed/blocked=0/0/0
  07:55:42 UTC -> steady-state mode and counters unchanged
  Self-Incorporation audit -> 200 JSON, empty persisted profile summary
  Guardian enforcing, audit integrity true; Ctrl+C -> exit 0
same profile; full CLI PID 48948; separate loopback port 17291
  07:57:50 UTC -> both repaired APIs 200; mode/counters unchanged
  07:59:59 UTC -> direct Homeostasis status still 200 with zero attempts
  missing audit credential -> 401; invalid/out-of-range limit -> 400
  filtered audit query -> 200; Ctrl+C -> exit 0
```

On the longer restart sample, the registry heartbeat became stale and the
Observatory correctly reported Homeostasis unknown; the repaired direct status
API still reported its actual running instance. This is a registry heartbeat
coverage limitation, not evidence of measured health. The GUI source was
unchanged in this follow-up; the preceding browser evidence remains separately
dated and was not relabeled as a new browser pass.

The final reviewed source snapshot was also launched from a new synthetic
profile on loopback port 17291, then stopped and restarted with the same data:

```text
final source snapshot, full CLI PID 50936
  startup at uptime 25s: all 12 inspected APIs return 200
  08:47:40 UTC, uptime 114s: observe_only; actuator counts 0/0/0
  Guardian enabled/enforcing; recoveries/restarts 0/0; Ctrl+C -> child exit 0
same profile, new full CLI PID 38840
  08:49:50 UTC, uptime 66s: all 12 APIs return 200; mode/counters unchanged
  audit: no credential 401; zero/out-of-range limits 400; filtered read 200
  08:51:18 UTC, uptime 154s: all 12 APIs still 200; mode/counters unchanged
  Guardian enabled/enforcing; Ctrl+C -> child exit 0
```

Engine degradation without model credentials remained visible. This final
repetition verifies launch, status and restart behavior; the separate final
81-test selection verifies continuity retrieval and answers across restart.
Final source artifacts are isolated under `.pytest_tmp_alpha_followup/`.

### Broad Test Run And Follow-up

The default run unblocked collection, then exposed the following failures
before its 900-second limit. This list records observations; it does not assert
that every failure was a production regression or has been resolved.

```text
tests/acceptance/test_maintenance_security.py::test_guard_policies_actuator_frequency_rejects_second_action
tests/acceptance/test_maintenance_security.py::test_guard_policies_rollback_cascade_rejects_third
tests/capabilities/test_hub_metrics_observability.py::test_metrics_chunks_total_increments_with_chunking_stream
tests/capabilities/test_static_security_scan.py::test_static_security_scan_baseline
tests/capabilities/test_storm_acceptance.py::TestSTORMAcceptanceCriteria::test_storm_respects_recall_strategy_parameter
tests/consciousness/test_active_inference_integration.py::test_active_inference_rationale_components
tests/consciousness/test_identity_unified.py::test_who_am_i_unified_identity
tests/storm/test_storm_security.py::TestSTORMSecurityGates::test_policy_violation_prevents_storage
tests/storm/test_storm_security.py::TestSTORMSecurityIntegration::test_full_remember_recall_security_flow
tests/test_aether_workflow_additional_paths.py::test_tiny_timeout_fast_path
tests/test_discovery_signing.py::test_discovery_registers_signed_manifest
tests/test_headers_and_expiry.py::test_headers_on_ask_and_stream_endpoints
tests/test_headers_and_expiry.py::test_headers_on_stream_get_alias
tests/test_headers_and_expiry.py::test_expiry_nonstream_and_bridge_409
tests/test_headers_and_expiry.py::test_expiry_stream_post_emits_error_and_final
tests/test_headers_and_expiry.py::test_expiry_stream_get_emits_error_and_final
tests/test_headers_and_expiry.py::test_expired_request_writes_fallback_dlq_file
```

The two maintenance failures reproduced on the unchanged release and are fixed
by valid, isolated fixtures. The stream metric failure was caused by the
verification Hub sharing test port 3021; the entire module passes on distinct
ports. The security scan flagged synthetic literal Bearer examples in new
tests; fixtures now use the supported token header and the unchanged scanner
passes. No scanner allowlist or signing policy was relaxed. Discovery signing
passes its isolated rerun. Other broad-run failures are not silently counted as
passing; current CI-directory verification is recorded separately.

An intermediate CI-directory run exposed a process-wide fragmentation heuristic
delta of 0.272 versus the unchanged 0.25 threshold; the same 1,500-iteration
workload passed in a fresh process at 0.111. That capability check now measures
the real workload in a fresh process with all assertions retained. The probe
also restores tracing it owns, avoiding global tracing leakage into later tests.
No quality threshold, test exclusion, signing policy or legacy baseline changed.

A complete intermediate run of the CI test directories recorded **1,914 passed,
8 skipped and 2 failed**. Its failures were:

```text
tests/capabilities/test_storm_acceptance.py::TestSTORMAcceptanceCriteria::test_storm_latency_acceptable
tests/unit/test_precommit_block_artifacts.py::test_hook_blocks_both_original_pattern_sets[nested/café report.json]
```

The STORM benchmark inherited 25 records while intending to measure 20. Each
acceptance case now starts with fresh storage and closes its database handles;
the benchmark verifies 20 core and 20 Fractal records before timing the same ten
queries against the unchanged 500 ms limit. Isolated runs passed (default:
7 passed/3 skipped; enabled: 9 passed/1 skipped). Both a fresh case and the
reproduced shared-data pair measured below 105 ms, so the earlier 502.59 ms
outlier's cause is not established by the contamination finding alone.

The artifact hook correctly blocked the Unicode filename; the Windows test
process decoded its child's UTF-8 output using a different locale encoding.
The verification environment now uses `PYTHONUTF8=1` consistently with
`PYTHONIOENCODING=utf-8`. All 15 unchanged artifact-hook tests pass. No artifact
protection code or assertion was weakened. The subsequent complete selection
passed **1,916 tests with 8 skipped**, exit 0, in 989.96 seconds of pytest
execution. Its final source-only snapshot includes the reviewed test fixture;
all 851 production-code files match the source used for the successful final
launch and restart. The eight skips retain existing optional-component and
feature-availability conditions; no new test exclusion was added.

Isolated comparison against untouched `b1b7ae12` reproduces the same two
consciousness failures and six request-header/expiry failures. The identity test
uses an absent root-relative model path; explicitly selecting the shipped
`config/self_model.json` passes. The rationale assertion compares evaluations of
different actions. The header/expiry cases expose existing ASK/stream deadline
and response-header gaps; the bridge success case passes. These findings remain
outside this runtime repair and are not accepted as passing contracts. The tiny
workflow timeout test passes in isolation on both sources.

Manual STORM probes had mutated environment variables during doctest collection.
Their import side effects are removed. A minimal existing-interface dispatch fix
also honors documented explicit base/pure/hybrid recall strategies. Default,
disabled and shadow routes retain their behavior. Pure STORM's pre-existing
candidate-adapter mismatch is not fixed or counted as successful recall here;
this alpha launch uses the default non-STORM path.

The configured advanced-memory hook defect also reproduced on untouched
`b1b7ae12`. It is repaired at `AetherraMemoryEngineAdvanced.remember`'s existing
persistence boundary. No redactor is enabled by default, and the launcher's
preferred direct core-memory adapter remains unchanged. Release signature
verification is separate from the existing memory signing metadata contract;
neither interface was replaced or relaxed. A legacy STORM integration assertion
still inspects a copy of metadata taken before its own hook returns, rather
than persisted output. The new reopened-storage regressions supply the latter
evidence without claiming that flawed assertion passes.

### Workspace Preservation

The original workspace retains its exact staged diff, Git status, HEAD and
branch. All 1,952 snapshotted tracked/untracked file contents are unchanged.
Only the scoped alpha implementation, tests and documentation are included in
the publication candidate. Runtime profiles, logs and test artifacts remain
ignored. The original workspace's staged diff and file contents are checked
again during publication. Verification servers were stopped.

### Signing And Remote Evidence

The prior [CI Quality Gates run](https://github.com/AetherraLabs/Aetherra/actions/runs/44690950600)
and [Release run](https://github.com/AetherraLabs/Aetherra/actions/runs/44692377747)
passed on the release's code parent, including signed bundle/manifest checks.
They do not verify this patch. No signing key, release workflow or enforcement
setting was weakened, and no new secret is needed for these offline checks.

Other limits: no fresh model run, soak/load test, clean desktop dependency
install, enabled privileged mutation or production/network deployment.
The full launcher still logs a watchdog teardown error before successful
shutdown; a short smoke does not establish long-running shutdown reliability.
Optional capability denials, relative-config defaults and deferred legacy
package findings remain documented limits. Earlier gpt-4o continuity evidence
remains in [PERSONAL_CONTINUITY.md](PERSONAL_CONTINUITY.md).

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
