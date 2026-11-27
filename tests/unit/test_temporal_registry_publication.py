"""Temporal registry health follows the owned collector, including after startup."""

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
import aetherra_os_launcher as launcher_module
import aetherra_service_registry as registry_module
from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)
from Aetherra.consciousness.temporal_observer import TemporalObserver
from aetherra_os_launcher import AetherraOSLauncher, MemoryAdapter
from aetherra_service_registry import ServiceStatus

# Local imports
from . import test_memory_temporal_history as history

policy = history.policy
memory = history.memory
temporal_policy = history.temporal_policy


async def until(check, timeout=3):
    deadline = time.monotonic() + timeout
    while not check():
        assert time.monotonic() < deadline, "Temporal registry state was not published"
        await asyncio.sleep(0.005)


@pytest_asyncio.fixture
async def temporal_launcher(memory, temporal_policy, monkeypatch):
    rules_path = temporal_policy / "guardian.json"
    rules = json.loads(rules_path.read_text())
    rules["allow"].extend(
        [
            {
                "requester": "service_registry",
                "subsystem": "service_registry",
                "action": "service_registry.*",
            },
            {
                "requester": "consciousness:core",
                "subsystem": "consciousness",
                "action": "consciousness.*",
            },
        ]
    )
    rules_path.write_text(json.dumps(rules))
    caps_path = temporal_policy / "capabilities.json"
    caps = json.loads(caps_path.read_text())
    caps["allow"]["service_registry"] = [
        "registry:register",
        "registry:status",
        "registry:heartbeat",
    ]
    caps_path.write_text(json.dumps(caps))
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", "")
    registry = registry_module.AetherraServiceRegistry()
    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    # Keep the real adapter, SQLite, job admission, collector and registry. The
    # unrelated engine constructor starts optional embedding/model components.
    backend = AetherraMemoryEngineAdvanced.__new__(AetherraMemoryEngineAdvanced)
    backend.core_memory = backend._checkpoint_core = memory
    launcher.systems["memory"] = MemoryAdapter(backend)
    monkeypatch.setattr(launcher, "_consciousness_core_readiness", lambda: None)
    monkeypatch.setattr(launcher, "_consciousness_observations", lambda: [])
    assert await registry.register_service("memory_system", backend)

    async def start():
        await launcher._start_consciousness_observer(
            {
                "consciousness_enabled": True,
                "temporal_observer": {
                    "enabled": True,
                    "history_id": "b" * 32,
                    "start_mode": "create",
                },
            }
        )
        return launcher._temporal_observer

    try:
        yield launcher, registry, start
    finally:
        await launcher._stop_consciousness_observer()


@pytest.mark.asyncio
async def test_starting_collector_is_not_discoverable_as_healthy(
    temporal_launcher, monkeypatch
):
    launcher, registry, start = temporal_launcher
    release = threading.Event()
    original = TemporalObserver._restore

    def held_restore(self):
        release.wait(4)
        original(self)

    monkeypatch.setattr(TemporalObserver, "_restore", held_restore)
    try:
        collector = await start()
        assert collector.get_runtime_status()["runtime_state"] == "starting"
        assert collector.get_runtime_status()["thread_alive"]
        assert registry.get_service("temporal_observer") is None
        assert (
            registry.get_service_info("temporal_observer").status
            is ServiceStatus.STARTING
        )
    finally:
        release.set()


@pytest.mark.asyncio
@pytest.mark.parametrize("reason", ["denied", "writer_fenced", "uncertain"])
async def test_post_start_block_removes_healthy_discovery(temporal_launcher, reason):
    launcher, registry, start = temporal_launcher
    collector = await start()
    await until(lambda: collector.get_runtime_status()["runtime_state"] == "running")
    await until(lambda: registry.get_service("temporal_observer") is collector)
    collector.block(reason)
    await until(lambda: registry.get_service("temporal_observer") is None)
    assert (
        registry.get_service_info("temporal_observer").status is ServiceStatus.DEGRADED
    )
    assert collector.get_runtime_status()["last_error_code"] == reason
    assert collector.get_runtime_status()["writer_epoch"] == 1


