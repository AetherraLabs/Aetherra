# Alpha Readiness Checklist

Updated: 2026-11-22

Candidate: working patch on `b1b7ae12ba4272cf630e989e3cf463a1b77b3624` (`v0.5.0-beta.2`).
Decision: **No-go for broader internal alpha operation**. ALPHA-01 through
ALPHA-06 are fixed locally. Full CLI restart and operator API checks pass;
the preceding browser and safety evidence remains applicable. Reviewed-commit
and current-CI acceptance remain open.
See [ALPHA_READINESS_DECISION.md](ALPHA_READINESS_DECISION.md) for evidence,
limitations, owners and retest conditions.

This checklist defines what must be true before Aetherra should be called ready
for an internal alpha. It is not a marketing launch checklist. It is a
technical and safety gate for proving that the current functional foundations
operate together as a bounded cognitive operating layer.

Alpha readiness means:

- Aetherra can boot through a known runtime path.
- Core systems expose understandable status.
- Privileged action paths route through Guardian and Security.
- Self-modifying paths remain proposal, approval, execution, rollback, and
  verification separated.
- The Runtime UI can observe the system without becoming an unsafe control
  surface.
- Repository contents are clean enough that source, docs, tests, and generated
  artifacts are distinguishable.

## Gate 1: Identity And Scope

Status: Reviewed for this candidate; docs consistency passes.

Required before alpha:

- `docs/WHO_IS_AETHERRA.md` defines the project identity.
- `README.md` explains that Aetherra is the entity and Lyrixa is the persona.
- `docs/ACTIVE_SYSTEMS.md` and `docs/SYSTEM_INDEX.md` match current system
  status.
- The project explicitly states that Aetherra is not AGI, sentient, or
  autonomous without limits.
- The core lifecycle is documented as observe, understand, propose, review,
  approve, execute, verify, and learn.

Validation:

```powershell
python tools\verify_docs_consistency.py
```

## Gate 2: System Foundation Status

Status: Documented foundations reviewed; not a claim of integrated alpha readiness.

Required before alpha:

- Security is functional complete.
- Guardian is functional complete.
- Engine is functional complete.
- Homeostasis, Self-Improvement, Maintenance, Self-Incorporation, Memory,
  Kernel, Agent System, Aether Script, Integration Validation, Runtime UI,
  Lyrixa, Hub, Artificial Intelligence, Consciousness, Coding, Chat, and AI
  Trainer are functional foundation complete.
- No system is marked `Partial` or `Planned` in `docs/SYSTEM_INDEX.md`.
- Each system document satisfies the Understanding Rule:
  - what it does
  - why it exists
  - what authority it owns
  - what authority it does not own
  - how it fails
  - how it interacts with other systems

Validation:

```powershell
python tools\verify_docs_consistency.py
```

## Gate 3: Safety And Governance

Status: Bounded observation-only retest passes; ALPHA-01 resolved locally.

Guardian reports enabled/enforcing and audit integrity true. Strict capability
denials, unauthorized chat rejection and disabled Kernel controls were observed.
The registered Homeostasis instance stays in observe_only with zero actuator
attempts/executions through startup, steady state and a new-process restart.
No broad capabilities or signing exceptions were added. Self-Incorporation
audit inspection now passes authentication, filtering and persisted-ledger
regressions (ALPHA-05); live privileged mutation was not exercised.

Required before alpha:

- Guardian can allow, deny, and require approval for privileged intent.
- Security can enforce capabilities, sandbox, signing, network, and audit
  boundaries.
- Denied privileged actions fail before mutation.
- Approval-required flows do not execute without a valid approval.
- Guardian and Security decisions are audited without exposing raw sensitive
  payloads.
- Self-Improvement remains proposal-only.
- Self-Incorporation validates approved plan scope before execution.
- Non-dry-run Self-Incorporation mutation has truthful rollback support or
  fails closed before mutation.

Validation:

```powershell
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_safety tests\unit\test_selfinc_integration_guardian.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_validation tests\unit\test_integration_validation.py
```

## Gate 4: Runtime Boot Path

Status: Full CLI boot and restart demonstrated, with documented degradation.

Hub and Kernel reported ready in both new processes. Engine reported degraded
without a configured provider. Both Ctrl+C shutdowns exited 0; a watchdog
teardown error remains a documented limitation. Optional service denials and
relative configuration defaults are not equivalent to all systems being ready.

Required before alpha:

- A documented launcher path starts the intended alpha runtime.
- Kernel starts and exposes readiness state.
- Hub starts and exposes health/readiness endpoints.
- Core services register or report absence cleanly.
- Missing optional services degrade gracefully.
- Startup does not require stale UI files, generated databases, local logs, or
  machine-specific paths.

Initial validation target:

```powershell
python tools\alpha_boot_validation.py
```

Verified full launch target (use the isolated configuration in the runbook):

```powershell
python aetherra_os_launcher.py --mode full --no-gui --config "$alphaProfile/launcher.json"
```

The boot validator, `tools/os_smoke.py` and standalone Hub helper do not prove
the full runtime boots. The manual check above uses the normal full launcher.

## Gate 5: Runtime UI Observatory

Status: Connected, degraded, stopped and reconnected browser checks pass;
ALPHA-02/03 resolved locally. Build, lint and all 17 GUI tests pass.

Engine degradation matches readiness evidence; missing services and stopped
runtime are unknown. Titles are visible and no application console errors were
observed. THREE.Clock deprecation and bundle-size warnings remain documented.

Required before alpha:

