# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import json

# Aetherra imports
from Aetherra.security.capabilities import POLICY_FILE, get_capability_limits


def setup_module(module):
    # Ensure policy dir exists and clean any existing file
    POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()


def teardown_module(module):
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()


def test_get_capability_limits_empty_when_missing():
    if POLICY_FILE.exists():
        POLICY_FILE.unlink()
    assert get_capability_limits("network:outbound") == {}


def test_get_capability_limits_present():
    data = {
        "allow": {"core:webhook_manager": ["network:webhook"]},
        "limits": {"network:outbound": {"timeout_sec": 9, "max_concurrency": 2}},
    }
    POLICY_FILE.write_text(json.dumps(data), encoding="utf-8")
    limits = get_capability_limits("network:outbound")
    assert isinstance(limits, dict)
    assert limits.get("timeout_sec") == 9
    assert limits.get("max_concurrency") == 2
