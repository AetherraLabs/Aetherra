from Aetherra.runtime_ui import (
    ObservatoryMode,
    SubsystemStatus,
    build_observatory_state,
)


def test_observatory_state_is_read_only_and_contains_core_systems():
    state = build_observatory_state(
        user_name="Tim",
        mode=ObservatoryMode.FIRST_LAUNCH,
        system_status={
            "guardian": {"status": "active", "health": 1.0, "activity": 0.7},
            "security": {"status": "active", "health": 0.98, "activity": 0.5},
            "homeostasis": {"status": "stable", "health": 0.92, "activity": 0.3},
            "memory": {"status": "stable", "health": 0.88, "activity": 0.4},
        },
    )
    payload = state.to_dict()

    assert payload["core_label"] == "AETHERRA"
    assert payload["greeting"] == "Good morning, Tim."
    assert payload["read_only"] is True
    assert payload["mode"] == "first_launch"

    systems = {subsystem["name"]: subsystem for subsystem in payload["subsystems"]}
    assert systems["guardian"]["status"] == "active"
    assert systems["security"]["status"] == "active"
    assert systems["homeostasis"]["status"] == "stable"
    assert systems["memory"]["status"] == "stable"
    assert "self_incorporation" in systems
    assert "integration_validation" in systems


def test_observatory_connections_reflect_degraded_or_contained_state():
    state = build_observatory_state(
        system_status={
            "guardian": {"status": "contained", "activity": 1.0},
            "security": {"status": "active", "activity": 0.2},
            "maintenance": {"status": "degraded", "activity": 0.6},
            "homeostasis": {"status": "stable", "activity": 0.4},
        }
    )

    connections = {
        (connection.source, connection.target): connection
        for connection in state.connections
    }

    assert (
        connections[("guardian", "security")].status
        == SubsystemStatus.CONTAINED
    )
    assert (
        connections[("homeostasis", "maintenance")].status
        == SubsystemStatus.DEGRADED
    )
    assert connections[("guardian", "security")].activity == 1.0


def test_observatory_events_are_bounded_and_serializable():
    state = build_observatory_state(
        mode=ObservatoryMode.ARCHITECT,
        events=[
            {
                "source": "guardian",
                "event_type": "decision",
                "summary": "Allowed bounded validation request",
                "severity": "info",
                "details": {"audit_id_hash": "abc123"},
            }
        ],
    )
    payload = state.to_dict()

    assert payload["lyrixa_guidance"].startswith("Architect Mode")
    assert payload["events"] == [
        {
                "source": "guardian",
                "event_type": "decision",
                "summary": "Allowed bounded validation request",
                "severity": "info",
                "visual_channel": "governance",
                "action_required": False,
                "occurred_at": payload["events"][0]["occurred_at"],
                "details": {"audit_id_hash": "abc123"},
            }
        ]


def test_observatory_events_normalize_visual_channel_and_action_required():
    state = build_observatory_state(
        events=[
            {
                "source": "guardian",
                "event_type": "containment",
                "summary": "Unsafe action contained",
                "severity": "critical",
            },
            {
                "source": "self_improvement",
                "event_type": "proposal",
                "summary": "Index tuning proposed",
                "severity": "notice",
            },
        ],
    )
    events = state.to_dict()["events"]

    assert events[0]["visual_channel"] == "containment"
    assert events[0]["action_required"] is True
    assert events[1]["visual_channel"] == "evolution"
    assert events[1]["action_required"] is False
