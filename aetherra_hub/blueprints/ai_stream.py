from __future__ import annotations

# Third party imports
import contextlib

# Standard library imports
import ipaddress
import os

from flask import Blueprint, Response, jsonify, request

# Local imports
from ..services import metrics_accum
from ..services.ai_stream import stream_sse
from ..services.control_auth import authorize_token_request
from ..services.idempotency import manager as idempotency_manager
from ..services.security import policy_snapshot

bp = Blueprint("ai_stream", __name__)

_DEFAULT_PROD_NETWORK_ALLOWLIST = ("localhost", "127.0.0.1", "::1")


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


def _request_source() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return str(request.remote_addr or "").strip()


def _source_allowed(source: str) -> bool:
    profile = (os.environ.get("AETHERRA_PROFILE", "") or "").lower()
    strict_network = os.environ.get("AETHERRA_NET_STRICT", "0") == "1"
    if profile not in ("prod", "production") and not strict_network:
        return True

    configured_allowlist = os.environ.get("AETHERRA_NETWORK_ALLOWLIST", "").strip()
    if configured_allowlist:
        allowlist = tuple(
            entry.strip().lower()
            for entry in configured_allowlist.split(",")
            if entry.strip()
        )
    else:
        allowlist = _DEFAULT_PROD_NETWORK_ALLOWLIST

    source_normalized = source.lower()
    if source_normalized in allowlist:
        return True

    with contextlib.suppress(ValueError):
        ip = ipaddress.ip_address(source_normalized)
        if ip.is_loopback and any(
            entry in allowlist for entry in _DEFAULT_PROD_NETWORK_ALLOWLIST
        ):
            return True

    return False


def _flask_sock_available() -> bool:
    try:
        # Third party imports
        import flask_sock  # noqa: F401
    except Exception:
        return False
    return True


def _principal_from_payload(body: dict, headers) -> str:
    context = body.get("context") if isinstance(body.get("context"), dict) else {}
    return str(
        headers.get("X-Aetherra-Principal")
        or headers.get("X-Principal")
        or body.get("principal")
        or context.get("principal")
        or "anonymous"
    )


def _duplicate_response(body: dict, headers):
    client_message_id = str(body.get("client_message_id") or "").strip()
    if not client_message_id:
        return None
    principal = _principal_from_payload(body, headers)
    if not idempotency_manager.check_and_mark(principal, client_message_id):
        return None
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


@bp.get("/api/ai/stream_ws")
def ai_stream_ws_advertise():
    source = _request_source()
    if not _source_allowed(source):
        return jsonify({"error": "forbidden"}), 403

    ws_enabled = os.environ.get("AETHERRA_AI_API_WS", "0") == "1"
    if not ws_enabled or not _flask_sock_available():
        return jsonify({"error": "ws_disabled"}), 501

    return jsonify(
        {
            "ok": True,
            "ws": {
                "route": "/ws/ai/stream",
                "frame_schema": "SSEEnvelopeV2",
            },
        }
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
    auth_error = _authorize_ai_request()
    if auth_error is not None:
        return auth_error
    duplicate_error = _duplicate_response(body, request.headers)
    if duplicate_error is not None:
        return duplicate_error

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
    duplicate_error = _duplicate_response(args, request.headers)
    if duplicate_error is not None:
        return duplicate_error

    def generate():
        yield from stream_sse(args, hdrs, last_event_id=last_event_id, method="GET")

    return _build_response(generate)
