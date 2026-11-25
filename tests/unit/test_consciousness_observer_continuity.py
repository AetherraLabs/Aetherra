"""Observer continuity is explicit, bounded, and independent of cached live ticks."""

# Standard library imports
import asyncio
import copy
import threading
import time
from concurrent.futures import Future
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness import runtime_observer as runtime
from tests.unit import test_checkpoint_session as recovery
from tests.unit import test_consciousness_observer_lifecycle as lifecycle_tests

observer_profile = lifecycle_tests.observer_profile

HANDLE = "a" * 32


def payload():
    return {
        "schema": 1,
        "checkpoint_id": HANDLE,
        "owner": "consciousness:observer",
        "scope": "observer_continuity:v1",
        "captured_at": 123.0,
        "qualia": {
            "valence": -0.3,
            "arousal": 0.2,
            "certainty": 0.3,
            "curiosity": 0.4,
            "care": 0.5,
            "fatigue": 0.6,
        },
        "trust": {
            "half_life_s": 3600.0,
            "subsystems": [
                {
                    "name": "memory",
                    "score": 40.0,
                    "last_event_ts": 123.0,
                    "history": [60.0, 40.0],
                }
            ],
        },
    }


class CheckpointStore:
    """I/O boundary double; actual observer/Core/codec execute normally."""

    def __init__(self, *, load_error=None, pending_load=False, pending_save=False):
        self.load_error = load_error
        self.pending_load, self.pending_save = pending_load, pending_save
        self.load = Future()
        self.save = Future()
        self.entered = threading.Event()
        self.rows = []
        self.controls = []

    def submit_load_lifecycle_checkpoint(self, **kwargs):
        self.controls.append(kwargs["control"])
        self.entered.set()
        if not self.pending_load:
            if self.load_error:
                # Aetherra imports
                from Aetherra.aetherra_core.memory.lifecycle_checkpoint import (
                    CheckpointError,
                )

                self.load.set_exception(CheckpointError(self.load_error))
            else:
                self.load.set_result(
                    SimpleNamespace(
                        record_id="row-original",
                        checkpoint_id=HANDLE,
                        payload=payload(),
                    )
                )
        return self.load

    def submit_store_lifecycle_checkpoint(self, **kwargs):
        self.controls.append(kwargs["control"])
        self.rows.append(copy.deepcopy(kwargs["payload"]))
        self.entered.set()
        if not self.pending_save:
            self.save.set_result(
                SimpleNamespace(
                    record_id="row-saved",
                    checkpoint_id=kwargs["checkpoint_id"],
                    payload=kwargs["payload"],
                )
            )
        return self.save


async def until(observer, predicate):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        status = observer.get_runtime_status()
        if predicate(status):
            return status
        # A positive delay lets the observer thread progress through audit I/O;
        # sleep(0) only yields to other tasks on this event loop.
        await asyncio.sleep(0.01)
    raise AssertionError(observer.get_runtime_status())


def observer(store=None, **kwargs):
    return runtime.ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [],
        tick_interval=10,
        checkpoint_store=store,
        continuity_enabled=True,
        **kwargs,
    )


@pytest.mark.parametrize(
    "config",
    [
        {"consciousness_continuity": None},
        {"consciousness_continuity": []},
        {"consciousness_continuity": {"enabled": "false"}},
        {"consciousness_continuity": {"enabled": 1}},
        {"consciousness_continuity": {"extra": 1}},
        {"consciousness_continuity": {"restore_checkpoint_id": "A" * 32}},
        {"consciousness_continuity": {"restore_checkpoint_id": True}},
        {"consciousness_continuity": {"enabled": True}},
    ],
)
def test_continuity_config_rejects_implicit_or_malformed_authority(config):
    with pytest.raises(ValueError, match="consciousness_config_invalid"):
        runtime.continuity_settings(config)


def test_default_continuity_is_disabled_without_selected_lineage(monkeypatch):
    monkeypatch.delenv("AETHERRA_CONSCIOUSNESS_ENABLED", raising=False)
    assert runtime.continuity_settings({}) == {
        "enabled": False,
        "restore_checkpoint_id": None,
    }


@pytest.mark.asyncio
async def test_disabled_continuity_never_contacts_checkpoint_store(observer_profile):
    store = CheckpointStore()
    owned = runtime.ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [],
        tick_interval=10,
        checkpoint_store=store,
    )
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    await owned.stop(save_checkpoint=True)
    assert store.controls == []
    assert owned.get_runtime_status()["continuity"]["state"] == "disabled"


@pytest.mark.asyncio
@pytest.mark.parametrize("save", [False, True])
async def test_fresh_lineage_saves_once_only_at_explicit_stop(observer_profile, save):
    store = CheckpointStore()
    owned = observer(store)
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    assert owned.get_runtime_status()["continuity"]["state"] == "fresh"
    assert store.controls == []
    await owned.stop(save_checkpoint=save)
    await owned.stop(save_checkpoint=True)
    status = owned.get_runtime_status()
    assert status["runtime_state"] == "stopped"
    assert len(store.rows) == int(save)
    assert status["continuity"]["state"] == ("saved" if save else "fresh")
    if save:
        assert status["continuity"]["saved_record_id"] == "row-saved"
        assert (
            store.rows[0]["checkpoint_id"]
            == status["continuity"]["saved_checkpoint_id"]
        )
        assert "ticks_completed" not in store.rows[0]


