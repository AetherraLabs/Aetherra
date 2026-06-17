import json

import pytest

from Aetherra.consciousness.self_model_manager import SelfModelManager


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    audit_root = tmp_path / "audit"
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(audit_root))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    return audit_root


def _audit_text(audit_root):
    return (audit_root / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _last_audit_entry(audit_root):
    entries = [
        json.loads(line)
        for line in _audit_text(audit_root).splitlines()
        if line.strip()
    ]
    return entries[-1]


def test_self_model_update_is_guardian_audited_without_identity_payload(
    monkeypatch, tmp_path
):
    audit_root = _guardian_env(monkeypatch, tmp_path)
    model_path = tmp_path / "self_model.json"
    manager = SelfModelManager(str(model_path))

    manager.update(lambda model: setattr(model.resources, "cpu_load", 12.5))

    assert model_path.exists()
    ledger_text = _audit_text(audit_root)
    assert str(model_path) not in ledger_text
    assert "aetherra-node" not in ledger_text
    entry = _last_audit_entry(audit_root)
    assert entry["details"]["intent"]["action"] == "consciousness.self_model_update"
    assert entry["details"]["intent"]["metadata"]["identity_changed"] is False


def test_self_model_update_guardian_denial_rolls_back_and_skips_write(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-consciousness-client",
        strict=True,
    )
    model_path = tmp_path / "self_model.json"
    manager = SelfModelManager(str(model_path))
    before = manager.get().model_copy(deep=True)

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        manager.update(
            lambda model: setattr(model.identity, "system_id", "do-not-persist-identity")
        )

    assert model_path.exists() is False
    assert manager.get().identity.system_id == before.identity.system_id
