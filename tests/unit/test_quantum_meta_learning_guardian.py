import json

import numpy as np
import pytest

from Aetherra.consciousness.quantum.meta_learning import QuantumMetaLearningSystem


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
        "quantum_states": dict(system.quantum_states),
        "learning_history": list(system.learning_history),
        "coherence_matrix": system.coherence_matrix.copy(),
        "consciousness_resonance": system.consciousness_resonance,
        "entanglement_network": dict(system.entanglement_network),
    }


def _assert_snapshot_equal(left, right):
    assert left["quantum_states"] == right["quantum_states"]
    assert left["learning_history"] == right["learning_history"]
    np.testing.assert_array_equal(left["coherence_matrix"], right["coherence_matrix"])
    assert left["consciousness_resonance"] == right["consciousness_resonance"]
    assert left["entanglement_network"] == right["entanglement_network"]


def test_quantum_meta_memory_enhancement_is_guardian_audited(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(np.random, "random", lambda: 1.0)
    system = QuantumMetaLearningSystem()

    result = system.quantum_enhance_meta_memory(target_coverage=0.91)

    assert result["target_coverage"] == 0.91
    assert result["estimated_final_coverage"] > result["initial_coverage"]
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_meta_learning_enhance_meta_memory"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "enhance_meta_memory"
    assert metadata["target_coverage"] == 0.91
    assert metadata["quantum_state_count"] == 0


def test_domain_learning_acceleration_is_guardian_audited_without_domain(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    system = QuantumMetaLearningSystem()
    domain = "private-cognitive-domain"

    acceleration = system.accelerate_domain_learning(domain, acceleration_factor=2.5)

    assert acceleration > 0
    ledger_text = _audit_text(tmp_path)
    assert domain not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_meta_learning_accelerate_domain_learning"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "accelerate_domain_learning"
    assert metadata["acceleration_factor"] == 2.5
    assert metadata["domain_hash"]


def test_quantum_meta_memory_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-learning-client",
        strict=True,
    )
    system = QuantumMetaLearningSystem()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        system.quantum_enhance_meta_memory(target_coverage=0.91)

    _assert_snapshot_equal(_snapshot(system), before)
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_meta_learning_enhance_meta_memory"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_domain_learning_denial_preserves_state_and_sanitizes_audit(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-quantum-learning-client",
        strict=True,
    )
    system = QuantumMetaLearningSystem()
    before = _snapshot(system)
    domain = "private-learning-domain"

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        system.accelerate_domain_learning(domain, acceleration_factor=3.0)

    _assert_snapshot_equal(_snapshot(system), before)
    ledger_text = _audit_text(tmp_path)
    assert domain not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.quantum_meta_learning_accelerate_domain_learning"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