@pytest.mark.asyncio
async def test_restore_is_applied_on_owner_before_first_tick(
    observer_profile, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness.checkpoint import encode_checkpoint
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    entered, release = threading.Event(), threading.Event()
    restored = []
    original_tick = ConsciousnessCore.tick

    def gated_tick(core):
        restored.append(encode_checkpoint(core.export_observer_checkpoint(HANDLE)))
        entered.set()
        assert release.wait(5)
        original_tick(core)

    monkeypatch.setattr(ConsciousnessCore, "tick", gated_tick)
    store = CheckpointStore()
    owned = observer(store, restore_checkpoint_id=HANDLE)
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        status = owned.get_runtime_status()
        assert status["ticks_completed"] == 0
        assert status["continuity"]["state"] == "restored"
        assert status["continuity"]["restored_record_id"] == "row-original"
        assert restored[0]["qualia"] == payload()["qualia"]
        assert restored[0]["trust"] == payload()["trust"]
        await owned.stop(timeout=0, save_checkpoint=True)
    finally:
        release.set()
        await owned.stop()
    assert store.rows == []  # A tick interrupted by stop cannot become a checkpoint.


@pytest.mark.asyncio
@pytest.mark.parametrize("code", ["missing", "invalid", "denied", "audit_failed"])
async def test_failed_restore_latches_and_inhibits_all_writes(observer_profile, code):
    store = CheckpointStore(load_error=code)
    owned = observer(store, restore_checkpoint_id=HANDLE)
    owned.start()
    await until(owned, lambda s: s["runtime_state"] == "blocked")
    await owned.stop(save_checkpoint=True)
    status = owned.get_runtime_status()
    assert status["ticks_attempted"] == 0
    assert status["continuity"]["state"] == "blocked"
    assert status["continuity"]["last_error_code"] == code
    assert store.rows == []


@pytest.mark.asyncio
async def test_cancelled_restore_keeps_worker_owned_and_rejects_late_result(
    observer_profile,
):
    store = CheckpointStore(pending_load=True)
    owned = observer(store, restore_checkpoint_id=HANDLE)
    owned.start()
    assert await asyncio.to_thread(store.entered.wait, 5)
    heartbeat = []

    async def chat():
        heartbeat.append("available")
        return "answer"

    _, answer = await asyncio.gather(
        owned.stop(timeout=0.01, save_checkpoint=True), chat()
    )
    status = owned.get_runtime_status()
    assert answer == "answer"
    assert heartbeat == ["available"]
    assert status["thread_alive"] is True
    assert status["runtime_state"] == "stopping"
    assert status["continuity"]["outstanding"] is True
    assert status["continuity"]["state"] == "uncertain"
    store.load.set_result(
        SimpleNamespace(record_id="row-late", checkpoint_id=HANDLE, payload=payload())
    )
    await owned.stop()
    status = owned.get_runtime_status()
    assert status["continuity"]["state"] == "uncertain"
    assert status["continuity"]["restored_record_id"] is None
    assert status["ticks_attempted"] == 0
    assert store.rows == []


@pytest.mark.asyncio
async def test_save_deadline_never_acknowledges_late_commit_or_retries(
    observer_profile,
):
    store = CheckpointStore(pending_save=True)
    owned = observer(store)
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    await owned.stop(timeout=0.05, save_checkpoint=True)
    status = owned.get_runtime_status()
    assert status["continuity"]["state"] == "uncertain"
    assert status["continuity"]["outstanding"] is True
    assert status["thread_alive"] is True
    store.save.set_result(
        SimpleNamespace(
            record_id="row-late",
            checkpoint_id=store.rows[0]["checkpoint_id"],
            payload=store.rows[0],
        )
    )
    await owned.stop(save_checkpoint=True)
    status = owned.get_runtime_status()
    assert status["continuity"]["saved_record_id"] is None
    assert status["continuity"]["state"] == "uncertain"
    assert len(store.rows) == 1


@pytest.mark.asyncio
async def test_policy_revoked_at_stop_prevents_checkpoint_submission(
    observer_profile, monkeypatch
):
    store = CheckpointStore()
    owned = observer(store)
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    monkeypatch.setenv("AETHERRA_GUARDIAN_ENABLED", "0")
    await owned.stop(save_checkpoint=True)
    assert store.rows == []
    assert owned.get_runtime_status()["continuity"]["state"] == "blocked"


@pytest.mark.asyncio
async def test_failed_tick_cannot_save_last_completed_tick(
    observer_profile, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    def broken(core):
        raise RuntimeError("private diagnostic")

    monkeypatch.setattr(ConsciousnessCore, "tick", broken)
    store = CheckpointStore()
    owned = observer(store)
    owned.start()
    await until(owned, lambda s: s["runtime_state"] == "failed")
    await owned.stop(save_checkpoint=True)
    assert store.rows == []
    assert owned.get_runtime_status()["continuity"]["last_error_code"] == "tick_failed"


def test_adapter_refuses_generic_or_replaced_memory_before_io():
    # Aetherra imports
    from aetherra_os_launcher import MemoryAdapter

    class Generic:
        def submit_load_lifecycle_checkpoint(self, **kwargs):
            raise AssertionError("foreign backend must never receive I/O")

    adapter = MemoryAdapter(Generic())
    with pytest.raises(RuntimeError, match="checkpoint_unavailable"):
        adapter.submit_load_lifecycle_checkpoint(
            owner="consciousness:observer",
            scope="observer_continuity:v1",
            checkpoint_id=HANDLE,
            control=None,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "expected"),
    [("_graceful_shutdown", True), ("_emergency_shutdown", False)],
)
async def test_launcher_requests_save_only_for_explicit_orderly_stop(method, expected):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    launcher = AetherraOSLauncher()
    requests = []

    class Owned:
        async def stop(self, *, save_checkpoint=False, deadline):
            requests.append(save_checkpoint)

        def get_runtime_status(self):
            return {"thread_alive": False, "continuity": {"outstanding": False}}

    launcher.systems["consciousness_core"] = Owned()
    await getattr(launcher, method)()
    assert requests == [expected]


@pytest.mark.asyncio
async def test_pending_checkpoint_prevents_launcher_memory_teardown():
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    launcher = AetherraOSLauncher()

    class Owned:
        async def stop(self, *, save_checkpoint=False, deadline):
            pass

        def get_runtime_status(self):
            return {"thread_alive": True, "continuity": {"outstanding": True}}

    class Memory:
        async def shutdown(self):
            raise AssertionError("Memory remains owned until observer drains")

    launcher.systems.update(consciousness_core=Owned(), memory=Memory())
    with pytest.raises(RuntimeError, match="consciousness_shutdown_pending"):
        await launcher._graceful_shutdown()


@pytest.mark.asyncio
async def test_restore_deadline_includes_detached_validation(
    observer_profile, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness import checkpoint

    entered, release = threading.Event(), threading.Event()
    now = [100.0]
    real_decode = checkpoint.decode_checkpoint

    def gated_decode(value):
        state = real_decode(value)
        entered.set()
        assert release.wait(5)
        return state

    monkeypatch.setattr(checkpoint, "decode_checkpoint", gated_decode)
    monkeypatch.setattr(
        runtime,
        "time",
        SimpleNamespace(monotonic=lambda: now[0], time=time.time, sleep=time.sleep),
    )
    store = CheckpointStore()
    owned = observer(store, restore_checkpoint_id=HANDLE)
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        now[0] = 102.0
        release.set()
        status = await until(
            owned, lambda s: not s["thread_alive"] or s["ticks_completed"] > 0
        )
        assert status["ticks_attempted"] == 0
        assert status["continuity"]["restored_record_id"] is None
        assert status["continuity"]["state"] == "uncertain"
    finally:
        release.set()
        await owned.stop()


@pytest.mark.asyncio
async def test_launcher_drains_owned_checkpoint_worker_before_memory_shutdown():
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    launcher = AetherraOSLauncher()
    drained = []

    class Store:
        def drain_lifecycle_checkpoints(self, *, timeout):
            drained.append(True)
            return False

    class Owned:
        _checkpoint_store = Store()

        async def stop(self, *, save_checkpoint=False, deadline):
            pass

        def get_runtime_status(self):
            return {
                "thread_alive": False,
                "continuity": {"enabled": True, "outstanding": False},
            }

    launcher.systems["consciousness_core"] = Owned()
    with pytest.raises(RuntimeError, match="consciousness_shutdown_pending"):
        await launcher._graceful_shutdown()
    assert drained == [True]


def test_blocked_continuity_status_never_exposes_private_reason():
    owned = observer(CheckpointStore())
    owned.block("private path and message")
    assert (
        owned.get_runtime_status()["continuity"]["last_error_code"] == "core_not_ready"
    )


@pytest.mark.asyncio
async def test_stale_completed_tick_cannot_be_saved(observer_profile, monkeypatch):
    store = CheckpointStore()
    owned = observer(store)
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    future_wall_time = time.time() + 60
    monkeypatch.setattr(
        runtime,
        "time",
        SimpleNamespace(
            monotonic=time.monotonic, time=lambda: future_wall_time, sleep=time.sleep
        ),
    )
    await owned.stop(save_checkpoint=True)
    assert store.rows == []
    assert owned.get_runtime_status()["continuity"]["state"] == "blocked"
    assert owned.get_runtime_status()["continuity"]["last_error_code"] == "stale"


@pytest.mark.asyncio
async def test_cached_status_reads_do_not_audit_decay_or_mutate_continuity(
    observer_profile,
):
    # Standard library imports
    from hashlib import sha256

    store = CheckpointStore()
    owned = observer(store)
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    ledger = observer_profile.parent.parent / ".aetherra/security/audit.jsonl"
    before = sha256(ledger.read_bytes()).hexdigest()
    for _ in range(10):
        status = owned.get_runtime_status()
        status["continuity"]["saved_record_id"] = "foreign"
        assert owned.get_runtime_status()["continuity"]["saved_record_id"] is None
        assert owned.get_think_stream()["tick_id"] == 1
    assert sha256(ledger.read_bytes()).hexdigest() == before
    assert store.controls == []
    await owned.stop()


@pytest.mark.asyncio
async def test_orderly_stop_during_later_tick_saves_only_frozen_completed_state(
    observer_profile, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness.checkpoint import decode_checkpoint
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    entered, release = threading.Event(), threading.Event()
    real_tick = ConsciousnessCore.tick
    calls = []

    def gated_tick(core):
        calls.append(True)
        if len(calls) == 2:
            entered.set()
            assert release.wait(5)
        real_tick(core)
        for name, value in payload()["qualia"].items():
            setattr(core.qualia, name, value)
        core.self_trust.restore_checkpoint(decode_checkpoint(payload()).trust)
        if len(calls) == 2:
            core.qualia.valence = 0.9

    monkeypatch.setattr(ConsciousnessCore, "tick", gated_tick)
    store = CheckpointStore()
    owned = runtime.ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [],
        tick_interval=0.2,
        checkpoint_store=store,
        continuity_enabled=True,
    )
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        stop = asyncio.create_task(owned.stop(save_checkpoint=True))
        await until(owned, lambda s: s["runtime_state"] == "stopping")
        release.set()
        await stop
        assert len(store.rows) == 1
        assert store.rows[0]["qualia"] == payload()["qualia"]
        assert store.rows[0]["trust"] == payload()["trust"]
        assert owned.get_runtime_status()["ticks_completed"] == 1
    finally:
        release.set()
        await owned.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("save", [False, True])
async def test_blocked_final_policy_recheck_cannot_block_cached_status_or_stop(
    observer_profile, save
):
    entered, release = threading.Event(), threading.Event()

    class RecheckFuture(Future):
        def __init__(self):
            super().__init__()
            self.reads = 0

        def result(self, timeout=None):
            self.reads += 1
            if self.reads == 2:
                entered.set()
                assert release.wait(5)
            return super().result(timeout)

    store = CheckpointStore()
    if save:
        store.save = RecheckFuture()
    else:
        store.load = RecheckFuture()
    owned = observer(store, restore_checkpoint_id=None if save else HANDLE)
    owned.start()
    stop = None
    try:
        if save:
            await until(owned, lambda s: s["ticks_completed"] == 1)
            stop = asyncio.create_task(owned.stop(timeout=0.1, save_checkpoint=True))
        assert await asyncio.to_thread(entered.wait, 5)
        status = await asyncio.wait_for(
            asyncio.to_thread(owned.get_runtime_status), 0.5
        )
        assert status["continuity"]["outstanding"] is True
        if stop is None:
            stop = asyncio.create_task(owned.stop(timeout=0.01))
        await asyncio.wait_for(stop, 0.5)
        assert owned.get_runtime_status()["thread_alive"] is True
        assert owned.get_runtime_status()["continuity"]["state"] == "uncertain"
    finally:
        release.set()
        if stop is not None:
            await stop
        await owned.stop()
    status = owned.get_runtime_status()
    assert status["continuity"]["saved_record_id"] is None
    assert status["continuity"]["restored_record_id"] is None
    assert status["continuity"]["state"] == "uncertain"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exit_kind", "expected"),
    [("cancelled", False), ("failure", False), ("critical", False), ("orderly", True)],
)
async def test_main_loop_classifies_only_orderly_exit_as_save_eligible(
    monkeypatch, exit_kind, expected
):
    # Aetherra imports
    import aetherra_os_launcher as launcher_module

    launcher = launcher_module.AetherraOSLauncher()
    launcher.running = exit_kind != "orderly"

    async def refresh():
        if exit_kind == "cancelled":
            raise asyncio.CancelledError()
        if exit_kind == "failure":
            raise RuntimeError("private internal error")

    async def noop(*args):
        pass

    launcher._refresh_owned_engine_heartbeat = refresh
    launcher._refresh_observation_service_heartbeats = noop
    launcher._write_os_status = noop
    launcher._cleanup_os_status = noop
    launcher.service_registry = SimpleNamespace(_running=False)
    launcher.kernel_loop = SimpleNamespace(running=False)
    monkeypatch.setattr(
        launcher_module,
        "asyncio",
        SimpleNamespace(sleep=noop, CancelledError=asyncio.CancelledError),
    )
    assert await launcher._main_operation_loop() is expected


@pytest.mark.asyncio
async def test_memory_uncertain_commit_remains_uncertain_without_receipt_or_retry(
    observer_profile,
):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.lifecycle_checkpoint import CheckpointError

    class UncertainStore(CheckpointStore):
        def submit_store_lifecycle_checkpoint(self, **kwargs):
            self.rows.append(copy.deepcopy(kwargs["payload"]))
            self.save.set_exception(CheckpointError("uncertain"))
            return self.save

    store = UncertainStore()
    owned = observer(store)
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    await owned.stop(save_checkpoint=True)
    await owned.stop(save_checkpoint=True)
    status = owned.get_runtime_status()["continuity"]
    assert status["state"] == "uncertain"
    assert status["last_error_code"] == "uncertain"
    assert status["saved_record_id"] is None
    assert len(store.rows) == 1


@pytest.mark.asyncio
async def test_monitor_reports_exception_class_without_private_details(caplog):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher
    from aetherra_service_registry import ServiceStatus

    stops = []

    class Owned:
        def get_runtime_status(self):
            return {"runtime_state": "running"}

        async def stop(self, *, save_checkpoint=False):
            stops.append(save_checkpoint)

    owned = Owned()

    class Registry:
        _stale_sec = 30

        def get_service_info(self, name):
            return SimpleNamespace(instance=owned, status=ServiceStatus.HEALTHY)

        async def update_service_status(self, *args, **kwargs):
            raise RuntimeError("private token and path")

    launcher = AetherraOSLauncher()
    launcher.service_registry = Registry()
    await launcher._monitor_consciousness_observer(owned)
    assert stops == [False]
    assert "RuntimeError" in caplog.text
    assert "private" not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("before_admission", [False, True])
async def test_cancelled_stop_abandons_save_and_retains_worker(
    observer_profile, monkeypatch, before_admission
):
    store = CheckpointStore(pending_save=True)
    owned = observer(store)
    entered, release = threading.Event(), threading.Event()
    exchange = owned._checkpoint_exchange

    def held_exchange(**kwargs):
        if before_admission:
            entered.set()
            assert release.wait(5)
        return exchange(**kwargs)

    monkeypatch.setattr(owned, "_checkpoint_exchange", held_exchange)
    owned.start()
    await until(owned, lambda s: s["ticks_completed"] == 1)
    stopping = asyncio.create_task(owned.stop(save_checkpoint=True))
    try:
        await until(
            owned,
            lambda s: entered.is_set() if before_admission else store.entered.is_set(),
        )
        stopping.cancel()
        with pytest.raises(asyncio.CancelledError):
            await stopping
        assert owned.get_runtime_status()["thread_alive"] is True
        assert owned._checkpoint_failed is True
        if store.controls:
            assert store.controls[0].cancelled.is_set()
        release.set()
        if store.rows:
            store.save.set_result(
                SimpleNamespace(
                    record_id="late",
                    checkpoint_id=store.rows[0]["checkpoint_id"],
                    payload=store.rows[0],
                )
            )
        await owned.stop()
        status = owned.get_runtime_status()
        assert status["continuity"]["saved_record_id"] is None
        assert status["continuity"]["state"] == "uncertain"
        assert not status["thread_alive"]
        if before_admission:
            assert not store.rows
    finally:
        release.set()
        if not store.save.done():
            store.save.set_result(
                SimpleNamespace(
                    record_id="late", checkpoint_id=HANDLE, payload=payload()
                )
            )
        await owned.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("method", ["_graceful_shutdown", "_emergency_shutdown"])
async def test_unsupported_checkpoint_backend_does_not_abort_shutdown(
    observer_profile, wrapped, method
):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher, MemoryAdapter

    class Unsupported:
        def drain_lifecycle_checkpoints(self, **kwargs):
            raise AssertionError("foreign backend received checkpoint drain")

        async def shutdown(self):
            pass

    launcher = AetherraOSLauncher()
    backend = Unsupported()
    launcher.systems["memory"] = MemoryAdapter(backend) if wrapped else backend
    await launcher._start_consciousness_observer(
        {
            "consciousness_enabled": True,
            "consciousness_continuity": {"enabled": True},
        }
    )
    owned = launcher.systems["consciousness_core"]
    assert owned.get_runtime_status()["runtime_state"] == "blocked"
    await getattr(launcher, method)()
    assert owned._checkpoint_store is None


memory = recovery.memory
policy = recovery.policy
governed = recovery.governed
database = recovery.database


@pytest.mark.asyncio
async def test_resume_restores_exact_state_before_tick_zero(database, monkeypatch):
    # Aetherra imports
    from Aetherra.consciousness.checkpoint import encode_checkpoint
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore

    _, commits = recovery.seed(database, 2)
    entered, release = threading.Event(), threading.Event()
    at_first_tick = []

    def first_tick(core):
        at_first_tick.append(
            (
                core.tick_count,
                core.total_events_perceived,
                encode_checkpoint(core.export_observer_checkpoint(HANDLE)),
            )
        )
        entered.set()
        assert release.wait(5)

    monkeypatch.setattr(ConsciousnessCore, "tick", first_tick)
    owned = observer(
        database, automatic=recovery.AUTO, recovery_attempt=commits[0].attempt
    )
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 3), owned.get_runtime_status()
        ticks, events, state = at_first_tick[0]
        assert (ticks, events) == (0, 0)
        assert state["qualia"] == recovery.stream.legacy.payload()["qualia"]
        assert state["trust"] == recovery.stream.legacy.payload()["trust"]
        status = owned.get_runtime_status()
        assert status["ticks_completed"] == 0
        continuity = status["continuity"]
        assert continuity["recovery_outcome"] == "committed_superseded"
        assert continuity["selected_checkpoint_id"] == commits[1].head.checkpoint_id
        assert continuity["restored_record_id"] == commits[1].head.record_id
        assert continuity["saved_record_id"] is None
        assert continuity["last_verified_observation_at_unix_s"] == 126
    finally:
        await owned.stop(timeout=0)
        release.set()
        await owned.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("damage", ["missing", "metadata", "denied_inspect"])
