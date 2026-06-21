from aetherra_hub.app import create_app
from aetherra_hub.blueprints import health as health_bp
from aetherra_hub.config import Settings
from aetherra_hub.services.readiness import assess_hub_readiness


def _settings(**overrides):
    data = {
        "ai_api_enabled": False,
        "ai_api_require_token": False,
        "ai_api_token": "",
        "prod_profile": False,
    }
    data.update(overrides)
    return Settings(**data)


def test_hub_readiness_endpoint_reports_ready(monkeypatch):
    monkeypatch.setattr(
        health_bp.registry_client,
        "get_kernel_status",
        lambda: {"running": True},
    )
    monkeypatch.setattr(
        health_bp.registry_client,
        "get_registry_status",
        lambda: {"services": {"aetherra_hub": {"status": "healthy"}}},
    )
    app = create_app(_settings())
    client = app.test_client()

    response = client.get("/api/hub/readiness")
    payload = response.get_json()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert payload["ok"] is True
    assert payload["readiness"]["readiness"] == "ready"
    assert payload["readiness"]["safe_for_clients"] is True
    assert payload["readiness"]["reasons"] == ["ready"]
    assert "ai_api_token" not in payload["settings"]


def test_hub_readiness_degrades_when_dependencies_are_missing():
    app = create_app(_settings())

    payload = assess_hub_readiness(
        app=app,
        settings=_settings(),
        kernel_status=None,
        registry_status=None,
    )

    assert payload["readiness"] == "degraded"
    assert payload["safe_for_clients"] is False
    assert "kernel_status_unavailable" in payload["reasons"]
    assert "service_registry_unavailable" in payload["reasons"]


def test_hub_readiness_blocks_when_required_routes_are_missing():
    app = create_app(_settings())

    payload = assess_hub_readiness(
        app=app,
        settings=_settings(),
        kernel_status={"running": True},
        registry_status={"services": {}},
        required_routes={"/not-registered"},
    )

    assert payload["readiness"] == "blocked"
    assert payload["safe_for_clients"] is False
    assert payload["checks"]["missing_routes"] == ["/not-registered"]


def test_hub_readiness_blocks_in_insecure_prod_posture(monkeypatch):
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    monkeypatch.delenv("AETHERRA_SCRIPT_VERIFY_STRICT", raising=False)
    monkeypatch.delenv("AETHERRA_SIGNING_STRICT", raising=False)
    app = create_app(_settings())
    settings = _settings(
        ai_api_enabled=True,
        ai_api_require_token=False,
        ai_api_token="",
        prod_profile=True,
    )

    payload = assess_hub_readiness(
        app=app,
        settings=settings,
        kernel_status={"running": True},
        registry_status={"services": {}},
    )

    assert payload["readiness"] == "blocked"
    assert "prod_ai_api_token_not_required" in payload["reasons"]
    assert "prod_ai_api_token_missing" in payload["reasons"]
    assert "prod_hub_control_token_missing" in payload["reasons"]
