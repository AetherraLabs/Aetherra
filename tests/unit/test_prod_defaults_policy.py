# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import pytest

# Aetherra imports
from Aetherra.security.capabilities import POLICY_FILE as CAP_FILE
from Aetherra.security.capabilities import has_capability
from Aetherra.security.net_policy import POLICY_FILE as NET_FILE
from Aetherra.security.net_policy import is_domain_allowed


@pytest.fixture(autouse=True)
def _cleanup_files(monkeypatch):
    # Ensure we don't inherit env from other tests
    for k in (
        "AETHERRA_PROFILE",
        "AETHERRA_REQUIRE_CAPABILITIES",
        "AETHERRA_NET_STRICT",
    ):
        monkeypatch.delenv(k, raising=False)
    # Clean policy files
    if CAP_FILE.exists():
        CAP_FILE.unlink()
    if NET_FILE.exists():
        NET_FILE.unlink()
    yield
    if CAP_FILE.exists():
        CAP_FILE.unlink()
    if NET_FILE.exists():
        NET_FILE.unlink()


def test_capabilities_deny_by_default_in_prod(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    # No capability policy and no explicit strict env -> should still deny in prod
    assert has_capability("plugin:demo", "execute") is False


def test_net_strict_and_default_allowlist_in_prod(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # No net policy file present and no explicit strict env
    # Default allowlist should permit localhost and *.aetherra.dev
    assert is_domain_allowed("http://localhost:8080/health", "unit:test") is True
    assert is_domain_allowed("https://api.aetherra.dev/v1", "unit:test") is True
    # Unknown domain should be denied under prod default strict
    assert is_domain_allowed("https://example.com", "unit:test") is False
