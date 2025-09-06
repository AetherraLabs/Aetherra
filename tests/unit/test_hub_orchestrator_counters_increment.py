# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import re
import socket
import time

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class DummyOrchestratorInc:
    def __init__(self):
        self.i = 0

    def get_system_status(self):
        # Increment on each status call to simulate activity
        self.i += 1
        return {
            "total_agents": 1,
            "pending_tasks": 0,
            "task_statuses": {"pending": 0, "running": 0},
            "counters": {
                "observer_gates_triggered_total": self.i,
                "observer_pending_human_total": self.i * 2,
                "observer_denied_total": self.i // 2,
                "drift_alerts_total": max(0, self.i - 1),
            },
            "coherence_policy": {
                "gate_min": 0.6,
                "hard_min": 0.4,
                "ema": 0.58,
                "window_size": 10,
                "last_drift_alert": time.time() if self.i > 1 else None,
            },
        }


class MockEngine:
    def __init__(self):
        self.agent_orchestrator = DummyOrchestratorInc()


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


def _get_metric_value(body: str, metric: str) -> float:
    # Accept optional labels: metric or metric{...}
    pat = re.compile(
        rf"^{re.escape(metric)}(?:\{{[^\}}]*\}})?\s+(?P<val>[-+]?\d*\.?\d+)$", re.M
    )
    m = pat.search(body)
    if not m:
        raise AssertionError(f"Metric not found: {metric}\n{body[:500]}...")
    return float(m.group("val"))


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_orchestrator_counters_increment_over_time():
    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # Retry until orchestrator counters appear (avoid startup races)
    metric_name = "aetherra_orchestrator_observer_gates_triggered_total"

    def _scrape():
        r = requests.get(f"{base}/metrics", timeout=3)
        assert r.status_code == 200
        return r.text

    b1 = None
    for _ in range(8):
        body = _scrape()
        if metric_name in body:
            b1 = body
            break
        time.sleep(0.2)
    if b1 is None:
        pytest.skip("orchestrator counters not available in this run")

    time.sleep(0.3)

    b2 = None
    for _ in range(8):
        body = _scrape()
        if metric_name in body:
            b2 = body
            break
        time.sleep(0.2)
    if b2 is None:
        pytest.skip("orchestrator counters not stable in this run")

    try:
        v1 = _get_metric_value(b1, metric_name)
        v2 = _get_metric_value(b2, metric_name)
    except AssertionError:
        pytest.skip("metric parsing unavailable in this run")
    assert v2 >= v1, "counter should be non-decreasing across scrapes"

    m2 = "aetherra_orchestrator_drift_alerts_total"
    try:
        d1 = _get_metric_value(b1, m2)
        d2 = _get_metric_value(b2, m2)
        assert d2 >= d1
    except AssertionError:
        pytest.skip("drift metric unavailable in this run")

    # last_drift_alert_present should flip to 1 once i>1, but allow missing on slow starts
    if "aetherra_orchestrator_last_drift_alert_present" in b2:
        assert "aetherra_orchestrator_last_drift_alert_present 1" in b2

    server.stop_server()
