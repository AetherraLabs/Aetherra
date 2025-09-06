# Contributing

<!-- Sourced from docs-organized/project/CONTRIBUTING.md -->

Please see `docs-organized/project/CONTRIBUTING.md` for the full contributor guide.

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

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
