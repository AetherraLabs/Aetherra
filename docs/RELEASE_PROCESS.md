<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
# Release Process (Alpha → Tag)

Status: Applies to 0.1.x alpha line. Will be hardened (multi‑sig, attestations) before beta.

## Goals

Deterministic, reproducible, policy‑gated release artifact with:

- Zero UNKNOWN licenses (enforced)
- Locked dependency graph (requirements.lock)
- SBOM + license report artifacts
- Changelog + version metadata alignment

## Prerequisites

- Working main branch is green on Quality Gates
- `requirements.lock` in sync with environment
- `CHANGELOG.md` updated with unreleased section promoted
- Version bump committed in `Aetherra/pyproject.toml`, `README.md`, any docs referencing version

## Steps

1. Ensure workspace clean

    ```powershell
    git status
    ```

1. Run Quality Gates (full) locally

    ```powershell
    python tools/quality_gates.py
    ```

1. Run packaging smoke test

    ```powershell
    python tools/packaging_smoke.py
    ```

1. Generate fresh license & SBOM artifacts (already in gates, run again if desired)

    ```powershell
    python tools/license_report.py --lock requirements.lock --json licenses_report.json
    python tools/generate_sbom.py --license-json licenses_report.json --out sbom.json
    ```

1. Commit & push

    ```powershell
    git add CHANGELOG.md Aetherra/pyproject.toml README.md sbom.json licenses_report.json
    git commit -m "chore(release): vX.Y.Z-alpha.N"
    git push origin main
    ```

1. Create annotated tag

    ```powershell
    git tag -a vX.Y.Z-alpha.N -m "Aetherra vX.Y.Z-alpha.N"
    git push origin vX.Y.Z-alpha.N
    ```

1. (Optional) Sign artifacts (future multi-sig):

    - Produce manifest (hashes) & sign with steward key (script TBD)

1. Publish to package index (internal / test):

    ```powershell
    python -m pip wheel . -w dist --no-deps
    python -m twine upload dist/aetherra-<version>-py3-none-any.whl
    ```

1. Create release notes from CHANGELOG section.

1. Post-release: Open next `-alpha.(N+1)` section in CHANGELOG.

## Validation Checklist

- [ ] Quality Gates PASS
- [ ] Packaging smoke PASS
- [ ] No UNKNOWN licenses
- [ ] SBOM present & committed (or attached to release)
- [ ] Changelog & version aligned
- [ ] Tag pushed

## Rollback

If a critical issue is found:

1. `git tag -d vX.Y.Z-alpha.N` locally & `git push origin :refs/tags/vX.Y.Z-alpha.N`
2. Revert problematic commits
3. Issue advisory + create replacement tag

---
Future (Beta): multi-party signature, provenance attestation, automated GH release action.
