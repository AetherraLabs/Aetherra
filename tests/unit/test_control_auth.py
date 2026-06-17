"""Tests for privileged Hub control-plane authorization."""

from __future__ import annotations

from aetherra_hub.services.control_auth import (
    authorize_control_request,
    authorize_token_request,
    provided_token,
)


def test_non_production_without_token_allows_loopback(monkeypatch):
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    monkeypatch.setenv("AETHERRA_PROFILE", "test")

    result = authorize_control_request({}, "127.0.0.1")

    assert result.allowed is True


def test_non_production_without_token_blocks_remote(monkeypatch):
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    monkeypatch.setenv("AETHERRA_PROFILE", "dev")

    result = authorize_control_request({}, "203.0.113.10")

    assert result.allowed is False
    assert result.status_code == 403
    assert result.error == "loopback_required"


def test_production_requires_configured_token(monkeypatch):
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")

    result = authorize_control_request({}, "127.0.0.1")

    assert result.allowed is False
    assert result.status_code == 503
    assert result.error == "control_token_not_configured"


def test_configured_token_is_required_even_for_loopback(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "dev")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "expected-token")

    missing = authorize_control_request({}, "127.0.0.1")
    invalid = authorize_control_request(
        {"X-Aetherra-Control-Token": "wrong-token"}, "127.0.0.1"
    )
    valid = authorize_control_request(
        {"Authorization": "Bearer expected-token"}, "127.0.0.1"
    )

    assert missing.allowed is False
    assert invalid.allowed is False
    assert valid.allowed is True


def test_service_token_authorization_requires_configuration_and_valid_token():
    missing_config = authorize_token_request({}, None)
    missing_token = authorize_token_request({}, "expected")
    valid = authorize_token_request({"Authorization": "Bearer expected"}, "expected")

    assert missing_config.status_code == 503
    assert missing_token.status_code == 401
    assert valid.allowed is True


def test_token_extraction_supports_standard_and_legacy_headers():
    assert provided_token({"Authorization": "Bearer abc"}) == "abc"
    assert provided_token({"X-Aetherra-Control-Token": "def"}) == "def"
    assert provided_token({"X-Aetherra-Token": "ghi"}) == "ghi"
