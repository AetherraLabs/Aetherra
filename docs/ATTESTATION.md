<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Release Attestation (Alpha Stub)

This document describes the planned attestation & provenance model for Aetherra releases. Current status: stub (metrics & integrity manifest in place; cryptographic signing deferred to Beta).

## Goals

- Provide a verifiable statement binding source revision, built artifacts, SBOM, license inventory, and integrity manifest.
- Enable downstream consumers to audit supply‑chain state (dependencies, overrides, risk acceptances) at tag time.
- Support future detached or in‑tag signatures (GPG / Sigstore) without changing the attestation payload schema.

## Artifacts Referenced

| Artifact           | Path                      | Purpose                                                           |
| ------------------ | ------------------------- | ----------------------------------------------------------------- |
| Integrity Manifest | `integrity-manifest.json` | Canonical SHA256 of critical inputs & built wheels                |
| License Report     | `licenses_report.json`    | Final resolved license inventory (zero UNKNOWN baseline enforced) |
| SBOM               | `sbom.json`               | Dependency list (minimal JSON SBOM)                               |
| Overrides          | `license_overrides.yml`   | SPDX override mappings (post-prune)                               |
| Risk Register      | `docs/RISK_ACCEPTANCE.md` | Accepted residual risks at release point                          |

## Attestation JSON Schema (Planned)

```jsonc
{
  "_schema": 1,
  "revision": "<git commit SHA>",
  "tag": "vX.Y.Z",
  "timestamp": "ISO-8601",
  "integrity_manifest_sha256": "<sha256 of integrity-manifest.json>",
  "integrity_entries": [ { "path": "...", "sha256": "..." } ],
  "sbom_sha256": "<sha256>",
  "license_report_sha256": "<sha256>",
  "overrides_sha256": "<sha256>",
  "risk_register_sha256": "<sha256>",
  "tool_versions": { "python": "3.11.x" },
  "meta": { "generator": "attestation_stub" }
}
```

## Current Implementation (Alpha)

- `tools/create_annotated_tag.py` and `tools/create_provenance_tag.py` embed the integrity manifest hash in the annotated tag message (if manifest present).
- No signature is produced yet; consumers can recompute manifest and compare hash in tag.

## Planned Beta Enhancements

- Sigstore keyless signing or GPG detached signature for attestation JSON.
- Inclusion of build environment digest (selected env vars, Python interpreter hash) with privacy scrubbing.
- Optional inclusion of vulnerability scan summary & severity counts.
- Multi-signer quorum (maintainer + automation bot) for elevated trust.

## Verification (Manual Example)

1. Fetch tag: `git fetch --tags`
2. Show tag: `git show vX.Y.Z` – note `INTEGRITY_MANIFEST_SHA256=...` line.
3. Recompute locally:
   - Run quality gates to regenerate artifacts.
   - Compute `sha256sum integrity-manifest.json`.
   - Compare with tag value.
4. (Future) Verify signature: `cosign verify-attestation ...` (planned).

## Trust Model (Interim)

Integrity relies on repository hosting (Git) + reproducibility docs. Cryptographic authenticity deferred to Beta milestone.

---

Status: Alpha stub – safe to reference; not yet a signed artifact. See `docs/BETA_MILESTONE.md` for roadmap tasks.
