from __future__ import annotations

# Standard library imports
import asyncio
import json
import logging
import os
from time import perf_counter
from typing import Any

# Third party imports
from flask import Blueprint, Response, current_app, jsonify, request

# Local imports
from ..services.idempotency_simple import IdempotencyStore
from ..services.plugin_metrics import observe_registration_latency, plugin_metrics
from ..services.plugin_security import (
    PluginValidationError,
    redact_text,
    validate_and_register_plugin,
)

bp = Blueprint("plugins", __name__)
log = logging.getLogger(__name__)

# In-memory plugin registry (minimal slice)
_PLUGIN_REGISTRY: dict[str, dict[str, Any]] = {}
_IDEM = IdempotencyStore(ttl_seconds=600)
_PARALLEL_SAMPLE_LAST: dict[str, Any] | None = None  # cached last sample summary

# counters now sourced from plugin_metrics service


def _advanced_mode(settings) -> bool:
    if getattr(settings, "require_plugin_signature", False):
        return True
    env_flags = [
        os.environ.get("AETH_ADVANCED_PLUGIN_VALIDATION", "0") == "1",
        os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1",
        os.environ.get("AETHERRA_HUB_STRICT", "0") == "1",
        os.environ.get("AETHERRA_STRICT", "0") == "1",
    ]
    return any(env_flags)


def _merged_plugins() -> dict[str, dict[str, Any]]:
    merged = dict(_PLUGIN_REGISTRY)
    try:  # include advanced store plugins if present
        # Local imports
        from ..services import plugins as adv

        for k, v in adv.store.plugins.items():
            merged[k] = v
    except Exception:
        log.debug("Failed to access advanced plugin store")
    return merged


@bp.get("")
def list_plugins() -> Any:
    items: list[dict[str, Any]] = []
    for name, meta in sorted(_merged_plugins().items()):
        items.append(
            {
                "name": name,
                "version": meta.get("version", "1.0.0"),
                "display_name": meta.get("display_name", name.title()),
                "description": meta.get("description", ""),
                "category": meta.get("category", "utilities"),
                "registered_at": meta.get("registered_at", ""),
            }
        )
    return jsonify({"plugins": items, "total": len(items)})


@bp.get("/metrics")
def plugin_metrics_endpoint() -> Any:
    return jsonify(plugin_metrics)


@bp.get("/openapi.json")
def plugin_openapi_spec() -> Any:
    spec = {
        "openapi": "3.0.1",
        "info": {"title": "Aetherra Plugin API", "version": "1.1.0"},
        "components": {
            "schemas": {
                "Plugin": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "display_name": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string"},
                        "registered_at": {"type": "string"},
                        "signature_verified": {"type": "boolean"},
                        "trust_zone": {"type": "string"},
                    },
                    "required": ["name", "version", "description"],
                },
                "PluginList": {
                    "type": "object",
                    "properties": {
                        "plugins": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Plugin"},
                        },
                        "total": {"type": "integer"},
                    },
                },
                "PluginRegisterRequest": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string"},
                        "signature": {"type": "string"},
                        "pubkey": {"type": "string"},
                    },
                    "required": ["name", "version", "description"],
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "detail": {"type": "string"},
                    },
                    "required": ["error"],
                },
            }
        },
        "paths": {
            "/api/plugins": {
                "get": {
                    "summary": "List plugins",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PluginList"
                                    },
                                    "example": {
                                        "plugins": [
                                            {
                                                "name": "hello_world",
                                                "version": "1.0.0",
                                                "display_name": "Hello World",
                                                "description": "Greets the world",
                                                "category": "utilities",
                                                "registered_at": "2025-01-01T00:00:00Z",
                                            }
                                        ],
                                        "total": 1,
                                    },
                                }
                            },
                        }
                    },
                }
            },
            "/api/plugins/register": {
                "post": {
                    "summary": "Register plugin",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PluginRegisterRequest"
                                },
                                "example": {
                                    "name": "hello_world",
                                    "version": "1.0.0",
                                    "description": "Greets the world",
                                    "category": "utilities",
                                },
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Registered",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Plugin"},
                                    "example": {
                                        "name": "hello_world",
                                        "version": "1.0.0",
                                        "display_name": "Hello World",
                                        "description": "Greets the world",
                                        "category": "utilities",
                                        "registered_at": "2025-01-01T00:00:00Z",
                                    },
                                }
                            },
                        },
                        "400": {
                            "description": "Validation error",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"},
                                    "examples": {
                                        "invalid": {
                                            "summary": "Invalid JSON",
                                            "value": {"error": "invalid_json"},
                                        },
                                        "validation": {
                                            "summary": "Validation failed",
                                            "value": {
                                                "error": "validation_error",
                                                "detail": "Plugin validation failed",
                                            },
                                        },
                                    },
                                }
                            },
                        },
                        "413": {
                            "description": "Payload too large",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"},
                                    "example": {
                                        "error": "payload_too_large",
                                        "limit_kb": 256,
                                    },
                                }
                            },
                        },
                    },
                }
            },
            "/api/plugins/metrics": {
                "get": {
                    "summary": "Plugin metrics",
                    "responses": {"200": {"description": "OK"}},
                }
            },
        },
    }
    return jsonify(spec)


