# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Network policy helpers and safe HTTP wrappers.

Policy file (optional): ~/.aetherra/policy/net_policy.json
{
  "allow_domains": ["example.com", "api.aetherra.ai"],
  "deny_domains": ["malicious.test"]
}

Env:
- AETHERRA_NET_STRICT=1 → deny if domain not explicitly allowed.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
POLICY_FILE = APP_DIR / "policy" / "net_policy.json"


def _load_policy() -> Dict[str, Any]:
    try:
        if POLICY_FILE.exists():
            data = json.loads(POLICY_FILE.read_text(encoding="utf-8") or "{}")
            return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("Failed to load net policy: %s", e)
    return {}


def _domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        return netloc.split(":")[0].lower()
    except Exception:
        return ""


def is_domain_allowed(url: str, requester: str) -> bool:
    dom = _domain_of(url)
    pol = _load_policy()
    allow = set(pol.get("allow_domains", []) or [])
    deny = set(pol.get("deny_domains", []) or [])
    strict = os.getenv("AETHERRA_NET_STRICT", "0") == "1"

    if dom in deny:
        logger.warning("Net policy deny: %s -> %s", requester, dom)
        return False
    if dom in allow:
        return True
    if strict:
        logger.warning(
            "Net policy strict deny (not in allow list): %s -> %s", requester, dom
        )
        return False
    logger.info("Net policy pass (no explicit rule): %s -> %s", requester, dom)
    return True


def http_post(
    url: str,
    json_payload: Dict[str, Any],
    timeout: float = 10.0,
    requester: str = "unknown",
) -> Optional[requests.Response]:
    if not is_domain_allowed(url, requester):
        return None
    try:
        return requests.post(url, json=json_payload, timeout=timeout)
    except requests.RequestException as e:
        logger.warning("HTTP POST failed: %s -> %s", url, e)
        return None


def http_get(
    url: str, timeout: float = 10.0, requester: str = "unknown"
) -> Optional[requests.Response]:
    if not is_domain_allowed(url, requester):
        return None
    try:
        return requests.get(url, timeout=timeout)
    except requests.RequestException as e:
        logger.warning("HTTP GET failed: %s -> %s", url, e)
        return None
