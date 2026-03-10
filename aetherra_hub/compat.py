"""Compatibility layer emulating legacy aetherra_hub_server interface.

Provides AetherraHubServer and start_hub_server backed by the modular
blueprint-based implementation. This allows incremental migration of
tools and tests away from the monolithic file while keeping the old
API surface functional.
"""

from __future__ import annotations

# Standard library imports
import threading
import time

# Third party imports
from werkzeug.serving import make_server

# Local imports
from .app import create_app
from .services import plugins as _plugins
from .services import registry_client as _reg_client
from .services.metrics_accum import chat_metrics

# Expose a FLASK_AVAILABLE flag for legacy tests that gated execution
try:  # pragma: no cover - simple availability flag
    # Third party imports
    import flask  # type: ignore  # noqa: F401

    FLASK_AVAILABLE = True
except Exception:  # pragma: no cover
    FLASK_AVAILABLE = False  # type: ignore


class AetherraHubServer:  # minimal subset used in tests/tools
    def __init__(self, port: int = 3001):
        self.port = port
        self._srv = None
        self._thread: threading.Thread | None = None
        self.server_running = False
        # Simple plugin store reference
        self._plugin_store = getattr(_plugins, "store", None)
        # Expose chat_metrics in dict form (tests sometimes inspect/mutate)
        self.chat_metrics = {
            "requests_total": 0,
            "chunks_total": 0,
            "chars_in_total": 0,
            "chars_out_total": 0,
            "tokens_in_total": 0,
            "tokens_out_total": 0,
            "fallback_mock_total": 0,
            "fallback_path_counts": {"mock": 0, "engine": 0, "cached": 0},
        }

    # Legacy API
    def start_server(self) -> bool:
        if self.server_running:
            return True
        app = create_app()
        self._srv = make_server("0.0.0.0", self.port, app)
        self._thread = threading.Thread(target=self._srv.serve_forever, daemon=True)
        self._thread.start()
        self.server_running = True
        # Seed minimal kernel / orchestrator status so initial metrics scrape includes histograms
        try:  # best-effort; avoids test flakiness when registry not yet populated
            if not _reg_client.get_kernel_status():
                _reg_client._last_kernel_status = {  # type: ignore[attr-defined]
                    "metrics": {"last_cycle_time": 0.001},
                    "queue_sizes": {
                        "high_priority": 0,
                        "normal_priority": 0,
                        "background": 0,
                    },
                }
            if not _reg_client.get_orchestrator_status():
                _reg_client._last_orchestrator_status = {  # type: ignore[attr-defined]
                    "avg_task_latency_ms": 0.5,
                    "total_agents": 0,
                    "pending_tasks": 0,
                }
        except Exception:
            pass
        return True

    def stop_server(self):  # pragma: no cover - rarely used
        if not self.server_running:
            return
        try:
            if self._srv:
                self._srv.shutdown()
        finally:
            self.server_running = False

    def is_running(self) -> bool:
        return self.server_running

    # Legacy helper used in smoke tests
    def register_plugin(self, manifest: dict):  # pragma: no cover - simple pass-through
        store = self._plugin_store
        if not store:
            return False
        try:
            store.register(manifest)
            return True
        except Exception:
            return False


_global_server: AetherraHubServer | None = None


def start_hub_server(port: int = 3001) -> AetherraHubServer:
    global _global_server
    if _global_server and _global_server.port != port:
        try:
            _global_server.stop_server()
        except Exception:  # pragma: no cover
            pass
        _global_server = None
    if _global_server is None:
        _global_server = AetherraHubServer(port)
        _global_server.start_server()
        # Best-effort readiness wait (avoids rare race where first test request 404s)
        try:  # pragma: no cover - timing dependent
            # Third party imports
            import requests  # type: ignore

            base = f"http://localhost:{port}"
            deadline = time.time() + 2.5  # short overall timeout
            while time.time() < deadline:
                try:
                    r = requests.get(base + "/api/ping", timeout=0.35)
                    if r.status_code == 200:
                        break
                except Exception:
                    pass
                time.sleep(0.05)
        except Exception:
            pass
        # Reset counters for deterministic tests
        cm = _global_server.chat_metrics
        for k in list(cm.keys()):
            if isinstance(cm[k], int):
                cm[k] = 0
        cm["fallback_path_counts"] = {"mock": 0, "engine": 0, "cached": 0}
        try:  # align mock fallback counter with real metric object
            chat_metrics.fallback_mock_total = 0  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover
            pass
    return _global_server


__all__ = ["AetherraHubServer", "start_hub_server", "FLASK_AVAILABLE"]
