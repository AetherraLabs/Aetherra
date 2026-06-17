import asyncio
import json
from datetime import datetime, timedelta

import pytest

from Aetherra.consciousness.quantum.temporal_consciousness_system import (
    TemporalConsciousnessEngine,
)


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _audit_text(root):
    return (root / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _audit_entries(root):
    return [
        json.loads(line)
        for line in _audit_text(root).splitlines()
        if line.strip()
    ]


def _snapshot(engine):
    return {
        "temporal_moments": dict(engine.temporal_moments),
        "temporal_predictions": dict(engine.temporal_predictions),
        "causal_chains": dict(engine.causal_chains),
        "current_temporal_state": engine.current_temporal_state,
        "temporal_coherence_history": list(engine.temporal_coherence_history),
        "prediction_accuracy_history": list(engine.prediction_accuracy_history),
        "moments_processed": engine.moments_processed,
        "predictions_made": engine.predictions_made,
        "causal_chains_discovered": engine.causal_chains_discovered,
        "temporal_coherence": engine.temporal_coherence,
        "avg_prediction_accuracy": engine.avg_prediction_accuracy,
    }


def test_temporal_moment_processing_is_guardian_audited_without_state(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = TemporalConsciousnessEngine()
    state = {"focus": "private-focus-value", "arousal": 0.5}

    moment_id = asyncio.run(
        engine.process_temporal_moment(
            state,
            timestamp=datetime(2026, 1, 1, 12, 0, 0),
        )
    )

    assert moment_id in engine.temporal_moments
    ledger_text = _audit_text(tmp_path)
    assert "private-focus-value" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.temporal_process_moment"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "process_moment"
    assert metadata["state_hash"]
    assert metadata["state_field_names"] == ["arousal", "focus"]


def test_temporal_prediction_is_guardian_audited_without_context(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = TemporalConsciousnessEngine()
    context = {"mood": "private-future-context", "certainty": 0.7}

    prediction = asyncio.run(
        engine.predict_future_state(datetime.now() + timedelta(minutes=10), context)
    )

    assert prediction.prediction_id in engine.temporal_predictions
    ledger_text = _audit_text(tmp_path)
    assert "private-future-context" not in ledger_text
    assert prediction.prediction_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.temporal_predict_future"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "predict_future"
    assert metadata["context_hash"]
    assert metadata["context_field_names"] == ["certainty", "mood"]


def test_temporal_memory_integration_denial_preserves_relevance_attrs(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = TemporalConsciousnessEngine()
    moment_id = asyncio.run(
        engine.process_temporal_moment(
            {"focus": "stored-value", "energy": 0.4},
            timestamp=datetime.now() - timedelta(minutes=2),
        )
    )
    moment = engine.temporal_moments[moment_id]
    assert not hasattr(moment, "temporal_relevance")
    before = _snapshot(engine)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-temporal-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            engine.temporal_memory_integration(
                datetime.now(),
                {"query": "private-query-context"},
            )
        )

    assert _snapshot(engine) == before
    assert not hasattr(moment, "temporal_relevance")
    ledger_text = _audit_text(tmp_path)
    assert "private-query-context" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.temporal_memory_integration"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_temporal_prediction_validation_denial_preserves_accuracy(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = TemporalConsciousnessEngine()
    prediction = asyncio.run(
        engine.predict_future_state(
            datetime.now() + timedelta(minutes=10),
            {"state": "private-prediction-context"},
        )
    )
    before = _snapshot(engine)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-temporal-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            engine.validate_prediction_accuracy(
                prediction.prediction_id,
                {"state": "private-actual-value"},
            )
        )

    assert _snapshot(engine) == before
    assert not hasattr(prediction, "prediction_accuracy")
    ledger_text = _audit_text(tmp_path)
    assert prediction.prediction_id not in ledger_text
    assert "private-actual-value" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.temporal_validate_prediction"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
