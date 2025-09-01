import asyncio
import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class DummyOrchestrator:
    def __init__(self):
        self._status = {
            "total_agents": 3,
            "pending_tasks": 2,
            "active_tasks": 1,
            "pending_by_priority": {"high": 1, "normal": 1},
            "task_statuses": {"pending": 2, "running": 1},
            "counters": {"timeouts_total": 0, "policy_denied_total": 0},
            "avg_task_latency_ms": 25.0,
            "coherence_policy": {
                "gate_min": 0.65,
                "hard_min": 0.4,
                "ema": 0.72,
                "window_size": 5,
                "last_drift_alert": None,
            },
        }

    def get_system_status(self):
        return self._status


class MockEngine:
    def __init__(self):
        self.agent_orchestrator = DummyOrchestrator()


async def _register_mock_engine(engine: MockEngine):
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("aetherra_engine", engine)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_coherence_metrics_exposed():
    # Register engine with orchestrator
    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text

    assert "aetherra_orchestrator_coherence_gate_min" in body
    assert "aetherra_orchestrator_coherence_hard_min" in body
    assert "aetherra_orchestrator_coherence_ema" in body
    assert "aetherra_orchestrator_coherence_window_size" in body
    assert "aetherra_orchestrator_last_drift_alert_present" in body

    server.stop_server()