async def test_invalid_automatic_recovery_blocks_ticks_and_stop_writes(
    database, policy, damage
):
    _, commits = recovery.seed(database, 1)
    if damage == "missing":
        database.conn.execute("DELETE FROM memories")
    elif damage == "metadata":
        database.conn.execute(
            "UPDATE checkpoint_stream_commits SET metadata_bytes=x'7b7d'"
        )
    else:
        # Standard library imports
        import json

        path = policy / "guardian.json"
        rules = json.loads(path.read_text())
        rules["allow"] = [
            r
            for r in rules["allow"]
            if r["action"] != "consciousness.continuity_inspect"
        ]
        path.write_text(json.dumps(rules))
    database.conn.commit()
    before = recovery.stream.legacy.rows(database)
    owned = observer(
        database, automatic=recovery.AUTO, recovery_attempt=commits[0].attempt
    )
    owned.start()
    status = await until(owned, lambda s: not s["thread_alive"])
    assert status["ticks_attempted"] == 0
    assert status["runtime_state"] == "blocked"
    assert status["continuity"]["last_error_code"] == (
        "denied" if damage == "denied_inspect" else "corrupt"
    )
    await owned.stop(save_checkpoint=True)
    assert recovery.stream.legacy.rows(database) == before


@pytest.mark.asyncio
@pytest.mark.parametrize("loss", ["policy", "ownership", "deadline"])
async def test_automatic_before_apply_rechecks_after_detached_decode(
    database, policy, monkeypatch, loss
):
    # Aetherra imports
    from Aetherra.consciousness import checkpoint

    recovery.seed(database, 1)
    entered, release = threading.Event(), threading.Event()
    original = checkpoint.decode_checkpoint

    def gated(value):
        state = original(value)
        if threading.current_thread().name == "consciousness-observer":
            entered.set()
            assert release.wait(5)
        return state

    monkeypatch.setattr(checkpoint, "decode_checkpoint", gated)
    local = [True]
    owned = observer(database, automatic=recovery.AUTO, local_owned=lambda: local[0])
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 3), owned.get_runtime_status()
        if loss == "policy":
            (policy / "capabilities.json").write_text('{"allow":{}}')
        elif loss == "ownership":
            local[0] = False
        else:
            # Expire the controlled monotonic deadline while detached validation is held.
            now = time.monotonic() + 2
            monkeypatch.setattr(time, "monotonic", lambda: now)
        release.set()
        await asyncio.to_thread(owned._thread.join, 3)
        status = owned.get_runtime_status()
        assert not status["thread_alive"]
        assert status["ticks_attempted"] == 0
        assert status["continuity"]["restored_record_id"] is None
    finally:
        release.set()
        await owned.stop()


