from __future__ import annotations

# Standard library imports
import os
import time

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services.ai_stream import _get_engine  # reuse engine fetch

bp = Blueprint("ai_ask", __name__)


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
        provided = request.headers.get("X-Aetherra-Token", "")
        if not expected or provided != expected:
            # Increment invalid token counter when a token is provided but incorrect
            try:
                if provided:
                    # Local imports
                    from ..services import metrics_accum

                    metrics_accum.inc_auth_invalid_token()
            except Exception:
                pass
            return jsonify({"error": "forbidden"}), 403
    body = request.get_json(silent=True) or {}
    message = str(body.get("message") or body.get("text") or "").strip()
    if not message:
        return jsonify({"error": "empty"}), 400
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
            ra = os.environ.get("AETHERRA_RETRY_AFTER_SEC", "5")
            try:
                ra_int = int(float(ra))
            except Exception:
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
