"""C1 lifecycle owns an optional observer, never chat or execution authority."""

# Standard library imports
import asyncio
import json
import threading
import time

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.core.types import Event


@pytest.fixture
def observer_profile(monkeypatch, tmp_path):
    policy = tmp_path / "policy"
    policy.mkdir()
    for name, value in {
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(policy),
        "AETHERRA_GUARDIAN_POLICY": str(policy / "guardian.json"),
        "AETHERRA_GUARDIAN_STATE_DIR": str(tmp_path / "guardian"),
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_GUARDIAN_ENABLED": "1",
        "AETHERRA_GUARDIAN_REQUIRE_POLICY": "1",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_SIGNING_STRICT": "1",
        "AETHERRA_SCRIPT_VERIFY_STRICT": "1",
        "AETHERRA_AUDIT": "1",
        "AETHERRA_SKIP_DOTENV": "1",
    }.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    policy_file = policy / "guardian.json"
    policy_file.write_text(
        json.dumps(
            {
                "version": 1,
                "default": "deny",
                "allow": [
                    {
                        "requester": "consciousness:core",
                        "subsystem": "consciousness",
                        "action": [
                            "consciousness.micro_reflection_update",
                            "consciousness.macro_reflection_update",
                        ],
                    }
                ],
            }
        )
    )
    return policy_file


def _module():
    # Aetherra imports
    from Aetherra.consciousness import runtime_observer

    return runtime_observer


async def _until(observer, predicate):
    for _ in range(150):
        status = observer.get_runtime_status()
        if predicate(status):
            return status
        await asyncio.sleep(0.02)
    raise AssertionError(observer.get_runtime_status())


@pytest.mark.parametrize("config", [{}, {"consciousness_enabled": False}])
def test_disabled_config_does_not_honor_ambient_autonomy(config, monkeypatch):
    monkeypatch.delenv("AETHERRA_CONSCIOUSNESS_ENABLED", raising=False)
    monkeypatch.setenv("AETHERRA_AUTONOMY_MODE", "autopilot")
    assert _module().observer_settings(config) is None


@pytest.mark.parametrize(
    "config",
    [
        {"consciousness_enabled": "false"},
        {"consciousness_enabled": True, "consciousness_mode": "assist"},
        {"consciousness_enabled": True, "consciousness_mode": "suggest"},
        {"consciousness_enabled": True, "consciousness_tick_hz": float("nan")},
        {"consciousness_enabled": True, "consciousness_tick_hz": 0},
        {"consciousness_enabled": True, "consciousness_tick_hz": True},
    ],
)
def test_invalid_or_acting_configuration_is_rejected(config):
    with pytest.raises(ValueError, match="consciousness_config_invalid"):
        _module().observer_settings(config)


@pytest.mark.asyncio
async def test_real_observer_processes_events_and_stops_independently(observer_profile):
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [
            Event(
                "svc.health",
                {"service": "memory_system", "status": "healthy"},
                source="runtime",
            )
        ],
        tick_interval=0.2,
    )
    try:
        observer.start()
        status = await _until(observer, lambda s: s["ticks_completed"] >= 2)
        assert status["runtime_state"] == "running"
        assert status["events_processed"] >= 2
        assert status["persistence_enabled"] is False
        assert status["action_execution_enabled"] is False
        stream = observer.get_think_stream()
        assert stream["events_processed"] == status["events_processed"]
        assert stream["autonomy_mode"] == "observe"
        assert stream["tick_id"] >= 2
    finally:
        await observer.stop()
    assert observer.get_runtime_status()["runtime_state"] == "stopped"
    assert observer.get_runtime_status()["thread_alive"] is False
    assert observer.get_think_stream()["status"] == "stopped"


@pytest.mark.asyncio
async def test_denied_reflection_has_no_completed_tick_or_retry(observer_profile):
    observer_profile.write_text(json.dumps({"version": 1, "default": "deny"}))
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None, observations=lambda: [], tick_interval=0.2
    )
    try:
        observer.start()
        status = await _until(observer, lambda s: s["runtime_state"] == "blocked")
        assert status["ticks_attempted"] == 1
        assert status["ticks_completed"] == 0
        assert status["last_tick_at"] is None
        assert status["think_stream_available"] is False
        await asyncio.sleep(0.25)
        assert observer.get_runtime_status()["ticks_attempted"] == 1
        assert observer.get_think_stream()["status"] == "blocked"
    finally:
        await observer.stop()


