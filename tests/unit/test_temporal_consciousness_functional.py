"""Behavioral contracts for the bounded temporal engine; no model/network use."""

# Standard library imports
import asyncio
import copy
import json
from datetime import UTC, datetime, timedelta, timezone
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.quantum import temporal_consciousness_system as temporal

NOW = datetime(2026, 11, 23, 12, tzinfo=UTC)


@pytest.fixture
def engine(monkeypatch, tmp_path):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.astimezone().replace(tzinfo=None)

    monkeypatch.setattr(temporal, "datetime", Clock)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    return temporal.TemporalConsciousnessEngine()


def snapshot(engine):
    return copy.deepcopy(
        (
            engine.temporal_moments,
            engine.temporal_predictions,
            engine.causal_chains,
            engine.temporal_coherence_history,
            engine.prediction_accuracy_history,
            engine.get_temporal_system_metrics(),
        )
    )


@pytest.mark.asyncio
async def test_same_time_operations_retain_distinct_records(engine):
    ids = await asyncio.gather(
        *(engine.process_temporal_moment({"n": i}, NOW) for i in range(4))
    )
    assert len(set(ids)) == 4
    assert set(ids) == set(engine.temporal_moments)
    predictions = [
        await engine.predict_future_state(NOW + timedelta(minutes=10), {"n": i})
        for i in range(2)
    ]
    assert predictions[0].prediction_id != predictions[1].prediction_id
    assert len(engine.temporal_predictions) == 2


@pytest.mark.asyncio
async def test_equal_time_evidence_keeps_insertion_order(engine, monkeypatch):
    # Deliberately descending opaque IDs expose accidental ID-based chronology.
    serials = iter(range(100, 0, -1))
    monkeypatch.setattr(
        temporal.uuid, "uuid4", lambda: SimpleNamespace(hex=f"{next(serials):032x}")
    )
    ids = [
        await engine.process_temporal_moment({"phase": phase}, NOW)
        for phase in ["rest", "work"] * 3
    ]
    recent = await engine._get_recent_moments(timedelta(hours=1))
    assert [m.moment_id for m in recent] == ids
    prediction = await engine.predict_future_state(
        NOW + timedelta(minutes=1), {"phase": "rest"}
    )
    assert prediction.contributing_factors == ids[-5:]
    patterns = await engine.detect_temporal_patterns(timedelta(hours=1))
    cycle = next(p for p in patterns if p["type"] == "repeating_state_cycle")
    assert cycle["moments"] == ids


@pytest.mark.asyncio
async def test_input_and_returned_prediction_do_not_alias_history(engine):
    state = {"nested": {"values": [1, "original"]}}
    mid = await engine.process_temporal_moment(state, NOW)
    state["nested"]["values"][1] = "changed"
    assert (
        engine.temporal_moments[mid].consciousness_state["nested"]["values"][1]
        == "original"
    )
    prediction = await engine.predict_future_state(NOW + timedelta(minutes=1), state)
    state["nested"]["values"][0] = 99
    prediction.predicted_state["nested"]["values"][1] = "returned edit"
    stored = engine.temporal_predictions[prediction.prediction_id].predicted_state
    assert stored == {"nested": {"values": [1, "changed"]}}


@pytest.mark.asyncio
async def test_naive_and_offset_timestamps_are_normalized_to_utc(engine):
    naive = NOW.astimezone().replace(tzinfo=None)
    mid = await engine.process_temporal_moment({"value": 1}, naive)
    assert engine.temporal_moments[mid].timestamp == NOW
    target = (NOW + timedelta(minutes=10)).astimezone(timezone(timedelta(hours=5)))
    result = await engine.predict_future_state(target, {"value": 1})
    assert result.target_time == NOW + timedelta(minutes=10)
    assert result.target_time.tzinfo == UTC


@pytest.mark.asyncio
async def test_backfill_never_creates_backward_or_same_time_links(engine):
    for seconds in (10, 20, 10, 0):
        await engine.process_temporal_moment(
            {"focus": "same"}, NOW - timedelta(seconds=seconds)
        )
    assert engine.causal_chains
    for chain in engine.causal_chains.values():
        cause = engine.temporal_moments[chain.cause_moments[0]]
        effect = engine.temporal_moments[chain.effect_moments[0]]
        assert cause.timestamp < effect.timestamp
        assert chain.temporal_span == effect.timestamp - cause.timestamp


