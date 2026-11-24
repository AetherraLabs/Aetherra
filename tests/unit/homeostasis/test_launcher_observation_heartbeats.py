"""Launcher liveness must preserve real observation flow past registry expiry."""

# Standard library imports
import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from types import SimpleNamespace

# Third party imports
import pytest
import pytest_asyncio

# Aetherra imports
import Aetherra.homeostasis.homeostasis_integration as integration
import aetherra_service_registry as registry_module
from Aetherra.homeostasis import audit_trace_layer, stability_metrics, system_supervisor
from Aetherra.homeostasis.stability_metrics import MetricSnapshot
from aetherra_service_registry import ServiceStatus

NAMES = {
    "homeostasis": ("homeostasis_system", "aetherra_homeostasis"),
    "self_improvement": ("self_improvement_engine",),
    "maintenance": ("maintenance_system", "aetherra_maintenance"),
}


@pytest_asyncio.fixture
async def live_launcher(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for key, value in {
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(tmp_path / "policy"),
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_HOMEOSTASIS_OBSERVE_ONLY": "1",
        "AETHERRA_SELFINC_ENABLED": "0",
        "AETHERRA_REGISTRY_URL": "",
        "AETHERRA_SKIP_DOTENV": "1",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.setattr(integration, "_homeostasis_instance", None)
    monkeypatch.setattr(audit_trace_layer, "_audit_layer_instance", None)
    monkeypatch.setattr(stability_metrics, "_stability_metrics", None)
    monkeypatch.setattr(system_supervisor, "_system_supervisor", None)
    registry = registry_module.AetherraServiceRegistry()
    monkeypatch.setattr(registry_module, "_service_registry", registry)
    registry._running = True

    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    await launcher._load_self_maintenance_systems(
        {"self_improvement_db": str(tmp_path / "self_improvement.db")}
    )
    await launcher._load_homeostasis_system({})
    await launcher._load_maintenance_system({"maintenance_enabled": True})
    homeostasis = launcher.systems["homeostasis"]

    async def sample():
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            memory_rtt=300.0,
            raw_data={"measured_metrics": ["memory_rtt"]},
        )
        homeostasis.metrics.current_snapshot = snapshot
        return snapshot

    async def no_external_watchdog():
        pass

    monkeypatch.setattr(homeostasis.metrics, "collect_snapshot", sample)
    monkeypatch.setattr(homeostasis, "_start_watchdog", no_external_watchdog)
    monkeypatch.setattr(homeostasis, "_integrate_with_scheduler", no_external_watchdog)
    homeostasis.metrics_bridge.bridge_interval = 3600
    await homeostasis.start()
    await sample()
    await asyncio.sleep(0)
    launcher.running = True
    assert await registry.register_service("unrelated_service", object())
    try:
        yield launcher, registry
    finally:
        launcher.running = False
        # Negative cases intentionally change flags or task state.
        homeostasis.running = True
        await homeostasis.stop()
        await launcher.systems["self_improvement"].impl.stop_improvement_cycle()
        for task in (launcher._improvement_telemetry_task,):
            if task is not None:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
        registry._running = False


def _age(registry):
    old = datetime.now() - timedelta(seconds=240)
    for info in registry._services.values():
        info.last_heartbeat = old
    return old


@pytest.mark.asyncio
async def test_normal_operation_loop_keeps_observation_flow_after_240_seconds(
    live_launcher, monkeypatch
):
    # Aetherra imports
    import aetherra_os_launcher as launcher_module

    launcher, registry = live_launcher
    homeostasis = launcher.systems["homeostasis"]
    engine = launcher.systems["self_improvement"].impl
    assert homeostasis.metrics_collection_task.get_loop() is asyncio.get_running_loop()
    assert engine.improvement_task.get_loop() is asyncio.get_running_loop()
    clock = datetime.now()
    started = clock
    ticks = 0
    unrelated_heartbeat = registry.get_service_info("unrelated_service").last_heartbeat

    class Clock:
        @staticmethod
        def now():
            return clock

    async def monitor_tick(_delay):
        registry._running = False

    async def operating_tick(delay):
        nonlocal clock, ticks
        assert delay == 30
        clock += timedelta(seconds=delay)
        ticks += 1
        await registry._heartbeat_monitor()
        registry._running = True
        for key, names in NAMES.items():
            for name in names:
                assert registry.get_service(name) is launcher.systems[key]
        before = engine.get_improvement_status()["homeostasis_flow"][
            "observations_received"
        ]
        await homeostasis.metrics_bridge._forward_metrics()
        assert (
            engine.get_improvement_status()["homeostasis_flow"]["observations_received"]
            > before
        )
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
        SimpleNamespace(**{**vars(asyncio), "sleep": operating_tick}),
    )
    monkeypatch.setattr(launcher, "_write_os_status", no_status_file)
    monkeypatch.setattr(launcher, "_cleanup_os_status", no_status_file)
    await launcher._main_operation_loop()
    assert ticks == 8, "the observation flow must survive all eight 30-second ticks"
    assert (clock - started).total_seconds() == 240
    assert (
        registry.get_service_info("unrelated_service").status is ServiceStatus.DEGRADED
    )
    # The monitor itself updates status timestamps, but no owner refreshed this service.
    assert unrelated_heartbeat < started + timedelta(seconds=180)
    records = launcher.systems["maintenance"].export_records()
    assert records
    assert all(record["status"] == "proposed" for record in records)
    assert all(record["execution"] is None for record in records)
    assert all(record["guardian_decision"] is None for record in records)