@pytest.mark.asyncio
async def test_c2a_restore_has_unknown_verified_time(observer_profile):
    owned = observer(CheckpointStore(), restore_checkpoint_id=HANDLE)
    owned.start()
    try:
        status = await until(owned, lambda s: s["ticks_completed"] == 1)
        assert status["continuity"]["last_verified_observation_at_unix_s"] is None
        assert status["continuity"]["observation_gap_state"] == "unknown"
        assert status["continuity"]["offline_duration_seconds"] is None
    finally:
        await owned.stop()


backends = recovery.backends


@pytest.mark.asyncio
@pytest.mark.parametrize("orderly", [False, True])
async def test_launcher_resumes_configured_descriptor_through_registered_memory(
    database, backends, policy, orderly
):
    # Standard library imports
    import json
    from dataclasses import asdict

    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher
    from aetherra_service_registry import AetherraServiceRegistry

    adapter, engine, original = backends
    _, commits = recovery.seed(adapter, 1)
    path = policy / "guardian.json"
    rules = json.loads(path.read_text())
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
                "action": "consciousness.micro_reflection_update",
            },
        ]
    )
    path.write_text(json.dumps(rules))
    registry = AetherraServiceRegistry()
    registry._running = True
    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    hub = SimpleNamespace(is_running=lambda: True)
    kernel = SimpleNamespace(get_status=lambda: {"running": True})
    chat = object()
    launcher.kernel_loop = kernel
    launcher._presence_owned_hub = hub
    launcher.systems.update(memory=adapter, aetherra=chat, aetherra_hub=hub)
    for name, instance in [
        ("memory_system", engine),
        ("aetherra_engine", chat),
        ("kernel_loop", kernel),
        ("aetherra_hub", hub),
    ]:
        assert await registry.register_service(name, instance)
    cfg = {
        "consciousness_enabled": True,
        "consciousness_continuity": {
            "enabled": True,
            "automatic": recovery.AUTO,
            "recovery_attempt": asdict(commits[0].attempt),
        },
    }
    try:
        await launcher._start_consciousness_observer(cfg)
        owned = launcher.systems["consciousness_core"]
        status = await until(
            owned, lambda s: s["ticks_completed"] > 0 or not s["thread_alive"]
        )
        assert status["ticks_completed"] == 1, status
        assert status["continuity"]["recovery_outcome"] == "committed_current"
        assert status["continuity"]["restored_record_id"] == commits[0].head.record_id
        # The receipt predicate compares cached identities without running policy.
        assert owned._local_owned()
        engine.core_memory = database
        assert not owned._local_owned()
        engine.core_memory = original
        assert owned._local_owned()
    finally:
        engine.core_memory = original
        await launcher._stop_consciousness_observer(save_checkpoint=orderly)
    rows = recovery.stream.legacy.rows(original)
    assert commits[0].head.record_id in {row[0] for row in rows}
    assert len(rows) == 1 + int(orderly)
    result = owned.get_runtime_status()["continuity"]
    if orderly:
        assert result["saved_trigger"] == "orderly_stop"
        assert result["last_save_acceptance"] == "acknowledged"
        assert result["saved_record_id"] in {row[0] for row in rows}
        assert result["saved_generation"] == 2
    else:
        assert result["saved_record_id"] is None


