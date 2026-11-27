"""Normal launcher Temporal binding and shutdown boundaries."""

# Standard library imports
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

# Third party imports
import pytest

# Aetherra imports
from Aetherra.runtime_ui.snapshot import collect_temporal_runtime_metrics
from aetherra_hub.services.state import hub_state
from aetherra_os_launcher import AetherraOSLauncher


class Registry:
    def get_service_info(self, name):
        return None

    def get_registry_status(self):
        return {"running": True}


@pytest.mark.parametrize(
    ("config", "state"),
    [({}, "disabled"), ({"temporal_observer": {"enabled": 1}}, "blocked")],
)
def test_inert_launcher(config, state):
    launcher = AetherraOSLauncher()
    registry = launcher.service_registry = Registry()
    asyncio.run(launcher._start_consciousness_observer(config))
    assert collect_temporal_runtime_metrics(registry)["temporal_runtime_state"] == state
    asyncio.run(launcher._stop_consciousness_observer())
    assert hub_state.temporal_status_provider(registry) is None


def test_shutdown_retains_original_and_suppresses_marker():
    launcher = AetherraOSLauncher()
    original = SimpleNamespace(
        stop=AsyncMock(side_effect=RuntimeError("core failure")),
        get_runtime_status=Mock(),
    )
    launcher._temporal_source = original
    launcher.systems["consciousness_core"] = Mock()
    temporal = launcher._temporal_observer = Mock()
    temporal.stop = AsyncMock(return_value=False)
    with pytest.raises(RuntimeError, match="core failure"):
        asyncio.run(launcher._stop_consciousness_observer(save_checkpoint=True))
    temporal.close_observation_admission.assert_called_once()
    assert temporal.stop.await_args.kwargs["save_history"] is False
    assert launcher._temporal_observer is temporal


@pytest.mark.asyncio
async def test_monitor_then_orderly_uses_original_core_deadline():
    launcher = AetherraOSLauncher()
    original = SimpleNamespace(stop=AsyncMock(), get_runtime_status=lambda: {})
    launcher._temporal_source = original
    launcher.systems["consciousness_core"] = Mock()
    temporal = launcher._temporal_observer = Mock()
    temporal.stop = AsyncMock(return_value=True)
    await launcher._monitor_consciousness_observer(original)
    initial_core_deadline = original.stop.await_args.kwargs["deadline"]
    initial_temporal_deadline = temporal.stop.await_args.kwargs["deadline"]
    assert not temporal.stop.await_args.kwargs["save_history"]
    await launcher._stop_consciousness_observer(save_checkpoint=True)
    assert original.stop.await_args.kwargs["deadline"] == initial_core_deadline
    assert temporal.stop.await_args.kwargs["deadline"] == initial_temporal_deadline
    assert temporal.stop.await_args.kwargs["save_history"] is False


@pytest.mark.asyncio
async def test_inert_launcher_never_stops_foreign_core():
    launcher = AetherraOSLauncher()
    launcher.service_registry = Registry()
    await launcher._start_consciousness_observer({})
    foreign = launcher.systems["consciousness_core"] = Mock()
    foreign.stop = AsyncMock()
    await launcher._stop_consciousness_observer()
    foreign.stop.assert_not_awaited()


