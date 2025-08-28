import asyncio
import socket

import pytest

requests = pytest.importorskip("requests")


hub_mod = __import__("aetherra_hub_server")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


class MockKernel:
    def __init__(self):
        self.paused = False
        self.queue_limits = {}
        self.drains = []

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    async def drain_queue(self, name: str, mode: str = "dlq"):
        self.drains.append((name, mode))

    def set_queue_limits(self, limits: dict):
        self.queue_limits.update(dict(limits))

    def get_status(self):
        return {
            "running": True,
            "paused": self.paused,
            "queue_limits": dict(self.queue_limits),
        }


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _register_mock_kernel(kernel: MockKernel):
    from aetherra_service_registry import get_service_registry

    reg = await get_service_registry()
    await reg.register_service("kernel_loop", kernel)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_control_requires_enabled_and_token(monkeypatch):
    # Ensure clean env
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_ENABLED", raising=False)
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"

    # When disabled entirely -> 501
    r = requests.post(f"{base}/api/kernel/control/pause", timeout=3)
    assert r.status_code == 501

    # Enable but no token set -> 403
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_ENABLED", "1")
    r = requests.post(f"{base}/api/kernel/control/pause", timeout=3)
    assert r.status_code == 403

    # Token set but header missing -> 403
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "secret123")
    r = requests.post(f"{base}/api/kernel/control/pause", timeout=3)
    assert r.status_code == 403

    # With correct header -> proceed (may still 500 if kernel not registered)
    r = requests.post(
        f"{base}/api/kernel/control/pause",
        headers={"X-Aetherra-Token": "secret123"},
        timeout=3,
    )
    # Kernel not registered yet, helper returns error -> 500 expected
    assert r.status_code in (200, 500)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_pause_resume_drain_and_queue_limits(monkeypatch):
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "tok")

    kernel = MockKernel()
    asyncio.run(_register_mock_kernel(kernel))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    headers = {"X-Aetherra-Token": "tok"}

    # Pause -> ok and kernel.paused becomes True
    r = requests.post(f"{base}/api/kernel/control/pause", headers=headers, timeout=3)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert kernel.paused is True

    # Resume -> ok and kernel.paused becomes False
    r = requests.post(f"{base}/api/kernel/control/resume", headers=headers, timeout=3)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    assert kernel.paused is False

    # Drain a valid queue
    r = requests.post(
        f"{base}/api/kernel/control/drain",
        json={"queue": "normal_priority", "mode": "drop"},
        headers=headers,
        timeout=5,
    )
    assert r.status_code == 200
    assert ("normal_priority", "drop") in kernel.drains

    # Update queue limits
    r = requests.post(
        f"{base}/api/kernel/control/queue_limits",
        json={"normal_priority": 7},
        headers=headers,
        timeout=3,
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    # Ensure kernel state reflects update
    assert kernel.queue_limits.get("normal_priority") == 7
    # Endpoint echoes updated limits
    assert j.get("status", {}).get("queue_limits", {}).get("normal_priority") == 7


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_kernel_status_and_metrics_shape(monkeypatch):
    # Register a mock kernel so status/metrics have content
    kernel = MockKernel()
    asyncio.run(_register_mock_kernel(kernel))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"

    # /api/kernel/status returns JSON with running key
    r = requests.get(f"{base}/api/kernel/status", timeout=3)
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)
    assert "running" in js

    # /api/kernel/metrics returns hub_ts and kernel object
    r = requests.get(f"{base}/api/kernel/metrics", timeout=3)
    assert r.status_code == 200
    jm = r.json()
    assert isinstance(jm, dict)
    assert "hub_ts" in jm
    assert isinstance(jm.get("kernel"), dict)

    # /metrics returns Prometheus text; ensure expected registry metric label appears
    r = requests.get(f"{base}/metrics", timeout=3)
    assert r.status_code == 200
    body = r.text
    assert isinstance(body, str) and len(body) > 0
    assert "aetherra_registry_services_total" in body


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_drain_invalid_queue_returns_400(monkeypatch):
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "t")

    kernel = MockKernel()
    asyncio.run(_register_mock_kernel(kernel))

    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()

    base = f"http://localhost:{port}"
    headers = {"X-Aetherra-Token": "t"}

    r = requests.post(
        f"{base}/api/kernel/control/drain",
        json={"queue": "not_a_queue", "mode": "dlq"},
        headers=headers,
        timeout=3,
    )
    assert r.status_code == 400
