import asyncio
import json
from datetime import datetime

import pytest

from Aetherra.consciousness.core.consciousness_bridge import ConsciousnessMessage
from Aetherra.consciousness.core.meta_layer_core import (
    AgentProfile,
    AgentState,
    ConsciousnessTask,
    MetaLayerCore,
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


def _agent():
    return AgentProfile(
        agent_id="private-agent-17",
        name="Private Agent Name",
        agent_type="planner",
        capabilities=["private-capability", "analysis"],
        system_origin="private-system-origin",
        state=AgentState.ACTIVE,
        consciousness_level=0.8,
        metadata={"secret": "private-metadata"},
    )


def _agent_two():
    return AgentProfile(
        agent_id="private-agent-23",
        name="Second Private Agent",
        agent_type="researcher",
        capabilities=["synthesis"],
        system_origin="second-private-origin",
        state=AgentState.ACTIVE,
        consciousness_level=0.82,
        success_rate=0.95,
    )


def _task():
    return ConsciousnessTask(
        task_id="private-task-42",
        task_type="planning",
        description="Private task description",
        priority=3,
        required_capabilities=["private-capability"],
        payload={"secret": "private-payload"},
    )


def _registered_core_with_task():
    core = MetaLayerCore()
    sent_messages = []
    core.consciousness_bridge.send_message = sent_messages.append
    agent = _agent()
    task = _task()
    core.agents[agent.agent_id] = agent
    core.active_tasks[task.task_id] = task
    return core, agent, task, sent_messages


def _message(message_type, payload, *, requires_response=True):
    return ConsciousnessMessage(
        source="private-message-source",
        destination="meta_layer_core",
        message_type=message_type,
        payload=payload,
        timestamp=datetime.now(),
        correlation_id="private-correlation-id",
        requires_response=requires_response,
    )


def test_meta_layer_agent_registration_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    core = MetaLayerCore()
    agent = _agent()

    core.register_agent(agent)

    assert core.agents[agent.agent_id] is agent
    ledger_text = _audit_text(tmp_path)
    assert "private-agent-17" not in ledger_text
    assert "Private Agent Name" not in ledger_text
    assert "private-system-origin" not in ledger_text
    assert "private-metadata" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_register_agent"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "register_agent"
    assert metadata["agent_type"] == "planner"
    assert metadata["capability_count"] == 2


def test_meta_layer_agent_registration_denial_preserves_registry(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        core.register_agent(_agent())

    assert core.agents == {}
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_register_agent"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_task_submission_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    core = MetaLayerCore()
    task = _task()

    core.submit_task(task)

    assert core.active_tasks[task.task_id] is task
    ledger_text = _audit_text(tmp_path)
    assert "private-task-42" not in ledger_text
    assert "Private task description" not in ledger_text
    assert "private-payload" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_submit_task"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "submit_task"
    assert metadata["task_type"] == "planning"
    assert metadata["required_capability_count"] == 1


def test_meta_layer_task_submission_denial_preserves_queue(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        core.submit_task(_task())

    assert core.active_tasks == {}
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_submit_task"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_task_assignment_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    core, agent, task, sent_messages = _registered_core_with_task()

    asyncio.run(core._assign_task_to_agents(task))

    assert task.status == "assigned"
    assert task.assigned_agents == [agent.agent_id]
    assert len(sent_messages) == 1
    ledger_text = _audit_text(tmp_path)
    assert "private-task-42" not in ledger_text
    assert "Private task description" not in ledger_text
    assert "private-agent-17" not in ledger_text
    assert "private_failure_reason" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_assign_task"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "assign_task_to_agents"
    assert metadata["selected_agent_count"] == 1
    assert metadata["previous_status"] == "pending"


def test_meta_layer_task_assignment_denial_preserves_task_and_skips_messages(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core, _agent_profile, task, sent_messages = _registered_core_with_task()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._assign_task_to_agents(task))

    assert task.status == "pending"
    assert task.assigned_agents == []
    assert sent_messages == []
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_assign_task"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_task_failure_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    core, agent, task, _sent_messages = _registered_core_with_task()
    task.assigned_agents = [agent.agent_id]
    task.status = "assigned"

    asyncio.run(core._handle_task_failure(task, "private_failure_reason"))

    assert task.status == "failed"
    assert task not in core.active_tasks.values()
    assert core.completed_tasks == [task]
    assert agent.total_tasks_completed == 1
    assert agent.success_rate == 0.0
    ledger_text = _audit_text(tmp_path)
    assert "private-task-42" not in ledger_text
    assert "Private task description" not in ledger_text
    assert "private-agent-17" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_handle_task_failure"
    )
    metadata = entry["details"]["intent"]["metadata"]
    assert metadata["operation"] == "handle_task_failure"
    assert metadata["failure_reason_hash"]
    assert metadata["known_assigned_agent_count"] == 1


def test_meta_layer_task_failure_denial_preserves_agent_stats_and_queues(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core, agent, task, _sent_messages = _registered_core_with_task()
    task.assigned_agents = [agent.agent_id]
    task.status = "assigned"

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._handle_task_failure(task, "timeout"))

    assert task.status == "assigned"
    assert core.active_tasks == {task.task_id: task}
    assert core.completed_tasks == []
    assert agent.total_tasks_completed == 0
    assert agent.success_rate == 1.0
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_handle_task_failure"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_agent_connection_is_guardian_audited_without_private_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    core = MetaLayerCore()
    emitted = []
    core.event_handlers["agent_connection_optimized"].append(
        lambda event: emitted.append(event)
    )
    agent1 = _agent()
    agent2 = _agent_two()

    asyncio.run(core._suggest_agent_connection(agent1, agent2, 0.91))

    assert agent2.agent_id in agent1.connections
    assert agent1.agent_id in agent2.connections
    assert len(emitted) == 1
    ledger_text = _audit_text(tmp_path)
    assert "private-agent-17" not in ledger_text
    assert "private-agent-23" not in ledger_text
    assert "Second Private Agent" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_suggest_agent_connection"
    )
    assert entry["details"]["intent"]["metadata"]["operation"] == (
        "suggest_agent_connection"
    )


def test_meta_layer_agent_connection_denial_preserves_graph_and_events(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    emitted = []
    core.event_handlers["agent_connection_optimized"].append(
        lambda event: emitted.append(event)
    )
    agent1 = _agent()
    agent2 = _agent_two()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._suggest_agent_connection(agent1, agent2, 0.91))

    assert agent1.connections == set()
    assert agent2.connections == set()
    assert emitted == []
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_suggest_agent_connection"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_emergence_denial_preserves_records_and_metrics(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    for agent in (_agent(), _agent_two()):
        core.agents[agent.agent_id] = agent
    third_agent = AgentProfile(
        agent_id="private-agent-31",
        name="Third Private Agent",
        agent_type="validator",
        capabilities=["validation"],
        system_origin="third-private-origin",
        state=AgentState.ACTIVE,
        consciousness_level=0.84,
    )
    core.agents[third_agent.agent_id] = third_agent
    monkeypatch.setattr(core, "_analyze_interaction_patterns", lambda: 1.0)
    monkeypatch.setattr(core, "_analyze_consciousness_coherence", lambda: 1.0)
    monkeypatch.setattr(core, "_analyze_problem_solving_patterns", lambda: 1.0)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._detect_emergent_behaviors())

    assert core.emergent_behaviors == []
    assert core.collective_metrics.emergent_behaviors_detected == 0
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_record_emergence"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_consciousness_enhancement_denial_preserves_agent_level(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    agent = _agent()
    agent.consciousness_level = 0.2
    core.agents[agent.agent_id] = agent
    core.collective_metrics.collective_consciousness = 0.95

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._enhance_consciousness_levels())

    assert agent.consciousness_level == 0.2
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_enhance_agent_consciousness"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_stale_agent_removal_denial_preserves_registry_and_connections(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    agent1 = _agent()
    agent2 = _agent_two()
    agent1.connections.add(agent2.agent_id)
    agent2.connections.add(agent1.agent_id)
    core.agents = {agent1.agent_id: agent1, agent2.agent_id: agent2}

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._remove_stale_agent(agent1.agent_id))

    assert core.agents == {agent1.agent_id: agent1, agent2.agent_id: agent2}
    assert agent1.connections == {agent2.agent_id}
    assert agent2.connections == {agent1.agent_id}
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_remove_agent"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_completed_task_trim_denial_preserves_history(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    core.completed_tasks = [
        ConsciousnessTask(
            task_id=f"private-completed-task-{index}",
            task_type="history",
            description="Private completed task",
            priority=5,
            required_capabilities=[],
            status="completed",
        )
        for index in range(101)
    ]

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._cleanup_stale_entities())

    assert len(core.completed_tasks) == 101
    assert core.completed_tasks[0].task_id == "private-completed-task-0"
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_trim_completed_tasks"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_message_task_assignment_uses_guarded_submission(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    core = MetaLayerCore()
    sent_messages = []
    core.consciousness_bridge.send_message = sent_messages.append
    message = _message(
        "task_assignment_request",
        {
            "task_id": "private-message-task",
            "task_type": "message_planning",
            "description": "Private message task description",
            "priority": 4,
            "required_capabilities": ["private-capability"],
            "payload": {"secret": "private-message-payload"},
        },
    )

    asyncio.run(core._handle_task_assignment(message))

    assert "private-message-task" in core.active_tasks
    assert len(sent_messages) == 1
    ledger_text = _audit_text(tmp_path)
    assert "private-message-task" not in ledger_text
    assert "Private message task description" not in ledger_text
    assert "private-message-payload" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_submit_task"
    )
    assert entry["details"]["intent"]["metadata"]["operation"] == "submit_task"