class OwnedRegistry(Registry):
    def __init__(self):
        self.entries = {}

    async def register_service(self, name, instance, **kwargs):
        self.entries[name] = SimpleNamespace(instance=instance)
        return True

    def get_service_info(self, name):
        return self.entries.get(name)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "replacement",
    ["temporal_observer", "consciousness_core", "memory_system", "missing"],
)
async def test_replacement_reports_only_original_cache(monkeypatch, replacement):
    # Aetherra imports
    from Aetherra.consciousness.runtime_observer import ConsciousnessObserver
    from Aetherra.consciousness.temporal_observer import TemporalObserver
    from aetherra_os_launcher import MemoryAdapter

    launcher = AetherraOSLauncher()
    registry = launcher.service_registry = OwnedRegistry()
    backend = SimpleNamespace(core_memory=SimpleNamespace(conn=object()))
    memory = launcher.systems["memory"] = MemoryAdapter(backend)
    monkeypatch.setattr(memory, "_checkpoint_backend", lambda: backend)
    monkeypatch.setattr(memory, "drain_temporal_history", lambda timeout: True)
    monkeypatch.setattr(TemporalObserver, "start", lambda self: True)
    monkeypatch.setattr(ConsciousnessObserver, "start", lambda self: True)
    await registry.register_service("memory_system", backend)
    config = {
        "consciousness_enabled": True,
        "temporal_observer": {
            "enabled": True,
            "history_id": "b" * 32,
            "start_mode": "create",
        },
    }
    await launcher._start_consciousness_observer(config)
    collector = registry.entries["temporal_observer"].instance
    assert launcher._temporal_source._temporal_enabled
    assert collector._owned()
    monkeypatch.setattr(
        memory,
        "_checkpoint_backend",
        Mock(side_effect=AssertionError("private memory callback")),
    )
    foreign = Mock()
    if replacement == "missing":
        del registry.entries["temporal_observer"]
    else:
        registry.entries[replacement].instance = foreign
    metrics = collect_temporal_runtime_metrics(registry)
    assert metrics["temporal_runtime_state"] == (
        "missing" if replacement == "missing" else "unavailable"
    )
    assert metrics["temporal_selected_head_record_id"] is None
    foreign.get_runtime_status.assert_not_called()
    memory._checkpoint_backend.assert_not_called()
    await launcher._stop_consciousness_observer()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ({"enabled": True}, "config_invalid"),
        (
            {"enabled": True, "history_id": "b" * 32, "start_mode": "create"},
            "memory_not_ready",
        ),
    ],
)
async def test_temporal_failure_does_not_block_core(monkeypatch, config, expected):
    # Aetherra imports
    from Aetherra.consciousness.runtime_observer import ConsciousnessObserver

    launcher = AetherraOSLauncher()
    registry = launcher.service_registry = OwnedRegistry()
    start = Mock(return_value=True)
    monkeypatch.setattr(ConsciousnessObserver, "start", start)
    await launcher._start_consciousness_observer(
        {"consciousness_enabled": True, "temporal_observer": config}
    )
    start.assert_called_once()
    assert registry.get_service_info("temporal_observer") is None
    assert launcher._temporal_source.get_runtime_status()["runtime_state"] != "blocked"
    metrics = collect_temporal_runtime_metrics(registry)
    assert metrics["temporal_last_error_code"] == expected
    await launcher._stop_consciousness_observer()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "marker"),
    [("_graceful_shutdown", True), ("_emergency_shutdown", False), ("orderly", True)],
)
async def test_shutdown_paths_close_before_core_and_use_separate_budgets(path, marker):
    # Standard library imports
    import time

    launcher = AetherraOSLauncher()
    sequence = []

    class Core:
        async def stop(self, **kwargs):
            sequence.append(("core", kwargs["deadline"] - time.monotonic()))

        def get_runtime_status(self):
            return {}

    class Temporal:
        def close_observation_admission(self):
            sequence.append(("close", None))

        async def stop(self, **kwargs):
            sequence.append(("temporal", kwargs["deadline"] - time.monotonic()))
            assert kwargs["save_history"] is marker
            return True

    launcher._temporal_source = Core()
    launcher._temporal_observer = Temporal()
    if path == "orderly":
        await launcher._stop_consciousness_observer(save_checkpoint=True)
    else:
        await getattr(launcher, path)()
    assert [name for name, _ in sequence] == ["close", "core", "temporal"]
    assert 1.8 < sequence[1][1] <= 2
    assert 0.8 < sequence[2][1] <= 1


@pytest.mark.asyncio
@pytest.mark.parametrize("collector_failure", [False, True])
async def test_idle_original_memory_is_drained_even_after_collector_exception(
    collector_failure,
):
    launcher = AetherraOSLauncher()
    memory = launcher._temporal_memory = Mock()
    memory.temporal_history_pending.return_value = False
    memory.drain_temporal_history.return_value = True
    launcher._temporal_registration_expected = True
    temporal = launcher._temporal_observer = Mock()
    temporal.stop = AsyncMock(return_value=True)
    launcher.systems["memory"] = Mock()
    if collector_failure:
        temporal.stop.side_effect = RuntimeError("collector failure")
        with pytest.raises(RuntimeError, match="collector failure"):
            await launcher._stop_consciousness_observer()
    else:
        await launcher._stop_consciousness_observer()
    memory.drain_temporal_history.assert_called_once()
    launcher.systems["memory"].drain_temporal_history.assert_not_called()


