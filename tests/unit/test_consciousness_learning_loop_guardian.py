import json

import pytest

from Aetherra.consciousness.learning_loop import LearningLoop


class FakeEpisodicStore:
    def __init__(self):
        self.events = []

    def new_event(self, **kwargs):
        self.events.append(kwargs)

    def list_recent(self, limit=100):
        return self.events[-limit:]


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


def test_learning_state_save_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    state_path = tmp_path / "learning" / "private-learning-state.json"
    episodes = FakeEpisodicStore()
    loop = LearningLoop(
        episodic_store=episodes,
        memory_engine=None,
        state_path=state_path,
    )

    adjustment = loop.process_outcome(
        {"action": "private_action_name", "confidence": 0.8, "risk_level": "medium"},
        {
            "context": "private_context_name",
            "success": True,
            "quality": 0.9,
            "latency_ms": 50,
            "secret_detail": "private_outcome_detail",
        },
    )

    assert adjustment.success is True
    assert state_path.exists()
    assert episodes.events
    ledger_text = _audit_text(tmp_path)
    assert str(state_path) not in ledger_text
    assert "private_action_name" not in ledger_text
    assert "private_context_name" not in ledger_text
    assert "private_outcome_detail" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.learning_state_save"
    assert entry["details"]["intent"]["metadata"]["iteration_count"] == 1
    assert entry["details"]["intent"]["metadata"]["context_count"] == 1
    assert entry["details"]["intent"]["metadata"]["action_count"] == 1


def test_learning_state_denial_restores_memory_and_skips_side_effects(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-learning-client",
        strict=True,
    )
    state_path = tmp_path / "learning" / "learning-state.json"
    episodes = FakeEpisodicStore()
    loop = LearningLoop(
        episodic_store=episodes,
        memory_engine=None,
        state_path=state_path,
    )
    before_state = json.loads(json.dumps(loop.state))

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        loop.process_outcome(
            {"action": "reflect", "confidence": 0.5, "risk_level": "medium"},
            {"context": "dream", "success": False, "quality": 0.2},
        )

    assert loop.state == before_state
    assert episodes.events == []
    assert not state_path.exists()
    assert not state_path.parent.exists()
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.learning_state_save"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
