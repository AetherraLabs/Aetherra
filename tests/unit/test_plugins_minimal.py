from __future__ import annotations

import json

from flask import Flask

from aetherra_hub.app import create_app
from aetherra_hub.config import Settings


def _app() -> Flask:
    s = Settings()
    return create_app(s)


def test_plugin_register_and_duplicate():
    app = _app()
    client = app.test_client()

    payload = {"name": "code_editor", "version": "1.0.0", "description": "Cool editor"}
    r1 = client.post(
        "/api/plugins/register",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json", "Idempotency-Key": "k1"},
    )
    assert r1.status_code == 200, r1.data
    data1 = r1.get_json()
    assert data1["status"] == "ok"

    r2 = client.post(
        "/api/plugins/register",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json", "Idempotency-Key": "k1"},
    )
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert data2.get("status") == "duplicate"


def test_plugin_payload_size_and_validation():
    app = _app()
    client = app.test_client()

    # Oversize
    big_desc = "x" * (app.settings.max_payload_kb * 1024 + 10)  # type: ignore[attr-defined]
    r_big = client.post(
        "/api/plugins/register",
        data=json.dumps({"name": "n", "version": "1.0.0", "description": big_desc}),
        headers={"Content-Type": "application/json"},
    )
    assert r_big.status_code == 413

    # Missing name
    r_err = client.post(
        "/api/plugins/register",
        data=json.dumps({"version": "1.0.0", "description": "desc"}),
        headers={"Content-Type": "application/json"},
    )
    assert r_err.status_code == 400


def test_plugin_list():
    app = _app()
    client = app.test_client()
    client.post(
        "/api/plugins/register",
        data=json.dumps({"name": "t1", "version": "1.0.0", "description": "d"}),
        headers={"Content-Type": "application/json"},
    )
    r = client.get("/api/plugins")
    assert r.status_code == 200
    js = r.get_json()
    assert js.get("total") >= 1


def test_plugin_metrics_and_openapi():
    app = _app()
    client = app.test_client()
    # Trigger a registration
    client.post(
        "/api/plugins/register",
        data=json.dumps({"name": "m1", "version": "1.0.0", "description": "desc"}),
        headers={"Content-Type": "application/json"},
    )
    r_metrics = client.get("/api/plugins/metrics")
    assert r_metrics.status_code == 200
    m = r_metrics.get_json()
    assert m.get("registrations_total", 0) >= 1
    r_spec = client.get("/api/plugins/openapi.json")
    assert r_spec.status_code == 200
    spec = r_spec.get_json()
    assert spec.get("openapi")
