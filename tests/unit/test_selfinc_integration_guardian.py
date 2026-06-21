import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from aetherra_self_incorporation import (
    FileItem,
    ItemType,
    SelfIncorporationConfig,
    SelfIncorporationService,
)
from aetherra_hmr_controller import HMRController


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


def _store_workflow_file(service, file_id="workflow-test-file"):
    workflow_path = Path("workflows") / "test_workflow.aether"
    service.code_index.store_file(
        FileItem(
            id=file_id,
            path=str(workflow_path),
            hash="abc123",
            size=10,
            mtime=1.0,
            type=ItemType.WORKFLOW,
            language="aether",
        )
    )
    return file_id


def _store_plugin_file(service, file_id="plugin-test-file"):
    plugin_path = Path("plugins") / "test_plugin.py"
    service.code_index.store_file(
        FileItem(
            id=file_id,
            path=str(plugin_path),
            hash="def456",
            size=20,
            mtime=1.0,
            type=ItemType.PLUGIN,
            language="python",
        )
    )
    return file_id


def _store_agent_file(service, file_id="agent-test-file"):
    agent_path = Path("agents") / "test_agent.py"
    service.code_index.store_file(
        FileItem(
            id=file_id,
            path=str(agent_path),
            hash="ghi789",
            size=20,
            mtime=1.0,
            type=ItemType.AGENT,
            language="python",
        )
    )
    return file_id


def _store_script_file(service, file_id="script-test-file"):
    script_path = Path("scripts") / "test_script.aether"
    service.code_index.store_file(
        FileItem(
            id=file_id,
            path=str(script_path),
            hash="script-hash-123",
            size=20,
            mtime=1.0,
            type=ItemType.AETHER,
            language="aether",
        )
    )
    return file_id


class _FakeServiceInfo:
    def __init__(self, instance):
        self.instance = instance


class _FakeRegistry:
    def __init__(self, services=None):
        self.services = services or {}

    def get_service_info(self, name):
        instance = self.services.get(name)
        return _FakeServiceInfo(instance) if instance is not None else None

    def get_service(self, name):
        return self.services.get(name)


class _TokenRollbackHMR:
    def __init__(self):
        self.tokens = []

    async def rollback_token(self, token):
        self.tokens.append(token)
        return {"ok": True}


class _NoTokenRollbackHMR:
    pass


class _PluginManager:
    def __init__(self):
        self.loaded = []
        self.unloaded = []

    def load_plugin(self, plugin_name):
        self.loaded.append(plugin_name)
        return True

    def unload_plugin(self, plugin_name):
        self.unloaded.append(plugin_name)
        return True


class _AgentOrchestrator:
    def __init__(self):
        self.registered = []
        self.unregistered = []

    def register_agent(self, agent_id, name, capabilities):
        self.registered.append(
            {
                "agent_id": agent_id,
                "name": name,
                "capabilities": list(capabilities),
            }
        )
        return True

    def unregister_agent(self, agent_id):
        self.unregistered.append(agent_id)
        return True


class _AetherScriptService:
    def __init__(self):
        self.executed = []

    async def execute_script_file(self, path):
        self.executed.append(path)
        return {"success": True, "result": {"ok": True}}


class _ActionUnsupportedHMR:
    async def rollback_token(self, token):
        return {"ok": False, "error": "should_not_be_called"}

    def supports_rollback_action(self, action):
        return False


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


@pytest.mark.asyncio
async def test_trigger_integrate_blocks_hmr_action_without_rollback_controller(
    service,
):
    service.config.hmr_enabled = True
    service.service_registry = None
    plan = _ready_plan("plan-no-rollback-controller")

    with (
        patch.object(service, "_run_integration_planning", return_value=plan),
        patch.object(
            service, "_evaluate_plan_ethics", new=AsyncMock()
        ) as evaluate_ethics,
        patch.object(
            service.core_integrator, "execute_plan", new=AsyncMock()
        ) as execute_plan,
    ):
        result = await service.trigger_integrate(dry_run=False)

    assert result["ok"] is False
    assert result["status"] == "rollback_unavailable"
    assert result["reason"] == (
        "rollback_unavailable:register_plugin:hmr_controller_unavailable"
    )
    assert evaluate_ethics.await_count == 0
    assert execute_plan.await_count == 0


