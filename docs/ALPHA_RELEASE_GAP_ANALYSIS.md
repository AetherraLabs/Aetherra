<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
# Alpha Release Gap Analysis (0.1.0-alpha.2)

Purpose: Living checklist of remaining items judged valuable before promoting the current alpha branch as a broadly consumable tagged release (public distribution & announcement). Items are grouped by readiness pillar. "Done" items here record completion evidence; open items track owner / intent. This file is intentionally concise; deep rationale lives in dedicated policy docs.

## Legend

- [x] Complete / validated
- [ ] Open (needs implementation)
- [-] In progress / partial

## 1. Governance & Compliance

- [x] License UNKNOWN count = 0 (baseline locked via ABS_MAX=0 auto-tighten)
- [x] Trend gating + enforcement history (licenses_unknown_history.json) operational
- [x] Overrides YAML normalized & documented (LICENSE_POLICY.md)
- [x] Add unit tests: override application, trend gating edge (tolerance, fail path)
- [x] Weekly scheduled stale override prune job (override_prune.yml cron @ Mon 03:00 UTC)
- [x] README cross-link to LICENSE_POLICY.md (governance section)

## 2. Security & Supply Chain

- [x] Threat model drafted (docs/THREAT_MODEL.md)
- [x] Link license gating + provenance additions inside threat model (section updates)
- [x] Integrate vulnerability scan (placeholder script wired) into quality_gates
- [x] SBOM generation step (baseline JSON) + artifact generation
- [-] Attestation / manifest signing: ATTESTATION.md + tag scripts present (signing & multi-sig deferred to Beta)

## 3. Testing & Quality Gates

- [x] Capability tests present (ownership, core behaviors)
- [x] Add governance test module for license tooling (tools/) (simulate UNKNOWN regression)
- [x] Establish explicit minimum coverage alignment (pyproject vs quality_gates) & document rationale (see COVERAGE_POLICY.md)
- [x] Add packaging smoke test: build wheel + install in temp venv + import sanity

## 4. Documentation

- [x] License policy (LICENSE_POLICY.md)
- [x] Alpha readiness guide (ALPHA_READINESS.md updated 0.1.0-alpha.2)
- [x] Add RELEASE_PROCESS.md (tagging, changelog update, build, sign, publish, announce)
- [x] CONTRIBUTING updated with governance test expectations (PR checklist)

## 5. Release Engineering

- [x] Changelog entry for 0.1.0-alpha.2
- [x] Sync version badge update automation (verify_version_badge.py)
- [x] Build reproducibility doc (deterministic build inputs list) & hash verification example (BUILD_REPRODUCIBILITY.md)
- [x] Optional: create integrity verification script (hash manifest vs local package contents) (generate_integrity_manifest.py)

## 6. Observability

- [x] Add metrics for license enforcement outcomes (gauges exported if prometheus_client present)
- [x] Plugin sandbox / timeout metrics surfaced (hub /metrics + plugin manager stats)

## 7. Risk Acceptance & Tracking

- [x] Residual risks enumerated in threat model
- [x] Formal risk acceptance note referencing ticket IDs / issues for Beta-scope mitigations (RISK_ACCEPTANCE.md initial)

## 8. Tooling Hardening

- [x] Dry-run flag docs for prune_license_overrides.py (README snippet)
- [x] Schema validation for overrides YAML (validate_license_overrides.py)
- [x] Dynamic SPDX ID fetch script (update_spdx_ids.py) (optional enhancement)

## 9. CI / Automation

- [x] CI pipeline executes: lint, tests, coverage, license gates, vuln scan, SBOM, package build (ci_quality_gates.yml)
- [x] Failure artifact upload: license report JSON, enforcement log, SBOM (artifact staging)
- [x] Version badge check integrated (verify_version_badge.py in CI)

## 10. Post-Alpha Roadmap Prep

- [x] Curate BETA_MILESTONE.md synthesizing open Beta-scope items (sandboxing, provenance, eval persistence)

---
Remaining mandatory blockers: None.

Pre-release optional (non-blocking) improvements (target Beta unless capacity available now):

1. Cryptographic attestation signing (Sigstore / GPG) for attestation JSON.
2. Sandbox enforcement (actual isolation + violation increments) beyond placeholder counters.
3. Advanced SPDX expression parser (full grammar) & deny-list enforcement mode.

Maintainers: with mandatory items complete, proceed to release steps (RELEASE_PROCESS.md) to tag 0.1.0-alpha.2 (or increment) using create_annotated_tag.py + provenance workflow.