@pytest.mark.asyncio
async def test_stop_between_local_check_and_sealed_startup_poll_refuses_receipt(
    database, monkeypatch
):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.checkpoint_stream import StreamJob

    _, commits = recovery.seed(database, 1)
    entered, release = threading.Event(), threading.Event()
    consumed = []
    real_poll = StreamJob.poll

    def gated(job, *, local_owned):
        if not job.outstanding and local_owned and not entered.is_set():
            entered.set()
            assert release.wait(3)
            result = real_poll(job, local_owned=local_owned)
            consumed.append(result)
            return result
        return real_poll(job, local_owned=local_owned)

    monkeypatch.setattr(StreamJob, "poll", gated)
    owned = observer(
        database, automatic=recovery.AUTO, recovery_attempt=commits[0].attempt
    )
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 3)
        await owned.stop(timeout=0)
        release.set()
        await owned.stop()
        await until(owned, lambda s: not s["thread_alive"])
        assert len(consumed) == 1
        assert consumed[0].value is None
        assert consumed[0].error_code == "uncertain"
        assert owned.get_runtime_status()["ticks_attempted"] == 0
    finally:
        release.set()
        await owned.stop()


@pytest.mark.asyncio
@pytest.mark.parametrize("automatic", [True, False], ids=["automatic", "explicit"])
@pytest.mark.parametrize("cut", ["stop", "deadline"])
async def test_core_import_preparation_never_blocks_status_or_publishes_after_cut(
    database, monkeypatch, automatic, cut
):
    # Aetherra imports
    from Aetherra.aetherra_core.memory import lifecycle_checkpoint
    from Aetherra.consciousness import self_trust
    from Aetherra.consciousness.core import consciousness_core

    # Save with real governed Memory, then pause the real trust-map construction.
    if automatic:
        recovery.seed(database, 1)
        owned = observer(database, automatic=recovery.AUTO)
    else:
        recovery.stream.legacy.save(database).result(2)
        owned = observer(database, restore_checkpoint_id=HANDLE)
    entered, release = threading.Event(), threading.Event()
    cores = []
    create_core = consciousness_core.ConsciousnessCore
    create_record = self_trust.SubsystemTrust

    def track_core(*args, **kwargs):
        core = create_core(*args, **kwargs)
        cores.append((core, core.qualia, core.self_trust.subsystems))
        return core

    def gated_trust_record(*args, **kwargs):
        record = create_record(*args, **kwargs)
        entered.set()
        assert release.wait(4)
        return record

    monkeypatch.setattr(consciousness_core, "ConsciousnessCore", track_core)
    monkeypatch.setattr(self_trust, "SubsystemTrust", gated_trust_record)
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 3)
        if cut == "stop":
            # Use an independent event loop so a lock-blocked stop cannot stall
            # this test's watchdog or depend on release to satisfy its deadline.
            await asyncio.wait_for(
                asyncio.to_thread(lambda: asyncio.run(owned.stop(timeout=0.05))), 0.75
            )
            pending = await asyncio.wait_for(
                asyncio.to_thread(owned.get_runtime_status), 0.5
            )
            assert pending["thread_alive"]
        else:
            pending = await asyncio.wait_for(
                asyncio.to_thread(owned.get_runtime_status), 0.5
            )
            assert pending["continuity"]["restored_record_id"] is None
            expired = SimpleNamespace(
                monotonic=lambda: time.monotonic() + 2, time=time.time, sleep=time.sleep
            )
            monkeypatch.setattr(lifecycle_checkpoint, "time", expired)
            monkeypatch.setattr(runtime, "time", expired)
        release.set()
        status = await until(
            owned, lambda s: not s["thread_alive"] or s["ticks_attempted"] > 0
        )
        assert status["ticks_attempted"] == 0
        assert status["continuity"]["restored_record_id"] is None
        core, original_qualia, original_subsystems = cores[0]
        assert core.qualia is original_qualia
        assert core.self_trust.subsystems is original_subsystems
    finally:
        release.set()
        await owned.stop()