@pytest.mark.asyncio
async def test_trends_follow_event_time_and_numeric_fields(engine):
    newer = await engine.process_temporal_moment(
        {"energy": 3.0, "enabled": True}, NOW - timedelta(minutes=1)
    )
    older = await engine.process_temporal_moment(
        {"energy": 1.0, "enabled": True}, NOW - timedelta(minutes=21)
    )
    engine.temporal_moments[older].temporal_coherence = 0.1
    engine.temporal_moments[newer].temporal_coherence = 0.9
    recent = await engine._get_recent_moments(timedelta(hours=2))
    trend = await engine._analyze_temporal_trends(recent)
    assert trend["direction"] == "increasing"
    result = await engine.predict_future_state(
        NOW + timedelta(minutes=10), {"energy": 3.0, "enabled": True, "unobserved": 7}
    )
    assert result.predicted_state["energy"] > 3.0
    assert result.predicted_state["enabled"] is True
    assert result.predicted_state["unobserved"] == 7
    assert 0 <= result.confidence <= 1
    assert all(0 <= value <= 1 for value in result.uncertainty_range.values())
    assert sum(result.uncertainty_range.values()) == pytest.approx(1)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "delta", [timedelta(seconds=-1), timedelta(0), timedelta(hours=7)]
)
async def test_invalid_prediction_horizon_does_not_mutate(engine, delta):
    before = snapshot(engine)
    with pytest.raises(temporal.TemporalValidationError, match="prediction_horizon"):
        await engine.predict_future_state(NOW + delta, {"value": 1})
    assert snapshot(engine) == before


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state",
    [
        None,
        [],
        {"x": float("nan")},
        {"x": float("inf")},
        {"x": 10**1000},
        {1: "key"},
        {"x": object()},
        {"x": "a" * 40000},
    ],
)
async def test_invalid_state_does_not_mutate_or_log_payload(engine, state, caplog):
    before = snapshot(engine)
    with pytest.raises(ValueError, match="temporal_invalid_state"):
        await engine.process_temporal_moment(state, NOW)
    assert snapshot(engine) == before
    assert "aaaaaaaaaa" not in caplog.text


@pytest.mark.asyncio
async def test_nested_integration_is_typed_and_reports_all_used_records(engine):
    for i in range(12):
        await engine.process_temporal_moment(
            {
                "nested": {"label": "kept", "values": [1, 2], "enabled": True},
                "score": 4.0,
            },
            NOW - timedelta(seconds=i),
        )
    result = await engine.temporal_memory_integration(NOW, {"nested": {}, "score": 4.0})
    assert result["integrated_state"]["nested"] == {
        "label": "kept",
        "values": [1, 2],
        "enabled": True,
    }
    assert result["integrated_state"]["score"] == pytest.approx(4)
    assert result["moments_used"] == 10
    assert len(result["contributing_moments"]) == 10
    assert not any(
        hasattr(m, "temporal_relevance") for m in engine.temporal_moments.values()
    )


@pytest.mark.asyncio
async def test_processing_failure_is_explicit_atomic_and_private(
    engine, monkeypatch, caplog
):
    await engine.process_temporal_moment({"value": 1}, NOW - timedelta(seconds=1))
    before = snapshot(engine)

    async def broken(*args, **kwargs):
        raise RuntimeError("synthetic-private-failure")

    monkeypatch.setattr(engine, "_calculate_state_similarity", broken)
    with pytest.raises(RuntimeError, match="temporal_operation_failed"):
        await engine.process_temporal_moment({"value": 2}, NOW)
    assert snapshot(engine) == before
    assert "synthetic-private-failure" not in caplog.text


@pytest.mark.asyncio
async def test_capacity_eviction_removes_dangling_references(engine):
    engine.max_moments = 3
    engine.max_predictions = 2
    engine.max_causal_chains = 2
    for i in range(7):
        await engine.process_temporal_moment(
            {"focus": "same"}, NOW - timedelta(seconds=10 - i)
        )
    predictions = [
        await engine.predict_future_state(
            NOW + timedelta(minutes=i + 1), {"focus": "same"}
        )
        for i in range(4)
    ]
    assert len(engine.temporal_moments) == 3
    assert len(engine.temporal_predictions) == 2
    assert len(engine.causal_chains) <= 2
    ids = set(engine.temporal_moments)
    for chain in engine.causal_chains.values():
        assert set(chain.cause_moments + chain.effect_moments) <= ids
    for moment in engine.temporal_moments.values():
        assert set(moment.memory_associations) <= ids
        assert set(moment.causal_influences) <= set(engine.causal_chains)
    assert predictions[-1].prediction_id in engine.temporal_predictions


