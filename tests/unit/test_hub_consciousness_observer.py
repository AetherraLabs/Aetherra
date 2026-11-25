"""Owned Consciousness snapshots take precedence over stale legacy push state."""

# Standard library imports
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import aetherra_service_registry as registry_module
from aetherra_hub.blueprints.consciousness import bp
from aetherra_hub.services.state import hub_state
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)


@pytest.fixture
def setup(monkeypatch):
    registry = AetherraServiceRegistry()
    registry._running = True
    monkeypatch.setattr(registry_module, "_service_registry", registry)
    monkeypatch.setattr(
        hub_state,
        "consciousness_state",
        {"tick_id": 999, "recent_narrative": ["stale legacy"]},
    )
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "test-control-token")
    app = Flask(__name__)
    app.register_blueprint(bp)
    return registry, app.test_client()


def _register(registry, **overrides):
    status = {
        "runtime_state": "running",
        "running": True,
        "thread_alive": True,
        "ticks_attempted": 4,
        "ticks_completed": 4,
        "last_tick_at": time.time(),
        "last_tick_age_seconds": 0.0,
        "tick_interval_seconds": 0.2,
        "events_processed": 7,
        "autonomy_mode": "observe",
        "persistence_enabled": False,
        "qfac_persistence_enabled": False,
        "action_execution_enabled": False,
        "think_stream_available": True,
        "last_error_code": "private internal error",
        **overrides,
    }
    snapshot = {
        "tick_id": 4,
        "events_processed": 7,
        "qualia": {"valence": 0.2},
        "focuses": [],
        "intentions": [],
        "recent_narrative": [{"summary": "A measured runtime observation"}],
        "runtime": status,
        "private_path": "private/path",
        "status": "running",
    }
    instance = SimpleNamespace(
        get_runtime_status=lambda: status, get_think_stream=lambda: snapshot
    )
    registry._services["consciousness_core"] = ServiceInfo(
        name="consciousness_core",
        instance=instance,
        status=ServiceStatus.HEALTHY,
        last_heartbeat=datetime.now(),
        metadata={"phase": "phase_c1_observer"},
    )
    return instance


def test_state_uses_owned_genuine_snapshot_not_legacy_cache(setup):
    registry, client = setup
    _register(registry)
    response = client.get("/api/consciousness/state")
    assert response.status_code == 200
    body = response.get_json()
    assert body["tick_id"] == 4
    assert body["events_processed"] == 7
    assert body["status"] == "running"
    assert body["runtime"]["ticks_completed"] == 4
    assert body["recent_narrative"] == [{"summary": "A measured runtime observation"}]
    assert "private" not in str(body)
    assert "stale legacy" not in str(body)


@pytest.mark.parametrize(
    "change",
    [
        {"runtime_state": "blocked"},
        {"runtime_state": "failed"},
        {"runtime_state": "starting"},
        {"runtime_state": "stopped"},
        {"runtime_state": "stopping"},
        {"running": False},
        {"thread_alive": False},
        {"ticks_completed": 0},
        {"last_tick_at": time.time() - 30},
        {"last_tick_at": time.time() + 30},
        {"last_tick_at": float("nan")},
        {"autonomy_mode": "auto"},
        {"action_execution_enabled": True},
        {"think_stream_available": False},
    ],
)
def test_unavailable_owned_observer_never_falls_back_to_legacy_state(setup, change):
    registry, client = setup
    instance = _register(registry, **change)

    def forbidden():
        raise AssertionError("unavailable state must not read cached ThinkStream")

    instance.get_think_stream = forbidden
    response = client.get("/api/consciousness/state")
    assert response.status_code == 503
    assert "stale legacy" not in str(response.get_json())
    assert "private" not in str(response.get_json())


def test_owned_status_failure_is_bounded_and_not_legacy_fallback(setup):
    registry, client = setup
    instance = _register(registry)

    def unavailable():
        raise RuntimeError("private path and details")

    instance.get_runtime_status = unavailable
    response = client.get("/api/consciousness/state")
    assert response.status_code == 503
    assert "private" not in str(response.get_json())
    assert "stale legacy" not in str(response.get_json())


def test_owned_missing_snapshot_is_unavailable(setup):
    registry, client = setup
    instance = _register(registry)
    instance.get_think_stream = lambda: None
    assert client.get("/api/consciousness/state").status_code == 503


def test_legacy_control_updates_remain_authorized_when_no_observer(setup):
    _, client = setup
    assert (
        client.post("/api/consciousness/update", json={"tick_id": 17}).status_code
        == 401
    )
    response = client.post(
        "/api/consciousness/update",
        json={"tick_id": 17},
        headers={"X-Aetherra-Control-Token": "test-control-token"},
    )
    assert response.status_code == 200
    assert client.get("/api/consciousness/state").get_json()["tick_id"] == 17


