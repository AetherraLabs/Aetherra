#!/usr/bin/env python3
"""
🏪 Aetherra Hub Server
======================

Built-in Python-based plugin marketplace server for Aetherra OS.
Provides plugin registration, discovery, and basic marketplace functionality.
"""

import logging
import os
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

    def _setup_routes(self):
        """Setup Flask routes for the Hub API"""
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

        # Internal helpers to access registry/kernel from sync Flask routes
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
                import asyncio

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

                out["lyrixa_chat"] = asyncio.run(_get())
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

        @app.route("/metrics", methods=["GET"])
        def prometheus_metrics():
            """Prometheus-style plaintext metrics for quick scraping."""
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync() or {}
            rs = _get_registry_status_sync() or {}
            os = _get_orchestrator_status_sync() or {}

            lines = []

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
                    import asyncio

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

                    result = asyncio.run(_call())
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
