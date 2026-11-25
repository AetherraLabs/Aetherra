"""Observer-mode isolation and real Guardian contracts for ConsciousnessCore."""

# Standard library imports
import json

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.qfac import qfac_api
from Aetherra.consciousness.continuity_memory import ContinuityMemory
from Aetherra.consciousness.core import config
from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
from Aetherra.consciousness.core.think_stream import ThinkStream, get_think_stream
from Aetherra.consciousness.core.types import Event, QualiaVector
from Aetherra.perception_bus.bus import PerceptionBus
from Aetherra.security.audit_ledger import SecurityAuditLedger


def _policy(monkeypatch, tmp_path, *, allow=True):
    policy = tmp_path / "policy"
    policy.mkdir()
    path = policy / "guardian.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "default": "deny",
                "allow": (
                    [
                        {
                            "requester": "consciousness:core",
                            "subsystem": "consciousness",
                            "action": f"consciousness.{kind}_reflection_update",
                            "target": f"reflection:{kind}",
                        }
                        for kind in ("micro", "macro")
                    ]
                    if allow
                    else []
                ),
            }
        ),
        encoding="utf-8",
    )
    for key, value in {
        "AETHERRA_GUARDIAN_ENABLED": "1",
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_GUARDIAN_REQUIRE_POLICY": "1",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(policy),
        "AETHERRA_GUARDIAN_POLICY": str(path),
        "AETHERRA_GUARDIAN_STATE_DIR": str(tmp_path / "guardian"),
        "AETHERRA_AUDIT": "1",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    return tmp_path / ".aetherra/security/audit.jsonl"


def _forbidden_disk_load(self):
    raise AssertionError("observer attempted continuity disk read")


def test_observer_construction_does_not_load_shared_continuity(monkeypatch):
    monkeypatch.setattr(ContinuityMemory, "load", _forbidden_disk_load)
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    assert core.continuity.path is None
    assert core.continuity.latest() is None


@pytest.mark.parametrize("injection", ["safety_envelope", "memory_engine"])
def test_observer_rejects_mutating_dependencies_before_loading(monkeypatch, injection):
    monkeypatch.setattr(ContinuityMemory, "load", _forbidden_disk_load)
    with pytest.raises(ValueError, match="observer"):
        ConsciousnessCore(PerceptionBus(), observer_only=True, **{injection: object()})


def test_disabled_continuity_rejects_persistence_without_file_access(monkeypatch):
    monkeypatch.setattr(ContinuityMemory, "load", _forbidden_disk_load)
    memory = ContinuityMemory(path=None)
    with pytest.raises(PermissionError, match="persistence_disabled"):
        memory.save()
    with pytest.raises(PermissionError, match="persistence_disabled"):
        memory.record(QualiaVector(), [], [], {}, tick=1)
    assert memory.buffer == []
    assert memory.get_stats()["persistence_enabled"] is False
    memory.clear()


def test_observer_ticks_keep_real_reflection_audit_but_no_persistence(
    monkeypatch, tmp_path, capsys
):
    audit = _policy(monkeypatch, tmp_path)
    monkeypatch.setattr(config, "ENABLE_QFAC_PERSISTENCE", True)
    monkeypatch.setattr(config, "AUTONOMY_MODE", "autopilot")
    monkeypatch.setattr(config, "CONTINUITY_SNAPSHOT_INTERVAL", 1)
    monkeypatch.setattr(config, "MACRO_REFLECTION_INTERVAL", 1)
    monkeypatch.setattr(config, "DEBUG_CONSCIOUSNESS", True)
    bus = PerceptionBus()
    bus.publish(
        Event(
            type="svc.health",
            payload={"service": "private-service", "restarts_1h": 8},
            source="private-source",
        )
    )
    bus.publish(Event(type="mem.pressure", payload={"secret": "private-payload"}))
    before_records = dict(qfac_api._store._by_id)
    core = ConsciousnessCore(bus, observer_only=True)
    snapshots = []
    core.ui.register_ui_callback(snapshots.append)
    core.tick()
    core.tick()
    assert core.total_events_perceived == 2
    assert len(core.narrative_thread) == 2
    assert [state["events_processed"] for state in snapshots] == [2, 2]
    assert all(state["autonomy_mode"] == "observe" for state in snapshots)
    assert core.continuity.buffer == []
    assert dict(qfac_api._store._by_id) == before_records
    assert core.safety_envelope is None
    assert core.memory_engine is None
    entries = [
        json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()
    ]
    actions = [item["details"]["intent"]["action"] for item in entries]
    assert actions.count("consciousness.micro_reflection_update") == 2
    assert actions.count("consciousness.macro_reflection_update") == 2
    assert "memory.qfac_store" not in actions
    assert "consciousness.continuity_save" not in actions
    assert "consciousness.autonomy_plan_execute" not in actions
    assert all(
        item["details"]["intent"]["metadata"]["qfac_enabled"] is False
        for item in entries
    )
    assert "private-service" not in audit.read_text(encoding="utf-8")
    assert "private-source" not in audit.read_text(encoding="utf-8")
    assert "private-payload" not in audit.read_text(encoding="utf-8")
    assert "private" not in capsys.readouterr().out


def test_observer_guardian_denial_prevents_reflection_and_stream(monkeypatch, tmp_path):
    audit = _policy(monkeypatch, tmp_path, allow=False)
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    snapshots = []
    core.ui.register_ui_callback(snapshots.append)
    with pytest.raises(PermissionError, match="guardian_denied"):
        core.tick()
    assert core.narrative_thread == []
    assert snapshots == []
    assert core.ui.tick_count == 0
    assert core.continuity.buffer == []
    entries = [
        json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()
    ]
    assert (
        entries[-1]["details"]["intent"]["action"]
        == "consciousness.micro_reflection_update"
    )
    assert entries[-1]["details"]["decision"]["status"] == "deny"


def test_observer_status_is_read_only_and_reports_effective_mode(monkeypatch, tmp_path):
    audit = _policy(monkeypatch, tmp_path)
    monkeypatch.setattr(config, "AUTONOMY_MODE", "autopilot")
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    first = core.get_status()
    second = core.get_status()
    assert first["autonomy_mode"] == second["autonomy_mode"] == "observe"
    assert first["observer_only"] is True
    assert first["continuity"]["persistence_enabled"] is False
    assert first["continuity"]["snci"] is None
    assert first["autopilot"]["available"] is False
    assert core.autopilot.last_eval is None
    assert not audit.exists()


def test_observer_rejects_direct_actuation_even_if_dependency_is_attached():
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    core.safety_envelope = object()
    with pytest.raises(PermissionError, match="observer"):
        core._maybe_act()


def test_observer_rejects_direct_snapshot_request():
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    with pytest.raises(PermissionError, match="persistence_disabled"):
        core._record_continuity_snapshot()
    assert core.continuity.buffer == []


def test_observers_do_not_share_callbacks_or_ticks(monkeypatch, tmp_path):
    _policy(monkeypatch, tmp_path)
    first = ConsciousnessCore(PerceptionBus(), observer_only=True)
    second = ConsciousnessCore(PerceptionBus(), observer_only=True)
    assert first.ui is not second.ui
    assert first.ui is not get_think_stream()
    one, two = [], []
    first.ui.register_ui_callback(one.append)
    second.ui.register_ui_callback(two.append)
    first.tick()
    assert len(one) == 1
    assert two == []
    assert second.ui.tick_count == 0
    second.tick()
    assert len(one) == len(two) == 1
    assert first.ui.tick_count == second.ui.tick_count == 1


def test_think_stream_exact_zero_and_observe_override_preserve_legacy_defaults(
    monkeypatch,
):
    monkeypatch.setattr(config, "AUTONOMY_MODE", "assist")
    stream = ThinkStream()
    snapshots = []
    stream.register_ui_callback(snapshots.append)
    stream.on_tick(QualiaVector(), [], [], events_processed=0, autonomy_mode="observe")
    stream.on_tick(QualiaVector(), [], [])
    assert snapshots[0]["events_processed"] == 0
    assert snapshots[0]["autonomy_mode"] == "observe"
    assert snapshots[1]["events_processed"] == 2
    assert snapshots[1]["autonomy_mode"] == "assist"


@pytest.mark.parametrize("reflection", ["micro", "macro"])
def test_observer_reflection_requires_a_successful_audit_append(
    monkeypatch, tmp_path, reflection
):
    audit = _policy(monkeypatch, tmp_path)
    attempted_records = []

    def fail_append(self, encoded):
        attempted_records.append(json.loads(encoded))
        raise OSError("synthetic full audit disk")

    monkeypatch.setattr(SecurityAuditLedger, "_append_bytes", fail_append)
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    core.ql.p.curiosity_gain = 0.75
    snapshots = []
    core.ui.register_ui_callback(snapshots.append)
    operation = core.tick if reflection == "micro" else core._reflect_macro
    with pytest.raises(PermissionError, match="guardian_audit_unavailable"):
        operation()
    assert len(attempted_records) == 1
    assert attempted_records[0]["details"]["decision"]["status"] in {
        "allow",
        "allow_limited",
    }
    assert attempted_records[0]["details"]["intent"]["action"] == (
        f"consciousness.{reflection}_reflection_update"
    )
    assert not audit.exists()
    assert core.narrative_thread == []
    assert core.ql.p.curiosity_gain == 0.75
    assert snapshots == []
    assert core.ui.tick_count == 0


@pytest.mark.parametrize("reflection", ["micro", "macro"])
def test_observer_reflection_preserves_corrupt_audit_and_rejects_missing_receipt(
    monkeypatch, tmp_path, reflection
):
    audit = _policy(monkeypatch, tmp_path)
    ledger = SecurityAuditLedger(audit)
    record = ledger.append(actor="test", event_type="synthetic_seed")
    record["reason"] = "tampered"
    audit.write_text(json.dumps(record) + "\n", encoding="utf-8")
    original = audit.read_bytes()
    assert ledger.verify_integrity() is False
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    core.ql.p.curiosity_gain = 0.75
    snapshots = []
    core.ui.register_ui_callback(snapshots.append)
    operation = core.tick if reflection == "micro" else core._reflect_macro
    with pytest.raises(PermissionError, match="guardian_audit_unavailable"):
        operation()
    assert audit.read_bytes() == original
    assert ledger.verify_integrity() is False
    assert core.narrative_thread == []
    assert core.ql.p.curiosity_gain == 0.75
    assert snapshots == []
    assert core.ui.tick_count == 0


@pytest.mark.parametrize("ambient_capacity", [0, -5, 1_000_000_000])
def test_observer_retains_bounded_recent_state_despite_standalone_capacity(
    monkeypatch, tmp_path, ambient_capacity
):
    _policy(monkeypatch, tmp_path)
    monkeypatch.setattr(config, "MAX_WORKING_MEMORY", ambient_capacity)
    monkeypatch.setattr(config, "MAX_NARRATIVE_MOMENTS", ambient_capacity)
    bus = PerceptionBus()
    core = ConsciousnessCore(bus, observer_only=True)
    core.ui.register_ui_callback(lambda snapshot: None)
    for index in range(80):
        bus.publish(
            Event(
                type="svc.health",
                payload={"service": f"synthetic-{index}", "restarts_1h": 8},
            )
        )
        core.tick()
    assert core.total_events_perceived == core.total_intents_formed == 80
    assert len(core.working_memory) == 64
    assert core.working_memory[0].payload["service"] == "synthetic-16"
    assert core.working_memory[-1].payload["service"] == "synthetic-79"
    assert len(core.narrative_thread) == 64
    assert "synthetic-79" in core.narrative_thread[-1].text
    assert len(core.active_intents) == 64
    assert core.active_intents[-1].goal == "Stabilize synthetic-79"


def test_standalone_reflection_retains_existing_audit_failure_contract(
    monkeypatch, tmp_path
):
    _policy(monkeypatch, tmp_path)
    monkeypatch.setattr(ContinuityMemory, "load", lambda self: None)
    monkeypatch.setattr(config, "ENABLE_QFAC_PERSISTENCE", False)

    def fail_append(self, encoded):
        raise OSError("synthetic full audit disk")

    monkeypatch.setattr(SecurityAuditLedger, "_append_bytes", fail_append)
    core = ConsciousnessCore(PerceptionBus())
    moment = core._reflect_micro([], [])
    assert core.narrative_thread == [moment]
