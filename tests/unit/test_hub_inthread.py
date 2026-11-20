# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import socket
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
import aetherra_hub.compat as hub_mod

requests = pytest.importorskip("requests")

FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


@pytest.fixture
def hub_factory(monkeypatch):
    created = []
    original_type = hub_mod.AetherraHubServer

    class Hub:
        def __init__(
            self, port, *, host=hub_mod._LEGACY_BIND_HOST, diagnostic_only=False
        ):
            self.port, self.host = port, host
            self.server_running = False
            self.stops = 0
            self.chat_metrics = {"requests_total": 0, "fallback_path_counts": {}}
            created.append(self)

        def start_server(self):
            self.server_running = True
            return True

        def is_running(self):
            return self.server_running

        def stop_server(self):
            self.stops += 1
            self.server_running = False

    monkeypatch.setattr(hub_mod, "_global_server", None)
    monkeypatch.setattr(hub_mod, "AetherraHubServer", Hub)
    monkeypatch.setattr(
        requests, "get", lambda *args, **kwargs: SimpleNamespace(status_code=200)
    )
    return SimpleNamespace(created=created, hub_type=Hub, original_type=original_type)


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost"])
def test_hub_factory_honors_explicit_host(hub_factory, host):
    server = hub_mod.start_hub_server(port=43210, host=host)
    assert server.host == host
    assert server.is_running()
    assert hub_mod._global_server is server


def test_hub_factory_omitted_host_keeps_historical_default(hub_factory):
    assert hub_mod.start_hub_server(port=43210).host == hub_mod._LEGACY_BIND_HOST


@pytest.mark.parametrize(
    ("initial", "requested"),
    [
        (hub_mod._LEGACY_BIND_HOST, "127.0.0.1"),
        ("127.0.0.1", hub_mod._LEGACY_BIND_HOST),
    ],
)
def test_hub_factory_replaces_conflicting_binding(hub_factory, initial, requested):
    old = hub_mod.start_hub_server(port=43210, host=initial)
    new = hub_mod.start_hub_server(port=43210, host=requested)
    assert new is not old
    assert old.stops == 1
    assert new.host == requested
    assert new.is_running()


def test_hub_factory_reuses_matching_live_binding(hub_factory):
    old = hub_mod.start_hub_server(port=43210, host="127.0.0.1")
    old.chat_metrics["requests_total"] = 7
    assert hub_mod.start_hub_server(port=43210, host="127.0.0.1") is old
    assert old.chat_metrics["requests_total"] == 7


def test_hub_factory_restarts_stopped_binding(hub_factory):
    old = hub_mod.start_hub_server(port=43210, host="127.0.0.1")
    old.stop_server()
    new = hub_mod.start_hub_server(port=43210, host="127.0.0.1")
    assert new.is_running()
    assert new.host == "127.0.0.1"


def test_hub_factory_does_not_publish_failed_start(hub_factory, monkeypatch):
    def fail(self):
        raise RuntimeError("controlled startup failure")

    monkeypatch.setattr(hub_factory.hub_type, "start_server", fail)
    with pytest.raises(RuntimeError, match="startup failure"):
        hub_mod.start_hub_server(port=43210, host="127.0.0.1")
    assert hub_mod._global_server is None


def test_hub_factory_retains_owner_when_teardown_fails(hub_factory, monkeypatch):
    old = hub_mod.start_hub_server(port=43210, host=hub_mod._LEGACY_BIND_HOST)

    def fail():
        raise RuntimeError("controlled shutdown failure")

    monkeypatch.setattr(old, "stop_server", fail)
    with pytest.raises(RuntimeError, match="shutdown"):
        hub_mod.start_hub_server(port=43210, host="127.0.0.1")
    assert hub_mod._global_server is old
    assert len(hub_factory.created) == 1


def test_hub_factory_omitted_host_does_not_widen_existing_binding(hub_factory):
    server = hub_mod.start_hub_server(port=43210, host="127.0.0.1")
    assert hub_mod.start_hub_server(port=43210) is server
    assert server.host == "127.0.0.1"


@pytest.mark.parametrize("host", ["", "   ", 7])
def test_hub_factory_rejects_invalid_explicit_hosts(hub_factory, host):
    with pytest.raises(ValueError, match="nonempty string"):
        hub_mod.start_hub_server(port=43210, host=host)
    assert hub_factory.created == []
    assert hub_mod._global_server is None