@pytest.mark.asyncio
async def test_policy_revocation_blocks_further_ticks(observer_profile, monkeypatch):
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None, observations=lambda: [], tick_interval=0.2
    )
    try:
        observer.start()
        await _until(observer, lambda s: s["ticks_completed"] >= 1)
        monkeypatch.setenv("AETHERRA_GUARDIAN_ENABLED", "0")
        status = await _until(observer, lambda s: s["runtime_state"] == "blocked")
        completed = status["ticks_completed"]
        await asyncio.sleep(0.25)
        assert observer.get_runtime_status()["ticks_completed"] == completed
        assert observer.get_think_stream()["status"] == "blocked"
    finally:
        await observer.stop()


@pytest.mark.asyncio
async def test_blocked_tick_does_not_block_event_loop_or_claim_stopped(
    observer_profile, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    entered, release = threading.Event(), threading.Event()
    real_tick = ConsciousnessCore.tick

    def slow_tick(core):
        entered.set()
        release.wait(5)
        real_tick(core)

    monkeypatch.setattr(ConsciousnessCore, "tick", slow_tick)
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None, observations=lambda: [], tick_interval=0.2
    )
    try:
        observer.start()
        await _until(observer, lambda s: entered.is_set())
        before = time.monotonic()
        await asyncio.sleep(0.02)
        await observer.stop(timeout=0.05)
        assert time.monotonic() - before < 0.5
        assert observer.get_runtime_status()["runtime_state"] == "stopping"
        assert observer.get_runtime_status()["thread_alive"] is True
        assert observer.start() is False
        release.set()
        await _until(observer, lambda s: not s["thread_alive"])
        assert observer.get_runtime_status()["runtime_state"] == "stopped"
        assert observer.get_runtime_status()["ticks_completed"] == 0
        assert observer.get_think_stream()["status"] == "stopped"
    finally:
        release.set()
        await observer.stop()