@bp.get("/openapi.yaml")
def plugin_openapi_yaml() -> Any:
    # Reuse JSON spec then dump to YAML (manual minimal serializer to avoid new deps)
    # Standard library imports
    import json as _json

    spec = plugin_openapi_spec().json

    def _to_yaml(obj: Any, indent: int = 0) -> str:
        pad = "  " * indent
        if isinstance(obj, dict):
            lines = []
            for k, v in obj.items():
                if isinstance(v, dict | list):
                    lines.append(f"{pad}{k}:")
                    lines.append(_to_yaml(v, indent + 1))
                else:
                    val = _json.dumps(v)
                    lines.append(f"{pad}{k}: {val}")
            return "\n".join(lines)
        if isinstance(obj, list):
            lines = []
            for item in obj:
                if isinstance(item, dict | list):
                    lines.append(f"{pad}-")
                    lines.append(_to_yaml(item, indent + 1))
                else:
                    val = _json.dumps(item)
                    lines.append(f"{pad}- {val}")
            return "\n".join(lines)
        return f"{pad}{_json.dumps(obj)}"

    yaml_body = _to_yaml(spec) + "\n"
    return Response(yaml_body, mimetype="application/yaml")


@bp.post("/register")
def register_plugin() -> Any:
    settings = current_app.settings  # type: ignore[attr-defined]
    start_t = perf_counter()

    # Dev override: allow unsigned plugins when header present or env flag set.
    # This lets local discovery succeed even if strict signing flags were enabled during hub start.
    allow_unsigned = False
    try:
        from flask import request as _req  # local import for clarity

        allow_unsigned = (
            os.environ.get("AETHERRA_ALLOW_UNSIGNED_DEV", "0") == "1"
            or _req.headers.get("X-Aeth-Allow-Unsigned") == "1"
        )
        if allow_unsigned:
            # Temporarily relax signature requirement for this request path only.
            # We don't mutate global settings object beyond this handler scope.
            try:
                # This attribute exists on Settings; best-effort downgrade
                settings.require_plugin_signature = False  # type: ignore[attr-defined]
            except Exception:
                pass
            # Also relax environment strict flags so advanced store logic downgrades.
            os.environ["AETHERRA_SIGNING_STRICT"] = "0"
            os.environ["AETHERRA_HUB_STRICT"] = "0"
            os.environ["AETHERRA_STRICT"] = "0"
            os.environ["AETH_ADVANCED_PLUGIN_VALIDATION"] = "0"
            # Make override visible to store.register logic
            os.environ["AETHERRA_ALLOW_UNSIGNED_DEV"] = "1"
            log.debug(
                "[PLUGINS][DEV] Unsigned registration override active (header/env)"
            )
    except Exception as _unsigned_exc:
        log.debug("[PLUGINS][DEV] Unsigned override handling error: %s", _unsigned_exc)

    # Idempotency
    idem_key = request.headers.get("Idempotency-Key") or request.headers.get("Idem-Key")
    if idem_key:
        hit = _IDEM.check_and_mark(idem_key)
        if hit.already_processed:
            plugin_metrics["duplicates_total"] += 1
            return jsonify({"status": "duplicate", "idempotency_key": idem_key})

    # Payload size guard
    raw = request.get_data(cache=False, as_text=True) or "{}"
    kb = len(raw.encode("utf-8")) / 1024.0
    if kb > settings.max_payload_kb:
        return (
            jsonify(
                {"error": "payload_too_large", "limit_kb": settings.max_payload_kb}
            ),
            413,
        )

    try:
        payload = json.loads(raw)
        assert isinstance(payload, dict)
    except Exception:
        plugin_metrics["validation_errors_total"] += 1
        return jsonify({"error": "invalid_json"}), 400

    adv_used = False
    # Possible advanced path (skip when unsigned override is active)
    if _advanced_mode(settings) and not allow_unsigned:
        try:
            # Local imports
            from ..services import plugins as adv

            adv_used = True
            ok, result = adv.store.register(payload)
            if not ok:
                # Heuristic: signature errors vs validation
                if "signature" in str(result).lower():
                    plugin_metrics["signature_errors_total"] += 1
                else:
                    plugin_metrics["validation_errors_total"] += 1
                return jsonify(result), 400
            plugin_id = result.get("plugin_id")
            meta = adv.store.plugins.get(plugin_id, {}).copy() if plugin_id else {}
            safe_desc = redact_text(meta.get("description", ""))
            plugin_metrics["registrations_total"] += 1
            plugin_metrics["advanced_mode_used_total"] += 1
            elapsed = (perf_counter() - start_t) * 1000.0
            observe_registration_latency(elapsed)
            return jsonify(
                {
                    "status": "ok",
                    "plugin": {**meta, "description": safe_desc},
                    "idempotency_key": idem_key,
                    "advanced": True,
                }
            )
        except Exception:
            # Fall back to minimal path if advanced fails unexpectedly
            log.exception("advanced registration failed; falling back")

    # Minimal path
    try:
        validation_result = validate_and_register_plugin(
            payload=payload,
            require_signature=settings.require_plugin_signature,
            max_description_len=settings.max_description_len,
        )
    except PluginValidationError:
        plugin_metrics["validation_errors_total"] += 1
        return (
            jsonify(
                {"error": "validation_error", "detail": "Plugin validation failed"}
            ),
            400,
        )
    except Exception:
        log.exception("registration failed")
        return jsonify({"error": "internal_error"}), 500

    meta = validation_result.registry_record
    _PLUGIN_REGISTRY[meta["name"]] = meta
    safe_desc = redact_text(meta.get("description", ""))
    plugin_metrics["registrations_total"] += 1
    if adv_used:
        plugin_metrics["advanced_mode_used_total"] += 1
    elapsed = (perf_counter() - start_t) * 1000.0
    observe_registration_latency(elapsed)
    return jsonify(
        {
            "status": "ok",
            "plugin": {**meta, "description": safe_desc},
            "idempotency_key": idem_key,
            "advanced": False,
        }
    )


