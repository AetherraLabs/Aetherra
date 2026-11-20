# Alpha Readiness Decision

Updated: 2026-07-18

This document records the internal alpha go/no-go decision for Aetherra. It
should be completed only after the alpha readiness checklist has been reviewed.

## Decision

Status: Draft

Decision:

- Pending

Decision date:

- Pending

Decision owner:

- Aetherra Labs

Release or commit:

- Pending

## Summary

Use this section to summarize whether Aetherra is ready for internal alpha
testing and why.

Required conclusion:

- Go
- No-go
- Go with documented limitations

## Required Evidence

Before this decision can be marked complete, record evidence for:

- Identity and scope reviewed.
- All active systems are functional complete or functional foundation complete.
- Guardian and Security checks pass.
- Integration Validation passes.
- Alpha boot validation passes.
- Runtime UI build and readiness checks pass.
- Repository hygiene checks pass.
- GitHub CI checks are green or exceptions are documented.
- Operator runbook exists and is usable.

## Validation Commands

Record the final command results here:

```powershell
python tools\alpha_boot_validation.py
python -m Aetherra.integration_validation
python tools\verify_docs_consistency.py
git diff --check
git status --short
```

Optional live validation:

```powershell
python tools\os_smoke.py
python tools\run_hub_ai_api.py --port 3001
```

## Known Limitations

List accepted limitations here. Each limitation should include:

- Description
- Risk
- Mitigation
- Owner
- Follow-up issue or document

## Go Conditions

Aetherra can be marked ready for internal alpha only if:

- No unexplained safety failure remains.
- No privileged action bypasses Guardian or Security.
- Self-Improvement remains proposal-only.
- Self-Incorporation applies only approved locked plans.
- Rollback behavior is truthful for non-dry-run mutation.
- Runtime UI is observational unless a control is explicitly Guardian-mediated.
- The repository has no staged or unstaged source changes.

## No-Go Conditions

Aetherra must not be marked alpha-ready if:

- Guardian is disabled or bypassed for privileged paths.
- Security enforcement is disabled for privileged paths.
- Self-Incorporation can mutate without approved scope validation.
- Rollback claims success without a truthful target.
- Integration Validation fails.
- Alpha boot validation fails.
- Runtime UI depends on deprecated non-plugin UI surfaces.
- CI reports active safety, quality, or repository hygiene failures.

## Final Notes

Pending.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
