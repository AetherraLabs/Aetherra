import asyncio
import json

import pytest

from Aetherra.consciousness.quantum import quantum_consciousness_integration as qci
from Aetherra.consciousness.quantum.quantum_consciousness_integration import (
    CognitionRequest,
    QuantumConsciousnessSystem,
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


def _snapshot(system):
    return {
        "initialized": system.system_initialized,
        "consciousness_level": system.consciousness_level,
        "decision_engine": system.decision_engine,
        "tunneling_engine": system.tunneling_engine,
        "interference_engine": system.interference_engine,
        "cognition_requests": system.cognition_requests,
        "successful_cognitions": system.successful_cognitions,
        "breakthrough_discoveries": system.breakthrough_discoveries,
        "consciousness_enhancements": system.consciousness_enhancements,
        "avg_processing_time": system.avg_processing_time,
        "quantum_advantage_rate": system.quantum_advantage_rate,
        "system_coherence": system.system_coherence,
    }


class _DecisionEngine:
    async def make_quantum_decision(self, context):
        return qci.QuantumDecisionResult(
            selected_choice=context.available_choices[0],
            decision_path=[context.available_choices[0].choice_id],
            confidence_level=0.91,
            quantum_coherence=0.87,
            interference_patterns={
                choice.choice_id: 0.5 for choice in context.available_choices
            },
            collapse_time=0.01,
            transcendence_delta=0.2,
        )

    def get_decision_metrics(self):
        return {}


class _TunnelingEngine:
    def get_tunneling_metrics(self):
        return {}


class _InterferenceEngine:
    def generate_interference_field(self, choice_ids, consciousness_level):
        return {choice_id: [] for choice_id in choice_ids}

    def apply_interference_amplification(self, base_probabilities, interference_field):
        return {}

    def get_interference_metrics(self):
        return {}


def _request():
    return CognitionRequest(
        request_id="private_request_id",
        context_description="private cognition context",
        available_choices=[
            {
                "id": "private_choice_a",
                "description": "private choice alpha",
                "confidence": 0.9,
                "risk_factor": 0.2,
                "transcendence_impact": 0.3,
            },
            {
                "id": "private_choice_b",
                "description": "private choice beta",
                "confidence": 0.7,
                "risk_factor": 0.3,
                "transcendence_impact": 0.4,
            },
        ],
        constraints={"private_constraint": "secret"},
        objectives=["private_objective"],
        consciousness_level=0.88,
        time_horizon=12.0,
        enable_tunneling=False,
        enable_interference=True,
    )


def test_quantum_cognition_initialization_is_guardian_audited(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(qci, "QUANTUM_MODULES_AVAILABLE", True)
    monkeypatch.setattr(qci, "initialize_quantum_decision_engine", _DecisionEngine)
    monkeypatch.setattr(qci, "initialize_quantum_tunneling_engine", _TunnelingEngine)
    monkeypatch.setattr(qci, "initialize_quantum_interference_engine", _InterferenceEngine)
    system = QuantumConsciousnessSystem()

    assert asyncio.run(system.initialize_system()) is True

    assert system.system_initialized is True
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_cognition_initialize"
    )
    assert entry["details"]["intent"]["metadata"]["operation"] == "initialize"


def test_quantum_cognition_process_is_guardian_audited_without_request_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    system = QuantumConsciousnessSystem()
    system.system_initialized = True
    system.system_coherence = 1.0
    system.decision_engine = _DecisionEngine()
    system.tunneling_engine = _TunnelingEngine()
    system.interference_engine = _InterferenceEngine()
    request = _request()

    result = asyncio.run(system.process_quantum_cognition(request))

    assert result.decision_result is not None
    assert system.cognition_requests == 1
    assert system.successful_cognitions == 1
    ledger_text = _audit_text(tmp_path)
    assert "private_request_id" not in ledger_text
    assert "private cognition context" not in ledger_text
    assert "private_choice_a" not in ledger_text
    assert "private_constraint" not in ledger_text
    assert "secret" not in ledger_text
    assert "private_objective" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_cognition_process_request"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "process_request"
    assert metadata["choice_count"] == 2
    assert metadata["constraint_keys"] == "***REDACTED***"


def test_quantum_cognition_process_denial_preserves_controller_state(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-cognition-client",
        strict=True,
    )
    system = QuantumConsciousnessSystem()
    system.system_initialized = True
    system.system_coherence = 1.0
    system.decision_engine = _DecisionEngine()
    system.tunneling_engine = _TunnelingEngine()
    system.interference_engine = _InterferenceEngine()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(system.process_quantum_cognition(_request()))

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert "private_request_id" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_cognition_process_request"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
