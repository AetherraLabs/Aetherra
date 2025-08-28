import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockOrchestrator:
    def __init__(self):
        self._tasks = {"t1": {"status": "pending", "priority": "high"}}

    def get_system_status(self):
        return {
            "status": "running",
            "total_agents": 2,
            "pending_tasks": 1,
            "total_tasks": 1,
            "task_statuses": {"pending": 1},
            "pending_by_priority": {"high": 1, "normal": 0, "background": 0},
            "counters": {"timeouts_total": 0, "policy_denied_total": 0},
        }


class MockEngine:
    def __init__(self):
        self.agent_orchestrator = MockOrchestrator()


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
def test_prometheus_orchestrator_metrics_exposed():
    import asyncio

    # Register engine with orchestrator
    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text

    # Basic presence
    assert "aetherra_orchestrator_agents_total" in body
    assert "aetherra_orchestrator_tasks_pending_total" in body

    # Labelled metrics
    assert 'aetherra_orchestrator_tasks_pending{priority="high"}' in body
    assert 'aetherra_orchestrator_tasks_total{status="pending"}' in body

    # Generic counters
    assert "aetherra_orchestrator_timeouts_total" in body
    assert "aetherra_orchestrator_policy_denied_total" in body
