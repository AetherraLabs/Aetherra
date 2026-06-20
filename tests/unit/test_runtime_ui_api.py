from __future__ import annotations

from flask import Flask

from aetherra_hub.blueprints.openapi import bp as openapi_bp
from aetherra_hub.blueprints.runtime_ui import bp


def _client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app.test_client()


def test_runtime_ui_observatory_api_returns_read_only_snapshot():
    response = _client().get("/api/runtime-ui/observatory")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True
    observatory = payload["observatory"]
    assert observatory["core_label"] == "AETHERRA"
    assert observatory["read_only"] is True
    assert observatory["mode"] == "overview"

    subsystems = {subsystem["name"]: subsystem for subsystem in observatory["subsystems"]}
    assert {"security", "guardian", "homeostasis", "aether_script"} <= set(subsystems)
    assert subsystems["security"]["metrics"]["authority"] == "enforce"
    assert observatory["events"][0]["details"]["authority"] == "observe_only"


def test_runtime_ui_manifest_api_describes_read_only_contract():
    response = _client().get("/api/runtime-ui/manifest")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True

    manifest = payload["manifest"]
    assert manifest["contract_version"] == "1.0"
    assert manifest["read_only"] is True
    assert manifest["controls_enabled"] is False
    assert manifest["legacy_ui_enabled"] is False
    assert manifest["authority"]["approve"] == "guardian"
    assert manifest["authority"]["enforce"] == "security"
    assert "future_controls_require_guardian_security_and_control_auth" in manifest["safety_rules"]
    assert manifest["endpoints"]["scene"] == "/api/runtime-ui/scene"
    assert manifest["endpoints"]["bootstrap"] == "/api/runtime-ui/bootstrap"
    assert manifest["endpoints"]["status"] == "/api/runtime-ui/status"
    assert "self_improvement" in manifest["supported_subsystems"]


def test_runtime_ui_status_api_reports_healthy_foundation():
    response = _client().get("/api/runtime-ui/status")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["status"] == "healthy"
    assert payload["read_only"] is True
    assert payload["contract_version"] == "1.0"
    assert payload["controls_enabled"] is False
    assert payload["legacy_ui_enabled"] is False
    assert payload["validation"]["ok"] is True
    assert payload["endpoints"]["bootstrap"] == "/api/runtime-ui/bootstrap"


def test_runtime_ui_bootstrap_api_returns_first_load_payload():
    response = _client().get("/api/runtime-ui/bootstrap?mode=first_launch&user=Tim&limit=2")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["manifest"]["read_only"] is True
    assert payload["observatory"]["mode"] == "first_launch"
    assert payload["observatory"]["greeting"] == "Good morning, Tim."
    assert payload["scene"]["coordinate_space"] == "normalized_3d"
    assert payload["activity"]["limit"] == 2
    assert len(payload["activity"]["events"]) == 2


def test_runtime_ui_bootstrap_api_rejects_invalid_mode_and_limit():
    invalid_mode = _client().get("/api/runtime-ui/bootstrap?mode=mutate")
    invalid_limit = _client().get("/api/runtime-ui/bootstrap?limit=lots")

    assert invalid_mode.status_code == 400
    assert invalid_mode.get_json()["error"] == "invalid_mode"
    assert invalid_limit.status_code == 400
    assert invalid_limit.get_json()["error"] == "limit must be an integer"


def test_runtime_ui_contract_validate_api_reports_current_contract_ok():
    response = _client().get("/api/runtime-ui/contract/validate?mode=first_launch&limit=2")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["validation"]["ok"] is True
    assert payload["validation"]["errors"] == []
    assert "observatory" in payload["validation"]["checked"]


def test_runtime_ui_observatory_api_accepts_architect_mode_and_user_name():
    response = _client().get("/api/runtime-ui/observatory?mode=architect&user=Tim")

    assert response.status_code == 200
    observatory = response.get_json()["observatory"]
    assert observatory["mode"] == "architect"
    assert observatory["greeting"] == "Good morning, Tim."
    assert observatory["lyrixa_guidance"].startswith("Architect Mode")