@pytest.mark.asyncio
async def test_running_collector_survives_actual_registry_stale_monitor(
    temporal_launcher, monkeypatch
):
    launcher, registry, start = temporal_launcher
    collector = await start()
    await until(lambda: collector.get_runtime_status()["runtime_state"] == "running")
    await until(lambda: registry.get_service("temporal_observer") is collector)
    now = datetime.now()
    monotonic = time.monotonic()
    monkeypatch.setattr(registry_module, "datetime", SimpleNamespace(now=lambda: now))
    monkeypatch.setattr(
        launcher_module, "time", SimpleNamespace(monotonic=lambda: monotonic)
    )

    async def monitor_tick(_delay):
        registry._running = False

    monkeypatch.setattr(
        registry_module,
        "asyncio",
        SimpleNamespace(**{**vars(asyncio), "sleep": monitor_tick}),
    )
    # Gate the owner monitor at its real polling boundary, then advance both
    # clocks. Each queue acknowledgement proves its preceding publication ended.
    polls = asyncio.Queue()

    async def owner_poll(_delay):
        ready = asyncio.get_running_loop().create_future()
        polls.put_nowait((asyncio.current_task(), ready))
        await ready

    monkeypatch.setattr(
        launcher_module,
        "asyncio",
        SimpleNamespace(**{**vars(asyncio), "sleep": owner_poll}),
    )

    async def temporal_poll():
        while True:
            task, ready = await asyncio.wait_for(polls.get(), 3)
            if task is launcher._temporal_task:
                return ready

    ready = await temporal_poll()
    for _ in range(7):
        now += timedelta(seconds=30)
        monotonic += 30
        ready.set_result(None)
        ready = await temporal_poll()
        assert registry.get_service_info("temporal_observer").last_heartbeat == now
        registry._running = True
        await registry._heartbeat_monitor()
        assert registry.get_service("temporal_observer") is collector
    assert registry.is_self_heartbeating("temporal_observer")


@pytest.mark.asyncio
async def test_stop_removes_healthy_registration_and_reuses_deadlines(
    temporal_launcher,
):
    launcher, registry, start = temporal_launcher
    collector = await start()
    await until(lambda: collector.get_runtime_status()["runtime_state"] == "running")
    await launcher._stop_consciousness_observer()
    assert collector.get_runtime_status()["runtime_state"] == "stopped"
    assert registry.get_service("temporal_observer") is None
    assert (
        registry.get_service_info("temporal_observer").status is ServiceStatus.STOPPING
    )
    deadlines = (
        launcher._consciousness_stop_deadline,
        launcher._temporal_stop_deadline,
    )
    await launcher._stop_consciousness_observer()
    assert deadlines == (
        launcher._consciousness_stop_deadline,
        launcher._temporal_stop_deadline,
    )
    assert launcher._temporal_task is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "replacement",
    ["temporal_observer", "consciousness_core", "memory_system", "blocked"],
)
async def test_replacement_during_preflight_never_publishes_stale_health(
    temporal_launcher, monkeypatch, replacement
):
    launcher, registry, start = temporal_launcher
    collector = await start()
    await until(lambda: collector.get_runtime_status()["runtime_state"] == "running")
    await until(lambda: registry.get_service("temporal_observer") is collector)
    original = registry._guardian_preflight
    entered, release = threading.Event(), threading.Event()

    def held_preflight(**kwargs):
        if kwargs["service_name"] == "temporal_observer":
            entered.set()
            release.wait(4)
        return original(**kwargs)

    monkeypatch.setattr(registry, "_guardian_preflight", held_preflight)
    clock = time.monotonic() + 31
    monkeypatch.setattr(
        launcher_module, "time", SimpleNamespace(monotonic=lambda: clock)
    )
    published_after_replacement = []
    replaced = False
    update = registry.update_service_status

    async def observed_update(name, status, *args, **kwargs):
        applied = await update(name, status, *args, **kwargs)
        if applied and replaced and name == "temporal_observer":
            published_after_replacement.append(status)
        return applied

    monkeypatch.setattr(registry, "update_service_status", observed_update)
    try:
        await until(entered.is_set)
        info = registry.get_service_info("temporal_observer")
        old = info.last_heartbeat
        if replacement == "blocked":
            collector.block("denied")
        else:
            registry.get_service_info(replacement).instance = object()
        replaced = True
        release.set()
        await until(
            lambda: (
                registry._status_preflight_worker is not None
                and not registry._status_preflight_worker.is_alive()
            )
        )
        await asyncio.sleep(0.02)
        assert ServiceStatus.HEALTHY not in published_after_replacement
        if replacement == "temporal_observer":
            await launcher._stop_consciousness_observer()
            assert info.last_heartbeat == old
            assert info.status is ServiceStatus.HEALTHY
    finally:
        release.set()


