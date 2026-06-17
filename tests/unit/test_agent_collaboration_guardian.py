import asyncio
import json

from Aetherra.aetherra_core.agents.collaboration import (
    AgentResponse,
    AgentRole,
    AIAgent,
    AICollaborationFramework,
    CollaborationTask,
    TaskPriority,
)


class _FastAgent(AIAgent):
    def __init__(self, role: AgentRole):
        super().__init__(role)
        self.capabilities = [f"{role.value}:test"]
        self.called = 0

    async def process_task(self, task: CollaborationTask) -> AgentResponse:
        self.called += 1
        return AgentResponse(
            agent_role=self.role,
            task_id=task.id,
            solution=f"{self.role.value} solution",
            confidence=0.9,
            execution_time=0.001,
            dependencies=[],
            suggestions=[],
            metadata={},
        )

    def get_capabilities(self):
        return self.capabilities


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


def _framework():
    framework = AICollaborationFramework()
    framework.ai_agents = {
        AgentRole.CODE_GENERATOR: _FastAgent(AgentRole.CODE_GENERATOR),
        AgentRole.OPTIMIZER: _FastAgent(AgentRole.OPTIMIZER),
        AgentRole.DEBUGGER: _FastAgent(AgentRole.DEBUGGER),
        AgentRole.DOCUMENTER: _FastAgent(AgentRole.DOCUMENTER),
    }
    return framework


def test_collaborative_solve_is_guardian_audited_without_problem_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    framework = _framework()

    result = asyncio.run(
        framework.collaborative_solve(
            "do-not-audit-this-problem",
            requirements=["do-not-audit-this-requirement"],
            priority=TaskPriority.HIGH,
        )
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in ledger_text.splitlines() if line.strip()]

    assert result["task_id"]
    assert "do-not-audit-this-problem" not in ledger_text
    assert "do-not-audit-this-requirement" not in ledger_text
    assert entries[-1]["details"]["intent"]["action"] == "agent.collaborative_solve"
    assert framework.active_tasks == {}
    assert len(framework.completed_tasks) == 1
    assert len(framework.collaboration_history) == 1


def test_collaborative_solve_denial_does_not_start_agents_or_mutate_state(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path, requester="external-agent", strict=True)
    framework = _framework()

    result = asyncio.run(framework.collaborative_solve("blocked", ["blocked"]))

    assert result["error"] == "guardian_denied"
    assert framework.active_tasks == {}
    assert framework.completed_tasks == []
    assert framework.collaboration_history == []
    assert all(agent.called == 0 for agent in framework.ai_agents.values())


def test_quick_solve_denial_does_not_delegate_to_agent(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path, requester="external-agent", strict=True)
    framework = _framework()
    code_agent = framework.ai_agents[AgentRole.CODE_GENERATOR]

    result = asyncio.run(framework.quick_solve("blocked quick solve"))

    assert result == "[Guardian] Quick solve denied"
    assert code_agent.called == 0


def test_add_agent_denial_does_not_mutate_registry(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path, requester="external-agent", strict=True)
    framework = _framework()
    replacement = _FastAgent(AgentRole.TESTER)

    framework.add_agent(replacement)

    assert AgentRole.TESTER not in framework.ai_agents
