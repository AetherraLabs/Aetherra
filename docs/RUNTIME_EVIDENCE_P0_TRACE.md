# P0 — QFAC metrics and Self-Incorporation reachability

Reviewed 2026-11-27 at main `3253893604a5cf3fb0417f95de3acf51131650f1`.
This is the first bounded investigation under the [evidence integrity plan](RUNTIME_EVIDENCE_INTEGRITY_PLAN.md).
It completes these two traces, **not the whole-repository P0 inventory or a new alpha GO**.
Runtime implementations, authority policies, CI deadlines and release signing are unchanged.

## Evidence and reproduction

- [Structured inventory and dependency edges](evidence/runtime_evidence_p0_inventory.json).
- [Sanitized observations, actual exits and retained artifact hashes](evidence/runtime_evidence_p0_2026-11-27.json).
- [Disposable diagnostic probe](../tools/inspect_runtime_evidence_p0.py).

Using the provisioned Windows Python 3.13.7 environment, from the checkout root:

```powershell
$py = 'D:/Aetherra Labs/.codex-c2b-execution-20261125/runtime/Scripts/python.exe'
& $py tools/inspect_runtime_evidence_p0.py --output ../p0-evidence-new
& $py -m pytest -q -o addopts= `
  tests/unit/test_selfinc_integration_guardian.py `
  tests/unit/test_self_incorporation_security.py `
  tests/unit/test_metrics_read_only_snapshot.py `
  tests/capabilities/test_qfac_validator_shadow_schema.py
```

The output directory must not exist. Other provisioned environments can use `python`.
Each child calls the real launcher CLI `main()` with `--mode full --no-gui --config <fresh-profile>/launcher.json`.
The existing alpha smoke helpers create isolated home/state/policy directories, deny external network/subprocess calls,
use an offline generation double, enforce Guardian/default-deny capabilities, disable HMR, and keep both signing flags
strict. No chat or real-model pass is claimed; internal boot generation may call that double.
The harness only observes lifecycle work, registers a labeled synthetic validator through the existing registry,
and invokes existing service methods. It creates no alternate runtime route or authority.

Three full-launch profiles were exercised: enable flag unset, `1`, and `0`. All use `AETHERRA_PROFILE=test`,
`SELFINC_STRICT=1`, strict trust mode, network/capability enforcement and signing. The unset profile uses
`NO_FAKE_DATA=1`; the explicit profiles use `0`, demonstrating that full mode itself activates the no-fake branch.
This is a strict-flags test profile, **not a native production-profile acceptance run**.

## RI-012 — QFAC metric provenance