@pytest.mark.asyncio
async def test_trigger_integrate_blocks_hmr_action_without_token_rollback_support(
    service,
):
    service.config.hmr_enabled = True
    service.service_registry = _FakeRegistry(
        {"hmr_controller": _NoTokenRollbackHMR()}
    )
    plan = _ready_plan("plan-no-token-rollback")

    with (
        patch.object(service, "_run_integration_planning", return_value=plan),
        patch.object(
            service, "_evaluate_plan_ethics", new=AsyncMock()
        ) as evaluate_ethics,
        patch.object(
            service.core_integrator, "execute_plan", new=AsyncMock()
        ) as execute_plan,
    ):
        result = await service.trigger_integrate(dry_run=False)

    assert result["ok"] is False
    assert result["status"] == "rollback_unavailable"
    assert result["reason"] == (
        "rollback_unavailable:register_plugin:hmr_token_rollback_unsupported"
    )
    assert evaluate_ethics.await_count == 0
    assert execute_plan.await_count == 0


@pytest.mark.asyncio
async def test_trigger_integrate_blocks_hmr_action_when_action_rollback_unsupported(
    service,
):
    service.config.hmr_enabled = True
    service.service_registry = _FakeRegistry(
        {"hmr_controller": _ActionUnsupportedHMR()}
    )
    plan = _ready_plan("plan-action-rollback-unsupported")

    with (
        patch.object(service, "_run_integration_planning", return_value=plan),
        patch.object(
            service, "_evaluate_plan_ethics", new=AsyncMock()
        ) as evaluate_ethics,
        patch.object(
            service.core_integrator, "execute_plan", new=AsyncMock()
        ) as execute_plan,
    ):
        result = await service.trigger_integrate(dry_run=False)

    assert result["ok"] is False
    assert result["status"] == "rollback_unavailable"
    assert result["reason"] == (
        "rollback_unavailable:register_plugin:hmr_action_rollback_unsupported"
    )
    assert evaluate_ethics.await_count == 0
    assert execute_plan.await_count == 0


@pytest.mark.asyncio
async def test_trigger_integrate_allows_dry_run_without_rollback_controller(
    service,
):
    service.config.hmr_enabled = True
    service.service_registry = None
    plan = _ready_plan("plan-dry-run-no-controller")

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
        ) as execute_plan,
    ):
        result = await service.trigger_integrate(dry_run=True)

    assert result["ok"] is True
    assert execute_plan.await_count == 1


@pytest.mark.asyncio
async def test_trigger_integrate_surfaces_workflow_rollback_token(service):
    file_id = _store_workflow_file(service, file_id="workflow-integrate-token")
    plan = {
        "plan_id": "workflow-integrate-token-plan",
        "status": "ready",
        "actions": [
            {
                "action": "register_workflow",
                "target": {"file_id": file_id},
                "deps": [],
            }
        ],
    }

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
    ):
        result = await service.trigger_integrate(dry_run=False)

    rollback_token = result["last_rollback_token"]
    assert result["ok"] is True
    assert result["rollback_tokens"] == [rollback_token]
    assert rollback_token.startswith("rb_register_workflow_")
    assert service.metrics["last_rollback_token"] == rollback_token
    plan_audit = next(
        record
        for record in service.audit_ledger.recent(limit=10)
        if record["action"] == "integration_plan"
    )
    assert plan_audit["result"]["rollback_token_count"] == 1
    assert rollback_token not in json.dumps(plan_audit)


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


@pytest.mark.asyncio
async def test_workflow_apply_produces_truthful_rollback_token(service):
    file_id = _store_workflow_file(service)
    plan = {
        "plan_id": "workflow-rollback-plan",
        "status": "ready",
        "actions": [
            {
                "action": "register_workflow",
                "target": {"file_id": file_id},
                "deps": [],
            }
        ],
    }

    apply_result = await service.core_integrator.execute_plan(plan, dry_run=False)

    assert apply_result["ok"] is True
    assert apply_result["applied"] == 1
    workflow_result = apply_result["results"][0]
    rollback_token = workflow_result["rollback_token"]
    workflow_name = workflow_result["name"]
    assert service._workflows[workflow_name]["rollback_token"] == rollback_token

    rollback_result = await service.trigger_rollback(rollback_token)

    assert rollback_result["ok"] is True
    assert rollback_result["rollback"]["status"] == "rolled_back"
    assert workflow_name not in service._workflows


@pytest.mark.asyncio
async def test_rollback_does_not_claim_success_for_unsupported_record(service):
    rollback_token = "rb_unsupported_record"
    service.audit_ledger.append(
        plan_id="unsupported-plan",
        action="integration_plan",
        status="applied",
        target={"plan_id": "unsupported-plan"},
        result={"rollback_token": rollback_token},
    )

    result = await service.trigger_rollback(rollback_token)

    assert result["ok"] is False
    assert result["error"] == "rollback_operation_unsupported"


