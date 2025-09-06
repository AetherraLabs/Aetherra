# Aetherra License Policy (Alpha)

<!-- SPDX-License-Identifier: Apache-2.0 -->

This document defines the initial (alpha) stance on third‑party dependency licenses for the Aetherra project.
It complements: LICENSE, COPYRIGHT, NOTICE, GOVERNANCE.md, AETHERRA_CLAIMS_VALIDATION.md and the packaging / provenance docs.

## 1. Objectives

- Transparency: Every transitive dependency MUST appear in `licenses_report.json` produced by `tools/license_report.py`.
- Traceability: A release manifest + SBOM + lock file give a cryptographically linked snapshot.
- Progressive Hardening: Alpha focuses on inventory + unknown surfacing; Beta will introduce deny / escalate classes.

## 2. Current Enforcement Model (Alpha)

| Category                                                                   | Policy                                                                              | Gate Behavior            |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------ |
| SPDX‐recognized permissive (MIT, BSD, Apache-2.0, ISC, Zlib, PSF, MPL-2.0) | Allowed                                                                             | Pass                     |
| Weak copyleft (LGPL-2.1/3, MPL-2.0 when not modified)                      | Allowed with notice                                                                 | Pass (log)               |
| Strong copyleft (GPL, AGPL)                                                | Allowed ONLY if toolchain/dev-only and not shipped in combined binary distributions | Warning (future block)   |
| Proprietary / Other / Custom                                               | Flag for review                                                                     | Warning                  |
| Unknown / Missing metadata                                                 | MUST be reduced over time                                                           | Warning (count surfaced) |

At alpha we do NOT fail the build on warnings; we surface counts to prevent silent drift.

## 3. Future Roadmap (Beta+)

Planned tightening (subject to community feedback):

1. Convert Unknown license count > 0 to a soft fail after grace period; require adding manual override annotation file (e.g. `licenses_overrides.yml`).
2. Disallow adding any new strong‑copyleft runtime dependency without explicit ADR (Architecture Decision Record) documenting isolation / compliance reasoning.
3. Introduce automated provenance attestation embedding license summary hash into the signed manifest.
4. Integrate an SPDX document export (tag:value or JSON) for all dependencies with normalized identifiers.
5. Add a transparency log entry (append-only) for each release capturing license diff vs prior release.

## 4. Manual Overrides (Planned)

A future `tools/enforce_license_policy.py` will:

- Read `licenses_report.json`.
- Load optional `license_overrides.yml` (NOT yet present) for packages lacking classifier metadata.
- Fail if: (a) unexpected new unknown appears without override, (b) prohibited license enters runtime set.

## 5. Developer Guidance

- Before introducing a new dependency, prefer existing standard libs or already-approved packages.
- If metadata is UNKNOWN, check upstream `PKG-INFO` or `pyproject.toml` and open an issue upstream if absent.
- Prefer actively maintained packages with SPDX identifiers in classifiers.

## 6. Metrics to Track

- Unknown license count (goal: trending downward to < 5 by Beta freeze).
- Strong / copyleft runtime dependency ratio.
- Delta in license inventory between releases.

## 7. Integration Points

- Current: surfaced in Quality Gates (License Report OK + warnings list).
- Upcoming: quality gate will parse this file to confirm presence (already implied by adding this doc) and later enforce thresholds.

## 8. Non-Goals (Alpha)

- Automated legal adjudication of complex dual-licensed terms.
- Redistribution packaging audits (handled post-Beta when binary distributions considered).

## 9. Change Control

All modifications to this policy require PR review from at least one governance maintainer and must update CHANGELOG with a License Policy section entry.

---

Alpha baseline established. Hardening items tracked in roadmap issues.

### Appendix: Overrides & Enforcement (Alpha Implementation Note)

An initial non-fatal enforcement script (`tools/enforce_license_policy.py`) now runs in the quality gates immediately after generating `licenses_report.json`. It surfaces:

- Total scanned packages
- Unknown license count (as `[LICENSE_ENFORCE]` log and `license_unknown_total <n>` metric line)
- Any deny-term substring matches (currently WARN-only)

Manual override annotations can be added in `license_overrides.yml` (kept empty by default). Uncomment the provided example block and supply:

```yaml
packages:
	<package_name>:
		license: <SPDX-ID>
		reason: <verification justification>
		approved_by: <handle or PR link>
```

Overrides only replace `UNKNOWN` entries; they do not mask explicit strong / copyleft identifiers. Future strict mode will require justification for each override addition.
