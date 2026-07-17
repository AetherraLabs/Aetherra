# Alpha Operator Runbook

Updated: 2026-06-21

This runbook explains how to operate Aetherra during controlled alpha
validation. It assumes a reviewed development environment, not production
autonomy.

## Operating Rule

Aetherra alpha operation is observation-first.

Privileged actions must remain mediated:

```text
Guardian decides.
Security enforces.
Self-Incorporation executes only approved locked plans.
Homeostasis verifies.
Maintenance records.
```

Do not connect alpha builds to sensitive systems, production credentials,
private user data, external automation targets, payment systems, or unattended
networked control surfaces.

## Prerequisites

Required:

- Python 3.11 or newer.
- Project dependencies installed from the repository requirements.
- Guardian and Security enforcement enabled for privileged paths.
- A clean or intentionally reviewed working tree.

Recommended environment:

```powershell
$env:AETHERRA_PROFILE = "test"
$env:AETHERRA_GUARDIAN_MODE = "enforcing"
$env:AETHERRA_REQUIRE_CAPABILITIES = "1"
$env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
$env:AETHERRA_SIGNING_STRICT = "1"
$env:AETHERRA_AUDIT = "1"
```

For local Hub control routes, set a non-public local token:

```powershell
$env:AETHERRA_HUB_CONTROL_TOKEN = "replace-with-local-alpha-token"
```

Do not commit local `.env` files or real tokens.

## Preflight

Run the non-destructive alpha readiness checks first:

```powershell
python tools\alpha_boot_validation.py
python -m Aetherra.integration_validation
python tools\verify_docs_consistency.py
```

Expected result:

- Alpha boot validation reports `passed: true`.
- Integration Validation reports `passed: true`.
- Docs consistency reports no missing documented environment variables or
  endpoints.

If any of those fail, do not proceed to live runtime testing until the failure
is understood.

## Start The Runtime

For lightweight API validation:

```powershell
python tools\run_hub_ai_api.py --port 3001
```

Then inspect:

```powershell
curl http://localhost:3001/api/health
curl http://localhost:3001/api/hub/readiness
curl http://localhost:3001/api/kernel/readiness
curl http://localhost:3001/api/runtime-ui/status
```

For broader OS smoke validation:

```powershell
python tools\os_smoke.py
```

The smoke path should remain reviewed because it may initialize local runtime
state. Prefer `tools\alpha_boot_validation.py` for CI.

## Inspect Health

Primary read-only checks:

```powershell
curl http://localhost:3001/api/hub/readiness
curl http://localhost:3001/api/kernel/readiness
curl http://localhost:3001/api/maintenance/status
curl http://localhost:3001/api/selfinc/status
curl http://localhost:3001/api/runtime-ui/status
```

Healthy alpha signals:

- Hub readiness is `ready` or an understood `degraded`.
- Kernel readiness is `ready` before scheduling runtime work.
- Maintenance loop status is visible.
- Self-Incorporation status is visible and not executing unapproved work.
- Runtime UI status is read-only and reports known systems.

Blocked signals:

- Guardian denial for required safety gates.
- Security missing capability enforcement.
- Kernel readiness `blocked`.
- Hub readiness `blocked`.
- Self-Incorporation rollback unavailable for a proposed non-dry-run mutation.
- Integration Validation failure.

## Review Guardian And Security Decisions

Guardian and Security decisions should be reviewed before trusting any
privileged behavior.

Useful surfaces:

```powershell
curl http://localhost:3001/api/guardian/status
curl http://localhost:3001/api/security/status
curl http://localhost:3001/api/selfinc/audit
```

Operator expectations:

- Denied actions should fail before mutation.
- Approval-required actions should not execute without approval.
- Audit payloads should avoid raw sensitive data.
- Self-Incorporation plans should include approved-scope evidence.

## Rollback Expectations

Rollback is required for non-dry-run Self-Incorporation mutation.

Expected behavior:

- Dry runs may proceed without rollback infrastructure.
- Non-dry-run plugin or agent integration requires HMR token rollback support.
- Locally reversible actions must emit bounded rollback tokens.
- Unsupported rollback attempts must fail closed.
- Rollback attempts must pass Guardian review.

Do not treat rollback as successful unless the response explicitly confirms the
rollback target and status.

## Stop The Runtime

If the Hub was started from a terminal, stop it with `Ctrl+C`.

After stopping, inspect the working tree:

```powershell
git status --short
```

Unexpected generated files, logs, databases, reports, or build outputs should be
ignored, removed, or moved to an appropriate artifact location before any
commit.

## Do Not Connect During Alpha

Do not connect alpha builds to:

- production credentials
- private customer or user data
- payment systems
- uncontrolled network automation
- real infrastructure mutation targets
- unattended plugin installation sources
- autonomous code execution without Guardian and Security enforcement

Alpha is for proving governed operation, not maximizing autonomy.

## Escalation

Stop testing and investigate if:

- Guardian is disabled or bypassed.
- Security capability enforcement is disabled for privileged paths.
- Self-Improvement attempts direct mutation.
- Self-Incorporation executes actions outside the approved plan scope.
- Rollback claims success without a truthful target.
- Runtime UI exposes mutation controls without Guardian mediation.
- CI or local validation reports unexplained failures.

## Completion Signal

An alpha run is acceptable only when:

- Preflight checks pass.
- Runtime readiness endpoints are understandable.
- No privileged action bypasses Guardian or Security.
- No generated artifacts are accidentally staged.
- Known limitations are recorded in the alpha decision document.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
