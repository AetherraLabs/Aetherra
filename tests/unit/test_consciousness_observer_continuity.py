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
        await asyncio.sleep(0)
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
        async def stop(self, *, save_checkpoint=False):
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
        async def stop(self, *, save_checkpoint=False):
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

        async def stop(self, *, save_checkpoint=False):
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
