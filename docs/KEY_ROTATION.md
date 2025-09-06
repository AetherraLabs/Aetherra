<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Aetherra Key Rotation & Signing Appendix

This appendix defines the minimal operational procedure for rotating cryptographic keys used in:

- Release manifest signing (Ed25519)
- Workflow / .aether file signing
- Future transparency log anchoring

## 1. Key Classes

| Class                    | Purpose                              | Default Lifetime        | Storage                                     |
| ------------------------ | ------------------------------------ | ----------------------- | ------------------------------------------- |
| Release Signing Key      | Sign release manifest & SBOM summary | 12 months (recommend 6) | `keys/release_signing_ed25519` (restricted) |
| Workflow Signing Key     | Sign .aether workflows (developer)   | 6 months                | Developer local keystore                    |
| Emergency Revocation Key | Issue revocation statements          | 24 months               | Offline / cold                              |

## 2. Rotation Triggers

Rotation MUST occur if any of:

1. Expiry window reached (T - 30 days).
2. Suspected compromise (immediate emergency rotation).
3. Cryptographic deprecation (algorithm weakness disclosure).
4. Personnel change triggering trust boundary update.

## 3. Standard Rotation Procedure (Release Key)

1. Generate new key pair:

   ```bash
   python tools/sign_release_manifest.py --gen-key --out keys/release_signing_ed25519.new
   ```
2. Derive public fingerprint (first 16 hex chars of pubkey hash) and record in `OWNERSHIP.md` under Pending Keys.
3. Dual-sign the next release manifest with BOTH old and new keys (transition release).
4. Publish manifest + fingerprints; update `aetherra_plugin_catalog.json` trust metadata if required.
5. After successful verification window (>= 7 days, no disputes), archive old private key (encrypted) or destroy if policy mandates.
6. Promote `.new` to active path name; remove `.new` suffix.
7. Update provenance record (planned transparency log) with rotation event.

## 4. Emergency Rotation (Compromise)

1. Revoke old key: create `revocations/<timestamp>_revocation.json` containing:

   ```json
   {"type":"revocation","reason":"compromise","fingerprint":"<old_fp>","ts":<unix>}
   ```
2. Commit + push revocation file, broadcast in release notes.
3. Invalidate any unsigned or singly-signed artifacts built after compromise timestamp.
4. Force clients / CI gate to reject manifests signed only by revoked key.
5. Issue hotfix release signed with emergency key + new primary.

## 5. Verification Rules (Target State)

| Artifact           | Required Signatures                       | Accepts Overlap | Reject Conditions                    |
| ------------------ | ----------------------------------------- | --------------- | ------------------------------------ |
| Release Manifest   | >=1 Active OR (Old+New during transition) | Yes             | Revoked-only, Missing, Tampered hash |
| Workflow (.aether) | 1 Developer key                           | N/A             | Unknown key, Expired, Revoked        |

## 6. Storage & Protection

- Private keys chmod 600 (or Windows equivalent ACL), never committed.
- Optional KMS integration in future (AWS KMS / Hashicorp Vault) – tracked in roadmap.
- Public keys and fingerprints committed to repository under `keys/` (pub only).

## 7. Auditing

Planned metrics to add to `tools/quality_gates.py`:

- Detect presence of at least one active signing key (public part).
- Warn if key age > 80% of lifetime window.
- Fail if revocation exists without a replacement key committed.

## 8. Future Enhancements

- Transparency log anchoring (Merkle root per release cycle).
- Multi-sig threshold (m-of-n maintainers) for release manifests.
- Automated key age telemetry into Hub admin panel.
- Hardware-backed keys (YubiKey Ed25519) for release chain.

## 9. Quick Reference Commands

```bash
# Generate new release key (Ed25519)
python tools/sign_release_manifest.py --gen-key --out keys/release_signing_ed25519.new

# Sign manifest with explicit key
python tools/sign_release_manifest.py --manifest dist/release_manifest.json --key keys/release_signing_ed25519

# Verify manifest signature
python tools/verify_release_manifest.py --manifest dist/release_manifest.json --pub keys/release_signing_ed25519.pub
```


---
Referenced by: `THREAT_MODEL.md`, `OWNERSHIP.md`, `PACKAGING_AND_RELEASE.md`.
