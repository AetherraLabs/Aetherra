#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Verify Aetherra OS Architecture Map (v1.x) conformance
------------------------------------------------------
Checks for the presence of core components, modules, and contracts referenced
in docs/aetherra_os_architecture_map_v_1.md and prints a compact PASS/FAIL report.
Can optionally perform light runtime probes (Hub HTTP endpoints) and validate
Security capability policies + env/HMR flags behavior.

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

# Standard library imports
import argparse
import contextlib
import http.client
import importlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _exists(path: str) -> bool:
    return Path(path).exists()


def _try_import(name: str) -> tuple[bool, str | None]:
    try:
        importlib.import_module(name)
        return True, None
    except Exception as e:
        return False, str(e)


def check_kernel() -> dict:
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


def check_engine() -> dict:
    # Prefer modern engine module path; fall back to legacy markers
    candidates = [
        ("Aetherra.aetherra_core.engine.aetherra_engine", True),
        ("aetherra_core_analyzer", False),
    ]
    ok_any = False
    errors: list[str] = []
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


def check_agents() -> dict:
    # Support both orchestrator and OS-level Agent Fabric
    canonical = "Aetherra.aetherra_core.agents.agent_orchestrator"
    shim = "Aetherra.aetherra_core.orchestration.agent_orchestrator"
    mods = [canonical, "aetherra_agent_fabric", shim]
    ok = False
    errors: list[str] = []
    found: list[str] = []
    for m in mods:
        good, err = _try_import(m)
        if good:
            ok = True
            found.append(m)
        else:
            errors.append(f"{m}: {err}")
    # Prefer canonical path; mark ok only if canonical or fabric present
    ok = any(x in found for x in (canonical, "aetherra_agent_fabric"))
    return {
        "ok": ok,
        "found": found,
        "notes": "Agent orchestrator/fabric available (canonical under aetherra_core.agents)",
        "errors": [] if ok else errors,
    }


def check_memory() -> dict:
    mods = [
        "Aetherra.aetherra_core.memory.quantum_memory_integration",
        "Aetherra.aetherra_core.memory.lyrixa_memory_engine",
        "Aetherra.aetherra_core.memory.quantum_memory_engine",
    ]
    ok_any = False
    errors: list[str] = []
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


def check_chat() -> dict:
    """Validate hub compatibility layer + Lyrixa chat service.

    The monolithic aetherra_hub_server.py file is deprecated; we now rely on
    aetherra_hub.compat (create_app-based implementation). Pass if compat imports
    and Lyrixa chat service import both succeed.
    """
    compat_ok, compat_err = _try_import("aetherra_hub.compat")
    chat_ok, chat_err = _try_import("Aetherra.lyrixa.chat.lyrixa_chat_service")
    ok = compat_ok and chat_ok
    errors: list[str] = []
    if not compat_ok:
        errors.append(f"compat import failed: {compat_err}")
    if not chat_ok:
        errors.append(f"chat import failed: {chat_err}")
    return {
        "ok": ok,
        "present": ["aetherra_hub.compat" if compat_ok else "(missing)"],
        "notes": "Hub compat + Lyrixa chat service import",
        "errors": errors,
    }


def check_security() -> dict:
    mods = [
        "Aetherra.security.plugin_signing",
        "Aetherra.security.sandbox",
        "Aetherra.security.prompt_defense",
    ]
    ok_all = True
    errors: list[str] = []
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


def check_docs_alignment() -> dict:
    ok = _exists("docs/aetherra_os_architecture_map_v_1.md")
    return {
        "ok": ok,
        "notes": "Architecture map present",
        "path": "docs/aetherra_os_architecture_map_v_1.md",
    }


def check_env_flags() -> dict:
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


