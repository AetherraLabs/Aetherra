from __future__ import annotations

# Standard library imports
import os

# Third party imports
from flask import Blueprint, Response, jsonify, request

# Local imports
from ..services import metrics_accum
from ..services.ai_stream import stream_sse

bp = Blueprint("ai_stream", __name__)


def _build_response(gen_func):
    return Response(
        gen_func(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@bp.post("/api/ai/stream")
def ai_stream_post():
    body = request.get_json(silent=True) or {}
    last_event_id = request.headers.get("Last-Event-ID")
    # Pass trace id if client supplied for continuity
    hdrs = {
        "trace_id": request.headers.get("X-Aetherra-Trace-Id", ""),
        "X-Aetherra-Principal": request.headers.get("X-Aetherra-Principal", ""),
    }

    # Fast disable gate returning legacy 501 (tests expect this)
    if (
        os.environ.get("AETHERRA_AI_API_ENABLED", "0") != "1"
        or os.environ.get("AETHERRA_AI_API_STREAM", "0") != "1"
    ):
        # If API intended but missing required token config in prod profile, count it
        profile = (os.environ.get("AETHERRA_PROFILE", "") or "").lower()
        if (
            profile in ("prod", "production")
            and os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
            and not (
                os.environ.get("AETHERRA_AI_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
            )
        ):
            metrics_accum.inc_auth_missing_token()
        return jsonify({"error": "disabled"}), 501
    # Enforce token if required (invalid token increments metric)
    if os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1":
        expected = os.environ.get("AETHERRA_AI_API_TOKEN") or os.environ.get(
            "AETHERRA_HUB_CONTROL_TOKEN", ""
        )
        provided = request.headers.get("X-Aetherra-Token", "")
        if expected and provided and provided != expected:
            try:
                metrics_accum.inc_auth_invalid_token()
            except Exception:
                pass
            return jsonify({"error": "forbidden"}), 403

    def generate():
        for chunk in stream_sse(body, hdrs, last_event_id=last_event_id):
            yield chunk

    return _build_response(generate)


@bp.get("/api/ai/stream")
def ai_stream_get():
    # Accept query params equivalent to body keys
    # Convert MultiDict to plain dict (first values only)
    args = {k: v for k, v in request.args.items()}
    last_event_id = request.headers.get("Last-Event-ID")
    hdrs = {
        "trace_id": request.headers.get("X-Aetherra-Trace-Id", ""),
        "X-Aetherra-Principal": request.headers.get("X-Aetherra-Principal", ""),
    }

    if (
        os.environ.get("AETHERRA_AI_API_ENABLED", "0") != "1"
        or os.environ.get("AETHERRA_AI_API_STREAM", "0") != "1"
    ):
        profile = (os.environ.get("AETHERRA_PROFILE", "") or "").lower()
        if (
            profile in ("prod", "production")
            and os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
            and not (
                os.environ.get("AETHERRA_AI_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
            )
        ):
            metrics_accum.inc_auth_missing_token()
        return jsonify({"error": "disabled"}), 501
    if os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1":
        expected = os.environ.get("AETHERRA_AI_API_TOKEN") or os.environ.get(
            "AETHERRA_HUB_CONTROL_TOKEN", ""
        )
        provided = request.headers.get("X-Aetherra-Token", "")
        if expected and provided and provided != expected:
            try:
                metrics_accum.inc_auth_invalid_token()
            except Exception:
                pass
            return jsonify({"error": "forbidden"}), 403

    def generate():
        for chunk in stream_sse(args, hdrs, last_event_id=last_event_id, method="GET"):
            yield chunk

    return _build_response(generate)