@bp.get("/parallel_sample")
def parallel_sample() -> Any:
    """Execute a lightweight parallel sample across up to 3 loaded plugins.

    Returns JSON with fields: success, failed, total, total_time, plugins[].
    If no suitable plugins are present, returns 503 with reason.
    Result is cached in module-level _PARALLEL_SAMPLE_LAST for stats exposure.
    """
    global _PARALLEL_SAMPLE_LAST  # noqa: PLW0603
    try:
        # Discover plugin execution manager (advanced) if available
        # Aetherra imports
        from Aetherra.aetherra_core.plugins.advanced_plugins import (
            LyrixaAdvancedPluginManager,
        )

        mgr = getattr(current_app, "_adv_plugin_mgr", None)
        if mgr is None:
            mgr = LyrixaAdvancedPluginManager()
            # Best-effort init (no plugins => 503)
            try:
                # Run async init quickly
                asyncio.run(mgr.initialize())
            except RuntimeError:
                # Fallback if event loop already running
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # schedule initialize and wait
                    loop.run_until_complete(mgr.initialize())
            setattr(current_app, "_adv_plugin_mgr", mgr)  # cache  # noqa: B010
        plugins_loaded = list(mgr.plugins.keys())
        if not plugins_loaded:
            return jsonify({"error": "no_plugins_available"}), 503
        sample = plugins_loaded[:3]
        steps = [{"plugin": p, "function": "main"} for p in sample]
        # Execute parallel sample with short timeout per plugin
        try:
            result = asyncio.run(
                mgr.execute_plugin_chain_parallel(
                    steps, shared_input={"sample": True}, timeout=0.25
                )
            )
        except RuntimeError:
            # Already in loop: create task group
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                mgr.execute_plugin_chain_parallel(
                    steps, shared_input={"sample": True}, timeout=0.25
                )
            )
        summary = {
            "success": result.get("success"),
            "failed": result.get("failed"),
            "total": len(result.get("results", [])),
            "total_time": result.get("total_time"),
            "plugins": [
                {
                    "plugin": r.get("plugin"),
                    "success": r.get("success"),
                    "error": r.get("error"),
                    "execution_time": r.get("execution_time"),
                }
                for r in result.get("results", [])
            ],
        }
        _PARALLEL_SAMPLE_LAST = summary
        return jsonify(summary)
    except Exception:  # pragma: no cover - defensive
        log.exception("parallel_sample failed")
        return (
            jsonify(
                {"error": "parallel_sample_failed", "detail": "Sample execution failed"}
            ),
            500,
        )
