#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Capability verification tests:
- Soft mode: missing capabilities yield warnings and verified list is populated when available
- Strict mode: AETHERRA_REQUIRE_CAPABILITIES=1 causes failure on missing capabilities
"""

import asyncio
import os
import sys
import types

import pytest

from aetherra_script_service import AetherScriptService


def run(script: str) -> dict:
    service = AetherScriptService()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(
        service.execute_script_content(script, filename="<capability-test>")
    )


def install_fake_capabilities_module(grants: dict[str, bool]):
    """Install a temporary Aetherra.security.capabilities module exposing has_capability()."""
    pkg = types.ModuleType("Aetherra")
    security = types.ModuleType("Aetherra.security")
    caps = types.ModuleType("Aetherra.security.capabilities")

    def has_capability(requester: str, capability: str) -> bool:
        return bool(grants.get(capability, False))

    # Direct attribute assignment is sufficient
    caps.has_capability = has_capability  # type: ignore[attr-defined]
    sys.modules["Aetherra"] = pkg
    sys.modules["Aetherra.security"] = security
    sys.modules["Aetherra.security.capabilities"] = caps


@pytest.mark.parametrize(
    ("grants", "missing"),
    [
        ({"alpha": True, "beta": False}, ["beta"]),
        ({"alpha": False, "beta": False}, ["alpha", "beta"]),
    ],
)
def test_capabilities_soft_mode(monkeypatch, grants, missing):
    # Ensure strict mode is disabled
    monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)
    install_fake_capabilities_module(grants)

    script = """
goal "soft capability check"
require
    capabilities = ["alpha", "beta"]
"""
    out = run(script)
    assert out.get("success") is True
    payload = out.get("result", {})
    # Verified ones should be present
    verified = set(payload.get("verified_capabilities", []))
    for cap, ok in grants.items():
        if ok:
            assert cap in verified
    # Missing should produce warnings
    warnings = ",".join(payload.get("warnings", []))
    for cap in missing:
        assert (cap in warnings) or ("capabilities_unverified" in warnings)


def test_capabilities_strict_failure(monkeypatch):
    # Enable strict mode and simulate one missing capability
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    install_fake_capabilities_module({"alpha": True, "beta": False})

    script = """
goal "strict capability check"
require
    capabilities = ["alpha", "beta"]
"""
    out = run(script)
    assert out.get("success") is False
    assert "Missing required capabilities" in (out.get("error") or "")
