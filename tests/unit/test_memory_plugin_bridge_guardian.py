import json

from Aetherra.aetherra_core.plugins import memory_plugin_bridge


def _configure_guardian(monkeypatch, tmp_path):
    audit_root = tmp_path / "audit"
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(audit_root))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    return audit_root


def _guardian_entries(root):
    audit_path = root / ".aetherra" / "security" / "audit.jsonl"
    if not audit_path.exists():
        return []
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class _ForgetEngine:
    def __init__(self):
        self.deleted = []

    def delete(self, key):
        self.deleted.append(key)


def test_plugin_forget_uses_guardian_and_sanitizes_audit(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    engine = _ForgetEngine()
    monkeypatch.setattr(memory_plugin_bridge, "_engine", engine)

    assert memory_plugin_bridge.plugin_forget("plugin-secret-key") is True
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert engine.deleted == ["plugin-secret-key"]
    assert entries[-1]["details"]["intent"]["action"] == "memory.plugin_forget"
    assert entries[-1]["details"]["decision"]["status"] in {"allow", "allow_limited"}
    assert "plugin-secret-key" not in ledger_text


def test_plugin_forget_denies_external_requester_before_backend_call(
    monkeypatch,
    tmp_path,
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    engine = _ForgetEngine()
    monkeypatch.setattr(memory_plugin_bridge, "_engine", engine)

    assert memory_plugin_bridge.plugin_forget("plugin-secret-key") is False
    entries = _guardian_entries(audit_root)

    assert engine.deleted == []
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"
