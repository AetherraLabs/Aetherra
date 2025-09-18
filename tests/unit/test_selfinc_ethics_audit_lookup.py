import requests

BASE = "http://localhost:3001/api/selfinc"


def test_ethics_audit_lookup():
    # Evaluate and get trace_id
    resp = requests.post(
        f"{BASE}/ethics/evaluate",
        json={
            "action": "register_plugin",
            "target": {"file_id": "plugin3", "declared_capabilities": ["network"]},
        },
        timeout=10,
    )
    assert resp.status_code == 200
    trace_id = resp.json()["trace_id"]
    # Lookup audit
    audit = requests.get(f"{BASE}/ethics/audit/{trace_id}", timeout=10)
    assert audit.status_code == 200
    data = audit.json()
    assert data["trace_id"] == trace_id
    assert "ethics_overall" in data
    assert "risk_level" in data
    assert "result" in data
