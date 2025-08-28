import pytest

from aetherra_hub_server import AetherraHubServer


@pytest.fixture
def hub():
    h = AetherraHubServer(port=0)
    app = getattr(h, "app", None)
    if not app:
        pytest.skip("Flask not available in test env")
    return h


def test_memory_status_endpoint_shape(hub):
    client = hub.app.test_client()
    rv = client.get("/api/memory/status")
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, dict)
    # Minimal keys expected from fallback
    assert "enabled" in data
    # If engine-like status present, check core fields
    if data.get("enabled"):
        for k in ("coherence", "branch", "branches", "entanglement_nodes"):
            assert k in data


def test_prometheus_metrics_includes_memory_and_chat(hub):
    # Exercise a small part of chat instrumentation by calling /api/ai/ask with API disabled
    # to avoid requiring tokens; metrics should still render with zeros
    client = hub.app.test_client()
    # First, render metrics baseline
    rv0 = client.get("/metrics")
    assert rv0.status_code == 200
    body0 = rv0.data.decode()
    # Memory series should exist (from fallback) even if zeros
    assert "aetherra_memory_coherence_score" in body0
    # Chat series should exist
    for key in (
        "aetherra_chat_requests_total",
        "aetherra_chat_streams_current",
        "aetherra_chat_latency_ms_sum",
        "aetherra_chat_latency_count",
        "aetherra_chat_chars_in_total",
        "aetherra_chat_chars_out_total",
        "aetherra_chat_tokens_in_total",
        "aetherra_chat_tokens_out_total",
    ):
        assert key in body0
    # Histogram buckets should exist (at least one bucket line)
    assert "aetherra_chat_latency_ms_bucket" in body0

    # If AI API is enabled in env, we could post to /api/ai/ask to increment counts.
    # Here we just assert the endpoint exists and returns disabled by default.
    rv = client.post("/api/ai/ask", json={"message": "hi"})
    assert rv.status_code in (200, 501, 403)

    rv1 = client.get("/metrics")
    assert rv1.status_code == 200
    body1 = rv1.data.decode()
    # Metrics still render
    assert "aetherra_chat_requests_total" in body1