def test_get_does_not_create_an_observer_or_registry(setup, monkeypatch):
    _, client = setup
    monkeypatch.setattr(registry_module, "_service_registry", None)
    monkeypatch.setattr(hub_state, "consciousness_state", {})

    def forbidden():
        raise AssertionError("GET must not start any service")

    monkeypatch.setattr(registry_module, "get_service_registry", forbidden)
    assert client.get("/api/consciousness/state").status_code == 503
    assert registry_module._service_registry is None


def test_stale_owned_status_is_not_labelled_running(setup):
    registry, client = setup
    _register(registry, last_tick_at=time.time() - 30)
    response = client.get("/api/consciousness/state")
    assert response.status_code == 503
    assert response.get_json()["status"] != "running"


def test_stopped_registry_cannot_expose_owned_observer_as_live(setup):
    registry, client = setup
    _register(registry)
    registry._running = False
    assert client.get("/api/consciousness/state").status_code == 503


def test_observer_stopping_during_snapshot_read_is_unavailable(setup):
    registry, client = setup
    instance = _register(registry)
    original = instance.get_think_stream

    def stop_during_read():
        result = original()
        instance.get_runtime_status()["runtime_state"] = "stopped"
        return result

    instance.get_think_stream = stop_during_read
    response = client.get("/api/consciousness/state")
    assert response.status_code == 503
    assert "recent_narrative" not in response.get_json()


def test_legacy_push_cannot_replace_owned_snapshot(setup):
    registry, client = setup
    _register(registry)
    response = client.post(
        "/api/consciousness/update",
        json={"tick_id": 1234},
        headers={"X-Aetherra-Control-Token": "test-control-token"},
    )
    assert response.status_code == 200
    assert client.get("/api/consciousness/state").get_json()["tick_id"] == 4


def test_slow_owned_status_read_is_bounded_and_preserves_legacy_cache(setup):
    # Standard library imports
    from threading import Event

    registry, client = setup
    instance = _register(registry)
    release = Event()

    def wait():
        release.wait(5)
        return {}

    instance.get_runtime_status = wait
    started = time.monotonic()
    try:
        response = client.get("/api/consciousness/state")
        assert response.status_code == 503
        assert time.monotonic() - started < 2
        assert hub_state.get_consciousness()["tick_id"] == 999
    finally:
        release.set()


@pytest.mark.parametrize("legacy_rate", ["invalid-rate", "0", "NaN"])
def test_disabled_observer_bad_legacy_hz_does_not_break_hub_boot(tmp_path, legacy_rate):
    """A fresh real app must not parse optional core settings while disabled."""
    repo = Path(__file__).resolve().parents[2]
    env = {
        name: value
        for name, value in os.environ.items()
        if not name.upper().startswith(
            ("AETH", "LYRIXA", "PYTHON", "OPENAI", "ANTHROPIC")
        )
        and not any(
            part in name.upper()
            for part in ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
        )
    }
    env.update(
        AETHERRA_CONSCIOUSNESS_ENABLED="0",
        AETHERRA_CONSCIOUSNESS_HZ=legacy_rate,
        AETHERRA_SKIP_DOTENV="1",
        AETHERRA_PROFILE="test",
        TEMP=str(tmp_path),
        TMP=str(tmp_path),
    )
    script = """
import sys
sys.path.insert(0, sys.argv[1])
from aetherra_hub.app import create_app
app = create_app()
assert "Aetherra.consciousness.core.config" not in sys.modules
client = app.test_client()
assert client.get("/health").status_code == 200
response = client.get("/api/consciousness/state")
assert response.status_code == 503
assert response.get_json()["status"] == "offline"
assert "Aetherra.consciousness.core.config" not in sys.modules
print("disabled observer: real Hub boot and offline state passed")
"""
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", script, str(repo)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-4000:]
    assert "real Hub boot and offline state passed" in result.stdout


def test_checkpoint_status_survives_offline_observer_without_payload(setup):
    registry, client = setup
    _register(
        registry,
        runtime_state="stopped",
        running=False,
        thread_alive=False,
        persistence_enabled=True,
        legacy_file_persistence_enabled=False,
        continuity={
            "enabled": True,
            "state": "saved",
            "selected_checkpoint_id": None,
            "restored_record_id": None,
            "saved_checkpoint_id": "a" * 32,
            "saved_record_id": "row-saved",
            "outstanding": False,
            "last_error_code": None,
            "payload": {"private": "secret"},
        },
    )
    for _ in range(3):
        response = client.get("/api/consciousness/state")
        assert response.status_code == 503
        body = response.get_json()
        assert body["runtime"]["continuity_saved_record_id"] == "row-saved"
        assert body["runtime"]["continuity_state"] == "saved"
        assert "private" not in str(body)
        assert "payload" not in str(body)
