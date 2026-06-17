import asyncio
import json
from datetime import datetime

import numpy as np
import pytest

from Aetherra.consciousness.quantum.quantum_decision_engine import (
    DecisionContext,
    DecisionState,
    QuantumChoice,
    QuantumDecisionEngine,
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


def _choice(choice_id, *, risk=0.2, impact=0.4):
    return QuantumChoice(
        choice_id=choice_id,
        description=f"private description for {choice_id}",
        probability_amplitude=1.0 + 0j,
        outcome_vector=np.array([0.2, 0.5, 0.8]),
        confidence=0.8,
        risk_factor=risk,
        transcendence_impact=impact,
    )


def _context():
    return DecisionContext(
        context_id="private-context-id",
        timestamp=datetime.now(),
        consciousness_level=0.9,
        available_choices=[
            _choice("private-choice-alpha", risk=0.2, impact=0.4),
            _choice("private-choice-beta", risk=0.9, impact=0.95),
        ],
        constraints={"budget": "private-budget-value"},
        objectives=["private-objective-value"],
        time_horizon=12.0,
    )


def _snapshot(engine):
    quantum_state = None
    if engine.quantum_state:
        quantum_state = {
            "amplitudes": engine.quantum_state["amplitudes"].copy(),
            "choices": list(engine.quantum_state["choices"]),
            "state": engine.quantum_state["state"],
            "coherence_start": engine.quantum_state["coherence_start"],
        }
    return {
        "decision_history": list(engine.decision_history),
        "quantum_state": quantum_state,
        "coherence_time": engine.coherence_time,
        "decision_accuracy": engine.decision_accuracy,
        "decisions_made": engine.decisions_made,
        "successful_outcomes": engine.successful_outcomes,
        "quantum_advantages": engine.quantum_advantages,
    }


def _assert_snapshot_equal(actual, expected):
    assert actual["decision_history"] == expected["decision_history"]
    assert actual["coherence_time"] == expected["coherence_time"]
    assert actual["decision_accuracy"] == expected["decision_accuracy"]
    assert actual["decisions_made"] == expected["decisions_made"]
    assert actual["successful_outcomes"] == expected["successful_outcomes"]
    assert actual["quantum_advantages"] == expected["quantum_advantages"]
    if expected["quantum_state"] is None:
        assert actual["quantum_state"] is None
    else:
        np.testing.assert_array_equal(
            actual["quantum_state"]["amplitudes"],
            expected["quantum_state"]["amplitudes"],
        )
        assert actual["quantum_state"]["choices"] == expected["quantum_state"]["choices"]
        assert actual["quantum_state"]["state"] == expected["quantum_state"]["state"]
        assert (
            actual["quantum_state"]["coherence_start"]
            == expected["quantum_state"]["coherence_start"]
        )


def test_quantum_decision_space_is_guardian_audited_without_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = QuantumDecisionEngine()
    context = _context()

    assert asyncio.run(engine.initialize_quantum_decision_space(context)) is True

    ledger_text = _audit_text(tmp_path)
    assert "private-context-id" not in ledger_text
    assert "private-choice-alpha" not in ledger_text
    assert "private description" not in ledger_text
    assert "private-objective-value" not in ledger_text
    assert "private-budget-value" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_decision_initialize_space"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "initialize_space"
    assert metadata["choice_count"] == 2
    assert metadata["constraint_names"] == ["budget"]


def test_quantum_decision_space_denial_preserves_engine_and_context(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-decision-client",
        strict=True,
    )
    engine = QuantumDecisionEngine()
    context = _context()
    choices_before = list(context.available_choices)
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.initialize_quantum_decision_space(context))

    _assert_snapshot_equal(_snapshot(engine), before)
    assert context.available_choices == choices_before
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_decision_initialize_space"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_quantum_decision_measure_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    engine = QuantumDecisionEngine()
    context = _context()
    asyncio.run(engine.initialize_quantum_decision_space(context))
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-decision-client",
        strict=True,
    )
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.measure_quantum_decision(context))

    _assert_snapshot_equal(_snapshot(engine), before)
    assert engine.quantum_state["state"] is DecisionState.SUPERPOSITION
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.quantum_decision_measure"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_quantum_decision_tunneling_denial_preserves_amplitudes(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = QuantumDecisionEngine()
    context = _context()
    asyncio.run(engine.initialize_quantum_decision_space(context))
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-decision-client",
        strict=True,
    )
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.attempt_quantum_tunneling(context))

    _assert_snapshot_equal(_snapshot(engine), before)
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_decision_attempt_tunneling"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