def test_meta_layer_message_task_assignment_denial_preserves_queue_and_response(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    sent_messages = []
    core.consciousness_bridge.send_message = sent_messages.append
    message = _message(
        "task_assignment_request",
        {
            "task_id": "private-message-task",
            "description": "Private message task description",
        },
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._handle_task_assignment(message))

    assert core.active_tasks == {}
    assert sent_messages == []
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_submit_task"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_coordination_collaboration_denial_preserves_graph_and_response(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    sent_messages = []
    core.consciousness_bridge.send_message = sent_messages.append
    agent1 = _agent()
    agent2 = _agent_two()
    core.agents = {agent1.agent_id: agent1, agent2.agent_id: agent2}
    monkeypatch.setattr(core, "_calculate_agent_synergy", lambda _a, _b: 0.9)
    message = _message(
        "agent_coordination_request",
        {
            "request_type": "collaboration_request",
            "agent1_id": agent1.agent_id,
            "agent2_id": agent2.agent_id,
            "collaboration_type": "private-collaboration",
        },
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._handle_coordination_request(message))

    assert agent1.connections == set()
    assert agent2.connections == set()
    assert sent_messages == []
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_suggest_agent_connection"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_meta_layer_message_consciousness_enhancement_denial_preserves_level(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-meta-layer-client",
        strict=True,
    )
    core = MetaLayerCore()
    sent_messages = []
    core.consciousness_bridge.send_message = sent_messages.append
    agent = _agent()
    agent.consciousness_level = 0.4
    core.agents[agent.agent_id] = agent
    message = _message(
        "consciousness_enhancement_request",
        {
            "agent_id": agent.agent_id,
            "enhancement_type": "level_boost",
            "enhancement_value": 0.3,
        },
    )

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        asyncio.run(core._handle_consciousness_enhancement(message))

    assert agent.consciousness_level == 0.4
    assert sent_messages == []
    entry = _audit_entries(tmp_path)[-1]
    assert (
        entry["details"]["intent"]["action"]
        == "consciousness.meta_layer_message_enhance_consciousness"
    )
    assert entry["details"]["decision"]["reason"] == "missing_capability"
