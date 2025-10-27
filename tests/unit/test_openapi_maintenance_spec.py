# Standard library imports
import os

# Third party imports
from flask.testing import FlaskClient

# Aetherra imports
from aetherra_hub.app import create_app


def test_openapi_includes_maintenance_status():
    os.environ.pop("AETHERRA_PROFILE", None)
    app = create_app()
    client: FlaskClient = app.test_client()

    resp = client.get("/api/openapi.json")
    assert resp.status_code == 200
    data = resp.get_json()

    # Ensure the maintenance status path is present
    paths = data.get("paths", {})
    assert "/api/maintenance/status" in paths

    # Basic schema presence
    components = data.get("components", {})
    schemas = components.get("schemas", {})
    assert "MaintenanceStatus" in schemas

    # Minimal shape sanity
    maint = schemas["MaintenanceStatus"]
    assert maint.get("type") == "object"
    props = maint.get("properties", {})
    for key in (
        "ok",
        "ts",
        "overall",
        "kpis",
        "homeostasis",
        "self_improvement",
        "self_incorporation",
    ):
        assert key in props
    # kpis sub-schema shape
    kpis = props.get("kpis", {})
    assert kpis.get("type") == "object"
    # Ensure new KPI fields are described
    kprops = kpis.get("properties", {})
    assert "proposals_generated" in kprops
    assert "proposals_executed" in kprops
    assert "proposals_accepted" in kprops
