"""Audit API regressions using the real service and persistent ledger."""

# Standard library imports
import asyncio
from pathlib import Path

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import aetherra_service_registry as registry_module
from aetherra_hub.blueprints.self_incorporation import bp
from aetherra_self_incorporation import (
    AuditLedger,
    SelfIncorporationConfig,
    SelfIncorporationService,
)


@pytest.fixture
def audit_api(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "audit-control-secret")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_SCRIPT_VERIFY_STRICT", "1")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    service = SelfIncorporationService(SelfIncorporationConfig())
    for action, status in (
        ("register_plugin", "applied"),
        ("register_plugin", "denied"),
        ("register_workflow", "applied"),
        ("register_plugin", "applied"),
        ("register_agent", "denied"),
        ("register_workflow", "quarantined"),
    ):
        service.audit_ledger.append(
            plan_id="private-plan",
            action=action,
            status=status,
            target={"path": "private-target"},
            result={"detail": "private-result"},
        )
    # Reopen the ledger so reads must use persisted records, not its cache.
    service.audit_ledger = AuditLedger(service.config.audit_db_path)
    registry = registry_module.AetherraServiceRegistry()
    monkeypatch.setattr(registry_module, "_service_registry", registry)
    assert asyncio.run(registry.register_service("self_incorporation", service))
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app.test_client(), service


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ({}, {"applied": 3, "denied": 2, "quarantined": 1}),
        ({"action": "register_plugin"}, {"applied": 2, "denied": 1}),
        ({"status": "applied"}, {"applied": 3}),
        ({"action": "register_plugin", "status": "applied"}, {"applied": 2}),
        ({"limit": "2"}, {"denied": 1, "quarantined": 1}),
        ({"action": "register_plugin", "limit": "2"}, {"applied": 1, "denied": 1}),
        ({"status": "applied", "limit": "2"}, {"applied": 2}),
        (
            {"action": "register_plugin", "status": "applied", "limit": "1"},
            {"applied": 1},
        ),
        ({"action": "missing"}, {}),
        ({"status": "missing"}, {}),
        ({"action": "' OR 1=1 --"}, {}),
    ],
)
def test_authenticated_audit_counts_latest_matching_records(audit_api, query, expected):
    client, service = audit_api

    response = client.get(
        "/api/selfinc/audit",
        query_string=query,
        headers={"X-Aetherra-Token": "audit-control-secret"},
    )

    assert response.status_code == 200, response.get_json()
    assert response.get_json() == {
        "audit_summary": expected,
        "filters": {
            "action": query.get("action"),
            "status": query.get("status"),
            "limit": int(query.get("limit", 50)),
        },
    }
    assert service.audit_ledger.verify_integrity()


@pytest.mark.parametrize("token", [None, "wrong-token"])
def test_audit_rejects_missing_or_wrong_control_token(audit_api, token):
    client, _ = audit_api
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = client.get("/api/selfinc/audit", headers=headers)

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


@pytest.mark.parametrize("limit", ["0", "-1", "bad", str(2**63)])
def test_audit_rejects_invalid_record_limit(audit_api, limit):
    client, _ = audit_api

    response = client.get(
        "/api/selfinc/audit",
        query_string={"limit": limit},
        headers={"X-Aetherra-Token": "audit-control-secret"},
    )

    assert response.status_code == 400


def test_audit_default_limit_keeps_service_totals_backward_compatible(audit_api):
    client, service = audit_api
    for _ in range(51):
        service.audit_ledger.append(
            plan_id="recent-plan",
            action="register_plugin",
            status="applied",
            target={},
            result={},
        )

    response = client.get(
        "/api/selfinc/audit",
        headers={"X-Aetherra-Token": "audit-control-secret"},
    )

    assert response.status_code == 200, response.get_json()
    assert response.get_json()["audit_summary"] == {"applied": 50}
    assert asyncio.run(service.get_audit_summary()) == {
        "applied": 54,
        "denied": 2,
        "quarantined": 1,
    }
    assert service.audit_ledger.summary() == {
        "applied": 54,
        "denied": 2,
        "quarantined": 1,
    }