@pytest.mark.asyncio
async def test_missing_core_dependencies_never_construct_observer_core(
    observer_profile, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    def unexpected(*args, **kwargs):
        raise AssertionError("Core must not be constructed before dependencies")

    monkeypatch.setattr(ConsciousnessCore, "__init__", unexpected)
    observer = _module().ConsciousnessObserver(
        readiness=lambda: "core_not_ready", observations=lambda: []
    )
    observer.start()
    status = await _until(observer, lambda s: s["runtime_state"] == "blocked")
    assert status["ticks_attempted"] == status["ticks_completed"] == 0
    await observer.stop()


@pytest.mark.asyncio
async def test_launcher_observer_opt_out_creates_no_resources(monkeypatch):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    monkeypatch.delenv("AETHERRA_CONSCIOUSNESS_ENABLED", raising=False)
    launcher = AetherraOSLauncher()
    await launcher._start_consciousness_observer({})
    assert "consciousness_core" not in launcher.systems
    assert launcher._consciousness_task is None
    assert launcher._perception_adapters == []


@pytest.mark.asyncio
async def test_launcher_starts_after_activation_and_stop_leaves_core_alive(
    observer_profile, monkeypatch
):
    # Standard library imports
    from types import SimpleNamespace

    # Aetherra imports
    import aetherra_service_registry as registry_module
    from aetherra_os_launcher import AetherraOSLauncher

    rules = json.loads(observer_profile.read_text())
    rules["allow"].append(
        {
            "requester": "service_registry",
            "subsystem": "service_registry",
            "action": "service_registry.*",
        }
    )
    observer_profile.write_text(json.dumps(rules))
    (observer_profile.parent / "capabilities.json").write_text(
        json.dumps(
            {
                "allow": {
                    "service_registry": [
                        "registry:register",
                        "registry:unregister",
                        "registry:status",
                        "registry:heartbeat",
                        "registry:broadcast",
                    ]
                }
            }
        )
    )
    registry = registry_module.AetherraServiceRegistry()
    registry._running = True
    monkeypatch.setattr(registry_module, "_service_registry", registry)
    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    order = []

    class Memory:
        async def activate(self):
            order.append("memory")

    class Engine:
        async def wake_up(self):
            order.append("engine")

        async def process_message(self, text):
            return {"content": text}

    memory, engine = Memory(), Engine()
    hub = SimpleNamespace(is_running=lambda: True)
    kernel = SimpleNamespace(running=True, get_status=lambda: {"running": True})
    launcher.systems.update(memory=memory, aetherra=engine, aetherra_hub=hub)
    launcher.kernel_loop = kernel
    launcher._presence_owned_hub = hub
    for name, obj in [
        ("memory_system", memory),
        ("aetherra_engine", engine),
        ("aetherra_hub", hub),
        ("kernel_loop", kernel),
    ]:
        assert await registry.register_service(name, obj)
    try:
        await launcher._activate_systems(
            {"quiet": True, "consciousness_enabled": True, "consciousness_tick_hz": 5}
        )
        observer = launcher.systems["consciousness_core"]
        await _until(
            observer,
            lambda s: (
                s["ticks_completed"] >= 1
                and registry.get_service("consciousness_core") is observer
            ),
        )
        assert order == ["memory", "engine"]
        assert registry.get_service("consciousness_core") is observer
        assert launcher._perception_adapters == []
        ledger = observer_profile.parent.parent / ".aetherra/security/audit.jsonl"

        def status_audits():
            rows = [json.loads(line) for line in ledger.read_text().splitlines()]
            return sum(
                row.get("details", {}).get("intent", {}).get("action")
                == "service_registry.status_update"
                and row["details"]["intent"]["metadata"]["service_name"]
                == "consciousness_core"
                for row in rows
            )

        first_audits = status_audits()
        await asyncio.sleep(1.25)
        assert status_audits() == first_audits  # unchanged status is coalesced
        await launcher._stop_consciousness_observer()
        assert observer.get_runtime_status()["runtime_state"] == "stopped"
        assert kernel.running is True
        assert registry._running is True
        assert await engine.process_message("still available") == {
            "content": "still available"
        }
    finally:
        await launcher._stop_consciousness_observer()
        registry._running = False


@pytest.mark.parametrize("value", [None, 10**400])
def test_explicit_invalid_config_cannot_inherit_opt_in_or_escape(value, monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    config = (
        {"consciousness_enabled": None}
        if value is None
        else {"consciousness_enabled": True, "consciousness_tick_hz": value}
    )
    with pytest.raises(ValueError, match="consciousness_config_invalid"):
        _module().observer_settings(config)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "config", [{"consciousness_enabled": True}, {"consciousness_enabled": None}]
)
async def test_launcher_preserves_existing_foreign_registry_owner(
    observer_profile, config
):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher
    from aetherra_service_registry import AetherraServiceRegistry

    rules = json.loads(observer_profile.read_text())
    rules["allow"].append(
        {
            "requester": "service_registry",
            "subsystem": "service_registry",
            "action": "service_registry.*",
        }
    )
    observer_profile.write_text(json.dumps(rules))
    registry = AetherraServiceRegistry()
    foreign = object()
    assert await registry.register_service("consciousness_core", foreign)
    original_info = registry.get_service_info("consciousness_core")
    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    try:
        await launcher._start_consciousness_observer(config)
        assert registry.get_service_info("consciousness_core") is original_info
        assert original_info.instance is foreign
        assert "consciousness_core" not in launcher.systems
        assert launcher._consciousness_task is None
    finally:
        await launcher._stop_consciousness_observer()


@pytest.mark.asyncio
@pytest.mark.parametrize("shape", ["real_adapters", "lookalike", "foreign"])
async def test_readiness_matches_normal_launcher_adapter_registration(
    observer_profile, shape
):
    # Standard library imports
    from types import SimpleNamespace

    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher, EngineAdapter, MemoryAdapter
    from aetherra_service_registry import AetherraServiceRegistry

    rules = json.loads(observer_profile.read_text())
    rules["allow"].append(
        {
            "requester": "service_registry",
            "subsystem": "service_registry",
            "action": "service_registry.*",
        }
    )
    observer_profile.write_text(json.dumps(rules))
    registry = AetherraServiceRegistry()
    registry._running = True
    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    memory_impl, engine_impl = object(), object()
    hub = SimpleNamespace(is_running=lambda: True)
    kernel = SimpleNamespace(get_status=lambda: {"running": True})
    launcher.kernel_loop = kernel
    launcher._presence_owned_hub = hub
    launcher.systems.update(
        memory=MemoryAdapter(memory_impl),
        aetherra=EngineAdapter(engine_impl),
        aetherra_hub=hub,
    )
    for name, instance in [
        ("memory_system", memory_impl),
        ("aetherra_engine", engine_impl),
        ("aetherra_hub", hub),
        ("kernel_loop", kernel),
    ]:
        assert await registry.register_service(name, instance)
    if shape == "lookalike":
        launcher.systems["memory"] = SimpleNamespace(impl=memory_impl)
    elif shape == "foreign":
        launcher.systems["aetherra"] = EngineAdapter(object())
    assert launcher._consciousness_core_readiness() == (
        None if shape == "real_adapters" else "core_not_ready"
    )


@pytest.mark.asyncio
async def test_temporal_projection_is_opt_in_and_absent_before_completed_tick(
    observer_profile,
):
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None, observations=lambda: [], tick_interval=0.2
    )
    assert hasattr(observer, "get_temporal_observation")
    assert observer.get_temporal_observation() is None
    try:
        observer.start()
        await _until(observer, lambda s: s["ticks_completed"] >= 1)
        assert observer.get_temporal_observation() is None
    finally:
        await observer.stop()


