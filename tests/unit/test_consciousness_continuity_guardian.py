import json
from types import SimpleNamespace

import pytest

from Aetherra.consciousness.continuity_memory import (
    ContinuityMemory,
    ContinuitySnapshot,
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


def _qualia():
    return SimpleNamespace(
        valence=0.4,
        arousal=0.3,
        certainty=0.9,
        curiosity=0.8,
        care=0.7,
        fatigue=0.1,
    )


def _focus(name):
    return SimpleNamespace(event=SimpleNamespace(type=name))


def _intent(goal):
    return SimpleNamespace(goal=goal)


def test_continuity_record_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    path = tmp_path / "private-continuity.json"
    memory = ContinuityMemory(path=str(path), max_snaps=5)

    memory.record(
        _qualia(),
        focuses=[_focus("private_focus_event")],
        intentions=[_intent("private_intention_goal")],
        trust_scores={"private_subsystem": 0.93},
        tick=42,
    )

    assert path.exists()
    assert len(memory.buffer) == 1
    ledger_text = _audit_text(tmp_path)
    assert str(path) not in ledger_text
    assert "private_focus_event" not in ledger_text
    assert "private_intention_goal" not in ledger_text
    assert "0.93" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.continuity_save"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["snapshot_count"] == 1
    assert metadata["latest_tick"] == 42
    assert metadata["qualia_label_count"] == 6
    assert metadata["trust_label_count"] == 1
    assert "qualia_keys" not in metadata
    assert "trust_keys" not in metadata


def test_continuity_record_denial_preserves_buffer_and_file(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-consciousness-client",
        strict=True,
    )
    path = tmp_path / "continuity.json"
    memory = ContinuityMemory(path=str(path), max_snaps=5)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        memory.record(
            _qualia(),
            focuses=[_focus("focus")],
            intentions=[_intent("goal")],
            trust_scores={"self": 0.5},
            tick=7,
        )

    assert memory.buffer == []
    assert not path.exists()
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.continuity_save"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_direct_continuity_save_denial_skips_file_write(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-consciousness-client",
        strict=True,
    )
    path = tmp_path / "continuity.json"
    memory = ContinuityMemory(path=str(path), max_snaps=5)
    memory.buffer.append(
        ContinuitySnapshot(
            ts=1.0,
            qualia={"valence": 0.1},
            focuses=["focus"],
            intentions=["goal"],
            trust_scores={"self": 0.5},
            tick=1,
        )
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        memory.save()

    assert not path.exists()
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["metadata"]["snapshot_count"] == 1
