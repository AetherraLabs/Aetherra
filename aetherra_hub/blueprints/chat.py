from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services.chat_bridge import get_lyrixa_status, handle_chat
from ..services.state import hub_state

bp = Blueprint("chat", __name__)


def _json_no_store(payload):
    response = jsonify(payload)
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.get("/api/lyrixa/status")
def lyrixa_status():
    hub_state.incr_requests()
    return _json_no_store(get_lyrixa_status())


@bp.post("/api/lyrixa/chat")
def lyrixa_chat():
    hub_state.incr_requests()
    try:
        payload = request.get_json(silent=True) or {}
    except Exception:
        return jsonify({"error": "invalid_json"}), 400
    body, code, headers = handle_chat(payload)
    resp = jsonify(body)
    try:
        for k, v in headers.items():
            resp.headers[k] = v
    except Exception:
        pass
    return resp, code
