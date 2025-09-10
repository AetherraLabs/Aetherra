#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Verify release manifest integrity and optional signature.

Checks:
 1. Manifest JSON parses
 2. Each listed artifact exists (relative to dist dir) and sha256 matches
 3. If signature file present (.sig) and public key provided, verify Ed25519
 4. Print concise PASS/FAIL summary and exit non-zero on failure

Usage:
  python tools/verify_release_manifest.py --manifest dist/release-manifest.json --dist dist \
      --pubkey <ed25519_hex_public_key>

Public key optional; if omitted and signature present, a warning is emitted.

Future: support multiple signatures, provenance chain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TRY_NACL = True
try:
    import nacl.encoding  # type: ignore
    import nacl.signing  # type: ignore
except Exception:  # pragma: no cover
    TRY_NACL = False

# Secondary backend: cryptography
TRY_CRYPTO = True
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (  # type: ignore
        Ed25519PublicKey,
    )
except Exception:  # pragma: no cover
    TRY_CRYPTO = False
    Ed25519PublicKey = None  # type: ignore


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_signature(
    manifest_bytes: bytes, sig_hex: str, pub_hex: str
) -> tuple[bool, str | None]:
    # Try PyNaCl first
    if TRY_NACL:
        try:
            vk = nacl.signing.VerifyKey(pub_hex, encoder=nacl.encoding.HexEncoder)  # type: ignore
            vk.verify(manifest_bytes, bytes.fromhex(sig_hex))  # raises on failure
            return True, None
        except Exception as e:  # pragma: no cover
            return False, str(e)
    # Fallback to cryptography
    if TRY_CRYPTO and Ed25519PublicKey is not None:
        try:
            vk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
            vk.verify(bytes.fromhex(sig_hex), manifest_bytes)
            return True, None
        except Exception as e:  # pragma: no cover
            return False, str(e)
    return False, "No Ed25519 backend available (install pynacl or cryptography)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--pubkey", help="Ed25519 public key hex")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[VERIFY][FAIL] manifest missing: {manifest_path}")
        return 2

    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except Exception as e:
        print(f"[VERIFY][FAIL] cannot parse manifest: {e}")
        return 2

    dist_dir = Path(args.dist)
    ok = True

    for art in manifest.get("artifacts", []):
        rel = art.get("path")
        sha = art.get("sha256")
        if not rel or not sha:
            print(f"[VERIFY][FAIL] artifact entry incomplete: {art}")
            ok = False
            continue
        p = dist_dir / rel
        if not p.exists():
            print(f"[VERIFY][FAIL] missing artifact file: {rel}")
            ok = False
            continue
        calc = sha256_file(p)
        if calc != sha:
            print(f"[VERIFY][FAIL] sha mismatch for {rel}: expected {sha} got {calc}")
            ok = False
        else:
            print(f"[VERIFY][OK] {rel} sha256 match")

    sig_path = manifest_path.with_suffix(manifest_path.suffix + ".sig")
    if sig_path.exists():
        sig_hex = sig_path.read_text().strip()
        pub_hex = args.pubkey
        if pub_hex:
            verified, err = verify_signature(
                json.dumps(manifest, sort_keys=True).encode("utf-8"), sig_hex, pub_hex
            )
            if verified:
                print("[VERIFY][OK] signature valid")
            else:
                print(f"[VERIFY][FAIL] signature invalid: {err}")
                ok = False
        else:
            print(
                "[VERIFY][WARN] signature present but no --pubkey provided (skipping verification)"
            )
    else:
        print("[VERIFY][INFO] no signature file present")

    if ok:
        print("[VERIFY][PASS] manifest verified")
        return 0
    print("[VERIFY][FAIL] manifest verification failed")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
