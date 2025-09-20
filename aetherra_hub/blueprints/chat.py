from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify, request

# Local imports
from ..services.chat_bridge import handle_chat

bp = Blueprint("chat", __name__)


@bp.post("/api/lyrixa/chat")
def lyrixa_chat():
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
