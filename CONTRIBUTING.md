# Contributing

This is the canonical contributor guide for Aetherra.

Quick links:

- Docs consistency gate: `docs/contributing/docs-consistency.md`

## Governance & Compliance Expectations

When submitting PRs that affect dependencies, licensing, or release engineering:

- Run `python tools/license_report.py --lock requirements.lock --json licenses_report.json` and ensure UNKNOWN count stays 0.
- If adding a new override in `license_overrides.yml`, include justification in the PR description.
- Do not add strong copyleft runtime dependencies without an ADR reference.
- Ensure `pytest -q -o addopts= tests/tools` passes (governance tooling tests).
- For build/release changes, run `python tools/packaging_smoke.py` locally.

## Adding Tests

- Place license governance tests under `tests/tools`.
- Use failure injection patterns in `tests/failure_injection` for resilience scenarios.

## Version Badge Drift

A forthcoming automation script will fail CI if README version badge mismatches project version; until then manually keep them in sync.

## .aether Script Signing & Pre-commit Hook

All `.aether` workflows and scripts must include an up-to-date `# @signature:` header.

To avoid manual steps, a git pre-commit hook is provided that automatically (re)signs any staged `.aether` files:

1. Ensure the hook file exists at `.git/hooks/pre-commit` (created automatically in this repo) and is executable.
2. Stage your changes (`git add` ...).
3. On `git commit`, the hook runs `tools/precommit_sign_aether.py` which calls `tools/sign_aether.py` for each changed `.aether` file and re-adds them to the index if modified.

Manual signing (if ever needed):

```bash
python tools/sign_aether.py workflows/parallel_workflow_demo.aether
```

Verify all signatures & static risk locally (strict mode):

```bash
python tools/verify_aether_scripts.py --root . --strict --profile test --fail-on-any-risk
```

Dry-run the pre-commit signer (show which files would be re-signed without modifying them):

```bash
python tools/precommit_sign_aether.py --dry-run workflows/parallel_workflow_demo.aether
```

CI also runs a strict verification workflow (`aether-verify-signatures.yml`) to prevent unsigned or tampered `.aether` content from merging.

## Deprecations & Lifecycle

Active deprecations are tracked to ensure safe removal after a stability window.

**Recently Completed:**
- Legacy Hub script (`aetherra_hub_server.py`) — fully migrated to `aetherra_hub.compat` module (removed).

If proposing a new deprecation, open an issue with label `deprecation-proposal` containing:

1. Rationale and replacement path
2. Planned enforcement layers (tests, hooks, gates)
3. Migration impact assessment
4. Target earliest removal version

Approved proposals should add a tracker doc under `docs/DEPRECATION_TRACKER_*.md` and an entry in `CHANGELOG.md` under Deprecations.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
