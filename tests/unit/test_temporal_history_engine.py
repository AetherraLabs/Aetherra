# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import replace
from threading import Event, Lock

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.temporal_history import (
    EMPTY,
    OWNER,
    SCOPE,
    AppendRequest,
    HistoryHead,
    HistoryKey,
    HistoryRecord,
    HistoryToken,
    TemporalEvent,
    TemporalSource,
)
from Aetherra.consciousness.quantum.temporal_consciousness_system import (
    TemporalConflictError,
    TemporalConsciousnessEngine,
    TemporalValidationError,
)

HISTORY_ID = "a" * 32


def add_record(
    prior=EMPTY,
    *,
    kind="observation",
    time=100,
    record_id=None,
    history_id=HISTORY_ID,
    sequence=1,
):
    source = TemporalSource("b" * 32, 80, sequence, time, sequence * 5, 2, 3, 4)
    event = TemporalEvent(
        record_id or f"{prior.ordinal + 1:032x}",
        kind,
        source,
        time + 1,
        {"session_start": "created", "session_end": "orderly_stop"}.get(kind),
    )
    request = AppendRequest(
        HistoryToken(HistoryKey(OWNER, SCOPE, history_id), 1), prior, "c" * 32, (event,)
    )
    return HistoryRecord.build(request, prior, event)


def apply(engine, records, *, head=None, authorize=lambda: None, guard=None):
    return engine.import_history_window(
        records,
        history_id=HISTORY_ID,
        selected_head=(
            head if head is not None else records[-1].head if records else EMPTY
        ),
        authorize=authorize,
        publication_guard=guard,
    )


def test_import_preserves_exact_ordinal_order_and_raw_clocks():
    engine = TemporalConsciousnessEngine()
    start = add_record(kind="session_start")
    earlier = add_record(start.head, time=120, sequence=1)
    latest = add_record(earlier.head, time=90, sequence=2)
    end = add_record(latest.head, kind="session_end", time=90, sequence=2)
    records = (start, earlier, latest, end)

    status = apply(engine, records)

    assert status == {
        "history_id": HISTORY_ID,
        "head_ordinal": 4,
        "head_record_id": end.event.record_id,
        "head_digest": end.digest,
        "retained_records": 4,
        "retained_observations": 2,
        "partial_window": False,
        "last_observation_record_id": latest.event.record_id,
    }
    assert list(engine.temporal_moments) == [
        earlier.event.record_id,
        latest.event.record_id,
    ]
    moment = engine.temporal_moments[latest.event.record_id]
    assert moment.timestamp.timestamp() == 90
    assert moment.consciousness_state == {
        "working_memory_count": 2,
        "active_intention_count": 3,
        "focus_count": 4,
    }
    assert not moment.memory_associations
    assert not moment.causal_influences
    assert not engine.temporal_predictions
    assert not engine.causal_chains
    assert not engine.temporal_coherence_history
    assert engine.history_provenance == records
    assert engine.history_provenance[-2] is not latest
    status["head_ordinal"] = -1
    assert engine.get_history_status()["head_ordinal"] == 4


def test_suffix_is_bounded_by_records_in_commit_order():
    engine = TemporalConsciousnessEngine()
    first = add_record()
    records = [first]
    for sequence in range(2, 258):
        records.append(
            add_record(records[-1].head, time=400 - sequence, sequence=sequence)
        )

    status = apply(engine, tuple(records[-256:]))

    assert status["partial_window"] is True
    assert status["retained_records"] == status["retained_observations"] == 256
    assert list(engine.temporal_moments) == [r.event.record_id for r in records[1:]]
    assert status["last_observation_record_id"] == records[-1].event.record_id
    with pytest.raises(TemporalValidationError):
        apply(engine, tuple(records))
    assert engine.get_history_status() == status


def test_empty_and_marker_only_windows_have_no_observation():
    engine = TemporalConsciousnessEngine()

    status = apply(engine, ())
    assert status["head_ordinal"] == status["retained_records"] == 0
    assert status["head_record_id"] is status["head_digest"] is None
    assert status["last_observation_record_id"] is None
    assert status["partial_window"] is False

    start = add_record(kind="session_start")
    status = apply(engine, (start,))
    assert status["retained_records"] == 1
    assert status["retained_observations"] == 0
    assert status["last_observation_record_id"] is None
    assert not engine.temporal_moments


def test_inconsistent_or_invalid_window_never_reaches_authorization():
    engine = TemporalConsciousnessEngine()
    first = add_record()
    second = add_record(first.head)
    conflict = add_record(first.head, record_id=first.event.record_id)
    mismatch = add_record(first.head, history_id="d" * 32)
    bad_time = add_record(second.head, time=1e20)
    wrong_prior = add_record(replace(first.head, digest="0" * 64))
    third = add_record(second.head)
    corrupt = add_record(first.head)
    object.__setattr__(corrupt.event.source, "sequence", True)
    original = apply(engine, (first,))

    def authorize():
        pytest.fail("invalid windows must be rejected before authorization")

    for records, head in (
        ((), first.head),
        ([], EMPTY),
        ((first,), EMPTY),
        ((first, second), HistoryHead(2, second.event.record_id, "0" * 64)),
        ((first, conflict), conflict.head),
        ((first, mismatch), mismatch.head),
        ((first, wrong_prior), wrong_prior.head),
        ((first, third), third.head),
        ((bad_time,), bad_time.head),
        ((corrupt,), corrupt.head),
    ):
        with pytest.raises(TemporalValidationError):
            apply(engine, records, head=head, authorize=authorize)
        assert engine.get_history_status() == original


