#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Lyrixa Diagnostics Utility

Checks health and wiring of Lyrixa subsystems after recent changes:
 - Aetherra OS / Hub availability (port 3001)
 - Service Registry connectivity
 - Persistent Memory availability
 - Basic Chat system responsiveness
 - Workspace Tools (scan + suggest)
 - Optional advanced Lyrixa Chat Service initialization

Usage:
  python tools/lyrixa_diagnostics.py [--verbose] [--skip-advanced]

Exit codes:
  0 = All critical checks passed (chat usable)
  1 = Critical failure (chat unusable or OS missing)
  2 = Partial degradation (chat basic only, advanced features unavailable)
"""

from __future__ import annotations

# Standard library imports
import asyncio
import os
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


@dataclass
class CheckResult:
    name: str
    status: str  # PASS | FAIL | WARN | SKIP
    detail: str = ""
    duration_ms: int = 0


@dataclass
class DiagnosticsReport:
    critical_pass: bool
    degraded: bool
    results: Dict[str, CheckResult]
    summary: str


async def check_port(host: str, port: int, timeout: float = 1.5) -> bool:
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False
    finally:
        _ = (time.time() - start) * 1000


async def run_checks(
    verbose: bool = False, skip_advanced: bool = False
) -> DiagnosticsReport:
    results: Dict[str, CheckResult] = {}

    async def record(name: str, coro, critical: bool = False, warn_only: bool = False):
        start = time.time()
        try:
            value = await coro
            if (
                isinstance(value, tuple)
                and len(value) == 2
                and isinstance(value[0], bool)
            ):
                ok, detail = value
            else:
                ok, detail = bool(value), str(value)
            status = "PASS" if ok else ("WARN" if warn_only else "FAIL")
            results[name] = CheckResult(
                name=name,
                status=status,
                detail=detail,
                duration_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            status = "FAIL" if critical else ("WARN" if not warn_only else "WARN")
            results[name] = CheckResult(
                name=name,
                status=status,
                detail=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )

    # 1. Hub / OS check
    async def hub_check():
        ok = await check_port("localhost", 3001)
        return ok, "Hub reachable on :3001" if ok else "Hub not reachable"

    await record("os_hub", hub_check(), critical=True)

    # 2. Service registry
    async def registry_check():
        try:
            # Aetherra imports
            from aetherra_service_registry import get_service_registry  # type: ignore

            reg = await get_service_registry()
            if not reg:
                return False, "registry unavailable"
            services = reg.list_services()
            return (len(services) >= 1), f"services={len(services)}"
        except Exception as e:
            return False, f"error: {e}"  # degrade

    await record("service_registry", registry_check(), critical=False)

    # 3. Persistent memory
    async def memory_check():
        try:
            # Aetherra imports
            from aetherra_persistent_memory import (  # type: ignore
                get_persistent_memory_system,
            )

            mem = await get_persistent_memory_system()
            if not mem:
                return False, "persistent memory not available"
            # light call
            total = len(getattr(mem, "memories", {}))
            return True, f"memories={total}"
        except Exception as e:
            return False, f"error: {e}"

    await record("persistent_memory", memory_check(), warn_only=True)

    # 4. Basic assistant initialize
    async def basic_chat_check():
        # Fast path: if no real API key present, skip heavy init to keep contract test fast
        placeholder = os.getenv("OPENAI_API_KEY", "")
        if not placeholder or placeholder.startswith("__"):
            return False, "assistant init disabled(no-api)"
        # Aetherra imports
        from Aetherra.lyrixa.lyrixa_basic import LyrixaBasicAssistant  # type: ignore

        assistant = LyrixaBasicAssistant()
        ok = await assistant.initialize()
        if not ok:
            return False, "assistant init failed"
        if not assistant.ai_chat_system:
            return False, "chat system missing"
        try:
            resp = await assistant.ai_chat_system.send_message("hello")  # type: ignore
            truncated = (
                (resp[:120] + "...")
                if isinstance(resp, str) and len(resp) > 120
                else str(resp)
            )
            return True, f"chat ok: {truncated}"
        except Exception as e:
            return False, f"chat error: {e}"

    await record("basic_chat", basic_chat_check(), critical=True)

    # 5. Workspace tools (indirect chat service pieces)
    async def workspace_tools_check():
        try:
            placeholder = os.getenv("OPENAI_API_KEY", "")
            if not placeholder or placeholder.startswith("__"):
                return False, "assistant init disabled(no-api)"
            # Aetherra imports
            from Aetherra.lyrixa.lyrixa_basic import (  # type: ignore
                LyrixaBasicAssistant,
            )

            assistant = LyrixaBasicAssistant()
            ok = await assistant.initialize()
            if not ok:
                return False, "assistant init failed"
            if not assistant.workspace_tools:
                return False, "workspace tools missing"
            summary = await assistant.workspace_tools.scan()
            return True, f"summary: py={summary.get('total_py_files')}"
        except Exception as e:
            return False, f"error: {e}"

    await record("workspace_tools", workspace_tools_check(), warn_only=True)

    # 6. Advanced Chat Service (optional)
    if skip_advanced:
        results["advanced_chat_service"] = CheckResult(
            name="advanced_chat_service",
            status="SKIP",
            detail="skipped by flag",
            duration_ms=0,
        )
    else:

        async def advanced_chat_check():
            try:
                # Aetherra imports
                from Aetherra.lyrixa.chat.lyrixa_chat_service import (  # type: ignore
                    ChatOptions,
                    LyrixaChatService,
                )

                svc = LyrixaChatService(workspace_root=ROOT)
                await svc.initialize()
                resp = await svc.chat("status?", ChatOptions())
                text = getattr(resp, "text", "<no text>")
                return True, f"advanced chat ok: {text[:80]}" if text else "no text"
            except Exception as e:
                return False, f"error: {e}"

        await record("advanced_chat_service", advanced_chat_check(), warn_only=True)

    # 7. Intelligence capability reinforcement check
    async def intelligence_capabilities_check():
        try:
            # Aetherra imports
            from Aetherra.lyrixa.intelligence.lyrixa_full_intelligence import (  # type: ignore
                LyrixaIntelligenceCore,
            )

            core = LyrixaIntelligenceCore()
            # Force run provider init cheaply (may no-op if keys absent)
            try:
                await core.initialize_providers()
            except Exception:
                pass
            required = [
                "memory_integration",
                "emotional_modeling",
                "learning_enabled",
            ]
            missing = [k for k in required if not core.config.get(k, True)]
            if missing:
                return False, f"disabled: {','.join(missing)}"
            return True, "all-enabled"
        except Exception as e:
            return False, f"error: {e}"

    await record(
        "intelligence_capabilities", intelligence_capabilities_check(), warn_only=True
    )

    # Determine overall status
    # Downgrade an empty service registry to WARN (non-critical) if OS hub is reachable
    if (
        "service_registry" in results
        and results["service_registry"].status == "FAIL"
        and "os_hub" in results
        and results["os_hub"].status == "PASS"
        and "services=0" in (results["service_registry"].detail or "")
    ):
        results["service_registry"].status = "WARN"
        results["service_registry"].detail += " (treated as non-critical)"

    # If the OS hub is reachable but we're in a separate process (so the local import
    # created a fresh, empty registry) and advanced or basic chat succeeded, upgrade
    # the service_registry status to PASS to avoid misleading degradation. This helps
    # when the full Aetherra OS is already running in another terminal.
    if (
        "service_registry" in results
        and results["service_registry"].status in {"WARN", "FAIL"}
        and "services=0" in (results["service_registry"].detail or "")
        and results.get("os_hub")
        and results["os_hub"].status == "PASS"
        and (
            (
                "advanced_chat_service" in results
                and results["advanced_chat_service"].status == "PASS"
            )
            or ("basic_chat" in results and results["basic_chat"].status == "PASS")
        )
    ):
        results["service_registry"].status = "PASS"
        if "external process" not in results["service_registry"].detail:
            results["service_registry"].detail += " (external process)"

    critical_pass = all(
        r.status == "PASS" for k, r in results.items() if k in {"os_hub", "basic_chat"}
    )
    degraded = (
        any(
            r.status in {"WARN", "FAIL"}
            for k, r in results.items()
            if k not in {"os_hub", "basic_chat"}
        )
        and critical_pass
    )

    summary_lines = []
    for r in results.values():
        summary_lines.append(f"{r.name:22s} {r.status:4s} {r.detail}")
    summary = "\n".join(summary_lines)

    return DiagnosticsReport(
        critical_pass=critical_pass, degraded=degraded, results=results, summary=summary
    )


SCHEMA_VERSION = "1.0"


def _ordered(obj):
    """Return a structure with deterministic key ordering for JSON emission."""
    if isinstance(obj, dict):
        return {k: _ordered(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [_ordered(x) for x in obj]
    return obj


async def main():
    # Standard library imports
    import argparse

    parser = argparse.ArgumentParser(description="Lyrixa diagnostics")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--skip-advanced", action="store_true")
    parser.add_argument(
        "--json", action="store_true", help="Emit deterministic JSON schema output"
    )
    args = parser.parse_args()

    # In JSON mode, suppress any third-party initialization prints by capturing stdout early
    if args.json:
        # Standard library imports
        import logging
        from io import StringIO

        # Suppress noisy provider warnings in JSON mode by providing dummy keys if unset
        for env_key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "AZURE_OPENAI_KEY"]:
            os.environ.setdefault(env_key, "__disabled__")

        # Redirect logging to stderr to prevent JSON contamination
        logging.basicConfig(level=logging.WARNING, stream=sys.stderr, force=True)

        real_stdout = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer  # type: ignore
        try:
            report = await run_checks(
                verbose=args.verbose, skip_advanced=args.skip_advanced
            )
        finally:
            sys.stdout = real_stdout  # type: ignore
            _ = buffer.getvalue()  # intentionally discarded
    else:
        report = await run_checks(
            verbose=args.verbose, skip_advanced=args.skip_advanced
        )
    if args.json:
        # Convert to deterministic JSON structure
        results_struct = {}
        for name, res in report.results.items():
            results_struct[name] = {
                "status": res.status,
                "detail": res.detail,
                "duration_ms": res.duration_ms,
            }
        # Deterministic summary lines: sorted by result name (mirrors test contract expectation)
        summary_lines = [
            f"{name:22s} {results_struct[name]['status']:4s} {results_struct[name]['detail']}"
            for name in sorted(results_struct)
        ]
        payload = {
            "schema": "lyrixa.diagnostics",
            "schema_version": SCHEMA_VERSION,
            "critical_pass": report.critical_pass,
            "degraded": report.degraded,
            "results": results_struct,
            "summary_lines": summary_lines,
        }
        # Standard library imports
        import json as _json

        # Ensure nothing else polluted stdout (warnings may have been printed earlier)
        # If environment warnings are printed before import (e.g., missing API keys),
        # they can appear before JSON and break contract. Best-effort mitigation: if
        # stdout already contains lines starting with '[Warning]' we move them to stderr.
        # (Since we're now at emission point, we can only prevent future prints.)
        # Flush only pure JSON (strip any prior warning lines captured by wrappers).
        doc = _json.dumps(_ordered(payload), indent=2, sort_keys=False)
        # Discard captured_pre_json (debug: could be logged to stderr if needed)
        print(doc)
        if report.critical_pass and not report.degraded:
            return 0
        if report.critical_pass and report.degraded:
            return 2
        return 1
    else:
        print("=== Lyrixa Diagnostics ===")
        print(report.summary)
        if report.critical_pass and not report.degraded:
            print("\nStatus: ALL CRITICAL SYSTEMS PASS ✅")
            return 0
        if report.critical_pass and report.degraded:
            print("\nStatus: DEGRADED (non-critical components failed) ⚠️")
            return 2
        print("\nStatus: CRITICAL FAILURE ❌")
        return 1


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
    except KeyboardInterrupt:
        code = 130
    sys.exit(code)
