# Packaging & Release (Alpha)

> Maintained and officially operated by **Aetherra Labs**. **Powered by Aetherra Labs.**

## Overview

Alpha packaging provides reproducible artifacts + integrity metadata:

- Source distribution (sdist) and wheel
- CycloneDX SBOM snapshot of the environment
- Release manifest (artifact hashes) optionally signed (ed25519)

## Build Steps

```bash
# 1. Clean dist
python -c "import shutil, pathlib; d=pathlib.Path('dist'); shutil.rmtree(d, ignore_errors=True); d.mkdir()"

# 2. Build wheel + sdist
python -m build  # or: python -m pip install build ; python -m build

# 3. Generate SBOM
python tools/generate_sbom.py --output dist/aetherra-sbom.json --version $(python -c "import importlib.metadata as im;print(im.version('aetherra'))" 2>nul || echo 0.0.0)

# 4. Release manifest (+ optional signing)
# Set AETHERRA_RELEASE_PRIVKEY to 64 hex chars (ed25519 private key) to sign
python tools/sign_release_manifest.py --dist dist --version 0.1.0-alpha.1 --sbom dist/aetherra-sbom.json
```

### One-shot helper

Instead of the manual sequence:

```bash
python tools/build_release_bundle.py --version 0.1.0-alpha.1
```

Adds SBOM + manifest (and signing when key present) in one run.

### Bootstrap (dev/CI convenience)

Windows (PowerShell):

```powershell
./scripts/bootstrap.ps1 -Version 0.1.0-alpha.1
```

Unix:

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh --version 0.1.0-alpha.1
```

## Signing

Environment variable: `AETHERRA_RELEASE_PRIVKEY` (hex Ed25519 private key). If provided, `release-manifest.json` obtains a `signing` section and a detached `.sig` file.

Verification (conceptual):

1. Obtain public key corresponding to private key.
2. Concatenate canonical JSON (sorted keys) → bytes
3. Verify detached signature.

(A formal verification helper will be added in a future iteration.)

Implemented helper (alpha):

```bash
python tools/verify_release_manifest.py --manifest dist/release-manifest.json --dist dist \
  --pubkey <ed25519_public_key_hex>
```

### Programmatic verification example (Python)

```python
import json, hashlib, pathlib, subprocess

manifest = json.loads(pathlib.Path('dist/release-manifest.json').read_text())
for art in manifest['artifacts']:
  data = pathlib.Path('dist')/art['path']
  h = hashlib.sha256(data.read_bytes()).hexdigest()
  assert h == art['sha256'], f"hash mismatch for {art['path']}"

# Optional signature check (PyNaCl)
try:
  import nacl.signing, nacl.encoding
  sig = pathlib.Path('dist/release-manifest.json.sig').read_text().strip()
  vk = nacl.signing.VerifyKey('<ed25519_public_key_hex>', encoder=nacl.encoding.HexEncoder)
  canonical = json.dumps(manifest, sort_keys=True).encode()
  vk.verify(canonical, bytes.fromhex(sig))
  print('signature OK')
except FileNotFoundError:
  print('no signature file present')
```

## Release Manifest Schema

```json
{
  "version": "0.1.0-alpha.1",
  "generated_at": "2025-09-05T12:00:00Z",
  "artifacts": [ {"path": "aetherra-0.1.0a1-py3-none-any.whl", "sha256": "..."} ],
  "sbom": "aetherra-sbom.json",
  "signing": {"tool_version": "alpha", "key_hint": "deadbeef..." }
}
```

## SBOM Notes

- Current implementation uses `pip list` + hashed RECORD files (best-effort)
- Future: adopt `cyclonedx-bom` for richer license metadata and dependency graph

## Integrity & Trust Roadmap

| Phase | Capability                                                          |
| ----- | ------------------------------------------------------------------- |
| Alpha | Manifest + optional signature, SBOM snapshot                        |
| Beta  | Multiple signatures, provenance attestation, verified plugin hashes |
| GA    | Reproducible build pipeline, transparency log, revocation list      |

## Dependency & Build Hygiene (Alpha)

Deterministic, secure builds rely on four supporting scripts (all in `tools/`):

| Script                 | Purpose                                                                                                   |
| ---------------------- | --------------------------------------------------------------------------------------------------------- |
| `dependency_lock.py`   | Generate a sorted `requirements.lock` from current environment (pin transitive versions).                 |
| `enforce_lock_sync.py` | Fail if active env drifts from `requirements.lock` (add to CI before tests).                              |
| `vuln_scan.py`         | Aggregate vulnerability scan via `pip-audit` / `osv-scanner` if installed; fails on High+ (configurable). |
| `license_report.py`    | Emit `licenses_report.json` + CSV-style stdout for license inventory (non-enforcing baseline).            |

Suggested CI Order (excerpt):

```bash
python tools/enforce_lock_sync.py
python tools/vuln_scan.py --lock requirements.lock
python tools/license_report.py --lock requirements.lock
```

Regenerating the lock (after intentional dependency changes):

```bash
python tools/dependency_lock.py
git add requirements.lock
```

Future Enhancements (planned):

- Policy gate to deny disallowed licenses.
- Vulnerability waiver file with auto-expiry.
- Richer SBOM license field population (CycloneDX library adoption).


Refer also to `LICENSE_POLICY.md` for evolving license stance (currently inventory + warnings; enforcement deferred to Beta).

## Operational Checklist (Alpha Release)

1. All quality gates green (coverage no-drop, capability tests pass)
2. SPDX strict pass
3. Build artifacts produced
4. SBOM generated
5. Manifest signed (if steward key available)
6. Create provenance tag (annotated) embedding manifest + sbom + lock hashes (see Provenance Tag Helper below)
7. Publish wheel/sdist + manifest + SBOM
8. (Optional) Run `verify_release_manifest.py` using public key to confirm integrity post-transfer

## Ownership

Release process controlled by Aetherra Labs (see OWNERSHIP.md). External contributions cannot publish official artifacts or signatures.

## Provenance Tag Helper (Alpha)

Purpose: Provide an auditable, immutable reference tying git history to shipped artifacts & dependency state.

Scripts: `tools/create_provenance_tag.py`, `tools/create_annotated_tag.py` (the latter can synthesize a minimal manifest if one is missing for experimentation workflows).

Generates an annotated tag message including:

- Release version
- SHA256 of `release-manifest.json`
- SHA256 of SBOM file
- SHA256 of `requirements.lock` (if present)
- Presence / absence of signature (and key hint)
- Timestamp & tool marker

Example:

```powershell
python tools/create_provenance_tag.py --version 0.1.0-alpha.1 `
  --manifest dist/release-manifest.json --sbom dist/aetherra-sbom.json `
  --lock requirements.lock --tag v0.1.0-alpha.1 --apply
```

If `--apply` is omitted the body is printed (copy/paste into a manual `git tag -a`).

Resulting annotated tag body makes later verification trivial: clone repo @ tag → recompute artifact hashes → compare to manifest hash recorded in tag.

Future (Beta+): Add builder identity, reproducible build hash, SLSA attestation link.