@pytest.mark.asyncio
async def test_temporal_projection_contains_only_detached_completed_counts(
    observer_profile,
):
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [
            Event("svc.health", {"service": "private-service", "restarts_1h": 6})
        ],
        tick_interval=10,
        temporal_observation_enabled=True,
    )
    assert observer.get_temporal_observation() is None
    try:
        observer.start()
        await _until(observer, lambda s: s["ticks_completed"] == 1)
        value = observer.get_temporal_observation()
        assert set(value) == {
            "session_id",
            "session_started_at_unix_s",
            "sequence",
            "observed_at_unix_s",
            "observed_uptime_s",
            "working_memory_count",
            "active_intention_count",
            "focus_count",
        }
        assert value["sequence"] == 1
        assert value["working_memory_count"] == 1
        assert value["active_intention_count"] == 1
        assert value["focus_count"] == 1
        assert len(value["session_id"]) == 32
        assert value["observed_at_unix_s"] >= value["session_started_at_unix_s"]
        assert value["observed_uptime_s"] >= 0
        assert "private" not in json.dumps(value)
        value["working_memory_count"] = 999
        assert observer.get_temporal_observation()["working_memory_count"] == 1
    finally:
        await observer.stop()
    assert observer.get_temporal_observation() is None


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["failed", "stopped", "readiness_lost"])
async def test_temporal_projection_never_publishes_an_unaccepted_tick(
    observer_profile, monkeypatch, outcome
):
    # Aetherra imports
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    entered, release = threading.Event(), threading.Event()
    ready = [True]
    original = ConsciousnessCore.tick

    def interrupted_tick(core):
        original(core)
        entered.set()
        release.wait(5)
        if outcome == "failed":
            raise RuntimeError("private-failure")
        if outcome == "readiness_lost":
            ready[0] = False

    monkeypatch.setattr(ConsciousnessCore, "tick", interrupted_tick)
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None if ready[0] else "core_not_ready",
        observations=lambda: [],
        tick_interval=0.2,
        temporal_observation_enabled=True,
    )
    try:
        observer.start()
        await _until(observer, lambda s: entered.is_set())
        assert observer.get_temporal_observation() is None
        if outcome == "stopped":
            await observer.stop(timeout=0.01)
        release.set()
        await _until(observer, lambda s: not s["thread_alive"])
        assert observer.get_temporal_observation() is None
        assert observer.get_runtime_status()["ticks_completed"] == 0
    finally:
        release.set()
        await observer.stop()


