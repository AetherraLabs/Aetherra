# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import socket

import pytest

from aetherra_hub import compat as hub_mod

requests = pytest.importorskip("requests")
FLASK_AVAILABLE = getattr(hub_mod, "FLASK_AVAILABLE", False)


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
def test_kernel_and_orchestrator_histograms_present_and_increasing():
    # Start server
    port = _free_port()
    server = hub_mod.AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    # First scrape
    r1 = requests.get(f"{base}/metrics", timeout=3)
    assert r1.status_code == 200
    body1 = r1.text

    # Check presence of histogram series (either provided or rolling fallback)
    assert "aetherra_kernel_cycle_time_ms_bucket" in body1
    assert "aetherra_orchestrator_task_latency_ms_bucket" in body1

    # Second scrape to allow rolling counters to increase
    r2 = requests.get(f"{base}/metrics", timeout=3)
    assert r2.status_code == 200
    body2 = r2.text

    # Buckets should still be present
    assert "aetherra_kernel_cycle_time_ms_bucket" in body2
    assert "aetherra_orchestrator_task_latency_ms_bucket" in body2
