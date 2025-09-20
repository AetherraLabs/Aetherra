# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Health Check Tool
=================
Performs a quick OS health check.

Strategy:
- Try a live check via the Service Registry (preferred, fast).
- If unavailable, run the headless smoke script as fallback.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict

CORE_SERVICES = [
    "aetherra_engine",
    "memory_system",
    "plugin_manager",
    "event_bus",
    "agent_fabric",
]


async def _live_check(timeout_s: float = 2.5) -> Dict[str, Any]:
    """Attempt a live health check using the Service Registry.

    Returns a structured result with per-service availability. If the registry
    isn't reachable or errors occur, raises an exception for the caller to
    handle (so we can fall back to smoke mode).
    """
    t0 = time.perf_counter()

    try:
        # Aetherra imports
        from aetherra_service_registry import get_service_registry  # type: ignore
    except Exception as e:  # pragma: no cover - import-time failure path
        raise RuntimeError(f"registry import failed: {e}")

    # Acquire registry (it's async)
    reg = await asyncio.wait_for(get_service_registry(), timeout=timeout_s)
    if reg is None:
        raise RuntimeError("service registry unavailable")

    # Basic registry heartbeat/status if available
    status_detail: Dict[str, Any] = {}
    get_status = getattr(reg, "get_registry_status", None)
    if callable(get_status):
        try:
            maybe = get_status()
            if asyncio.iscoroutine(maybe):
                status_detail = await asyncio.wait_for(maybe, timeout=timeout_s)
            else:
                status_detail = maybe  # type: ignore[assignment]
        except Exception:
            status_detail = {}

    # Probe core services presence via get_service()
    present: Dict[str, bool] = {}
    for name in CORE_SERVICES:
        try:
            svc = reg.get_service(name)  # type: ignore[attr-defined]
        except Exception:
            svc = None
        present[name] = bool(svc)

    ok = all(
        present.get(n, False)
        for n in ["aetherra_engine", "memory_system", "plugin_manager"]
    )

    dt = time.perf_counter() - t0
    return {
        "mode": "live",
        "ok": ok,
        "checks": [{"name": n, "ok": present.get(n, False)} for n in CORE_SERVICES],
        "registry": status_detail or None,
        "duration_ms": round(dt * 1000, 1),
    }


def _run_smoke(timeout_s: float = 20.0) -> Dict[str, Any]:
    """Run the headless smoke script as a fallback check."""
    t0 = time.perf_counter()
    python = sys.executable or "python"
    script = os.path.join(os.path.dirname(__file__), "..", "tools", "os_smoke.py")
    script = os.path.abspath(script)

    try:
        env = {
            **os.environ,
            "AETHERRA_QUIET": os.environ.get("AETHERRA_QUIET", "1"),
            # Ensure consistent UTF-8 decoding across platforms
            "PYTHONIOENCODING": "utf-8",
        }
        proc = subprocess.run(
            [python, script],
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
            env=env,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 0 and "[SMOKE][OK]" in out
        detail = "PASS" if ok else f"FAIL (code={proc.returncode})"
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ""
        ok = False
        detail = "TIMEOUT"

    dt = time.perf_counter() - t0
    return {
        "mode": "smoke",
        "ok": ok,
        "checks": [{"name": "tools/os_smoke.py", "ok": ok, "detail": detail}],
        "output_tail": out.splitlines()[-20:],
        "duration_ms": round(dt * 1000, 1),
    }


def main(*_args: Any, **_kwargs: Any) -> Dict[str, Any]:
    """Tool 'health_check' — Quick OS health check tool.

    Returns a dict with keys: status, mode, checks, summary, duration_ms.
    """
    # Prefer live check; fall back to smoke.
    live: Dict[str, Any] | None = None
    try:
        live = asyncio.run(_live_check())
    except Exception:
        live = None

    # Decide on fallback
    use_smoke = False
    if live is None:
        use_smoke = True
    else:
        if not live.get("ok"):
            checks = {c.get("name"): bool(c.get("ok")) for c in live.get("checks", [])}
            core_present = any(
                checks.get(n)
                for n in ["aetherra_engine", "memory_system", "plugin_manager"]
            )
            total = int((live.get("registry") or {}).get("total_services", 0))
            if not core_present or total == 0:
                use_smoke = True

    smoke: Dict[str, Any] | None = None
    if use_smoke:
        smoke = _run_smoke()

    # Choose primary result
    primary = (
        live if (live and live.get("ok")) else (smoke if smoke is not None else live)
    )
    status = "ok" if primary and primary.get("ok") else "fail"
    if primary and primary.get("mode") == "live" and not primary.get("ok") and live:
        # live but not ok → possibly degraded if some core present
        checks = {c.get("name"): bool(c.get("ok")) for c in live.get("checks", [])}
        core_present = any(
            checks.get(n)
            for n in ["aetherra_engine", "memory_system", "plugin_manager"]
        )
        if core_present:
            status = "degraded"

    res_out: Dict[str, Any] = {
        "status": status,
        "mode": primary.get("mode") if primary else None,
        "checks": primary.get("checks", []) if primary else [],
        "summary": (
            "Live registry check passed"
            if primary and primary.get("mode") == "live" and primary.get("ok")
            else (
                "Smoke check passed"
                if primary and primary.get("mode") == "smoke" and primary.get("ok")
                else "Health check failed"
            )
        ),
        "duration_ms": primary.get("duration_ms") if primary else None,
    }

    # Attach details
    if primary and primary.get("mode") == "smoke":
        res_out["output_tail"] = primary.get("output_tail")
    if live and live.get("registry"):
        res_out["registry"] = live.get("registry")
    if smoke and primary is not smoke:
        res_out["fallback"] = {
            k: v for k, v in smoke.items() if k in {"mode", "ok", "duration_ms"}
        }

    return res_out


if __name__ == "__main__":
    # Allow running as a script for quick manual checks.
    result = main()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") in {"ok", "degraded"} else 1)
