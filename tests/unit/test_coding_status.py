from pathlib import Path

from Aetherra.coding import assess_coding_readiness
from aetherra_hub.app import create_app
from aetherra_hub.blueprints.openapi import bp as openapi_bp


def test_coding_readiness_reports_ready_for_current_repository():
    payload = assess_coding_readiness()

    assert payload["readiness"] == "ready"
    assert payload["safe_for_assist"] is True
    assert payload["safe_for_autonomous_apply"] is False
    assert payload["checks"]["proposal_only_default"] is True
    assert payload["checks"]["direct_mutation_allowed"] is False
    assert payload["checks"]["guardian_required_for_mutation"] is True
    assert payload["checks"]["self_incorporation_required_for_apply"] is True
    assert "candidate patch proposal" in payload["authority"]["owns"]
    assert "direct repository mutation" in payload["authority"]["does_not_own"]
    assert payload["authority"]["mutation_path"][0] == "Coding proposal"


def test_coding_readiness_blocks_when_required_contracts_are_missing(tmp_path):
    payload = assess_coding_readiness(tmp_path)

    assert payload["readiness"] == "blocked"
    assert payload["safe_for_assist"] is False
    assert payload["safe_for_autonomous_apply"] is False
    assert "missing_required:system_document" in payload["reasons"]


def test_coding_status_endpoint_is_read_only_and_no_store():
    client = create_app().test_client()

    response = client.get("/api/coding/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["readiness"]["system"] == "coding"
    assert payload["readiness"]["safe_for_autonomous_apply"] is False


def test_coding_status_route_is_documented_in_openapi():
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(openapi_bp)

    response = app.test_client().get("/api/openapi.json")

    assert response.status_code == 200
    paths = response.get_json()["paths"]
    assert "/api/coding/status" in paths


def test_coding_readiness_accepts_explicit_project_root(tmp_path):
    required_paths = [
        "docs/AETHERRA_CODING_SYSTEM.md",
        "docs/AETHERRA_GUARDIAN_SYSTEM.md",
        "docs/AETHERRA_SECURITY_SYSTEM.md",
        "docs/AETHERRA_SELF-INCORPORATION_SYSTEM.md",
        "tools/verify_aether_scripts.py",
        "tools/spec_tests_gate.py",
        "tools/quality_gates.py",
        "Aetherra/security/script_signing.py",
        "Aetherra/security/plugin_signing.py",
        "aetherra_hub/blueprints/self_incorporation.py",
    ]
    for relative_path in required_paths:
        path = tmp_path / Path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# placeholder\n", encoding="utf-8")

    payload = assess_coding_readiness(tmp_path)

    assert payload["readiness"] == "ready"
    assert payload["reasons"] == ["ready"]
