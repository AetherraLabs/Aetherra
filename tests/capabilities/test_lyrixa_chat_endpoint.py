import pytest
import requests

from aetherra_hub_server import start_hub_server

HAS_FLASK = True
try:
    import flask  # noqa: F401
except Exception:
    HAS_FLASK = False


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_lyrixa_chat_endpoint_basic():
    # Start hub server on a test port (global singleton safe to call repeatedly)
    server = start_hub_server(port=3011)
    assert server.is_running()

    # Basic identity-style query; endpoint should respond even if Lyrixa service isn't online
    r = requests.post(
        "http://localhost:3011/api/lyrixa/chat",
        json={"message": "Who are you?", "allow_edits": False},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "text" in data and isinstance(data["text"], str)
    # Suggestions and applied_changes are present in the happy path; tolerate absence in fallback
    if "suggestions" in data:
        assert isinstance(data["suggestions"], list)
    if "applied_changes" in data:
        assert isinstance(data["applied_changes"], list)