@pytest.mark.asyncio
async def test_hmr_rollback_uses_controller_token_contract(service):
    rollback_token = "rb_hmr_supported_record"
    hmr = _TokenRollbackHMR()
    service.service_registry = _FakeRegistry({"hmr_controller": hmr})
    service.audit_ledger.append(
        plan_id="hmr-plan",
        action="register_plugin",
        status="applied",
        target={"plan_id": "hmr-plan"},
        result={"rollback_token": rollback_token},
    )

    result = await service.trigger_rollback(rollback_token)

    assert result["ok"] is True
    assert result["rollback"]["status"] == "rolled_back"
    assert hmr.tokens == [rollback_token]


@pytest.mark.asyncio
async def test_hmr_plugin_apply_registers_truthful_controller_rollback(service):
    file_id = _store_plugin_file(service, file_id="plugin-hmr-token-file")
    plugin_manager = _PluginManager()
    service.plugin_manager = plugin_manager
    hmr = HMRController(_FakeRegistry(), object(), strict=True)
    service.service_registry = _FakeRegistry({"hmr_controller": hmr})
    plan = {
        "plan_id": "plugin-hmr-token-plan",
        "status": "ready",
        "actions": [
            {
                "action": "register_plugin",
                "target": {"file_id": file_id},
                "deps": [],
            }
        ],
    }

    apply_result = await service.core_integrator.execute_plan(plan, dry_run=False)
    rollback_token = apply_result["results"][0]["rollback_token"]
    rollback_result = await service.trigger_rollback(rollback_token)

    assert apply_result["ok"] is True
    assert plugin_manager.loaded == ["test_plugin"]
    assert rollback_result["ok"] is True
    assert plugin_manager.unloaded == ["test_plugin"]


@pytest.mark.asyncio
async def test_hmr_agent_apply_registers_truthful_controller_rollback(service):
    file_id = _store_agent_file(service, file_id="agent-hmr-token-file")
    agent_orchestrator = _AgentOrchestrator()
    service.agent_orchestrator = agent_orchestrator
    hmr = HMRController(_FakeRegistry(), object(), strict=True)
    service.service_registry = _FakeRegistry({"hmr_controller": hmr})
    plan = {
        "plan_id": "agent-hmr-token-plan",
        "status": "ready",
        "actions": [
            {
                "action": "register_agent",
                "target": {"file_id": file_id},
                "deps": [],
            }
        ],
    }

    apply_result = await service.core_integrator.execute_plan(plan, dry_run=False)
    rollback_token = apply_result["results"][0]["rollback_token"]
    rollback_result = await service.trigger_rollback(rollback_token)

    assert apply_result["ok"] is True
    assert agent_orchestrator.registered[0]["agent_id"] == "test_agent"
    assert rollback_result["ok"] is True
    assert agent_orchestrator.unregistered == ["test_agent"]


@pytest.mark.asyncio
async def test_script_apply_rolls_back_selfinc_applied_marker_only(service):
    file_id = _store_script_file(service, file_id="script-marker-file")
    script_service = _AetherScriptService()
    service.aether_script_service = script_service
    plan = {
        "plan_id": "script-marker-rollback-plan",
        "status": "ready",
        "actions": [
            {
                "action": "load_aether_script",
                "target": {"file_id": file_id},
                "deps": [],
            }
        ],
    }

    apply_result = await service.core_integrator.execute_plan(plan, dry_run=False)
    script_result = apply_result["results"][0]
    rollback_token = script_result["rollback_token"]
    script_key = script_result["script_key"]

    assert apply_result["ok"] is True
    assert script_key in service.core_integrator._applied_scripts
    assert script_result["rollback_scope"] == "selfinc_applied_script_marker"

    rollback_result = await service.trigger_rollback(rollback_token)

    assert rollback_result["ok"] is True
    assert rollback_result["rollback"]["rollback_scope"] == (
        "selfinc_applied_script_marker"
    )
    assert script_key not in service.core_integrator._applied_scripts
    assert script_service.executed == [str(Path("scripts") / "test_script.aether")]


@pytest.mark.asyncio
async def test_proposal_actions_require_guardian_before_execution(
    monkeypatch,
    service,
    guardian_env,
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    service._running = True
    proposal = {
        "proposal_id": "proposal-action-denied",
        "type": "optimize",
        "params": {
            "actions": [
                {
                    "action": "register_workflow",
                    "target": {"file_id": "workflow-denied"},
                    "deps": [],
                }
            ],
            "dry_run": False,
        },
    }

    with patch.object(
        service.core_integrator,
        "execute_plan",
        new=AsyncMock(),
    ) as execute_plan:
        result = await service.handle_improvement_proposal(proposal)

    assert result["status"] == "rejected"
    assert result["details"]["reason"] == "missing_capability"
    assert execute_plan.await_count == 0