Confirmed record: [DEV-QFAC-001](DEVELOPMENT_ISSUES.md#dev-qfac-001--validator-metric-provenance),
[GitHub #389](https://github.com/AetherraLabs/Aetherra/issues/389).

Actual dependency path:

```text
CLI main -> launch_full_os (full/no-fake normalization)
         -> process environment: VALIDATOR_FAKE=1; override counts removed
GET /metrics -> build_all_metrics_lines -> registry_client.get_service("qfac_validator")
             -> get_status() if present -> override branch -> Prometheus response
```

| Input to the real Hub route | Observed green / blocked | Evidence meaning |
| --- | --- | --- |
| No validator registered at boot | 0 / 0 | Missing source, not measured zero |
| Synthetic registered validator supplies 17 / 4; normal full flags | 0 / 0 | Confirmed reachable override |
| Same fixture; only override flag changed to 0 | 17 / 4 | Registry/route can carry actual supplied values |
| Same fixture throws; override remains 0 | 0 / 0 | Failure also loses provenance |

Every scrape above returned HTTP 200. The fixture flag change is a labeled diagnostic control inside the disposable
child and is restored afterward. It is not an operator workaround or real validator backend verification.
No owned `qfac_validator` producer registration was found in launcher/Kernel/Hub/runtime roots; all three children
confirmed absence before injection. `qfac_memory_system` is a separate service. No owned Observatory or runtime
control consumer of these two validator counters was found in the audited roots; external Prometheus consumers remain
unknown. Thus loss of real backend measurements and an authorization effect are **not established**.

Static optional-profile follow-up: early QFAC memory-stub selection also accepts `test`/`ci` profiles independently
of `FAST_STUB=0`, if a QFAC-enable variable is truthy. That optional memory service was not enabled in this probe;
full/dev/optional-feature matrices remain required. Do not generalize validator findings to all QFAC memory behavior.

## RI-013 — Verification evidence and action authority

Confirmed record: [DEV-SELFINC-001](DEVELOPMENT_ISSUES.md#dev-selfinc-001--verification-and-planning-trust),
existing [GitHub #67](https://github.com/AetherraLabs/Aetherra/issues/67).

The real service discovered one harmless unsigned utility, classified it, evaluated it and persisted a SafetyIndex
row. Classification/evaluation were **explicit internal calls by the probe**: startup only triggered discovery,
and no owned automatic evaluator caller or Hub classification/evaluation route was found. Both enabled registered
instances began with zero classifications. A registry `handle_message` dispatcher supports status/proposals,
not an evaluator command. This distinguishes available internal methods from automatic normal-chat behavior.

```text
trigger_scan -> CodeIndex -> explicit trigger_classify -> ClassificationIndex
 -> explicit trigger_security_eval -> SecurityGate.evaluate_security
 -> path-derived verification / tier -> SafetyIndex SQLite
 -> _run_integration_planning -> eligible tiers -> action target / priority
```

Native Windows produced `verified=false`, `signature_present=false`, `signature_valid=false`, but tier `TRUSTED` and
a high-priority `import_utility` plan. Reopening the SQLite index returned the same decision; a second evaluation
processed zero files because the existing non-quarantined row was reused. This is persistence across a new index
object, **not a process-restart test**. Existing decisions lack the demonstrated fresh signature evidence required
by #67's strict artifact contract.

One inspectable trace from the explicit-enable run:

```text
unsigned fixture -> sha256:ae416f1cd9dfc11105959301cfec9348b4144f7bda7a13d35bf57bb385cc85b4
SafetyIndex: verified=false, signature_valid=false, trust_tier=trusted
plan 1ab6b9fe -> same file_id -> import_utility, priority=high
unapproved service apply -> newly generated plan b27fd73f -> Guardian deny -> execute_plan calls=0
```

Windows path separators prevented the legacy verifier's forward-slash substring match in this case. A separately
labeled `PurePosixPath` model of the same verifier returned `verified=true` while reporting no signature. This is a
confirmed path-model contradiction plus source tracing, **not native Linux execution** or a Linux launch pass.
The trust tier also affects conflict resolution, action priority and ethics inputs; planning eligibility is not
permission to execute.

Authority was traced separately:

```text
POST /api/selfinc/apply -> control authentication -> disclosure gate
 -> registered service.trigger_integrate -> plan/scope lock
 -> Guardian intent + capability checker + approval -> ethics/rollback constraints
 -> CoreIntegrator.execute_plan -> validate_plan_scope_lock -> downstream action
```

The tested unauthenticated HTTP request returned 401. The default free disclosure tier rejected authenticated mutation
with 403. A separate direct unapproved service request reached real Guardian and returned `guardian_denied`;
a fail-before-mutation tripwire recorded zero calls to `execute_plan`. Apply generates a fresh plan from the same
persisted evidence; its ID differs from the inspected planning pass. This does not establish behavior under every
approved policy, downstream action or artifact type. Existing focused tests cover approval, scope expansion and
capability/signature helpers, but do not prove the legacy evaluator supplies cryptographic evidence.

A second internal caller, `integrate_with_canary`, also reads the plan and checks HMR availability, rollback support
and `_guardian_preflight_canary` before its execute call. No owned external caller was found; HMR remained disabled
and canary execution was not tested here. The self-improvement Hub uses `handle_message("selfimprovement.proposal", ...)`,
a separate authenticated proposal path rather than the legacy artifact evaluator. No equivalence between their
verification evidence is assumed.

Read-only presentation is source-traced separately: `App.tsx::loadBootstrap` requests `/api/runtime-ui/bootstrap`,
whose payload uses `collect_runtime_ui_system_status` / `_observe_service` to read the registered instance and map
its observations into Observatory nodes. Maintenance status also reads the registered service. These are display
consumers; the UI does not grant execution authority. This is static reachability, not a browser rendering check.

The separate `SelfIncorporationSecurity.verify_signature` helper rejected this unsigned fixture under strict flags.
It is not called by the traced legacy evaluator/planner/apply path; proposal authentication uses the security object
separately. Its companion-file SHA-256 comparison is not keyed signature authentication. Existing script HMAC and
plugin Ed25519 interfaces, and release Ed25519 verification, are distinct authorities; no release-signing result
validates legacy planning trust. P1 must reuse supported verification interfaces and preserve Guardian/approval gates.
No unapproved execution bypass is claimed; sensitive authority findings follow [SECURITY.md](../SECURITY.md).

## Additional finding — Two startup owners disagree

Confirmed record: [DEV-SELFINC-002](DEVELOPMENT_ISSUES.md#dev-selfinc-002--startup-ownership-and-opt-in),
existing [GitHub #42](https://github.com/AetherraLabs/Aetherra/issues/42).

| Enable flag | Launcher enabled | Registered enabled | Same instance | Hub status |
| --- | --- | --- | --- | --- |
| Unset | false | true | false | healthy, running |
| 1 | true | true | true at observation | healthy, running |
| 0 | false | false | true | disabled, stopped |

The launcher defaults to disabled, but Kernel `_enqueue_self_incorporation_startup` defaults to enabled and
`_ensure_self_incorporation_registered` constructs/re-registers a second instance. The kernel then scans through the
registry. With explicit `1`, the launcher later re-registers its own enabled instance. The unset case therefore
contradicts the launcher-only opt-in conclusion in #42's historical source review. Explicit `0` contained discovery
in the measured profile; preserve it in supervised verification until ownership/defaults are corrected.

## Verification, retained failures and next gate

- Focused existing tests: **62 passed**, exit 0. The first selection used a nonexistent test path and exited 4;
  no tests ran in that attempt. It is a harness-selection error, not an engineering defect.
- Initial two-profile diagnostic: both exited 0. Refined three-profile diagnostic: first two exited 0; explicit-disable
  observations completed, then its process required a kill after the 60-second shutdown limit (exit 1).
  Its worker receipt said zero before the process settled. That receipt alone is insufficient shutdown evidence.
- Final repeat added a 50-second stack-dump watchdog without changing any runtime or shutdown deadline. All three
  processes exited 0 in approximately 10 seconds each; no stack dump fired. The earlier delay remains unexplained.
  Logs/hashes from every run are retained. No common cause with DEV-HOMEOSTASIS-001, DEV-CI-001 or CKPT records is proven.
- Ruff, Black, isort and Markdown checks passed; repository documentation consistency exited 0.
- Native Linux, production/dev/optional-QFAC profiles, real validator, approved integration, browser, live model and
  physical keyboard checks remain unverified. No full-suite, fresh-install or new CI run is claimed for this trace.

The diagnostic tool records observations rather than tests that institutionalize the bugs. The three confirmed
records remain OPEN. Prioritize Self-Incorporation opt-in/trust-evidence corrections and the bounded QFAC metric
correction as separate P1 changes; authority review remains a gate before P2 embedding migration. Continue broader
P0 inventory. No historical unknown-cause record, alpha limitation or signing requirement is closed or relaxed.
