# Standard library imports
import importlib
import sys
from functools import partial

# Third party imports
import pytest


@pytest.fixture(autouse=True)
def enable_consciousness(monkeypatch):
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "1")
    # Reset singletons between tests if modules were imported
    for mod_name in [
        "Aetherra.consciousness.workspace_core",
        "Aetherra.consciousness.affect_engine",
        "Aetherra.consciousness.self_model",
        "Aetherra.consciousness.event_bus",
    ]:
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
    return


@pytest.fixture
def metrics_listener(monkeypatch):
    """Own a real loopback exporter and registry, then release both after a test."""
    client = pytest.importorskip("prometheus_client")
    # Aetherra imports
    from Aetherra.consciousness import metrics_exporter as exporter

    registry = client.CollectorRegistry()
    listeners = []
    monkeypatch.setenv("AETHERRA_PROMETHEUS", "1")
    monkeypatch.setenv("AETHERRA_PROM_PORT", "0")
    monkeypatch.setattr(exporter, "_started", False)
    for name in (
        "_workspace_queue_gauge",
        "_narrative_coherence_gauge",
        "_identity_coherence_gauge",
        "_narrative_chapters_gauge",
        "_workspace_candidate_counter",
        "_workspace_broadcast_counter",
        "_workspace_latency_hist",
        "_narrative_generation_hist",
    ):
        monkeypatch.setattr(exporter, name, None)
    for name in ("Gauge", "Counter", "Histogram"):
        monkeypatch.setattr(
            exporter, name, partial(getattr(client, name), registry=registry)
        )

    def start(port):
        listener = client.start_http_server(port, addr="127.0.0.1", registry=registry)
        listeners.append(listener)
        return listener

    monkeypatch.setattr(exporter, "start_http_server", start)
    try:
        yield exporter, listeners
    finally:
        for server, thread in listeners:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            assert not thread.is_alive(), "metrics exporter did not stop"