@pytest.mark.asyncio
async def test_blocked_publication_is_nonblocking_bounded_and_cancellable(
    temporal_launcher, monkeypatch
):
    launcher, registry, start = temporal_launcher
    collector = await start()
    await until(lambda: collector.get_runtime_status()["runtime_state"] == "running")
    await until(lambda: registry.get_service("temporal_observer") is collector)
    original = registry._guardian_preflight
    entered, release = threading.Event(), threading.Event()
    calls = []
    caller = threading.get_ident()

    def held_preflight(**kwargs):
        if kwargs["service_name"] == "temporal_observer":
            calls.append(threading.get_ident())
            entered.set()
            release.wait(5)
        return original(**kwargs)

    monkeypatch.setattr(registry, "_guardian_preflight", held_preflight)
    collector.block("denied")
    try:
        await until(entered.is_set)
        ticks = 0
        end = time.monotonic() + 1.2
        while time.monotonic() < end:
            ticks += 1
            await asyncio.sleep(0.01)
        assert ticks >= 30
        assert calls == [calls[0]]
        assert calls[0] != caller
        before = time.monotonic()
        await launcher._stop_consciousness_observer()
        assert time.monotonic() - before < 3.2
        assert launcher._temporal_task is None
        old = registry.get_service_info("temporal_observer").last_heartbeat
    finally:
        release.set()
    await until(lambda: not registry._status_preflight_worker.is_alive())
    await asyncio.sleep(0.02)
    assert registry.get_service_info("temporal_observer").last_heartbeat == old


@pytest.mark.asyncio
async def test_denied_status_preserves_policy_and_retries_when_permitted(
    temporal_launcher, temporal_policy, monkeypatch
):
    launcher, registry, start = temporal_launcher
    collector = await start()
    await until(lambda: collector.get_runtime_status()["runtime_state"] == "running")
    await until(lambda: registry.get_service("temporal_observer") is collector)
    # Isolate Temporal publication from Core's deliberate stop-on-policy-denial
    # behavior. The original Core worker remains alive and is stopped in cleanup.
    launcher._consciousness_task.cancel()
    await asyncio.gather(launcher._consciousness_task, return_exceptions=True)
    launcher._consciousness_task = None
    attempt_finished = asyncio.Event()

    async def owner_poll(delay):
        if asyncio.current_task() is launcher._temporal_task:
            attempt_finished.set()
        await asyncio.sleep(delay)

    monkeypatch.setattr(
        launcher_module,
        "asyncio",
        SimpleNamespace(**{**vars(asyncio), "sleep": owner_poll}),
    )
    policy_path = temporal_policy / "guardian.json"
    original_policy = policy_path.read_text()
    denied = json.loads(original_policy)
    denied["allow"] = [
        rule for rule in denied["allow"] if rule["requester"] != "service_registry"
    ]
    policy_path.write_text(json.dumps(denied))
    collector.block("denied")
    old = registry.get_service_info("temporal_observer").last_heartbeat
    ledger = temporal_policy.parent / ".aetherra/security/audit.jsonl"

    def status_denied():
        return any(
            row.get("details", {}).get("intent", {}).get("action")
            == "service_registry.status_update"
            and row["details"]["intent"]["metadata"]["service_name"]
            == "temporal_observer"
            and row["details"].get("decision", {}).get("status") == "deny"
            for row in (json.loads(line) for line in ledger.read_text().splitlines())
        )

    await asyncio.wait_for(attempt_finished.wait(), 3)
    assert status_denied()
    assert registry.get_service_info("temporal_observer").last_heartbeat == old
    # Registry registration defaults healthy. A denied update cannot bypass
    # Guardian to correct that cached state, even though the collector is blocked.
    assert registry.get_service("temporal_observer") is collector
    policy_path.write_text(original_policy)
    clock = time.monotonic() + 31
    monkeypatch.setattr(
        launcher_module, "time", SimpleNamespace(monotonic=lambda: clock)
    )
    await until(lambda: registry.get_service("temporal_observer") is None)
    assert (
        registry.get_service_info("temporal_observer").status is ServiceStatus.DEGRADED
    )
    assert collector.get_runtime_status()["writer_epoch"] == 1


