import asyncio
import json

import pytest

from aetherra_hmr_controller import HMRController


class _Registry:
    def __init__(self):
        self.messages = []

    async def broadcast_message(self, message_type, data):
        self.messages.append((message_type, data))


class _Kernel:
    def __init__(self):
        self.attempts = 0
        self.successes = 0
        self.rollbacks = 0
        self.swaps = []

    def record_hmr_attempt(self, target):
        self.attempts += 1

    def record_hmr_success(self, target, swap_ms):
        self.successes += 1

    def record_hmr_rollback(self, target):
        self.rollbacks += 1

    async def quiesce_for_target(self, target, timeout_sec):
        return True

    async def swap_system(self, target, instance):
        self.swaps.append((target, instance))
        return True

    def get_status(self):
        return {"ok": True}


class _PluginManager:
    def __init__(self):
        self.unloaded = []

    def unload_plugin(self, plugin_name):
        self.unloaded.append(plugin_name)
        return True


class _KernelWithPlugins(_Kernel):
    def __init__(self):
        super().__init__()
        self.plugin_manager = _PluginManager()


class _AgentOrchestrator:
    def __init__(self):
        self.unregistered = []

    def unregister_agent(self, agent_id):
        self.unregistered.append(agent_id)
        return True


class _KernelWithAgents(_Kernel):
    def __init__(self):
        super().__init__()
        self.agent_orchestrator = _AgentOrchestrator()


@pytest.fixture
def guardian_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_HMR_AUDIT_PATH", str(tmp_path / "hmr_audit.jsonl"))
    monkeypatch.setenv("AETHERRA_HMR_ALLOWED_SOURCES", "trusted.module,C:/trusted/*")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return tmp_path


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_hmr_reload_writes_guardian_audit(monkeypatch, guardian_env):
    controller = HMRController(_Registry(), _Kernel(), strict=True)
    shadow = object()

    async def load_shadow(target, source):
        return shadow

    monkeypatch.setattr(controller, "_load_shadow", load_shadow)

    result = asyncio.run(
        controller.handle_kernel_task(
            {
                "type": "hmr_reload",
                "data": {
                    "target": "engine",
                    "source": "trusted.module",
                    "mode": "safe",
                },
            }
        )
    )
    entries = _audit_entries(guardian_env)

    assert result["ok"] is True
    assert entries[-1]["details"]["intent"]["action"] == "hmr.reload"
    assert "hot_reload" in entries[-1]["details"]["risk"]["factors"]
    assert controller.kernel.attempts == 1
    assert controller.kernel.successes == 1


def test_hmr_reload_blocks_explicit_requester_without_capability(
    monkeypatch, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    controller = HMRController(_Registry(), _Kernel(), strict=True)

    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(
            controller.handle_kernel_task(
                {
                    "type": "hmr_reload",
                    "data": {
                        "target": "engine",
                        "source": "trusted.module",
                        "requester": "untrusted_operator",
                    },
                }
            )
        )

    assert controller.kernel.attempts == 0
    assert controller.kernel.swaps == []


def test_hmr_guardian_audit_omits_raw_source_path(monkeypatch, guardian_env):
    controller = HMRController(_Registry(), _Kernel(), strict=True)
    source = "C:/trusted/do-not-audit-this-value/source.py"

    async def load_shadow(target, source):
        return object()

    monkeypatch.setattr(controller, "_load_shadow", load_shadow)

    result = asyncio.run(
        controller.handle_kernel_task(
            {
                "type": "hmr_reload",
                "data": {
                    "target": "engine",
                    "source": source,
                    "mode": "safe",
                },
            }
        )
    )
    entries = _audit_entries(guardian_env)

    assert result["ok"] is True
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])
    assert source not in json.dumps(entries[-1])


def test_hmr_register_plugin_rollback_token_contract(guardian_env):
    kernel = _KernelWithPlugins()
    controller = HMRController(_Registry(), kernel, strict=True)
    token = "rb_register_plugin_private-plugin_1_abcd"

    registration = controller.register_rollback_token(
        token,
        "register_plugin",
        {"status": "applied", "name": "private-plugin"},
        {"file_id": "private-file"},
    )
    rollback = asyncio.run(controller.rollback_token(token))

    assert registration["ok"] is True
    assert rollback["ok"] is True
    assert kernel.plugin_manager.unloaded == ["private-plugin"]
    assert kernel.rollbacks == 1
    assert token not in controller._rollback_tokens


def test_hmr_register_plugin_rollback_audit_omits_raw_token_and_plugin(
    guardian_env,
):
    kernel = _KernelWithPlugins()
    controller = HMRController(_Registry(), kernel, strict=True)
    token = "rb_register_plugin_do-not-audit-token_1_abcd"

    controller.register_rollback_token(
        token,
        "register_plugin",
        {"status": "applied", "name": "do-not-audit-plugin"},
        {"file_id": "private-file"},
    )
    asyncio.run(controller.rollback_token(token))

    audit_text = (guardian_env / "hmr_audit.jsonl").read_text(encoding="utf-8")
    assert token not in audit_text
    assert "do-not-audit-plugin" not in audit_text


def test_hmr_unsupported_action_does_not_register_token(guardian_env):
    controller = HMRController(_Registry(), _KernelWithPlugins(), strict=True)

    result = controller.register_rollback_token(
        "rb_register_agent_private-agent_1_abcd",
        "register_agent",
        {"status": "applied", "id": "private-agent"},
        {},
    )

    assert result["ok"] is False
    assert result["error"] == "rollback_action_unsupported"


def test_hmr_register_agent_rollback_token_contract(guardian_env):
    kernel = _KernelWithAgents()
    controller = HMRController(_Registry(), kernel, strict=True)
    token = "rb_register_agent_private-agent_1_abcd"

    registration = controller.register_rollback_token(
        token,
        "register_agent",
        {"status": "applied", "id": "private-agent"},
        {"file_id": "private-agent-file"},
    )
    rollback = asyncio.run(controller.rollback_token(token))

    assert registration["ok"] is True
    assert rollback["ok"] is True
    assert kernel.agent_orchestrator.unregistered == ["private-agent"]
    assert kernel.rollbacks == 1
    assert token not in controller._rollback_tokens


def test_hmr_register_agent_rollback_audit_omits_raw_token_and_agent(
    guardian_env,
):
    kernel = _KernelWithAgents()
    controller = HMRController(_Registry(), kernel, strict=True)
    token = "rb_register_agent_do-not-audit-token_1_abcd"

    controller.register_rollback_token(
        token,
        "register_agent",
        {"status": "applied", "id": "do-not-audit-agent"},
        {"file_id": "private-agent-file"},
    )
    asyncio.run(controller.rollback_token(token))

    audit_text = (guardian_env / "hmr_audit.jsonl").read_text(encoding="utf-8")
    assert token not in audit_text
    assert "do-not-audit-agent" not in audit_text
