import asyncio
import json
from datetime import datetime, timedelta

import pytest

from Aetherra.consciousness.quantum import phase_7_3_integration as integration_module
from Aetherra.consciousness.quantum import (
    quantum_memory_system,
    temporal_consciousness_system,
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


def _fresh_integration():
    quantum_memory_system.quantum_memory_system = None
    temporal_consciousness_system.temporal_consciousness_engine = None
    integration_module.quantum_memory_temporal_integration = None
    return integration_module.QuantumMemoryTemporalIntegration()


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


def _snapshot(system):
    return {
        "integrated_states": dict(system.integrated_states),
        "bridges": dict(system.memory_temporal_bridges),
        "evolution_history": list(system.consciousness_evolution_history),
        "states_integrated": system.states_integrated,
        "bridges_created": system.bridges_created,
        "evolution_events": system.consciousness_evolution_events,
        "avg_integration_strength": system.avg_integration_strength,
        "temporal_memory_coherence": system.temporal_memory_coherence,
        "memory_count": len(system.memory_system.memory_traces),
        "moment_count": len(system.temporal_system.temporal_moments),
        "prediction_count": len(system.temporal_system.temporal_predictions),
    }


def test_integrated_consciousness_state_is_guardian_audited_without_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    system = _fresh_integration()
    consciousness_data = {"focus": "private-integrated-focus", "certainty": 0.8}

    state_id = asyncio.run(
        system.create_integrated_consciousness_state(
            consciousness_data,
            temporal_context=datetime(2026, 1, 1, 12, 0, 0),
        )
    )

    assert state_id in system.integrated_states
    ledger_text = _audit_text(tmp_path)
    assert "private-integrated-focus" not in ledger_text
    assert state_id not in ledger_text
    entry = next(
        entry
        for entry in _audit_entries(tmp_path)
        if entry["details"]["intent"]["action"]
        == "consciousness.memory_temporal_integration_create_state"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "create_state"
    assert metadata["consciousness_hash"]
    assert metadata["consciousness_field_names"] == ["certainty", "focus"]


def test_integrated_consciousness_state_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-integration-client",
        strict=True,
    )
    system = _fresh_integration()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            system.create_integrated_consciousness_state(
                {"focus": "blocked-integrated-focus"},
                temporal_context=datetime(2026, 1, 1, 12, 0, 0),
            )
        )

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert "blocked-integrated-focus" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.memory_temporal_integration_create_state"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_enhanced_retrieval_denial_preserves_state_and_query(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-integration-client",
        strict=True,
    )
    system = _fresh_integration()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            system.enhanced_memory_retrieval(
                {"topic": "private-retrieval-query"},
                temporal_context=datetime.now(),
                temporal_window=timedelta(minutes=5),
            )
        )

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert "private-retrieval-query" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.memory_temporal_integration_enhanced_retrieval"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_evolution_processing_denial_preserves_history_and_trigger(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-integration-client",
        strict=True,
    )
    system = _fresh_integration()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            system.consciousness_evolution_processing(
                {"trigger": "private-evolution-trigger", "strength": 1.0}
            )
        )

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert "private-evolution-trigger" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.memory_temporal_integration_evolution_processing"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
