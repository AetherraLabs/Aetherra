# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import json
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.security.capabilities import POLICY_FILE, has_capability


def write_policy(tmp_path: Path, allow_map: dict):
    POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    POLICY_FILE.write_text(json.dumps({"allow": allow_map}), encoding="utf-8")


@pytest.fixture(autouse=True)
def cleanup_policy(tmp_path, monkeypatch):
    # Point home dir to a temp so ~/.aetherra resolves there? Not available in module.
    # We'll just ensure POLICY_FILE location exists and clean it up after.
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()
    if POLICY_FILE.parent.exists():
        for p in POLICY_FILE.parent.glob("*.json"):
            p.unlink()
    yield
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()


def test_non_strict_allows_when_not_listed(monkeypatch):
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()
    assert has_capability("core:webhook_manager", "network:webhook") is True


def test_strict_denies_when_not_listed(monkeypatch):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()
    assert has_capability("core:webhook_manager", "network:webhook") is False


def test_strict_allows_when_listed(monkeypatch):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    write_policy(
        Path("."), {"core:webhook_manager": ["network:webhook", "network:outbound"]}
    )
    assert has_capability("core:webhook_manager", "network:webhook") is True
