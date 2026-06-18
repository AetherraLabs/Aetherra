from Aetherra.homeostasis.recommendation import build_recommendation_report


def test_recommendation_report_suggests_actions_without_execution():
    observation = {"risk": {"level": "critical", "score": 80}}
    diagnosis = {
        "phase": "diagnosis",
        "causes": [
            {
                "category": "memory_pressure",
                "severity": "high",
                "evidence": [{"metric": "memory_rtt", "value": 180.0}],
            },
            {
                "category": "agent_or_kernel_overload",
                "severity": "critical",
                "evidence": [{"metric": "queue_depth", "value": 120.0}],
            },
        ],
    }

    report = build_recommendation_report(observation, diagnosis)

    assert report["phase"] == "recommendation"
    assert report["actions_enabled"] is False
    assert report["execution"] == {
        "performed": False,
        "reason": "recommendation_phase_is_read_only",
    }
    assert report["summary"]["status"] == "recommendations_available"
    assert report["summary"]["requires_guardian_before_execution"] is True
    actions = [item["action_type"] for item in report["recommendations"]]
    assert actions == ["increase_task_workers", "optimize_memory_cache"]
    assert all(item["requires_guardian"] is True for item in report["recommendations"])


def test_recommendation_report_handles_no_causes():
    report = build_recommendation_report(
        observation={"risk": {"level": "nominal"}},
        diagnosis={"phase": "diagnosis", "causes": []},
    )

    assert report["summary"] == {
        "status": "no_recommendations",
        "recommendation_count": 0,
        "highest_priority": None,
        "requires_guardian_before_execution": False,
    }
    assert report["recommendations"] == []
