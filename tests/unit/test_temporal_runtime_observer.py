"""Strict optional collector configuration."""

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.temporal_observer import temporal_settings

# Local imports
from . import test_memory_temporal_history as history

memory = history.memory
policy = history.policy
temporal_policy = history.temporal_policy


def test_disabled_by_default():
    assert temporal_settings({}) is None
    assert temporal_settings({"temporal_observer": {"enabled": False}}) is None


@pytest.mark.parametrize(
    "settings",
    [
        None,
        {},
        {"enabled": 1},
        {"enabled": False, "history_id": "0" * 32},
        {"enabled": True, "history_id": "X" * 32, "start_mode": "create"},
        {"enabled": True, "history_id": "1" * 32, "start_mode": "reset"},
    ],
)
def test_invalid_temporal_settings(settings):
    with pytest.raises(ValueError, match="temporal_config_invalid"):
        temporal_settings(
            {"consciousness_enabled": True, "temporal_observer": settings}
        )


def test_valid_requires_enabled_observe_core():
    settings = {"enabled": True, "history_id": "a" * 32, "start_mode": "create"}
    with pytest.raises(ValueError, match="temporal_config_invalid"):
        temporal_settings(
            {"consciousness_enabled": False, "temporal_observer": settings}
        )
    assert (
        temporal_settings(
            {"consciousness_enabled": True, "temporal_observer": settings}
        )
        == settings
    )


def _wait(check):
    # Standard library imports
    import time

    deadline = time.monotonic() + 4
    while not check():
        assert time.monotonic() < deadline
        time.sleep(0.002)


def _observer(source, memory, **kwargs):
    # Aetherra imports
    from Aetherra.consciousness.temporal_observer import TemporalObserver

    return TemporalObserver(
        source,
        memory,
        settings={"enabled": True, "history_id": "b" * 32, "start_mode": "create"},
        readiness=lambda: None,
        local_owned=lambda: True,
        **kwargs,
    )


def test_stop_cancels_original_pre_admission_control(
    memory, temporal_policy, monkeypatch
):
    # Standard library imports
    import asyncio
    import threading
    import time

    held, release = threading.Event(), threading.Event()
    controls = []
    original = memory.submit_acquire_temporal_history

    def delayed(**kwargs):
        controls.append(kwargs["control"])
        held.set()
        assert release.wait(4)
        return original(**kwargs)

    monkeypatch.setattr(memory, "submit_acquire_temporal_history", delayed)
    observer = _observer(None, memory)
    observer.start()
    try:
        assert held.wait(3)
        assert not asyncio.run(observer.stop(deadline=time.monotonic() + 0.05))
        assert controls[0].cancelled.is_set()
        assert observer.get_status()["outstanding"]
        assert not asyncio.run(observer.stop())
    finally:
        release.set()
        _wait(lambda: not observer.get_status()["thread_alive"])
    assert asyncio.run(observer.stop())
    assert observer.get_status()["last_error_code"] == "uncertain"


def test_late_engine_gate_rejects_publication_and_never_reads_source(
    memory, temporal_policy
):
    # Standard library imports
    import asyncio
    import threading
    import time
    from contextlib import contextmanager

    # Aetherra imports
    from Aetherra.consciousness.quantum.temporal_consciousness_system import (
        TemporalConsciousnessEngine,
    )

    entered, release, sampled = threading.Event(), threading.Event(), threading.Event()

    class Engine(TemporalConsciousnessEngine):
        def import_history_window(self, records, *, publication_guard, **kwargs):
            @contextmanager
            def delayed_guard():
                entered.set()
                assert release.wait(4)
                with publication_guard:
                    yield

            return super().import_history_window(
                records, publication_guard=delayed_guard(), **kwargs
            )

    class Source:
        def get_temporal_observation(self):
            sampled.set()

    engine = Engine()
    observer = _observer(Source(), memory, engine_factory=lambda: engine)
    observer.start()
    try:
        assert entered.wait(3)
        assert observer.get_status()["accepted_observations"] == 0
        assert not asyncio.run(
            observer.stop(save_history=True, deadline=time.monotonic() + 0.04)
        )
    finally:
        release.set()
        _wait(lambda: not observer.get_status()["thread_alive"])
    assert engine.get_history_status() == {}
    assert not sampled.is_set()
    assert observer.get_status()["runtime_state"] == "blocked"


def test_inert_blocked_instance_never_starts():
    # Aetherra imports
    from Aetherra.consciousness.temporal_observer import TemporalObserver

    def unexpected():
        pytest.fail("callback on inert instance")

    obs = TemporalObserver(
        None,
        None,
        settings=None,
        local_owned=unexpected,
        readiness=unexpected,
        engine_factory=unexpected,
    )
    obs.block("temporal_config_invalid")
    assert not obs.start()
    assert obs.get_status()["runtime_state"] == "blocked"


