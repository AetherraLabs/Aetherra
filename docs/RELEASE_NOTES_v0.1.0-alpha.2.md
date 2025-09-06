# Aetherra v0.1.0-alpha.2 Release Notes

Date: 2025-09-06
Tag: `v0.1.0-alpha.2`
Provenance Tag: `v0.1.0-alpha.2-provenance`

## Highlights

- Regenerated license report (`licenses_report.json`) with 0 UNKNOWN entries (all resolved via vetted overrides).
- SBOM (`sbom.json`) refreshed (261 components) using lightweight in-repo generator.
- Integrity manifest (`integrity_manifest.json`) published embedding hashes for core supply-chain artifacts.
- Vulnerability scan tooling (`tools/vuln_scan.py`) upgraded from placeholder hash-only mode to multi-engine wrapper (pip-audit / osv-scanner best-effort) with graceful fallback.
- Quality gates pipeline remains green after fixes.

## Supply Chain & Integrity

```text
requirements.lock      SHA256 a8e00b0146a9186734a923004add221a7333dc1d578c5eff6246ad00e8c14980
licenses_report.json   SHA256 85ff9ec601ba6d1b19a2cc9bb6734decd051485514be881d4354751871c03074
sbom.json              SHA256 3fbaecd85de1efc928f6fa415055a382bd6ba03210a7d955bd5a501f36c1f46a
```

These values are embedded (integrity manifest hash) within the annotated tag for traceability.

## Governance & Compliance

- License enforcement baseline auto-tightened (trend tolerance: 0 growth; fail-on-increase active).
- Overrides validated against canonical + dynamic SPDX lists; weekly prune automation in place.
- No new UNKNOWN licenses introduced; gating scripts confirm compliance.

## Security & Observability

- Sandbox/plugin execution timeout metrics now increment and surface via hub `/metrics` endpoint.
- Vulnerability scan wrapper exits cleanly when scanners absent (early alpha mode) while preserving gating structure for future enforcement.

## Deferred (Beta Roadmap)

- Cryptographic signing & attestation (Sigstore / GPG) integration.
- Full sandbox isolation & policy violation counters (beyond timeouts).
- SPDX expression parser with deny-list and license policy strict mode.
- Automated signed provenance attestation emission.

## Upgrade Notes

No breaking changes; governance tooling improvements only. Consumers pulling artifacts should verify the above SHA256 hashes against `integrity_manifest.json`.

## Acknowledgements

Thanks to contributors advancing governance, provenance, and observability foundations ahead of schedule.

---
For full policy references see: `docs/ALPHA_RELEASE_GAP_ANALYSIS.md`, `docs/LICENSE_POLICY.md`, `docs/RELEASE_PROCESS.md`, `docs/ATTESTATION.md`.
