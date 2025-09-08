# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Plugin signing and verification utilities.

- Uses ed25519 if 'nacl' is available; otherwise provides permissive fallbacks.
- Sign manifests (dict) and attach signature+pubkey fields.
- Verify signatures on manifests and hub-catalog entries.

Never fail closed in dev; callers can enforce strict mode via AETHERRA_SIGNING_STRICT=1.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable, Optional

STRICT = os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1"
APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
REVOCATIONS_FILE = APP_DIR / "revocations.json"
TRANSPARENCY_LOG = APP_DIR / "signing_log.jsonl"

try:
    # PyNaCl optional
    from nacl.exceptions import BadSignatureError  # type: ignore
    from nacl.signing import SigningKey, VerifyKey  # type: ignore

    NACL = True
except Exception:
    NACL = False
    SigningKey = None  # type: ignore
    VerifyKey = None  # type: ignore
    BadSignatureError = Exception  # type: ignore


def _manifest_bytes(manifest: dict) -> bytes:
    # Stable JSON canonicalization
    return json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _is_revoked(pubkey_b64: Optional[str], key_id: Optional[str] = None) -> bool:
    try:
        if REVOCATIONS_FILE.exists():
            data = json.loads(REVOCATIONS_FILE.read_text(encoding="utf-8"))
            revoked_keys = set(data.get("pubkeys", []))
            revoked_ids = set(data.get("key_ids", []))
            if pubkey_b64 and pubkey_b64 in revoked_keys:
                return True
            if key_id and key_id in revoked_ids:
                return True
    except Exception:
        return False
    return False


def _append_transparency(entry: dict) -> None:
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with open(TRANSPARENCY_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except Exception:
        pass


def compute_files_hash(paths: Iterable[str]) -> str:
    """Compute a deterministic SHA256 tree hash for a list of file paths."""
    h = hashlib.sha256()
    for p in sorted(paths):
        try:
            h.update(Path(p).read_bytes())
        except Exception:
            # include path marker to avoid silent omission
            h.update(("MISSING:" + p).encode("utf-8"))
    return h.hexdigest()


def generate_keypair(seed: Optional[bytes] = None) -> tuple[str, str]:
    """Return (public_base64, secret_base64)."""
    if not NACL:
        # Fallback: return dummy keys for dev
        dummy = base64.b64encode(b"aetherra-dev-key").decode()
        return dummy, dummy
    sk = SigningKey(seed) if seed else SigningKey.generate()  # type: ignore[call-arg,attr-defined]
    pk = sk.verify_key
    return base64.b64encode(bytes(pk)).decode(), base64.b64encode(bytes(sk)).decode()


def sign_manifest(manifest: dict, secret_b64: Optional[str]) -> dict:
    out = dict(manifest)
    if not secret_b64 or not NACL:
        out.setdefault("signature", None)
        out.setdefault("pubkey", None)
        return out
    sk_bytes = base64.b64decode(secret_b64)
    sk = SigningKey(sk_bytes)  # type: ignore[call-arg]
    sig = sk.sign(_manifest_bytes(manifest)).signature
    out["signature"] = base64.b64encode(sig).decode()
    out["pubkey"] = base64.b64encode(bytes(sk.verify_key)).decode()
    # write transparency entry
    _append_transparency(
        {
            "ts": __import__("time").time(),
            "manifest_name": manifest.get("name"),
            "version": manifest.get("version"),
            "pubkey": out.get("pubkey"),
            "signature": out.get("signature"),
        }
    )
    return out


def verify_plugin_signature(manifest: dict) -> bool:
    sig = manifest.get("signature")
    pub = manifest.get("pubkey")
    if not sig or not pub:
        return not STRICT  # allow if not strict
    if not NACL:
        return not STRICT
    # revocation check
    if _is_revoked(pub, manifest.get("key_id")):
        return False
    try:
        vk = VerifyKey(base64.b64decode(pub))  # type: ignore[call-arg]
        vk.verify(
            _manifest_bytes(
                {k: v for k, v in manifest.items() if k not in ("signature", "pubkey")}
            ),
            base64.b64decode(sig),
        )
        # optional code hash verification when provided
        code_hash = manifest.get("code_hash")
        code_files = manifest.get("code_files")
        if code_hash and isinstance(code_hash, str) and isinstance(code_files, list):
            calculated = compute_files_hash([str(p) for p in code_files])
            if calculated != code_hash:
                return False
        return True
    except BadSignatureError:
        return False
    except Exception:
        return not STRICT