def due_on_first_tick(database, monkeypatch, policy, *, interval=10):
    # Standard library imports
    import json

    # Aetherra imports
    from Aetherra.consciousness.checkpoint_session import ObserverCheckpointSession

    path = policy / "guardian.json"
    rules = json.loads(path.read_text())
    rules["allow"].append(
        {
            "requester": "consciousness:core",
            "subsystem": "consciousness",
            "action": "consciousness.micro_reflection_update",
        }
    )
    path.write_text(json.dumps(rules))
    take = ObserverCheckpointSession.take_restore

    # A monotonic scheduler pause makes the first completed tick due without
    # shortening either the production interval or the Memory acceptance window.
    offset = [0]
    monkeypatch.setattr(
        runtime,
        "time",
        SimpleNamespace(
            monotonic=lambda: time.monotonic() + offset[0],
            time=time.time,
            sleep=time.sleep,
        ),
    )

    def advance_clock(session):
        selection = take(session)
        offset[0] = 30
        return selection

    monkeypatch.setattr(ObserverCheckpointSession, "take_restore", advance_clock)
    return runtime.ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [],
        checkpoint_store=database,
        tick_interval=interval,
        continuity_enabled=True,
        automatic=dict(recovery.AUTO, start_mode="create", save_interval_seconds=30),
    )