@pytest.mark.asyncio
async def test_admission_exception_still_stops_core_and_suppresses_marker():
    launcher = AetherraOSLauncher()
    launcher._temporal_source = SimpleNamespace(
        stop=AsyncMock(), get_runtime_status=lambda: {}
    )
    temporal = launcher._temporal_observer = Mock()
    temporal.close_observation_admission.side_effect = RuntimeError("admission failure")
    temporal.stop = AsyncMock(return_value=False)
    with pytest.raises(RuntimeError, match="temporal_shutdown_pending"):
        await launcher._stop_consciousness_observer(save_checkpoint=True)
    launcher._temporal_source.stop.assert_awaited_once()
    assert temporal.stop.await_args.kwargs["save_history"] is False


def test_default_launcher_does_not_import_temporal_engine(tmp_path):
    # Standard library imports
    import os
    import subprocess
    import sys

    code = """
import asyncio
import sys
from aetherra_os_launcher import AetherraOSLauncher
launcher = AetherraOSLauncher()
asyncio.run(launcher._start_consciousness_observer({}))
assert 'Aetherra.consciousness.quantum.temporal_consciousness_system' not in sys.modules
assert not any(name.startswith('Aetherra.consciousness.quantum.') for name in sys.modules)
assert not launcher._temporal_observer.get_status()['thread_alive']
"""
    subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        env={**os.environ, "AETHERRA_WORKSPACE_ROOT": str(tmp_path)},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("fault", ["constructor", "binding"])
@pytest.mark.parametrize("enabled", [False, True])
async def test_temporal_setup_exception_preserves_core(monkeypatch, fault, enabled):
    # Aetherra imports
    from Aetherra.consciousness import temporal_observer
    from Aetherra.consciousness.runtime_observer import ConsciousnessObserver

    launcher = AetherraOSLauncher()
    registry = launcher.service_registry = OwnedRegistry()
    config = {"consciousness_enabled": True}
    if enabled:
        config["temporal_observer"] = {
            "enabled": True,
            "history_id": "b" * 32,
            "start_mode": "create",
        }
    failure = Mock(side_effect=RuntimeError("synthetic fault"))
    if fault == "constructor":
        monkeypatch.setattr(temporal_observer, "TemporalObserver", failure)
    else:
        monkeypatch.setattr(hub_state, "bind_temporal_status", failure)
    started = []
    monkeypatch.setattr(
        ConsciousnessObserver, "start", lambda self: started.append(self) or True
    )
    await launcher._start_consciousness_observer(config)
    assert started == [registry.get_service_info("consciousness_core").instance]
    assert registry.get_service_info("temporal_observer") is None
    assert launcher._consciousness_task is not None
    await launcher._stop_consciousness_observer()


@pytest.mark.asyncio
@pytest.mark.parametrize("fault", ["reject", "raise", "true_without_registration"])
async def test_temporal_rejected_registration_is_blocked(monkeypatch, fault):
    # Aetherra imports
    from Aetherra.consciousness.runtime_observer import ConsciousnessObserver
    from Aetherra.consciousness.temporal_observer import TemporalObserver

    launcher = AetherraOSLauncher()
    registry = launcher.service_registry = OwnedRegistry()
    register = registry.register_service

    async def reject(name, instance, **kwargs):
        if name == "temporal_observer":
            if fault == "raise":
                raise RuntimeError("synthetic fault")
            return fault == "true_without_registration"
        return await register(name, instance, **kwargs)

    monkeypatch.setattr(registry, "register_service", reject)
    monkeypatch.setattr(launcher, "_temporal_memory_owned", lambda: True)
    monkeypatch.setattr(ConsciousnessObserver, "start", lambda self: True)
    start = Mock()
    monkeypatch.setattr(TemporalObserver, "start", start)
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
    metrics = collect_temporal_runtime_metrics(registry)
    assert metrics["temporal_runtime_state"] == "blocked"
    assert metrics["temporal_last_error_code"] == "unavailable"
    assert not launcher._temporal_registration_expected
    assert "temporal_observer" not in launcher.systems
    start.assert_not_called()
    await launcher._stop_consciousness_observer()


