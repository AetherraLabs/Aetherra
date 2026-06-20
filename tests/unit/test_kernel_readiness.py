from Aetherra.aetherra_core.os_kernel import assess_kernel_readiness


def _base_status(**overrides):
    status = {
        "running": True,
        "paused": False,
        "uptime": 12.0,
        "cycle_count": 3,
        "plugin_invoke_timeout_sec": 20.0,
        "backpressure_guard_pass": True,
        "backpressure_guard_violations": [],
        "night_schedule_guard_pass": True,
        "metrics": {"errors_count": 0},
        "queue_sizes": {
            "high_priority": 0,
            "normal_priority": 2,
            "background": 4,
        },
        "queue_limits": {
            "high_priority": 10,
            "normal_priority": 10,
            "background": 20,
        },
        "plugin_cb_open": False,
        "dlq_count": 0,
        "hmr": {"attempts": 0, "success": 0, "rollback": 0},
        "inflight": {"engine": 0},
    }
    status.update(overrides)
    return status


def test_kernel_readiness_ready_when_guards_and_queues_are_healthy():
    payload = assess_kernel_readiness(_base_status())

    assert payload["readiness"] == "ready"
    assert payload["safe_to_schedule"] is True
    assert payload["reasons"] == ["ready"]
    assert payload["checks"]["status_contract_complete"] is True


def test_kernel_readiness_blocks_incomplete_status_contract():
    payload = assess_kernel_readiness({"running": True})

    assert payload["readiness"] == "blocked"
    assert payload["safe_to_schedule"] is False
    assert "status_contract_incomplete" in payload["reasons"]


def test_kernel_readiness_degrades_when_paused_or_circuit_open():
    payload = assess_kernel_readiness(
        _base_status(paused=True, plugin_cb_open=True)
    )

    assert payload["readiness"] == "degraded"
    assert payload["safe_to_schedule"] is False
    assert "kernel_paused" in payload["reasons"]
    assert "plugin_circuit_breaker_open" in payload["reasons"]


def test_kernel_readiness_blocks_failed_safety_guards():
    payload = assess_kernel_readiness(
        _base_status(
            backpressure_guard_pass=False,
            night_schedule_guard_pass=False,
        )
    )

    assert payload["readiness"] == "blocked"
    assert payload["safe_to_schedule"] is False
    assert "backpressure_guard_failed" in payload["reasons"]
    assert "night_schedule_guard_failed" in payload["reasons"]


def test_kernel_readiness_reports_queue_pressure():
    payload = assess_kernel_readiness(
        _base_status(
            queue_sizes={"normal_priority": 9},
            queue_limits={"normal_priority": 10},
        )
    )

    assert payload["readiness"] == "degraded"
    assert payload["checks"]["queue_pressure"]["normal_priority"]["ratio"] == 0.9
    assert "queue_near_limit:normal_priority" in payload["reasons"]
