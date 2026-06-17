# SPDX-License-Identifier: GPL-3.0-or-later
# Security metrics Phase 0 tests: ensure auth + HMR counters exported.

# Standard library imports
import re
import socket

# Third party imports
import pytest

# Aetherra imports
from aetherra_hub.compat import start_hub_server

requests = pytest.importorskip("requests")


def _free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get_metrics(port: int) -> str:
    r = requests.get(f"http://localhost:{port}/metrics", timeout=5)
    assert r.status_code == 200
    return r.text


def test_missing_token_increments_metric(monkeypatch):
    # Force prod profile, enable AI API + stream + require token but omit token
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    # Bypass hard fail to allow metric path verification (guard already verified elsewhere)
    monkeypatch.setenv("AETHERRA_PROD_UNSAFE_ALLOW", "1")
    # Ensure no token vars
    for k in ("AETHERRA_AI_API_TOKEN", "AETHERRA_HUB_CONTROL_TOKEN"):
        monkeypatch.delenv(k, raising=False)

    port = _free_tcp_port()
    server = start_hub_server(port=port)
    try:
        # Now simulate disabled path (unset stream flag) to exercise missing token counter logic
        monkeypatch.setenv("AETHERRA_AI_API_STREAM", "0")
        r = requests.post(
            f"http://localhost:{port}/api/ai/stream", json={"message": "hi"}
        )
        assert r.status_code == 501

        body = _get_metrics(port)
        # Counter should be >=1
        m = re.search(r"aetherra_chat_auth_missing_token_total (\d+)", body)
        assert m, "missing token metric not exported"
        val = int(m.group(1))
        assert val >= 1
    finally:
        server.stop_server()


def test_security_metric_series_always_present(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    port = _free_tcp_port()
    server = start_hub_server(port=port)
    try:
        body = _get_metrics(port)
        for name in [
            "aetherra_chat_auth_missing_token_total",
            "aetherra_chat_auth_invalid_token_total",
            "aetherra_hmr_denied_total",
        ]:
            assert name in body, f"{name} not exported"
    finally:
        server.stop_server()
