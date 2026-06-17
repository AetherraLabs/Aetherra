import json

import pytest

from aetherra_hub.app import create_app
from aetherra_hub.services import trainer as trainer_service


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_TRAINER_ENABLED", "1")
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


def _reset_trainer_state():
    with trainer_service._lock:
        trainer_service._jobs.clear()
        trainer_service._evals.clear()
        trainer_service._eval_last_score = None
        trainer_service._eval_runs_total = 0


def _audit_text(tmp_path):
    return (tmp_path / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _audit_entries(tmp_path):
    return [
        json.loads(line)
        for line in _audit_text(tmp_path).splitlines()
        if line.strip()
    ]


def test_trainer_job_and_eval_submission_are_guardian_audited_without_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    _reset_trainer_state()

    job_id = trainer_service.submit_job(
        {
            "task": "sft",
            "base_model": "do-not-audit-this-model",
            "dataset_id": "do-not-audit-this-dataset",
            "params": {"private_lr": 0.1},
        }
    )
    eval_id = trainer_service.submit_eval(
        {
            "task": "safety",
            "model": "do-not-audit-this-eval-model",
            "dataset_id": "do-not-audit-this-eval-dataset",
        }
    )

    assert job_id in {job["job_id"] for job in trainer_service.list_jobs()}
    assert eval_id in {ev["eval_id"] for ev in trainer_service.list_evals()}
    ledger_text = _audit_text(tmp_path)
    assert "do-not-audit-this-model" not in ledger_text
    assert "do-not-audit-this-dataset" not in ledger_text
    assert "do-not-audit-this-eval-model" not in ledger_text
    entries = _audit_entries(tmp_path)
    actions = [entry["details"]["intent"]["action"] for entry in entries[-2:]]
    assert actions == ["trainer.submit_job", "trainer.submit_eval"]


def test_trainer_job_guardian_denial_stops_queue_mutation(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-trainer-client",
        strict=True,
    )
    _reset_trainer_state()

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        trainer_service.submit_job({"task": "sft", "dataset_id": "blocked-dataset"})

    assert trainer_service.list_jobs() == []


def test_hub_trainer_job_guardian_denial_returns_403(monkeypatch, tmp_path):
    _guardian_env(monkeypatch, tmp_path, strict=True)
    _reset_trainer_state()
    client = create_app().test_client()

    response = client.post(
        "/api/trainer/jobs",
        json={
            "task": "sft",
            "dataset_id": "blocked-dataset",
            "guardian_requester": "external-trainer-client",
        },
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "guardian_denied"
    assert trainer_service.list_jobs() == []
