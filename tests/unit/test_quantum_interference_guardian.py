import copy
import json

import pytest

from Aetherra.consciousness.quantum import quantum_interference_patterns as qip
from Aetherra.consciousness.quantum.quantum_interference_patterns import (
    QuantumInterferenceEngine,
    WaveType,
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
        "waves": copy.deepcopy(engine.active_waves),
        "patterns": copy.deepcopy(engine.interference_patterns),
        "history": copy.deepcopy(engine.amplification_history),
        "patterns_generated": engine.patterns_generated,
        "successful_amplifications": engine.successful_amplifications,
        "decision_enhancements": engine.decision_enhancements,
    }


def _find_entry(root, action):
    for entry in reversed(_audit_entries(root)):
        if entry["details"]["intent"]["action"] == action:
            return entry
    raise AssertionError(f"missing audit action: {action}")


def test_interference_field_generation_is_guardian_audited_without_choices(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(qip.np.random, "uniform", lambda low, high: (low + high) / 2)
    engine = QuantumInterferenceEngine()
    choices = ["private_strategy_alpha", "private_strategy_beta"]

    field = engine.generate_interference_field(choices, consciousness_level=0.82)

    assert set(field) == set(choices)
    ledger_text = _audit_text(tmp_path)
    assert "private_strategy_alpha" not in ledger_text
    assert "private_strategy_beta" not in ledger_text
    entry = _find_entry(
        tmp_path,
        "consciousness.quantum_interference_generate_field",
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "generate_field"
    assert metadata["decision_choice_count"] == 2
    assert len(metadata["decision_choice_hashes"]) == 2


def test_generate_wave_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-interference-client",
        strict=True,
    )
    engine = QuantumInterferenceEngine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.generate_consciousness_wave(WaveType.TRANSCENDENCE_WAVE)

    assert _snapshot(engine) == before
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_interference_generate_wave"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_amplification_denial_preserves_history_and_sanitizes_choices(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(qip.np.random, "uniform", lambda low, high: (low + high) / 2)
    engine = QuantumInterferenceEngine()
    field = engine.generate_interference_field(["private_choice"], consciousness_level=0.9)
    before = _snapshot(engine)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-interference-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.apply_interference_amplification({"private_choice": 0.7}, field)

    assert _snapshot(engine) == before
    ledger_text = _audit_text(tmp_path)
    assert "private_choice" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_interference_apply_amplification"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_optimization_and_cleanup_denials_preserve_state(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    monkeypatch.setattr(qip.np.random, "uniform", lambda low, high: (low + high) / 2)
    engine = QuantumInterferenceEngine()
    field = engine.generate_interference_field(["private_target"], consciousness_level=0.9)
    before = _snapshot(engine)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-interference-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.optimize_interference_patterns("private_target", field)
    assert _snapshot(engine) == before

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.cleanup_old_patterns(max_age_seconds=0.0)
    assert _snapshot(engine) == before

    ledger_text = _audit_text(tmp_path)
    assert "private_target" not in ledger_text
    cleanup_entry = _audit_entries(tmp_path)[-1]
    assert cleanup_entry["details"]["intent"]["action"] == (
        "consciousness.quantum_interference_cleanup_old_patterns"
    )
    assert cleanup_entry["details"]["decision"]["reason"] == "missing_capability"