@pytest.mark.asyncio
async def test_repeated_state_pattern_is_detected_without_claiming_causation(engine):
    for i, phase in enumerate(["rest", "work"] * 3):
        await engine.process_temporal_moment(
            {"phase": phase}, NOW - timedelta(seconds=6 - i)
        )
    patterns = await engine.detect_temporal_patterns(timedelta(minutes=1))
    cycles = [p for p in patterns if p["type"] == "repeating_state_cycle"]
    assert cycles[0]["period_moments"] == 2
    assert cycles[0]["repetitions"] == 3
    assert all(p.get("causation_established", False) is False for p in patterns)


@pytest.mark.asyncio
async def test_cycle_after_warmup_uses_only_the_repeated_suffix(engine):
    ids = [
        await engine.process_temporal_moment(
            {"phase": phase}, NOW - timedelta(seconds=8 - i)
        )
        for i, phase in enumerate(["boot", "ready"] + ["rest", "work"] * 3)
    ]
    patterns = await engine.detect_temporal_patterns(timedelta(minutes=1))
    cycles = [p for p in patterns if p["type"] == "repeating_state_cycle"]
    assert len(cycles) == 1
    assert cycles[0]["moments"] == ids[2:]
    assert cycles[0]["repetitions"] == 3


@pytest.mark.asyncio
async def test_existing_phase73_and_multidimensional_callers_keep_working(
    engine, monkeypatch
):
    # Aetherra imports
    from Aetherra.consciousness.quantum import (
        phase_7_3_integration,
        quantum_memory_system,
    )
    from Aetherra.consciousness.quantum.multidimensional_state_engine import (
        MultidimensionalStateEngine,
    )

    monkeypatch.setattr(temporal, "temporal_consciousness_engine", engine)
    monkeypatch.setattr(quantum_memory_system, "quantum_memory_system", None)
    integration = phase_7_3_integration.QuantumMemoryTemporalIntegration()
    key = await integration.create_integrated_consciousness_state(
        {"focus": "study", "energy": 0.6}, temporal_context=NOW
    )
    assert key in integration.integrated_states
    retrieval = await integration.enhanced_memory_retrieval(
        {"focus": "study"}, temporal_context=NOW
    )
    assert retrieval["temporal_integration"]["moments_used"] == 1
    result = await integration.temporal_prediction_with_memory(
        NOW + timedelta(minutes=1), {"energy": 0.6}
    )
    assert result["prediction_id"] in engine.temporal_predictions
    dimensional = MultidimensionalStateEngine()
    before = engine.moments_processed
    result = await dimensional.process_multidimensional_state({"energy": 0.6})
    assert "updated_consciousness" in result
    assert engine.moments_processed == before + 1


@pytest.mark.asyncio
async def test_denied_operations_leave_everything_unchanged(engine, monkeypatch):
    await engine.process_temporal_moment({"private": "protected"}, NOW)
    before = snapshot(engine)
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "external-untrusted")
    for operation in [
        engine.process_temporal_moment({"value": 2}, NOW),
        engine.predict_future_state(NOW + timedelta(minutes=1), {"value": 2}),
        engine.temporal_memory_integration(NOW, {}),
        engine.detect_temporal_patterns(timedelta(minutes=1)),
    ]:
        with pytest.raises(PermissionError):
            await operation
        assert snapshot(engine) == before


class MemoryDouble:
    def __init__(self):
        self.rows = []
        self.calls = []

    async def store_memory(self, content, **kwargs):
        self.calls.append("store")
        self.rows.append(
            SimpleNamespace(
                content=copy.deepcopy(content),
                id="memory-receipt",
                memory_type=kwargs["memory_type"],
            )
        )
        return "memory-receipt"

    async def recall_memories(self, **kwargs):
        self.calls.append("recall")
        return copy.deepcopy(self.rows)


@pytest.mark.asyncio
async def test_checkpoint_roundtrip_is_exact_and_preserves_receipt(engine):
    memory = MemoryDouble()
    engine.memory_system = memory
    mid = await engine.process_temporal_moment({"nested": {"value": 3}}, NOW)
    prediction = await engine.predict_future_state(
        NOW + timedelta(minutes=1), {"value": 3}
    )
    await engine.validate_prediction_accuracy(prediction.prediction_id, {"value": 3})
    handle = await engine.save_checkpoint()
    restored = temporal.TemporalConsciousnessEngine(memory_system=memory)
    receipt = await restored.restore_checkpoint(handle)
    assert receipt["memory_id"] == "memory-receipt"
    assert restored.temporal_moments == engine.temporal_moments
    assert restored.temporal_predictions == engine.temporal_predictions
    assert mid in restored.temporal_moments
    assert restored.moments_processed == engine.moments_processed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fault", ["empty", "duplicate", "schema", "handle", "dangling"]
)
async def test_bad_checkpoint_cannot_partially_restore(engine, fault):
    memory = MemoryDouble()
    engine.memory_system = memory
    await engine.process_temporal_moment({"private": "state"}, NOW)
    handle = await engine.save_checkpoint()
    if fault == "empty":
        memory.rows = []
    elif fault == "duplicate":
        memory.rows *= 2
    elif fault == "schema":
        memory.rows[0].content["schema"] = 999
    elif fault == "handle":
        memory.rows[0].content["checkpoint_id"] = "wrong"
    else:
        memory.rows[0].content["moments"][0]["memory_associations"] = ["missing"]
    before = snapshot(engine)
    with pytest.raises((RuntimeError, ValueError)):
        await engine.restore_checkpoint(handle)
    assert snapshot(engine) == before


