"""Only the launcher's real serving Hub may refresh its registry liveness."""

# Standard library imports
import asyncio
import http.client
import json
import threading
from datetime import datetime, timedelta
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
import aetherra_service_registry as registry_module
from aetherra_service_registry import ServiceStatus


@pytest.fixture
def owned_hub(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name, value in {
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(tmp_path / "policy"),
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_REGISTRY_URL": "",
        "AETHERRA_SKIP_DOTENV": "1",
    }.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    registry = registry_module.AetherraServiceRegistry()
    registry._running = True
    monkeypatch.setattr(registry_module, "_service_registry", registry)

    # Aetherra imports
    from aetherra_hub import compat
    from aetherra_os_launcher import AetherraOSLauncher

    # Isolate optional metrics cache seeding; use the real Flask app and transport.
    monkeypatch.setattr(compat._reg_client, "get_kernel_status", lambda: {})
    monkeypatch.setattr(compat._reg_client, "get_orchestrator_status", lambda: {})
    monkeypatch.setattr(compat._reg_client, "_last_kernel_status", None, raising=False)
    monkeypatch.setattr(
        compat._reg_client, "_last_orchestrator_status", None, raising=False
    )
    server = compat.AetherraHubServer(port=0, host="127.0.0.1")
    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    launcher.running = True
    try:
        assert server.start_server()
        assert server.is_running()
        launcher.systems["aetherra_hub"] = server
        launcher._presence_owned_hub = server
        assert asyncio.run(
            registry.register_service(
                "aetherra_hub", server, metadata={"port": server._srv.server_port}
            )
        )
        yield launcher, registry, server
    finally:
        launcher.running = False
        server.stop_server()
        registry._running = False


def _health(server):
    connection = http.client.HTTPConnection(
        "127.0.0.1", server._srv.server_port, timeout=2
    )
    try:
        connection.request("GET", "/health")
        response = connection.getresponse()
        body = json.loads(response.read())
        assert response.status == 200
        assert body["status"] == "healthy"
    finally:
        connection.close()


@pytest.mark.parametrize("activity", ["idle", "request_teardown"])
@pytest.mark.asyncio
async def test_owned_hub_remains_registered_after_240_seconds(
    owned_hub, monkeypatch, activity
):
    # Aetherra imports
    import aetherra_os_launcher as launcher_module
    from Aetherra.homeostasis.stability_metrics import MetricSnapshot, StabilityMetrics

    launcher, registry, server = owned_hub
    initial_time = datetime.now()
    clock = initial_time
    ticks = 0
    _health(server)

    class Clock:
        @staticmethod
        def now():
            return clock

    async def monitor_tick(_delay):
        registry._running = False

    async def operation_tick(delay):
        nonlocal clock, ticks
        assert delay == 30
        clock += timedelta(seconds=delay)
        ticks += 1
        if activity == "request_teardown":
            _health(server)
        await registry._heartbeat_monitor()
        registry._running = True
        assert registry.get_service("aetherra_hub") is server
        assert registry.get_service_info("aetherra_hub").status is ServiceStatus.HEALTHY
        if ticks == 8:
            launcher.running = False

    async def no_status_file():
        pass

    monkeypatch.setattr(registry_module, "datetime", Clock)
    monkeypatch.setattr(
        registry_module,
        "asyncio",
        SimpleNamespace(**{**vars(asyncio), "sleep": monitor_tick}),
    )
    monkeypatch.setattr(
        launcher_module,
        "asyncio",
        SimpleNamespace(**{**vars(asyncio), "sleep": operation_tick}),
    )
    monkeypatch.setattr(launcher, "_write_os_status", no_status_file)
    monkeypatch.setattr(launcher, "_cleanup_os_status", no_status_file)
    await launcher._main_operation_loop()
    assert ticks == 8, "Hub registration must survive idle time and request teardown"
    assert (clock - initial_time).total_seconds() == 240
    _health(server)
    collector = StabilityMetrics()

    async def existing_registry():
        return registry

    monkeypatch.setattr(collector, "_get_service_registry", existing_registry)
    snapshot = MetricSnapshot(timestamp=clock.timestamp())
    await collector._collect_hub_metrics(snapshot)
    assert snapshot.hub_connection == 1.0
    assert "hub_connection" in snapshot.raw_data["measured_metrics"]


@pytest.mark.parametrize(
    "condition",
    [
        "stopped",
        "dead_thread",
        "replaced",
        "unowned",
        "missing_owner",
        "missing_registration",
        "degraded",
        "failed",
        "guardian_denied",
        "launcher_shutdown",
        "registry_stopped",
        "remote_proxy",
    ],
)
@pytest.mark.asyncio
async def test_hub_heartbeat_requires_live_owned_authorized_registration(
    owned_hub, monkeypatch, tmp_path, condition
):
    launcher, registry, server = owned_hub
    if condition == "stopped":
        server.stop_server()
    elif condition == "dead_thread":
        server._srv.shutdown()
        server._thread.join(timeout=2)
        assert server.server_running is True
        assert not server._thread.is_alive()
    elif condition == "replaced":
        assert await registry.register_service("aetherra_hub", object())
    elif condition == "unowned":
        launcher._presence_owned_hub = None
    elif condition == "missing_owner":
        launcher.systems.pop("aetherra_hub")
    elif condition == "missing_registration":
        assert await registry.unregister_service("aetherra_hub")
    elif condition in {"degraded", "failed"}:
        await registry.update_service_status("aetherra_hub", ServiceStatus(condition))
    elif condition == "guardian_denied":
        monkeypatch.setattr(registry, "_registry_capability_checker", lambda *_: False)
    elif condition == "launcher_shutdown":
        launcher.running = False
    elif condition == "registry_stopped":
        registry._running = False
    else:
        proxy = SimpleNamespace(is_running=lambda: True)
        launcher.systems["aetherra_hub"] = proxy
        launcher._presence_owned_hub = None
        assert await registry.register_service("aetherra_hub", proxy)
    info = registry.get_service_info("aetherra_hub")
    old = datetime.now() - timedelta(seconds=240)
    if info is not None:
        info.last_heartbeat = old
    await launcher._refresh_observation_service_heartbeats()
    if info is None:
        assert registry.get_service_info("aetherra_hub") is None
    else:
        assert info.last_heartbeat == old
    if condition in {"degraded", "failed"}:
        assert info.status is ServiceStatus(condition)
    if condition == "guardian_denied":
        entries = [
            json.loads(line)
            for line in (tmp_path / ".aetherra/security/audit.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        assert any(
            entry.get("event_type") == "guardian_decision"
            and entry["details"].get("intent", {}).get("action")
            == "service_registry.heartbeat_update"
            and entry["details"]["decision"]["status"] == "deny"
            for entry in entries
        )


def test_flask_factory_and_requests_preserve_explicit_hub_owner(owned_hub):
    # Aetherra imports
    from aetherra_hub.app import create_app

    _, registry, server = owned_hub
    before = {
        thread.ident
        for thread in threading.enumerate()
        if thread.name == "hub-registry-heartbeat"
    }
    client = create_app().test_client()
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200
    _health(server)
    assert registry.get_service_info("aetherra_hub").instance is server
    assert {
        thread.ident
        for thread in threading.enumerate()
        if thread.name == "hub-registry-heartbeat"
    } == before
