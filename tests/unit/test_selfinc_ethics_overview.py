# Third party imports
import requests

BASE = "http://localhost:3001/api/selfinc"


def post_evaluate(action, target):
    resp = requests.post(
        f"{BASE}/ethics/evaluate", json={"action": action, "target": target}, timeout=10
    )
    assert resp.status_code == 200
    return resp.json()


def get_overview():
    resp = requests.get(f"{BASE}/ethics/overview", timeout=10)
    assert resp.status_code == 200
    return resp.json()


def test_ethics_overview_counts(monkeypatch):
    # High risk
    post_evaluate(
        "register_plugin",
        {
            "file_id": "plugin1",
            "declared_capabilities": ["network", "exec", "filesystem"],
        },
    )
    # Medium risk
    post_evaluate(
        "register_plugin",
        {
            "file_id": "plugin2",
            "declared_capabilities": ["ui"],
            "complexity_score": 0.6,
        },
    )
    overview = get_overview()
    stats = overview["stats"]
    assert stats["total_decisions"] >= 2
    assert stats["avg_score"] > 0
    assert overview["risk_assessment"]["high_risk_actions"] >= 1
    assert overview["risk_assessment"]["medium_risk_actions"] >= 1
