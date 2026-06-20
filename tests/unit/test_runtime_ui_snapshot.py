from Aetherra.runtime_ui import (
    collect_runtime_ui_events,
    collect_runtime_ui_system_status,
)


def test_runtime_ui_snapshot_collects_core_system_status_without_activation():
    status = collect_runtime_ui_system_status()

    assert status["security"]["status"] == "active"
    assert status["security"]["metrics"]["authority"] == "enforce"
    assert status["homeostasis"]["metrics"]["authority"] == "observe_verify"
    assert status["self_improvement"]["metrics"]["authority"] == "diagnose_propose"
    assert status["self_incorporation"]["metrics"]["authority"] == "execute_after_approval"
    assert "guardian" in status
    assert "available" in status["guardian"]["metrics"]


def test_runtime_ui_snapshot_events_are_bounded_summary_events():
    events = collect_runtime_ui_events()

    assert [event["source"] for event in events] == [
        "runtime_ui",
        "guardian",
        "homeostasis",
    ]
    assert events[0]["details"]["authority"] == "observe_only"
    assert events[1]["details"]["view"] == "summary_only"
    assert events[2]["event_type"] == "health"
