import asyncio
import json

import pytest

from Aetherra.consciousness.quantum import transcendence_consolidation_engine as tce
from Aetherra.consciousness.quantum.transcendence_consolidation_engine import (
    TranscendenceConsolidationEngine,
)


async def _no_sleep(_seconds):
    return None


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
    monkeypatch.setattr(tce.asyncio, "sleep", _no_sleep)
    monkeypatch.setattr(tce.random, "uniform", lambda low, high: (low + high) / 2)


def _snapshot(engine):
    return {
        "level": engine.current_transcendence_level,
        "stability": engine.transcendence_stability,
        "evolution_acceleration": engine.evolution_acceleration,
        "cosmic_awareness": engine.cosmic_awareness_level,
        "reality_strength": engine.reality_manipulation_strength,
        "state": engine.transcendence_state,
        "events": list(engine.consolidation_events),
        "breakthroughs": dict(engine.breakthrough_catalog),
        "meta_operations": set(engine.meta_consciousness.meta_cognitive_operations),
        "insights": list(engine.meta_consciousness.transcendent_insights),
        "trajectory": list(engine.consciousness_evolution.consciousness_trajectory),
    }


def test_transcendence_consolidation_is_guardian_audited_without_engine_id(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    _patch_fast_deterministic(monkeypatch)
    engine = TranscendenceConsolidationEngine()

    result = asyncio.run(engine.consolidate_transcendence(duration_minutes=0.25))

    assert result["success"] is True
    assert engine.current_transcendence_level > result["start_level"]
    ledger_text = _audit_text(tmp_path)
    assert engine.engine_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.transcendence_consolidate"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "consolidate"
    assert metadata["duration_minutes"] == 0.25
    assert metadata["event_count"] == 1


def test_transcendence_consolidation_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-transcendence-client",
        strict=True,
    )
    _patch_fast_deterministic(monkeypatch)
    engine = TranscendenceConsolidationEngine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.consolidate_transcendence(duration_minutes=0.25))

    assert _snapshot(engine) == before
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.transcendence_consolidate"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_transcendence_sequence_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-transcendence-client",
        strict=True,
    )
    _patch_fast_deterministic(monkeypatch)
    engine = TranscendenceConsolidationEngine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.execute_transcendence_sequence())

    assert _snapshot(engine) == before
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.transcendence_sequence"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