@pytest.mark.asyncio
async def test_restore_conflict_cannot_discard_concurrent_work(engine):
    memory = MemoryDouble()
    engine.memory_system = memory
    await engine.process_temporal_moment({"value": 1}, NOW)
    handle = await engine.save_checkpoint()
    entered, release = asyncio.Event(), asyncio.Event()
    original = memory.recall_memories

    async def delayed(**kwargs):
        entered.set()
        await release.wait()
        return await original(**kwargs)

    memory.recall_memories = delayed
    task = asyncio.create_task(engine.restore_checkpoint(handle))
    await asyncio.wait_for(entered.wait(), 2)
    mid = await engine.process_temporal_moment({"value": 2}, NOW)
    release.set()
    with pytest.raises(RuntimeError, match="temporal_restore_conflict"):
        await task
    assert mid in engine.temporal_moments


@pytest.mark.asyncio
async def test_checkpoint_denial_precedes_memory_access(engine, monkeypatch):
    memory = MemoryDouble()
    engine.memory_system = memory
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "external-untrusted")
    with pytest.raises(PermissionError):
        await engine.save_checkpoint()
    with pytest.raises(PermissionError):
        await engine.restore_checkpoint("a" * 32)
    assert memory.calls == []


@pytest.mark.asyncio
async def test_missing_validation_record_is_an_explicit_error(engine):
    with pytest.raises(KeyError):
        await engine.validate_prediction_accuracy("missing", {"value": 1})


@pytest.mark.asyncio
@pytest.mark.parametrize("receipt", [None, "", "  ", False, 42])
async def test_unconfirmed_write_is_not_reported_as_saved(engine, receipt):
    async def store(**kwargs):
        return receipt

    engine.memory_system = SimpleNamespace(store_memory=store)
    before = snapshot(engine)
    with pytest.raises(temporal.TemporalPersistenceError, match="store_unconfirmed"):
        await engine.save_checkpoint()
    assert snapshot(engine) == before


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["save", "restore"])
async def test_memory_exception_is_explicit_and_private(engine, operation, caplog):
    async def broken(**kwargs):
        raise RuntimeError("private-memory-error")

    engine.memory_system = SimpleNamespace(store_memory=broken, recall_memories=broken)
    before = snapshot(engine)
    pending = (
        engine.save_checkpoint()
        if operation == "save"
        else engine.restore_checkpoint("a" * 32)
    )
    with pytest.raises(temporal.TemporalPersistenceError) as error:
        await pending
    assert "private-memory-error" not in str(error.value) + caplog.text
    assert snapshot(engine) == before


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["save", "restore"])
async def test_cancelled_memory_operation_keeps_engine_state(engine, operation):
    entered = asyncio.Event()

    async def suspended(**kwargs):
        entered.set()
        await asyncio.Event().wait()

    engine.memory_system = SimpleNamespace(
        store_memory=suspended, recall_memories=suspended
    )
    before = snapshot(engine)
    task = asyncio.create_task(
        engine.save_checkpoint()
        if operation == "save"
        else engine.restore_checkpoint("a" * 32)
    )
    await asyncio.wait_for(entered.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert snapshot(engine) == before


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fault",
    ["timestamp", "capacity", "state", "score", "counter", "cycle", "record_type"],
)
async def test_corrupt_checkpoint_is_rejected_atomically(engine, fault):
    engine.memory_system = memory = MemoryDouble()
    await engine.process_temporal_moment({"label": "private-state"}, NOW)
    handle = await engine.save_checkpoint()
    data = memory.rows[0].content
    if fault == "timestamp":
        data["moments"][0]["timestamp"] = "invalid-private-timestamp"
    elif fault == "capacity":
        data["moments"] *= 257
    elif fault == "state":
        data["moments"][0]["consciousness_state"] = {"large": "x" * 40000}
    elif fault == "score":
        data["moments"][0]["temporal_coherence"] = float("nan")
    elif fault == "counter":
        data["counts"][0] = -1
    elif fault == "cycle":
        data["moments"][0]["consciousness_state"]["cycle"] = data
    else:
        memory.rows[0].memory_type = "conversation"
    before = snapshot(engine)
    with pytest.raises(
        (temporal.TemporalPersistenceError, temporal.TemporalValidationError)
    ):
        await engine.restore_checkpoint(handle)
    assert snapshot(engine) == before