def test_loopback_rebinding_releases_socket_and_owned_thread(monkeypatch):
    from flask import Flask

    app = Flask("binding_test")
    app.add_url_rule("/api/ping", view_func=lambda: {"status": "ok"})
    monkeypatch.setattr(hub_mod, "create_app", lambda: app)
    monkeypatch.setattr(
        hub_mod._reg_client, "get_kernel_status", lambda: {"ready": True}
    )
    monkeypatch.setattr(
        hub_mod._reg_client, "get_orchestrator_status", lambda: {"ready": True}
    )
    monkeypatch.setattr(hub_mod, "_global_server", None)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    first = second = None
    try:
        first = hub_mod.start_hub_server(port=port, host="127.0.0.1")
        old_thread = first._thread
        old_socket = first._srv.socket
        assert old_socket.getsockname()[0] == "127.0.0.1"
        second = hub_mod.start_hub_server(port=port, host="localhost")
        assert second is not first
        assert old_socket.fileno() == -1
        assert not old_thread.is_alive()
        assert second._srv.socket.getsockname()[0] == "127.0.0.1"
        assert (
            requests.get(f"http://127.0.0.1:{port}/api/ping", timeout=2).status_code
            == 200
        )
    finally:
        for server in (second, first):
            if server is not None:
                server.stop_server()
    assert hub_mod._global_server._srv is None


def test_hub_thread_start_failure_closes_unstarted_listener(monkeypatch):
    from flask import Flask

    closed = []
    listener = SimpleNamespace(
        serve_forever=lambda: None, server_close=lambda: closed.append(True)
    )

    class UnstartedThread:
        ident = None

        def __init__(self, **kwargs):
            pass

        def start(self):
            raise RuntimeError("controlled thread startup failure")

    monkeypatch.setattr(hub_mod, "create_app", lambda: Flask("unstarted_test"))
    monkeypatch.setattr(hub_mod, "make_server", lambda *args: listener)
    monkeypatch.setattr(hub_mod.threading, "Thread", UnstartedThread)
    server = hub_mod.AetherraHubServer(host="127.0.0.1")
    with pytest.raises(RuntimeError, match="thread startup"):
        server.start_server()
    assert closed == [True]
    assert server._srv is None
    assert not server.is_running()


def test_socket_close_failure_does_not_reuse_dead_hub(hub_factory, monkeypatch):
    server = hub_factory.original_type(port=43210, host="127.0.0.1")
    closed = []

    def close():
        closed.append(True)
        if len(closed) == 1:
            raise RuntimeError("controlled socket close failure")

    server._srv = SimpleNamespace(shutdown=lambda: None, server_close=close)
    server._thread = SimpleNamespace(
        ident=1, join=lambda **kwargs: None, is_alive=lambda: False
    )
    server.server_running = True
    monkeypatch.setattr(hub_mod, "_global_server", server)
    with pytest.raises(RuntimeError, match="socket close"):
        server.stop_server()
    assert not server.is_running()
    assert server._srv is not None
    replacement = hub_mod.start_hub_server(port=43210, host="127.0.0.1")
    assert replacement is not server
    assert replacement.is_running()
    assert len(closed) == 2


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_hub_runs_in_thread_and_handles_federation_and_telemetry(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.delenv("AETHERRA_NET_STRICT", raising=False)
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    # Find a free port for the hub
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()

    server = hub_mod.AetherraHubServer(port)
    ok = server.start_server()
    assert ok and server.is_running()

    base = f"http://localhost:{port}"

    # Health
    r = requests.get(f"{base}/health", timeout=3)
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"

    # Telemetry ingest
    r = requests.post(f"{base}/api/telemetry", json={"event": "unit_ping"}, timeout=3)
    assert r.status_code == 200

    # Stats should reflect telemetry
    r = requests.get(f"{base}/api/stats", timeout=3)
    assert r.status_code == 200
    stats = r.json()
    assert stats.get("telemetry_received", 0) >= 1

    # Federation: add a peer and announce/sync
    r = requests.post(f"{base}/api/peers", json={"url": f"{base}"}, timeout=3)
    assert r.status_code == 200

    r = requests.post(f"{base}/api/peers/announce", timeout=3)
    assert r.status_code in (200, 501)  # 501 if federation disabled

    r = requests.post(f"{base}/api/peers/sync", timeout=5)
    assert r.status_code in (200, 501)

    # Plugins listing includes federated view when enabled
    r = requests.get(f"{base}/api/plugins", timeout=3)
    assert r.status_code == 200

    # Memory graph optics may be disabled
    r = requests.get(f"{base}/api/memory/graph", timeout=3)
    assert r.status_code in (200, 501)
