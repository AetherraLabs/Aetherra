import asyncio
import json

from aetherra_script_service import AetherScriptService


def _guardian_env(monkeypatch, tmp_path, *, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def test_script_execution_is_guardian_audited_without_source_payload(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    service = AetherScriptService()
    asyncio.run(service.initialize())

    result = asyncio.run(
        service.execute_script_content(
            """
goal "private script goal"
require
    capabilities = ["memory.read", "private.capability"]
    plugins = ["private_plugin>=1.0"]
private_value = "do-not-audit-this-script-value"
""",
            filename=str(tmp_path / "private_workflow.aether"),
        )
    )

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in ledger_text.splitlines() if line.strip()]
    script_entry = next(
        entry
        for entry in entries
        if entry["details"]["intent"]["action"] == "script.execute"
    )
    metadata = script_entry["details"]["intent"]["metadata"]

    assert result["success"] is True
    assert "private script goal" not in ledger_text
    assert "do-not-audit-this-script-value" not in ledger_text
    assert "private.capability" not in ledger_text
    assert "private_plugin" not in ledger_text
    assert metadata["declared_capability_count"] == 2
    assert len(metadata["declared_capability_hashes"]) == 2
    assert metadata["declared_plugin_count"] == 1
    assert metadata["declared_plugin_hashes"]
    assert metadata["script_hash"]


def test_script_execution_guardian_denial_prevents_interpreter_mutation(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path, strict=True)
    service = AetherScriptService()
    asyncio.run(service.initialize())

    result = asyncio.run(
        service.execute_script_content(
            'blocked_value = "should-not-execute"',
            filename=str(tmp_path / "blocked.aether"),
            context={"_requester": "external-script-runner"},
        )
    )

    assert result["success"] is False
    assert result["error"] == "guardian_denied"
    assert "blocked_value" not in service._last_ctx