@pytest.mark.asyncio
async def test_temporal_projection_uses_monotonic_source_freshness(
    observer_profile, monkeypatch
):
    # Standard library imports
    from types import SimpleNamespace

    observer = _module().ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [],
        tick_interval=10,
        temporal_observation_enabled=True,
    )
    try:
        observer.start()
        await _until(observer, lambda s: s["ticks_completed"] == 1)
        value = observer.get_temporal_observation()
        clock = time.monotonic()
        with monkeypatch.context() as patch:
            patch.setattr(
                _module(),
                "time",
                SimpleNamespace(
                    monotonic=lambda: clock + 31,
                    time=lambda: value["observed_at_unix_s"],
                ),
            )
            assert observer.get_temporal_observation() is None
        # A backwards wall clock cannot make a fresh monotonic observation stale.
        with monkeypatch.context() as patch:
            patch.setattr(
                _module(),
                "time",
                SimpleNamespace(
                    monotonic=time.monotonic,
                    time=lambda: 0.0,
                ),
            )
            assert observer.get_temporal_observation() == value
    finally:
        await observer.stop()


@pytest.mark.parametrize("enabled", [1, "1", None])
def test_temporal_projection_configuration_rejects_non_boolean(enabled):
    with pytest.raises(ValueError, match="consciousness_config_invalid"):
        _module().ConsciousnessObserver(
            readiness=lambda: None,
            observations=lambda: [],
            temporal_observation_enabled=enabled,
        )


@pytest.mark.asyncio
async def test_temporal_projection_rechecks_readiness_after_checkpoint_freeze(
    observer_profile, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    ready = [True]
    original = ConsciousnessCore.export_observer_checkpoint

    def revoke_after_freeze(core, handle):
        result = original(core, handle)
        ready[0] = False
        return result

    monkeypatch.setattr(
        ConsciousnessCore, "export_observer_checkpoint", revoke_after_freeze
    )
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None if ready[0] else "core_not_ready",
        observations=lambda: [],
        tick_interval=10,
        continuity_enabled=True,
        checkpoint_store=object(),
        temporal_observation_enabled=True,
    )
    try:
        observer.start()
        await _until(observer, lambda s: s["runtime_state"] in {"blocked", "running"})
        assert observer.get_temporal_observation() is None
        assert observer.get_runtime_status()["ticks_completed"] == 0
    finally:
        await observer.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("delay", [5, 31])
async def test_temporal_projection_does_not_refresh_timestamp_after_slow_freeze(
    observer_profile, monkeypatch, delay
):
    # Standard library imports
    from types import SimpleNamespace

    # Aetherra imports
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    offset = [0.0]
    original = ConsciousnessCore.export_observer_checkpoint

    def delayed_freeze(core, handle):
        result = original(core, handle)
        offset[0] = delay
        return result

    monkeypatch.setattr(ConsciousnessCore, "export_observer_checkpoint", delayed_freeze)
    monkeypatch.setattr(
        _module(),
        "time",
        SimpleNamespace(
            time=time.time,
            monotonic=lambda: time.monotonic() + offset[0],
        ),
    )
    # Freeze scheduling after one real tick/export so the evidence cannot be
    # replaced by a second observation during the simulated delay.
    monkeypatch.setattr(
        _module().ConsciousnessObserver,
        "_wait_for_tick",
        lambda observer, deadline: observer._stop.wait(5),
    )
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [],
        tick_interval=10,
        continuity_enabled=True,
        checkpoint_store=object(),
        temporal_observation_enabled=True,
    )
    try:
        observer.start()
        await _until(observer, lambda s: s["ticks_completed"] == 1)
        value = observer.get_temporal_observation()
        if delay == 31:
            assert value is None
        else:
            assert value is not None
            wall_elapsed = (
                value["observed_at_unix_s"] - value["session_started_at_unix_s"]
            )
            assert abs(value["observed_uptime_s"] - wall_elapsed) < 1
    finally:
        await observer.stop()


@pytest.mark.asyncio
async def test_temporal_projection_refuses_explicitly_lost_local_ownership(
    observer_profile,
):
    observer = _module().ConsciousnessObserver(
        readiness=lambda: None,
        local_owned=lambda: False,
        observations=lambda: [],
        tick_interval=10,
        temporal_observation_enabled=True,
    )
    try:
        observer.start()
        await _until(observer, lambda s: s["runtime_state"] in {"blocked", "running"})
        assert observer.get_temporal_observation() is None
    finally:
        await observer.stop()
