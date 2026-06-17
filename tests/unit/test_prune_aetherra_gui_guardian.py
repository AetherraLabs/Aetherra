import json

from Aetherra.guardian.approval import resolve_approval
from tools import prune_aetherra_gui


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


def _configure_gui_tree(monkeypatch, tmp_path):
    root = tmp_path / "workspace"
    gui = root / "Aetherra" / "gui"
    gui.mkdir(parents=True)
    (gui / "aetherra_os_gui.py").write_text("keep", encoding="utf-8")
    (gui / "legacy-dashboard.py").write_text("legacy", encoding="utf-8")
    legacy_dir = gui / "web_dashboard"
    legacy_dir.mkdir()
    (legacy_dir / "index.html").write_text("legacy", encoding="utf-8")
    monkeypatch.setattr(prune_aetherra_gui, "ROOT", root)
    monkeypatch.setattr(prune_aetherra_gui, "GUI_DIR", gui)
    return gui, legacy_dir


def test_prune_aetherra_gui_dry_run_does_not_require_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    gui, legacy_dir = _configure_gui_tree(monkeypatch, tmp_path)
    monkeypatch.setattr(prune_aetherra_gui, "_guardian_preflight_apply", None)
    monkeypatch.setattr("sys.argv", ["prune_aetherra_gui.py"])

    result = prune_aetherra_gui.main()

    assert result == 0
    assert (gui / "legacy-dashboard.py").exists()
    assert legacy_dir.exists()
    assert _guardian_entries(audit_root) == []


def test_prune_aetherra_gui_apply_writes_guardian_audit_without_raw_paths(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    gui, legacy_dir = _configure_gui_tree(monkeypatch, tmp_path)
    pending = prune_aetherra_gui._guardian_preflight_apply()
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)
    monkeypatch.setattr("sys.argv", ["prune_aetherra_gui.py", "--apply"])

    result = prune_aetherra_gui.main()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert result == 0
    assert (gui / "aetherra_os_gui.py").exists()
    assert not (gui / "legacy-dashboard.py").exists()
    assert not legacy_dir.exists()
    assert entries[-1]["details"]["intent"]["action"] == "maintenance.aetherra_gui_prune"
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "legacy-dashboard.py" not in ledger_text
    assert "web_dashboard" not in ledger_text


def test_prune_aetherra_gui_apply_denies_external_requester_before_delete(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    gui, legacy_dir = _configure_gui_tree(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    monkeypatch.setattr("sys.argv", ["prune_aetherra_gui.py", "--apply"])

    result = prune_aetherra_gui.main()
    entries = _guardian_entries(audit_root)

    assert result == 1
    assert (gui / "legacy-dashboard.py").exists()
    assert legacy_dir.exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"
