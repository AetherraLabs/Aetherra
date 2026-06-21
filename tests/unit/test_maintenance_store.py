import json

from Aetherra.maintenance import (
    MaintenanceCoordinator,
    MaintenanceDecision,
    MaintenanceEvidence,
    MaintenanceProposal,
    MaintenanceRecordStore,
)


def _proposal() -> MaintenanceProposal:
    return MaintenanceProposal(
        proposal_id="proposal-store-1",
        source="self_improvement",
        target_subsystem="memory",
        issue="memory pressure elevated",
        proposed_action="optimize memory index",
        expected_benefit="lower recall latency",
        risk_level="medium",
        rollback_plan="restore previous memory index",
    )


def _coordinator_with_cycle() -> MaintenanceCoordinator:
    coordinator = MaintenanceCoordinator()
    coordinator.route_proposal(
        _proposal(),
        diagnosis=MaintenanceEvidence(
            source="self_improvement",
            summary="memory index pressure likely cause",
        ),
        guardian_decision=MaintenanceDecision(
            status="allow_limited",
            reason="bounded maintenance proposal",
        ),
        security_allowed=True,
        security_reason="capabilities satisfied",
        cycle_id="maint-store-1",
    )
    return coordinator


def test_record_store_default_uses_approved_generated_output_path(tmp_path):
    store = MaintenanceRecordStore.default(tmp_path)

    assert store.file_path == (
        tmp_path / "artifacts" / "maintenance" / "maintenance_cycles.jsonl"
    )


def test_record_store_blocks_unapproved_destination(tmp_path):
    try:
        MaintenanceRecordStore(
            file_path=tmp_path / "maintenance_cycles.jsonl",
            project_root=tmp_path,
        )
    except ValueError as exc:
        assert "root_level_generated_reports_are_not_allowed" in str(exc)
    else:
        raise AssertionError("Expected unapproved Maintenance record path to fail")


def test_record_store_exports_and_loads_coordinator_records(tmp_path):
    source = _coordinator_with_cycle()
    store = MaintenanceRecordStore.default(tmp_path)

    store.export_from(source)
    restored = MaintenanceCoordinator()
    loaded_count = store.load_into(restored)

    assert loaded_count == 1
    assert restored.get_cycle("maint-store-1").can_execute() is True
    assert restored.get_status()["cycle_count"] == 1


def test_record_store_appends_one_cycle_record(tmp_path):
    coordinator = _coordinator_with_cycle()
    store = MaintenanceRecordStore.default(tmp_path)

    result = store.append_cycle(coordinator, "maint-store-1")

    lines = store.file_path.read_text(encoding="utf-8").splitlines()
    assert result is True
    assert len(lines) == 1
    assert json.loads(lines[0])["cycle_id"] == "maint-store-1"


def test_record_store_append_returns_false_for_unknown_cycle(tmp_path):
    coordinator = MaintenanceCoordinator()
    store = MaintenanceRecordStore.default(tmp_path)

    result = store.append_cycle(coordinator, "missing-cycle")

    assert result is False
    assert not store.file_path.exists()


def test_record_store_rejects_invalid_jsonl(tmp_path):
    store = MaintenanceRecordStore.default(tmp_path)
    store.file_path.parent.mkdir(parents=True, exist_ok=True)
    store.file_path.write_text("{invalid-json}\n", encoding="utf-8")

    try:
        store.load_records()
    except ValueError as exc:
        assert "Invalid Maintenance record at line 1" in str(exc)
    else:
        raise AssertionError("Expected invalid JSONL to raise ValueError")
