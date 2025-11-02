# SPDX-License-Identifier: GPL-3.0-or-later
import os
from pathlib import Path

from fastapi.testclient import TestClient


def test_approvals_crud_and_persistence(tmp_path, monkeypatch):
    # Configure persistence path before (re)initializing store
    log_path = tmp_path / "approvals_log.jsonl"
    monkeypatch.setenv("AETHERRA_APPROVALS_PERSIST", "1")
    monkeypatch.setenv("AETHERRA_APPROVALS_LOG_PATH", str(log_path))

    # Import app and replace approval_store with a fresh one
    from Aetherra.api import aether_server
    from Aetherra.api.approvals import ApprovalStore

    aether_server.approval_store = ApprovalStore()
    client = TestClient(aether_server.app)

    # Request a new approval
    req = {
        "intent_goal": "restart service xyz",
        "risk": "medium",
        "requested_by": "tester",
        "reason": "integration test",
        "diff_preview": {"mode": "assist"},
    }
    r = client.post("/approvals/request", json=req)
    assert r.status_code == 200
    rec = r.json()
    rec_id = rec["id"]

    # List pending
    r = client.get("/approvals", params={"status": "pending"})
    assert r.status_code == 200
    data = r.json()
    assert any(a["id"] == rec_id for a in data.get("approvals", []))

    # Get record
    r = client.get(f"/approvals/{rec_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "pending"

    # Approve
    r = client.post(
        f"/approvals/{rec_id}/approve", json={"approver": "owner", "reason": "ok"}
    )
    assert r.status_code == 200

    # List approved
    r = client.get("/approvals", params={"status": "approved"})
    assert r.status_code == 200
    data = r.json()
    assert any(a["id"] == rec_id for a in data.get("approvals", []))

    # Create a second pending and deny it
    r2 = client.post("/approvals/request", json={**req, "reason": "deny-me"})
    assert r2.status_code == 200
    rec2 = r2.json()
    rec2_id = rec2["id"]
    r = client.post(
        f"/approvals/{rec2_id}/deny", json={"approver": "owner", "reason": "no"}
    )
    assert r.status_code == 200

    # Create a third and revoke it while pending
    r3 = client.post("/approvals/request", json={**req, "reason": "revoke-me"})
    assert r3.status_code == 200
    rec3_id = r3.json()["id"]
    r = client.post(
        f"/approvals/{rec3_id}/revoke", json={"approver": "owner", "reason": "rev"}
    )
    assert r.status_code == 200

    # Check JSONL persistence file has lines with event fields
    assert log_path.exists(), "log file should exist"
    content = log_path.read_text(encoding="utf-8").strip().splitlines()
    # Expect at least 4 events: request, approved, denied, revoked
    assert len(content) >= 4
    # Spot-check events
    events = ["requested", "approved", "denied", "revoked"]
    for line in content:
        for ev in events:
            if f'"event": "{ev}"' in line:
                events.remove(ev)
                break
    assert not events, f"missing events in log: {events}"
