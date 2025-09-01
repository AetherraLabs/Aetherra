import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockOrchestrator:
    def get_system_status(self):
        return {"total_agents": 0, "pending_tasks": 0}


class MockEngine:
    def __init__(self):
        self.agent_orchestrator = MockOrchestrator()

    def get_session_metrics(self):
        return {
            "ab_recall_total": 3,
            "ab_recall_classical_total": 2,
            "ab_recall_quantum_total": 1,
            "ab_recall_latency_ms_sum_classical": 12.3,
            "ab_recall_latency_ms_count_classical": 2,
            "ab_recall_latency_ms_sum_quantum": 7.7,
            "ab_recall_latency_ms_count_quantum": 1,
        }

    async def get_system_status(self):
        # Provide full payload path
        return {
            "session_metrics": self.get_session_metrics(),
            "ab": {"mode": "abp", "pmem_ready": False},
        }


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
def test_prometheus_ab_recall_series_exposed():
    import asyncio

    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text

    # Totals
    assert "aetherra_engine_ab_recall_total" in body
    assert "aetherra_engine_ab_recall_classical_total" in body
    assert "aetherra_engine_ab_recall_quantum_total" in body
    # Latency aggregates with bucket labels
    assert 'aetherra_engine_ab_recall_latency_ms_sum{bucket="classical"}' in body
    assert 'aetherra_engine_ab_recall_latency_ms_count{bucket="classical"}' in body
    assert 'aetherra_engine_ab_recall_latency_ms_sum{bucket="quantum"}' in body
    assert 'aetherra_engine_ab_recall_latency_ms_count{bucket="quantum"}' in body
    # Mode/pmem gauges
    assert 'aetherra_engine_ab_mode{mode="abp"} 1' in body
    assert "aetherra_engine_ab_pmem_ready" in body
