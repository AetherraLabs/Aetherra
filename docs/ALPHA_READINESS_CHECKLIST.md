# Alpha Readiness Checklist

Updated: 2026-11-24

Current released baseline: `17a833cd` (`v0.5.0-beta.11`), incorporating Phase A
and Phase B through [PR #352](https://github.com/AetherraLabs/Aetherra/pull/352).
Clean merge verification passed 3,494 tests, 38 skips and 5 passing subtests,
29 GUI tests and all 12 main workflows. Required production and release signing
passed; the release signature and signed artifact checksums were verified.
See the [merged-main checkpoint](ALPHA_READINESS_DECISION.md#phase-b-merged-main-checkpoint).

**Phase C1: GO for supervised operation of the frozen Windows source-runtime
candidate.** It remains uncommitted and unmerged. Hosted CI, fresh installation,
browser and live-model checks are unverified for C1. Local acceptance is recorded
in the [decision](ALPHA_READINESS_DECISION.md#phase-c1-observer-candidate) and
[source-bound evidence](evidence/integration_phase_c1_2026-11-24.json):

- [x] Default-disabled normal launch has no observer registration in three fresh
  processes, including empty-history restart and a separate profile; all exit
  zero without force and with zero generation fallback.
- [x] Real Guardian allow, deny and audit-failure regressions enforce truthful
  completed ticks and fixed 64-entry retention. Both normal-launch signed audit
  chains verify; the denied 215-second profile has zero completed ticks.
- [x] The allowed 215-second window advances completed ticks 1 → 214 and measured
  events 4 → 856, beyond the 180-second stale threshold. Engine and observer
  heartbeats stay fresh; independent observer stop leaves chat usable.
- [x] Actual Consciousness and Observatory HTTP payloads show live/blocked/stopped
  state; after stop they report HTTP 503/offline. Stale/failed cases and pure
  cached reads have regressions. No public stop route was added.
- [x] The observer performs no persistent continuity access, QFAC write, Memory
  consolidation or actuation. The full suite passes 3,651 tests, 38 skips and
  5 passing subtests, exit
  zero, with 45.29% configured coverage against the unchanged 22% requirement.
  Boot/integration and quality gates pass with zero new/edited violations.
- [x] Opaque saved/retrieved/provider IDs correlate through real storage and
  context-derived generation, including after observer stop and default-profile
  process restart. Browser/live-model results are explicitly unverified.

These checks support local supervised C1 operation, not remote CI or merged-main
acceptance. Next is C2 safe profile-scoped continuity with failed-restore
protection and accurate trust rehydration. Pending temporal observer work remains
separate and preserved. Strict signing stays enforced.

## Historical Phase B Candidate Checkpoints

At the earlier `ba3a04ad` (`v0.5.0-beta.10`) baseline, Phase A was merged through
PR #351. The then-focused Phase B local candidate is recorded in
[the decision addendum](ALPHA_READINESS_DECISION.md#phase-b-observation-and-maintenance-candidate)
and [evidence](evidence/integration_phase_b_2026-11-24.json). Those evidence records capture pre-commit verification; PR CI and integration
are separate gates. Historical main/release passes below do not certify this
candidate.

**GO remains bounded to supervised internal alpha on the documented Windows
source-runtime profile.** The initial Phase B checkpoint passed 3,455 tests,
38 skips and 5 passing subtests. Its Hub heartbeat concern is repaired and
passed 15 new regressions, a 129-test focused bundle and two extended normal
launch sessions. Its final default full suite passed 3,470 tests, with
38 skips and 5 passing subtests, after correcting a cold-start allowance
in the active-shutdown test and isolating a legacy alert fixture from shared
metric history, and replacing an unrelated whole-script timing benchmark with
a deterministic timeout-path regression. Existing shutdown and alert assertions
remain unchanged. The final run used an independent clean source snapshot.
See [the follow-up decision](ALPHA_READINESS_DECISION.md#hub-heartbeat-follow-up)
and [evidence](evidence/hub_heartbeat_followup_2026-11-24.json).

Observe-only behavior and durable proposal/cycle correlation across restart
remain verified. Earlier Observatory/browser and live-model evidence retain
their original source scope. Execution, unattended/production operation and
Stage 22 remain outside the verified boundary.

Final PR review repaired validator defaults/fallback estimates entering measured
history. The reviewed source passed **3,472 tests, 38 skips and 5 passing
subtests**, 87 focused provenance/flow tests, the unchanged quality gate, and
two further 215-second normal launches with real SQLite/history checks.
All 1,547 frozen source/control hashes matched. See the
[review checkpoint](ALPHA_READINESS_DECISION.md#phase-b-pr-review-checkpoint)
and [review evidence](evidence/integration_phase_b_pr_review_2026-11-24.json).
Hosted PR CI and merged-main acceptance remain separate gates.

The full-suite checkpoint is `3ea0df0`. A subsequent CI-only subprocess import
failure was reproduced and corrected in the test harness; 90 focused tests and
style checks pass. Production source is unchanged. See the
[CI follow-up](ALPHA_READINESS_DECISION.md#ci-subprocess-import-follow-up)
for the verification boundary and current PR checks.

Final merge review also repaired failed-restore overwrite and hidden persistence
errors. The backend and integrated bundles passed 234 and 158 tests respectively;
29 GUI tests, type checking, build and lint pass. Earlier full-suite records do
not certify these later edits. See the
[merge-review checkpoint](ALPHA_READINESS_DECISION.md#merge-review-maintenance-restore-and-status)
and its evidence; current-head CI and clean-main verification are separate.

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

Status: Fresh observation-only retest passes. Guardian enforces with intact
audit; six initialized samples show zero actuator actions, recoveries and restarts.
Twelve expired requests across three processes leave stored IDs unchanged. Signing stays
strict. Privileged live mutation remains outside the verified scope.

Required before alpha:

- Guardian can allow, deny, and require approval for privileged intent.
- Security can enforce capabilities, sandbox, signing, network, and audit
  boundaries.
- Denied privileged actions fail before mutation.
- Approval-required flows do not execute without a valid approval.
- Guardian and Security decisions are audited without exposing raw sensitive
  payloads.
- Self-Improvement remains proposal-only.
- Full launch defaults Self-Incorporation off; effective disabled status and
  no automatic Self-Improvement implementation must match the requested profile.
- Self-Incorporation validates approved plan scope before execution.
- Non-dry-run Self-Incorporation mutation has truthful rollback support or
  fails closed before mutation.

Validation:

```powershell
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_safety tests\unit\test_selfinc_integration_guardian.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp_alpha_validation tests\unit\test_integration_validation.py
```

## Gate 4: Runtime Boot Path

Status: Fresh-install full CLI boot and restart pass in the isolated candidate,
with an additional normal launch verified from clean main.

All 12 JSON endpoints return 200 in six initialized samples. All three Ctrl+C
exits are zero without force. No-provider fallback reports degradation; six gpt-4o replies
report Engine readiness and no fallback. This uses the new venv with system-site
packages disabled and the newly downloaded pinned retrieval model.

Required before alpha:

- A documented launcher path starts the intended alpha runtime.
- Kernel starts and exposes readiness state.
- Hub starts and exposes health/readiness endpoints.
- Core services register or report absence cleanly.
- Missing/starting core services and unselected providers cannot make startup
  ready; provider selection is not proof of a successful live response.
- Only live Kernel evidence can establish safe scheduling. Daemon/file fallback
  remains diagnostic, with unknown guards rather than fabricated passing checks.
- Poll the four core observation routes during a chat turn; verify bounded busy
  responses, retained SSE ownership and shutdown during active generation.
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

No-provider degradation changes to configured-model Engine readiness. Unavailable
evidence remains unknown. Read-only controls and three observation titles render
with zero observed console errors. Fresh npm install/audit, all 18 GUI tests,
build and lint pass. THREE.Clock and bundle-size warnings remain documented.

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

Status: Focused changes were merged through PR #327. Original workspaces, indexes,
and unrelated changes are preserved. Profiles, caches, raw logs and screenshots
remain outside committed source. Public evidence contains only synthetic data
and summary hashes. Clean-main acceptance passes; see the integrated evidence.

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

Status at the 2026-11-22 desktop checkpoint: Fresh dependency consistency, lock
sync and audit passed. All 168 installed distributions had zero advisory findings
and zero skips. Python quality reported zero new violations, 978 unchanged legacy
files and 55 resolved, with no baseline change. That default suite passed:
**3,136 passed / 40 skipped**, exit 0, with default collection/addopts/coverage.
Hosted Windows installation passed 87 regressions and the 18-test Observatory
suite; reviewed runtime CI was green. Current candidate verification is separate
in [the Phase A addendum](ALPHA_READINESS_DECISION.md#phase-a-core-integration-candidate).

The metadata compatibility, project-ancestor filtering and metrics listener
isolation regressions pass. No new skips were added to hide a failure. Optional
features outside this installation graph are explicitly documented, not claimed
as verified. Existing signing workflows and approved keys remain unchanged.

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

The first supervised-use exercise on PR #328 main completed 600 + 300 seconds
across restart: 32 samples, 12 JSON endpoints each, 16 gpt-4o turns without
fallback, normal shutdown and browser reconnection. Initial disclosure wording
failed despite successful persistence; the prompt correction integrated in
PR #347. Cold-start recall delayed health polling; the subsequent
steady-state window does not establish uninterrupted responsiveness. See
[the decision and limitations](ALPHA_READINESS_DECISION.md) and
[exercise evidence](evidence/supervised_alpha_2026-11-22.json).

Status: Exact fresh installation, full CLI, browser and real-model procedures
are recorded. Three fresh-runtime processes, six live gpt-4o turns with no
fallback and twelve rejected expired requests are verified. Earlier 35-turn varied
live evidence remains historical. Local directories provide storage isolation.

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

Status: GO for supervised internal alpha on the verified Windows source-runtime
profile and local C1 operation on the frozen candidate. The released Phase B
baseline passed merge, clean-main and required production/release signing gates.
C1 remains uncommitted and unmerged, with hosted CI, fresh installation, browser
and live-model checks unverified. Unattended/production operation and unverified
installation graphs remain NO-GO; no broader authority is inferred.

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

1. Review the locally verified C1 candidate before any commit, publication and
   hosted CI; merged-main acceptance remains a separate gate.
2. Start C2 safe profile-scoped continuity restore/write and accurate trust
   rehydration through existing interfaces. Keep strict signing and governance;
   pending temporal observer work remains a separate preserved milestone.
3. Verify optional features, other platforms and broader operating modes
   separately before extending the GO decision.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
