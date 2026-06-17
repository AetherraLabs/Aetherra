# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import json
from dataclasses import dataclass

# Third party imports
import pytest

# Aetherra imports
import Aetherra.security.net_policy as net_policy


@dataclass
class _Response:
    status_code: int = 200


def write_net_policy(allow=None, deny=None):
    policy_file = net_policy._policy_file()
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    data = {"allow_domains": allow or [], "deny_domains": deny or []}
    policy_file.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture(autouse=True)
def cleanup_net_policy(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    policy_file = net_policy._policy_file()
    if policy_file.exists():
        policy_file.unlink()
    if policy_file.parent.exists():
        for p in policy_file.parent.glob("*.json"):
            p.unlink()
    yield
    if policy_file.exists():
        policy_file.unlink()


def test_non_strict_allows_unknown(monkeypatch):
    monkeypatch.delenv("AETHERRA_NET_STRICT", raising=False)
    write_net_policy(allow=["example.com"], deny=["bad.test"])
    assert net_policy.is_domain_allowed("https://unknown.tld/api", "unit:test") is True


def test_strict_blocks_unknown(monkeypatch):
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(allow=["example.com"], deny=["bad.test"])
    assert net_policy.is_domain_allowed("https://unknown.tld/api", "unit:test") is False


def test_deny_list_blocks(monkeypatch):
    monkeypatch.setenv("AETHERRA_NET_STRICT", "0")
    write_net_policy(allow=["example.com"], deny=["blocked.example"])
    assert net_policy.is_domain_allowed("https://blocked.example/path", "unit:test") is False


def test_allow_list_permits(monkeypatch):
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(allow=["api.service.local"], deny=[])
    assert net_policy.is_domain_allowed("https://api.service.local/v1", "unit:test") is True


def test_http_post_writes_guardian_audit(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(allow=["api.service.local"], deny=[])
    calls = []

    def _post(url, json, timeout, headers):
        calls.append({"url": url, "json": json, "timeout": timeout, "headers": headers})
        return _Response()

    monkeypatch.setattr(net_policy.requests, "post", _post)

    response = net_policy.http_post(
        "https://api.service.local/v1/hook",
        {"ok": True},
        requester="core:webhook_manager",
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert isinstance(response, _Response)
    assert calls
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["intent"]["action"] == "network.request"
    assert entries[-1]["details"]["intent"]["target"] == "network:api.service.local"
    assert entries[-1]["details"]["intent"]["capabilities"] == ["network:webhook"]


def test_http_get_blocked_by_guardian_missing_capability(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    write_net_policy(allow=["api.service.local"], deny=[])
    called = False

    def _get(url, timeout, headers):
        nonlocal called
        called = True
        return _Response()

    monkeypatch.setattr(net_policy.requests, "get", _get)

    response = net_policy.http_get(
        "https://api.service.local/private",
        requester="unit:test",
    )

    assert response is None
    assert called is False


def test_guardian_network_audit_omits_payload_headers_and_query(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(allow=["api.service.local"], deny=[])

    monkeypatch.setattr(
        net_policy.requests,
        "post",
        lambda url, json, timeout, headers: _Response(),
    )

    response = net_policy.http_post(
        "https://api.service.local/v1/hook?token=query-secret",
        {"secret": "payload-secret"},
        requester="unit:test",
        headers={"Authorization": "Bearer header-secret"},
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")

    assert isinstance(response, _Response)
    assert "payload-secret" not in ledger_text
    assert "header-secret" not in ledger_text
    assert "query-secret" not in ledger_text
    assert "api.service.local" in ledger_text
