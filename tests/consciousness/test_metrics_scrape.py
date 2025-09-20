# Standard library imports
import os
import time
import urllib.request

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.metrics_exporter import (
    initialize_exporter,
    update_workspace_queue,
)


@pytest.mark.skipif(
    os.getenv("SKIP_PROM_TESTS") == "1", reason="Prometheus tests skipped by env"
)
def test_metrics_scrape_endpoint():
    os.environ["AETHERRA_PROMETHEUS"] = "1"
    os.environ["AETHERRA_PROM_PORT"] = "9210"
    active = initialize_exporter()
    if not active:
        pytest.skip("Exporter inactive (missing prometheus_client)")
    update_workspace_queue(3)
    time.sleep(0.2)
    body = None
    for _ in range(5):
        try:
            with urllib.request.urlopen(
                "http://localhost:9210/metrics", timeout=2
            ) as r:  # nosec B310
                body = r.read().decode("utf-8", errors="replace")
            break
        except Exception:
            time.sleep(0.2)
    assert body and "aetherra_consciousness_workspace_queue_size" in body
