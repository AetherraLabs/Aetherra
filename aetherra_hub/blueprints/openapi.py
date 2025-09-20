"""OpenAPI blueprint extracted from monolithic hub server."""

from __future__ import annotations

# Third party imports
from flask import Blueprint, jsonify

# Local imports
from ..config import settings

bp = Blueprint("openapi", __name__, url_prefix="/api")


@bp.get("/openapi.json")
def openapi_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {"title": "Aetherra Chat API", "version": "2"},
        "paths": {
            "/api/ai/ask": {
                "post": {
                    "summary": "Synchronous ask",
                    "parameters": [
                        {
                            "name": "X-Aetherra-Chat-Version",
                            "in": "header",
                            "required": False,
                            "schema": {"type": "string", "enum": ["2"]},
                        }
                    ],
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/api/ai/stream": {
                "post": {"summary": "SSE stream (POST)"},
                "get": {"summary": "SSE stream (GET alias)"},
            },
            "/api/ai/stream_ws": {
                "get": {"summary": "Advertise WebSocket availability"}
            },
        },
        "components": {
            "schemas": {
                "SSEEnvelopeV2": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "trace_id": {"type": "string"},
                        "ts": {"type": "string"},
                        "type": {"type": "string"},
                        "data": {"type": "object"},
                        "client_message_id": {"type": "string"},
                    },
                }
            }
        },
        "x-aetherra": {
            "ai_enabled": settings.ai_api_enabled,
            "stream_enabled": settings.ai_api_stream,
            "require_token": settings.ai_api_require_token,
            "ws_enabled": settings.ws_enabled,
            "version_required": settings.chat_version_required,
            "idempotency_ttl_sec": settings.idem_ttl_sec,
            "ws": {"route": "/ws/ai/stream", "frame_schema": "SSEEnvelopeV2"},
        },
    }
    # Fallback minimal on error
    return jsonify(spec)
