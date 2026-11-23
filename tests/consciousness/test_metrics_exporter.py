# Standard library imports
import os

# Third party imports
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_PROM_TESTS") == "1", reason="Prometheus tests skipped by env"
)


def test_metrics_exporter_basic(metrics_listener):
    exporter, listeners = metrics_listener
    assert exporter.initialize_exporter()
    assert exporter.initialize_exporter()
    assert len(listeners) == 1
    assert exporter._workspace_queue_gauge is not None
    assert exporter._narrative_coherence_gauge is not None
