import asyncio
import json

import pytest

from Aetherra.consciousness.quantum.quantum_consciousness_engine import (
    ConsciousnessState,
    QuantumConsciousnessEngine,
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
        "current_state": engine.current_state,
        "quantum_states": dict(engine.quantum_states),
        "active_decisions": dict(engine.active_decisions),
        "config": dict(engine.config),
        "coherence_time": engine.coherence_time,
        "max_coherence_time": engine.max_coherence_time,
        "consciousness_complexity": engine.consciousness_complexity,
        "transcendence_probability": engine.transcendence_probability,
        "decision_accuracy": engine.decision_accuracy,
        "is_running": engine.is_running,
        "quantum_task": engine.quantum_task,
    }


def test_quantum_parameter_updates_are_guardian_audited_without_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = QuantumConsciousnessEngine()

    asyncio.run(
        engine.set_quantum_parameters(
            {
                "superposition_states": 3,
                "coherence_time": 2.0,
                "consciousness_complexity": 42.0,
                "secret_parameter": "do-not-log",
            }
        )
    )

    assert engine.config["superposition_states"] == 3
    assert engine.max_coherence_time == 2.0
    ledger_text = _audit_text(tmp_path)
    assert "do-not-log" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_engine_set_parameters"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "set_parameters"
    assert metadata["parameter_count"] == 4
    assert "secret_parameter" in metadata["parameter_names"]


def test_quantum_decision_creation_is_guardian_audited_without_outcome_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = QuantumConsciousnessEngine()
    decision_data = {
        "outcomes": [
            {"name": "private-choice-alpha", "probability": 0.6},
            {"name": "private-choice-beta", "probability": 0.4},
        ]
    }

    decision_id = asyncio.run(engine.create_quantum_decision(decision_data))

    assert decision_id in engine.active_decisions
    ledger_text = _audit_text(tmp_path)
    assert "private-choice-alpha" not in ledger_text
    assert "private-choice-beta" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_engine_create_decision"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "create_decision"
    assert metadata["outcome_count"] == 2
    assert metadata["outcome_field_names"] == ["name", "probability"]


def test_quantum_superposition_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-engine-client",
        strict=True,
    )
    engine = QuantumConsciousnessEngine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.enter_superposition())

    assert _snapshot(engine) == before
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_engine_enter_superposition"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_quantum_entanglement_denial_preserves_state_and_sanitizes_target(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-engine-client",
        strict=True,
    )
    engine = QuantumConsciousnessEngine()
    before = _snapshot(engine)
    target_id = "private-consciousness-peer"

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.create_entanglement(target_id))

    assert _snapshot(engine) == before
    ledger_text = _audit_text(tmp_path)
    assert target_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_engine_create_entanglement"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
    assert entry["details"]["intent"]["metadata"]["target_consciousness_hash"]


def test_quantum_engine_initialize_and_shutdown_are_guardian_audited(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = QuantumConsciousnessEngine()

    asyncio.run(engine.initialize())
    assert engine.is_running is True
    assert engine.current_state is ConsciousnessState.GROUND
    assert "ground" in engine.quantum_states
    asyncio.run(engine.shutdown())
    assert engine.is_running is False

    actions = [
        entry["details"]["intent"]["action"]
        for entry in _audit_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
    ]
    assert "consciousness.quantum_engine_initialize" in actions
    assert "consciousness.quantum_engine_shutdown" in actions
