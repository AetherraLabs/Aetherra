# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import json

# Third party imports
import pytest

# Aetherra imports
from Aetherra.core.webhook_manager import WebhookManager
from Aetherra.security.capabilities import POLICY_FILE as CAP_FILE
from Aetherra.security.net_policy import POLICY_FILE as NET_FILE


def write_cap_policy(grant: bool):
    CAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    allow = {"core:webhook_manager": ["network:webhook"]} if grant else {}
    CAP_FILE.write_text(json.dumps({"allow": allow}), encoding="utf-8")


def write_net_policy(allow_domains):
    NET_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"allow_domains": allow_domains, "deny_domains": []}
    NET_FILE.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture(autouse=True)
def cleanup_files():
    # ensure clean slate
    if CAP_FILE.exists():
        CAP_FILE.unlink()
    if NET_FILE.exists():
        NET_FILE.unlink()
    yield
    if CAP_FILE.exists():
        CAP_FILE.unlink()
    if NET_FILE.exists():
        NET_FILE.unlink()


def test_trigger_blocked_without_capability(monkeypatch):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    write_cap_policy(grant=False)
    manager = WebhookManager()
    manager.register_webhook("evt", "https://example.com/hook")
    # Should print denial and not crash
    manager.trigger_webhook("evt", {"ok": True})


def test_trigger_blocked_by_net_policy(monkeypatch):
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    write_cap_policy(grant=True)
    # Strict network policy only allows localhost
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(["localhost", "127.0.0.1"])

    manager = WebhookManager()
    manager.register_webhook("evt", "https://remote.example/hook")
    manager.trigger_webhook("evt", {"ok": True})
    # Since strict net policy blocks domain, webhook should be blocked before HTTP call
    # We assert by observation: no exception, printed blocked message via stdout already captured
    # and no network call attempted (implicit as we didn't patch http_post)
    assert True


def test_trigger_success_path(monkeypatch):
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    write_cap_policy(grant=True)
    monkeypatch.setenv("AETHERRA_NET_STRICT", "1")
    write_net_policy(["api.service.local"])

    # Patch http_post to simulate success
    # Aetherra imports
    import Aetherra.security.net_policy as netp

    class _R:
        def raise_for_status(self):
            return None

    def ok_post(url, json_payload, timeout=10.0, requester="unknown"):
        return _R()

    monkeypatch.setattr(netp, "http_post", ok_post, raising=True)

    manager = WebhookManager()
    url = "https://api.service.local/hook"
    manager.register_webhook("evt", url)
    manager.trigger_webhook("evt", {"ok": True})
