import asyncio
import json

from Aetherra.aetherra_core.agents.goals import (
    GoalPriority,
    GoalStatus,
    LyrixaGoalSystem,
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


def test_goal_create_and_subtask_complete_are_guardian_audited_without_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    goals = LyrixaGoalSystem(str(tmp_path / "goals.json"))

    goal_id = asyncio.run(
        goals.create_goal(
            "Private Launch Plan",
            "do-not-audit-this-goal-description",
            priority=GoalPriority.HIGH,
            metadata={"private_note": "do-not-audit-this-metadata-value"},
        )
    )
    subtask_id = asyncio.run(
        goals.add_subtask(
            goal_id,
            "Private Subtask",
            "do-not-audit-this-subtask-description",
        )
    )
    assert asyncio.run(goals.complete_subtask(subtask_id)) is True

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in ledger_text.splitlines() if line.strip()]

    assert "do-not-audit-this-goal-description" not in ledger_text
    assert "do-not-audit-this-subtask-description" not in ledger_text
    assert "do-not-audit-this-metadata-value" not in ledger_text
    assert entries[-1]["details"]["intent"]["action"] == "agent.subtask_complete"
    assert goals.goals[goal_id].status == GoalStatus.COMPLETED


def test_goal_create_denial_does_not_mutate_state_or_write_store(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-agent",
        strict=True,
    )
    goals_file = tmp_path / "goals.json"
    goals = LyrixaGoalSystem(str(goals_file))

    goal_id = asyncio.run(
        goals.create_goal(
            "Blocked Goal",
            "This should not be persisted",
            priority=GoalPriority.CRITICAL,
        )
    )

    assert goal_id == ""
    assert goals.goals == {}
    assert goals.subtasks == {}
    assert not goals_file.exists()


def test_goal_update_and_delete_denials_leave_existing_state_unchanged(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    goals = LyrixaGoalSystem(str(tmp_path / "goals.json"))
    goal_id = asyncio.run(
        goals.create_goal(
            "Original Goal",
            "Original description",
            priority=GoalPriority.MEDIUM,
        )
    )

    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-agent",
        strict=True,
    )
    assert asyncio.run(goals.update_goal(goal_id, status="paused", progress=0.5)) is False
    assert asyncio.run(goals.delete_goal(goal_id)) is False

    assert goal_id in goals.goals
    assert goals.goals[goal_id].status == GoalStatus.ACTIVE
    assert goals.goals[goal_id].progress == 0.0


def test_subtask_create_denial_does_not_mutate_goal(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    goals = LyrixaGoalSystem(str(tmp_path / "goals.json"))
    goal_id = asyncio.run(
        goals.create_goal(
            "Parent Goal",
            "Parent description",
            priority=GoalPriority.MEDIUM,
        )
    )

    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-agent",
        strict=True,
    )
    subtask_id = asyncio.run(goals.add_subtask(goal_id, "Blocked", "Blocked"))

    assert subtask_id == ""
    assert goals.subtasks == {}
    assert goals.goals[goal_id].subtasks == []