def test_denied_authority_does_not_replace_a_previous_import():
    engine = TemporalConsciousnessEngine()
    first = add_record()
    second = add_record(first.head)
    previous = apply(engine, (first,))

    def deny():
        assert engine.get_history_status() == previous
        raise PermissionError("denied")

    with pytest.raises(PermissionError):
        apply(engine, (first, second), authorize=deny)

    assert engine.get_history_status() == previous
    assert list(engine.temporal_moments) == [first.event.record_id]


def test_cancellation_can_close_gate_while_authority_check_is_blocked():
    engine = TemporalConsciousnessEngine()
    previous = apply(engine, ())
    started, release = Event(), Event()
    lock = Lock()
    closed = False

    def authorize():
        started.set()
        assert release.wait(5)

    @contextmanager
    def guard():
        with lock:
            if closed:
                raise PermissionError("cancelled")
            yield

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            apply, engine, (add_record(),), authorize=authorize, guard=guard()
        )
        try:
            assert started.wait(5)
            assert lock.acquire(timeout=1)
            try:
                closed = True
            finally:
                lock.release()
        finally:
            release.set()
        with pytest.raises(PermissionError):
            future.result(timeout=5)

    assert engine.get_history_status() == previous


def test_reentrant_import_changes_revision_and_rejects_outer_publication():
    engine = TemporalConsciousnessEngine()
    first = add_record()
    second = add_record(first.head)

    with pytest.raises(TemporalConflictError):
        apply(engine, (first,), authorize=lambda: apply(engine, (first, second)))

    assert engine.get_history_status()["head_record_id"] == second.event.record_id


@pytest.mark.asyncio
async def test_runtime_history_rejects_legacy_mutators_and_checkpoints():
    engine = TemporalConsciousnessEngine()
    status = apply(engine, ())

    for operation, args in (
        (engine.process_temporal_moment, ({},)),
        (engine.predict_future_state, (None, {})),
        (engine.validate_prediction_accuracy, ("example", {})),
        (engine.save_checkpoint, ()),
        (engine.restore_checkpoint, ("0" * 32,)),
    ):
        with pytest.raises(TemporalConflictError):
            await operation(*args)

    assert engine.get_history_status() == status


def test_smaller_engine_capacity_retains_latest_committed_moments():
    engine = TemporalConsciousnessEngine(max_moments=1)
    earlier = add_record(time=120)
    latest = add_record(earlier.head, time=90, sequence=2)

    status = apply(engine, (earlier, latest))

    assert list(engine.temporal_moments) == [latest.event.record_id]
    assert status["retained_observations"] == 1
    assert status["retained_records"] == 2
    assert status["last_observation_record_id"] == latest.event.record_id
    assert engine.history_provenance == (earlier, latest)


def test_invalid_absolute_datetime_is_normalized(monkeypatch):
    # Standard library imports
    from datetime import datetime

    # Aetherra imports
    from Aetherra.consciousness.quantum import temporal_consciousness_system

    class BoundaryDatetime(datetime):
        @classmethod
        def fromtimestamp(cls, timestamp, tz=None):
            if timestamp == 253402300800:
                raise ValueError("year 10000 is out of range")
            return super().fromtimestamp(timestamp, tz)

    monkeypatch.setattr(
        temporal_consciousness_system, "_DATETIME_TYPE", BoundaryDatetime
    )
    engine = TemporalConsciousnessEngine()
    previous = apply(engine, ())
    invalid = add_record(time=253402300800 - 1)

    with pytest.raises(TemporalValidationError, match="^temporal_history_invalid$"):
        apply(engine, (invalid,))
    assert engine.get_history_status() == previous


def test_invalid_reconfigured_capacity_is_rejected_before_authorization():
    engine = TemporalConsciousnessEngine()
    first = add_record()
    previous = apply(engine, (first,))
    engine.max_moments = 0
    second = add_record(first.head)

    def authorize():
        pytest.fail("invalid capacity must be rejected before authorization")

    with pytest.raises(TemporalValidationError, match="^temporal_invalid_capacity$"):
        apply(engine, (first, second), authorize=authorize)
    assert engine.get_history_status() == previous
    assert list(engine.temporal_moments) == [first.event.record_id]


@pytest.mark.asyncio
async def test_standalone_mutation_prevents_runtime_import():
    engine = TemporalConsciousnessEngine()
    standalone_id = await engine.process_temporal_moment({"focus_count": 1})

    with pytest.raises(TemporalConflictError):
        apply(engine, (add_record(),))

    assert not engine.get_history_status()
    assert list(engine.temporal_moments) == [standalone_id]
