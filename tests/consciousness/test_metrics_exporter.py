# Standard library imports
import os
import time

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.metrics_exporter import initialize_exporter

pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_PROM_TESTS") == "1", reason="Prometheus tests skipped by env"
)


def test_metrics_exporter_basic():
    os.environ["AETHERRA_PROMETHEUS"] = "1"
    os.environ["AETHERRA_PROM_PORT"] = "9209"  # avoid clash
    active = initialize_exporter()
    if not active:
        pytest.skip("Prometheus client not available or exporter inactive")
    # Give a moment for server thread
    time.sleep(0.2)
    # Spot check some helper functions exist (not invoking full network fetch here)
    # Aetherra imports
    from Aetherra.consciousness import metrics_exporter as me

    assert me._workspace_queue_gauge is not None
    assert me._narrative_coherence_gauge is not None
