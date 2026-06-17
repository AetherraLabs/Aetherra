# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import json

# Third party imports
import pytest

# Aetherra imports
import Aetherra.security.capabilities as capabilities


@pytest.fixture(autouse=True)
def isolated_policy_home(tmp_path, monkeypatch):
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    policy_file = capabilities._policy_file()
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    return policy_file


def test_get_capability_limits_empty_when_missing(isolated_policy_home):
    if isolated_policy_home.exists():
        isolated_policy_home.unlink()
    assert capabilities.get_capability_limits("network:outbound") == {}


def test_get_capability_limits_present(isolated_policy_home):
    data = {
        "allow": {"core:webhook_manager": ["network:webhook"]},
        "limits": {"network:outbound": {"timeout_sec": 9, "max_concurrency": 2}},
    }
    isolated_policy_home.write_text(json.dumps(data), encoding="utf-8")
    limits = capabilities.get_capability_limits("network:outbound")
    assert isinstance(limits, dict)
    assert limits.get("timeout_sec") == 9
    assert limits.get("max_concurrency") == 2