@pytest.mark.asyncio
async def test_constructor_failure_preserves_preexisting_foreign_core(monkeypatch):
    # Aetherra imports
    from Aetherra.consciousness import temporal_observer

    launcher = AetherraOSLauncher()
    launcher.service_registry = OwnedRegistry()
    foreign = SimpleNamespace(stop=AsyncMock(), get_runtime_status=lambda: {})
    launcher.systems["consciousness_core"] = foreign
    monkeypatch.setattr(
        temporal_observer,
        "TemporalObserver",
        Mock(side_effect=RuntimeError("synthetic fault")),
    )
    await launcher._start_consciousness_observer({"consciousness_enabled": True})
    await launcher._stop_consciousness_observer()
    foreign.stop.assert_not_awaited()


@pytest.mark.asyncio
async def test_legacy_caller_can_stop_existing_core_before_startup_evaluation():
    launcher = AetherraOSLauncher()
    legacy = SimpleNamespace(stop=AsyncMock(), get_runtime_status=lambda: {})
    launcher.systems["consciousness_core"] = legacy
    await launcher._stop_consciousness_observer()
    legacy.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_temporal_thread_start_refusal_settles_original_memory(monkeypatch):
    # Standard library imports
    import threading

    # Aetherra imports
    from Aetherra.consciousness.runtime_observer import ConsciousnessObserver
    from aetherra_os_launcher import MemoryAdapter

    launcher = AetherraOSLauncher()
    registry = launcher.service_registry = OwnedRegistry()
    backend = SimpleNamespace(core_memory=SimpleNamespace(conn=object()))
    memory = launcher.systems["memory"] = MemoryAdapter(backend)
    drain = Mock(return_value=True)
    monkeypatch.setattr(memory, "_checkpoint_backend", lambda: backend)
    monkeypatch.setattr(memory, "drain_temporal_history", drain)
    monkeypatch.setattr(ConsciousnessObserver, "start", lambda self: True)
    await registry.register_service("memory_system", backend)
    with monkeypatch.context() as start:
        refused = Mock(side_effect=RuntimeError("thread start refused"))
        start.setattr(threading.Thread, "start", refused)
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
    refused.assert_called_once()
    status = launcher._get_temporal_runtime_status()
    assert status["runtime_state"] == "blocked"
    assert status["last_error_code"] == "unavailable"
    assert status["thread_alive"] is False
    assert status["outstanding"] is False
    foreign = launcher.systems["memory"] = Mock()
    for _ in range(2):
        await asyncio.wait_for(launcher._stop_consciousness_observer(), timeout=2)
    assert drain.called
    assert not foreign.mock_calls


def test_subsystem_snapshot_keeps_unregistered_core_and_blocked_temporal(monkeypatch):
    # Aetherra imports
    from Aetherra.runtime_ui import snapshot

    registry = Registry()
    monkeypatch.setattr(
        "aetherra_service_registry.get_existing_service_registry", lambda: registry
    )
    monkeypatch.setattr(snapshot, "_guardian_status", lambda observed_at: {})
    blocked = {"runtime_state": "blocked", "last_error_code": "config_invalid"}
    monkeypatch.setattr(
        hub_state, "temporal_status_provider", Mock(return_value=lambda: blocked)
    )
    core = snapshot.collect_runtime_ui_system_status()["consciousness"]
    assert core["status"] == "unknown"
    assert core["metrics"]["available"] is False
    assert core["metrics"]["evidence"] == "service_unregistered"
    assert core["metrics"]["temporal_runtime_state"] == "blocked"
    assert core["metrics"]["temporal_last_error_code"] == "config_invalid"


def test_temporal_successful_start_publishes_liveness(monkeypatch):
    # Standard library imports
    import threading

    # Aetherra imports
    from Aetherra.consciousness.temporal_observer import TemporalObserver

    observer = TemporalObserver(
        None,
        None,
        settings={"enabled": True},
        local_owned=lambda: True,
        readiness=lambda: None,
    )
    release = threading.Event()
    entered = threading.Event()
    original = observer._run

    def controlled_worker():
        entered.set()
        release.wait(3)
        original()

    monkeypatch.setattr(observer, "_run", controlled_worker)
    try:
        assert observer.start()
        assert entered.wait(2)
        assert observer.get_status()["thread_alive"]
    finally:
        observer.close_observation_admission()
        release.set()
        assert asyncio.run(observer.stop())
    assert not observer.get_status()["thread_alive"]
