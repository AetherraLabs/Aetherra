import json

from aetherra_hub.app import create_app
from aetherra_hub.blueprints import agents


def _client(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_AGENTS_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    return create_app().test_client()


def _headers():
    return {
        "Authorization": "Bearer control-secret",
        "X-Aetherra-Principal": "agent-admin",
    }


def test_agent_task_submission_writes_guardian_audit(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    monkeypatch.setattr(
        agents.registry_client,
        "execute_agent_task",
        lambda name, data, priority: "task-1",
    )

    response = client.post(
        "/api/tasks",
        json={
            "name": "summarize",
            "description": "Summarize project notes",
            "input_data": {"document_id": "doc-1"},
            "priority": "normal",
        },
        headers=_headers(),
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert response.status_code == 200
    assert response.get_json()["task_id"] == "task-1"
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["intent"]["action"] == "agent.execute_task"
    assert entries[-1]["details"]["intent"]["target"] == "agent_task:summarize"


def test_agent_task_submission_blocked_by_guardian_missing_capability(
    monkeypatch, tmp_path
):
    client = _client(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    called = False

    def _execute_agent_task(name, data, priority):
        nonlocal called
        called = True
        return "task-should-not-run"

    monkeypatch.setattr(agents.registry_client, "execute_agent_task", _execute_agent_task)

    response = client.post(
        "/api/tasks",
        json={"name": "blocked", "input_data": {"x": 1}},
        headers=_headers(),
    )
    payload = response.get_json()

    assert response.status_code == 403
    assert payload["error"] == "missing_capability"
    assert payload["guardian"]["status"] == "deny"
    assert called is False


def test_agent_task_guardian_audit_does_not_store_input_payload(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    monkeypatch.setattr(
        agents.registry_client,
        "execute_agent_task",
        lambda name, data, priority: "task-2",
    )

    response = client.post(
        "/api/tasks",
        json={
            "name": "private-task",
            "input_data": {"secret": "do-not-audit-this-value"},
        },
        headers=_headers(),
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "do-not-audit-this-value" not in ledger_text
    assert "private-task" in ledger_text
