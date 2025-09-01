import asyncio
import socket
import time

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class DummyOrchestratorCounters:
    def __init__(self):
        self._status = {
            "total_agents": 1,
            "pending_tasks": 0,
            "task_statuses": {"pending": 0, "running": 0},
            "counters": {
                "observer_gates_triggered_total": 3,
                "observer_pending_human_total": 2,
                "observer_denied_total": 1,
                "drift_alerts_total": 4,
            },
            "coherence_policy": {
                "gate_min": 0.6,
                "hard_min": 0.4,
                "ema": 0.58,
                "window_size": 10,
                "last_drift_alert": time.time(),
            },
        }

    def get_system_status(self):
        return self._status


class MockEngine:
    def __init__(self):
        self.agent_orchestrator = DummyOrchestratorCounters()


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
def test_orchestrator_counter_metrics_exposed():
    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text

    # Counters should be exported with `aetherra_orchestrator_` prefix
    assert "aetherra_orchestrator_observer_gates_triggered_total" in body
    assert "aetherra_orchestrator_observer_pending_human_total" in body
    assert "aetherra_orchestrator_observer_denied_total" in body
    assert "aetherra_orchestrator_drift_alerts_total" in body

    # Coherence last drift alert present should be 1 for our status
    assert "aetherra_orchestrator_last_drift_alert_present 1" in body

    server.stop_server()
