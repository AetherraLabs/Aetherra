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

# Standard library imports
import base64
import hashlib
import json
import logging
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

STRICT = os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1"
APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
REVOCATIONS_FILE = APP_DIR / "revocations.json"
TRANSPARENCY_LOG = APP_DIR / "signing_log.jsonl"

try:
    # PyNaCl optional (fast path)
    # Third party imports
    from nacl.exceptions import BadSignatureError  # type: ignore
    from nacl.signing import SigningKey, VerifyKey  # type: ignore

    NACL = True
except Exception:
    NACL = False
    SigningKey = None  # type: ignore
    VerifyKey = None  # type: ignore
    BadSignatureError = Exception  # type: ignore

# Secondary fallback: cryptography's Ed25519
CRYPTO = True
try:
    # Third party imports
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (  # type: ignore
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives.serialization import (  # type: ignore
        Encoding,
        NoEncryption,
        PrivateFormat,
        PublicFormat,
    )
except Exception:  # pragma: no cover
    CRYPTO = False
    Ed25519PrivateKey = cast(Any, None)  # type: ignore
    Ed25519PublicKey = cast(Any, None)  # type: ignore
    Encoding = cast(Any, None)  # type: ignore
    NoEncryption = cast(Any, None)  # type: ignore
    PrivateFormat = cast(Any, None)  # type: ignore
    PublicFormat = cast(Any, None)  # type: ignore


def _manifest_bytes(manifest: dict) -> bytes:
    # Stable JSON canonicalization
    return json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _is_revoked(pubkey_b64: str | None, key_id: str | None = None) -> bool:
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
    except Exception as exc:  # pragma: no cover
        logging.debug("plugin_signing.transparency_append_failed: %s", exc)


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


def generate_keypair(seed: bytes | None = None) -> tuple[str, str]:
    """Return (public_base64, secret_base64) for Ed25519.

    Uses PyNaCl when available; otherwise falls back to cryptography. If neither is
    available, returns a deterministic dev dummy keypair.
    """
    if NACL:
        sk = SigningKey(seed) if seed else SigningKey.generate()  # type: ignore[call-arg,attr-defined]
        pk = sk.verify_key
        return (
            base64.b64encode(bytes(pk)).decode(),
            base64.b64encode(bytes(sk)).decode(),
        )
    if CRYPTO:
        # cryptography doesn't support seeding directly; ignore seed in fallback
        sk = Ed25519PrivateKey.generate()
        pk = sk.public_key()
        pk_raw = pk.public_bytes(Encoding.Raw, PublicFormat.Raw)
        sk_raw = sk.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        return base64.b64encode(pk_raw).decode(), base64.b64encode(sk_raw).decode()
    # Last-resort dev dummy keys (do not use in production)
    dummy = base64.b64encode(b"aetherra-dev-key").decode()
    return dummy, dummy


def sign_manifest(manifest: dict, secret_b64: str | None) -> dict:
    out = dict(manifest)
    if not secret_b64:
        out.setdefault("signature", None)
        out.setdefault("pubkey", None)
        return out
    msg = _manifest_bytes(manifest)
    try:
        if NACL:
            sk = SigningKey(base64.b64decode(secret_b64))  # type: ignore[call-arg]
            sig = sk.sign(msg).signature
            out["signature"] = base64.b64encode(sig).decode()
            out["pubkey"] = base64.b64encode(bytes(sk.verify_key)).decode()
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
        if CRYPTO:
            sk_raw = base64.b64decode(secret_b64)
            sk = Ed25519PrivateKey.from_private_bytes(sk_raw)
            sig = sk.sign(msg)
            out["signature"] = base64.b64encode(sig).decode()
            pk_raw = sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
            out["pubkey"] = base64.b64encode(pk_raw).decode()
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
    except Exception as exc:  # pragma: no cover - signature fallback
        logging.debug("plugin_signing.sign_manifest_failed: %s", exc)
    out.setdefault("signature", None)
    out.setdefault("pubkey", None)
    return out


def verify_plugin_signature(manifest: dict) -> bool:
    sig = manifest.get("signature")
    pub = manifest.get("pubkey")
    if not sig or not pub:
        return not STRICT  # allow if not strict
    # revocation check
    if _is_revoked(pub, manifest.get("key_id")):
        return False
    msg = _manifest_bytes(
        {k: v for k, v in manifest.items() if k not in ("signature", "pubkey")}
    )
    # Try PyNaCl, then cryptography
    if NACL:
        try:
            vk = VerifyKey(base64.b64decode(pub))  # type: ignore[call-arg]
            vk.verify(msg, base64.b64decode(sig))
            ok_v = True
        except BadSignatureError:
            ok_v = False
        except Exception:
            ok_v = False
    elif CRYPTO:
        try:
            vk = Ed25519PublicKey.from_public_bytes(base64.b64decode(pub))
            vk.verify(base64.b64decode(sig), msg)
            ok_v = True
        except Exception:
            ok_v = False
    else:
        # No crypto libs available: in strict mode, fail closed when a signature is present
        return not STRICT
    if not ok_v:
        return False
    # optional code hash verification when provided
    code_hash = manifest.get("code_hash")
    code_files = manifest.get("code_files")
    if code_hash and isinstance(code_hash, str) and isinstance(code_files, list):
        calculated = compute_files_hash([str(p) for p in code_files])
        if calculated != code_hash:
            return False
    return True


def validate_plugin_signature(plugin_data: dict) -> dict:
    """Validate plugin signature structure for tests.

    Returns a result dict with minimal fields:
      {"name": str, "valid": bool, "reason": str | None}
    Always graceful on malformed input; never raises.
    """
    name = str(plugin_data.get("name", "")) if isinstance(plugin_data, dict) else ""
    manifest = plugin_data if isinstance(plugin_data, dict) else {}
    try:
        valid = verify_plugin_signature(manifest)
        return {
            "name": name,
            "valid": bool(valid),
            "reason": None if valid else "invalid_signature",
        }
    except Exception as e:  # pragma: no cover - defensive
        return {"name": name, "valid": False, "reason": str(e)}


__all__ = [
    "generate_keypair",
    "sign_manifest",
    "verify_plugin_signature",
    "validate_plugin_signature",
]
