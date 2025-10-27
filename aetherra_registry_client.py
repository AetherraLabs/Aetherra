# SPDX-License-Identifier: GPL-3.0-or-later
"""
HTTP client for the Aetherra Registry Daemon.
Falls back to no-op when AETHERRA_REGISTRY_URL is not set.
"""

from __future__ import annotations

import os
from typing import Any

try:
    import requests
except Exception:  # pragma: no cover - optional dep
    requests = None


def _base_url() -> str | None:
    url = os.environ.get("AETHERRA_REGISTRY_URL", "").strip()
    return url or None


def http_get_status() -> dict[str, Any] | None:
    base = _base_url()
    if not base or not requests:
        return None
    try:
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
        payload = {
            "name": name,
            "status": status,
            "metadata": metadata or {},
            "endpoints": endpoints or {},
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
        r = requests.post(
            f"{base}/api/registry/heartbeat", json={"name": name}, timeout=2.0
        )
        return r.status_code == 200 and bool((r.json() or {}).get("ok"))
    except Exception:
        return False
