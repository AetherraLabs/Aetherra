# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import json
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
import Aetherra.security.capabilities as capabilities


def write_policy(tmp_path: Path, allow_map: dict):
    policy_file = capabilities._policy_file()
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    policy_file.write_text(json.dumps({"allow": allow_map}), encoding="utf-8")


@pytest.fixture(autouse=True)
def cleanup_policy(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    policy_file = capabilities._policy_file()
    if policy_file.exists():
        policy_file.unlink()
    if policy_file.parent.exists():
        for p in policy_file.parent.glob("*.json"):
            p.unlink()
    yield
    if policy_file.exists():
        policy_file.unlink()


def test_non_strict_allows_when_not_listed(monkeypatch):
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    policy_file = capabilities._policy_file()
    if policy_file.exists():
        policy_file.unlink()
    assert capabilities.has_capability("core:webhook_manager", "network:webhook") is True


def test_strict_denies_when_not_listed(monkeypatch):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    policy_file = capabilities._policy_file()
    if policy_file.exists():
        policy_file.unlink()
    assert capabilities.has_capability("core:webhook_manager", "network:webhook") is False


def test_strict_allows_when_listed(monkeypatch):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    write_policy(
        Path("."), {"core:webhook_manager": ["network:webhook", "network:outbound"]}
    )
    assert capabilities.has_capability("core:webhook_manager", "network:webhook") is True
