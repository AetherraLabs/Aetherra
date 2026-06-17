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
- In production profile (AETHERRA_PROFILE=prod|production), strict is on by default
    and a default allowlist is assumed when no policy exists: ["localhost", "127.0.0.1", ".aetherra.dev"].
"""

from __future__ import annotations

# Standard library imports
import json
import logging
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Third party imports
import requests
from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

logger = logging.getLogger(__name__)

APP_DIR = Path(os.path.expanduser("~/.aetherra")).resolve()
POLICY_FILE = APP_DIR / "policy" / "net_policy.json"


def _policy_file() -> Path:
    """Resolve the network policy path at call time.

    Tests and isolated deployments can set AETHERRA_POLICY_HOME to avoid
    mutating the real user profile.
    """
    policy_home = os.getenv("AETHERRA_POLICY_HOME", "").strip()
    if policy_home:
        return Path(policy_home).expanduser().resolve() / "net_policy.json"
    return POLICY_FILE


def _is_production_profile() -> bool:
    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    return profile in {"prod", "production"}


def _strict_net_policy_enabled() -> bool:
    if os.getenv("AETHERRA_PROD_UNSAFE_ALLOW", "0") == "1":
        return False
    return os.getenv("AETHERRA_NET_STRICT", "0") == "1" or _is_production_profile()


def _load_policy() -> dict[str, Any]:
    try:
        policy_file = _policy_file()
        if policy_file.exists():
            data = json.loads(policy_file.read_text(encoding="utf-8") or "{}")
            return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("Failed to load net policy: %s", e)
    # Provide empty dict to allow defaults downstream
    return {}


def _domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        return netloc.split(":")[0].lower()
    except Exception:
        return ""


def _guardian_capability_for_requester(requester: str) -> str:
    if requester == "core:webhook_manager" or requester.endswith(":webhook_manager"):
        return "network:webhook"
    return "network:outbound"


def _guardian_allows_network(
    *,
    url: str,
    requester: str,
    method: str,
) -> bool:
    parsed = urlparse(url)
    domain = _domain_of(url)
    intent = IntentDeclaration(
        requester=requester or "unknown",
        subsystem="network",
        action="network.request",
        target=f"network:{domain or 'unknown'}",
        purpose=f"Perform outbound {method.upper()} request",
        capabilities=(_guardian_capability_for_requester(requester or "unknown"),),
        evidence=(f"network_domain:{domain or 'unknown'}",),
        reversible=False,
        metadata={
            "method": method.upper(),
            "scheme": parsed.scheme,
            "path_length": len(parsed.path or ""),
        },
    )
    decision = evaluate_intent(intent)
    return decision.status in {GuardianStatus.ALLOW, GuardianStatus.ALLOW_LIMITED}


def is_domain_allowed(url: str, requester: str) -> bool:
    dom = _domain_of(url)
    pol = _load_policy()
    allow = list(pol.get("allow_domains", []) or [])
    deny = set(pol.get("deny_domains", []) or [])
    # Default allowlist in production when none provided
    if _is_production_profile() and not allow:
        allow = ["localhost", "127.0.0.1", ".aetherra.dev"]
    allow = set(allow)
    strict = _strict_net_policy_enabled()

    if dom in deny:
        logger.warning("Net policy deny: %s -> %s", requester, dom)
        return False
    # Exact or wildcard/suffix allow matches (e.g., '*.example.com' or '.example.com')
    if dom in allow:
        return True
    for entry in allow:
        try:
            e = str(entry).strip().lower()
            if e.startswith("*."):
                suffix = e[1:]  # keep leading dot
                if dom.endswith(suffix):
                    return True
            elif e.startswith("."):
                if dom.endswith(e):
                    return True
        except Exception:
            continue
    if strict:
        logger.warning("Net policy strict deny (not in allow list): %s -> %s", requester, dom)
        return False
    logger.info("Net policy pass (no explicit rule): %s -> %s", requester, dom)
    return True


def http_post(
    url: str,
    json_payload: dict[str, Any],
    timeout: float = 10.0,
    requester: str = "unknown",
    headers: Mapping[str, str] | None = None,
) -> requests.Response | None:
    if not is_domain_allowed(url, requester):
        return None
    if not _guardian_allows_network(url=url, requester=requester, method="POST"):
        logger.warning("Guardian blocked HTTP POST: %s -> %s", requester, _domain_of(url))
        return None
    try:
        return requests.post(url, json=json_payload, timeout=timeout, headers=headers)
    except requests.RequestException as e:
        logger.warning("HTTP POST failed: %s -> %s", url, e)
        return None


def http_get(
    url: str,
    timeout: float = 10.0,
    requester: str = "unknown",
    headers: Mapping[str, str] | None = None,
) -> requests.Response | None:
    if not is_domain_allowed(url, requester):
        return None
    if not _guardian_allows_network(url=url, requester=requester, method="GET"):
        logger.warning("Guardian blocked HTTP GET: %s -> %s", requester, _domain_of(url))
        return None
    try:
        return requests.get(url, timeout=timeout, headers=headers)
    except requests.RequestException as e:
        logger.warning("HTTP GET failed: %s -> %s", url, e)
        return None
