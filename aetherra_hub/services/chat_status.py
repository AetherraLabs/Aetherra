"""Read-only readiness contract for the Aetherra Chat system."""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any

from ..config import Settings
from .security import policy_snapshot

CHAT_READINESS_CONTRACT_VERSION = "1.0"


def assess_chat_readiness(settings: Settings) -> dict[str, Any]:
    """Assess whether Chat transport is safe enough for clients."""

    reasons: list[str] = []
    ai_enabled = os.environ.get("AETHERRA_AI_API_ENABLED", "0") == "1"
    stream_enabled = os.environ.get("AETHERRA_AI_API_STREAM", "0") == "1"
    require_token = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
    token_configured = bool(
        os.environ.get("AETHERRA_AI_API_TOKEN")
        or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
    )
    safety_mode = os.environ.get("AETHERRA_CHAT_SAFETY_MODE", "standard").strip().lower()
    if safety_mode not in {"standard", "strict"}:
        reasons.append("invalid_safety_mode")

    if settings.prod_profile and ai_enabled:
        if not require_token:
            reasons.append("prod_ai_chat_token_not_required")
        if not token_configured:
            reasons.append("prod_ai_chat_token_missing")

    if not ai_enabled:
        reasons.append("ai_developer_api_disabled")
    if ai_enabled and not stream_enabled:
        reasons.append("streaming_disabled")

    if any(reason.startswith("prod_") for reason in reasons) or "invalid_safety_mode" in reasons:
        readiness = "blocked"
    elif "ai_developer_api_disabled" in reasons or "streaming_disabled" in reasons:
        readiness = "degraded"
    else:
        readiness = "ready"

    return {
        "ok": readiness in {"ready", "degraded"},
        "system": "chat",
        "contract_version": CHAT_READINESS_CONTRACT_VERSION,
        "readiness": readiness,
        "safe_for_clients": readiness == "ready",
        "reasons": sorted(set(reasons)) or ["ready"],
        "checks": {
            "ai_api_enabled": ai_enabled,
            "streaming_enabled": stream_enabled,
            "token_required": require_token,
            "token_configured": token_configured,
            "safety_mode": safety_mode or "standard",
            "prod_profile": settings.prod_profile,
            "lyrixa_bridge_available": True,
            "offline_fallback_available": True,
        },
        "authority": {
            "owns": [
                "chat HTTP transport",
                "SSE stream transport",
                "chat ingress safety preflight",
                "trace and policy response headers",
                "offline chat fallback routing",
            ],
            "does_not_own": [
                "AI engine reasoning authority",
                "Lyrixa identity authority",
                "Guardian approval decisions",
                "Security capability policy",
                "Kernel scheduling",
                "Memory persistence authority",
            ],
        },
    }


def build_chat_status_payload(settings: Settings) -> dict[str, Any]:
    """Build the public Chat readiness payload without executing chat."""

    return {
        "ok": True,
        "settings": {
            key: value
            for key, value in asdict(settings).items()
            if not key.endswith("_token")
        },
        "policy": policy_snapshot(),
        "readiness": assess_chat_readiness(settings),
    }