def hold_periodic_boundary(monkeypatch, stage):
    # Standard library imports
    import sqlite3

    # Aetherra imports
    from Aetherra.aetherra_core.memory import lifecycle_checkpoint as persistence

    entered, release, committed = (threading.Event() for _ in range(3))

    def pause():
        entered.set()
        assert release.wait(5)

    # Aetherra imports
    import Aetherra.guardian.core as guardian

    append_decision = guardian.append_guardian_decision
    connect = sqlite3.connect
    recheck = persistence._recheck_policy

    def audit(intent, risk, decision):
        if stage == "audit" and intent.action == "consciousness.continuity_advance":
            pause()
        return append_decision(intent, risk, decision)

    class Connection(sqlite3.Connection):
        def commit(self):
            generation = self.execute(
                "SELECT generation FROM checkpoint_stream_heads"
            ).fetchone()[0]
            if generation and stage == "commit":
                pause()
            super().commit()
            if generation:
                committed.set()

    def policy_check(intent):
        if committed.is_set() and stage == "before_policy":
            pause()
        recheck(intent)
        if committed.is_set() and stage == "after_policy":
            pause()

    monkeypatch.setattr(guardian, "append_guardian_decision", audit)
    monkeypatch.setattr(
        sqlite3, "connect", lambda *a, **kw: connect(*a, **kw, factory=Connection)
    )
    monkeypatch.setattr(persistence, "_recheck_policy", policy_check)
    return entered, release


async def heartbeat_launcher(policy):
    # Standard library imports
    import json

    # Aetherra imports
    from aetherra_kernel_loop import AetherraKernelLoop
    from aetherra_os_launcher import AetherraOSLauncher, EngineAdapter
    from aetherra_service_registry import AetherraServiceRegistry

    path = policy / "guardian.json"
    rules = json.loads(path.read_text())
    rules["allow"].append(
        {
            "requester": "service_registry",
            "subsystem": "service_registry",
            "action": "service_registry.*",
        }
    )
    path.write_text(json.dumps(rules))
    launcher = AetherraOSLauncher()
    registry = launcher.service_registry = AetherraServiceRegistry()
    launcher.running = registry._running = True
    kernel = launcher.kernel_loop = AetherraKernelLoop()
    kernel.running = True
    engine = kernel.aetherra_engine = EngineAdapter(SimpleNamespace(initialized=True))
    launcher.systems["aetherra"] = engine
    launcher._kernel_task = asyncio.current_task()
    assert await registry.register_service("kernel_loop", kernel)
    assert await registry.register_service("aetherra_engine", engine.impl)
    return launcher


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["audit", "commit", "after_policy"])
async def test_blocked_periodic_work_keeps_ticks_heartbeat_status_and_bounded_stop(
    database, monkeypatch, policy, stage
):
    launcher = await heartbeat_launcher(policy)
    owned = due_on_first_tick(database, monkeypatch, policy, interval=0.2)
    entered, release = hold_periodic_boundary(monkeypatch, stage)
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 1.5), owned.get_runtime_status()
        engine_info = launcher.service_registry.get_service_info("aetherra_engine")
        before = engine_info.last_heartbeat
        assert await asyncio.wait_for(launcher._refresh_owned_engine_heartbeat(), 0.8)
        assert engine_info.last_heartbeat > before
        active = await until(owned, lambda s: s["ticks_completed"] >= 2)
        assert active["continuity"]["outstanding"]
        assert owned.get_think_stream()["runtime_state"] == "running"
        await asyncio.wait_for(owned.stop(timeout=0.05, save_checkpoint=True), 0.5)
        await asyncio.wait_for(owned.stop(save_checkpoint=True), 0.5)
        assert owned.get_runtime_status()["continuity"]["outstanding"]
        assert database.lifecycle_checkpoint_pending()
    finally:
        release.set()
        await owned.stop(timeout=0)
        await until(owned, lambda s: not s["thread_alive"])
    rejected = owned.get_runtime_status()["continuity"]
    assert rejected["saved_record_id"] is None
    assert not rejected["outstanding"]
    assert rejected["last_save_acceptance"] == "unacknowledged"
    assert len(recovery.stream.legacy.rows(database)) <= 1


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["before_policy", "after_policy", "expiry"])
async def test_owner_wakes_inside_ten_second_tick_wait(
    database, monkeypatch, policy, stage
):
    owned = due_on_first_tick(database, monkeypatch, policy)
    entered, release = hold_periodic_boundary(
        monkeypatch, "after_policy" if stage == "expiry" else stage
    )
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 1.5), owned.get_runtime_status()
        if stage == "expiry":
            expired = await asyncio.wait_for(
                until(
                    owned,
                    lambda s: s["continuity"]["last_error_code"] == "uncertain",
                ),
                1.5,
            )
            assert expired["continuity"]["outstanding"]
        else:
            (policy / "capabilities.json").write_text('{"allow":{}}')
        release.set()
        end = await asyncio.wait_for(
            until(owned, lambda s: not s["continuity"]["outstanding"]), 0.8
        )
        assert end["ticks_completed"] == 1
        status = end["continuity"]
        assert bool(status["saved_record_id"]) == (stage == "after_policy")
        assert status["last_save_acceptance"] == (
            "acknowledged" if stage == "after_policy" else "unacknowledged"
        )
        assert len(recovery.stream.legacy.rows(database)) == 1
    finally:
        release.set()
        await owned.stop()


@pytest.mark.asyncio
async def test_repeated_launcher_checkpoint_drain_uses_original_deadline(monkeypatch):
    # Aetherra imports
    import aetherra_os_launcher as launcher_module

    launcher = launcher_module.AetherraOSLauncher()
    elapsed = [100.0]
    budgets = []

    def drain(*, timeout):
        budgets.append(timeout)
        return timeout == 0

    class Owned:
        _checkpoint_store = SimpleNamespace(drain_lifecycle_checkpoints=drain)

        async def stop(self, *, save_checkpoint, deadline):
            assert deadline == 102.0
            elapsed[0] += 1.25

        def get_runtime_status(self):
            return {"continuity": {"enabled": True}}

    launcher.systems["consciousness_core"] = Owned()
    monkeypatch.setattr(
        launcher_module, "time", SimpleNamespace(monotonic=lambda: elapsed[0])
    )
    with pytest.raises(RuntimeError, match="consciousness_shutdown_pending"):
        await launcher._stop_consciousness_observer(save_checkpoint=True)
    await launcher._stop_consciousness_observer()
    assert budgets == [0.75, 0.0]


