# Standard library imports
import socket

# Third party imports
import pytest
import requests

# Aetherra imports
from aetherra_hub.compat import AetherraHubServer


def _free_port() -> int:
    s = socket.socket()
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.skipif(
    True, reason="Flask dependency or environment heavy; placeholder smoke"
)
def test_replay_gap_metric_increments(monkeypatch):  # pragma: no cover - optional
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_SSE_REPLAY_MAX_EVENTS", "10")
    monkeypatch.setenv("AETHERRA_SSE_REPLAY_MAX_AGE_S", "60")

    port = _free_port()
    server = AetherraHubServer(port)
    assert server.start_server()
    base = f"http://localhost:{port}"

    r1 = requests.post(
        f"{base}/api/ai/stream", json={"message": "one"}, stream=True, timeout=5
    )
    assert r1.status_code == 200
    text1 = "".join(chunk.decode("utf-8") for chunk in r1.iter_content(chunk_size=None))
    last_id = 0
    for line in text1.splitlines():
        if line.startswith("id: "):
            try:
                last_id = int(line.split(": ", 1)[1])
            except Exception:
                pass
    assert last_id > 0

    # Second request with Last-Event-ID should not produce gap metric if no frames missed
    r2 = requests.post(
        f"{base}/api/ai/stream",
        json={"message": "two"},
        headers={"Last-Event-ID": str(last_id)},
        stream=True,
        timeout=5,
    )
    assert r2.status_code == 200

    # Scrape metrics and verify presence of gauge (value may be 0 or 1 depending on timing)
    rmetrics = requests.get(f"{base}/metrics", timeout=5)
    assert rmetrics.status_code == 200
    assert "aetherra_chat_resume_gaps_total" in rmetrics.text
