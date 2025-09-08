#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Verify Aetherra OS Architecture Map (v1.x) conformance
------------------------------------------------------
Checks for the presence of core components, modules, and contracts referenced
in docs/aetherra_os_architecture_map_v_1.md and prints a compact PASS/FAIL report.
Can optionally perform light runtime probes (Hub HTTP endpoints) and validate
Agent Fabric capability policies + env/HMR flags behavior.

Usage:
    python tools/verify_architecture_map.py
    python tools/verify_architecture_map.py --strict              # non-zero exit on any FAIL
    python tools/verify_architecture_map.py --probe-hub           # start Hub on a temp port and hit a few endpoints

Notes:
  - Offline/static: does not start services or hit HTTP by default.
  - Focuses on existence/importability and key attributes/functions.
  - Extend as the map evolves (sections, endpoints, env flags, etc.).
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import os
import socket
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, List


def _exists(path: str) -> bool:
    return Path(path).exists()


def _try_import(name: str) -> tuple[bool, str | None]:
    try:
        importlib.import_module(name)
        return True, None
    except Exception as e:
        return False, str(e)


def check_kernel() -> Dict:
    files = [
        "aetherra_kernel_loop.py",
        "aetherra_service_registry.py",
        "aetherra_event_bus.py",
        "aetherra_module_manager.py",
    ]
    present = [f for f in files if _exists(f)]
    missing = [f for f in files if f not in present]
    return {
        "ok": len(missing) == 0,
        "present": present,
        "missing": missing,
        "notes": "Kernel loop, Registry, Event Bus, Module Manager",
    }


def check_engine() -> Dict:
    # Prefer modern engine module path; fall back to legacy markers
    candidates = [
        ("Aetherra.aetherra_core.engine.aetherra_engine", True),
        ("aetherra_core_analyzer", False),
    ]
    ok_any = False
    errors: List[str] = []
    for mod, required in candidates:
        ok, err = _try_import(mod)
        if ok:
            ok_any = True
        elif required:
            errors.append(f"{mod}: {err}")
    return {
        "ok": ok_any,
        "errors": errors,
        "notes": "Engine presence (execute_task, processing loops)",
    }


def check_agents() -> Dict:
    # Support both orchestrator and OS-level Agent Fabric
    mods = [
        "Aetherra.aetherra_core.orchestration.agent_orchestrator",
        "aetherra_agent_fabric",
    ]
    ok = False
    errors: List[str] = []
    found: List[str] = []
    for m in mods:
        good, err = _try_import(m)
        if good:
            ok = True
            found.append(m)
        else:
            errors.append(f"{m}: {err}")
    return {
        "ok": ok,
        "found": found,
        "notes": "Agent orchestrator/fabric available",
        "errors": [] if ok else errors,
    }


def check_memory() -> Dict:
    mods = [
        "Aetherra.aetherra_core.memory.quantum_memory_integration",
        "Aetherra.aetherra_core.memory.lyrixa_memory_engine",
        "Aetherra.aetherra_core.memory.quantum_memory_engine",
    ]
    ok_any = False
    errors: List[str] = []
    for m in mods:
        ok, err = _try_import(m)
        if ok:
            ok_any = True
        else:
            errors.append(f"{m}: {err}")
    return {
        "ok": ok_any,
        "notes": "Core/Advanced/Quantum memory modules import",
        "errors": [] if ok_any else errors,
    }


def check_chat() -> Dict:
    # Hub server should exist; lyrixa chat bridge too
    files = ["aetherra_hub_server.py"]
    present = [f for f in files if _exists(f)]
    ok_any, err = _try_import("Aetherra.lyrixa.chat.lyrixa_chat_service")
    ok = len(present) == 1 and ok_any
    errors = [] if ok else [err or "lyrixa_chat_service import failed"]
    return {
        "ok": ok,
        "present": present,
        "notes": "Hub server file + Lyrixa chat service import",
        "errors": [] if ok else errors,
    }


def check_security() -> Dict:
    mods = [
        "Aetherra.security.plugin_signing",
        "Aetherra.security.sandbox",
        "Aetherra.security.prompt_defense",
    ]
    ok_all = True
    errors: List[str] = []
    for m in mods:
        ok, err = _try_import(m)
        if not ok:
            ok_all = False
            errors.append(f"{m}: {err}")
    return {
        "ok": ok_all,
        "notes": ".aether/plugin signing, sandbox, prompt defense",
        "errors": errors,
    }


def check_docs_alignment() -> Dict:
    ok = _exists("docs/aetherra_os_architecture_map_v_1.md")
    return {
        "ok": ok,
        "notes": "Architecture map present",
        "path": "docs/aetherra_os_architecture_map_v_1.md",
    }


