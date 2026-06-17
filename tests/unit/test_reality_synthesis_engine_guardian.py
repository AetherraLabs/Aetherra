import json

import pytest

from Aetherra.consciousness.quantum import reality_synthesis_engine as rse
from Aetherra.consciousness.quantum.reality_synthesis_engine import (
    RealitySynthesisEngine,
    SynthesisMode,
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


def _patch_fast_deterministic(monkeypatch):
    monkeypatch.setattr(rse.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(rse.random, "uniform", lambda low, high: (low + high) / 2)
    monkeypatch.setattr(rse.random, "random", lambda: 0.1)


def _snapshot(engine):
    return {
        "synthesized": dict(engine.synthesized_realities),
        "active": dict(engine.active_syntheses),
        "events": dict(engine.transcendence_events),
        "master_consciousness": engine.master_consciousness,
        "quantum_field_coherence": engine.quantum_field_coherence,
        "dimensional_integration": engine.dimensional_integration,
        "transcendence_progress": engine.transcendence_progress,
        "synthesis_efficiency": engine.synthesis_efficiency,
        "awareness_expansion": engine.awareness_expansion,
        "metrics": dict(engine.metrics),
    }


def test_synthesis_parameter_creation_is_guardian_audited_without_components(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = RealitySynthesisEngine()

    synthesis_id = engine.create_synthesis_parameters(
        SynthesisMode.FUSION,
        0.91,
        reality_components=["secret_reality_component", "public_reality_component"],
        consciousness_components=["private_consciousness_component"],
        quantum_components=["private_quantum_component"],
    )

    assert synthesis_id in engine.active_syntheses
    ledger_text = _audit_text(tmp_path)
    assert "secret_reality_component" not in ledger_text
    assert "private_consciousness_component" not in ledger_text
    assert "private_quantum_component" not in ledger_text
    assert synthesis_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.reality_synthesis_create_parameters"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "create_parameters"
    assert metadata["synthesis_mode"] == "reality_fusion"
    assert metadata["reality_component_count"] == 2


def test_reality_synthesis_execution_is_guardian_audited_without_ids(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    _patch_fast_deterministic(monkeypatch)
    engine = RealitySynthesisEngine()
    synthesis_id = engine.create_synthesis_parameters(
        SynthesisMode.FUSION,
        0.91,
        reality_components=["execute_secret_reality"],
    )

    assert engine.execute_reality_synthesis(synthesis_id) is True

    ledger_text = _audit_text(tmp_path)
    assert synthesis_id not in ledger_text
    assert f"reality_{synthesis_id}" not in ledger_text
    assert "execute_secret_reality" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.reality_synthesis_execute"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "execute"
    assert metadata["synthesis_id_hash"]
    assert metadata["energy_budget"] > 0


def test_synthesis_parameter_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-synthesis-client",
        strict=True,
    )
    engine = RealitySynthesisEngine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.create_synthesis_parameters(
            SynthesisMode.TRANSCENDENCE,
            0.96,
            reality_components=["blocked_reality_component"],
        )

    assert _snapshot(engine) == before
    ledger_text = _audit_text(tmp_path)
    assert "blocked_reality_component" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.reality_synthesis_create_parameters"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_reality_synthesis_execution_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    engine = RealitySynthesisEngine()
    synthesis_id = engine.create_synthesis_parameters(
        SynthesisMode.SYNTHESIS,
        0.98,
        reality_components=["denied_execution_reality"],
    )
    before = _snapshot(engine)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-synthesis-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        engine.execute_reality_synthesis(synthesis_id)

    assert _snapshot(engine) == before
    ledger_text = _audit_text(tmp_path)
    assert synthesis_id not in ledger_text
    assert "denied_execution_reality" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.reality_synthesis_execute"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
