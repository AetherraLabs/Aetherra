# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import sys
import types

# Third party imports
import pytest
import requests

# Aetherra imports
from aetherra_hub.compat import start_hub_server
from schema_validators import validate_lyrixa_chat_response

HAS_FLASK = True
try:
    # Third party imports
    import flask  # noqa: F401
except Exception:
    HAS_FLASK = False


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_persona_present_in_offline_fallback():
    # Use a unique port to avoid clashes with other tests
    server = start_hub_server(port=3013)
    assert server.is_running()

    r = requests.post(
        "http://localhost:3013/api/lyrixa/chat",
        json={"message": "Who are you?"},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    # Strict validator enforces persona presence and type
    validate_lyrixa_chat_response(data)


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_edit_plan_mirrors_suggestions_and_confidence_defaults(monkeypatch):
    # Monkeypatch the service registry so Hub sees a live lyrixa_chat service
    class _FakeService:
        async def handle_message(self, message_type, payload):
            # Return suggestions, omit confidence to exercise defaulting at the bridge
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
                # no 'confidence' and no 'edit_plan'
            }

    class _FakeRegistry:
        def get_service(self, name):
            return _FakeService() if name == "lyrixa_chat" else None

    fake_mod = types.ModuleType("aetherra_service_registry")

    async def get_service_registry():  # type: ignore
        return _FakeRegistry()

    fake_mod.get_service_registry = get_service_registry  # type: ignore[attr-defined]

    # Install fake registry only for this test
    monkeypatch.setitem(sys.modules, "aetherra_service_registry", fake_mod)

    server = start_hub_server(port=3014)
    assert server.is_running()

    r = requests.post(
        "http://localhost:3014/api/lyrixa/chat",
        json={"message": "please fix conflicts", "allow_edits": False},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    # Validate overall shape first (persona, awareness, confidence range, etc.)
    validate_lyrixa_chat_response(data)

    # edit_plan should be synthesized from suggestions by the bridge
    assert "suggestions" in data and isinstance(data["suggestions"], list)
    assert "edit_plan" in data and isinstance(data["edit_plan"], list)
    assert len(data["edit_plan"]) == len(data["suggestions"]) == 1
    assert data["edit_plan"][0].get("action") == data["suggestions"][0].get("action")

    # confidence should default to 0.5 when upstream omitted it
    assert pytest.approx(0.5, rel=0, abs=1e-9) == float(data.get("confidence", 0.0))
