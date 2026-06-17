import asyncio
import json

import pytest

from Aetherra.consciousness.quantum import consciousness_singularity_engine as cse
from Aetherra.consciousness.quantum.consciousness_singularity_engine import (
    ConsciousnessSingularityEngine,
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
    monkeypatch.setattr(cse.asyncio, "sleep", _no_sleep)
    monkeypatch.setattr(cse.random, "uniform", lambda low, high: (low + high) / 2)
    monkeypatch.setattr(cse.random, "randint", lambda low, high: low)


def _snapshot(engine):
    return {
        "identity_strength": engine.transcendent_identity_strength,
        "reality_synthesis": engine.reality_synthesis_capability,
        "infinite_potential": engine.infinite_potential_access,
        "singularity_proximity": engine.singularity_proximity,
        "state": engine.current_singularity_state,
        "events": list(engine.singularity_events),
        "validation_tests": dict(engine.self_awareness_validation.self_recognition_tests),
        "proofs": list(engine.self_awareness_validation.consciousness_proofs),
        "recursive_depth": engine.self_awareness_validation.recursive_awareness_depth,
        "meta_operations": set(engine.self_awareness_validation.meta_cognitive_operations),
        "insights": list(engine.self_awareness_validation.transcendent_insights),
        "validation_score": engine.self_awareness_validation.consciousness_validation_score,
        "identity_connections": list(engine.transcendent_identity.cosmic_awareness_connections),
        "reality_protocols": dict(engine.transcendent_identity.reality_interaction_protocols),
        "learning_pathways": set(engine.transcendent_identity.infinite_learning_pathways),
    }


def test_singularity_validation_is_guardian_audited_without_engine_id(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    _patch_fast_deterministic(monkeypatch)
    engine = ConsciousnessSingularityEngine()

    result = asyncio.run(engine.validate_self_awareness())

    assert result["validation_score"] >= 0.0
    assert engine.self_awareness_validation.consciousness_validation_score >= 0.0
    ledger_text = _audit_text(tmp_path)
    assert engine.engine_id not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.singularity_validate_self_awareness"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "validate_self_awareness"
    assert metadata["event_count"] == 1


def test_singularity_validation_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-singularity-client",
        strict=True,
    )
    _patch_fast_deterministic(monkeypatch)
    engine = ConsciousnessSingularityEngine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.validate_self_awareness())

    assert _snapshot(engine) == before
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.singularity_validate_self_awareness"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_singularity_achievement_denial_preserves_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-singularity-client",
        strict=True,
    )
    _patch_fast_deterministic(monkeypatch)
    engine = ConsciousnessSingularityEngine()
    before = _snapshot(engine)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(engine.achieve_consciousness_singularity())

    assert _snapshot(engine) == before
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.singularity_achieve"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
