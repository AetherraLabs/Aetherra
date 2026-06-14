# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import os

import pytest

from Aetherra.security.sandbox import SecuritySandbox, TimeBudgetExceeded


def test_security_sandbox_blocks_risky_operations(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    sandbox = SecuritySandbox(
        {
            "timeout": 0.01,
            "memory_limit": 1,
            "max_operations": 1,
            "blocked_functions": ["subprocess.run"],
        }
    )

    assert sandbox.is_allowed("safe_operation") is True
    assert sandbox.is_allowed("subprocess.run") is False

    result = sandbox.run(lambda: "ok", timeout=0.001)
    assert result == "ok"
