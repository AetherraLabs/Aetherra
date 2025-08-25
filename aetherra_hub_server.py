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
from typing import Dict, Optional

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
        app = self.app

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
                            jsonify({"error": "signature verification unavailable"}),
                            400,
                        )  # type: ignore[name-defined]
                    if getattr(self, "verify_signature", None) is None:
                        return jsonify(
                            {"error": "signature verification unavailable"}
                        ), 400  # type: ignore[name-defined]
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
