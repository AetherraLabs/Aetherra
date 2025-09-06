<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
# Risk Acceptance Register (Alpha)

This document records explicitly accepted residual risks for the 0.1.x alpha line.

| ID     | Risk                        | Description                              | Mitigation In Place             | Planned Mitigation                           | Target Phase | Owner      |
| ------ | --------------------------- | ---------------------------------------- | ------------------------------- | -------------------------------------------- | ------------ | ---------- |
| RA-001 | Plugin privilege            | Plugins run in-process without isolation | Timeouts, basic metrics         | Subprocess / sandbox isolation + trust tiers | Beta         | Platform   |
| RA-002 | Single signing key          | One key compromise forges releases       | Key rotation procedure (manual) | Multi-sig + transparency log                 | Beta         | Security   |
| RA-003 | Unencrypted memory          | Memory DBs stored plaintext              | Host FS permissions             | Encryption at rest selectable per store      | Beta         | Memory     |
| RA-004 | No deny license gate        | Disallowed license not blocked           | Trend gating + overrides        | SPDX deny list hard fail                     | Beta         | Governance |
| RA-005 | No provenance attestation   | Builds lack SLSA-style provenance        | Integrity manifest + lock file  | Attestation + builder identity               | Beta         | Release    |
| RA-006 | Limited vuln scan assurance | Dependent on local tool availability     | Best-effort pip-audit/osv run   | CI enforced scanner container                | Beta         | Security   |

Review cadence: each pre-release (alpha tag) and prior to Beta promotion.