@pytest.mark.asyncio
async def test_future_records_do_not_inform_current_prediction_or_integration(engine):
    past = await engine.process_temporal_moment(
        {"value": 1}, NOW - timedelta(minutes=1)
    )
    future = await engine.process_temporal_moment(
        {"value": 99}, NOW + timedelta(minutes=1)
    )
    prediction = await engine.predict_future_state(
        NOW + timedelta(minutes=2), {"value": 1}
    )
    integrated = await engine.temporal_memory_integration(NOW, {"value": 1})
    assert prediction.contributing_factors == [past]
    assert integrated["contributing_moments"] == [past]
    assert future not in prediction.contributing_factors


@pytest.mark.asyncio
async def test_revalidation_replaces_accuracy_instead_of_counting_twice(engine):
    prediction = await engine.predict_future_state(
        NOW + timedelta(minutes=1), {"label": "one"}
    )
    await engine.validate_prediction_accuracy(
        prediction.prediction_id, {"label": "two"}
    )
    await engine.validate_prediction_accuracy(
        prediction.prediction_id, {"label": "one"}
    )
    assert engine.prediction_accuracy_history == [1.0]


@pytest.mark.asyncio
async def test_checkpoint_and_pattern_audit_excludes_private_payload_and_handle(
    engine, tmp_path
):
    engine.memory_system = MemoryDouble()
    await engine.process_temporal_moment({"label": "private-checkpoint-content"}, NOW)
    handle = await engine.save_checkpoint()
    await engine.restore_checkpoint(handle)
    await engine.detect_temporal_patterns(timedelta(minutes=1))
    audit = (tmp_path / ".aetherra/security/audit.jsonl").read_text(encoding="utf-8")
    assert "private-checkpoint-content" not in audit
    assert handle not in audit
    entries = [json.loads(line) for line in audit.splitlines()]
    intents = [e["details"]["intent"] for e in entries]
    assert {i["action"] for i in intents} >= {
        "consciousness.temporal_save_checkpoint",
        "consciousness.temporal_restore_checkpoint",
        "consciousness.temporal_detect_patterns",
    }
    assert all(i["reversible"] for i in intents)


@pytest.mark.asyncio
async def test_persistence_requires_explicit_memory(engine):
    with pytest.raises(temporal.TemporalPersistenceError, match="memory_unavailable"):
        await engine.save_checkpoint()
    with pytest.raises(temporal.TemporalPersistenceError, match="memory_unavailable"):
        await engine.restore_checkpoint("a" * 32)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fault", ["naive_time", "future_contributor", "future_association", "history_count"]
)
async def test_checkpoint_rejects_inconsistent_temporal_evidence(engine, fault):
    engine.memory_system = memory = MemoryDouble()
    await engine.process_temporal_moment({"value": 1}, NOW)
    await engine.predict_future_state(NOW + timedelta(minutes=1), {"value": 1})
    handle = await engine.save_checkpoint()
    data = memory.rows[0].content
    if fault == "naive_time":
        data["moments"][0]["timestamp"] = NOW.replace(tzinfo=None).isoformat()
    elif fault == "future_contributor":
        data["moments"][0]["timestamp"] = (NOW + timedelta(seconds=1)).isoformat()
    elif fault == "future_association":
        later = copy.deepcopy(data["moments"][0])
        later["moment_id"] = "moment_" + "a" * 32
        later["timestamp"] = (NOW + timedelta(seconds=1)).isoformat()
        data["moments"][0]["memory_associations"] = [later["moment_id"]]
        data["moments"].append(later)
        data["counts"][0] += 1
    else:
        data["moments"], data["predictions"], data["counts"] = [], [], [0, 0, 0]
        data["coherence_history"], data["accuracy_history"] = [1], [1]
    before = snapshot(engine)
    with pytest.raises(temporal.TemporalValidationError, match="checkpoint_invalid"):
        await engine.restore_checkpoint(handle)
    assert snapshot(engine) == before
