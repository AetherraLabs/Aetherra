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

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
POLICY_FILE = APP_DIR / "policy" / "capabilities.json"


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
    except Exception:
        pass
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
        logger.info("Capability used without explicit grant: %s -> %s", requester, capability)
    return True
