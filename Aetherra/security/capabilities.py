# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Simple capability policy checks for Aetherra components and plugins.

Policy file (optional): ~/.aetherra/policy/capabilities.json
{
  "allow": {
    "core:webhook_manager": ["network:outbound", "network:webhook"]
  }
}

Behavior:
- Default allow in dev/staging. Deny-by-default in production profile.
- Strict enforcement is enabled if either:
    - AETHERRA_REQUIRE_CAPABILITIES=1, or
    - AETHERRA_PROFILE is 'prod' or 'production'.
    In strict mode, access is denied unless explicitly granted by policy.
"""

from __future__ import annotations

# Standard library imports
import json
import logging
import os
from pathlib import Path
from threading import RLock

logger = logging.getLogger(__name__)

APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
POLICY_FILE = APP_DIR / "policy" / "capabilities.json"

# Ephemeral (in-process) grants layered on top of policy file contents.
# Tests can safely grant capabilities without mutating user policy state.
_EPHEMERAL_GRANTS: dict[str, set[str]] = {}
_LOCK = RLock()

__all__ = [
    "has_capability",
    "check_capability",
    "grant_capability",
    "revoke_capability",
    "list_capabilities",
    "get_capability_limits",
]


def _load_policy_full() -> dict:
    """Load full capabilities policy JSON (allow + optional limits).

    Structure:
    {
      "allow": { "requester": ["cap1", "cap2"] },
      "limits": { "capability": { "timeout_sec": 10, "max_concurrency": 1 } }
    }
    """
    try:
        if POLICY_FILE.exists():
            data = json.loads(POLICY_FILE.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.warning("Failed to load capabilities policy: %s", e)
    return {}


def _load_policy() -> dict[str, list[str]]:
    """Load only the allow map from the capabilities policy."""
    data = _load_policy_full()
    allow = data.get("allow", {}) if isinstance(data, dict) else {}
    try:
        if isinstance(allow, dict):
            return {str(k): list(v) for k, v in allow.items() if isinstance(v, list)}
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.debug("Failed loading capability policy file %s: %s", POLICY_FILE, exc)
    return {}


def get_capability_limits(capability: str) -> dict:
    """Return per-capability limits from policy, if any.

    Example capabilities.json:
    {
      "allow": { "core:webhook_manager": ["network:webhook"] },
      "limits": {
        "network:outbound": { "timeout_sec": 10, "max_concurrency": 1 },
        "network:webhook": { "timeout_sec": 8 }
      }
    }
    """
    try:
        cap = (capability or "").strip()
        if not cap:
            return {}
        data = _load_policy_full()
        limits = data.get("limits") if isinstance(data, dict) else None
        if isinstance(limits, dict):
            cfg = limits.get(cap)
            if isinstance(cfg, dict):
                # Shallow copy to avoid accidental mutation
                return dict(cfg)
    except Exception as e:
        logger.debug("capabilities.get_capability_limits error: %s", e)
    return {}


def has_capability(requester: str, capability: str) -> bool:
    """Return True if requester is allowed the named capability.

    Strict mode with AETHERRA_REQUIRE_CAPABILITIES=1 denies by default.
    Otherwise, default allow but log a warning when not explicitly granted.
    """
    requester = requester or "unknown"
    capability = capability or "unknown"
    allow_map = _load_policy()
    allowed = capability in allow_map.get(requester, [])

    # Strict when explicitly enabled or when running in production profile
    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    strict_env = os.getenv("AETHERRA_REQUIRE_CAPABILITIES", "0") == "1"
    strict = strict_env or profile in ("prod", "production")
    if strict and not allowed:
        logger.warning("Capability denied (strict): %s -> %s", requester, capability)
        return False
    if not allowed:
        logger.info("Capability denied (no explicit grant): %s -> %s", requester, capability)
        # Enforce deny by default unless permissive override set
        if not os.environ.get("AETHERRA_CAPABILITIES_PERMISSIVE"):
            return False
    return True


# --- Public API expected by tests -------------------------------------------------


def _normalize(value: str | None) -> str:
    return (value or "").strip()


def grant_capability(requester: str, capability: str) -> bool:
    """Grant a capability ephemerally for this process.

    Returns True if the grant was added (or already present). Empty inputs are ignored.
    """
    r = _normalize(requester) or "unknown"
    c = _normalize(capability)
    # Reject obviously invalid capability tokens (empty, wildcard only, malformed dot patterns)
    if not c or c.startswith(".") or c.endswith(".") or ".." in c:
        return False
    with _LOCK:
        bucket = _EPHEMERAL_GRANTS.setdefault(r, set())
        bucket.add(c)
    return True


def revoke_capability(requester: str, capability: str) -> bool:
    """Revoke an ephemerally granted capability.

    Returns True if it was present, False otherwise.
    """
    r = _normalize(requester) or "unknown"
    c = _normalize(capability)
    with _LOCK:
        bucket = _EPHEMERAL_GRANTS.get(r)
        if not bucket or c not in bucket:
            return False
        bucket.discard(c)
        if not bucket:
            _EPHEMERAL_GRANTS.pop(r, None)
        return True


def list_capabilities(requester: str) -> list[str]:
    """List all capabilities (policy + ephemeral) for a requester."""
    r = _normalize(requester) or "unknown"
    policy_map = _load_policy()
    with _LOCK:
        ephem = _EPHEMERAL_GRANTS.get(r, set())
        combined = set(policy_map.get(r, [])) | set(ephem)
    return sorted(combined)


def check_capability(requester: str, capability: str) -> bool:
    """Check if requester has capability (ephemeral or policy).

    Mirrors the historical interface expected by tests. Uses ephemeral grants
    first (no warning), then falls back to policy-based `has_capability`.
    """
    r = _normalize(requester) or "unknown"
    c = _normalize(capability)
    if not c:
        logger.info("cap_check: empty capability for requester=%s", r)
        return False
    # Invalid structural patterns never allowed
    if c.startswith(".") or c.endswith(".") or ".." in c:
        logger.info("cap_check: invalid pattern %s for requester=%s", c, r)
        return False
    # If requester was empty/None originally and we normalized to 'unknown', deny by default
    if not requester:
        logger.info("cap_check: empty requester for capability=%s", c)
        return False
    policy_map = _load_policy()
    # Only honor ephemeral grants for principals that exist in policy (prevents leakage from other tests)
    if r in policy_map:
        with _LOCK:
            if c in _EPHEMERAL_GRANTS.get(r, set()):
                logger.info("cap_check: ephemeral grant allow %s -> %s", r, c)
                return True
    else:
        # Unknown principal -> deny regardless of earlier ephemeral grants
        logger.info("cap_check: unknown principal deny %s -> %s", r, c)
        return False
    # Fall back to policy evaluation for known principal
    allowed = has_capability(r, c)
    logger.info("cap_check: policy evaluation %s -> %s result=%s", r, c, allowed)
    return allowed
