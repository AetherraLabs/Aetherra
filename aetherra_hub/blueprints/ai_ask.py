from __future__ import annotations

# Standard library imports
import logging
import os
import time

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services.ai_stream import _get_engine  # reuse engine fetch
from ..services.control_auth import authorize_token_request
from ..services.guardian_chat import evaluate_chat_ingress
from ..services.idempotency import manager as idempotency_manager
from ..services.metrics_accum import inc_chat_rate_limited
from ..services.security import safety_precheck

bp = Blueprint("ai_ask", __name__)
logger = logging.getLogger(__name__)


@bp.post("/api/ai/ask")
def ai_ask_post():
    # Gate flags similar to legacy: API must be enabled
    if os.environ.get("AETHERRA_AI_API_ENABLED", "0") != "1":
        return jsonify({"error": "disabled"}), 501
    require_token = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
    if require_token:
        expected = os.environ.get("AETHERRA_AI_API_TOKEN") or os.environ.get(
            "AETHERRA_HUB_CONTROL_TOKEN", ""
        )
        decision = authorize_token_request(
            request.headers,
            expected,
            missing_configuration_error="ai_token_not_configured",
            unauthorized_status=403,
        )
        if not decision.allowed:
            try:
                from ..services import metrics_accum

                if decision.status_code == 503:
                    metrics_accum.inc_auth_missing_token()
                else:
                    metrics_accum.inc_auth_invalid_token()
            except Exception as exc:
                logger.debug(
                    "Failed to record AI API authorization metric: %s",
                    exc,
                    exc_info=True,
                )
            return jsonify({"error": decision.error}), decision.status_code
    body = request.get_json(silent=True) or {}
    message = str(body.get("message") or body.get("text") or "").strip()
    if not message:
        return jsonify({"error": "empty"}), 400
    trace_id = str(body.get("trace_id") or request.headers.get("X-Aetherra-Trace") or "")
    sc = safety_precheck(message, trace_id, "/api/ai/ask")
    if not sc.get("allow", True):
        return (
            jsonify(
                {
                    "error": {
                        "code": "policy_violation",
                        "message": "Request rejected by the safety policy",
                        "details": {
                            "reasons": sc.get("reasons", []),
                            "trace_id": trace_id,
                        },
                    }
                }
            ),
            403,
        )
    message = str(sc.get("message") or message)
    context = body.get("context") if isinstance(body.get("context"), dict) else {}
    principal = (
        request.headers.get("X-Aetherra-Principal")
        or request.headers.get("X-Principal")
        or body.get("principal")
        or context.get("principal")
        or "hub:chat"
    )
    client_message_id = str(body.get("client_message_id") or "").strip()
    if client_message_id and idempotency_manager.check_and_mark(
        str(principal),
        client_message_id,
    ):
        return (
            jsonify(
                {
                    "ok": False,
                    "client_message_id": client_message_id,
                    "error": {
                        "code": "duplicate",
                        "message": "Duplicate client_message_id",
                    },
                }
            ),
            409,
        )
    guardian_decision = evaluate_chat_ingress(
        message=message,
        route="/api/ai/ask",
        principal=principal,
        trace_id=trace_id,
        priority=str(body.get("priority") or "normal"),
        context={"priority": body.get("priority")},
        streaming=False,
    )
    if not guardian_decision.allowed:
        return (
            jsonify(
                {
                    "error": {
                        "code": "guardian_denied",
                        "message": "Request rejected by Guardian",
                        "details": {
                            "reason": guardian_decision.reason,
                            "trace_id": trace_id,
                        },
                    }
                }
            ),
            403,
        )
    # Try to obtain engine with a brief local retry (helps test race on registry)
    engine = None
    for _ in range(5):
        engine = _get_engine()
        if engine and hasattr(engine, "process_message"):
            break
        time.sleep(0.02)
    if not engine or not hasattr(engine, "process_message"):
        return jsonify(
            {"ok": True, "result": {"text": "offline", "response": "offline"}}
        )
    try:
        # Standard library imports
        import asyncio

        async def _run():
            return await engine.process_message(
                message, {"priority": body.get("priority")}
            )

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_run())
        finally:
            loop.close()
        return jsonify({"ok": True, "result": result})
    except Exception as e:  # pragma: no cover
        msg = str(e)
        if "rate limit" in msg.lower():
            inc_chat_rate_limited()
            ra = os.environ.get("AETHERRA_RETRY_AFTER_SEC", "5")
            try:
                ra_int = int(float(ra))
            except (TypeError, ValueError):
                ra_int = 5
            resp = jsonify(
                {
                    "error": {
                        "code": "rate_limited",
                        "message": "AI service rate limit exceeded",
                        "details": {"retry_after_sec": ra_int},
                    }
                }
            )
            resp.status_code = 429
            resp.headers["Retry-After"] = str(ra_int)
            return resp
        return jsonify({"ok": False, "error": msg}), 500
