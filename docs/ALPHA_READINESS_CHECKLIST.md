# Alpha Readiness Checklist

Updated: 2026-11-22

Candidate: `codex/alpha-chat-contracts`, based on main `d00120e8`
(`v0.5.0-beta.4`), with focused fixes verified before publication. **Go for supervised synthetic
verification; no-go for broader internal alpha.** ALPHA-07 and the original nine
legacy failures are repaired. The final default suite finished with 3,115 passed / 40 skipped and process exit 0.
Candidate integration/CI and desktop dependency disposition remain open. See [the decision](ALPHA_READINESS_DECISION.md)
and [inspectable evidence](evidence/internal_alpha_suite_2026-11-22.json).

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

Status: Shipped identity configuration and live Aetherra/Lyrixa relationship pass; explicit paths remain supported.

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

Status: Foundations reviewed; completion labels do not imply all runtime services are ready.

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

Status: Bounded observation-only retest passes. Guardian is enforcing with intact
audit; four runtime samples show zero actuator attempts/executions/blocks and
zero recoveries/restarts. ALPHA-07 expiry rejects before storage/generation.
Signing remains strict. Privileged live mutation was not exercised.

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

Status: Full CLI fresh-profile boot and restart pass on the isolated candidate.

All 12 inspected JSON endpoints return 200 at startup and steady state in both
processes; both Ctrl+C shutdowns exit 0. No-provider failure remains degraded;
configured gpt-4o reports Engine ready with three successful lifecycle receipts
and zero problems. Unknown/malformed receipts still fail readiness. Optional policy
denials, relative configuration defaults and watchdog teardown logging remain
documented limitations.

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

Status: Fresh connected, stopped and reconnected browser verification passes.

Engine changes from no-provider degradation to configured-model readiness;
absent/stale evidence remains unknown. Read-only controls and three observation titles render without observed
application console errors. All 18 GUI tests, build and lint pass using the previously installed
locked GUI dependencies. THREE.Clock and bundle-size warnings remain documented.

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

Status: Pass for bounded contracts: five integration runner checks and the current
unit/integration regression selection. Runtime samples separately confirm
observation-only operation; this does not authorize privileged mutation.

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

Status: Focused hygiene checks pass in the isolated candidate. The source clone
began at main; only scoped fixes/tests/docs are edited. Raw logs, profiles,
dependencies and screenshots remain ignored. Original workspaces and indexes
are preserved. Evidence records the source checkpoint before publication.

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

Status: Default repository suite and local quality checks pass; candidate remote CI remains open.

Final frozen-source suite: **3,115 passed / 40 skipped**, process exit 0, with default
collection/addopts/coverage. The diagnostic rerun exposed SQLite lifetime,
coordination, event-loop/import and streaming-isolation defects; all are fixed
with focused red/green regressions. Exact tool pins resolve the provisioned Ruff
binary mismatch. Fixed-baseline quality: zero new violations, 980 unchanged
legacy files, 53 resolved. No new skips or baseline entries were added.
Published beta.4 signing verifies; prior main CI does not cover this patch.
Desktop dependency security debt and the provisioned pyxnat/pathlib metadata
conflict remain explicit; the suite is not a fresh-install clearance.

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

Status: Exact CLI, browser, expiry, no-provider and real-model procedures recorded.

Fresh verification records two normal-launcher processes, three live gpt-4o
turns with no fallback and eight expired requests with unchanged stored IDs.
The previous 35-turn varied-paraphrase/missing-fact/separate-profile matrix is
retained as historical evidence, not claimed as rerun. Local directories provide
storage isolation; readiness, shutdown and dependency limits remain explicit.

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

Status: Go for supervised synthetic verification; no-go for broader internal alpha.

The requested repairs pass locally. Candidate CI/merge and clean-main
verification remain, along with desktop dependency disposition. The final
default repository suite passes; it is no longer an open test blocker. No broader operating authority or risk acceptance is inferred.

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

1. When work resumes, run candidate CI and verify clean main after an approved merge.
2. Resolve or explicitly disposition desktop dependency debt and fresh-install limits.
3. Preserve strict signing, observation-only behavior and the fresh live/browser evidence.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
