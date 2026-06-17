import json

from Aetherra.guardian.approval import resolve_approval
from tools.maintenance.complete_organizer import ComprehensiveAetherraOrganizer


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


def _create_core_tree(tmp_path):
    base = tmp_path / "workspace" / "Aetherra" / "aetherra_core"
    source = base / "engine" / "intelligence.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 'move me'\n", encoding="utf-8")
    consumer = base / "consumer.py"
    consumer.write_text(
        "from aetherra_core.engine.intelligence import VALUE\n",
        encoding="utf-8",
    )
    (base / "intelligence").mkdir(parents=True)
    return base, source, base / "intelligence" / "core_intelligence.py", consumer


def test_complete_organizer_dry_run_does_not_require_guardian(monkeypatch, tmp_path):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    base, source, destination, _consumer = _create_core_tree(tmp_path)
    organizer = ComprehensiveAetherraOrganizer(base_path=base, dry_run=True)
    monkeypatch.setattr(organizer, "_guardian_preflight_execute", None)

    organizer.run_complete_organization()

    assert source.exists()
    assert not destination.exists()
    assert (tmp_path / "COMPREHENSIVE_ORGANIZATION_REPORT.md").exists()
    assert _guardian_entries(audit_root) == []


def test_complete_organizer_execute_uses_guardian_approval_and_sanitized_audit(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    base, source, destination, consumer = _create_core_tree(tmp_path)
    organizer = ComprehensiveAetherraOrganizer(base_path=base, dry_run=False)
    moves = organizer.get_comprehensive_reorganization_plan()
    pending = organizer._guardian_preflight_execute(moves)
    approval_id = pending.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="guardian-test")
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", approval_id)

    organizer.run_complete_organization()
    entries = _guardian_entries(audit_root)
    ledger_text = (
        audit_root / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert not source.exists()
    assert destination.exists()
    assert (
        tmp_path / "comprehensive_cleanup_backup" / "engine" / "intelligence.py"
    ).exists()
    assert "aetherra_core.intelligence.core_intelligence" in consumer.read_text(
        encoding="utf-8"
    )
    assert entries[-1]["details"]["intent"]["action"] == (
        "maintenance.complete_organization"
    )
    assert entries[-1]["details"]["decision"]["reason"] == "approved_with_guardian_approval"
    assert "maintenance_operation" in entries[-1]["details"]["risk"]["factors"]
    assert "intelligence.py" not in ledger_text


def test_complete_organizer_execute_denies_external_requester_before_mutation(
    monkeypatch, tmp_path
):
    audit_root = _configure_guardian(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(audit_root / "policy"))
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "untrusted_operator")
    base, source, destination, consumer = _create_core_tree(tmp_path)
    organizer = ComprehensiveAetherraOrganizer(base_path=base, dry_run=False)

    organizer.run_complete_organization()
    entries = _guardian_entries(audit_root)

    assert source.exists()
    assert not destination.exists()
    assert "aetherra_core.engine.intelligence" in consumer.read_text(encoding="utf-8")
    assert not (tmp_path / "comprehensive_cleanup_backup").exists()
    assert not (tmp_path / "COMPREHENSIVE_ORGANIZATION_REPORT.md").exists()
    assert entries[-1]["details"]["intent"]["requester"] == "untrusted_operator"
    assert entries[-1]["details"]["decision"]["reason"] == "missing_capability"
