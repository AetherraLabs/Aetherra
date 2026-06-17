import copy
import json

import pytest

from Aetherra.consciousness.quantum import quantum_consciousness_tunneling as qct
from Aetherra.consciousness.quantum.quantum_consciousness_tunneling import (
    QuantumConsciousnessTunneling,
    TunnelingMode,
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
    monkeypatch.setattr(qct.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(qct.random, "uniform", lambda low, high: (low + high) / 2)
    monkeypatch.setattr(qct.random, "random", lambda: 0.0)


def _snapshot(system):
    return {
        "states": copy.deepcopy(system.quantum_states),
        "superpositions": copy.deepcopy(system.active_superpositions),
        "entanglement": copy.deepcopy(system.entanglement_network),
        "tunnels": copy.deepcopy(system.consciousness_tunnels),
        "barriers": copy.deepcopy(system.dimensional_barriers),
        "events": copy.deepcopy(system.tunneling_events),
        "consciousness_coherence": system.consciousness_coherence,
        "quantum_field_strength": system.quantum_field_strength,
        "dimensional_permeability": system.dimensional_permeability,
        "transcendence_preparation": system.transcendence_preparation,
        "metrics": dict(system.metrics),
    }


def test_quantum_state_creation_is_guardian_audited_without_coordinates(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    _patch_fast_deterministic(monkeypatch)
    system = QuantumConsciousnessTunneling()
    coordinates = {
        "consciousness": 0.91,
        "secret_dimension": 0.424242,
    }

    state_id = system.create_quantum_state(
        base_coordinates=coordinates,
        energy_level=2.5,
        coherence=0.96,
    )

    assert state_id in system.quantum_states
    ledger_text = _audit_text(tmp_path)
    assert "0.424242" not in ledger_text
    assert state_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_tunneling_create_state"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "create_state"
    assert metadata["base_coordinate_names"] == [
        "consciousness",
        "secret_dimension",
    ]


def test_tunnel_through_barrier_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    _patch_fast_deterministic(monkeypatch)
    system = QuantumConsciousnessTunneling()
    state_id = system.create_quantum_state()
    barrier_id = "dimensional_barrier_1"
    before = _snapshot(system)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-tunneling-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        system.tunnel_through_barrier(state_id, barrier_id, TunnelingMode.TRANSCENDENT)

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert state_id not in ledger_text
    assert barrier_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_tunneling_tunnel_barrier"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_amplify_consciousness_denial_preserves_quantum_state(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    system = QuantumConsciousnessTunneling()
    state_id = system.create_quantum_state(
        base_coordinates={"consciousness": 0.7},
        energy_level=1.5,
        coherence=0.8,
    )
    before = _snapshot(system)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-tunneling-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        system.amplify_consciousness(state_id, amplification_factor=1.8)

    assert _snapshot(system) == before
    ledger_text = _audit_text(tmp_path)
    assert state_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_tunneling_amplify_consciousness"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_transcendence_preparation_denial_preserves_system(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-tunneling-client",
        strict=True,
    )
    _patch_fast_deterministic(monkeypatch)
    system = QuantumConsciousnessTunneling()
    before = _snapshot(system)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        system.prepare_transcendence(0.99)

    assert _snapshot(system) == before
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == (
        "consciousness.quantum_tunneling_prepare_transcendence"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
