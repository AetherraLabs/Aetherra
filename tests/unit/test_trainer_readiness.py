from flask import Flask

from aetherra_hub.app import create_app
from aetherra_hub.blueprints.openapi import bp as openapi_bp
from aetherra_hub.services import trainer as trainer_service


def test_trainer_readiness_reports_disabled_safe_default(monkeypatch):
    monkeypatch.setenv("AETHERRA_TRAINER_ENABLED", "0")

    payload = trainer_service.assess_trainer_readiness()

    assert payload["readiness"] == "disabled"
    assert payload["safe_for_status"] is True
    assert payload["safe_for_queue_submission"] is False
    assert payload["safe_for_real_training"] is False
    assert "trainer_disabled_safe_default" in payload["reasons"]
    assert payload["checks"]["real_training_backend_enabled"] is False
    assert payload["checks"]["dataset_ingestion_enabled"] is False
    assert payload["checks"]["model_registry_writes_enabled"] is False


def test_trainer_readiness_reports_guarded_when_queue_scaffold_enabled(monkeypatch):
    monkeypatch.setenv("AETHERRA_TRAINER_ENABLED", "1")

    payload = trainer_service.assess_trainer_readiness()

    assert payload["readiness"] == "guarded"
    assert payload["safe_for_queue_submission"] is True
    assert payload["safe_for_real_training"] is False
    assert payload["reasons"] == ["ready"]
    assert "trainer readiness reporting" in payload["authority"]["owns"]
    assert "real training backend execution" in payload["authority"]["does_not_own"]


def test_trainer_status_payload_preserves_legacy_metrics(monkeypatch):
    monkeypatch.setenv("AETHERRA_TRAINER_ENABLED", "0")

    payload = trainer_service.build_trainer_status_payload()

    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["enabled"] is False
    assert "jobs" in payload
    assert "evals" in payload
    assert payload["readiness"]["readiness"] == "disabled"


def test_trainer_status_endpoint_returns_no_store_readiness(monkeypatch):
    monkeypatch.setenv("AETHERRA_TRAINER_ENABLED", "0")
    client = create_app().test_client()

    response = client.get("/api/trainer/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert payload["ok"] is True
    assert payload["read_only"] is True
    assert payload["readiness"]["safe_for_real_training"] is False


def test_trainer_status_route_is_documented_in_openapi():
    app = Flask(__name__)
    app.register_blueprint(openapi_bp)

    response = app.test_client().get("/api/openapi.json")

    assert response.status_code == 200
    paths = response.get_json()["paths"]
    assert "/api/trainer/status" in paths
