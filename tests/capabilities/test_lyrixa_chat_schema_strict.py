# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import sys
import types

# Third party imports
import pytest
import requests
from schema_validators import validate_lyrixa_chat_response

# Aetherra imports
from aetherra_hub.compat import start_hub_server

HAS_FLASK = True
try:
    # Third party imports
    import flask  # noqa: F401
except Exception:
    HAS_FLASK = False


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_lyrixa_chat_offline_fallback_schema_strict():
    server = start_hub_server(port=3015)
    assert server.is_running()

    r = requests.post(
        "http://localhost:3015/api/lyrixa/chat",
        json={"message": "Hello"},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    validate_lyrixa_chat_response(data)


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_lyrixa_chat_upstream_suggestions_schema_strict(monkeypatch):
    # Fake registry to force lyrixa_chat availability
    class _FakeService:
        async def handle_message(self, message_type, payload):
            return {
                "text": "Applied analysis",
                "suggestions": [
                    {
                        "title": "Resolve merge conflict markers",
                        "file": "tests/tmp_conflict.py",
                        "action": "remove_conflict_markers",
                    }
                ],
                "applied_changes": [],
                # no confidence -> bridge should default to 0.5
            }

    class _FakeRegistry:
        def get_service(self, name):
            return _FakeService() if name == "lyrixa_chat" else None

    fake_mod = types.ModuleType("aetherra_service_registry")

    async def get_service_registry():  # type: ignore
        return _FakeRegistry()

    fake_mod.get_service_registry = get_service_registry  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "aetherra_service_registry", fake_mod)

    server = start_hub_server(port=3016)
    assert server.is_running()

    r = requests.post(
        "http://localhost:3016/api/lyrixa/chat",
        json={"message": "please fix conflicts", "allow_edits": False},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    validate_lyrixa_chat_response(data)
    # Additional assertion: if suggestions exist, edit_plan should mirror length
    if isinstance(data.get("suggestions"), list):
        assert isinstance(data.get("edit_plan"), list)
        assert len(data["edit_plan"]) == len(data["suggestions"])
