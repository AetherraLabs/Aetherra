#!/usr/bin/env python3
"""
🏪 Aetherra Hub Server
======================

Built-in Python-based plugin marketplace server for Aetherra OS.
Provides plugin registration, discovery, and basic marketplace functionality.
"""

import asyncio
import logging
import os
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional, cast

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Provide stubs so static analysis doesn't flag unbound names
    Flask = None  # type: ignore[assignment]
    jsonify = None  # type: ignore[assignment]
    request = None  # type: ignore[assignment]
    CORS = None  # type: ignore[assignment]
    print("⚠️ Flask not available - using mock hub server")

logger = logging.getLogger(__name__)


class AetherraHubServer:
    """🏪 Built-in Aetherra Hub Server"""

    def __init__(self, port: int = 3001):
        self.port = port
        self.plugins = {}
        self.stats = {
            "total_plugins": 0,
            "active_registrations": 0,
            "startup_time": datetime.now(),
            "requests_served": 0,
            "telemetry_received": 0,
            "last_telemetry_at": None,
        }
        self.server_running = False
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)  # type: ignore[name-defined]
            CORS(self.app)  # type: ignore[name-defined]  # Enable CORS for web interface
            self._setup_routes()
        else:
            self.app = None
        # In-process chat metrics (best-effort, hub-level)
        self.chat_metrics = {
            "requests_total": 0,
            "streams_current": 0,
            "latency_ms_sum": 0.0,
            "latency_count": 0,
            "chars_in_total": 0,
            "chars_out_total": 0,
            # Estimated token counters (heuristic unless tokenizer wired)
            "tokens_in_total": 0,
            "tokens_out_total": 0,
            # Simple latency histogram (ms) as raw per-bucket counts
            "latency_hist": {
                50: 0,
                100: 0,
                250: 0,
                500: 0,
                1000: 0,
                2000: 0,
                5000: 0,
                "+Inf": 0,
            },
        }
        # Rolling histograms (hub-level fallback) for latency
        self.kernel_latency_hist = {
            10: 0,
            20: 0,
            50: 0,
            100: 0,
            200: 0,
            500: 0,
            1000: 0,
            "+Inf": 0,
        }
        self.orchestrator_latency_hist = {
            10: 0,
            20: 0,
            50: 0,
            100: 0,
            200: 0,
            500: 0,
            1000: 0,
            2000: 0,
            "+Inf": 0,
        }

    def _setup_routes(self):
        """Setup Flask routes for the Hub API"""

        # Helper: run a coroutine to completion in a loop-safe way from sync Flask routes
        def _run_coro_blocking(coro):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                result_container: Dict[str, Any] = {}

                def _runner():
                    try:
                        new_loop = asyncio.new_event_loop()
                        try:
                            asyncio.set_event_loop(new_loop)
                            result_container["result"] = new_loop.run_until_complete(
                                coro
                            )
                        finally:
                            new_loop.close()
                    except Exception as e:
                        result_container["error"] = e

                t = threading.Thread(target=_runner)
                t.start()
                t.join(timeout=3.0)
                if "result" in result_container:
                    return result_container["result"]
                raise result_container.get("error", RuntimeError("async-run-timeout"))
            else:
                return asyncio.run(coro)

        # Optional imports for federation and telemetry
        try:
            from Aetherra.hub.federation import get_federation_manager

            self.federation = get_federation_manager(
                self_url=f"http://localhost:{self.port}"
            )
            # Seed peers from env
            peers_env = os.environ.get("AETHERRA_PEERS", "").strip()
            if peers_env:
                for p in [s.strip() for s in peers_env.split(",") if s.strip()]:
                    try:
                        self.federation.add_peer(p)
                    except Exception:
                        pass
        except Exception:
            self.federation = None
        try:
            from Aetherra.telemetry.optin import get_telemetry

            self.telemetry = get_telemetry()
        except Exception:
            self.telemetry = None
        try:
            from Aetherra.memory.graph_optics import summarize_memory_graph

            self.memory_summarizer = summarize_memory_graph
        except Exception:
            self.memory_summarizer = None
        # Optional signing verification
        try:
            import importlib

            ps = importlib.import_module("Aetherra.security.plugin_signing")
            self.verify_signature = getattr(ps, "verify_plugin_signature", None)
            # Capture module-level default strict (legacy) and library availability
            self.signing_strict = bool(getattr(ps, "STRICT", False))
            self._signing_has_lib = bool(getattr(ps, "NACL", False))
        except Exception:
            self.verify_signature = None
            self.signing_strict = False
            self._signing_has_lib = False
        # If Flask isn't available or app is None, skip route setup
        if not FLASK_AVAILABLE or self.app is None:
            return
        app = cast(Any, self.app)

        # --- CORS & Private Network Access (PNA) headers ---
        # Chrome 130+ requires Access-Control-Allow-Private-Network: true on preflight responses
        # when a public site accesses a private network resource (e.g., localhost).
        # We also set standard CORS headers and allow our custom auth header.
        @app.after_request
        def _add_cors_pna_headers(resp):  # type: ignore[override]
            """Add strict CORS and Private Network Access headers.

            Defaults: allow https://aetherra.dev and localhost origins only.
            Configure with:
              - AETHERRA_CORS_ALLOW_PATTERN: regex to match allowed Origin values
              - AETHERRA_PNA_ALLOW: '1' to enable Access-Control-Allow-Private-Network (default '1')
            """
            try:
                import re

                origin = request.headers.get("Origin")  # type: ignore[name-defined]
                allow_pattern = os.environ.get(
                    "AETHERRA_CORS_ALLOW_PATTERN",
                    r"^https?://(localhost|127\.0\.0\.1)(:\\d+)?$|^https://(www\.)?aetherra\.dev(:\\d+)?$",
                )
                pna_allow = os.environ.get("AETHERRA_PNA_ALLOW", "1").strip() == "1"
                allowed = bool(origin and re.match(allow_pattern, origin))
                if allowed:
                    resp.headers["Access-Control-Allow-Origin"] = origin
                    vary = resp.headers.get("Vary")
                    resp.headers["Vary"] = (vary + ", Origin") if vary else "Origin"
                    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                    resp.headers["Access-Control-Allow-Headers"] = (
                        "Content-Type, X-Aetherra-Token"
                    )
                    # Only opt into Private Network Access for allowed origins
                    if pna_allow:
                        resp.headers["Access-Control-Allow-Private-Network"] = "true"
                    resp.headers["Access-Control-Max-Age"] = "600"
                # Do not set wildcard or credentials; we purposely keep it strict.
            except Exception:
                pass
            return resp

        # Respond to any OPTIONS preflight early so clients don’t 404 on dynamic routes
        @app.route("/", methods=["OPTIONS"])  # type: ignore[misc]
        @app.route("/<path:_any>", methods=["OPTIONS"])  # type: ignore[misc]
        def _cors_options(_any: Optional[str] = None):
            from flask import make_response  # type: ignore

            # Empty 204 response; headers are added by after_request above
            return make_response(("", 204))

        # Internal helpers to access registry/kernel from sync Flask routes
        def _create_tokenizer():
            """Create a token counting function based on env + optional libs.

            AETHERRA_TOKENIZER: heuristic | tiktoken | engine (default: heuristic)
            AETHERRA_TOKENIZER_MODEL: e.g., cl100k_base
            """
            mode = os.environ.get("AETHERRA_TOKENIZER", "heuristic").strip().lower()
            if mode == "tiktoken":
                try:
                    import tiktoken  # type: ignore

                    model = os.environ.get("AETHERRA_TOKENIZER_MODEL", "cl100k_base")
                    enc = None
                    try:
                        enc = tiktoken.get_encoding(model)
                    except Exception:
                        try:
                            enc = tiktoken.encoding_for_model(model)
                        except Exception:
                            enc = tiktoken.get_encoding("cl100k_base")

                    def _cnt(text: str) -> int:
                        try:
                            return int(len(enc.encode(text or "")))
                        except Exception:
                            return int(max(1, round((len(text or "")) / 4)))

                    return _cnt
                except Exception:
                    pass
            if mode == "engine":

                def _cnt_engine(text: str) -> int:
                    def _call(eng):
                        try:
                            for name in (
                                "estimate_tokens",
                                "count_tokens",
                                "token_count",
                            ):
                                fn = getattr(eng, name, None)
                                if fn is not None:
                                    try:
                                        return True, int(fn(text))
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                        return True, int(max(1, round((len(text or "")) / 4)))

                    try:
                        ok, val = _with_engine_call(_call)
                        return (
                            int(val)
                            if ok
                            else int(max(1, round((len(text or "")) / 4)))
                        )
                    except Exception:
                        return int(max(1, round((len(text or "")) / 4)))

                return _cnt_engine

            # Default heuristic
            def _cnt_heur(text: str) -> int:
                try:
                    return int(max(1, round((len(text or "")) / 4)))
                except Exception:
                    return 1

            return _cnt_heur

        _count_tokens = _create_tokenizer()

        def _get_registry_status_sync():
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    return reg.get_registry_status()

                return _a.run(_run())
            except Exception:
                return None

        def _get_kernel_status_sync():
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("kernel_loop")
                    if not info:
                        return None
                    kernel = info.instance
                    if not kernel or not hasattr(kernel, "get_status"):
                        return None
                    return kernel.get_status()

                return _a.run(_run())
            except Exception:
                return None

        def _get_orchestrator_status_sync():
            """Best-effort lookup of orchestrator status via the engine service."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return None
                    eng = info.instance
                    orch = getattr(eng, "agent_orchestrator", None)
                    if orch and hasattr(orch, "get_system_status"):
                        try:
                            return orch.get_system_status()
                        except Exception:
                            return None
                    if hasattr(eng, "get_system_status"):
                        try:
                            st = await eng.get_system_status()  # type: ignore[attr-defined]
                            if isinstance(st, dict):
                                return st.get("agent_orchestrator")
                        except Exception:
                            return None
                    return None

                return _a.run(_run())
            except Exception:
                return None

        def _with_kernel_mutation(fn):
            """Helper to run a mutation against the kernel instance safely from Flask.

            Accepts either a sync function (kernel -> result) or an async function
            (kernel -> awaitable result). Returns (ok: bool, message|payload).
            """
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("kernel_loop")
                    if not info:
                        return False, "kernel not registered"
                    kernel = info.instance
                    if not kernel:
                        return False, "kernel instance unavailable"
                    try:
                        if _a.iscoroutinefunction(fn):
                            return await fn(kernel)
                        else:
                            return fn(kernel)
                    except Exception as e:  # pragma: no cover - surfaced to caller
                        return False, str(e)

                return _a.run(_run())
            except Exception as e:  # pragma: no cover - defensive
                return False, str(e)

        def _get_memory_quantum_status_sync():
            """Best-effort quantum memory status.

            Tries service registry → engine.memory_system.engine.get_status()
            Fallback: instantiate QuantumEnhancedMemoryEngine (ephemeral).
            """
            # Try via service registry and engine
            try:
                import asyncio as _a

                from aetherra_service_registry import (
                    get_service_registry as _get,
                )

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return None
                    eng = info.instance
                    ms = getattr(eng, "memory_system", None)
                    if ms is None:
                        return None
                    # Common shapes:
                    # - ms.get_quantum_status()
                    # - ms.engine.get_status()
                    if hasattr(ms, "get_quantum_status"):
                        try:
                            return {"enabled": True, **(await ms.get_quantum_status())}  # type: ignore[func-returns-value]
                        except Exception:
                            pass
                    inner = getattr(ms, "engine", None)
                    if inner is not None and hasattr(inner, "get_status"):
                        try:
                            st = inner.get_status()
                            if isinstance(st, dict):
                                return {"enabled": True, **st}
                        except Exception:
                            pass
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass

            # Fallback: ephemeral instance
            try:
                from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
                    QuantumEnhancedMemoryEngine as _Q,
                )

                q = _Q()
                st = q.get_status()
                if isinstance(st, dict):
                    st = dict(st)
                else:
                    st = {}
                st.update({"enabled": False, "ephemeral": True})
                return st
            except Exception:
                return {"enabled": False}

        def _get_memory_audit_sync():
            """Best-effort memory audit (branch DAG/edges) data.

            Tries service registry → engine.memory_system.engine.audit_branch_dag()
            Fallback: instantiate QuantumEnhancedMemoryEngine and call audit.
            """
            # Try via service registry and engine
            try:
                import asyncio as _a

                from aetherra_service_registry import (
                    get_service_registry as _get,
                )

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return None
                    eng = info.instance
                    ms = getattr(eng, "memory_system", None)
                    if ms is None:
                        return None
                    inner = getattr(ms, "engine", None)
                    target = inner or ms
                    if hasattr(target, "audit_branch_dag"):
                        try:
                            audit = target.audit_branch_dag()  # type: ignore[attr-defined]
                            if isinstance(audit, dict):
                                return {"enabled": True, "audit": audit}
                        except Exception:
                            pass
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass

            # Fallback: ephemeral instance
            try:
                from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
                    QuantumEnhancedMemoryEngine as _Q,
                )

                q = _Q()
                try:
                    audit = q.audit_branch_dag()
                except Exception:
                    audit = {}
                return {"enabled": False, "ephemeral": True, "audit": audit}
            except Exception:
                return {"enabled": False}

        @app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint"""
            self.stats["requests_served"] += 1
            return jsonify(
                {  # type: ignore[name-defined]
                    "status": "healthy",
                    "uptime_seconds": (
                        datetime.now() - self.stats["startup_time"]
                    ).total_seconds(),
                    "plugins_registered": len(self.plugins),
                    "requests_served": self.stats["requests_served"],
                }
            )

        @app.route("/status", methods=["GET"])
        def status_check():
            """Status endpoint for Hub connector compatibility"""
            self.stats["requests_served"] += 1
            return jsonify(
                {  # type: ignore[name-defined]
                    "status": "online",
                    "running": True,
                    "uptime_seconds": (
                        datetime.now() - self.stats["startup_time"]
                    ).total_seconds(),
                    "plugins_registered": len(self.plugins),
                    "requests_served": self.stats["requests_served"],
                    "hub_connected": True,
                    "services": ["hub_server", "plugin_registry"],
                    "capabilities": [
                        "plugin_registration",
                        "plugin_discovery",
                        "marketplace",
                    ],
                }
            )

        @app.route("/api/plugins", methods=["GET"])
        def list_plugins():
            """List all registered plugins"""
            self.stats["requests_served"] += 1
            data = {
                "plugins": list(self.plugins.values()),
                "total": len(self.plugins),
                "timestamp": datetime.now().isoformat(),
            }
            # Include federated view if available
            if self.federation is not None:
                data["federated"] = self.federation.get_federated_plugins()
                data["peers"] = self.federation.list_peers()
            return jsonify(data)  # type: ignore[name-defined]

        @app.route("/api/plugins/register", methods=["POST"])
        def register_plugin():
            """Register a new plugin"""
            try:
                plugin_data = request.get_json()  # type: ignore[name-defined]
                if not plugin_data or not isinstance(plugin_data, dict):
                    return jsonify({"error": "Invalid plugin data"}), 400  # type: ignore[name-defined]

                # Determine strictness at request time (env-driven)
                strict_env = (
                    os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1"
                    or os.environ.get("AETHERRA_HUB_STRICT", "0") == "1"
                    or os.environ.get("AETHERRA_STRICT", "0") == "1"
                )
                # Determine strictness from environment only (test-driven behavior)
                strict = bool(strict_env)

                # Validate manifest schema before any mutation (always enforced)
                schema_errors = []
                normalized = dict(plugin_data)
                try:
                    from Aetherra.plugins.manifest_schema import validate_manifest

                    ok, errs, norm = validate_manifest(plugin_data)
                    schema_errors = errs
                    normalized = norm
                except Exception:
                    # If validator unavailable, respond with a clear error in strict
                    # and accept in non-strict for dev convenience
                    ok = not strict
                if not ok:
                    # In non-strict mode, allow a minimal manifest missing only entry_point
                    soft_entry_only = (
                        not strict
                        and isinstance(schema_errors, list)
                        and len(schema_errors) == 1
                        and (
                            "entry_point" in str(schema_errors[0])
                            and "required" in str(schema_errors[0])
                        )
                    )
                    if soft_entry_only:
                        # Fill a safe default entry point for dev; proceed
                        normalized = dict(plugin_data)
                        normalized.setdefault("entry_point", "main.py")
                        ok = True
                    else:
                        return (
                            jsonify(
                                {"error": "manifest_invalid", "details": schema_errors}
                            ),  # type: ignore[name-defined]
                            400,
                        )

                # Verify signature (before mutating payload)
                has_sig = bool(plugin_data.get("signature")) and bool(
                    plugin_data.get("pubkey")
                )
                verified = False
                if strict:
                    # In strict mode, signature must be present and valid
                    if not has_sig:
                        return jsonify({"error": "invalid signature"}), 400  # type: ignore[name-defined]
                    # Quick sanity check: signature and pubkey must be valid base64
                    try:
                        import base64 as _b64

                        sig_b64 = str(plugin_data.get("signature"))
                        pk_b64 = str(plugin_data.get("pubkey"))
                        _ = _b64.b64decode(sig_b64, validate=True)
                        _ = _b64.b64decode(pk_b64, validate=True)
                    except Exception:
                        return jsonify({"error": "invalid signature"}), 400  # type: ignore[name-defined]
                    # If verification library is unavailable, reject in strict mode
                    if not getattr(self, "_signing_has_lib", False):
                        return (
                            jsonify({"error": "signature verification unavailable"}),  # type: ignore[name-defined,operator]
                            400,
                        )
                    if getattr(self, "verify_signature", None) is None:
                        return jsonify(  # type: ignore[name-defined,operator]
                            {"error": "signature verification unavailable"}
                        ), 400
                    try:
                        verified = bool(self.verify_signature(plugin_data))  # type: ignore[call-arg]
                    except Exception:
                        verified = False
                    if not verified:
                        return jsonify({"error": "invalid signature"}), 400  # type: ignore[name-defined]
                else:
                    # Non-strict: verify if signature present; otherwise allow
                    if has_sig and getattr(self, "verify_signature", None) is not None:
                        try:
                            verified = bool(self.verify_signature(plugin_data))  # type: ignore[call-arg]
                        except Exception:
                            verified = False

                # Compute trust zone mapping
                trust_zone = "unsigned"
                try:
                    from Aetherra.plugins.manifest_schema import compute_trust_zone

                    trust_zone = compute_trust_zone(strict, bool(verified))
                except Exception:
                    trust_zone = "unsigned"

                # Use normalized manifest for storage
                plugin_id = (
                    normalized.get("name")
                    or plugin_data.get("name")
                    or f"plugin_{len(self.plugins) + 1}"
                )
                # Mutate only after verification
                normalized["registered_at"] = datetime.now().isoformat()
                normalized["status"] = "registered"
                normalized["signature_verified"] = bool(verified)
                normalized["trust_zone"] = trust_zone

                self.plugins[plugin_id] = normalized
                self.stats["requests_served"] += 1
                self.stats["active_registrations"] += 1

                logger.info(f"[OK] Plugin registered: {plugin_id}")

                return jsonify(
                    {  # type: ignore[name-defined]
                        "status": "success",
                        "message": f"Plugin {plugin_id} registered successfully",
                        "plugin_id": plugin_id,
                    }
                )

            except Exception as e:
                logger.error(f"❌ Plugin registration failed: {e}")
                return jsonify({"error": str(e)}), 500  # type: ignore[name-defined]

        @app.route("/api/plugins/<plugin_id>", methods=["GET"])
        def get_plugin(plugin_id):
            """Get specific plugin details"""
            self.stats["requests_served"] += 1
            if plugin_id in self.plugins:
                return jsonify(self.plugins[plugin_id])  # type: ignore[name-defined]
            else:
                return jsonify({"error": "Plugin not found"}), 404  # type: ignore[name-defined]

        @app.route("/api/stats", methods=["GET"])
        def get_stats():
            """Get Hub statistics"""
            self.stats["requests_served"] += 1
            out = dict(self.stats)
            # Best-effort: include Lyrixa chat service availability from the registry
            try:
                from aetherra_service_registry import get_service_registry

                async def _get():
                    reg = await get_service_registry()
                    info = reg.get_service_info("lyrixa_chat")
                    if not info:
                        return {"registered": False}
                    return {
                        "registered": True,
                        "status": getattr(info.status, "value", str(info.status)),
                        "registered_at": info.registered_at.isoformat(),
                        "last_heartbeat": info.last_heartbeat.isoformat(),
                    }

                out["lyrixa_chat"] = _run_coro_blocking(_get())
            except Exception:
                out["lyrixa_chat"] = {"registered": False}
            if self.federation is not None:
                out["peers"] = self.federation.list_peers()
                out["federated_count"] = len(self.federation.get_federated_plugins())
            return jsonify(out)  # type: ignore[name-defined]

        @app.route("/api/registry/status", methods=["GET"])
        def api_registry_status():
            """Expose the Service Registry status (counts, services, timestamps)."""
            self.stats["requests_served"] += 1
            status = _get_registry_status_sync()
            if not isinstance(status, dict):
                status = {"running": False}
            return jsonify(status)  # type: ignore[name-defined]

        @app.route("/api/kernel/metrics", methods=["GET"])
        def api_kernel_metrics():
            """Expose kernel status/metrics as JSON via the Hub."""
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync()
            if not isinstance(ks, dict):
                ks = {"running": False}
            # Add minimal hub context
            return jsonify({"hub_ts": datetime.now().isoformat(), "kernel": ks})  # type: ignore[name-defined]

        @app.route("/api/kernel/status", methods=["GET"])
        def api_kernel_status():
            """Return kernel get_status() as JSON (lightweight)."""
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync()
            if not isinstance(ks, dict):
                ks = {"running": False}
            return jsonify(ks)  # type: ignore[name-defined]

        @app.route("/api/site_status", methods=["GET"])
        @app.route("/site_status", methods=["GET"])  # alias for older/alternate clients
        def api_site_status():
            """Aggregated status for Docs widget to minimize cross-origin requests.

            Returns a JSON bundle with:
            - plugins.total: count of registered plugins
            - kernel.running: boolean if kernel is running
            - kernel.uptime_seconds: numeric uptime if available
            - kernel.queue_sizes: {high_priority, normal_priority, background}
            - hub.ts: ISO timestamp when generated
            - hub.requests_served: hub request counter
            """
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync()
            if not isinstance(ks, dict):
                ks = {}
            # Derive running state and uptime
            running = bool(
                ks.get("running") is True or str(ks.get("state", "")).lower() == "running"
            )
            uptime = 0.0
            try:
                # Prefer direct uptime key; fallback to metrics.uptime if present
                if isinstance(ks.get("uptime"), (int, float)):
                    uptime = float(ks.get("uptime") or 0.0)
                else:
                    uptime = float((ks.get("metrics", {}) or {}).get("uptime", 0.0))
            except Exception:
                uptime = 0.0
            # Queue sizes map
            qs = ks.get("queue_sizes", {}) if isinstance(ks.get("queue_sizes"), dict) else {}
            out = {
                "ok": True,
                "hub": {
                    "ts": datetime.now().isoformat(),
                    "requests_served": self.stats.get("requests_served", 0),
                },
                "plugins": {"total": int(len(self.plugins))},
                "kernel": {
                    "running": running,
                    "uptime_seconds": uptime,
                    "queue_sizes": {
                        "high_priority": int(qs.get("high_priority", 0) or 0),
                        "normal_priority": int(qs.get("normal_priority", 0) or 0),
                        "background": int(qs.get("background", 0) or 0),
                    },
                },
            }
            return jsonify(out)  # type: ignore[name-defined]

        @app.route("/metrics", methods=["GET"])
        def prometheus_metrics():
            """Prometheus-style plaintext metrics for quick scraping."""
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync() or {}
            rs = _get_registry_status_sync() or {}
            os = _get_orchestrator_status_sync() or {}
            ms = _get_memory_quantum_status_sync() or {}
            ma = _get_memory_audit_sync() or {}

            lines = []
            # Track whether we emitted histogram series; if not, emit zero fallbacks
            kernel_hist_emitted = False
            orch_hist_emitted = False

            # helper for safe numeric conversion (defined at function scope)
            def _num(x):
                try:
                    return float(x)
                except Exception:
                    return 0.0

            # Kernel metrics
            try:
                if isinstance(ks, dict) and ks:
                    m = ks.get("metrics", {}) or {}
                    qs = ks.get("queue_sizes", {}) or {}
                    ql = ks.get("queue_limits", {}) or {}
                    cb_open = bool(ks.get("plugin_cb_open", False))
                    dlq_count = int(ks.get("dlq_count", 0))
                    uptime = float(ks.get("uptime", 0))

                    lines.append(f"aetherra_kernel_uptime_seconds {_num(uptime)}")
                    lines.append(
                        f"aetherra_kernel_cycles_total {_num(m.get('total_cycles', 0))}"
                    )
                    lines.append(
                        f"aetherra_kernel_cycle_time_seconds {_num(m.get('last_cycle_time', 0.0))}"
                    )
                    lines.append(
                        f"aetherra_kernel_cycle_time_seconds_avg {_num(m.get('avg_cycle_time', 0.0))}"
                    )
                    lines.append(
                        f"aetherra_kernel_errors_total {_num(m.get('errors_count', 0))}"
                    )
                    lines.append(
                        f"aetherra_kernel_night_cycles_total {_num(m.get('night_cycles_count', 0))}"
                    )
                    lines.append(
                        f'aetherra_kernel_queue_size{{queue="high"}} {_num(qs.get("high_priority", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_size{{queue="normal"}} {_num(qs.get("normal_priority", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_size{{queue="background"}} {_num(qs.get("background", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_limit{{queue="high"}} {_num(ql.get("high_priority", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_limit{{queue="normal"}} {_num(ql.get("normal_priority", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_limit{{queue="background"}} {_num(ql.get("background", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_drops_total{{queue="high"}} {_num(m.get("drops_high", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_drops_total{{queue="normal"}} {_num(m.get("drops_normal", 0))}'
                    )
                    lines.append(
                        f'aetherra_kernel_queue_drops_total{{queue="background"}} {_num(m.get("drops_background", 0))}'
                    )
                    lines.append(
                        f"aetherra_kernel_tasks_expired_total {_num(m.get('expired_tasks', 0))}"
                    )
                    lines.append(f"aetherra_kernel_dlq_count {_num(dlq_count)}")
                    lines.append(
                        f"aetherra_kernel_plugin_cb_open {1 if cb_open else 0}"
                    )
                    # Plugin invoke metrics if present
                    for k in (
                        "plugin_invoke_timeouts",
                        "plugin_invoke_errors",
                        "plugin_cb_open_count",
                        "plugin_invoke_rate_limited",
                    ):
                        if k in m:
                            lines.append(f"aetherra_kernel_{k} {_num(m.get(k, 0))}")
                    # Latency histogram (cycle time), prefer provided histogram if any
                    hist = m.get("cycle_hist") or {}
                    if isinstance(hist, dict) and hist:
                        # assume ms buckets
                        try:
                            order = sorted(
                                [float(x) for x in hist.keys() if x != "+Inf"]
                            )  # type: ignore[arg-type]
                            cum = 0.0
                            for b in order:
                                v = _num(hist.get(b, 0))
                                cum += max(0.0, v)
                                lines.append(
                                    f'aetherra_kernel_cycle_time_ms_bucket{{le="{int(b)}"}} {cum}'
                                )
                            kernel_hist_emitted = True
                            inf_v = _num(hist.get("+Inf", 0))
                            lines.append(
                                f'aetherra_kernel_cycle_time_ms_bucket{{le="+Inf"}} {cum + max(0.0, inf_v)}'
                            )
                        except Exception:
                            pass
                    else:
                        # Rolling fallback: accumulate last_cycle_time into hub histogram and export cumulative
                        try:
                            raw = float(m.get("last_cycle_time", 0.0))
                            ms_val = raw * 1000.0 if raw < 10 else raw
                        except Exception:
                            ms_val = 0.0
                        if ms_val > 0:
                            placed = False
                            for b in (10, 20, 50, 100, 200, 500, 1000):
                                if ms_val <= b:
                                    self.kernel_latency_hist[b] = (
                                        int(self.kernel_latency_hist.get(b, 0)) + 1
                                    )
                                    placed = True
                                    break
                            if not placed:
                                self.kernel_latency_hist["+Inf"] = (
                                    int(self.kernel_latency_hist.get("+Inf", 0)) + 1
                                )
                        cum = 0
                        for b in (10, 20, 50, 100, 200, 500, 1000):
                            cum += int(self.kernel_latency_hist.get(b, 0))
                            lines.append(
                                f'aetherra_kernel_cycle_time_ms_bucket{{le="{b}"}} {_num(cum)}'
                            )
                        kernel_hist_emitted = True
                        lines.append(
                            f'aetherra_kernel_cycle_time_ms_bucket{{le="+Inf"}} {_num(cum + int(self.kernel_latency_hist.get("+Inf", 0)))}'
                        )
            except Exception:
                pass

            # If kernel histogram wasn't emitted (e.g., services not ready), publish zero-valued buckets to ensure series presence
            if not kernel_hist_emitted:
                try:
                    cum = 0.0
                    for b in (10, 20, 50, 100, 200, 500, 1000):
                        lines.append(
                            f'aetherra_kernel_cycle_time_ms_bucket{{le="{b}"}} 0.0'
                        )
                    lines.append(
                        'aetherra_kernel_cycle_time_ms_bucket{le="+Inf"} 0.0'.replace(
                            "{", "{{"
                        ).replace("}", "}}")
                    )
                except Exception:
                    pass

            # Registry metrics
            try:
                if isinstance(rs, dict) and rs:
                    lines.append(
                        f"aetherra_registry_services_total {_num(rs.get('total_services', 0))}"
                    )
                    sc = rs.get("service_count_by_status") or {}
                    for st, cnt in sc.items():
                        lines.append(
                            f'aetherra_registry_services{{status="{st}"}} {_num(cnt)}'
                        )
            except Exception:
                pass

            # Orchestrator metrics
            try:
                if isinstance(os, dict) and os:
                    lines.append(
                        f"aetherra_orchestrator_agents_total {_num(os.get('total_agents', 0))}"
                    )
                    lines.append(
                        f"aetherra_orchestrator_tasks_pending_total {_num(os.get('pending_tasks', 0))}"
                    )
                    # Active tasks gauge (if provided)
                    if "active_tasks" in os:
                        lines.append(
                            f"aetherra_orchestrator_tasks_active {_num(os.get('active_tasks', 0))}"
                        )
                    # Pending by priority (if available)
                    pbp = os.get("pending_by_priority") or {}
                    if isinstance(pbp, dict):
                        for prio, cnt in pbp.items():
                            lines.append(
                                f'aetherra_orchestrator_tasks_pending{{priority="{prio}"}} {_num(cnt)}'
                            )
                    # Task status breakdown (if available)
                    tstat = os.get("task_statuses") or {}
                    if isinstance(tstat, dict):
                        for st, cnt in tstat.items():
                            lines.append(
                                f'aetherra_orchestrator_tasks_total{{status="{st}"}} {_num(cnt)}'
                            )
                    # Generic counters (timeouts, policy_denied, etc.)
                    ctrs = os.get("counters") or {}
                    if isinstance(ctrs, dict):
                        for k, v in ctrs.items():
                            lines.append(f"aetherra_orchestrator_{str(k)} {_num(v)}")
                    # Orchestrator latency histogram (if provided or approximate)
                    oh = (
                        os.get("latency_hist_ms")
                        or os.get("task_latency_hist_ms")
                        or {}
                    )
                    if isinstance(oh, dict) and oh:
                        try:
                            order = sorted([float(x) for x in oh.keys() if x != "+Inf"])  # type: ignore[arg-type]
                            cum = 0.0
                            for b in order:
                                v = _num(oh.get(b, 0))
                                cum += max(0.0, v)
                                lines.append(
                                    f'aetherra_orchestrator_task_latency_ms_bucket{{le="{int(b)}"}} {cum}'
                                )
                            orch_hist_emitted = True
                            inf_v = _num(oh.get("+Inf", 0))
                            lines.append(
                                f'aetherra_orchestrator_task_latency_ms_bucket{{le="+Inf"}} {cum + max(0.0, inf_v)}'
                            )
                        except Exception:
                            pass
                    else:
                        # Rolling fallback: accumulate avg_task_latency_ms into hub histogram and export cumulative
                        try:
                            ms_val = float(os.get("avg_task_latency_ms", 0.0))
                        except Exception:
                            ms_val = 0.0
                        if ms_val > 0:
                            placed = False
                            for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
                                if ms_val <= b:
                                    self.orchestrator_latency_hist[b] = (
                                        int(self.orchestrator_latency_hist.get(b, 0))
                                        + 1
                                    )
                                    placed = True
                                    break
                            if not placed:
                                self.orchestrator_latency_hist["+Inf"] = (
                                    int(self.orchestrator_latency_hist.get("+Inf", 0))
                                    + 1
                                )
                        cum = 0
                        for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
                            cum += int(self.orchestrator_latency_hist.get(b, 0))
                            lines.append(
                                f'aetherra_orchestrator_task_latency_ms_bucket{{le="{b}"}} {_num(cum)}'
                            )
                        orch_hist_emitted = True
                        lines.append(
                            f'aetherra_orchestrator_task_latency_ms_bucket{{le="+Inf"}} {_num(cum + int(self.orchestrator_latency_hist.get("+Inf", 0)))}'
                        )
            except Exception:
                pass

            # If orchestrator histogram wasn't emitted yet, ensure presence with zero-valued buckets
            if not orch_hist_emitted:
                try:
                    for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
                        lines.append(
                            f'aetherra_orchestrator_task_latency_ms_bucket{{le="{b}"}} 0.0'
                        )
                    lines.append(
                        'aetherra_orchestrator_task_latency_ms_bucket{le="+Inf"} 0.0'.replace(
                            "{", "{{"
                        ).replace("}", "}}")
                    )
                except Exception:
                    pass

            # Memory (quantum) metrics
            try:
                if isinstance(ms, dict) and ms:
                    # Only emit when we have structure
                    if "coherence" in ms:
                        lines.append(
                            f"aetherra_memory_coherence_score {_num(ms.get('coherence', 0.0))}"
                        )
                    if "branches" in ms:
                        lines.append(
                            f"aetherra_memory_branches_total {_num(ms.get('branches', 0))}"
                        )
                    if "fragments" in ms:
                        lines.append(
                            f"aetherra_memory_fragments_total {_num(ms.get('fragments', 0))}"
                        )
                    if "entanglement_nodes" in ms:
                        lines.append(
                            f"aetherra_memory_entanglement_nodes_total {_num(ms.get('entanglement_nodes', 0))}"
                        )
                    # Optional branch info as a gauge (low cardinality expected)
                    if isinstance(ms.get("branch"), str):
                        br = str(ms.get("branch"))
                        lines.append(f'aetherra_memory_branch_info{{branch="{br}"}} 1')
                # Optional branch edges metric from audit
                if isinstance(ma, dict) and ma:
                    audit = ma.get("audit") or {}
                    if isinstance(audit, dict):
                        # Nodes count
                        nodes_cnt = None
                        nodes_val = audit.get("nodes")
                        if isinstance(nodes_val, (list, tuple)):
                            try:
                                nodes_cnt = len(nodes_val)
                            except Exception:
                                nodes_cnt = None
                        if nodes_cnt is None and isinstance(
                            audit.get("node_count"), (int, float)
                        ):
                            nodes_cnt = audit.get("node_count")
                        if nodes_cnt is not None:
                            lines.append(
                                f"aetherra_memory_branch_nodes_total {_num(nodes_cnt)}"
                            )
                        # Edges count
                        edge_cnt = None
                        edges_val = audit.get("edges")
                        if isinstance(edges_val, (list, tuple)):
                            try:
                                edge_cnt = len(edges_val)
                            except Exception:
                                edge_cnt = None
                            # Edges by type
                            try:
                                by_type = {}
                                for e in edges_val:
                                    if isinstance(e, dict):
                                        t = (
                                            str(e.get("type") or "").strip()
                                            or "unknown"
                                        )
                                        by_type[t] = int(by_type.get(t, 0)) + 1
                                for t, cnt in by_type.items():
                                    lines.append(
                                        f'aetherra_memory_branch_edges_total_by_type{{type="{t}"}} {_num(cnt)}'
                                    )
                            except Exception:
                                pass
                        if edge_cnt is None and isinstance(
                            audit.get("edge_count"), (int, float)
                        ):
                            edge_cnt = audit.get("edge_count")
                        if edge_cnt is not None:
                            lines.append(
                                f"aetherra_memory_branch_edges_total {_num(edge_cnt)}"
                            )
                        # Optional low-cardinality per-branch gauges
                        try:
                            nodes_by_branch = {}
                            if isinstance(nodes_val, (list, tuple)):
                                for n in nodes_val:
                                    if isinstance(n, dict):
                                        br = str(
                                            n.get("branch") or n.get("branch_id") or ""
                                        ).strip()
                                        if br:
                                            nodes_by_branch[br] = (
                                                int(nodes_by_branch.get(br, 0)) + 1
                                            )
                            edges_by_branch = {}
                            if isinstance(edges_val, (list, tuple)):
                                for e in edges_val:
                                    if isinstance(e, dict):
                                        br = str(
                                            e.get("branch")
                                            or e.get("src_branch")
                                            or e.get("src_branch_id")
                                            or ""
                                        ).strip()
                                        if br:
                                            edges_by_branch[br] = (
                                                int(edges_by_branch.get(br, 0)) + 1
                                            )
                            # Emit only when small to avoid cardinality bloat
                            if 0 < len(nodes_by_branch) <= 8:
                                for br, cnt in nodes_by_branch.items():
                                    lines.append(
                                        f'aetherra_memory_branch_nodes{{branch="{br}"}} {_num(cnt)}'
                                    )
                            if 0 < len(edges_by_branch) <= 8:
                                for br, cnt in edges_by_branch.items():
                                    lines.append(
                                        f'aetherra_memory_branch_edges{{branch="{br}"}} {_num(cnt)}'
                                    )
                        except Exception:
                            pass
            except Exception:
                pass

            # Chat metrics (hub-level)
            try:
                cm = self.chat_metrics
                lines.append(
                    f"aetherra_chat_requests_total {_num(cm.get('requests_total', 0))}"
                )
                lines.append(
                    f"aetherra_chat_streams_current {_num(cm.get('streams_current', 0))}"
                )
                # Export sum and count to allow histogram-like calc in PromQL
                lines.append(
                    f"aetherra_chat_latency_ms_sum {_num(cm.get('latency_ms_sum', 0.0))}"
                )
                lines.append(
                    f"aetherra_chat_latency_count {_num(cm.get('latency_count', 0))}"
                )
                # Histogram buckets (cumulative)
                try:
                    hist = cm.get("latency_hist", {}) or {}
                    order = [50, 100, 250, 500, 1000, 2000, 5000]
                    cum = 0
                    for b in order:
                        cnt = int(hist.get(b, 0))
                        cum += max(0, cnt)
                        lines.append(
                            f'aetherra_chat_latency_ms_bucket{{le="{b}"}} {_num(cum)}'
                        )
                    inf_cnt = int(hist.get("+Inf", 0)) + cum
                    lines.append(
                        f'aetherra_chat_latency_ms_bucket{{le="+Inf"}} {_num(inf_cnt)}'
                    )
                except Exception:
                    pass
                lines.append(
                    f"aetherra_chat_chars_in_total {_num(cm.get('chars_in_total', 0))}"
                )
                lines.append(
                    f"aetherra_chat_chars_out_total {_num(cm.get('chars_out_total', 0))}"
                )
                # Token totals
                lines.append(
                    f"aetherra_chat_tokens_in_total {_num(cm.get('tokens_in_total', 0))}"
                )
                lines.append(
                    f"aetherra_chat_tokens_out_total {_num(cm.get('tokens_out_total', 0))}"
                )
            except Exception:
                pass

            body = "\n".join(lines) + "\n"
            from flask import Response  # type: ignore

            return Response(body, mimetype="text/plain; version=0.0.4; charset=utf-8")  # type: ignore[call-arg]

        # ---------------- Control-plane (opt-in, token-guarded) -----------------
        def _control_enabled_and_token_ok(req):
            if os.environ.get("AETHERRA_HUB_CONTROL_ENABLED", "0") != "1":
                return False, (jsonify({"error": "disabled"}), 501)  # type: ignore[name-defined]
            expected = os.environ.get("AETHERRA_HUB_CONTROL_TOKEN", "").strip()
            if not expected:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            got = req.headers.get("X-Aetherra-Token", "").strip()
            if got != expected:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            return True, None

        # ---------------- Optional AI developer API (opt-in) -----------------
        def _ai_enabled_and_token_ok(req):
            if os.environ.get("AETHERRA_AI_API_ENABLED", "0") != "1":
                return False, (jsonify({"error": "disabled"}), 501)  # type: ignore[name-defined]
            # Optional token check: prefer dedicated AI token, fall back to hub control token
            require = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
            if not require:
                return True, None
            token = (
                os.environ.get("AETHERRA_AI_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                or ""
            ).strip()
            if not token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            got = req.headers.get("X-Aetherra-Token", "").strip()
            if got != token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            return True, None

        def _with_engine_call(fn):
            """Call into the registered Aetherra engine (sync or async)."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return False, "engine not registered"
                    impl = info.instance
                    try:
                        if _a.iscoroutinefunction(fn):
                            return await fn(impl)
                        else:
                            return fn(impl)
                    except Exception as e:
                        return False, str(e)

                return _a.run(_run())
            except Exception as e:
                return False, str(e)

        @app.route("/api/kernel/control/pause", methods=["POST"])
        def api_kernel_pause():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _do(kernel):
                kernel.pause()
                return True, "paused"

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/kernel/control/resume", methods=["POST"])
        def api_kernel_resume():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _do(kernel):
                kernel.resume()
                return True, "resumed"

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/kernel/control/drain", methods=["POST"])
        def api_kernel_drain():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            name = str(body.get("queue") or "").strip()
            mode = str(body.get("mode") or "dlq").strip()
            if name not in ("high_priority", "normal_priority", "background"):
                return jsonify({"error": "invalid queue"}), 400  # type: ignore[name-defined]

            async def _do(kernel):
                await kernel.drain_queue(name, mode=mode)
                return True, f"drained:{name}:{mode}"

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/kernel/control/queue_limits", methods=["POST"])
        def api_kernel_queue_limits():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            limits = request.get_json(silent=True) or {}  # type: ignore[name-defined]

            def _do(kernel):
                try:
                    kernel.set_queue_limits(limits)
                    return True, {
                        "queue_limits": kernel.get_status().get("queue_limits", {})
                    }
                except Exception as e:
                    return False, str(e)

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/peers", methods=["GET", "POST"])
        def peers_endpoint():
            """List/add federation peers."""
            self.stats["requests_served"] += 1
            if self.federation is None:
                return jsonify({"peers": [], "enabled": False})  # type: ignore[name-defined]
            if request.method == "POST":  # type: ignore[name-defined]
                body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
                url = body.get("url")
                if url:
                    self.federation.add_peer(url)
                return jsonify({"status": "ok"})  # type: ignore[name-defined]
            return jsonify({"peers": self.federation.list_peers(), "enabled": True})  # type: ignore[name-defined]

        @app.route("/api/peers/sync", methods=["POST"])  # manual trigger
        def peers_sync():
            self.stats["requests_served"] += 1
            if self.federation is None:
                return jsonify({"synced": False, "reason": "disabled"}), 501  # type: ignore[name-defined]
            try:
                self.federation.sync_once()
                return jsonify(
                    {
                        "synced": True,
                        "federated_count": len(self.federation.get_federated_plugins()),
                    }
                )  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"peer sync error: {e}")
                return jsonify({"synced": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/peers/announce", methods=["POST"])  # best-effort gossip
        def peers_announce():
            self.stats["requests_served"] += 1
            if self.federation is None:
                return jsonify({"announced": False, "reason": "disabled"}), 501  # type: ignore[name-defined]
            try:
                self.federation.announce_once()
                return jsonify({"announced": True})  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"peer announce error: {e}")
                return jsonify({"announced": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/ai/ask", methods=["POST"])
        def ai_ask():
            """Optional developer AI endpoint to ask the engine; disabled by default."""
            self.stats["requests_served"] += 1
            ok, resp = _ai_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            msg = str(body.get("message") or body.get("content") or "").strip()
            ctx = body.get("context") if isinstance(body.get("context"), dict) else {}
            # Hub-level chat observability (request received)
            try:
                self.chat_metrics["requests_total"] += 1
                self.chat_metrics["chars_in_total"] += len(msg)
                # Token estimate
                self.chat_metrics["tokens_in_total"] += _count_tokens(msg)
            except Exception:
                pass
            import time as _t

            _t0 = _t.time()

            async def _call(engine):
                try:
                    result = await engine.process_message(msg, ctx)
                    return True, result
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            # Update latency and output size even on failure (best-effort)
            try:
                dt_ms = (time.time() - _t0) * 1000.0  # type: ignore[name-defined]
            except Exception:
                try:
                    import time as _t2

                    dt_ms = (_t2.time() - _t0) * 1000.0
                except Exception:
                    dt_ms = 0.0
            try:
                self.chat_metrics["latency_ms_sum"] += float(dt_ms)
                self.chat_metrics["latency_count"] += 1
                # Histogram bucketing
                try:
                    ms_val = float(dt_ms)
                    hist = self.chat_metrics.get("latency_hist", {}) or {}
                    placed = False
                    for b in (50, 100, 250, 500, 1000, 2000, 5000):
                        if ms_val <= b:
                            hist[b] = int(hist.get(b, 0)) + 1
                            placed = True
                            break
                    if not placed:
                        hist["+Inf"] = int(hist.get("+Inf", 0)) + 1
                    self.chat_metrics["latency_hist"] = hist
                except Exception:
                    pass
                if success and isinstance(payload, dict):
                    out = payload.get("result") or payload
                    # count characters from result.response if present
                    if isinstance(out, dict):
                        txt = str(out.get("response") or "")
                    else:
                        txt = str(out)
                    self.chat_metrics["chars_out_total"] += len(txt)
                    self.chat_metrics["tokens_out_total"] += _count_tokens(txt)
            except Exception:
                pass
            if success:
                return jsonify({"ok": True, "result": payload})  # type: ignore[name-defined]
            return jsonify({"ok": False, "error": payload}), code  # type: ignore[name-defined]

        @app.route("/api/ai/stream", methods=["POST"])
        def ai_stream():
            """Server-Sent Events stream for developer AI; opt-in and token-guarded.

            Emits a short sequence of events: status -> token -> (trace?) -> final.
            """
            self.stats["requests_served"] += 1
            # Must be enabled globally and streaming flag set
            ok, resp = _ai_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            if os.environ.get("AETHERRA_AI_API_STREAM", "0") != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]

            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            msg = str(body.get("message") or body.get("content") or "").strip()
            ctx = body.get("context") if isinstance(body.get("context"), dict) else {}

            def _sse(event: str, data: Dict[str, Any]):
                import json as _json

                return f"event: {event}\ndata: {_json.dumps(data)}\n\n"

            def _generate():
                # Mark stream open
                try:
                    self.chat_metrics["streams_current"] += 1
                    self.chat_metrics["requests_total"] += 1
                    self.chat_metrics["chars_in_total"] += len(msg)
                    self.chat_metrics["tokens_in_total"] += _count_tokens(msg)
                except Exception:
                    pass
                # Initial status
                yield _sse("status", {"phase": "start"})
                # Token confirmation
                require = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
                yield _sse("token", {"required": require, "ok": True})

                # Call engine and stream final result
                async def _call(engine):
                    try:
                        result = await engine.process_message(msg, ctx)
                        return True, result
                    except Exception as e:
                        return False, str(e)

                import time as _t

                _t0s = _t.time()
                try:
                    result = _with_engine_call(_call)
                except Exception as e:  # pragma: no cover - defensive
                    result = (False, str(e))

                if not isinstance(result, tuple) or len(result) != 2:
                    success, payload = False, "server"
                else:
                    success, payload = result  # type: ignore[assignment]

                if success:
                    yield _sse("final", {"ok": True, "result": payload})
                else:
                    yield _sse("final", {"ok": False, "error": payload})
                # Stream closed
                try:
                    self.chat_metrics["streams_current"] = max(
                        0, int(self.chat_metrics.get("streams_current", 0)) - 1
                    )
                    # Update latency aggregates and histogram
                    try:
                        dt_ms = (time.time() - _t0s) * 1000.0  # type: ignore[name-defined]
                    except Exception:
                        try:
                            dt_ms = (_t.time() - _t0s) * 1000.0
                        except Exception:
                            dt_ms = 0.0
                    self.chat_metrics["latency_ms_sum"] += float(dt_ms)
                    self.chat_metrics["latency_count"] += 1
                    hist = self.chat_metrics.get("latency_hist", {}) or {}
                    placed = False
                    for b in (50, 100, 250, 500, 1000, 2000, 5000):
                        if float(dt_ms) <= b:
                            hist[b] = int(hist.get(b, 0)) + 1
                            placed = True
                            break
                    if not placed:
                        hist["+Inf"] = int(hist.get("+Inf", 0)) + 1
                    self.chat_metrics["latency_hist"] = hist
                    if success and isinstance(payload, dict):
                        out = payload.get("result") or payload
                        txt = str(out.get("response") if isinstance(out, dict) else out)
                        self.chat_metrics["chars_out_total"] += len(txt)
                        self.chat_metrics["tokens_out_total"] += _count_tokens(txt)
                except Exception:
                    pass

            from flask import Response  # type: ignore

            return Response(
                _generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )  # type: ignore[call-arg]

        # ---------------- Optional Agents API (opt-in) -----------------
        def _agents_enabled_and_token_ok(req):
            if os.environ.get("AETHERRA_AGENTS_API_ENABLED", "0") != "1":
                return False, (jsonify({"error": "disabled"}), 501)  # type: ignore[name-defined]
            require = os.environ.get("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "0") == "1"
            if not require:
                return True, None
            token = (
                os.environ.get("AETHERRA_AGENTS_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                or ""
            ).strip()
            if not token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            got = req.headers.get("X-Aetherra-Token", "").strip()
            if got != token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            return True, None

        @app.route("/api/agents", methods=["GET"])
        def api_agents_list():
            """Return agent orchestrator summary (counts and basic status)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    # Best-effort: use orchestrator status directly if present
                    orch = getattr(eng, "agent_orchestrator", None)
                    if orch and hasattr(orch, "get_system_status"):
                        return True, {"orchestrator": orch.get_system_status()}
                    # Fallback to full engine status
                    if hasattr(eng, "get_system_status"):
                        # Engine method is async per engine implementation
                        import asyncio as _a

                        async def _g():
                            return await eng.get_system_status()  # type: ignore[attr-defined]

                        return True, {"engine": _a.run(_g())}
                    return False, "unavailable"
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "data": payload}), code  # type: ignore[name-defined]

        @app.route("/api/agents/metrics", methods=["GET"])
        def api_agents_metrics():
            """Expose orchestrator metrics only (lightweight)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    orch = getattr(eng, "agent_orchestrator", None)
                    if orch and hasattr(orch, "get_system_status"):
                        return True, orch.get_system_status()
                    return False, "unavailable"
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "metrics": payload}), code  # type: ignore[name-defined]

        @app.route("/api/agents/evaluate", methods=["POST"])
        def api_agents_evaluate():
            """Trigger a lightweight agent evaluation harness via the engine."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            plan = request.get_json(silent=True) or {}  # type: ignore[name-defined]

            async def _call(eng):
                try:
                    if not hasattr(eng, "run_agent_evaluation"):
                        return False, "unavailable"
                    report = await eng.run_agent_evaluation(plan)
                    return True, report
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "report": payload}), code  # type: ignore[name-defined]

        @app.route("/api/agents/evaluation", methods=["GET"])
        def api_agents_evaluation_get():
            """Fetch the last agent evaluation report from the engine (if available)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    if not hasattr(eng, "get_last_agent_evaluation"):
                        return True, None
                    return True, eng.get_last_agent_evaluation()
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "report": payload}), code  # type: ignore[name-defined]

        @app.route("/api/tasks", methods=["POST"])
        def api_task_submit():
            """Submit a task to the agent orchestrator via the engine."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            name = str(body.get("name") or body.get("task") or "").strip()
            data = body.get("data") if isinstance(body.get("data"), dict) else {}
            priority = str(body.get("priority") or "normal").strip()
            if not name:
                return jsonify({"error": "invalid"}), 400  # type: ignore[name-defined]

            async def _call(eng):
                try:
                    if not hasattr(eng, "execute_task"):
                        return False, "unavailable"
                    tid = await eng.execute_task(name, data, priority)
                    return True, {"task_id": tid}
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify(
                {
                    "ok": bool(success),
                    **({} if not isinstance(payload, dict) else payload),
                }
            ), code  # type: ignore[name-defined]

        @app.route("/api/tasks/<task_id>", methods=["GET"])
        def api_task_status(task_id):
            """Return task status by id from the orchestrator."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    if not hasattr(eng, "get_task_status"):
                        return False, "unavailable"
                    st = eng.get_task_status(task_id)
                    if st is None:
                        return False, "not_found"
                    return True, st
                except Exception as e:
                    return False, str(e)

            success, payload = _with_engine_call(_call)
            if success:
                return jsonify({"ok": True, "status": payload})  # type: ignore[name-defined]
            code = 404 if payload == "not_found" else 500
            return jsonify({"ok": False, "error": payload}), code  # type: ignore[name-defined]

        @app.route("/api/tasks/<task_id>/stream", methods=["POST"])
        def api_task_stream(task_id):
            """SSE stream for task progress updates (opt-in and token-guarded)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            if os.environ.get("AETHERRA_AGENTS_API_STREAM", "0") != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]

            poll_ms = int(os.environ.get("AETHERRA_AGENTS_STREAM_POLL_MS", "200"))

            def _sse(event: str, data: Dict[str, Any]):
                import json as _json

                return f"event: {event}\ndata: {_json.dumps(data)}\n\n"

            def _generate():
                # Initial status and token confirmation
                yield _sse("status", {"phase": "start", "task_id": task_id})
                require = (
                    os.environ.get("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "0") == "1"
                )
                yield _sse("token", {"required": require, "ok": True})

                # Poll for status a few times or until complete
                import time as _t

                def _get_once():
                    def _call(eng):
                        try:
                            if not hasattr(eng, "get_task_status"):
                                return True, None
                            return True, eng.get_task_status(task_id)
                        except Exception:
                            return True, None

                    res = _with_engine_call(_call)
                    if not isinstance(res, tuple) or len(res) != 2:
                        ok2, payload2 = False, None
                    else:
                        ok2, payload2 = res
                    return payload2 if ok2 else None

                last = None
                for _ in range(20):  # ~4 seconds at 200ms
                    st = _get_once() or {}
                    if not isinstance(st, dict):
                        st = {}
                    if st != last and st:
                        yield _sse("update", {"task_id": task_id, "status": st})
                        last = st
                    # Terminal?
                    try:
                        prog = float(st.get("progress", 0))
                        if prog >= 100 or str(st.get("state", "")).lower() in (
                            "done",
                            "complete",
                            "failed",
                        ):
                            break
                    except Exception:
                        pass
                    _t.sleep(max(0.05, poll_ms / 1000.0))

                # Final status
                st = _get_once() or last or {}
                if not isinstance(st, dict):
                    st = {}
                yield _sse("final", {"ok": True, "task_id": task_id, "status": st})

            from flask import Response  # type: ignore

            return Response(
                _generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )  # type: ignore[call-arg]

        @app.route("/api/telemetry", methods=["POST"])
        def telemetry_ingest():
            """Receive opt-in telemetry events locally (no forwarding by default)."""
            self.stats["requests_served"] += 1
            try:
                evt = request.get_json(silent=True) or {}  # type: ignore[name-defined]
                # Very basic validation
                if not isinstance(evt.get("event"), str):
                    return jsonify({"error": "invalid"}), 400  # type: ignore[name-defined]
                # Optionally update stats counters
                self.stats["telemetry_received"] = (
                    int(self.stats.get("telemetry_received", 0)) + 1
                )
                self.stats["last_telemetry_at"] = datetime.now().isoformat()
                return jsonify({"status": "ok"})  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"telemetry error: {e}")
                return jsonify({"error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/lyrixa/chat", methods=["POST"])  # lightweight chat bridge
        def lyrixa_chat():
            """Forward chat requests to the registered Lyrixa chat service (best-effort)."""
            self.stats["requests_served"] += 1
            try:
                payload = request.get_json(silent=True) or {}  # type: ignore[name-defined]
                msg = payload.get("message") or payload.get("content") or ""
                allow_edits = bool(payload.get("allow_edits", False))
                edit_root = payload.get("edit_root")
                # Lazy import to avoid tight coupling
                try:
                    from aetherra_service_registry import get_service_registry

                    async def _call():
                        reg = await get_service_registry()
                        svc = reg.get_service("lyrixa_chat")
                        if not svc:
                            return None
                        return await svc.handle_message(
                            "lyrixa.chat",
                            {
                                "message": msg,
                                "allow_edits": allow_edits,
                                "edit_root": edit_root,
                            },
                        )

                    result = _run_coro_blocking(_call())
                except Exception:
                    result = None

                if not result:
                    # Deterministic fallback mirroring LyrixaChatService
                    text = (
                        "Lyrixa chat service is not online right now. "
                        "I can still answer identity and Aetherra questions."
                    )
                    return jsonify(
                        {"text": text, "suggestions": [], "applied_changes": []}
                    )  # type: ignore[name-defined]

                return jsonify(result)  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"lyrixa chat error: {e}")
                return jsonify({"error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/memory/graph", methods=["GET"])
        def memory_graph():
            """Return a summarized memory graph (nodes/edges counts and samples)."""
            self.stats["requests_served"] += 1
            if not self.memory_summarizer:
                return jsonify({"enabled": False, "reason": "not available"}), 501  # type: ignore[name-defined]
            try:
                data = self.memory_summarizer(max_nodes=100)
                return jsonify({"enabled": True, **data})  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"memory graph error: {e}")
                return jsonify({"enabled": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/memory/status", methods=["GET"])
        def memory_status():
            """Return quantum memory status (coherence/branch/entanglement) if available.

            Best-effort via service registry; falls back to ephemeral engine instance.
            """
            self.stats["requests_served"] += 1
            try:
                st = _get_memory_quantum_status_sync()
                if not isinstance(st, dict):
                    st = {"enabled": False}
                return jsonify(st)  # type: ignore[name-defined]
            except Exception:
                return jsonify({"enabled": False}), 200  # type: ignore[name-defined]

        @app.route("/api/memory/audit", methods=["GET"])
        def memory_audit():
            """Return memory branch DAG audit info (nodes/edges) if available.

            Best-effort via service registry; falls back to ephemeral engine instance.
            """
            self.stats["requests_served"] += 1
            try:
                data = _get_memory_audit_sync()
                if not isinstance(data, dict):
                    data = {"enabled": False}
                return jsonify(data)  # type: ignore[name-defined]
            except Exception:
                return jsonify({"enabled": False}), 200  # type: ignore[name-defined]

        @app.route("/services", methods=["GET"])
        def get_services():
            """Get available services for Aetherra OS compatibility"""
            self.stats["requests_served"] += 1
            return jsonify(
                {  # type: ignore[name-defined]
                    "services": ["hub_server", "plugin_registry", "plugin_discovery"],
                    "status": "online",
                    "running": True,
                    "total_services": 3,
                    "hub_capabilities": [
                        "plugin_registration",
                        "plugin_discovery",
                        "marketplace",
                    ],
                }
            )

        @app.route("/", methods=["GET"])
        def index():
            """Hub web interface"""
            return """
            <html>
            <head><title>Aetherra Hub - Plugin Marketplace</title></head>
            <body style="font-family: monospace; background: #0a0a0a; color: #00ffaa; padding: 20px;">
                <h1>🏪 Aetherra Hub - Plugin Marketplace</h1>
                <p>Status: <span style="color: #66ffcc;">ONLINE</span></p>
                <p>Registered Plugins: <span id="plugin-count">Loading...</span></p>
                <p>Uptime: <span id="uptime">Loading...</span></p>
                <p>Lyrixa Chat Service: <span id="lyrixa-status">Checking...</span></p>
                <hr>
                <h2>API Endpoints:</h2>
                <ul>
                    <li><a href="/health" style="color: #00ffaa;">GET /health</a> - Health check</li>
                    <li><a href="/api/plugins" style="color: #00ffaa;">GET /api/plugins</a> - List plugins</li>
                    <li><a href="/api/stats" style="color: #00ffaa;">GET /api/stats</a> - Hub statistics</li>
                    <li>POST /api/lyrixa/chat - Lyrixa chat bridge</li>
                    <li>POST /api/plugins/register - Register plugin</li>
                </ul>
                <script>
                    fetch('/api/stats').then(r=>r.json()).then(d=>{
                        document.getElementById('plugin-count').textContent = Object.keys(d).length || 0;
                        document.getElementById('uptime').textContent = Math.round((Date.now() - new Date(d.startup_time)) / 1000) + 's';
                        try {
                            const ly = d.lyrixa_chat || { registered: false };
                            const el = document.getElementById('lyrixa-status');
                            if (ly.registered) {
                                const ok = ly.status === 'healthy' || ly.status === 'HEALTHY';
                                el.textContent = ok ? 'ONLINE' : (ly.status || 'REGISTERED');
                                el.style.color = ok ? '#66ffcc' : '#ffd166';
                            } else {
                                el.textContent = 'OFFLINE';
                                el.style.color = '#ff6b6b';
                            }
                        } catch (e) { /* no-op */ }
                    });
                </script>
            </body>
            </html>
            """

    def start_server(self):
        """Start the Hub server"""
        if not FLASK_AVAILABLE:
            logger.warning("⚠️ Flask not available - starting mock hub server")
            self.server_running = True
            return True

        try:
            logger.info(f"[HUB] Starting Aetherra Hub server on port {self.port}")

            # Start Flask server in a separate thread
            import threading

            def run_flask():
                if self.app is None:
                    return
                self.app.run(
                    host="localhost",
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True,
                )

            self.server_thread = threading.Thread(target=run_flask, daemon=True)
            self.server_thread.start()

            # Wait a moment for server to start
            time.sleep(1)

            self.server_running = True
            logger.info(
                f"[OK] Aetherra Hub server online at http://localhost:{self.port}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start Hub server: {e}")
            self.server_running = False
            return False

    def register_plugin(self, plugin_data: Dict) -> bool:
        """Register a plugin directly (for internal use)"""
        try:
            plugin_id = plugin_data.get("name", f"plugin_{len(self.plugins)}")
            plugin_data["registered_at"] = datetime.now().isoformat()
            plugin_data["status"] = "registered"
            plugin_data["source"] = "internal"

            self.plugins[plugin_id] = plugin_data
            self.stats["active_registrations"] += 1

            logger.info(f"[OK] Plugin registered internally: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Internal plugin registration failed: {e}")
            return False

    def is_running(self) -> bool:
        """Check if the Hub server is running"""
        return self.server_running

    def get_plugin_count(self) -> int:
        """Get the number of registered plugins"""
        return len(self.plugins)

    def get_stats(self) -> Dict:
        """Get Hub statistics"""
        return {
            **self.stats,
            "total_plugins": len(self.plugins),
            "uptime_seconds": (
                datetime.now() - self.stats["startup_time"]
            ).total_seconds(),
        }

    def stop_server(self):
        """Stop the Hub server"""
        self.server_running = False
        logger.info("🛑 Aetherra Hub server stopped")

    # OS integration hook: allow launcher to call a generic shutdown()
    def shutdown(self):
        """Gracefully stop the Hub server (alias for stop_server)."""
        try:
            self.stop_server()
        except Exception:
            pass


# Global Hub instance
hub_server = None


def start_hub_server(port: int = 3001) -> AetherraHubServer:
    """Start the global Hub server"""
    global hub_server
    if hub_server is None:
        hub_server = AetherraHubServer(port)
        hub_server.start_server()
    return hub_server


def get_hub_server() -> Optional[AetherraHubServer]:
    """Get the global Hub server instance"""
    return hub_server


if __name__ == "__main__":
    # Test the Hub server
    print("🧪 Testing Aetherra Hub Server")
    server = AetherraHubServer(3001)

    if server.start_server():
        print("[OK] Hub server started successfully")

        # Register a test plugin
        test_plugin = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for Hub server",
            "type": "utility",
        }

        server.register_plugin(test_plugin)
        print(f"📊 Hub stats: {server.get_stats()}")

        # Keep running for testing
        print("🔄 Hub server running... (Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Stopping Hub server...")
            server.stop_server()
    else:
        print("❌ Failed to start Hub server")
