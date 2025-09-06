# Security, Signing, and Federation Enhancements (2025-08-12)

This document summarizes the recent improvements aligned with the project’s priorities:

- Distributed/hub federation
- Security posture (signing, sandboxing/static analysis)
- Telemetry opt-in

## Additions and Changes

1. Hub registration tests

- tests/unit/test_hub_plugin_registration_strict.py: Enforces HTTP 400 for unsigned manifests when AETHERRA_SIGNING_STRICT=1.
- tests/unit/test_hub_plugin_registration_non_strict.py: Allows unsigned manifests (HTTP 200) when strict=0.
- tests/unit/test_hub_plugin_registration_signed_strict.py: Positive path under strict mode; accepts a properly signed manifest (HTTP 200). Skips when PyNaCl is unavailable.

1. Static verifier improvements

- tools/verify_aether_scripts.py:
  - Adds per-file risky-line output in markdown: "L&lt;line&gt;: [kind] snippet".
  - Sorts files by descending risk score and prints a Top 5 summary.
  - New flag --max-findings-per-file (default 50) to cap the number of risky lines shown per file for compact PR reports.

1. CI workflow updates

- .github/workflows/security-sanity.yml:
  - Runs targeted tests for telemetry, static risk, signing, federation, in-thread hub, and plugin registration (strict/non-strict/signed).
  - Keeps strict signing and script verification enabled via env flags. The signed test is allowed to skip when PyNaCl isn’t present.

## How to run locally

- Run the hub tests:

```bash
pytest -q tests/unit/test_hub_inthread.py \
  tests/unit/test_hub_plugin_registration_strict.py \
  tests/unit/test_hub_plugin_registration_non_strict.py \
  tests/unit/test_hub_plugin_registration_signed_strict.py
```

- Generate the .aether static report with capped findings (example cap=30):

```bash
python tools/verify_aether_scripts.py --strict --output aether_static_report.md --max-findings-per-file 30
```

## Notes

- The positive-path signed test requires PyNaCl; when missing, it skips without failing CI.
- The static verifier still exits non-zero when any file exceeds the risk threshold (default 5) or when strict signature checks fail.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
