# SPDX-License-Identifier: GPL-3.0-or-later
# Security metrics Phase 0 tests: ensure auth + HMR counters exported.

import re

import pytest

from aetherra_hub.compat import start_hub_server

requests = pytest.importorskip("requests")


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

    port = 39401
    start_hub_server(port=port)

    # Now simulate disabled path (unset stream flag) to exercise missing token counter logic
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "0")
    r = requests.post(f"http://localhost:{port}/api/ai/stream", json={"message": "hi"})
    assert r.status_code == 501

    body = _get_metrics(port)
    # Counter should be >=1
    m = re.search(r"aetherra_chat_auth_missing_token_total (\d+)", body)
    assert m, "missing token metric not exported"
    val = int(m.group(1))
    assert val >= 1


def test_security_metric_series_always_present(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    port = 39402
    start_hub_server(port=port)
    body = _get_metrics(port)
    for name in [
        "aetherra_chat_auth_missing_token_total",
        "aetherra_chat_auth_invalid_token_total",
        "aetherra_hmr_denied_total",
    ]:
        assert name in body, f"{name} not exported"
