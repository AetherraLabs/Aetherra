import json

import pytest

from Aetherra.aetherra_core.agents.lyrixa_assistant import LyrixaAssistant


class _AgentInterface:
    def __init__(self):
        self.called = False

    async def execute_task(self, task_spec):
        self.called = True
        return {"ok": True, "task_id": task_spec["id"]}


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


def _assistant(tmp_path):
    assistant = LyrixaAssistant(workspace_path=str(tmp_path))
    assistant.is_initialized = True
    assistant.context = {"session_id": assistant.session_id}
    return assistant


@pytest.mark.asyncio
async def test_assistant_execute_task_audits_without_payload(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path)
    assistant = _assistant(tmp_path)
    interface = _AgentInterface()
    assistant.agent_interface = interface

    result = await assistant.execute_task(
        "do-not-audit-this-task-description",
        "analysis",
        {"secret": "do-not-audit-this-context-value", "priority": 3},
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in ledger_text.splitlines() if line.strip()]

    assert result["ok"] is True
    assert interface.called is True
    assert assistant.active_tasks
    assert "do-not-audit-this-task-description" not in ledger_text
    assert "do-not-audit-this-context-value" not in ledger_text
    assert entries[-1]["details"]["intent"]["action"] == "ai.assistant_execute_task"


@pytest.mark.asyncio
async def test_assistant_execute_task_denial_stops_before_delegation(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-ai-client",
        strict=True,
    )
    assistant = _assistant(tmp_path)
    interface = _AgentInterface()
    assistant.agent_interface = interface

    result = await assistant.execute_task("blocked", "coding", {"priority": 1})

    assert result["error"] == "guardian_denied"
    assert interface.called is False
    assert assistant.active_tasks == {}


@pytest.mark.asyncio
async def test_assistant_fallback_denial_stops_before_active_task_mutation(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-ai-client",
        strict=True,
    )
    assistant = _assistant(tmp_path)

    result = await assistant.execute_task("blocked fallback", "general")

    assert result["error"] == "guardian_denied"
    assert assistant.active_tasks == {}