def test_runtime_ui_observatory_api_rejects_invalid_mode():
    response = _client().get("/api/runtime-ui/observatory?mode=execute")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["ok"] is False
    assert payload["error"] == "invalid_mode"
    assert "overview" in payload["allowed_modes"]


def test_runtime_ui_scene_api_returns_state_and_layout():
    response = _client().get("/api/runtime-ui/scene?mode=first_launch&user=Tim")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["observatory"]["greeting"] == "Good morning, Tim."
    assert payload["scene"]["coordinate_space"] == "normalized_3d"
    assert payload["scene"]["read_only"] is True

    nodes = {node["name"]: node for node in payload["scene"]["nodes"]}
    assert nodes["guardian"]["group"] == "governance"
    assert nodes["consciousness"]["group"] == "cognition"


def test_runtime_ui_scene_api_rejects_invalid_mode():
    response = _client().get("/api/runtime-ui/scene?mode=mutate")

    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_mode"


def test_runtime_ui_activity_api_returns_bounded_events():
    response = _client().get("/api/runtime-ui/activity?limit=2")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["filters"]["limit"] == 2
    assert len(payload["events"]) == 2
    assert all("visual_channel" in event for event in payload["events"])


def test_runtime_ui_activity_api_filters_by_channel_and_source():
    channel_response = _client().get("/api/runtime-ui/activity?channel=governance")
    source_response = _client().get("/api/runtime-ui/activity?source=homeostasis")

    assert channel_response.status_code == 200
    channel_payload = channel_response.get_json()
    assert channel_payload["events"]
    assert all(
        event["visual_channel"] == "governance"
        for event in channel_payload["events"]
    )

    assert source_response.status_code == 200
    source_payload = source_response.get_json()
    assert source_payload["events"]
    assert all(event["source"] == "homeostasis" for event in source_payload["events"])


def test_runtime_ui_activity_api_rejects_invalid_limit():
    response = _client().get("/api/runtime-ui/activity?limit=many")

    assert response.status_code == 400
    assert response.get_json()["error"] == "limit must be an integer"


def test_runtime_ui_subsystem_api_returns_focus_profile():
    response = _client().get("/api/runtime-ui/subsystems/self-improvement")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["subsystem"]["name"] == "self_improvement"
    assert payload["profile"]["authority_owner"] == "Self-Improvement"
    assert payload["profile"]["primary_view"] == "proposal_stream"
    assert "propose_only" in payload["profile"]["safety_rules"]
    assert payload["lyrixa_guidance"].startswith("You are viewing Self-Improvement.")


def test_runtime_ui_subsystem_api_returns_related_connections():
    response = _client().get("/api/runtime-ui/subsystems/guardian")

    assert response.status_code == 200
    payload = response.get_json()
    connection_labels = {connection["label"] for connection in payload["connections"]}
    assert {"policy_enforcement", "proposal_review", "approved_execution"} <= connection_labels


def test_runtime_ui_subsystem_api_rejects_unknown_subsystem():
    response = _client().get("/api/runtime-ui/subsystems/desktop")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["ok"] is False
    assert payload["error"] == "unknown_subsystem"
    assert "guardian" in payload["valid_subsystems"]


def test_runtime_ui_routes_are_documented_in_openapi():
    app = Flask(__name__)
    app.register_blueprint(openapi_bp)

    response = app.test_client().get("/api/openapi.json")

    assert response.status_code == 200
    paths = response.get_json()["paths"]
    assert "/api/runtime-ui/activity" in paths
    assert "/api/runtime-ui/bootstrap" in paths
    assert "/api/runtime-ui/contract/validate" in paths
    assert "/api/runtime-ui/manifest" in paths
    assert "/api/runtime-ui/observatory" in paths
    assert "/api/runtime-ui/scene" in paths
    assert "/api/runtime-ui/status" in paths
    assert "/api/runtime-ui/subsystems/{subsystem_name}" in paths


def test_runtime_ui_routes_are_registered_before_frontend_catch_all():
    from aetherra_hub.app import create_app

    response = create_app().test_client().get("/api/runtime-ui/observatory")

    assert response.status_code == 200
    assert response.get_json()["ok"] is True
