# Alpha Readiness Checklist

Updated: 2026-07-18

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

Status: In progress

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

Status: In progress

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

Status: In progress

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

Status: In progress

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

Optional live validation target:

```powershell
python tools\os_smoke.py
python tools\run_hub_ai_api.py --port 3001
```

## Gate 5: Runtime UI Observatory

Status: Pending

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
python -m pytest -q -o addopts= --basetemp .pytest_tmp_runtime_ui tests\unit\test_runtime_ui_readiness.py
```

## Gate 6: Integration Validation

Status: In progress

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

Status: In progress

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

Status: Pending

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

Status: In progress

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

Status: Pending

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

1. Continue repository hygiene on generated artifacts and stale root files.
2. Run the full alpha readiness command set and record known limitations.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
