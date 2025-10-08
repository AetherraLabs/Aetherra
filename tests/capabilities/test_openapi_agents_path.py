import json


def test_openapi_includes_agents_path():
    # Lazy import to avoid heavy init
    from aetherra_hub.app import create_app

    app = create_app()
    client = app.test_client()
    rv = client.get("/api/openapi.json")
    assert rv.status_code == 200
    data = rv.get_json(force=True)
    assert isinstance(data, dict)
    paths = data.get("paths") or {}
    assert "/api/agents" in paths, "OpenAPI should document /api/agents path"
