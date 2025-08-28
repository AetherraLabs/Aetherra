import asyncio
import socket

import pytest

requests = pytest.importorskip("requests")

hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockOrchestrator:
    def __init__(self):
        self._tasks = {}

    async def submit_task(self, task):
        tid = f"t_{len(self._tasks) + 1}"
        self._tasks[tid] = {"task_id": tid, "state": "queued", "progress": 0}
        return tid

    def get_system_status(self):
        return {"total_agents": 1, "pending_tasks": len(self._tasks)}

    def get_task_status(self, tid):
        st = self._tasks.get(tid)
        if not st:
            return None
        # Simulate progress on successive calls
        st["progress"] = min(100, st.get("progress", 0) + 60)
        st["state"] = "done" if st["progress"] >= 100 else "running"
        return dict(st)


class MockEngine:
    def __init__(self):
        self.agent_orchestrator = MockOrchestrator()
        self._last_eval = None

    async def execute_task(self, name: str, data: dict, priority: str = "normal"):
        return await self.agent_orchestrator.submit_task(
            {
                "name": name,
                "data": data,
                "priority": priority,
            }
        )

    def get_task_status(self, task_id: str):
        return self.agent_orchestrator.get_task_status(task_id)

    async def get_system_status(self):
        return {"agent_orchestrator": self.agent_orchestrator.get_system_status()}

    async def run_agent_evaluation(self, plan: dict | None = None):
        # Minimal deterministic report
        report = {
            "ts": "now",
            "cases": [
                {
                    "name": (plan or {}).get("cases", [{}])[0].get("name", "eval"),
                    "ok": True,
                    "duration_sec": 0.01,
                }
            ],
            "summary": {
                "total": 1,
                "success": 1,
                "failed": 0,
                "avg_duration_sec": 0.01,
                "errors": {},
                "wall_time_sec": 0.01,
            },
        }
        self._last_eval = report
        return report

    def get_last_agent_evaluation(self):
        return self._last_eval


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
def test_agents_api_disabled(monkeypatch):
    # Ensure disabled
    for k in (
        "AETHERRA_AGENTS_API_ENABLED",
        "AETHERRA_AGENTS_API_REQUIRE_TOKEN",
        "AETHERRA_AGENTS_API_TOKEN",
    ):
        monkeypatch.delenv(k, raising=False)

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    r = requests.get(f"{base}/api/agents", timeout=3)
    assert r.status_code == 501
    assert r.json().get("error") == "disabled"

    r = requests.get(f"{base}/api/agents/metrics", timeout=3)
    assert r.status_code == 501
    assert r.json().get("error") == "disabled"

    r = requests.post(f"{base}/api/tasks", json={"name": "x"}, timeout=3)
    assert r.status_code == 501
    assert r.json().get("error") == "disabled"


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_agents_api_token_and_happy_path(monkeypatch):
    monkeypatch.setenv("AETHERRA_AGENTS_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AGENTS_API_TOKEN", "sek")
    monkeypatch.setenv("AETHERRA_AGENTS_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AGENTS_STREAM_POLL_MS", "50")

    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # Missing token -> 403
    r = requests.get(f"{base}/api/agents", timeout=3)
    assert r.status_code == 403

    # With token -> 200
    r = requests.get(
        f"{base}/api/agents", headers={"X-Aetherra-Token": "sek"}, timeout=3
    )
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True

    # Metrics
    r = requests.get(
        f"{base}/api/agents/metrics", headers={"X-Aetherra-Token": "sek"}, timeout=3
    )
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True
    assert isinstance(js.get("metrics"), dict)

    # Submit task
    r = requests.post(
        f"{base}/api/tasks",
        json={"name": "demo", "data": {"x": 1}, "priority": "high"},
        headers={"X-Aetherra-Token": "sek"},
        timeout=3,
    )
    assert r.status_code == 200
    tid = r.json().get("task_id")
    assert isinstance(tid, str) and tid

    # Status
    r = requests.get(
        f"{base}/api/tasks/{tid}", headers={"X-Aetherra-Token": "sek"}, timeout=3
    )
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True
    assert isinstance(js.get("status"), dict)

    # SSE stream
    with requests.post(
        f"{base}/api/tasks/{tid}/stream",
        headers={"X-Aetherra-Token": "sek"},
        timeout=5,
        stream=True,
    ) as resp:
        assert resp.status_code == 200
        assert resp.headers.get("Content-Type", "").startswith("text/event-stream")
        text = "".join(
            [chunk.decode("utf-8") for chunk in resp.iter_content(chunk_size=None)]
        )
        assert "event: status" in text
        assert "event: token" in text
        assert "event: update" in text or "event: final" in text
        assert "event: final" in text


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_agents_evaluation_flow(monkeypatch):
    monkeypatch.setenv("AETHERRA_AGENTS_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AGENTS_API_TOKEN", "sek")

    asyncio.run(_register_mock_engine(MockEngine()))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # Trigger evaluation
    r = requests.post(
        f"{base}/api/agents/evaluate",
        json={"cases": [{"name": "eval.quick.status"}]},
        headers={"X-Aetherra-Token": "sek"},
        timeout=5,
    )
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True
    assert isinstance(js.get("report"), dict)

    # Fetch last report
    r = requests.get(
        f"{base}/api/agents/evaluation",
        headers={"X-Aetherra-Token": "sek"},
        timeout=3,
    )
    assert r.status_code == 200
    js = r.json()
    assert js.get("ok") is True
    rep = js.get("report")
    assert isinstance(rep, dict) and "summary" in rep
