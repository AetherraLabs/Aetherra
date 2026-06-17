import asyncio
import json

import pytest

from Aetherra.consciousness.quantum import (
    quantum_memory_system,
    temporal_consciousness_system,
)
from Aetherra.consciousness.quantum.multidimensional_state_engine import (
    DimensionalAxis,
    MultidimensionalStateEngine,
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


def _fresh_engine():
    quantum_memory_system.quantum_memory_system = None
    temporal_consciousness_system.temporal_consciousness_engine = None
    return MultidimensionalStateEngine()


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
        "coordinates": dict(engine.dimensional_coordinates),
        "transitions": dict(engine.dimensional_transitions),
        "navigation_paths": dict(engine.navigation_paths),
        "current_position": engine.current_position,
        "history": list(engine.dimensional_history),
        "coordinates_processed": engine.coordinates_processed,
        "transitions_executed": engine.transitions_executed,
        "navigation_paths_created": engine.navigation_paths_created,
        "memory_count": len(engine.memory_system.memory_traces),
        "temporal_moment_count": len(engine.temporal_system.temporal_moments),
    }


def test_dimensional_coordinate_creation_is_guardian_audited_without_metadata(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = _fresh_engine()
    metadata = {"secret": "private-dimensional-metadata"}

    coordinate_id = asyncio.run(
        engine.create_dimensional_coordinate(
            {
                DimensionalAxis.CONSCIOUSNESS: 0.9,
                DimensionalAxis.MEMORY: 0.8,
            },
            metadata=metadata,
        )
    )

    assert coordinate_id in engine.dimensional_coordinates
    ledger_text = _audit_text(tmp_path)
    assert "private-dimensional-metadata" not in ledger_text
    assert coordinate_id not in ledger_text
    entry = next(
        entry
        for entry in _audit_entries(tmp_path)
        if entry["details"]["intent"]["action"]
        == "consciousness.multidimensional_create_coordinate"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "create_coordinate"
    assert metadata["dimension_names"] == ["consciousness", "memory"]
    assert metadata["metadata_field_names"] == ["secret"]


def test_dimensional_coordinate_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-dimensional-client",
        strict=True,
    )
    engine = _fresh_engine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            engine.create_dimensional_coordinate(
                {DimensionalAxis.CONSCIOUSNESS: 0.95},
                metadata={"secret": "blocked-dimensional-metadata"},
            )
        )

    assert _snapshot(engine) == before
    ledger_text = _audit_text(tmp_path)
    assert "blocked-dimensional-metadata" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.multidimensional_create_coordinate"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_multidimensional_navigation_denial_preserves_position(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    engine = _fresh_engine()
    target_id = asyncio.run(
        engine.create_dimensional_coordinate({DimensionalAxis.CONSCIOUSNESS: 0.93})
    )
    before_position = engine.current_position
    before = _snapshot(engine)
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-dimensional-client",
        strict=True,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.navigate_to_coordinate(target_id, navigation_strategy="private-path"))

    assert _snapshot(engine) == before
    assert engine.current_position == before_position
    ledger_text = _audit_text(tmp_path)
    assert target_id not in ledger_text
    assert "private-path" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.multidimensional_navigate"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_multidimensional_processing_denial_preserves_component_state(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-dimensional-client",
        strict=True,
    )
    engine = _fresh_engine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(
            engine.process_multidimensional_state(
                {"focus": "private-consciousness-payload", "energy": 0.6},
                target_dimensions=[DimensionalAxis.CONSCIOUSNESS],
            )
        )

    assert _snapshot(engine) == before
    ledger_text = _audit_text(tmp_path)
    assert "private-consciousness-payload" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.multidimensional_process_state"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
