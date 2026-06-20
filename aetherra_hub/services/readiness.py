"""Read-only readiness assessment for the Aetherra Hub."""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import asdict
from typing import Any

from flask import Flask

from ..config import Settings

HUB_READINESS_CONTRACT_VERSION = "1.0"

REQUIRED_ROUTES = frozenset(
    {
        "/api/ping",
        "/health",
        "/status",
        "/api/openapi.json",
        "/metrics",
        "/api/kernel/status",
        "/api/kernel/readiness",
        "/api/runtime-ui/status",
        "/api/maintenance/status",
    }
)


def _route_paths(app: Flask) -> set[str]:
    return {
        str(rule.rule)
        for rule in app.url_map.iter_rules()
        if "GET" in getattr(rule, "methods", set())
        or "POST" in getattr(rule, "methods", set())
    }


def _prod_security_reasons(settings: Settings) -> list[str]:
    if not settings.prod_profile:
        return []

    reasons: list[str] = []
    if settings.ai_api_enabled:
        if not settings.ai_api_require_token:
            reasons.append("prod_ai_api_token_not_required")
        if not settings.ai_api_token:
            reasons.append("prod_ai_api_token_missing")

    if not os.environ.get("AETHERRA_HUB_CONTROL_TOKEN"):
        reasons.append("prod_hub_control_token_missing")
    if os.environ.get("AETHERRA_REQUIRE_CAPABILITIES", "0") != "1":
        reasons.append("prod_capabilities_not_required")
    if os.environ.get("AETHERRA_SCRIPT_VERIFY_STRICT", "0") != "1":
        reasons.append("prod_script_strict_verify_disabled")
    if os.environ.get("AETHERRA_SIGNING_STRICT", "0") != "1":
        reasons.append("prod_plugin_signing_strict_disabled")
    return reasons


def _dependency_reasons(
    *, kernel_status: dict[str, Any] | None, registry_status: dict[str, Any] | None
) -> list[str]:
    reasons: list[str] = []
    if not kernel_status:
        reasons.append("kernel_status_unavailable")
    elif not bool(kernel_status.get("running", False)):
        reasons.append("kernel_not_running")

    if not registry_status:
        reasons.append("service_registry_unavailable")
    return reasons


def assess_hub_readiness(
    *,
    app: Flask,
    settings: Settings,
    kernel_status: dict[str, Any] | None,
    registry_status: dict[str, Any] | None,
    required_routes: Iterable[str] = REQUIRED_ROUTES,
) -> dict[str, Any]:
    """Assess whether the Hub is safe enough for alpha clients.

    The assessment reads Flask route metadata, environment-derived settings, and
    dependency status snapshots. It does not start services, mutate registry
    state, or call privileged control endpoints.
    """

    routes = _route_paths(app)
    missing_routes = sorted(set(required_routes).difference(routes))
    reasons: list[str] = []
    if missing_routes:
        reasons.append("required_routes_missing")

    security_reasons = _prod_security_reasons(settings)
    dependency_reasons = _dependency_reasons(
        kernel_status=kernel_status,
        registry_status=registry_status,
    )
    reasons.extend(security_reasons)
    reasons.extend(dependency_reasons)

    blocking_prefixes = ("prod_",)
    if missing_routes or any(reason.startswith(blocking_prefixes) for reason in reasons):
        readiness = "blocked"
    elif dependency_reasons:
        readiness = "degraded"
    else:
        readiness = "ready"

    return {
        "ok": readiness in {"ready", "degraded"},
        "system": "hub",
        "contract_version": HUB_READINESS_CONTRACT_VERSION,
        "readiness": readiness,
        "safe_for_clients": readiness == "ready",
        "reasons": sorted(set(reasons)) or ["ready"],
        "checks": {
            "required_routes_present": not missing_routes,
            "missing_routes": missing_routes,
            "route_count": len(routes),
            "prod_profile": settings.prod_profile,
            "ai_api_enabled": settings.ai_api_enabled,
            "ai_api_token_required": settings.ai_api_require_token,
            "ai_api_token_configured": bool(settings.ai_api_token),
            "registry_visible": bool(registry_status),
            "kernel_visible": bool(kernel_status),
            "kernel_running": bool((kernel_status or {}).get("running", False)),
        },
        "authority": {
            "owns": [
                "HTTP API routing",
                "request authentication gates",
                "read-only status and metrics surfaces",
                "Hub service registration and heartbeat",
                "OpenAPI discovery contract",
            ],
            "does_not_own": [
                "Guardian policy decisions",
                "Security capability enforcement rules",
                "Kernel scheduling authority",
                "Memory persistence authority",
                "Self-Incorporation execution authority",
                "Runtime UI rendering",
            ],
        },
    }


def build_hub_readiness_payload(
    *,
    app: Flask,
    settings: Settings,
    kernel_status: dict[str, Any] | None,
    registry_status: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build the public Hub readiness payload."""

    return {
        "ok": True,
        "settings": {
            key: value
            for key, value in asdict(settings).items()
            if not key.endswith("_token")
        },
        "readiness": assess_hub_readiness(
            app=app,
            settings=settings,
            kernel_status=kernel_status,
            registry_status=registry_status,
        ),
    }
