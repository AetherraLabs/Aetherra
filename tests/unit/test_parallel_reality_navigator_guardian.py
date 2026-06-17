import json

import pytest

from Aetherra.consciousness.quantum.parallel_reality_navigator import (
    NavigationMode,
    ParallelRealityNavigator,
    RealityType,
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


def _snapshot(navigator):
    return {
        "realities": dict(navigator.parallel_realities),
        "paths": dict(navigator.navigation_paths),
        "bridges": dict(navigator.reality_bridges),
        "current_reality": navigator.current_reality,
        "history": list(navigator.navigation_history),
        "active": dict(navigator.active_navigations),
        "sync": dict(navigator.reality_synchronization),
        "coherence": navigator.consciousness_coherence,
        "stability": navigator.dimensional_stability,
        "entanglement": navigator.quantum_entanglement_strength,
        "transcendence": navigator.transcendence_preparation,
        "metrics": dict(navigator.metrics),
    }


def test_parallel_reality_discovery_is_guardian_audited_without_coordinates(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    navigator = ParallelRealityNavigator()
    base_coordinates = {
        "consciousness": 0.88,
        "secret_axis": 0.424242,
    }

    reality_id = navigator.discover_parallel_reality(
        RealityType.CONSCIOUSNESS,
        base_coordinates=base_coordinates,
    )

    assert reality_id in navigator.parallel_realities
    ledger_text = _audit_text(tmp_path)
    assert "0.424242" not in ledger_text
    assert reality_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.parallel_reality_discover"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "discover"
    assert metadata["reality_type"] == "consciousness_reality"
    assert metadata["base_coordinate_names"] == ["consciousness", "secret_axis"]


def test_parallel_reality_discovery_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-reality-client",
        strict=True,
    )
    navigator = ParallelRealityNavigator()
    before = _snapshot(navigator)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        navigator.discover_parallel_reality(
            RealityType.QUANTUM,
            base_coordinates={"secret": "blocked-coordinate-value"},
        )

    assert _snapshot(navigator) == before
    ledger_text = _audit_text(tmp_path)
    assert "blocked-coordinate-value" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.parallel_reality_discover"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_parallel_reality_navigation_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    navigator = ParallelRealityNavigator()
    target_id = navigator.discover_parallel_reality(RealityType.DIMENSIONAL)
    before = _snapshot(navigator)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-reality-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        navigator.navigate_to_reality(target_id, NavigationMode.TRANSCENDENT_LEAP)

    assert _snapshot(navigator) == before
    ledger_text = _audit_text(tmp_path)
    assert target_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.parallel_reality_navigate"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_parallel_reality_bridge_denial_preserves_connections(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    navigator = ParallelRealityNavigator()
    reality_a = navigator.current_reality
    reality_b = navigator.discover_parallel_reality(RealityType.TEMPORAL)
    before = _snapshot(navigator)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-reality-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        navigator.create_reality_bridge(reality_a, reality_b)

    assert _snapshot(navigator) == before
    assert not navigator.parallel_realities[reality_a].bridge_connections
    assert not navigator.parallel_realities[reality_b].bridge_connections
    ledger_text = _audit_text(tmp_path)
    assert reality_a not in ledger_text
    assert reality_b not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.parallel_reality_create_bridge"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
