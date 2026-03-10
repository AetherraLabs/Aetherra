#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
verify_llm_setup.py

Quick checks for Aetherra LLM provider configuration and AI API flags.
- Verifies AETHERRA_AI_API_* flags consistency
- Verifies presence of provider keys (OpenAI/Anthropic/Google)
- Optionally performs a minimal provider round-trip if libraries present

Exit codes:
 0 = OK
 1 = Misconfiguration detected
"""

from __future__ import annotations

# Standard library imports
import json
import os
import sys
from typing import Any


def _env_bool(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip() == "1"


def check_flags() -> dict[str, Any]:
    out: dict[str, Any] = {"ok": True, "warnings": [], "notes": []}
    enabled = _env_bool("AETHERRA_AI_API_ENABLED")
    stream = _env_bool("AETHERRA_AI_API_STREAM")
    require = _env_bool("AETHERRA_AI_API_REQUIRE_TOKEN")
    token = (
        os.environ.get("AETHERRA_AI_API_TOKEN")
        or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
        or ""
    ).strip()

    if not enabled:
        out["warnings"].append(
            "AETHERRA_AI_API_ENABLED=0 (developer AI endpoints disabled)"
        )
    if stream and not enabled:
        out["warnings"].append("AETHERRA_AI_API_STREAM=1 but AI API is disabled")
    if require and not token:
        out["ok"] = False
        out["warnings"].append(
            "Token required but no AETHERRA_AI_API_TOKEN or AETHERRA_HUB_CONTROL_TOKEN set"
        )
    return out


def check_provider_keys() -> dict[str, Any]:
    out: dict[str, Any] = {"ok": True, "providers": {}}
    for name, env in (
        ("openai", "OPENAI_API_KEY"),
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("google", "GOOGLE_API_KEY"),
    ):
        val = os.environ.get(env, "").strip()
        out["providers"][name] = {"present": bool(val)}
    if not any(p["present"] for p in out["providers"].values()):
        out["ok"] = False
    return out


def maybe_round_trip() -> dict[str, Any]:
    """Attempt a minimal local round-trip if SDKs are installed and keys present.
    Best-effort: never raises, returns status only.
    """
    res: dict[str, Any] = {"attempted": False, "ok": True, "details": []}
    # OpenAI
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        try:
            # Third party imports
            from openai import OpenAI  # type: ignore

            client = OpenAI()
            # Use a lightweight models.list call
            _ = client.models.list()
            res["details"].append("OpenAI SDK reachable")
            res["attempted"] = True
        except Exception as e:  # pragma: no cover
            res["details"].append(f"OpenAI check failed: {e}")
            res["ok"] = False
            res["attempted"] = True
    # Anthropic
    akey = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if akey:
        try:
            # Third party imports
            import anthropic  # type: ignore

            _ = anthropic.Anthropic(api_key=akey)
            res["details"].append("Anthropic SDK reachable")
            res["attempted"] = True
        except Exception as e:  # pragma: no cover
            res["details"].append(f"Anthropic check failed: {e}")
            res["ok"] = False
            res["attempted"] = True
    return res


def main() -> int:
    report: dict[str, Any] = {
        "flags": check_flags(),
        "providers": check_provider_keys(),
        "round_trip": maybe_round_trip(),
    }
    ok = (
        bool(report["flags"]["ok"])
        and bool(report["providers"]["ok"])
        and bool(report["round_trip"]["ok"])
        if report["round_trip"]["attempted"]
        else bool(report["flags"]["ok"]) and bool(report["providers"]["ok"])
    )
    # Print compact JSON for CI readability
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
