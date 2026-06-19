from Aetherra.homeostasis.diagnosis import build_diagnosis_report


def test_diagnosis_identifies_bounded_causes_from_observation():
    observation = {
        "phase": "observation",
        "actions_enabled": False,
        "state": {
            "pending_actions": 3,
            "emergency_stop": False,
        },
        "pressure": {
            "metrics": {
                "memory_rtt": {
                    "level": "high",
                    "direction": "above_maximum",
                    "value": 180.0,
                    "target": 50.0,
                },
                "queue_depth": {
                    "level": "critical",
                    "direction": "above_critical",
                    "value": 120.0,
                    "target": 5.0,
                },
                "hub_connection": {
                    "level": "high",
                    "direction": "below_target",
                    "value": 0.0,
                    "target": 1.0,
                },
            }
        },
        "risk": {"factors": []},
    }

    diagnosis = build_diagnosis_report(observation)

    assert diagnosis["phase"] == "diagnosis"
    assert diagnosis["actions_enabled"] is False
    assert diagnosis["summary"]["status"] == "causes_identified"
    assert diagnosis["summary"]["primary_cause"] == "agent_or_kernel_overload"
    categories = {cause["category"] for cause in diagnosis["causes"]}
    assert "memory_pressure" in categories
    assert "agent_or_kernel_overload" in categories
    assert "service_degradation" in categories
    assert "controller_backlog" in categories


def test_diagnosis_reports_no_clear_cause_for_nominal_observation():
    diagnosis = build_diagnosis_report(
        {
            "phase": "observation",
            "pressure": {"metrics": {}},
            "state": {"pending_actions": 0, "emergency_stop": False},
            "risk": {"factors": []},
        }
    )

    assert diagnosis["summary"] == {
        "status": "no_clear_cause",
        "primary_cause": None,
        "cause_count": 0,
        "highest_severity": "nominal",
    }
