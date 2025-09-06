#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Create and (optionally) sign a release manifest of built artifacts.

Manifest fields:
- version
- artifacts: list[{ path, sha256 }]
- sbom (optional reference)
- generated_at (iso8601)
- signing: { tool_version, key_hint } when signing enabled

Signing (simple alpha approach):
- If AETHERRA_RELEASE_PRIVKEY (ed25519 hex) is set, create detached signature
  file <manifest>.sig (hex) using pynacl.
- Otherwise, manifest is emitted unsigned.

Usage:
  python tools/sign_release_manifest.py --dist dist --version 0.1.0-alpha.1 --sbom dist/aetherra-sbom.json

Future: integrate formal key management, multiple signatures, provenance (SLSA).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

# (No additional typing imports required)

TRY_NACL = True
try:
    import nacl.encoding  # type: ignore
    import nacl.signing  # type: ignore
except Exception:  # pragma: no cover
    TRY_NACL = False


def hash_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_artifacts(dist_dir: Path) -> list[dict[str, str]]:
    artifacts: list[dict[str, str]] = []
    for p in dist_dir.glob("*"):
        if p.is_file():
            artifacts.append({"path": p.name, "sha256": hash_file(p)})
    return artifacts


def maybe_sign(
    manifest_bytes: bytes, key_hex: str | None
) -> tuple[str | None, str | None]:
    if not key_hex:
        return None, None
    if not TRY_NACL:
        return None, "PyNaCl not available"
    try:
        key = nacl.signing.SigningKey(key_hex, encoder=nacl.encoding.HexEncoder)  # type: ignore
        sig = key.sign(manifest_bytes).signature.hex()
        return sig, None
    except Exception as e:  # pragma: no cover
        return None, str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--version", required=True)
    ap.add_argument("--sbom")
    ap.add_argument("--output", default="dist/release-manifest.json")
    args = ap.parse_args()

    dist_path = Path(args.dist)
    if not dist_path.exists():
        print(f"[MANIFEST] dist path missing: {dist_path}")
        return 2

    artifacts = collect_artifacts(dist_path)
    # Optional lock hash for provenance
    lock_path = Path("requirements.lock")
    lock_hash = hash_file(lock_path) if lock_path.exists() else None

    manifest = {
        "version": args.version,
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "artifacts": artifacts,
        "provenance": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "implementation": platform.python_implementation(),
            "lock_hash": lock_hash,
        },
    }
    if args.sbom:
        sbom_rel = os.path.relpath(args.sbom, dist_path)
        manifest["sbom"] = sbom_rel

    key_hex = os.getenv("AETHERRA_RELEASE_PRIVKEY")
    sig, err = maybe_sign(json.dumps(manifest, sort_keys=True).encode("utf-8"), key_hex)
    if sig:
        key_hint = (key_hex[:8] + "...") if key_hex else "unknown"
        manifest["signing"] = {"tool_version": "alpha", "key_hint": key_hint}
    elif err:
        manifest["signing_warning"] = err

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2))
    print(f"[MANIFEST] wrote {out_path}")
    if sig:
        sig_path = out_path.with_suffix(out_path.suffix + ".sig")
        sig_path.write_text(sig)
        print(f"[MANIFEST] signature -> {sig_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