def check_hub_minimal_api_probe(port: int | None = None, timeout: float = 1.5) -> dict:
    try:
        # Aetherra imports
        from aetherra_hub.compat import AetherraHubServer  # updated to compat layer
    except Exception as e:
        return {
            "ok": False,
            "errors": [f"import hub compat failed: {e}"],
            "notes": "Flask or dependencies may be missing; install to enable probe",
        }

    errors: list[str] = []
    p = port or _find_free_port()
    server = AetherraHubServer(p)
    started = bool(server.start_server())
    if not started:
        return {"ok": False, "errors": ["hub failed to start"], "port": p}
    # Give it a brief moment
    time.sleep(0.2)

    def _get(path: str) -> tuple[int, str]:
        connection = http.client.HTTPConnection("localhost", p, timeout=timeout)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            code = int(response.status)
            ctype = str(response.getheader("Content-Type", ""))
            body = response.read().decode("utf-8", errors="replace")
            return code, ctype + "\n" + body[:200]
        except Exception as error:  # pragma: no cover - network timing sensitive
            errors.append(f"GET {path}: {type(error).__name__}")
            return 0, ""
        finally:
            connection.close()

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


def check_capability_policies_and_deny_defaults() -> dict:
    """Verify the active capability API using isolated child-process policies."""
    probe = """
import json
from Aetherra.security.capabilities import check_capability, has_capability
print(json.dumps({
    "allowed": has_capability("architecture:principal", "agent:read"),
    "ungranted": has_capability("architecture:principal", "agent:execute_task"),
    "unknown_principal": check_capability("architecture:unknown", "agent:read"),
}))
"""
    cases = {
        "strict_dev": ("dev", "1", "valid"),
        "production": ("prod", "0", "valid"),
        "production_alias": ("production", "0", "valid"),
        "missing_policy": ("prod", "0", "missing"),
        "malformed_policy": ("prod", "0", "malformed"),
    }
    matrix = {}
    root = Path(__file__).resolve().parents[1]
    try:
        with tempfile.TemporaryDirectory(prefix="aetherra-policy-probe-") as scratch:
            for name, (profile, strict, policy_kind) in cases.items():
                policy_home = Path(scratch) / name
                policy_home.mkdir()
                policy = policy_home / "capabilities.json"
                if policy_kind == "valid":
                    policy.write_text(
                        json.dumps(
                            {"allow": {"architecture:principal": ["agent:read"]}}
                        ),
                        encoding="utf-8",
                    )
                elif policy_kind == "malformed":
                    policy.write_text("{", encoding="utf-8")
                env = {
                    key: value
                    for key, value in os.environ.items()
                    if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP"}
                }
                env.update(
                    {
                        "AETHERRA_PROFILE": profile,
                        "AETHERRA_REQUIRE_CAPABILITIES": strict,
                        "AETHERRA_PROD_UNSAFE_ALLOW": "0",
                        "AETHERRA_POLICY_HOME": str(policy_home),
                        "PYTHONIOENCODING": "utf-8",
                    }
                )
                result = subprocess.run(
                    [sys.executable, "-c", probe],
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=15,
                    check=False,
                )
                if result.returncode:
                    raise ValueError("policy_probe_failed")
                actual = json.loads(result.stdout)
                expected = {
                    "allowed": policy_kind == "valid",
                    "ungranted": False,
                    "unknown_principal": False,
                }
                if not isinstance(actual, dict) or set(actual) != set(expected):
                    raise ValueError("policy_probe_invalid")
                if any(type(value) is not bool for value in actual.values()):
                    raise ValueError("policy_probe_invalid")
                matrix[name] = actual
                if actual != expected:
                    return {
                        "ok": False,
                        "matrix": matrix,
                        "errors": ["capability_policy_contract_mismatch"],
                    }
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {
            "ok": False,
            "matrix": matrix,
            "errors": ["capability_policy_probe_failed"],
        }
    return {
        "ok": True,
        "matrix": matrix,
        "notes": "Explicit grants and strict default denial verified via Security API",
    }


def check_hmr_env_behavior() -> dict:
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
        # Aetherra imports
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
            "allowed_sources": sorted(ctrl.allowed_sources),
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


def main(argv: list[str]) -> int:
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
