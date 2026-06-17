import asyncio
import json

from Aetherra.guardian.approval import resolve_approval
from tools import deploy_storm_shadow


def _configure_deployment(monkeypatch, tmp_path):
    audit_root = tmp_path / "audit"
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(audit_root))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_MEMORY_STORM", "1")
    monkeypatch.setenv("AETHERRA_STORM_SHADOW_MODE", "1")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    monkeypatch.setattr(deploy_storm_shadow, "print_header", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(deploy_storm_shadow, "print_status", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        deploy_storm_shadow,
        "print_deployment_summary",
        lambda *_args, **_kwargs: None,
    )
    return audit_root


def _guardian_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _patch_readiness_checks(monkeypatch, calls):
    async def memory_engine_ok():
        return True, []

    async def smoke_ok():
        calls["smoke"] += 1
        return True, []

    def metrics_ok():
        calls["metrics"] += 1
        return True, []

    monkeypatch.setattr(deploy_storm_shadow, "check_environment", lambda: (True, []))
    monkeypatch.setattr(deploy_storm_shadow, "check_storm_config", lambda: (True, []))
    monkeypatch.setattr(deploy_storm_shadow, "check_memory_engine", memory_engine_ok)
    monkeypatch.setattr(deploy_storm_shadow, "run_smoke_test", smoke_ok)
    monkeypatch.setattr(deploy_storm_shadow, "check_metrics_available", metrics_ok)


def test_storm_full_deployment_gate_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_deployment(monkeypatch, tmp_path)
    calls = {"smoke": 0, "metrics": 0}
    _patch_readiness_checks(monkeypatch, calls)
    pending_decision = deploy_storm_shadow._guardian_preflight_full_validation()
    approval_id = pending_decision.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    result = asyncio.run(deploy_storm_shadow.main(check_only=False))
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert calls == {"smoke": 1, "metrics": 1}
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.deployment_gate"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "STORM shadow mode deployment test memory" not in ledger_text
    assert deploy_storm_shadow.METRICS_ENDPOINT not in ledger_text


def test_storm_full_deployment_gate_denies_external_requester_before_side_effects(
    monkeypatch, tmp_path
):
    audit_root = _configure_deployment(monkeypatch, tmp_path)
    calls = {"smoke": 0, "metrics": 0}
    _patch_readiness_checks(monkeypatch, calls)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")

    result = asyncio.run(deploy_storm_shadow.main(check_only=False))
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert calls == {"smoke": 0, "metrics": 0}
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.deployment_gate"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"
