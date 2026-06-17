import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


@pytest.fixture
def guardian_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return tmp_path


@pytest.fixture
def service(guardian_env):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = SelfIncorporationConfig()
        config.hmr_enabled = True
        config.index_db_path = temp_path / "test_index.db"
        config.index_jsonl_path = temp_path / "test_index.jsonl"
        config.audit_db_path = temp_path / "test_audit.db"
        yield SelfIncorporationService(config)


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _ready_plan(plan_id: str = "plan-do-not-audit-this-value"):
    return {
        "plan_id": plan_id,
        "status": "ready",
        "actions": [
            {
                "action": "register_plugin",
                "target": {"file_id": "plugin-do-not-audit-this-value"},
                "deps": [],
            }
        ],
    }


@pytest.mark.asyncio
async def test_trigger_integrate_writes_guardian_audit_without_raw_plan_values(
    service, guardian_env
):
    plan = _ready_plan()

    with (
        patch.object(service, "_run_integration_planning", return_value=plan),
        patch.object(
            service,
            "_evaluate_plan_ethics",
            return_value={
                "overall_score": 0.95,
                "risk_factors": [],
                "reasoning": [],
            },
        ),
        patch.object(
            service.core_integrator,
            "execute_plan",
            return_value={"ok": True, "applied": 0, "skipped": 1, "errors": 0},
        ),
    ):
        result = await service.trigger_integrate(dry_run=True)

    entries = _audit_entries(guardian_env)
    audit_json = json.dumps(entries[-1])

    assert result["ok"] is True
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.integrate_plan"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in audit_json


@pytest.mark.asyncio
async def test_trigger_integrate_blocks_external_requester_before_ethics_or_execution(
    monkeypatch, service, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    plan = _ready_plan("plan-denied")

    with (
        patch.object(service, "_run_integration_planning", return_value=plan),
        patch.object(
            service, "_evaluate_plan_ethics", new=AsyncMock()
        ) as evaluate_ethics,
        patch.object(
            service.core_integrator, "execute_plan", new=AsyncMock()
        ) as execute_plan,
    ):
        result = await service.trigger_integrate(
            dry_run=False,
            requester="untrusted_operator",
        )

    assert result["ok"] is False
    assert result["status"] == "guardian_denied"
    assert result["reason"] == "missing_capability"
    assert evaluate_ethics.await_count == 0
    assert execute_plan.await_count == 0


def test_hub_selfinc_apply_passes_requester_to_guardian(monkeypatch, guardian_env):
    from aetherra_hub.app import create_app
    from aetherra_hub.blueprints import self_incorporation as selfinc_blueprint

    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    app = create_app()
    client = app.test_client()
    service = SelfIncorporationService(SelfIncorporationConfig())

    async def run_plan(include_experimental=False):
        return _ready_plan("hub-plan-denied")

    service._run_integration_planning = run_plan
    monkeypatch.setattr(selfinc_blueprint, "disclosure_policy", None)
    monkeypatch.setattr(selfinc_blueprint, "get_service", lambda name: service)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = client.post(
            "/api/selfinc/apply",
            json={"dry_run": False},
            headers={
                "Authorization": "Bearer control-secret",
                "X-Aetherra-Principal": "untrusted_operator",
            },
        )
    finally:
        asyncio.set_event_loop(None)
        loop.close()
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["ok"] is False
    assert payload["status"] == "guardian_denied"
    entries = _audit_entries(guardian_env)
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.integrate_plan"
