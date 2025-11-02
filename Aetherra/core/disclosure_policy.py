# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Disclosure Policy — Safe Autonomy Layers

Centralized helpers to enforce tiered disclosure controls:
- free (Observation Layer): metadata-only, no code/patch content, no writes
- reflect (Reflection Layer): structured descriptions allowed, still no raw patch
- integrate (Integration Layer): full capability

Use is_free(), allow_reflection(), allow_integration(), and redact_payload() to
apply policy across APIs and UI layers without disabling services.
"""

from __future__ import annotations

import os
from typing import Any

TIERS = ("free", "reflect", "integrate")


def get_tier() -> str:
    tier = (os.environ.get("AETHERRA_DISCLOSURE_TIER", "free") or "free").strip().lower()
    if tier not in TIERS:
        return "free"
    return tier


def is_free() -> bool:
    return get_tier() == "free"


def allow_reflection() -> bool:
    return get_tier() in ("reflect", "integrate")


def allow_integration() -> bool:
    return get_tier() == "integrate"


_REDACT_KEYS = {
    # typical content-bearing keys to strip or summarize
    "diff",
    "patch",
    "code",
    "content",
    "files",
    "file_list",
    "lines",
    "chunks",
    "unified_diff",
    "raw",
    "details",
    "plan_steps",
}


def _summarize(obj: Any) -> Any:
    try:
        if isinstance(obj, (list, tuple, set)):
            return {"count": len(obj)}
        if isinstance(obj, dict):
            return {"keys": len(obj), "items": min(len(obj), 10)}
        s = str(type(obj)).split("'")[1]
        return {"type": s}
    except Exception:
        return {"summary": "redacted"}


def redact_payload(data: Any) -> Any:
    """Return a metadata-only representation suitable for the Free tier.

    - Removes or summarizes code/diff/patch-bearing fields
    - Keeps counts and high-level status
    """
    try:
        if data is None:
            return None
        if isinstance(data, (str, bytes)):
            # Never return raw strings in free mode (might be code); replace with hint
            return {"message": "Details available in higher tiers"}
        if isinstance(data, list):
            return {"count": len(data)}
        if isinstance(data, dict):
            out: dict[str, Any] = {}
            for k, v in data.items():
                lk = str(k).lower()
                if lk in _REDACT_KEYS:
                    out[k] = _summarize(v)
                    continue
                # Block obvious content-like values
                if isinstance(v, (bytes, bytearray)):
                    out[k] = {"bytes": len(v)}
                    continue
                if isinstance(v, str) and ("\n" in v or v.strip().startswith("diff ")):
                    out[k] = {"message": "Redacted"}
                    continue
                # Recurse for nested
                if isinstance(v, (dict, list, tuple)):
                    out[k] = redact_payload(v)
                else:
                    out[k] = v
            # Add tier marker
            out.setdefault("disclosure_tier", get_tier())
            return out
        # Fallback: summarize unknown types
        return _summarize(data)
    except Exception:
        return {"message": "Redacted", "disclosure_tier": get_tier()}


def deny_message(action: str) -> dict[str, Any]:
    tier = get_tier()
    if tier == "free":
        note = (
            "This is the Observation Layer. I can report opportunities, but I "
            "won't display code, patches, or apply changes."
        )
    elif tier == "reflect":
        note = (
            "This is the Reflection Layer. I can describe improvements, but I "
            "won't display raw patch content."
        )
    else:
        note = ""
    return {
        "ok": False,
        "tier": tier,
        "action": action,
        "message": "Upgrade required for this operation",
        "note": note,
    }
