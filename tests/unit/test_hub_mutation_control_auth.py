"""Authorization tests for privileged Hub mutation endpoints."""

from __future__ import annotations

import pytest

# Aetherra imports
from aetherra_hub.app import create_app

MUTATION_REQUESTS = (
    ("/api/homeostasis/mode", {"mode": "observe_only"}),
    ("/api/homeostasis/emergency_stop", {"reason": "test"}),
    ("/api/homeostasis/reset_emergency", {}),
    (
        "/api/homeostasis/actuators/execute",
        {"action_type": "noop", "target_service": "test"},
    ),
    ("/api/homeostasis/rollback", {}),
    ("/api/selfimprove/apply", {"proposal_id": "SI-TEST"}),
    ("/api/selfimprove/batch-apply", {"proposals": []}),
    ("/api/selfinc/scan", {}),
    ("/api/selfinc/apply", {"dry_run": True}),
    ("/api/selfinc/rollback", {"rb_token": "rb_test"}),
    (
        "/api/selfinc/ethics/evaluate",
        {"action": "inspect", "target": {"file_id": "test"}},
    ),
    ("/api/interactive/trigger", {"emotion": "calm"}),
)


@pytest.mark.parametrize(("path", "payload"), MUTATION_REQUESTS)
def test_mutation_endpoint_requires_control_token(monkeypatch, path, payload):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    client = create_app().test_client()

    response = client.post(path, json=payload)

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_authorized_request_reaches_endpoint_validation(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    client = create_app().test_client()

    response = client.post(
        "/api/selfinc/rollback",
        json={},
        headers={"Authorization": "Bearer control-secret"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "rollback token required"
