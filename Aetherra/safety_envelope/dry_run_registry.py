# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Dry-Run Capability Registry
===========================

A wrapper around CapabilityRegistry that prevents side effects by:
- Running preconditions as-is
- Replacing action with a no-op that returns a simulated result
- Replacing rollback with a no-op
- Replacing verify with a stub that always returns True

Use this for integration tests and pre-act checks where safety matters.
Enable via environment flag in runners or construct explicitly.
"""

from __future__ import annotations

import os
from dataclasses import replace
from typing import Optional

from .capability_registry import Capability, CapabilityRegistry


class DryRunCapabilityRegistry(CapabilityRegistry):
    """Non-destructive wrapper around an existing CapabilityRegistry."""

    def __init__(self, base: CapabilityRegistry):
        self._base = base

    def register(self, cap: Capability) -> None:  # type: ignore[override]
        # Forward registration to base registry
        self._base.register(cap)

    def get(self, name: str) -> Optional[Capability]:  # type: ignore[override]
        cap = self._base.get(name)
        if not cap:
            return None

        def _noop_action(args: dict) -> dict:
            return {"dry_run": True, "capability": cap.name, "args": args}

        def _noop_rollback(args: dict) -> dict:
            return {"dry_run": True, "status": "no-op"}

        def _verify(args: dict) -> bool:
            """Verify succeeds by default; in strict mode, allow test-driven failures.

            Strict mode (AETHERRA_DRY_RUN_STRICT=1) behavior:
            - If args contain keys like 'simulate_fail'/'force_fail' truthy → return False
            - Else return True
            """
            if os.getenv("AETHERRA_DRY_RUN_STRICT", "0") == "1":
                for k in ("simulate_fail", "force_fail"):
                    if bool(args.get(k)):
                        return False
            return True

        # Return a capability with overridden action/rollback/verify
        return replace(cap, action=_noop_action, rollback=_noop_rollback, verify=_verify)

    def list_all(self) -> list[str]:  # type: ignore[override]
        return self._base.list_all()

    def list_by_risk(self, risk: str) -> list[str]:  # type: ignore[override]
        return self._base.list_by_risk(risk)