def test_fixed_sampler_records_changes_gaps_and_rollback(
    memory, temporal_policy, monkeypatch
):
    # Standard library imports
    import asyncio
    import threading
    import time
    from queue import Queue

    def source(session, seq, wall, count):
        return {
            "session_id": session * 32,
            "session_started_at_unix_s": 10.0,
            "sequence": seq,
            "observed_at_unix_s": wall,
            "observed_uptime_s": float(seq),
            "working_memory_count": count,
            "active_intention_count": 1,
            "focus_count": 0,
        }

    sequence = iter(
        [
            source("a", 1, 11.0, 1),
            source("a", 1, 11.0, 1),
            source("a", 3, 13.0, 1),
            None,
            source("a", 5, 12.0, 1),
            source("a", 6, 11.0, 2),
            source("b", 1, 15.0, 2),
        ]
    )

    class Source:
        def get_temporal_observation(self):
            return next(sequence)

    ready, advance = Queue(), threading.Event()
    observer = _observer(Source(), memory)

    def wait_for_sample(deadline):
        ready.put(deadline)
        assert advance.wait(4)
        advance.clear()

    monkeypatch.setattr(observer, "_wait_for_sample", wait_for_sample)
    observer.start()
    try:
        for i, expected in enumerate((1, 1, 1, 1, 2, 3, 4)):
            deadline = ready.get(timeout=4)
            assert time.monotonic() + 3 < deadline <= time.monotonic() + 5
            status = observer.get_status()
            assert status["accepted_observations"] == expected
            assert status["source_fresh"] is (i != 3)
            if i == 5:
                assert status["observation_gap_state"] == "inconsistent"
            if i != 6:
                advance.set()
        assert status["skipped_observations"] == 2
        assert [
            r.event.reason
            for r in observer._engine.history_provenance
            if r.event.kind == "gap"
        ] == ["source_unavailable", "source_changed"]
    finally:
        observer.close_observation_admission()
        advance.set()
        assert asyncio.run(observer.stop(save_history=True))
    assert observer._engine.history_provenance[-1].event.kind == "session_end"


def test_expired_memory_job_remains_owned_until_real_settlement(
    memory, temporal_policy, monkeypatch
):
    # Standard library imports
    import asyncio
    import threading
    import time

    # Aetherra imports
    from Aetherra.aetherra_core.memory import temporal_history_worker

    original = temporal_history_worker._recheck_policy
    held, release = threading.Event(), threading.Event()

    def delayed(intent):
        original(intent)
        held.set()
        assert release.wait(4)

    monkeypatch.setattr(temporal_history_worker, "_recheck_policy", delayed)
    observer = _observer(None, memory)
    observer.start()
    try:
        assert held.wait(3)
        _wait(lambda: observer.get_status()["runtime_state"] == "blocked")
        assert observer.get_status()["outstanding"]
        assert observer.get_status()["last_error_code"] == "uncertain"
        assert not asyncio.run(observer.stop(deadline=time.monotonic() + 0.03))
        assert not asyncio.run(observer.stop())
    finally:
        release.set()
        _wait(lambda: not observer.get_status()["thread_alive"])
    assert asyncio.run(observer.stop())
    assert not observer.get_status()["outstanding"]
    assert observer.get_status()["runtime_state"] == "blocked"


def test_cached_status_expires_while_admission_is_stalled(
    memory, temporal_policy, monkeypatch
):
    # Standard library imports
    import asyncio
    import threading

    held, release = threading.Event(), threading.Event()
    original = memory.submit_acquire_temporal_history

    def delayed(**kwargs):
        held.set()
        assert release.wait(4)
        return original(**kwargs)

    monkeypatch.setattr(memory, "submit_acquire_temporal_history", delayed)
    observer = _observer(None, memory)
    observer.start()
    try:
        assert held.wait(3)
        _wait(lambda: observer.get_status()["last_error_code"] == "uncertain")
        assert observer.get_status()["outstanding"]
    finally:
        release.set()
        _wait(lambda: not observer.get_status()["thread_alive"])
    assert observer.get_status()["last_error_code"] == "uncertain"
    assert asyncio.run(observer.stop())


def _sample_data():
    return {
        "session_id": "a" * 32,
        "session_started_at_unix_s": 1.0,
        "sequence": 1,
        "observed_at_unix_s": 2.0,
        "observed_uptime_s": 1.0,
        "working_memory_count": 1,
        "active_intention_count": 0,
        "focus_count": 0,
    }


