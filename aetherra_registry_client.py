# SPDX-License-Identifier: GPL-3.0-or-later
"""
HTTP client for the Aetherra Registry Daemon.
Falls back to no-op when AETHERRA_REGISTRY_URL is not set.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except Exception:  # pragma: no cover - optional dep
    requests = None


def _base_url() -> str | None:
    url = os.environ.get("AETHERRA_REGISTRY_URL", "").strip()
    return url or None


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _daemon_host(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or parsed.path or "unknown"


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "registry_daemon_client" and capability in {
        "registry:register",
        "registry:status",
        "registry:heartbeat",
        "network:outbound",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_daemon_call(
    *,
    action: str,
    base_url: str,
    service_name: str | None = None,
    status: str | None = None,
    metadata: dict[str, Any] | None = None,
    endpoints: dict[str, Any] | None = None,
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = (
        os.environ.get("AETHERRA_PRINCIPAL", "").strip() or "registry_daemon_client"
    )
    approval_id = os.environ.get("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    if action.endswith("heartbeat"):
        registry_capability = "registry:heartbeat"
    elif action.endswith(("status", "update")):
        registry_capability = "registry:status"
    else:
        registry_capability = "registry:register"
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="service_registry",
            action=action,
            target=f"registry_daemon:{_daemon_host(base_url)}",
            purpose="Forward Service Registry state to the external registry daemon",
            capabilities=(registry_capability, "network:outbound"),
            evidence=("aetherra_registry_client",),
            reversible=True,
            rollback_plan="send a compensating registry update or remove stale daemon registration",
            metadata={
                "daemon_host_hash": _hash_value(_daemon_host(base_url)),
                "service_name": service_name,
                "status": status,
                "metadata_keys": tuple(sorted(str(key) for key in metadata or {})),
                "endpoint_keys": tuple(sorted(str(key) for key in endpoints or {})),
                "operation": action.rsplit(".", 1)[-1],
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def http_get_status() -> dict[str, Any] | None:
    base = _base_url()
    if not base or not requests:
        return None
    try:
        decision = _guardian_preflight_daemon_call(
            action="service_registry.daemon_status",
            base_url=base,
        )
        if not decision.allowed:
            return None
        r = requests.get(f"{base}/api/registry/status", timeout=2.0)
        if r.status_code == 200:
            js = r.json()
            if isinstance(js, dict):
                return js
    except Exception:
        return None
    return None


def http_register_service(
    name: str,
    *,
    status: str = "starting",
    metadata: dict[str, Any] | None = None,
    endpoints: dict[str, str] | None = None,
) -> bool:
    base = _base_url()
    if not base or not requests:
        return False
    try:
        metadata = metadata or {}
        endpoints = endpoints or {}
        decision = _guardian_preflight_daemon_call(
            action="service_registry.daemon_register",
            base_url=base,
            service_name=name,
            status=status,
            metadata=metadata,
            endpoints=endpoints,
        )
        if not decision.allowed:
            return False
        payload = {
            "name": name,
            "status": status,
            "metadata": metadata,
            "endpoints": endpoints,
        }
        r = requests.post(f"{base}/api/registry/register", json=payload, timeout=2.0)
        return r.status_code == 200 and bool((r.json() or {}).get("ok"))
    except Exception:
        return False


essential_services = (
    "kernel_loop",
    "aetherra_engine",
    "module_manager",
    "event_bus",
    "memory_system",
)


def http_update(
    name: str, *, status: str | None = None, metadata: dict[str, Any] | None = None
) -> bool:
    base = _base_url()
    if not base or not requests:
        return False
    try:
        decision = _guardian_preflight_daemon_call(
            action="service_registry.daemon_update",
            base_url=base,
            service_name=name,
            status=status,
            metadata=metadata,
        )
        if not decision.allowed:
            return False
        payload: dict[str, Any] = {"name": name}
        if status:
            payload["status"] = status
        if metadata:
            payload["metadata"] = metadata
        r = requests.post(f"{base}/api/registry/update", json=payload, timeout=2.0)
        return r.status_code == 200 and bool((r.json() or {}).get("ok"))
    except Exception:
        return False


def http_heartbeat(name: str) -> bool:
    base = _base_url()
    if not base or not requests:
        return False
    try:
        decision = _guardian_preflight_daemon_call(
            action="service_registry.daemon_heartbeat",
            base_url=base,
            service_name=name,
        )
        if not decision.allowed:
            return False
        r = requests.post(
            f"{base}/api/registry/heartbeat", json={"name": name}, timeout=2.0
        )
        return r.status_code == 200 and bool((r.json() or {}).get("ok"))
    except Exception:
        return False
