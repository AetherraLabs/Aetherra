# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Script signing utilities for .aether source files.

Design goals:
- Simple, offline-friendly signing using HMAC-SHA256 with a workspace-local secret
- Embed signature as a first-line comment `# @signature: <hex>` to keep files portable
- Optional strict verification controlled by AETHERRA_SCRIPT_VERIFY_STRICT=1

For higher-assurance signing (ed25519), extend this module to use PyNaCl similarly
to plugin signing, but keep HMAC as a default path to avoid mandatory deps.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Tuple

try:
    # Preferred: use the API key store if available
    from Aetherra.security.api_keys import get_key  # type: ignore
except Exception:  # pragma: no cover - optional import
    get_key = None  # type: ignore

SIGNATURE_MARKER = "# @signature:"
DEFAULT_KEY_NAME = "aether_script_signing_secret"


def _get_secret_bytes() -> bytes:
    if get_key:
        key = get_key(DEFAULT_KEY_NAME)
        if key:
            return key.encode("utf-8")
    # Fallback dev secret. Replace in production via api_keys store.
    return b"aetherra-dev-signing-secret"


def _compute_signature(payload: bytes) -> str:
    secret = _get_secret_bytes()
    mac = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return mac


def _split_header_and_body(script_content: str) -> Tuple[str, str]:
    """
    Split header and body without normalizing newlines.

    If the first line starts with the signature marker, return that full line
    (sans trailing CR/LF) as header and the remainder of the text exactly as
    found on disk as body. This preserves CRLF vs LF so signatures computed
    over the body remain stable across platforms.
    """
    if script_content.startswith(SIGNATURE_MARKER):
        # Find the first newline position (handles both LF and CRLF by using \n)
        nl = script_content.find("\n")
        if nl == -1:
            # Single-line file with just header
            line = script_content.rstrip("\r\n")
            return line, ""
        # Header line without trailing CR/LF; body is everything after the first \n
        header_line = script_content[:nl].rstrip("\r\n")
        body = script_content[nl + 1 :]
        return header_line, body
    return "", script_content


def embed_signature(script_content: str) -> str:
    header, body = _split_header_and_body(script_content)
    body_bytes = body.encode("utf-8")
    sig = _compute_signature(body_bytes)
    signed_header = f"{SIGNATURE_MARKER} {sig}"
    return f"{signed_header}\n{body}"


def verify_embedded_signature(script_content: str) -> Tuple[bool, str]:
    header, body = _split_header_and_body(script_content)
    if not header:
        return False, "missing signature header"
    try:
        _, provided = header.split(":", 1)
        provided = provided.strip()
    except ValueError:
        return False, "invalid signature header format"
    expected = _compute_signature(body.encode("utf-8"))
    if hmac.compare_digest(provided, expected):
        return True, "ok"
    return False, "signature mismatch"
