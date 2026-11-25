"""The owned Engine heartbeat depends on a live kernel and audited authorization."""

# Standard library imports
import asyncio
import json
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from types import SimpleNamespace

# Third party imports
import pytest
import pytest_asyncio

# Aetherra imports
import aetherra_service_registry as registry_module
from Aetherra.security.audit_ledger import SecurityAuditLedger
from aetherra_kernel_loop import AetherraKernelLoop
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)


@pytest_asyncio.fixture
async def engine_launcher(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for key, value in {
        "AETHERRA_PROFILE": "test",
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(tmp_path / "policy"),
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_SKIP_DOTENV": "1",
        "AETHERRA_REGISTRY_URL": "",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("AETHERRA_GUARDIAN_POLICY", raising=False)
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher, EngineAdapter

    launcher = AetherraOSLauncher()
    registry = AetherraServiceRegistry()
    launcher.service_registry = registry
    registry._running = True
    # The liveness contract is initialized state, not text-generation behavior.
    adapter = EngineAdapter(SimpleNamespace(initialized=True))
    kernel = AetherraKernelLoop()
    kernel.running = True
    kernel.aetherra_engine = adapter
    launcher.kernel_loop = kernel
    launcher.systems["aetherra"] = adapter
    launcher.running = True
    task = asyncio.create_task(asyncio.Event().wait())
    launcher._kernel_task = task
    assert await registry.register_service("kernel_loop", kernel)
    assert await registry.register_service("aetherra_engine", adapter.impl)
    assert await registry.register_service("unrelated_service", object())
    try:
        yield launcher, registry, adapter, tmp_path
    finally:
        launcher.running = False
        registry._running = False
        kernel.running = False
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
async def test_operation_loop_preserves_owned_engine_past_real_registry_expiry(
    engine_launcher, monkeypatch
):
    # Aetherra imports
    import aetherra_os_launcher as launcher_module

    launcher, registry, adapter, root = engine_launcher
    clock = datetime.now()
    started = clock
    ticks = 0

    class Clock:
        @staticmethod
        def now():
            return clock

    async def monitor_tick(delay):
        if delay == registry._heartbeat_interval_sec:
            registry._running = False
        else:
            await asyncio.sleep(delay)

    async def operating_tick(delay):
        nonlocal clock, ticks
        assert delay == 30
        clock += timedelta(seconds=30)
        ticks += 1
        # The real kernel already maintains its own heartbeat.
        await registry.update_heartbeat("kernel_loop")
        await registry._heartbeat_monitor()
        registry._running = True
        assert (
            registry.get_service_info("aetherra_engine").status is ServiceStatus.HEALTHY
        )
        if ticks == 8:
            launcher.running = False

    async def no_status_file():
        pass

    monkeypatch.setattr(registry_module, "datetime", Clock)
    monkeypatch.setattr(
        registry_module,
        "asyncio",
        SimpleNamespace(
            **{
                **vars(asyncio),
                "sleep": monitor_tick,
            }
        ),
    )
    monkeypatch.setattr(
        launcher_module,
        "asyncio",
        SimpleNamespace(
            **{
                **vars(asyncio),
                "sleep": operating_tick,
            }
        ),
    )
    monkeypatch.setattr(launcher, "_write_os_status", no_status_file)
    monkeypatch.setattr(launcher, "_cleanup_os_status", no_status_file)
    await launcher._main_operation_loop()
    assert ticks == 8
    assert (clock - started).total_seconds() == 240
    info = registry.get_service_info("aetherra_engine")
    assert info.instance is adapter.impl
    assert info.status is ServiceStatus.HEALTHY
    assert info.last_heartbeat >= started + timedelta(seconds=210)
    assert (
        registry.get_service_info("unrelated_service").status is ServiceStatus.DEGRADED
    )
    records = [
        json.loads(line)
        for line in (root / ".aetherra/security/audit.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    updates = [
        record
        for record in records
        if record.get("details", {}).get("intent", {}).get("action")
        == "service_registry.status_update"
        and record["details"]["intent"]["metadata"]["service_name"] == "aetherra_engine"
    ]
    assert len(updates) == 8
    assert all(record["details"]["decision"]["status"] == "allow" for record in updates)


def _invalidate(launcher, registry, adapter, condition):
    if condition == "launcher_stopped":
        launcher.running = False
    elif condition == "registry_stopped":
        registry._running = False
    elif condition == "foreign_registry":
        launcher.service_registry = AetherraServiceRegistry()
    elif condition == "uninitialized":
        adapter.impl.initialized = False
    elif condition == "truthy_initialized":
        adapter.impl.initialized = 1
    elif condition == "kernel_stopped":
        launcher.kernel_loop.running = False
    elif condition == "kernel_engine_replaced":
        launcher.kernel_loop.aetherra_engine = object()
    elif condition == "engine_replaced":
        launcher.systems["aetherra"] = object()
    elif condition == "implementation_replaced":
        adapter.impl = SimpleNamespace(initialized=True)
    elif condition == "duck_adapter":
        impostor = SimpleNamespace(impl=adapter.impl)
        launcher.systems["aetherra"] = impostor
        launcher.kernel_loop.aetherra_engine = impostor
    elif condition == "task_missing":
        launcher._kernel_task = None
    elif condition == "task_canceling":
        launcher._kernel_task.cancel()
    elif condition.startswith("engine_") or condition.startswith("kernel_"):
        name = "aetherra_engine" if condition.startswith("engine_") else "kernel_loop"
        info = registry.get_service_info(name)
        action = condition.split("_", 1)[1]
        if action == "missing":
            registry._services.pop(name)
        elif action == "foreign":
            info.instance = object()
        elif action == "registration_replaced":
            registry._services[name] = ServiceInfo(
                name, info.instance, status=ServiceStatus.HEALTHY
            )
        elif action == "stub":
            info.metadata["stub"] = True
        elif action == "mock":
            info.metadata["type"] = "mock"
        else:
            info.status = ServiceStatus(action)
    else:
        raise AssertionError(condition)


@pytest.mark.parametrize(
    "condition",
    [
        "launcher_stopped",
        "registry_stopped",
        "uninitialized",
        "truthy_initialized",
        "kernel_stopped",
        "kernel_engine_replaced",
        "engine_replaced",
        "implementation_replaced",
        "duck_adapter",
        "task_missing",
        "task_canceling",
        "engine_missing",
        "engine_foreign",
        "engine_failed",
        "engine_degraded",
        "engine_stub",
        "engine_mock",
        "kernel_missing",
        "kernel_foreign",
        "kernel_failed",
        "kernel_degraded",
        "kernel_stub",
        "kernel_mock",
    ],
)
@pytest.mark.asyncio
async def test_refresh_requires_live_owned_initialized_engine(
    engine_launcher, condition
):
    launcher, registry, adapter, _ = engine_launcher
    info = registry.get_service_info("aetherra_engine")
    before = info.last_heartbeat
    _invalidate(launcher, registry, adapter, condition)
    assert await launcher._refresh_owned_engine_heartbeat() is False
    assert info.last_heartbeat == before


@pytest.mark.asyncio
async def test_completed_kernel_task_is_not_liveness(engine_launcher):
    launcher, registry, _, _ = engine_launcher
    before = registry.get_service_info("aetherra_engine").last_heartbeat
    launcher._kernel_task.cancel()
    await asyncio.gather(launcher._kernel_task, return_exceptions=True)
    assert await launcher._refresh_owned_engine_heartbeat() is False
    assert registry.get_service_info("aetherra_engine").last_heartbeat == before


@pytest.mark.parametrize("failure", ["policy", "audit"])
@pytest.mark.asyncio
async def test_authorization_failure_does_not_refresh_or_interrupt_launcher(
    engine_launcher, monkeypatch, failure
):
    launcher, registry, _, root = engine_launcher
    before = registry.get_service_info("aetherra_engine").last_heartbeat
    if failure == "policy":
        path = root / "deny.json"
        path.write_text(
            json.dumps(
                {
                    "default": "allow",
                    "deny": [
                        {"action": "service_registry.status_update"},
                    ],
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("AETHERRA_GUARDIAN_POLICY", str(path))
    else:

        def unavailable(*args, **kwargs):
            raise OSError("synthetic unavailable ledger")

        monkeypatch.setattr(SecurityAuditLedger, "append", unavailable)
    assert await launcher._refresh_owned_engine_heartbeat() is False
    assert launcher.running is True
    assert registry.get_service_info("aetherra_engine").last_heartbeat == before


@contextmanager
def _contended_audit(root, monkeypatch):
    ledger = SecurityAuditLedger(root / ".aetherra/security/audit.jsonl")
    acquired, release, entered = threading.Event(), threading.Event(), threading.Event()
    append = SecurityAuditLedger.append

    def observed(ledger, **kwargs):
        entered.set()
        return append(ledger, **kwargs)

    def hold():
        with ledger._lock:
            acquired.set()
            release.wait(5)

    monkeypatch.setattr(SecurityAuditLedger, "append", observed)
    holder = threading.Thread(target=hold, daemon=True)
    holder.start()
    assert acquired.wait(1)
    try:
        yield entered, release
    finally:
        release.set()
        holder.join(1)


@pytest.mark.parametrize(
    "condition",
    [
        "launcher_stopped",
        "registry_stopped",
        "foreign_registry",
        "uninitialized",
        "kernel_stopped",
        "kernel_engine_replaced",
        "implementation_replaced",
        "task_canceling",
        "kernel_registration_replaced",
        "engine_registration_replaced",
        "engine_degraded",
    ],
)
@pytest.mark.asyncio
async def test_liveness_is_rechecked_after_real_contended_audit(
    engine_launcher, monkeypatch, condition
):
    launcher, registry, adapter, root = engine_launcher
    info = registry.get_service_info("aetherra_engine")
    before = info.last_heartbeat
    with _contended_audit(root, monkeypatch) as (entered, release):
        update = asyncio.create_task(launcher._refresh_owned_engine_heartbeat())
        async with asyncio.timeout(1):
            while not entered.is_set():
                await asyncio.sleep(0.001)
        _invalidate(launcher, registry, adapter, condition)
        release.set()
        assert await update is False
    assert info.last_heartbeat == before


@pytest.mark.asyncio
async def test_engine_heartbeat_and_observer_monitor_serialize_without_stopping_observer(
    engine_launcher, monkeypatch
):
    launcher, registry, _, root = engine_launcher

    class Observer:
        stopped = False
        reads = 0

        def get_runtime_status(self):
            self.reads += 1
            return {"runtime_state": "stopped" if self.stopped else "running"}

        async def stop(self):
            self.stopped = True

    observer = Observer()
    assert await registry.register_service("consciousness_core", observer)
    info = registry.get_service_info("consciousness_core")
    before = info.last_heartbeat
    monitor = None
    with _contended_audit(root, monkeypatch) as (entered, release):
        refresh = asyncio.create_task(launcher._refresh_owned_engine_heartbeat())
        try:
            async with asyncio.timeout(1):
                while not entered.is_set():
                    await asyncio.sleep(0.001)
            monitor = asyncio.create_task(
                launcher._monitor_consciousness_observer(observer)
            )
            async with asyncio.timeout(1):
                while not observer.reads:
                    await asyncio.sleep(0.001)
            await asyncio.sleep(0.02)
            assert not observer.stopped
            assert not monitor.done()
            release.set()
            assert await refresh is True
            async with asyncio.timeout(1):
                while info.last_heartbeat == before:
                    await asyncio.sleep(0.001)
            assert info.status is ServiceStatus.HEALTHY
            assert not observer.stopped
        finally:
            refresh.cancel()
            if monitor:
                monitor.cancel()
            await asyncio.gather(
                refresh, *([monitor] if monitor else []), return_exceptions=True
            )
