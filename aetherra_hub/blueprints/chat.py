from __future__ import annotations

# Standard library imports
import contextlib

# Third party imports
from flask import Blueprint, current_app, jsonify, request

# Local imports
from ..config import settings as default_settings
from ..services.chat_bridge import get_lyrixa_status, handle_chat
from ..services.chat_contract import add_response_headers, request_trace_id
from ..services.chat_status import build_chat_status_payload
from ..services.state import hub_state

bp = Blueprint("chat", __name__)
bp.after_request(add_response_headers)


def _json_no_store(payload):
    response = jsonify(payload)
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/api/lyrixa/status")
def lyrixa_status():
    hub_state.incr_requests()
    return _json_no_store(get_lyrixa_status())


@bp.get("/api/chat/status")
def chat_status():
    hub_state.incr_requests()
    settings = getattr(current_app, "settings", default_settings)
    return _json_no_store(build_chat_status_payload(settings))


@bp.post("/api/lyrixa/chat")
def lyrixa_chat():
    hub_state.incr_requests()
    try:
        payload = request.get_json(silent=True) or {}
    except Exception:
        return jsonify({"error": "invalid_json"}), 400
    payload["trace_id"] = request_trace_id()
    body, code, headers = handle_chat(payload)
    resp = jsonify(body)
    with contextlib.suppress(Exception):
        for k, v in headers.items():
            resp.headers[k] = v
    return resp, code
