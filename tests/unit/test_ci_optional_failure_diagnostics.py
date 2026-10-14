"""Offline contracts for best-effort runtime failure diagnostics."""

# Standard library imports
import asyncio
import logging
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness import (
    metrics_exporter as metrics,
    workspace_core as workspace,
)
from Aetherra.consciousness.sensors import registry

PRIVATE = "private-payload secret-key C:/private/state"


def fail(*args, **kwargs):
    raise RuntimeError(PRIVATE)


def assert_diagnostic(caplog, operation, exception="RuntimeError"):
    records = [record for record in caplog.records if operation in record.getMessage()]
    assert len(records) == 1
    assert records[0].getMessage() == f"{operation} failed ({exception})"
    assert records[0].exc_info is None
    assert records[0].stack_info is None
    assert PRIVATE not in caplog.text
    assert "C:/private" not in caplog.text


@pytest.fixture(autouse=True)
def offline_runtime(monkeypatch, tmp_path, caplog):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_STREAM", "0")
    monkeypatch.setenv("AETHERRA_PROMETHEUS", "0")
    monkeypatch.setenv("AETHERRA_AFFECT_WEIGHT", "0")
    monkeypatch.setattr(workspace, "_metrics_init", None)
    monkeypatch.setattr(workspace, "_get_affect_engine", None)
    caplog.set_level(logging.DEBUG)


METRIC_CASES = [
    (
        "update_workspace_queue",
        "_workspace_queue_gauge",
        (7,),
        "Workspace queue gauge update",
    ),
    (
        "update_narrative_coherence",
        "_narrative_coherence_gauge",
        (0.4,),
        "Narrative coherence gauge update",
    ),
    (
        "update_identity_coherence",
        "_identity_coherence_gauge",
        (0.4,),
        "Identity coherence gauge update",
    ),
    (
        "increment_chapter_count",
        "_narrative_chapters_gauge",
        (),
        "Narrative chapter counter increment",
    ),
    (
        "inc_workspace_candidate",
        "_workspace_candidate_counter",
        (PRIVATE,),
        "Workspace candidate counter increment",
    ),
    (
        "inc_workspace_broadcast",
        "_workspace_broadcast_counter",
        (PRIVATE,),
        "Workspace broadcast counter increment",
    ),
    (
        "observe_workspace_latency",
        "_workspace_latency_hist",
        (-1.0,),
        "Workspace latency observation",
    ),
    (
        "observe_narrative_generation",
        "_narrative_generation_hist",
        (-1.0,),
        "Narrative generation observation",
    ),
]


@pytest.mark.parametrize(("function", "attribute", "args", "operation"), METRIC_CASES)
def test_metric_failure_is_sanitized(
    monkeypatch, caplog, function, attribute, args, operation
):
    broken = SimpleNamespace(set=fail, inc=fail, labels=fail, observe=fail)
    monkeypatch.setattr(metrics, attribute, broken)
    assert getattr(metrics, function)(*args) is None
    assert_diagnostic(caplog, operation)


@pytest.mark.parametrize(("function", "attribute", "args", "operation"), METRIC_CASES)
def test_absent_metric_remains_quiet(
    monkeypatch, caplog, function, attribute, args, operation
):
    monkeypatch.setattr(metrics, attribute, None)
    assert getattr(metrics, function)(*args) is None
    assert not caplog.records


@pytest.mark.parametrize("server_fails", [True, False])
def test_exporter_initialization_fallback(monkeypatch, caplog, server_fails):
    monkeypatch.setenv("AETHERRA_PROMETHEUS", "1")
    monkeypatch.setattr(metrics, "_started", False)
    for name in (
        "_workspace_queue_gauge",
        "_narrative_coherence_gauge",
        "_narrative_chapters_gauge",
        "_workspace_candidate_counter",
        "_workspace_broadcast_counter",
        "_workspace_latency_hist",
        "_narrative_generation_hist",
    ):
        monkeypatch.setattr(metrics, name, None)
    monkeypatch.setattr(metrics, "Gauge", lambda *args, **kwargs: object())
    monkeypatch.setattr(metrics, "Counter", fail)
    monkeypatch.setattr(metrics, "Histogram", lambda *args, **kwargs: object())
    monkeypatch.setattr(
        metrics, "start_http_server", fail if server_fails else lambda port: None
    )
    assert metrics.initialize_exporter() is (not server_fails)
    assert metrics._started is (not server_fails)
    assert_diagnostic(
        caplog,
        (
            "Metrics listener startup"
            if server_fails
            else "Workspace counter and histogram registration"
        ),
    )


@pytest.mark.parametrize(
    ("attribute", "operation"),
    [
        ("_metrics_update_q", "Workspace enqueue queue metric update"),
        ("_metrics_inc_candidate", "Workspace enqueue candidate metric increment"),
    ],
)
def test_enqueue_survives_metric_failure(monkeypatch, caplog, attribute, operation):
    monkeypatch.setattr(workspace, attribute, fail)
    ws = workspace.WorkspaceCore()
    assert ws.add_candidate({"private": PRIVATE}, priority=5, source=PRIVATE)
    assert ws.queue_size() == 1
    assert_diagnostic(caplog, operation)


