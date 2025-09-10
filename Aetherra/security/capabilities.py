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


def _load_policy() -> dict[str, list[str]]:
    try:
        if POLICY_FILE.exists():
            data = json.loads(POLICY_FILE.read_text(encoding="utf-8") or "{}")
            allow = data.get("allow", {})
            if isinstance(allow, dict):
                return {str(k): list(v) for k, v in allow.items() if isinstance(v, list)}
    except Exception as e:
        logger.warning("Failed to load capabilities policy: %s", e)
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