@pytest.mark.asyncio
async def test_consumed_periodic_receipt_survives_stop_before_status_publication(
    database, monkeypatch, policy
):
    # Aetherra imports
    from Aetherra.consciousness.checkpoint_session import ObserverCheckpointSession

    owned = due_on_first_tick(database, monkeypatch, policy)
    status = ObserverCheckpointSession.get_cached_status
    entered, release = threading.Event(), threading.Event()

    def after_consumption(session):
        result = status(session)
        if result["last_save_acceptance"] == "acknowledged" and not entered.is_set():
            entered.set()
            assert release.wait(3)
        return result

    monkeypatch.setattr(
        ObserverCheckpointSession, "get_cached_status", after_consumption
    )
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 2)
        await owned.stop(timeout=0)
    finally:
        release.set()
        await until(owned, lambda s: not s["thread_alive"])
    receipt = owned.get_runtime_status()["continuity"]
    assert receipt["last_save_acceptance"] == "acknowledged"
    assert receipt["saved_record_id"] == recovery.stream.legacy.rows(database)[0][0]
    assert receipt["saved_trigger"] == "periodic"
    assert not receipt["outstanding"]


@pytest.mark.asyncio
async def test_launcher_two_seconds_then_zero_budget_until_actual_periodic_drain(
    database, monkeypatch, policy
):
    # Aetherra imports
    import aetherra_os_launcher as launcher_module

    owned = due_on_first_tick(database, monkeypatch, policy)
    # The launcher and observer share a monotonic domain, including the
    # scheduler pause injected by due_on_first_tick.
    monkeypatch.setattr(launcher_module, "time", runtime.time)
    entered, release = hold_periodic_boundary(monkeypatch, "after_policy")
    launcher = launcher_module.AetherraOSLauncher()
    launcher.systems["consciousness_core"] = owned
    launcher._consciousness_task = asyncio.create_task(asyncio.sleep(60))
    owned.start()
    try:
        assert await asyncio.to_thread(entered.wait, 2)
        started = time.monotonic()
        with pytest.raises(RuntimeError, match="consciousness_shutdown_pending"):
            await asyncio.wait_for(
                launcher._stop_consciousness_observer(save_checkpoint=True), 2.5
            )
        assert 1.75 <= time.monotonic() - started < 2.5
        assert database.lifecycle_checkpoint_pending()
        with pytest.raises(RuntimeError, match="consciousness_shutdown_pending"):
            await asyncio.wait_for(launcher._stop_consciousness_observer(), 0.3)
    finally:
        release.set()
        await until(owned, lambda s: not s["thread_alive"])
    assert not owned.get_runtime_status()["continuity"]["outstanding"]
    assert await asyncio.to_thread(database.drain_lifecycle_checkpoints, 0.5)
    await asyncio.wait_for(launcher._stop_consciousness_observer(), 0.3)
    assert owned.get_runtime_status()["continuity"]["saved_record_id"] is None
    assert len(recovery.stream.legacy.rows(database)) == 1


@pytest.mark.asyncio
async def test_launcher_budget_includes_executor_wait_and_allows_drained_probe(
    monkeypatch,
):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    class Drained:
        _checkpoint_store = SimpleNamespace(
            drain_lifecycle_checkpoints=lambda *, timeout: timeout == 0
        )

        async def stop(self, *, save_checkpoint, deadline):
            pass

        def get_runtime_status(self):
            return {"continuity": {"enabled": True}}

    async def busy_executor(*args, **kwargs):
        await asyncio.Event().wait()

    launcher = AetherraOSLauncher()
    launcher.systems["consciousness_core"] = Drained()
    launcher._consciousness_stop_deadline = time.monotonic() + 0.05
    monkeypatch.setattr(asyncio, "to_thread", busy_executor)
    with pytest.raises(RuntimeError, match="consciousness_shutdown_pending"):
        await asyncio.wait_for(launcher._stop_consciousness_observer(), 0.4)
    finished_monitor = asyncio.create_task(asyncio.sleep(0))
    await finished_monitor
    launcher._consciousness_task = finished_monitor
    await asyncio.wait_for(launcher._stop_consciousness_observer(), 0.2)


@pytest.mark.asyncio
async def test_ownership_lost_between_positive_sample_and_worker_seal(
    database, monkeypatch, policy
):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.checkpoint_stream import (
        AdvanceReceipt,
        StreamJob,
    )

    owned = due_on_first_tick(database, monkeypatch, policy)
    sealing, sampled, release, sealed = (threading.Event() for _ in range(4))
    local_owner = threading.Event()
    local_owner.set()
    original = StreamJob._seal

    def gate_seal(job, value, error, **kwargs):
        if type(value) is AdvanceReceipt:
            sealing.set()
            assert release.wait(3)
            original(job, value, error, **kwargs)
            sealed.set()
        else:
            original(job, value, error, **kwargs)

    def identity():
        answer = local_owner.is_set()
        if (
            threading.current_thread() is owned._thread
            and sealing.is_set()
            and not sampled.is_set()
        ):
            sampled.set()
            assert sealed.wait(3)
        return answer

    monkeypatch.setattr(StreamJob, "_seal", gate_seal)
    monkeypatch.setattr(owned, "_local_owned", identity)
    owned.start()
    try:
        assert await asyncio.to_thread(sealing.wait, 2)
        owned._wake.set()
        assert await asyncio.to_thread(sampled.wait, 0.5)
        local_owner.clear()
        release.set()
        terminal = {"unacknowledged", "acknowledged"}
        status = await until(
            owned, lambda s: s["continuity"]["last_save_acceptance"] in terminal
        )
        assert status["continuity"]["last_save_acceptance"] == "unacknowledged"
        assert status["continuity"]["saved_record_id"] is None
        assert status["continuity"]["observed_generation"] == 0
    finally:
        release.set()
        local_owner.set()
        await owned.stop(save_checkpoint=True)
    assert len(recovery.stream.legacy.rows(database)) == 1
