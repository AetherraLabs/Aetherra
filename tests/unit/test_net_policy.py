import json

import pytest

from Aetherra.security.net_policy import POLICY_FILE, is_domain_allowed


def write_net_policy(allow=None, deny=None):
    POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"allow_domains": allow or [], "deny_domains": deny or []}
    POLICY_FILE.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture(autouse=True)
def cleanup_net_policy():
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()
    if POLICY_FILE.parent.exists():
        for p in POLICY_FILE.parent.glob("*.json"):
            p.unlink()
    yield
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()


def test_non_strict_allows_unknown(monkeypatch):
    monkeypatch.delenv("AETHERRA_NET_STRICT", raising=False)
    write_net_policy(allow=["example.com"], deny=["bad.test"])
    assert is_domain_allowed("https://unknown.tld/api", "unit:test") is True


def test_strict_blocks_unknown(monkeypatch):
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(allow=["example.com"], deny=["bad.test"])
    assert is_domain_allowed("https://unknown.tld/api", "unit:test") is False


def test_deny_list_blocks(monkeypatch):
    monkeypatch.setenv("AETHERRA_NET_STRICT", "0")
    write_net_policy(allow=["example.com"], deny=["blocked.example"])
    assert is_domain_allowed("https://blocked.example/path", "unit:test") is False


def test_allow_list_permits(monkeypatch):
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(allow=["api.service.local"], deny=[])
    assert is_domain_allowed("https://api.service.local/v1", "unit:test") is True
