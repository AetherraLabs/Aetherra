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
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                        "priority": {
                                            "type": "string",
                                            "enum": ["low", "normal", "high"],
                                        },
                                    },
                                    "required": ["message"],
                                },
                                "example": {
                                    "message": "What is the status of the system?",
                                    "priority": "normal",
                                },
                            }
                        },
                    },
                    "parameters": [
                        {
                            "name": "X-Aetherra-Chat-Version",
                            "in": "header",
                            "required": False,
                            "schema": {"type": "string", "enum": ["2"]},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AskResponse"
                                    },
                                    "example": {
                                        "ok": True,
                                        "result": {
                                            "response": "Echo: What is the status of the system?",
                                            "context": {"priority": "normal"},
                                        },
                                    },
                                }
                            },
                        },
                        "400": {"description": "Bad Request (missing/empty message)"},
                        "403": {"description": "Forbidden (token required/mismatch)"},
                        "501": {"description": "API disabled"},
                    },
                }
            },
            "/api/qfac/admin/show": {
                "get": {
                    "summary": "QFAC admin: Show retrieval policy and parity counters",
                    "parameters": [
                        {
                            "name": "Authorization",
                            "in": "header",
                            "required": False,
                            "description": "Bearer <AETHERRA_HUB_CONTROL_TOKEN> (if configured)",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "X-Aetherra-Control-Token",
                            "in": "header",
                            "required": False,
                            "description": "Alternative header for control token",
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/QfacAdminShow"
                                    },
                                    "example": {
                                        "available": False,
                                        "retrieval_policy": {
                                            "threshold": 0.0,
                                            "parity_enabled": 0,
                                        },
                                        "parity_counters": {
                                            "total": 0,
                                            "top1_match": 0,
                                            "any_rank_mismatch": 0,
                                            "threshold_dropped": 0,
                                        },
                                    },
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/qfac/admin/reset": {
                "post": {
                    "summary": "QFAC admin: Reset retrieval parity counters",
                    "parameters": [
                        {
                            "name": "Authorization",
                            "in": "header",
                            "required": False,
                            "description": "Bearer <AETHERRA_HUB_CONTROL_TOKEN> (if configured)",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "X-Aetherra-Control-Token",
                            "in": "header",
                            "required": False,
                            "description": "Alternative header for control token",
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/QfacAdminReset"
                                    },
                                    "examples": {
                                        "ok": {
                                            "summary": "Success",
                                            "value": {"ok": True},
                                        },
                                        "unavailable": {
                                            "summary": "Unavailable",
                                            "value": {
                                                "ok": False,
                                                "reason": "qfac unavailable",
                                            },
                                        },
                                    },
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/ai/stream": {
                "post": {
                    "summary": "SSE stream (POST)",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"message": {"type": "string"}},
                                    "required": ["message"],
                                },
                                "example": {"message": "stream this response"},
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Event stream",
                            "content": {
                                "text/event-stream": {
                                    "schema": {"type": "string"},
                                    "example": 'id: 1\nevent: status\ndata: {"id":1,"trace_id":"t-123","ts":"2025-01-01T00:00:00Z","type":"status","data":{"message":"starting"}}\n\n',
                                }
                            },
                        }
                    },
                },
                "get": {
                    "summary": "SSE stream (GET alias)",
                    "parameters": [
                        {
                            "name": "message",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "example": "stream this response",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Event stream",
                            "content": {
                                "text/event-stream": {"schema": {"type": "string"}}
                            },
                        }
                    },
                },
            },
            "/api/ai/stream_ws": {
                "get": {
                    "summary": "Advertise WebSocket availability",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ws": {
                                                "type": "object",
                                                "properties": {
                                                    "route": {"type": "string"},
                                                    "frame_schema": {"type": "string"},
                                                },
                                            }
                                        },
                                    },
                                    "example": {
                                        "ws": {
                                            "route": "/ws/ai/stream",
                                            "frame_schema": "SSEEnvelopeV2",
                                        }
                                    },
                                }
                            },
                        }
                    },
                }
            },
            "/api/agents": {
                "get": {
                    "summary": "Agents orchestrator status",
                    "parameters": [
                        {
                            "name": "X-Aetherra-Token",
                            "in": "header",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Required when agents API is enabled with token enforcement",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ok": {"type": "boolean"},
                                            "orchestrator": {
                                                "type": "object",
                                                "properties": {
                                                    "total_agents": {"type": "integer"},
                                                    "pending_tasks": {
                                                        "type": "integer"
                                                    },
                                                },
                                            },
                                        },
                                        "required": ["ok"],
                                    },
                                    "example": {
                                        "ok": True,
                                        "orchestrator": {
                                            "total_agents": 0,
                                            "pending_tasks": 0,
                                        },
                                    },
                                }
                            },
                        },
                        "403": {"description": "Forbidden (token required/mismatch)"},
                        "501": {"description": "API disabled"},
                    },
                }
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
                    "example": {
                        "id": 1,
                        "trace_id": "trace-abc123",
                        "ts": "2025-01-01T00:00:00Z",
                        "type": "status",
                        "data": {"message": "stream started"},
                        "client_message_id": "cmsg-42",
                    },
                },
                "AskResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "result": {
                            "type": "object",
                            "properties": {
                                "response": {"type": "string"},
                                "context": {"type": "object"},
                            },
                        },
                    },
                    "required": ["ok"],
                    "example": {
                        "ok": True,
                        "result": {
                            "response": "Echo: hello world",
                            "context": {"priority": "normal"},
                        },
                    },
                },
                "QfacAdminShow": {
                    "type": "object",
                    "properties": {
                        "available": {"type": "boolean"},
                        "retrieval_policy": {
                            "type": "object",
                            "properties": {
                                "threshold": {"type": "number"},
                                "parity_enabled": {"type": "integer", "enum": [0, 1]},
                            },
                            "required": ["threshold", "parity_enabled"],
                        },
                        "parity_counters": {
                            "type": "object",
                            "properties": {
                                "total": {"type": "integer"},
                                "top1_match": {"type": "integer"},
                                "any_rank_mismatch": {"type": "integer"},
                                "threshold_dropped": {"type": "integer"},
                            },
                            "required": [
                                "total",
                                "top1_match",
                                "any_rank_mismatch",
                                "threshold_dropped",
                            ],
                        },
                        "parity_by_k": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                            "description": "Optional per-k parity counters (e.g., k=1,3,5,10)",
                            "example": {"1": 0, "3": 0, "5": 0, "10": 0},
                        },
                    },
                    "required": ["available", "retrieval_policy", "parity_counters"],
                },
                "QfacAdminReset": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "reason": {"type": "string"},
                        "error": {"type": "string"},
                    },
                    "required": ["ok"],
                },
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
