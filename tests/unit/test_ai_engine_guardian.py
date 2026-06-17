import json

import pytest

from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine


class _DummyOrchestrator:
    def __init__(self):
        self.called = False
        self.submitted_task = None

    async def submit_task(self, task):
        self.called = True
        self.submitted_task = task
        return "task-1"


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


def _engine(tmp_path):
    engine = AetherraEngine(
        memory_db_path=str(tmp_path / "memory.db"),
        reasoning_db_path=str(tmp_path / "reasoning.db"),
        improvement_db_path=str(tmp_path / "improvement.db"),
        orchestrator_db_path=str(tmp_path / "orchestrator.json"),
    )
    engine.agent_orchestrator = _DummyOrchestrator()
    return engine


@pytest.mark.asyncio
async def test_engine_execute_task_writes_guardian_audit_without_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    engine = _engine(tmp_path)

    task_id = await engine.execute_task(
        "summarize_private_notes",
        {
            "secret": "do-not-audit-this-task-value",
            "required_capabilities": ["summarization"],
            "timeout": 30,
        },
        priority="high",
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in ledger_text.splitlines() if line.strip()]

    assert task_id == "task-1"
    assert engine.agent_orchestrator.called is True
    assert "do-not-audit-this-task-value" not in ledger_text
    assert entries[-1]["details"]["intent"]["action"] == "ai.engine_execute_task"
    assert engine.active_tasks["task-1"]["name"] == "summarize_private_notes"


@pytest.mark.asyncio
async def test_engine_execute_task_denial_stops_before_submit(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-ai-client",
        strict=True,
    )
    engine = _engine(tmp_path)

    with pytest.raises(PermissionError):
        await engine.execute_task(
            "network.export",
            {
                "secret": "do-not-submit-this",
                "required_capabilities": ["network"],
            },
        )

    assert engine.agent_orchestrator.called is False
    assert engine.active_tasks == {}