@pytest.mark.asyncio
async def test_stopping_collector_stops_healthy_discovery_before_cleanup(
    temporal_launcher,
):
    launcher, registry, start = temporal_launcher
    collector = await start()
    await until(lambda: collector.get_runtime_status()["runtime_state"] == "running")
    await until(lambda: registry.get_service("temporal_observer") is collector)
    collector.close_observation_admission()
    await until(lambda: registry.get_service("temporal_observer") is None)
    assert collector.get_runtime_status()["runtime_state"] == "stopping"
    assert (
        registry.get_service_info("temporal_observer").status is ServiceStatus.STOPPING
    )


@pytest.mark.asyncio
async def test_refused_worker_start_publishes_blocked_registration(
    temporal_launcher, monkeypatch
):
    launcher, registry, start = temporal_launcher

    def refused_start(self):
        raise RuntimeError("worker start refused")

    monkeypatch.setattr(TemporalObserver, "start", refused_start)
    collector = await start()
    assert collector.get_runtime_status()["runtime_state"] == "blocked"
    assert registry.get_service("temporal_observer") is None
    assert (
        registry.get_service_info("temporal_observer").status is ServiceStatus.DEGRADED
    )
    await launcher._stop_consciousness_observer()
    assert registry.get_service("temporal_observer") is None


@pytest.mark.asyncio
@pytest.mark.parametrize("loss", ["stopped_core", "expired_cache"])
async def test_lost_source_or_expired_cache_is_not_healthy(
    temporal_launcher, monkeypatch, loss
):
    # Aetherra imports
    from Aetherra.consciousness import temporal_observer as temporal_module

    launcher, registry, start = temporal_launcher
    samples = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def wait_for_sample(self, _deadline):
        loop.call_soon_threadsafe(samples.put_nowait, self.get_runtime_status())
        self._wake.wait(4)
        self._wake.clear()

    monkeypatch.setattr(TemporalObserver, "_wait_for_sample", wait_for_sample)
    collector = await start()
    source = launcher._temporal_source
    status = await asyncio.wait_for(samples.get(), 3)
    if not status["source_fresh"]:
        await until(lambda: source.get_temporal_observation() is not None)
        collector._wake.set()
        status = await asyncio.wait_for(samples.get(), 3)
    assert status["source_fresh"]
    await until(lambda: registry.get_service("temporal_observer") is collector)
    epoch = status["writer_epoch"]
    owner = registry.get_service_info("temporal_observer")

    with monkeypatch.context() as patch:
        if loss == "stopped_core":
            await source.stop()
            assert source.get_temporal_observation() is None
            collector._wake.set()
            status = await asyncio.wait_for(samples.get(), 3)
            assert not status["source_fresh"]
        else:
            patch.setattr(
                temporal_module,
                "time",
                SimpleNamespace(
                    **{**vars(time), "monotonic": lambda: time.monotonic() + 6}
                ),
            )
        status = collector.get_runtime_status()
        assert status["runtime_state"] == "running"
        assert status["thread_alive"]
        assert not status["source_fresh"]
        assert registry.get_service_info("consciousness_core").instance is source
        assert registry.get_service_info("temporal_observer") is owner
        await until(lambda: registry.get_service("temporal_observer") is None)
        assert owner.status is ServiceStatus.DEGRADED
        assert collector.get_runtime_status()["writer_epoch"] == epoch
        if loss == "expired_cache":
            # The same live Core supplies a fresh sample; no writer is reacquired.
            assert source.get_temporal_observation() is not None
            collector._wake.set()
            status = await asyncio.wait_for(samples.get(), 3)
            assert status["source_fresh"]
            await until(lambda: registry.get_service("temporal_observer") is collector)
            assert registry.get_service_info("temporal_observer") is owner
            assert collector.get_runtime_status()["writer_epoch"] == epoch
