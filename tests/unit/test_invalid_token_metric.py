# Standard library imports
import importlib
import re
import sys

# Third party imports
import pytest


def _metric_value(body: str, metric_name: str) -> int:
    match = re.search(rf"^{re.escape(metric_name)}\s+([0-9]+)", body, re.MULTILINE)
    assert match, body
    return int(match.group(1))


@pytest.mark.asyncio
async def test_invalid_token_increments(monkeypatch):
    # Ensure clean import
    if "aetherra_hub.app" in sys.modules:
        importlib.reload(importlib.import_module("aetherra_hub.app"))

    # Enable API + stream, require token, set expected token
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_AI_API_STREAM", "1")
    monkeypatch.setenv("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    monkeypatch.setenv("AETHERRA_AI_API_TOKEN", "expected")
    monkeypatch.setenv(
        "AETHERRA_PROD_UNSAFE_ALLOW", "1"
    )  # bypass prod guard if profile prod
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")

    # Aetherra imports
    from aetherra_hub.app import create_app

    app = create_app()
    client = app.test_client()

    metric_name = "aetherra_chat_auth_invalid_token_total"
    initial = _metric_value(client.get("/metrics").data.decode(), metric_name)

    # First request with wrong token should 403 and increment metric
    r = client.post(
        "/api/ai/stream", json={"message": "hi"}, headers={"X-Aetherra-Token": "wrong"}
    )
    assert r.status_code == 403

    # Scrape metrics
    mr = client.get("/metrics")
    body = mr.data.decode()
    assert _metric_value(body, metric_name) == initial + 1

    # Second wrong attempt increments again
    r2 = client.post(
        "/api/ai/stream", json={"message": "hi"}, headers={"X-Aetherra-Token": "nope"}
    )
    assert r2.status_code == 403
    mr2 = client.get("/metrics")
    body2 = mr2.data.decode()
    assert _metric_value(body2, metric_name) == initial + 2
