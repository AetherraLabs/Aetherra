from Aetherra.homeostasis.learning import build_learning_report


def test_learning_report_correlates_homeostasis_decisions_and_outcomes():
    records = [
        {
            "hash": "decision-1",
            "timestamp": "2026-01-01T00:00:00Z",
            "event_type": "guardian_decision",
            "details": {
                "intent": {
                    "subsystem": "homeostasis",
                    "action": "homeostasis.actuate",
                    "target": "kernel_system:increase_task_workers",
                    "metadata": {
                        "action_type": "increase_task_workers",
                        "target_service": "kernel_system",
                    },
                },
                "decision": {"status": "allow_limited"},
            },
        },
        {
            "hash": "outcome-1",
            "event_type": "guardian_outcome",
            "details": {
                "decision_audit_id": "decision-1",
                "outcome": {"status": "completed", "affected_count": 1},
            },
        },
        {
            "hash": "decision-2",
            "event_type": "guardian_decision",
            "details": {
                "intent": {
                    "subsystem": "security",
                    "action": "security.policy_update",
                },
                "decision": {"status": "deny"},
            },
        },
    ]

    report = build_learning_report(records)

    assert report["phase"] == "learning"
    assert report["actions_enabled"] is False
    assert report["summary"] == {
        "decision_count": 1,
        "outcome_count": 1,
        "completed": 1,
        "failed": 0,
        "success_rate": 1.0,
    }
    assert report["action_effectiveness"]["increase_task_workers"]["completed"] == 1
    assert report["correlations"][0]["latest_outcome_status"] == "completed"


def test_learning_report_handles_no_outcomes():
    report = build_learning_report([])

    assert report["summary"] == {
        "decision_count": 0,
        "outcome_count": 0,
        "completed": 0,
        "failed": 0,
        "success_rate": None,
    }
    assert report["action_effectiveness"] == {}
    assert report["correlations"] == []
