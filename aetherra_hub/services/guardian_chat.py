from __future__ import annotations

# Standard library imports
import hashlib
import os
from typing import Any


def _hash_value(value: Any) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "hub:chat" and capability in {"chat:process", "ai:message"}:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def evaluate_chat_ingress(
    *,
    message: str,
    route: str,
    principal: str | None = None,
    trace_id: str | None = None,
    priority: str = "normal",
    context: dict[str, Any] | None = None,
    streaming: bool = False,
    allow_edits: bool = False,
):
    """Evaluate a Guardian intent before chat ingress reaches an AI engine."""

    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = (principal or os.getenv("AETHERRA_PRINCIPAL", "")).strip() or "hub:chat"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    context = context or {}
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="chat",
            action="chat.ingress",
            target=f"chat_route:{route}",
            purpose="Process a chat prompt through the Hub chat ingress pipeline",
            capabilities=("chat:process", "ai:message"),
            evidence=(f"chat_ingress:{route}",),
            reversible=True,
            rollback_plan="do not process prompt; remove queued stream/request state if present",
            metadata={
                "route": route,
                "message_hash": _hash_value(message),
                "message_length": len(str(message or "")),
                "trace_id_hash": _hash_value(trace_id),
                "priority": priority,
                "context_keys": sorted(str(key) for key in context),
                "streaming": streaming,
                "allow_edits": allow_edits,
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )
