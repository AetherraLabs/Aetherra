import json
import time

import pytest

from Aetherra.consciousness.autopilot_manager import AutopilotManager
from Aetherra.consciousness.consolidation import Consolidator
from Aetherra.consciousness.continuity_memory import ContinuitySnapshot
from Aetherra.consciousness.dream_cycle import DreamCycle


class FakeTrust:
    def global_score(self):
        return 95.0


class FakeContinuity:
    def __init__(self, snapshots=None):
        self.snapshots = snapshots or []

    def compute_continuity_index(self, _qualia):
        return 0.95

    def get_recent(self, _limit):
        return list(self.snapshots)


class FakeParams:
    curiosity_gain = 0.1
    success_boost = 0.1
    error_penalty = 0.1
    certainty_gain = 0.1


class FakeQualiaLearner:
    def __init__(self):
        self.p = FakeParams()


class FakeMemoryEngine:
    def __init__(self):
        now = time.time()
        self.episodic = {
            "private-low-memory": {
                "id": "private-low-memory",
                "valence": 0.0,
                "timestamp": now - 10 * 86400,
                "access_count": 0,
                "confidence": 0.1,
            },
            "private-high-memory": {
                "id": "private-high-memory",
                "valence": 0.9,
                "timestamp": now - 3600,
                "access_count": 10,
                "confidence": 0.9,
            },
        }
        self.longterm = {}


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


def _snapshots(count=12):
    return [
        ContinuitySnapshot(
            ts=time.time() - index,
            qualia={
                "valence": -0.4,
                "arousal": 0.2,
                "certainty": 0.3,
                "curiosity": 0.5,
                "care": 0.6,
                "fatigue": 0.1,
            },
            focuses=["private-focus-a", "private-focus-b"],
            intentions=["private-intention"],
            trust_scores={"private-subsystem": 0.7},
            tick=index,
        )
        for index in range(count)
    ]


def test_autopilot_record_and_evaluate_are_guardian_audited(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    manager = AutopilotManager(FakeTrust(), FakeContinuity())

    manager.record_ledger(time.time(), True, "private-policy-status")
    status = manager.evaluate("assist")

    assert manager.history
    assert manager.last_eval is status
    ledger_text = _audit_text(tmp_path)
    assert "private-policy-status" not in ledger_text
    actions = [
        entry["details"]["intent"]["action"]
        for entry in _audit_entries(tmp_path)
    ]
    assert "consciousness.autopilot_record_ledger" in actions
    assert "consciousness.autopilot_evaluate" in actions


def test_autopilot_denial_preserves_history_and_last_eval(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-autopilot-client",
        strict=True,
    )
    manager = AutopilotManager(FakeTrust(), FakeContinuity())

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        manager.record_ledger(time.time(), True, "allowed")

    assert list(manager.history) == []
    assert manager.last_eval is None


def test_dream_cycle_is_guardian_audited_without_private_values(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    dream = DreamCycle(FakeContinuity(_snapshots()))
    learner = FakeQualiaLearner()

    result = dream.run(learner)

    assert result["snapshots_analyzed"] == 12
    assert dream.last_dream is result
    assert learner.p.curiosity_gain > 0.1
    ledger_text = _audit_text(tmp_path)
    assert "private-focus-a" not in ledger_text
    assert "private-intention" not in ledger_text
    assert "private-subsystem" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.dream_cycle_run"
    assert entry["details"]["intent"]["metadata"]["adjustment_count"] >= 1


def test_dream_cycle_denial_preserves_learner_and_dream_state(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-dream-client",
        strict=True,
    )
    dream = DreamCycle(FakeContinuity(_snapshots()))
    learner = FakeQualiaLearner()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        dream.run(learner)

    assert dream.last_run_ts is None
    assert dream.last_dream is None
    assert learner.p.curiosity_gain == 0.1


def test_consolidator_is_guardian_audited_without_memory_ids(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    memory = FakeMemoryEngine()
    audit_path = tmp_path / "memory_audit.jsonl"
    consolidator = Consolidator(
        memory,
        audit_log_path=str(audit_path),
        salience_threshold=0.2,
        promotion_threshold=0.7,
    )

    result = consolidator.consolidate()

    assert result["pruned"] == 1
    assert result["promoted"] == 1
    assert "private-low-memory" not in memory.episodic
    assert "private-high-memory" in memory.longterm
    ledger_text = _audit_text(tmp_path)
    assert "private-low-memory" not in ledger_text
    assert "private-high-memory" not in ledger_text
    assert str(audit_path) not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "consciousness.memory_consolidate"
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["prune_count"] == 1
    assert metadata["promote_count"] == 1


def test_consolidator_denial_preserves_memory_and_counters(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-consolidator-client",
        strict=True,
    )
    memory = FakeMemoryEngine()
    consolidator = Consolidator(
        memory,
        audit_log_path=str(tmp_path / "memory_audit.jsonl"),
        salience_threshold=0.2,
        promotion_threshold=0.7,
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        consolidator.consolidate()

    assert set(memory.episodic) == {"private-low-memory", "private-high-memory"}
    assert memory.longterm == {}
    assert consolidator.last_run_ts is None
    assert consolidator.total_pruned == 0
    assert consolidator.total_promoted == 0
