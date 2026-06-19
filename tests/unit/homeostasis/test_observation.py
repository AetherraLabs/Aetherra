import time

from Aetherra.homeostasis.observation import build_observation_report
from Aetherra.homeostasis.stability_metrics import MetricSnapshot


def _setpoints():
    return {
        "core_metrics": {
            "memory_rtt": {
                "target": 50.0,
                "max_acceptable": 120.0,
                "critical_threshold": 500.0,
                "control_band": 20.0,
            },
            "plugin_load_success": {
                "target": 95.0,
                "min_acceptable": 85.0,
                "critical_threshold": 70.0,
                "control_band": 5.0,
            },
            "queue_depth": {
                "target": 5.0,
                "max_acceptable": 50.0,
                "critical_threshold": 100.0,
                "control_band": 10.0,
            },
        }
    }


def test_observation_report_is_read_only_awareness_snapshot():
    collected_at = time.time()
    snapshot = MetricSnapshot(
        timestamp=collected_at - 2.0,
        memory_rtt=55.0,
        plugin_load_success=96.0,
        queue_depth=4.0,
    )

    report = build_observation_report(
        metrics_snapshot=snapshot,
        health_summary={"status": "healthy", "health_score": 98.0},
        controller_status={
            "mode": "observe_only",
            "running": True,
            "pending_actions": 0,
            "confirmation_pending": 0,
        },
        actuator_status={"actions_executed": 0},
        setpoints=_setpoints(),
        collected_at=collected_at,
    )

    assert report["phase"] == "observation"
    assert report["actions_enabled"] is False
    assert report["state"]["controller_mode"] == "observe_only"
    assert report["state"]["pending_actions"] == 0
    assert report["metrics"]["values"]["memory_rtt"] == 55.0
    assert report["metrics"]["sample_age_seconds"] == 2.0
    assert report["pressure"]["level"] == "nominal"
    assert report["risk"] == {"level": "nominal", "score": 0, "factors": []}


def test_observation_report_surfaces_pressure_and_risk_without_actions():
    snapshot = MetricSnapshot(
        timestamp=time.time(),
        memory_rtt=180.0,
        plugin_load_success=60.0,
        queue_depth=120.0,
    )

    report = build_observation_report(
        metrics_snapshot=snapshot,
        health_summary={"status": "degraded"},
        controller_status={"mode": "advisory", "pending_actions": 2},
        supervisor_status={"runlevel": "DEGRADED"},
        setpoints=_setpoints(),
    )

    assert report["actions_enabled"] is False
    assert report["pressure"]["metrics"]["memory_rtt"]["level"] == "high"
    assert report["pressure"]["metrics"]["plugin_load_success"]["level"] == "critical"
    assert report["pressure"]["metrics"]["queue_depth"]["level"] == "critical"
    assert report["risk"]["level"] == "critical"
    assert "critical_metric_pressure" in report["risk"]["factors"]
    assert "pending_homeostasis_actions" in report["risk"]["factors"]
