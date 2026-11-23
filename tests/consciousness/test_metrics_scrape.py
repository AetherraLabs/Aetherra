# Standard library imports
import os
import urllib.request

# Third party imports
import pytest


@pytest.mark.skipif(
    os.getenv("SKIP_PROM_TESTS") == "1", reason="Prometheus tests skipped by env"
)
def test_metrics_scrape_endpoint(metrics_listener):
    exporter, listeners = metrics_listener
    assert exporter.initialize_exporter()
    exporter.update_workspace_queue(3)
    server, _ = listeners[0]
    with urllib.request.urlopen(
        f"http://127.0.0.1:{server.server_port}/metrics", timeout=2
    ) as response:  # nosec B310
        body = response.read().decode("utf-8")
    assert "aetherra_consciousness_workspace_queue_size 3.0" in body