@pytest.mark.parametrize("key", list(NAMES))
@pytest.mark.parametrize(
    "condition", ["missing", "unowned", "replaced", "failed", "degraded"]
)
@pytest.mark.asyncio
async def test_heartbeat_requires_owned_healthy_registration(
    live_launcher, key, condition
):
    launcher, registry = live_launcher
    old = _age(registry)
    owned = launcher.systems.pop(key) if condition == "unowned" else None
    for name in NAMES[key]:
        info = registry.get_service_info(name)
        if condition == "missing":
            registry._services.pop(name)
        elif condition == "replaced":
            info.instance = object()
        elif condition in {"failed", "degraded"}:
            info.status = ServiceStatus(condition)
    try:
        await launcher._refresh_observation_service_heartbeats()
    finally:
        if owned is not None:
            launcher.systems[key] = owned
    for name in NAMES[key]:
        info = registry.get_service_info(name)
        if info is not None:
            assert info.last_heartbeat == old
            if condition in {"failed", "degraded"}:
                assert info.status is ServiceStatus(condition)
    assert registry.get_service_info("unrelated_service").last_heartbeat == old


@pytest.mark.parametrize(
    "condition",
    ["uninitialized", "stopped", "metrics_done", "bridge_done", "bridge_stopped"],
)
@pytest.mark.asyncio
async def test_homeostasis_heartbeat_requires_live_collection_and_bridge(
    live_launcher, condition
):
    launcher, registry = live_launcher
    homeostasis = launcher.systems["homeostasis"]
    old = _age(registry)
    if condition == "uninitialized":
        homeostasis.initialized = False
    elif condition == "stopped":
        homeostasis.running = False
    elif condition == "bridge_stopped":
        homeostasis.metrics_bridge.running = False
    else:
        task = (
            homeostasis.metrics_collection_task
            if condition == "metrics_done"
            else homeostasis.metrics_bridge._task
        )
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    await launcher._refresh_observation_service_heartbeats()
    assert all(
        registry.get_service_info(name).last_heartbeat == old
        for name in NAMES["homeostasis"]
    )


@pytest.mark.parametrize("condition", ["inactive", "done", "cancelling"])
@pytest.mark.asyncio
async def test_self_improvement_heartbeat_requires_active_task(
    live_launcher, condition
):
    launcher, registry = live_launcher
    engine = launcher.systems["self_improvement"].impl
    old = _age(registry)
    if condition == "inactive":
        engine.improvement_active = False
    else:
        engine.improvement_task.cancel()
        if condition == "done":
            await asyncio.gather(engine.improvement_task, return_exceptions=True)
    await launcher._refresh_observation_service_heartbeats()
    assert registry.get_service_info("self_improvement_engine").last_heartbeat == old
    engine.improvement_active = True


@pytest.mark.parametrize(
    "condition", ["launcher_stopped", "registry_stopped", "denied"]
)
@pytest.mark.asyncio
async def test_shutdown_or_guardian_denial_preserves_heartbeats(
    live_launcher, monkeypatch, tmp_path, condition
):
    launcher, registry = live_launcher
    old = _age(registry)
    if condition == "launcher_stopped":
        launcher.running = False
    elif condition == "registry_stopped":
        registry._running = False
    else:
        monkeypatch.setattr(registry, "_registry_capability_checker", lambda *_: False)
    await launcher._refresh_observation_service_heartbeats()
    assert all(info.last_heartbeat == old for info in registry._services.values())
    if condition == "denied":
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


@pytest.mark.parametrize("condition", ["unavailable", "raises", "malformed"])
@pytest.mark.asyncio
async def test_maintenance_heartbeat_requires_available_status(
    live_launcher, monkeypatch, condition
):
    launcher, registry = live_launcher
    old = _age(registry)

    def status():
        if condition == "raises":
            raise RuntimeError("offline")
        return {"service": {"available": False}} if condition == "unavailable" else {}

    monkeypatch.setattr(launcher.systems["maintenance"], "get_status", status)
    await launcher._refresh_observation_service_heartbeats()
    assert all(
        registry.get_service_info(name).last_heartbeat == old
        for name in NAMES["maintenance"]
    )