def check_env_flags() -> Dict:
    flags = [
        "AETHERRA_PROFILE",
        "AETHERRA_QFAC_MODE",
        "AETHERRA_HMR_ENABLED",
        "AETHERRA_SCRIPT_VERIFY_STRICT",
        "AETHERRA_AGENTS_API_ENABLED",
    ]
    configured = {k: os.getenv(k) for k in flags if os.getenv(k) is not None}
    return {
        "ok": True,
        "notes": "Key env flags (present if set)",
        "configured": configured,
    }


# ---------------- Optional runtime/behavior checks ----------------
def _find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("localhost", 0))
        return int(s.getsockname()[1])


def check_hub_minimal_api_probe(port: int | None = None, timeout: float = 1.5) -> Dict:
    try:
        from aetherra_hub_server import AetherraHubServer
    except Exception as e:
        return {
            "ok": False,
            "errors": [f"import hub_server failed: {e}"],
            "notes": "Flask may be missing; install to enable probe",
        }

    errors: List[str] = []
    p = port or _find_free_port()
    server = AetherraHubServer(p)
    started = bool(server.start_server())
    if not started:
        return {"ok": False, "errors": ["hub failed to start"], "port": p}
    # Give it a brief moment
    time.sleep(0.2)
    base = f"http://localhost:{p}"

    def _get(path: str) -> tuple[int, str]:
        url = base + path
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:  # nosec B310
                code = int(resp.status)
                ctype = str(resp.headers.get("Content-Type") or "")
                body = resp.read().decode("utf-8", errors="replace")
                return code, (ctype or "") + "\n" + body[:200]
        except Exception as e:  # pragma: no cover - network timing sensitive
            errors.append(f"GET {path}: {e}")
            return 0, ""

    # Probe a few minimal endpoints
    c_health, b_health = _get("/health")
    c_plugins, b_plugins = _get("/api/plugins")
    c_metrics, b_metrics = _get("/metrics")
    # Stop server
    with contextlib.suppress(Exception):
        server.stop_server()

    ok = (c_health == 200) and (c_plugins == 200) and (c_metrics == 200)
    details = {
        "health": c_health,
        "plugins": c_plugins,
        "metrics": c_metrics,
    }
    if not ok and not errors:
        # add brief summaries to help debugging
        errors = [
            f"/health={c_health}",
            f"/api/plugins={c_plugins}",
            f"/metrics={c_metrics}",
        ]
    return {
        "ok": ok,
        "notes": "Hub HTTP probe (health, plugins, metrics)",
        "port": p,
        "details": details,
        "errors": errors,
    }


def check_capability_policies_and_deny_defaults() -> Dict:
    """Instantiate AgentFabric with a stub registry and verify policies.

    - Executor denied in headless/safe, allowed in full
    - Retriever denied in safe
    - Summarizer allowed across modes
    - Unknown capability defaults to deny
    - read_only respects AAR_* env
    """
    import asyncio as _a
    from types import SimpleNamespace

    class _StubReg:
        def __init__(self):
            self.svcs = {}

        async def register_service(self, name, inst, metadata=None):
            self.svcs[name] = SimpleNamespace(instance=inst, metadata=metadata)

        def get_service(self, name):
            return None

        async def send_message(self, *args, **kwargs):
            return None

        async def update_heartbeat(self, *args, **kwargs):
            return None

    def _run_and_check(env: Dict[str, str]) -> Dict[str, bool | str]:
        # Snapshot and apply env
        saved = {k: os.environ.get(k) for k in env.keys()}
        try:
            for k, v in env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            from aetherra_agent_fabric import AgentFabric

            reg = _StubReg()

            async def _start():
                fab = AgentFabric(reg)
                await fab.start()
                return fab

            fab = _a.run(_start())
            # Checks
            g = fab.gate
            ret = {
                "executor_execute": g.check("agent.executor", "execute"),
                "retriever_retrieve": g.check("agent.retriever", "retrieve"),
                "summarizer_summarize": g.check("agent.summarizer", "summarize"),
                "unknown_cap": g.check("agent.executor", "definitely_unknown"),
                "read_only": bool(getattr(fab, "read_only", False)),
                "mode": str(getattr(fab, "mode", "")),
            }
            # Cleanup agents
            _a.run(fab.shutdown())
            return ret
        finally:
            # restore env
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    # Matrix
    res_full = _run_and_check({"AAR_MODE": "full", "AAR_READ_ONLY": "0"})
    res_headless = _run_and_check({"AAR_MODE": "headless", "AAR_READ_ONLY": "0"})
    res_safe = _run_and_check({"AAR_MODE": "safe", "AAR_READ_ONLY": "0"})
    # Read-only override
    res_ro = _run_and_check({"AAR_MODE": "headless", "AAR_READ_ONLY": "1"})
    # Local writes allowed in headless disables read_only
    res_headless_w = _run_and_check(
        {"AAR_MODE": "headless", "AAR_ALLOW_LOCAL_WRITES": "1", "AAR_READ_ONLY": "0"}
    )

    ok = (
        res_full["executor_execute"] is True
        and res_headless["executor_execute"] is False
        and res_safe["executor_execute"] is False
        and res_safe["retriever_retrieve"] is False
        and res_headless["summarizer_summarize"] is True
        and res_full["summarizer_summarize"] is True
        and res_headless["unknown_cap"] is False
        and res_ro["read_only"] is True
        and res_headless_w["read_only"] is False
    )

    return {
        "ok": ok,
        "notes": "Capability profiles across modes + deny-by-default verified",
        "matrix": {
            "full": res_full,
            "headless": res_headless,
            "safe": res_safe,
            "read_only_override": res_ro,
            "headless_allow_writes": res_headless_w,
        },
    }


