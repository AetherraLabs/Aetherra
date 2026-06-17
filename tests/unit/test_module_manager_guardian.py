import asyncio
import json

import pytest

from aetherra_module_manager import ModuleManager


class _Registry:
    def __init__(self):
        self.messages = []

    async def broadcast_message(self, message_type, data):
        self.messages.append((message_type, data))


@pytest.fixture
def guardian_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return tmp_path


def _audit_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_module_load_writes_guardian_audit_without_spec_values(guardian_env):
    manager = ModuleManager(_Registry())

    result = asyncio.run(
        manager.load_module(
            "demo_module",
            {
                "version": "1.0",
                "secret": "do-not-audit-this-value",
            },
        )
    )
    entries = _audit_entries(guardian_env)

    assert result["ok"] is True
    assert entries[-1]["details"]["intent"]["action"] == "module_manager.load"
    assert "module_lifecycle" in entries[-1]["details"]["risk"]["factors"]
    assert "do-not-audit-this-value" not in json.dumps(entries[-1])


def test_module_load_blocks_explicit_requester_without_capability(
    monkeypatch, guardian_env
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(guardian_env / "policy"))
    manager = ModuleManager(_Registry())

    with pytest.raises(PermissionError, match="missing_capability"):
        asyncio.run(
            manager.load_module(
                "blocked_module",
                {"guardian_requester": "untrusted_operator"},
            )
        )

    assert manager.get_status()["modules"] == []


def test_module_reload_unload_and_rollback_write_guardian_audit(guardian_env):
    manager = ModuleManager(_Registry())

    assert asyncio.run(manager.reload_module("demo_module", {"version": "1.1"}))["ok"]
    assert asyncio.run(manager.unload_module("demo_module")) == {"ok": True}
    assert asyncio.run(manager.rollback_module("demo_module"))["ok"]
    entries = _audit_entries(guardian_env)

    assert entries[-3]["details"]["intent"]["action"] == "module_manager.reload"
    assert entries[-2]["details"]["intent"]["action"] == "module_manager.unload"
    assert entries[-1]["details"]["intent"]["action"] == "module_manager.rollback"
    metrics = manager.get_metrics()
    assert metrics["loads_total"] == 1
    assert metrics["reloads_total"] == 1
    assert metrics["rollbacks_total"] == 1
