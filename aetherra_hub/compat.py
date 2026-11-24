"""Compatibility layer emulating legacy aetherra_hub_server interface.

Provides AetherraHubServer and start_hub_server backed by the modular
blueprint-based implementation. This allows incremental migration of
tools and tests away from the monolithic file while keeping the old
API surface functional.
"""

from __future__ import annotations

# Standard library imports
import contextlib
import logging
import threading
import time

# Local imports
from .app import create_app
from .errors import HubRequestDrainTimeoutError
from .request_server import make_server
from .services import plugins as _plugins
from .services import registry_client as _reg_client
from .services.metrics_accum import chat_metrics
from .services.request_ownership import RequestOwnership

logger = logging.getLogger(__name__)
_LEGACY_BIND_HOST = "0.0.0.0"  # noqa: S104 - historical default for direct callers
REQUEST_DRAIN_TIMEOUT_SECONDS = 5.0

# Expose a FLASK_AVAILABLE flag for legacy tests that gated execution
try:  # pragma: no cover - simple availability flag
    # Third party imports
    import flask  # type: ignore  # noqa: F401

    FLASK_AVAILABLE = True
except Exception:  # pragma: no cover
    FLASK_AVAILABLE = False  # type: ignore


class AetherraHubServer:  # minimal subset used in tests/tools
    def __init__(self, port: int = 3001, *, host: str = _LEGACY_BIND_HOST):
        self.port = port
        self.host = host
        self._srv = None
        self._thread: threading.Thread | None = None
        self._ownership: RequestOwnership | None = None
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
        if self._srv is not None:
            # A previous drain/close failure still owns its resources.
            self.stop_server()
        app = create_app()
        self._ownership = RequestOwnership(app)
        self._srv = make_server(self.host, self.port, self._ownership)
        try:
            self._thread = threading.Thread(target=self._srv.serve_forever, daemon=True)
            self._thread.start()
        except BaseException:
            self.stop_server()
            raise
        self.server_running = True
        # Seed minimal kernel / orchestrator status so initial metrics scrape includes histograms
        # Best-effort; preserves legacy metrics seeding when registry is not populated.
        with contextlib.suppress(Exception):
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
        return True

    def stop_server(self):  # pragma: no cover - rarely used
        if self._thread is threading.current_thread():
            raise RuntimeError("Hub cannot stop from its serving thread")
        if self._ownership is not None:
            self._ownership.begin_drain()
        if self._srv is not None and self.server_running:
            self._srv.shutdown()
        if self._thread is not None and self._thread.ident is not None:
            self._thread.join(timeout=3)
            if self._thread.is_alive():
                raise RuntimeError("Hub shutdown thread timeout")
        self.server_running = False
        deadline = time.monotonic() + REQUEST_DRAIN_TIMEOUT_SECONDS
        for owner in (self._ownership, self._srv):
            wait_for_idle = getattr(owner, "wait_for_idle", None)
            if callable(wait_for_idle) and not wait_for_idle(
                max(0, deadline - time.monotonic())
            ):
                # Preserve ownership for a later retry. In particular, the launcher
                # must not close Memory while a detached stream worker still runs.
                raise HubRequestDrainTimeoutError(
                    "Hub request drain timeout; resources retained"
                )
        if self._srv is not None:
            self._srv.server_close()
        self.server_running = False
        self._thread = None
        self._srv = None
        self._ownership = None

    def is_running(self) -> bool:
        return bool(
            self.server_running and self._thread is not None and self._thread.is_alive()
        )

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


_server_factory_lock = threading.RLock()


def start_hub_server(
    port: int = 3001,
    *,
    host: str | None = None,
) -> AetherraHubServer:
    with _server_factory_lock:
        return _start_hub_server(port, host=host)


def _start_hub_server(port: int, *, host: str | None) -> AetherraHubServer:
    global _global_server
    if host is not None and (not isinstance(host, str) or not host.strip()):
        raise ValueError("Hub host must be a nonempty string")
    bind_host = (
        host
        if host is not None
        else (
            _global_server.host
            if _global_server is not None and _global_server.port == port
            else _LEGACY_BIND_HOST
        )
    )
    if _global_server is not None:
        if (
            _global_server.port == port
            and _global_server.host == bind_host
            and _global_server.is_running()
        ):
            return _global_server
        try:
            _global_server.stop_server()
        except Exception:
            logger.warning("Previous Hub shutdown failed")
            raise
        _global_server = None
    if _global_server is None:
        candidate = AetherraHubServer(port, host=bind_host)
        try:
            if not candidate.start_server() or not candidate.is_running():
                raise RuntimeError("Hub startup failed")
        except BaseException:
            candidate.stop_server()
            raise
        _global_server = candidate
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
                    logger.debug("Hub readiness probe failed")
                time.sleep(0.05)
        except Exception:
            logger.warning("Hub readiness check unavailable")
        # Reset counters for deterministic tests
        cm = _global_server.chat_metrics
        for k in list(cm.keys()):
            if isinstance(cm[k], int):
                cm[k] = 0
        cm["fallback_path_counts"] = {"mock": 0, "engine": 0, "cached": 0}
        try:  # align mock fallback counter with real metric object
            chat_metrics.fallback_mock_total = 0  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover
            logger.warning("Hub fallback metric reset failed")
    return _global_server


__all__ = ["AetherraHubServer", "start_hub_server", "FLASK_AVAILABLE"]