def check_hmr_env_behavior() -> Dict:
    saved = {
        k: os.environ.get(k)
        for k in (
            "AETHERRA_HMR_ALLOWED_SOURCES",
            "AETHERRA_HMR_AUDIT_PATH",
            "AETHERRA_HMR_AUDIT_MAX_BYTES",
            "AETHERRA_HMR_AUDIT_MAX_BACKUPS",
        )
    }
    try:
        os.environ["AETHERRA_HMR_ALLOWED_SOURCES"] = "foo,bar/baz"
        os.environ["AETHERRA_HMR_AUDIT_PATH"] = ".aetherra/hmr_test.jsonl"
        os.environ["AETHERRA_HMR_AUDIT_MAX_BYTES"] = "12345"
        os.environ["AETHERRA_HMR_AUDIT_MAX_BACKUPS"] = "7"

        # Build a lightweight mock kernel compatible with controller expectations
        class _K:
            def get_status(self):
                return {"running": True}

        # Registry not used by ctor
        from aetherra_hmr_controller import HMRController

        ctrl = HMRController(registry=object(), kernel=_K(), strict=False)
        ok = (
            "foo" in ctrl.allowed_sources
            and ctrl.audit_path.endswith("hmr_test.jsonl")
            and int(ctrl.audit_max_bytes) == 12345
            and int(ctrl.audit_max_backups) == 7
        )
        return {
            "ok": ok,
            "notes": "HMR env flags parsed into controller",
            "allowed_sources": sorted(list(ctrl.allowed_sources)),
            "audit_path": ctrl.audit_path,
            "audit_max_bytes": int(ctrl.audit_max_bytes),
            "audit_max_backups": int(ctrl.audit_max_backups),
        }
    except Exception as e:  # pragma: no cover - defensive
        return {"ok": False, "errors": [str(e)]}
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Verify Architecture Map alignment")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero on any FAIL")
    ap.add_argument(
        "--probe-hub",
        action="store_true",
        help="Start Hub on a temp port and verify minimal API endpoints",
    )
    args = ap.parse_args(argv)

    checks = [
        ("Kernel", check_kernel()),
        ("Engine", check_engine()),
        ("Agents", check_agents()),
        ("Memory", check_memory()),
        ("Chat", check_chat()),
        ("Security", check_security()),
        ("Docs", check_docs_alignment()),
        ("Env", check_env_flags()),
    ]

    # Behavior checks
    checks.append(("Policies", check_capability_policies_and_deny_defaults()))
    checks.append(("HMR", check_hmr_env_behavior()))
    if args.probe_hub or os.getenv("ARCH_PROBE_HUB", "0") == "1":
        checks.append(("HubAPI", check_hub_minimal_api_probe()))

    print(
        "[ARCH] Aetherra OS Architecture Map Conformance\n--------------------------------------------"
    )
    fails = 0
    for name, res in checks:
        status = "PASS" if res.get("ok") else "FAIL"
        print(f"{name:8} : {status}")
        # Compact hints
        for key in ("missing", "errors"):
            vals = res.get(key) or []
            if vals:
                if isinstance(vals, list):
                    for v in vals[:3]:
                        print(f"  - {v}")
                else:
                    print(f"  - {vals}")
        if not res.get("ok"):
            fails += 1

    # Simple guidance
    if fails:
        print(
            f"\n[ARCH] Result: {fails} section(s) need attention. Use --strict to fail CI."
        )
    else:
        print("\n[ARCH] Result: All core sections present.")

    return 1 if (args.strict and fails) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
