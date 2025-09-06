<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Ownership & Release Authority

This document clarifies project ownership, release authority, and contribution acceptance for the Aetherra AI Operating System.

## Steward Ownership

Aetherra is stewarded by **Aetherra Labs**. Stewardship conveys responsibility (not exclusive authorship) over:

- Strategic direction & roadmap arbitration
- Security posture & key management
- Official release packaging and distribution
- Trust / signing policies for workflows, plugins, and scripts
- Emergency response (security, legal, integrity incidents)

## Official vs Community Code

| Category               | Definition                                                       | Trust Tier                             | Activation Path                   |
| ---------------------- | ---------------------------------------------------------------- | -------------------------------------- | --------------------------------- |
| Core (Official)        | Kernel, orchestrator, memory engines, security & signing modules | Highest – must be steward-signed       | Auto-enabled in releases          |
| Official Extension     | Plugins / workflows elevated to supported status                 | High – steward signature required      | Enabled by default once published |
| Community Contribution | PR-submitted code not yet elevated                               | Medium – contributor signed (optional) | Reviewed; may run in sandbox      |
| Experimental / Sandbox | High-risk, exploratory, or un-audited code                       | Low – never treated as official        | Manual opt-in only                |

Only steward-signed artifacts are recognized as "official" in strict security modes.

## Release Pipeline Control

- Release tags (git) MUST be created & signed by a steward key.
- Build & packaging jobs referencing protected branches run under steward-controlled CI credentials.
- A Software Bill of Materials (SBOM) + hash manifest is generated per release and archived.
- Reproducibility checks (hash comparison of critical modules) are logged before publication.

## Signing & Verification

| Element             | Requirement                                                  | Enforcement                             |
| ------------------- | ------------------------------------------------------------ | --------------------------------------- |
| Workflows (.aether) | Valid signature + intact hash chain                          | Refused if invalid or unsigned (strict) |
| Plugins / Scripts   | SPDX headers + signature for official status                 | Quarantined if missing when strict      |
| Steward Keys        | Rotated ≥ every 12 months or on incident                     | Revocation list distributed             |
| Community Keys      | Recorded for attribution; not trusted for official elevation | May sign commits / PRs                  |

## Strict Mode Behavior

When enabled (policy flag or env), the platform enforces:

1. Only steward keys accepted for: kernel adjacencies, privileged plugins, system workflows.
2. Any unsigned or altered official artifact → quarantine + alert.
3. Sandbox isolation for community plugins until explicit elevation commit merges.
4. Metrics emitted: `aetherra_signing_failures_total`, `aetherra_quarantined_artifacts_total`.

## Contribution Acceptance Flow

1. Fork & PR submission (must include rationale + tests for new capabilities).
2. Maintainer functional review (architecture, tests, security notes).
3. Steward sign-off required for: new network surfaces, cryptography, memory engine changes, policy / auth layers.
4. Merge: squash or rebase; authors preserved in commit trailers.
5. Optional: Elevation to Official Extension (separate PR updating catalog + signed manifest).

## Ownership Boundaries

Aetherra Labs does not claim ownership over third-party contributions; all accepted code remains under GPL-3.0-or-later with attribution preserved via git history and SPDX headers.

## Dispute & Escalation

- Technical direction disputes: maintainer vote → steward tie-break.
- Security disagreements: security team triage → steward final decision.
- License / attribution conflicts: legal review; may temporarily remove artifact pending resolution.

## Key Compromise Procedure (Summary)

1. Detect anomaly (metrics spike, invalid signature attempts, external report).
2. Revoke compromised key; publish revocation notice in `SECURITY.md` and release feed.
3. Rotate CI secrets & regenerate affected signatures.
4. Issue patched release with updated manifest + advisory.
5. Post-mortem published within 72h (unless embargoed for active exploit mitigation).

## FAQ

**Q: Can I distribute a fork with modifications?**  Yes, under GPL-3.0-or-later; you must preserve license & attribution.

**Q: Can my plugin become official?**  Yes—after review, security evaluation, tests, and steward signature.

**Q: Are unsigned community workflows blocked?**  In normal mode they may execute with reduced trust; in strict mode they are rejected unless whitelisted.

## Amendments

Changes to this document require a PR + 72h review window + steward approval.

---
For ownership questions: [ownership@aetherra.dev](mailto:ownership@aetherra.dev)
