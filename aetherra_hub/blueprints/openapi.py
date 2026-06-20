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
            "/api/lyrixa/status": {
                "get": {
                    "summary": "Lyrixa service status",
                    "description": "Read-only Lyrixa readiness and capability status. Reports live registered service status when available and a bounded offline fallback when Lyrixa is not registered.",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live Lyrixa status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LyrixaStatusResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/maintenance/status": {
                "get": {
                    "summary": "Unified maintenance status",
                    "description": "Aggregated, best-effort status across Homeostasis, Self-Improvement, and Self-Incorporation. Always returns 200 with availability flags; missing subsystems are reported as available: false.",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/MaintenanceStatus"
                                    },
                                    "example": {
                                        "ok": True,
                                        "ts": "2025-10-23T12:34:56.789123",
                                        "overall": {
                                            "runlevel": "ONLINE",
                                            "health_percent": 92.5,
                                            "critical_health_percent": 98.0,
                                            "overall_running": True,
                                        },
                                        "kpis": {
                                            "system_health_score": 0.925,
                                            "actions_executed": 245,
                                            "proposals_generated": 12,
                                            "proposals_executed": 10,
                                            "proposals_accepted": 7,
                                            "files_integrated": 80,
                                            "files_quarantined": 5,
                                            "last_rollback_token": None,
                                        },
                                        "homeostasis": {
                                            "available": True,
                                            "running": True,
                                            "orchestrator": {
                                                "running": True,
                                                "initialized": True,
                                            },
                                            "health": {
                                                "supervisor": {"runlevel": "ONLINE"}
                                            },
                                            "si_health_contribution": {"score": 0.12},
                                        },
                                        "self_improvement": {
                                            "available": True,
                                            "status": {
                                                "improvement_active": True,
                                                "total_proposals": 0,
                                            },
                                        },
                                        "self_incorporation": {
                                            "available": True,
                                            "status": {"status": "ok", "running": True},
                                        },
                                    },
                                }
                            },
                        }
                    },
                }
            },
            "/api/hub/readiness": {
                "get": {
                    "summary": "Hub readiness contract",
                    "description": "Read-only readiness assessment for Hub route registration, production security posture, service registry visibility, and Kernel dependency visibility.",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live Hub readiness state.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HubReadinessResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/runtime-ui/manifest": {
                "get": {
                    "summary": "Runtime UI contract and safety manifest",
                    "description": "Read-only discovery document for Cognitive Observatory clients, including supported endpoints, modes, subsystems, authority ownership, and safety posture.",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime capability state.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiManifestResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/runtime-ui/status": {
                "get": {
                    "summary": "Runtime UI foundation status",
                    "description": "Compact health/readiness summary for the Runtime UI API foundation, including contract validation status and safety posture.",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiStatusResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/runtime-ui/bootstrap": {
                "get": {
                    "summary": "Runtime UI first-load bootstrap payload",
                    "description": "Read-only first-load payload for Cognitive Observatory clients. Includes manifest, Observatory state, scene metadata, and bounded activity events.",
                    "parameters": [
                        {
                            "name": "mode",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": [
                                    "first_launch",
                                    "overview",
                                    "architect",
                                    "subsystem",
                                ],
                            },
                        },
                        {
                            "name": "user",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "maxLength": 64},
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 25,
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiBootstrapResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid mode or limit"},
                    },
                }
            },
            "/api/runtime-ui/contract/validate": {
                "get": {
                    "summary": "Validate Runtime UI contract coherence",
                    "description": "Builds the current read-only bootstrap payload and validates cross-object consistency between manifest, Observatory state, scene metadata, and activity events.",
                    "parameters": [
                        {
                            "name": "mode",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": [
                                    "first_launch",
                                    "overview",
                                    "architect",
                                    "subsystem",
                                ],
                            },
                        },
                        {
                            "name": "user",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "maxLength": 64},
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 25,
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiContractValidationResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid mode or limit"},
                    },
                }
            },
            "/api/runtime-ui/observatory": {
                "get": {
                    "summary": "Runtime UI Cognitive Observatory snapshot",
                    "description": "Read-only state contract for the future Cognitive Observatory renderer. This endpoint does not execute actions, mutate memory/code, or approve privileged operations.",
                    "parameters": [
                        {
                            "name": "mode",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": [
                                    "first_launch",
                                    "overview",
                                    "architect",
                                    "subsystem",
                                ],
                            },
                        },
                        {
                            "name": "user",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "maxLength": 64},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiObservatoryResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid mode"},
                    },
                }
            },
            "/api/runtime-ui/activity": {
                "get": {
                    "summary": "Runtime UI Cognitive Observatory activity stream",
                    "description": "Bounded read-only Observatory activity events with normalized visual channels. This endpoint does not expose raw audit logs.",
                    "parameters": [
                        {
                            "name": "channel",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "maxLength": 64},
                        },
                        {
                            "name": "source",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "maxLength": 64},
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 25,
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiActivityResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid limit"},
                    },
                }
            },
            "/api/runtime-ui/scene": {
                "get": {
                    "summary": "Runtime UI Cognitive Observatory scene",
                    "description": "Read-only Observatory state plus renderer-agnostic normalized 3D scene metadata for future Cognitive Observatory clients.",
                    "parameters": [
                        {
                            "name": "mode",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": [
                                    "first_launch",
                                    "overview",
                                    "architect",
                                    "subsystem",
                                ],
                            },
                        },
                        {
                            "name": "user",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "maxLength": 64},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiSceneResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Invalid mode"},
                    },
                }
            },
            "/api/runtime-ui/subsystems/{subsystem_name}": {
                "get": {
                    "summary": "Runtime UI focused subsystem snapshot",
                    "description": "Read-only subsystem profile, status, related Observatory connections, and Lyrixa guidance for a focused Observatory view.",
                    "parameters": [
                        {
                            "name": "subsystem_name",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "user",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "maxLength": 64},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime status.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/RuntimeUiSubsystemResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Unknown subsystem"},
                    },
                }
            },
            "/api/kernel/readiness": {
                "get": {
                    "summary": "Kernel readiness contract",
                    "description": "Read-only readiness assessment for Kernel scheduling, lifecycle, queue pressure, and safety guard state.",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "headers": {
                                "Cache-Control": {
                                    "schema": {"type": "string"},
                                    "description": "Always no-store for live runtime state.",
                                }
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/KernelReadinessResponse"
                                    }
                                }
                            },
                        }
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
                "HubReadinessResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "settings": {"type": "object"},
                        "readiness": {
                            "type": "object",
                            "properties": {
                                "ok": {"type": "boolean"},
                                "system": {"type": "string"},
                                "contract_version": {"type": "string"},
                                "readiness": {
                                    "type": "string",
                                    "enum": ["ready", "degraded", "blocked"],
                                },
                                "safe_for_clients": {"type": "boolean"},
                                "reasons": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "checks": {"type": "object"},
                                "authority": {"type": "object"},
                            },
                            "required": [
                                "ok",
                                "system",
                                "contract_version",
                                "readiness",
                                "safe_for_clients",
                                "reasons",
                                "checks",
                                "authority",
                            ],
                        },
                    },
                    "required": ["ok", "settings", "readiness"],
                },
                "LyrixaStatusResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "system": {"type": "string"},
                        "service": {"type": "string"},
                        "readiness": {
                            "type": "string",
                            "enum": ["ready", "degraded", "offline"],
                        },
                        "safe_for_interaction": {"type": "boolean"},
                        "initialized": {"type": "boolean"},
                        "forced_offline": {"type": "boolean"},
                        "degraded_components": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "capabilities": {"type": "object"},
                        "authority": {"type": "object"},
                    },
                    "required": [
                        "ok",
                        "system",
                        "service",
                        "readiness",
                        "safe_for_interaction",
                    ],
                },
                "KernelReadinessResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "kernel": {"type": "object"},
                        "readiness": {
                            "type": "object",
                            "properties": {
                                "ok": {"type": "boolean"},
                                "system": {"type": "string"},
                                "contract_version": {"type": "string"},
                                "readiness": {
                                    "type": "string",
                                    "enum": [
                                        "ready",
                                        "degraded",
                                        "blocked",
                                        "offline",
                                    ],
                                },
                                "safe_to_schedule": {"type": "boolean"},
                                "reasons": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "checks": {"type": "object"},
                                "authority": {"type": "object"},
                                "source": {"type": "string"},
                            },
                            "required": [
                                "ok",
                                "system",
                                "contract_version",
                                "readiness",
                                "safe_to_schedule",
                                "reasons",
                                "checks",
                                "authority",
                                "source",
                            ],
                        },
                    },
                    "required": ["ok", "kernel", "readiness"],
                },
                "MaintenanceStatus": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "ts": {"type": "string", "format": "date-time"},
                        "overall": {
                            "type": "object",
                            "properties": {
                                "runlevel": {"type": "string"},
                                "health_percent": {"type": ["number", "null"]},
                                "critical_health_percent": {"type": ["number", "null"]},
                                "overall_running": {"type": "boolean"},
                            },
                            "required": ["runlevel", "overall_running"],
                        },
                        "kpis": {
                            "type": "object",
                            "properties": {
                                "system_health_score": {"type": ["number", "null"]},
                                "actions_executed": {"type": ["integer", "null"]},
                                "proposals_generated": {"type": ["integer", "null"]},
                                "proposals_executed": {"type": ["integer", "null"]},
                                "proposals_accepted": {"type": ["integer", "null"]},
                                "files_integrated": {"type": ["integer", "null"]},
                                "files_quarantined": {"type": ["integer", "null"]},
                                "last_rollback_token": {"type": ["string", "null"]},
                            },
                        },
                        "homeostasis": {
                            "type": "object",
                            "properties": {
                                "available": {"type": "boolean"},
                                "running": {"type": ["boolean", "null"]},
                                "orchestrator": {"type": "object"},
                                "health": {"type": "object"},
                                "si_health_contribution": {"type": ["object", "null"]},
                            },
                            "required": ["available"],
                        },
                        "self_improvement": {
                            "type": "object",
                            "properties": {
                                "available": {"type": "boolean"},
                                "status": {"type": "object"},
                            },
                            "required": ["available"],
                        },
                        "self_incorporation": {
                            "type": "object",
                            "properties": {
                                "available": {"type": "boolean"},
                                "status": {"type": "object"},
                            },
                            "required": ["available"],
                        },
                    },
                    "required": [
                        "ok",
                        "ts",
                        "overall",
                        "kpis",
                        "homeostasis",
                        "self_improvement",
                        "self_incorporation",
                    ],
                },
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
                "RuntimeUiObservatoryResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "observatory": {"$ref": "#/components/schemas/RuntimeUiObservatory"},
                    },
                    "required": ["ok", "observatory"],
                },
                "RuntimeUiManifestResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "manifest": {"$ref": "#/components/schemas/RuntimeUiManifest"},
                    },
                    "required": ["ok", "manifest"],
                },
                "RuntimeUiStatusResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "status": {"type": "string"},
                        "read_only": {"type": "boolean"},
                        "contract_version": {"type": "string"},
                        "controls_enabled": {"type": "boolean"},
                        "legacy_ui_enabled": {"type": "boolean"},
                        "validation": {"$ref": "#/components/schemas/RuntimeUiContractValidation"},
                        "endpoints": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                    },
                    "required": [
                        "ok",
                        "status",
                        "read_only",
                        "contract_version",
                        "controls_enabled",
                        "legacy_ui_enabled",
                        "validation",
                        "endpoints",
                    ],
                },
                "RuntimeUiBootstrapResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "read_only": {"type": "boolean"},
                        "manifest": {"$ref": "#/components/schemas/RuntimeUiManifest"},
                        "observatory": {"$ref": "#/components/schemas/RuntimeUiObservatory"},
                        "scene": {"$ref": "#/components/schemas/RuntimeUiScene"},
                        "activity": {
                            "type": "object",
                            "properties": {
                                "events": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/RuntimeUiEvent"},
                                },
                                "total": {"type": "integer"},
                                "limit": {"type": "integer"},
                            },
                            "required": ["events", "total", "limit"],
                        },
                    },
                    "required": [
                        "ok",
                        "read_only",
                        "manifest",
                        "observatory",
                        "scene",
                        "activity",
                    ],
                },
                "RuntimeUiContractValidationResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "read_only": {"type": "boolean"},
                        "validation": {"$ref": "#/components/schemas/RuntimeUiContractValidation"},
                    },
                    "required": ["ok", "read_only", "validation"],
                },
                "RuntimeUiContractValidation": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "errors": {"type": "array", "items": {"type": "string"}},
                        "warnings": {"type": "array", "items": {"type": "string"}},
                        "checked": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["ok", "errors", "warnings", "checked"],
                },
                "RuntimeUiSubsystemResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "read_only": {"type": "boolean"},
                        "subsystem": {"$ref": "#/components/schemas/RuntimeUiSubsystem"},
                        "profile": {"$ref": "#/components/schemas/RuntimeUiSubsystemProfile"},
                        "connections": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiConnection"},
                        },
                        "events": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiEvent"},
                        },
                        "lyrixa_guidance": {"type": ["string", "null"]},
                    },
                    "required": [
                        "ok",
                        "read_only",
                        "subsystem",
                        "profile",
                        "connections",
                        "events",
                    ],
                },
                "RuntimeUiSceneResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "observatory": {"$ref": "#/components/schemas/RuntimeUiObservatory"},
                        "scene": {"$ref": "#/components/schemas/RuntimeUiScene"},
                    },
                    "required": ["ok", "observatory", "scene"],
                },
                "RuntimeUiActivityResponse": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "read_only": {"type": "boolean"},
                        "events": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiEvent"},
                        },
                        "total": {"type": "integer"},
                        "filters": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": ["string", "null"]},
                                "source": {"type": ["string", "null"]},
                                "limit": {"type": "integer"},
                            },
                        },
                    },
                    "required": ["ok", "read_only", "events", "total", "filters"],
                },
                "RuntimeUiManifest": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "contract_version": {"type": "string"},
                        "status": {"type": "string"},
                        "read_only": {"type": "boolean"},
                        "controls_enabled": {"type": "boolean"},
                        "legacy_ui_enabled": {"type": "boolean"},
                        "supported_modes": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "supported_subsystems": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "supported_activity_channels": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "endpoints": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                        "authority": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                        "safety_rules": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "name",
                        "contract_version",
                        "status",
                        "read_only",
                        "controls_enabled",
                        "legacy_ui_enabled",
                        "supported_modes",
                        "supported_subsystems",
                        "supported_activity_channels",
                        "endpoints",
                        "authority",
                        "safety_rules",
                    ],
                },
                "RuntimeUiObservatory": {
                    "type": "object",
                    "properties": {
                        "mode": {"type": "string"},
                        "core_label": {"type": "string"},
                        "greeting": {"type": "string"},
                        "generated_at": {"type": "string", "format": "date-time"},
                        "read_only": {"type": "boolean"},
                        "subsystems": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiSubsystem"},
                        },
                        "connections": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiConnection"},
                        },
                        "events": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiEvent"},
                        },
                        "lyrixa_guidance": {"type": ["string", "null"]},
                    },
                    "required": [
                        "mode",
                        "core_label",
                        "greeting",
                        "generated_at",
                        "read_only",
                        "subsystems",
                        "connections",
                        "events",
                    ],
                },
                "RuntimeUiSubsystem": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "label": {"type": "string"},
                        "status": {"type": "string"},
                        "health": {"type": ["number", "null"]},
                        "activity": {"type": "number"},
                        "summary": {"type": "string"},
                        "metrics": {"type": "object"},
                    },
                    "required": ["name", "label", "status", "activity", "summary", "metrics"],
                },
                "RuntimeUiConnection": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "label": {"type": "string"},
                        "activity": {"type": "number"},
                        "status": {"type": "string"},
                    },
                    "required": ["source", "target", "label", "activity", "status"],
                },
                "RuntimeUiEvent": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "event_type": {"type": "string"},
                        "summary": {"type": "string"},
                        "severity": {"type": "string"},
                        "visual_channel": {"type": "string"},
                        "action_required": {"type": "boolean"},
                        "occurred_at": {"type": "string", "format": "date-time"},
                        "details": {"type": "object"},
                    },
                    "required": [
                        "source",
                        "event_type",
                        "summary",
                        "severity",
                        "visual_channel",
                        "action_required",
                        "occurred_at",
                        "details",
                    ],
                },
                "RuntimeUiScene": {
                    "type": "object",
                    "properties": {
                        "core_label": {"type": "string"},
                        "read_only": {"type": "boolean"},
                        "coordinate_space": {"type": "string"},
                        "nodes": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiSceneNode"},
                        },
                        "connections": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/RuntimeUiSceneConnection"},
                        },
                    },
                    "required": [
                        "core_label",
                        "read_only",
                        "coordinate_space",
                        "nodes",
                        "connections",
                    ],
                },
                "RuntimeUiSceneNode": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "label": {"type": "string"},
                        "group": {"type": "string"},
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "z": {"type": "number"},
                        "radius": {"type": "number"},
                        "emphasis": {"type": "number"},
                        "status": {"type": "string"},
                        "accessibility_label": {"type": "string"},
                    },
                    "required": [
                        "name",
                        "label",
                        "group",
                        "x",
                        "y",
                        "z",
                        "radius",
                        "emphasis",
                        "status",
                        "accessibility_label",
                    ],
                },
                "RuntimeUiSceneConnection": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "label": {"type": "string"},
                        "status": {"type": "string"},
                        "pulse": {"type": "number"},
                        "thickness": {"type": "number"},
                    },
                    "required": ["source", "target", "label", "status", "pulse", "thickness"],
                },
                "RuntimeUiSubsystemProfile": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "purpose": {"type": "string"},
                        "authority_owner": {"type": "string"},
                        "primary_view": {"type": "string"},
                        "panels": {"type": "array", "items": {"type": "string"}},
                        "related_endpoints": {"type": "array", "items": {"type": "string"}},
                        "safety_rules": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "title",
                        "purpose",
                        "authority_owner",
                        "primary_view",
                        "panels",
                        "related_endpoints",
                        "safety_rules",
                    ],
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
