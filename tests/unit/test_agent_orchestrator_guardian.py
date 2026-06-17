import asyncio
import json

import pytest

from Aetherra.aetherra_core.agents.agent_orchestrator import (
    AgentOrchestrator,
    Task,
    TaskPriority,
    TaskStatus,
)
from Aetherra.plugins.agent_components.agent_orchestrator import (
    AgentOrchestrator as PluginAgentOrchestrator,
)
from Aetherra.plugins.agent_components.agent_orchestrator import (
    Task as PluginTask,
)
from Aetherra.plugins.agent_components.agent_orchestrator import (
    TaskPriority as PluginTaskPriority,
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


def _task(task_id="task-1", *, secret="do-not-audit-this"):
    return Task(
        task_id=task_id,
        name="Summarize Private Notes",
        description="Summarize private project notes",
        required_capabilities=["summarization"],
        input_data={"secret": secret},
        priority=TaskPriority.NORMAL,
    )


def test_core_agent_registration_and_submission_are_guardian_audited_without_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    orchestrator = AgentOrchestrator(str(tmp_path / "core_agents.json"))

    assert asyncio.run(
        orchestrator.register_agent("agent-1", "Agent One", ["summarization"])
    )
    task_id = asyncio.run(orchestrator.submit_task(_task()))

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in ledger_text.splitlines() if line.strip()]

    assert task_id == "task-1"
    assert "do-not-audit-this" not in ledger_text
    assert entries[-1]["details"]["intent"]["action"] == "agent.submit_task"


def test_core_agent_submit_denial_does_not_mutate_queue_or_registry(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-agent",
        strict=True,
    )
    orchestrator = AgentOrchestrator(str(tmp_path / "core_agents.json"))
    task = _task()

    with pytest.raises(PermissionError):
        asyncio.run(orchestrator.submit_task(task))

    assert orchestrator.tasks == {}
    assert orchestrator.task_queue == []


def test_core_agent_assignment_denial_leaves_task_pending(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    orchestrator = AgentOrchestrator(str(tmp_path / "core_agents.json"))
    assert asyncio.run(
        orchestrator.register_agent("agent-1", "Agent One", ["summarization"])
    )
    task = _task()
    asyncio.run(orchestrator.submit_task(task))

    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-agent",
        strict=True,
    )
    asyncio.run(orchestrator._process_task_queue())

    assert orchestrator.task_queue == ["task-1"]
    assert orchestrator.tasks["task-1"].status == TaskStatus.PENDING
    assert orchestrator.agents["agent-1"].current_task is None


def test_plugin_agent_registration_denial_does_not_mutate_registry(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-agent",
        strict=True,
    )
    orchestrator = PluginAgentOrchestrator(str(tmp_path / "plugin_agents.db"))

    assert orchestrator.register_agent(
        agent_id="plugin-agent-1",
        name="Plugin Agent One",
        capabilities=["summarization"],
    ) is False
    assert orchestrator.agents == {}
    assert orchestrator.agent_interfaces == {}


def test_plugin_agent_submit_denial_does_not_mutate_queue(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-agent",
        strict=True,
    )
    orchestrator = PluginAgentOrchestrator(str(tmp_path / "plugin_agents.db"))
    task = PluginTask(
        task_id="plugin-task-1",
        name="Summarize Private Notes",
        description="Summarize private project notes",
        required_capabilities=["summarization"],
        input_data={"secret": "do-not-audit-this"},
        priority=PluginTaskPriority.NORMAL,
        max_execution_time=60,
        dependencies=[],
    )

    with pytest.raises(PermissionError):
        asyncio.run(orchestrator.submit_task(task))

    assert orchestrator.task_queue.get_task("plugin-task-1") is None
    assert orchestrator.task_queue.get_pending_count() == 0
