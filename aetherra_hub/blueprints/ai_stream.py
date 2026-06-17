from __future__ import annotations

# Third party imports
import contextlib

# Standard library imports
import os

from flask import Blueprint, Response, jsonify, request

# Local imports
from ..services import metrics_accum
from ..services.ai_stream import stream_sse
from ..services.control_auth import authorize_token_request
from ..services.security import policy_snapshot

bp = Blueprint("ai_stream", __name__)


def _authorize_ai_request():
    if os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") != "1":
        return None
    expected = os.environ.get("AETHERRA_AI_API_TOKEN") or os.environ.get(
        "AETHERRA_HUB_CONTROL_TOKEN", ""
    )
    decision = authorize_token_request(
        request.headers,
        expected,
        missing_configuration_error="ai_token_not_configured",
        unauthorized_status=403,
    )
    if decision.allowed:
        return None
    with contextlib.suppress(Exception):
        if decision.status_code == 503:
            metrics_accum.inc_auth_missing_token()
        else:
            metrics_accum.inc_auth_invalid_token()
    return jsonify({"error": decision.error}), decision.status_code


def _build_response(gen_func):
    # Standard library imports
    import json

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        # Surface current policy in responses (gate8 expectation)
        "X-Aetherra-Policy": json.dumps(policy_snapshot()),
    }
    return Response(gen_func(), mimetype="text/event-stream", headers=headers)


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
    auth_error = _authorize_ai_request()
    if auth_error is not None:
        return auth_error

    def generate():
        yield from stream_sse(body, hdrs, last_event_id=last_event_id)

    return _build_response(generate)


@bp.get("/api/ai/stream")
def ai_stream_get():
    # Accept query params equivalent to body keys
    # Convert MultiDict to plain dict (first values only)
    args = dict(request.args.items())
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
    auth_error = _authorize_ai_request()
    if auth_error is not None:
        return auth_error

    def generate():
        yield from stream_sse(args, hdrs, last_event_id=last_event_id, method="GET")

    return _build_response(generate)
