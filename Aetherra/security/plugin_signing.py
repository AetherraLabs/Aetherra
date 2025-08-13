"""
Plugin signing and verification utilities.

- Uses ed25519 if 'nacl' is available; otherwise provides permissive fallbacks.
- Sign manifests (dict) and attach signature+pubkey fields.
- Verify signatures on manifests and hub-catalog entries.

Never fail closed in dev; callers can enforce strict mode via AETHERRA_SIGNING_STRICT=1.
"""

from __future__ import annotations

import base64
import json
import os
from typing import Optional, Tuple

STRICT = os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1"

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


def generate_keypair(seed: Optional[bytes] = None) -> Tuple[str, str]:
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
    return out


def verify_plugin_signature(manifest: dict) -> bool:
    sig = manifest.get("signature")
    pub = manifest.get("pubkey")
    if not sig or not pub:
        return not STRICT  # allow if not strict
    if not NACL:
        return not STRICT
    try:
        vk = VerifyKey(base64.b64decode(pub))  # type: ignore[call-arg]
        vk.verify(
            _manifest_bytes(
                {k: v for k, v in manifest.items() if k not in ("signature", "pubkey")}
            ),
            base64.b64decode(sig),
        )
        return True
    except BadSignatureError:
        return False
    except Exception:
        return not STRICT