@pytest.mark.parametrize("stall", ["owned", "readiness", "append_readiness", "source"])
def test_preflight_in_original_window(memory, temporal_policy, stall):
    # Standard library imports
    import threading
    from types import SimpleNamespace

    entered, release = threading.Event(), threading.Event()

    def delayed():
        entered.set()
        assert release.wait(5)

    ready_calls = 0

    def readiness():
        nonlocal ready_calls
        ready_calls += 1
        if stall == "readiness" or (stall == "append_readiness" and ready_calls == 2):
            delayed()

    def source():
        if stall == "source":
            delayed()
        return _sample_data()

    def owned():
        if stall == "owned":
            delayed()
        return True

    observer = _observer(SimpleNamespace(get_temporal_observation=source), memory)
    observer._owned = owned
    observer._readiness = readiness
    observer.start()
    try:
        assert entered.wait(3)
        assert observer.get_status()["outstanding"]
        _wait(lambda: observer.get_status()["last_error_code"] == "uncertain")
    finally:
        release.set()
        if observer.get_status()["runtime_state"] != "blocked":
            observer.block("unavailable")
        _wait(lambda: not observer.get_status()["thread_alive"])
    assert observer.get_status()["last_error_code"] == "uncertain"
    assert observer.get_status()["accepted_observations"] == 0


def test_late_typed_error_cannot_replace_uncertain(
    memory, temporal_policy, monkeypatch
):
    # Standard library imports
    import threading

    # Aetherra imports
    from Aetherra.aetherra_core.memory.lifecycle_checkpoint import CheckpointError

    held, release = threading.Event(), threading.Event()

    def delayed(**kwargs):
        held.set()
        assert release.wait(4)
        raise CheckpointError("denied")

    monkeypatch.setattr(memory, "submit_acquire_temporal_history", delayed)
    observer = _observer(None, memory)
    observer.start()
    try:
        assert held.wait(3)
        _wait(lambda: observer.get_status()["last_error_code"] == "uncertain")
    finally:
        release.set()
        _wait(lambda: not observer.get_status()["thread_alive"])
    assert observer.get_status()["last_error_code"] == "uncertain"


@pytest.mark.parametrize("origin", ["source", "factory"])
def test_callback_cancellation_settles_blocked(memory, temporal_policy, origin):
    # Standard library imports
    import asyncio
    from types import SimpleNamespace

    def cancelled():
        raise asyncio.CancelledError

    observer = _observer(
        SimpleNamespace(get_temporal_observation=cancelled),
        memory,
        **({"engine_factory": cancelled} if origin == "factory" else {}),
    )
    observer.start()
    _wait(lambda: not observer.get_status()["thread_alive"])
    assert observer.get_status()["runtime_state"] == "blocked"
    assert observer.get_status()["last_error_code"] == "cancelled"
    assert asyncio.run(observer.stop())


def test_same_cached_sample_after_transient_readiness(memory, temporal_policy):
    # Standard library imports
    import asyncio
    import threading
    from types import SimpleNamespace

    ready = iter([None, "busy", None, None])
    observer = _observer(SimpleNamespace(get_temporal_observation=_sample_data), memory)
    observer._readiness = lambda: next(ready, None)
    sampled = threading.Event()

    def wait_once(deadline):
        if not sampled.is_set():
            sampled.set()
        else:
            observer._wake.wait(3)

    observer._wait_for_sample = wait_once
    observer.start()
    try:
        _wait(lambda: observer.get_status()["accepted_observations"] == 1)
        assert observer._engine.history_provenance[-1].event.source.sequence == 1
    finally:
        assert asyncio.run(observer.stop())


def test_closed_unchanged_probe_preserves_sequence_and_skipped_count(
    memory, temporal_policy, monkeypatch
):
    # Standard library imports
    import asyncio
    from types import SimpleNamespace

    samples = iter([_sample_data(), dict(_sample_data(), sequence=4)])
    observer = _observer(
        SimpleNamespace(get_temporal_observation=lambda: next(samples)), memory
    )
    observer._wait_for_sample = lambda deadline: None
    reads = []
    submit = memory.submit_read_temporal_history

    def close_before_read(**kwargs):
        observer.close_observation_admission()
        job = submit(**kwargs)
        reads.append(job.admitted)
        return job

    monkeypatch.setattr(memory, "submit_read_temporal_history", close_before_read)
    observer.start()
    try:
        _wait(lambda: bool(reads))
    finally:
        assert asyncio.run(observer.stop())
    assert reads == [False]
    assert observer._seen.sequence == 1
    assert observer.get_status()["skipped_observations"] == 0
