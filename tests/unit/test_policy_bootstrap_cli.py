# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from __future__ import annotations

import json
import sys

import pytest


@pytest.mark.skipif(
    sys.platform.startswith("win") is False,
    reason="Path semantics aligned for CI; ok to run on all",
)
def test_policy_bootstrap_creates_files(tmp_path, monkeypatch):
    # Point policy home to temp dir
    policy_dir = tmp_path / "policy"
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(policy_dir))

    # Import module and run main
    from Aetherra.cli.policy_bootstrap import main  # type: ignore

    rc = main(["--all", "--allow", "api.example.com", ".corp.example"])
    assert rc == 0

    cap = policy_dir / "capabilities.json"
    net = policy_dir / "net_policy.json"
    assert cap.exists() and net.exists()

    cap_data = json.loads(cap.read_text(encoding="utf-8"))
    net_data = json.loads(net.read_text(encoding="utf-8"))

    assert "allow" in cap_data and isinstance(cap_data["allow"], dict)
    allow_domains = net_data.get("allow_domains", [])
    assert "localhost" in allow_domains and ".aetherra.dev" in allow_domains
    assert "api.example.com" in allow_domains and ".corp.example" in allow_domains