def test_affect_failure_preserves_weight_floor(monkeypatch, caplog):
    monkeypatch.setenv("AETHERRA_AFFECT_WEIGHT", "1")
    monkeypatch.setattr(workspace, "_get_affect_engine", fail)
    ws = workspace.WorkspaceCore()
    assert ws._compute_sort_key(2, 0.0) == -20000.0
    assert_diagnostic(caplog, "Workspace affect weight calculation")


def test_workspace_initialization_survives_optional_failures(monkeypatch, caplog):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_STREAM", "1")
    monkeypatch.setattr(workspace.os, "makedirs", fail)
    monkeypatch.setattr(workspace, "_metrics_init", fail)
    ws = workspace.WorkspaceCore()
    assert ws.enabled()
    assert_diagnostic(caplog, "Workspace stream directory creation")
    assert_diagnostic(caplog, "Workspace metrics initialization")


@pytest.mark.parametrize(
    ("failure_site", "operation"),
    [
        ("subscriber", "Workspace subscriber delivery"),
        ("metric", "Workspace broadcast metric increment"),
        ("write", "Workspace stream append"),
        ("hook", "Workspace stream hook delivery"),
    ],
)
def test_broadcast_failure_keeps_delivery(
    monkeypatch, tmp_path, caplog, failure_site, operation
):
    ws = workspace.WorkspaceCore()
    received = []
    if failure_site == "subscriber":
        ws.subscribe(fail)
    ws.subscribe(received.append)
    if failure_site == "metric":
        monkeypatch.setattr(workspace, "_metrics_inc_broadcast", fail)
    if failure_site in ("write", "hook"):
        ws._stream_enabled = True
        ws._stream_path = str(tmp_path / "stream.log")
        if failure_site == "write":
            monkeypatch.setattr(workspace, "open", fail, raising=False)
        else:
            ws.set_stream_hook(fail)
    candidate = workspace.WorkspaceCandidate(
        0.0, 0, payload={"private": PRIVATE}, source=PRIVATE
    )
    asyncio.run(ws._broadcast(candidate))
    assert received == [candidate.payload]
    assert ws._broadcast_count_window == 1
    assert_diagnostic(caplog, operation)


@pytest.mark.parametrize(
    ("site", "operation"),
    [
        ("queue", "Workspace dequeue queue metric update"),
        ("latency", "Workspace latency metric observation"),
        ("loop", "Workspace selection iteration"),
    ],
)
def test_selection_loop_survives_optional_failure(monkeypatch, caplog, site, operation):
    ws = workspace.WorkspaceCore()
    assert ws.add_candidate({"private": PRIVATE})
    received = []
    ws.subscribe(received.append)
    if site == "queue":
        monkeypatch.setattr(workspace, "_metrics_update_q", fail)
    elif site == "latency":
        monkeypatch.setattr(workspace, "_metrics_obs_latency", fail)
    else:
        monkeypatch.setattr(ws, "_reset_window_if_needed", fail)

    async def one_iteration():
        nonlocal ticks
        ticks += 1
        if ticks > 1:
            raise asyncio.CancelledError

    ticks = 0
    monkeypatch.setattr(workspace.asyncio, "sleep", lambda seconds: one_iteration())
    ws._running = True
    asyncio.run(ws._loop())
    assert received == ([] if site == "loop" else [{"private": PRIVATE}])
    assert_diagnostic(caplog, operation)


def test_stop_cleans_up_cancelled_task(caplog):
    async def run():
        ws = workspace.WorkspaceCore()
        await ws.start()
        await ws.stop()
        assert ws._task is None
        assert not ws._running

    asyncio.run(run())
    records = [record for record in caplog.records if record.name == workspace.__name__]
    assert len(records) == 1
    assert records[0].levelno == logging.DEBUG
    assert (
        records[0].getMessage()
        == "Workspace task cancellation acknowledged (CancelledError)"
    )
    assert records[0].exc_info is None


def test_sensor_shutdown_continues_after_failure(monkeypatch, caplog):
    stopped = []
    monkeypatch.setattr(
        registry,
        "_DEFAULT_SENSORS",
        [
            SimpleNamespace(stop=fail),
            SimpleNamespace(stop=lambda: stopped.append(True)),
        ],
    )
    registry.stop_all_sensors()
    assert stopped == [True]
    assert registry._DEFAULT_SENSORS == []
    assert_diagnostic(caplog, "Default sensor shutdown")


@pytest.mark.parametrize(
    "exception", [KeyboardInterrupt, SystemExit, asyncio.CancelledError]
)
def test_metric_does_not_swallow_process_control(monkeypatch, exception):
    def interrupt(value):
        raise exception

    monkeypatch.setattr(
        metrics, "_workspace_queue_gauge", SimpleNamespace(set=interrupt)
    )
    with pytest.raises(exception):
        metrics.update_workspace_queue(1)


def test_latency_clamp_and_counter_source_are_unchanged(monkeypatch):
    observed = []
    sources = []
    counter = SimpleNamespace(inc=lambda: None)
    monkeypatch.setattr(
        metrics, "_workspace_latency_hist", SimpleNamespace(observe=observed.append)
    )
    monkeypatch.setattr(
        metrics,
        "_workspace_candidate_counter",
        SimpleNamespace(labels=lambda **kwargs: sources.append(kwargs) or counter),
    )
    metrics.observe_workspace_latency(-0.5)
    metrics.observe_workspace_latency(0.125)
    metrics.inc_workspace_candidate("")
    assert observed == [0.0, 0.125]
    assert sources == [{"source": "unknown"}]