@pytest.mark.asyncio
async def test_blocked_maintenance_status_does_not_accumulate_workers(
    live_launcher, monkeypatch
):
    launcher, registry = live_launcher
    old = _age(registry)
    release = threading.Event()
    calls = 0

    def blocked_status():
        nonlocal calls
        calls += 1
        release.wait(5)
        return {"service": {"available": True}}

    monkeypatch.setattr(launcher.systems["maintenance"], "get_status", blocked_status)
    try:
        await asyncio.wait_for(launcher._refresh_observation_service_heartbeats(), 2)
        for _ in range(3):
            await asyncio.wait_for(
                launcher._refresh_observation_service_heartbeats(), 0.5
            )
        assert calls == 1
        assert registry.get_service_info("maintenance_system").last_heartbeat == old
        assert registry.get_service_info("homeostasis_system").last_heartbeat > old
        assert registry.get_service_info("self_improvement_engine").last_heartbeat > old
    finally:
        release.set()
        pending = launcher._maintenance_liveness_future
        if pending is not None:
            await asyncio.wrap_future(pending)
    monkeypatch.setattr(
        launcher.systems["maintenance"],
        "get_status",
        lambda: {"service": {"available": False}},
    )
    await launcher._refresh_observation_service_heartbeats()
    assert registry.get_service_info("maintenance_system").last_heartbeat == old


@pytest.mark.parametrize("condition", ["shutdown", "registry_stopped", "replaced"])
@pytest.mark.asyncio
async def test_maintenance_status_cannot_pulse_after_lifecycle_changes(
    live_launcher, monkeypatch, condition
):
    launcher, registry = live_launcher
    old = _age(registry)
    loop = asyncio.get_running_loop()
    started = asyncio.Event()
    release = threading.Event()

    def status():
        loop.call_soon_threadsafe(started.set)
        release.wait(5)
        return {"service": {"available": True}}

    monkeypatch.setattr(launcher.systems["maintenance"], "get_status", status)
    refresh = asyncio.create_task(launcher._refresh_observation_service_heartbeats())
    try:
        await asyncio.wait_for(started.wait(), 2)
        if condition == "shutdown":
            launcher.running = False
        elif condition == "registry_stopped":
            registry._running = False
        else:
            for name in NAMES["maintenance"]:
                registry.get_service_info(name).instance = object()
    finally:
        release.set()
        await refresh
    assert all(
        registry.get_service_info(name).last_heartbeat == old
        for name in NAMES["maintenance"]
    )


def test_blocked_maintenance_probe_does_not_delay_process_shutdown(
    monkeypatch, tmp_path
):
    # Standard library imports
    import os
    import subprocess
    import sys
    from pathlib import Path

    # Do not rely on an import path inherited from the parent test runner.
    monkeypatch.delenv("PYTHONPATH", raising=False)
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", "")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    child_env = os.environ.copy()
    child_env["PYTHONPATH"] = str(Path(__file__).resolve().parents[3])
    script = """
import asyncio
import threading
from Aetherra.maintenance import MaintenanceService
from aetherra_os_launcher import AetherraOSLauncher
from aetherra_service_registry import AetherraServiceRegistry

async def main():
    launcher = AetherraOSLauncher()
    registry = AetherraServiceRegistry()
    registry._running = True
    launcher.service_registry = registry
    launcher.running = True
    maintenance = MaintenanceService.with_default_store(".")
    launcher.systems["maintenance"] = maintenance
    await registry.register_service("maintenance_system", maintenance)
    before = registry.get_service_info("maintenance_system").last_heartbeat
    blocked = threading.Event()
    maintenance.get_status = blocked.wait
    await launcher._refresh_observation_service_heartbeats()
    assert registry.get_service_info("maintenance_system").last_heartbeat == before
    await launcher._graceful_shutdown()

asyncio.run(main())
print("SHUTDOWN_COMPLETE", flush=True)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env=child_env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "SHUTDOWN_COMPLETE" in result.stdout


@pytest.mark.asyncio
async def test_failed_maintenance_reader_start_can_retry(live_launcher, monkeypatch):
    # Aetherra imports
    import aetherra_os_launcher as launcher_module

    launcher, registry = live_launcher
    old = _age(registry)
    real_thread = launcher_module.Thread

    class UnavailableThread:
        def __init__(self, **_kwargs):
            pass

        def start(self):
            raise RuntimeError("cannot start thread")

    monkeypatch.setattr(launcher_module, "Thread", UnavailableThread)
    await launcher._refresh_observation_service_heartbeats()
    assert registry.get_service_info("maintenance_system").last_heartbeat == old
    monkeypatch.setattr(launcher_module, "Thread", real_thread)
    await launcher._refresh_observation_service_heartbeats()
    assert registry.get_service_info("maintenance_system").last_heartbeat > old
