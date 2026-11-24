"""Scheduling readiness requires current Kernel evidence, not inferred artifacts."""

# Standard library imports
import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.os_kernel.readiness import assess_kernel_readiness
from aetherra_hub.services import registry_client


def live_status():
    return {
        "running": True,
        "paused": False,
        "queue_sizes": {"normal_priority": 0},
        "queue_limits": {"normal_priority": 10},
        "metrics": {},
        "backpressure_guard_pass": True,
        "night_schedule_guard_pass": True,
        "plugin_cb_open": False,
        "dlq_count": 0,
        "hmr": {},
        "inflight": {},
    }


@pytest.fixture
def no_local_kernel(monkeypatch, tmp_path):
    # Keep the actual sync/async bridge, while controlling only service discovery.
    async def registry():
        return SimpleNamespace(get_service_info=lambda name: None)

    monkeypatch.setattr(registry_client, "_get_registry_async", registry)
    monkeypatch.setattr("aetherra_registry_client.http_get_status", lambda: None)
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize(
    ("heartbeat", "state", "recent"),
    [
        (999.0, "healthy", True),
        (820.0, "healthy", True),
        (819.0, "healthy", False),
        (1001.0, "healthy", False),
        (None, "healthy", False),
        (float("nan"), "healthy", False),
        (float("inf"), "healthy", False),
        (999.0, "starting", False),
        (999.0, "failed", False),
        (999.0, "stopping", False),
    ],
)
def test_daemon_heartbeat_is_diagnostic_not_scheduling_evidence(
    no_local_kernel, monkeypatch, heartbeat, state, recent
):
    monkeypatch.setattr(registry_client.time, "time", lambda: 1000.0)
    monkeypatch.setattr(
        "aetherra_registry_client.http_get_status",
        lambda: {
            "services": {"kernel_loop": {"last_heartbeat": heartbeat, "status": state}}
        },
    )
    status = registry_client.get_kernel_status()
    assert status["running"] is recent
    assert status["_source"] == "registry_daemon"
    assert status["backpressure_guard_pass"] is None
    assert status["night_schedule_guard_pass"] is None
    report = assess_kernel_readiness(status)
    assert report["readiness"] != "ready"
    assert report["safe_to_schedule"] is False
    assert "kernel_status_inferred" in report["reasons"]
    json.dumps(status, allow_nan=False)


@pytest.mark.parametrize(
    ("timestamp_key", "offset", "recent"),
    [
        ("live_time", -10, True),
        ("live_time", -181, False),
        ("live_time", 10, False),
        ("shutdown_time", -10, False),
    ],
)
def test_metrics_artifact_cannot_restore_live_kernel_readiness(
    no_local_kernel, timestamp_key, offset, recent
):
    (no_local_kernel / "aetherra_kernel_metrics.json").write_text(
        json.dumps(
            {
                timestamp_key: (
                    datetime.now(UTC) + timedelta(seconds=offset)
                ).isoformat(),
                "cycle_count": 7,
            }
        ),
        encoding="utf-8",
    )
    status = registry_client.get_kernel_status()
    assert status["running"] is recent
    assert status["cycle_count"] == 7  # retained diagnostic value
    assert status["_source"] == "file_fallback"
    assert status["backpressure_guard_pass"] is None
    report = assess_kernel_readiness(status)
    assert report["safe_to_schedule"] is False
    assert "kernel_status_inferred" in report["reasons"]


@pytest.mark.parametrize(
    "source", ["registry_daemon", "file_fallback", "unknown_source"]
)
def test_non_live_provenance_cannot_borrow_a_complete_live_contract(source):
    report = assess_kernel_readiness({**live_status(), "_source": source})
    assert report["readiness"] != "ready"
    assert report["safe_to_schedule"] is False
    assert "kernel_status_inferred" in report["reasons"]


@pytest.mark.parametrize(
    "guard", ["backpressure_guard_pass", "night_schedule_guard_pass"]
)
@pytest.mark.parametrize("unknown", [None, "true", 1])
def test_unobserved_live_guard_does_not_count_as_passing(guard, unknown):
    report = assess_kernel_readiness({**live_status(), guard: unknown})
    assert report["readiness"] == "blocked"
    assert report["safe_to_schedule"] is False


def test_registered_live_kernel_keeps_existing_ready_contract(monkeypatch):
    observed = live_status()

    async def registry():
        return SimpleNamespace(
            get_service_info=lambda name: SimpleNamespace(
                instance=SimpleNamespace(get_status=lambda: observed)
            )
        )

    monkeypatch.setattr(registry_client, "_get_registry_async", registry)
    status = registry_client.get_kernel_status()
    assert status is observed
    report = assess_kernel_readiness(status)
    assert report["readiness"] == "ready"
    assert report["safe_to_schedule"] is True
