# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Aetherra Labs and Contributors

from datetime import datetime, timedelta

import pytest

from Aetherra.aetherra_core.orchestration.orchestration_bridge import (
    AgentOrchestrator,
    AgentTask,
    AgentType,
    TaskStatus,
)


@pytest.mark.asyncio
async def test_execute_next_task_respects_priority_order():
    orchestrator = AgentOrchestrator()

    # Build deterministic queue entries without relying on planner output.
    base = datetime.now()
    low = AgentTask(
        id="task_low",
        agent_type=AgentType.ANALYZER,
        task_type="code_analysis",
        description="low",
        input_data={},
        priority=1,
        created_at=base,
    )
    high = AgentTask(
        id="task_high",
        agent_type=AgentType.ANALYZER,
        task_type="code_analysis",
        description="high",
        input_data={},
        priority=9,
        created_at=base + timedelta(milliseconds=1),
    )

    orchestrator.task_queue = [low, high]

    result = await orchestrator.execute_next_task()

    assert result is not None
    assert result["status"] == "completed"
    assert result["task_id"] == "task_high"


@pytest.mark.asyncio
async def test_execute_workflow_returns_stall_error_on_unresolved_dependency(
    monkeypatch,
):
    orchestrator = AgentOrchestrator()

    async def _plan_workflow(_input_data):
        return {
            "plan": [
                {
                    "agent_type": "analyzer",
                    "task_type": "code_analysis",
                    "description": "blocked",
                    "input_data": {},
                    "dependencies": ["missing_dependency"],
                }
            ]
        }

    planner = orchestrator.agents[AgentType.PLANNER]
    monkeypatch.setattr(planner, "_plan_workflow", _plan_workflow)

    result = await orchestrator.execute_workflow("blocked workflow", {})

    assert result["success"] is False
    assert "stalled" in result["error"].lower()
    assert result["pending_tasks"]
    assert result["pending_tasks"][0]["dependencies"] == ["missing_dependency"]


@pytest.mark.asyncio
async def test_can_execute_task_rejects_failed_dependency():
    orchestrator = AgentOrchestrator()

    dependency = AgentTask(
        id="dep",
        agent_type=AgentType.ANALYZER,
        task_type="code_analysis",
        description="dependency",
        input_data={},
        priority=5,
        created_at=datetime.now(),
        status=TaskStatus.FAILED,
    )
    orchestrator.completed_tasks[dependency.id] = dependency

    candidate = AgentTask(
        id="candidate",
        agent_type=AgentType.CODER,
        task_type="code_generation",
        description="candidate",
        input_data={},
        priority=5,
        created_at=datetime.now(),
        dependencies=[dependency.id],
    )

    assert orchestrator._can_execute_task(candidate) is False
