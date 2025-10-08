from __future__ import annotations

from aetherra_hub.app import create_app


def test_openapi_contains_qfac_admin_paths():
    app = create_app()
    client = app.test_client()
    r = client.get("/api/openapi.json")
    assert r.status_code == 200
    data = r.get_json()
    assert "/api/qfac/admin/show" in data.get("paths", {})
    assert "/api/qfac/admin/reset" in data.get("paths", {})
    assert "get" in data["paths"]["/api/qfac/admin/show"]
    assert "post" in data["paths"]["/api/qfac/admin/reset"]