- Runtime UI builds from `Aetherra/lyrixa/gui`.
- Runtime UI does not depend on deprecated non-plugin UI surfaces.
- The first screen represents Aetherra as a Cognitive Observatory, not a
  generic chatbot or legacy dashboard.
- UI reads system state from bounded status/readiness APIs.
- UI mutation controls remain absent or Guardian-mediated.
- Browser smoke verification confirms the UI renders without console errors.

Validation:

```powershell
Push-Location Aetherra\lyrixa\gui
npm.cmd run build
Pop-Location
$runtimeUiTests = @(Get-ChildItem tests/unit/test_runtime_ui_*.py | ForEach-Object { $_.FullName })
python -m pytest -q -o addopts= --basetemp .pytest_tmp_runtime_ui @runtimeUiTests
```

## Gate 6: Integration Validation

Status: Pass for bounded contracts: 5 runner checks plus focused regressions.

The contracts cover allow/deny, approved-scope mismatch and truthful failure
when rollback is unavailable. The separate real full-launcher retest supplies
bounded Homeostasis observation-only evidence; see Gate 3.

Required before alpha:

- Integration Validation proves Security, Guardian, Homeostasis, Maintenance,
  Self-Improvement, Self-Incorporation, Aether Script, Kernel, and Hub cooperate
  through current contracts.
- Validation remains non-destructive by default.
- Validation includes both allow and deny paths.
- Validation reports enough evidence to explain failures.
- Validation can run locally and in CI.

Validation:

```powershell
python -m Aetherra.integration_validation
python -m pytest -q -o addopts= --basetemp .pytest_tmp_integration_validation tests\unit\test_integration_validation.py
```

## Gate 7: Repository Hygiene

Status: Focused checks pass; isolated working patch used for verification.

Website-artifact verification passes. Runtime profiles, logs, test outputs and
GUI dependencies/build output stay ignored. This is not an exhaustive cleanup
of all legacy repository artifacts. Unrelated user changes remain out of scope.

Required before alpha:

- Build outputs are ignored or removed from source control.
- Runtime/cache folders are ignored or removed from source control.
- Generated reports are ignored unless intentionally promoted into `docs/`.
- Distribution/package artifacts are ignored or published as release assets.
- Vendor/dependency bundles are ignored.
- Deprecated non-plugin UI surfaces are archived or removed.
- Plugin GUI surfaces remain available for future plugin work.
- Root files are limited to active entry points, package/config files, public
  policy docs, and compatibility launchers.

Validation:

```powershell
python tools\ci_verify_no_website_artifacts.py
git status --short
```

## Gate 8: CI And Security Checks

Status: Local CI selection passes (1,916 passed/8 skipped); remote candidate CI open.

All 31 reported checks on `2f4b3324` were successful when reviewed on
2026-11-21, including signed CI and Release. `b1b7ae12` is the resulting release
version commit, not a separately tested full CI run. None of these old remote
checks verify the current working patch. Signing remains enforced; 13 local
signing tests pass. Default collection now succeeds with 3,093 tests. Full
execution reached its time bound with failures; see the decision for named
findings and scoped reruns. The final local CI directory selection passes in a
source-only snapshot; this is not remote workflow or coverage acceptance. The
fixed style baseline remains unchanged.
Legacy desktop dependency findings are deferred, and this check does not claim
that all Advanced Security findings or installed packages are clean.

Required before alpha:

- Fast quality checks pass.
- Security sanity checks pass.
- Docs consistency checks pass.
- Import validation passes.
- Aether Script verification passes.
- Commit lint passes.
- Large-file and size gates pass.
- GitHub Advanced Security findings that affect active source are triaged or
  fixed.

Validation:

```powershell
python tools\verify_docs_consistency.py
git diff --check
```

GitHub Actions remain the source of truth for remote CI status.

## Gate 9: Operator Runbook

Status: Verified bounded observation and repaired operator API procedures recorded.

The runbook documents the full CLI, isolated synthetic storage, correct JSON
routes, authenticated Guardian reads, GUI proxy, stop/restart and fallback
interpretation. Hub Homeostasis status now uses the initialized launcher
instance (ALPHA-04). Authenticated Self-Incorporation audit reads support
validated filters and limits (ALPHA-05). Broader operational acceptance remains
pending; stale registry evidence still displays unknown.

Required before alpha:

- A short alpha runbook explains how to start Aetherra.
- The runbook explains how to inspect health.
- The runbook explains how to stop the runtime.
- The runbook explains how to review Guardian/Security decisions.
- The runbook explains rollback expectations and limitations.
- The runbook explains what should not be connected during alpha.

Primary file:

- `docs/ALPHA_OPERATOR_RUNBOOK.md`

## Gate 10: Alpha Decision

Status: Recorded — No-go for broader internal alpha operation.

All six recorded runtime blockers are fixed and retested locally, and the local
CI test selection passes. Broader acceptance still requires a reproducible
commit, current remote CI and disposition of the documented legacy limitations.
No remaining risk has been silently accepted.

Before calling alpha ready:

- All gates above are complete or explicitly accepted as known limitations.
- Known limitations are documented.
- The active branch is merged cleanly.
- GitHub checks are green or documented with a justified exception.
- The repository has no uncommitted source changes.
- The alpha tag or release candidate points to a reproducible commit.

Decision record:

- `docs/ALPHA_READINESS_DECISION.md`

## Current Next Actions

1. Assess the documented legacy failures outside the passing CI selection.
2. Review and commit the scoped fixes, then verify current CI and a clean
   checkout before reconsidering Go.
3. Preserve strict signing and unrelated workspace changes throughout acceptance.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
