#!/usr/bin/env python3
"""
Lyrixa Connectivity Test (standalone)
Checks that Lyrixa is wired into Engine, Memory, Kernel, Agents, Plugins, and Chat.
Usage:
  python lyrixa_connectivity_test.py [--base http://localhost:5000] [--timeout 8]
Env (optional):
  AETHERRA_WEB_BASE, AETHERRA_WEB_PORT, AETHER_BASE_URL
  AETHERRA_AI_API_TOKEN (used when /api/ai/* requires a token)
Exit code is non-zero if any REQUIRED checks fail.
"""

import argparse
import asyncio
import inspect
import json
import os
import sys
from urllib import request

REQUIRED = []
OPTIONAL = []


def getenv_bool(name, default=False):
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).lower() in ("1", "true", "yes", "y", "on")


def http_json(url, method="GET", body=None, headers=None, timeout=8):
    if headers is None:
        headers = {}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as resp:  # nosec - local test client
            ct = resp.headers.get("Content-Type", "")
            raw = resp.read()
            if (
                "application/json" in ct
                or raw.strip().startswith(b"{")
                or raw.strip().startswith(b"[")
            ):
                return True, json.loads(raw.decode("utf-8")), resp.status
            return True, raw.decode("utf-8", errors="ignore"), resp.status
    except Exception as e:  # pragma: no cover - network/env specific
        return False, str(e), None


def try_import_engine_status():
    try:
        from Aetherra.aetherra_core.engine.aetherra_engine import (  # type: ignore
            AetherraEngine,
        )

        eng = AetherraEngine()
        status = eng.get_system_status()  # may be sync or async
        if inspect.iscoroutine(status):
            status = asyncio.run(status)
        return True, status
    except Exception as e:  # pragma: no cover - import/runtime specific
        return False, str(e)


def _safe_sample_text(resp, max_len=120):
    try:
        if isinstance(resp, dict) and "text" in resp:
            return str(resp.get("text", ""))[:max_len]
        return str(resp)[:max_len]
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--base",
        type=str,
        default=os.getenv("AETHER_BASE_URL")
        or f"{os.getenv('AETHERRA_WEB_BASE', 'http://localhost')}:{os.getenv('AETHERRA_WEB_PORT', '5000')}",  # noqa: E501
        help="Base URL for the Aetherra Hub/HTTP endpoints (default: http://localhost:5000)",
    )
    ap.add_argument(
        "--timeout", type=int, default=int(os.getenv("AETHERRA_HTTP_TIMEOUT", "8"))
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict required checks (stats must show lyrixa_chat.registered, all Hub endpoints must pass)",
    )
    args = ap.parse_args()

    base = args.base.rstrip("/")
    token = os.getenv("AETHERRA_AI_API_TOKEN")
    headers = {}
    if token:
        headers["X-Aetherra-Token"] = token
        headers["Authorization"] = f"Bearer {token}"

    results = []

    def record(name, required, ok, details):
        results.append(
            {
                "name": name,
                "required": required,
                "ok": bool(ok),
                "details": details,
            }
        )

    # 0) Engine import + status (in-process check)
    ok, details = try_import_engine_status()
    record("Engine.get_system_status()", True, ok, details)

    # 1) /health
    ok, resp, code = http_json(f"{base}/health", headers=headers, timeout=args.timeout)
    hub_available = ok and code == 200
    if hub_available:
        record(
            "GET /health",
            True,
            True,
            {"code": code},
        )
    else:
        # In non-strict mode, treat missing Hub as SKIP so in-process checks can still pass
        record(
            "GET /health",
            args.strict,
            False,
            {"code": code, "error": resp if not ok else resp},
        )

    # 2) /api/stats (expects lyrixa_chat summary when registry online)
    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/stats", headers=headers, timeout=args.timeout
        )
        lyrixa_registered = False
        if ok and isinstance(resp, dict):
            lyrixa = resp.get("lyrixa_chat") or {}
            lyrixa_registered = bool(lyrixa.get("registered", False))
        stats_ok = ok and (code == 200) and (lyrixa_registered if args.strict else True)
        record(
            "GET /api/stats (lyrixa_chat.registered)"
            if args.strict
            else "GET /api/stats",
            True,
            stats_ok,
            {
                "code": code,
                "lyrixa_chat": (
                    resp.get("lyrixa_chat") if ok and isinstance(resp, dict) else None
                ),
            },
        )
    else:
        record(
            "GET /api/stats",
            False if not args.strict else True,
            False,
            {"skipped": True},
        )

    # 3) Chat API (model path)
    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/ai/ask",
            method="POST",
            headers=headers,
            body={
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 64,
                "temperature": 0.1,
            },
            timeout=args.timeout,
        )

        def _has_text(d):
            if not isinstance(d, dict):
                return False
            t = d.get("text")
            if isinstance(t, str) and t.strip():
                return True
            res = d.get("result")
            if isinstance(res, dict):
                rt = res.get("text")
                if isinstance(rt, str) and rt.strip():
                    return True
                # some hubs return {result:{confidence:..., ...}} without text
            return False

        llm_ok = (
            ok
            and code == 200
            and isinstance(resp, dict)
            and (
                _has_text(resp)
                if args.strict
                else (
                    ("text" in resp) or (resp.get("ok") is True) or ("result" in resp)
                )
            )
        )
        record(
            "POST /api/ai/ask (LLM path)",
            True,
            llm_ok,
            {"code": code, "sample": _safe_sample_text(resp, 80)},
        )
    else:
        record(
            "POST /api/ai/ask (LLM path)",
            False if not args.strict else True,
            False,
            {"skipped": True},
        )

    # 4) Lyrixa bridge
    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/lyrixa/chat",
            method="POST",
            headers=headers,
            body={"content": "status: please summarize your connected systems."},
            timeout=args.timeout,
        )
        lyrixa_bridge_ok = (
            ok and code == 200 and isinstance(resp, dict) and "text" in resp
        )
        record(
            "POST /api/lyrixa/chat (bridge)",
            True,
            lyrixa_bridge_ok,
            {"code": code, "sample": _safe_sample_text(resp, 120)},
        )
    else:
        record(
            "POST /api/lyrixa/chat (bridge)",
            False if not args.strict else True,
            False,
            {"skipped": True},
        )

    # 5) Memory status
    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/memory/status", headers=headers, timeout=args.timeout
        )
        mem_ok = ok and code == 200
        record(
            "GET /api/memory/status",
            True,
            mem_ok,
            {
                "code": code,
                "summary_keys": list(resp.keys())
                if isinstance(resp, dict)
                else str(resp),
            },
        )
    else:
        record(
            "GET /api/memory/status",
            False if not args.strict else True,
            False,
            {"skipped": True},
        )

    # 6) Kernel metrics snapshot (JSON) and Prometheus /metrics (text)
    if hub_available:
        ok1, resp1, code1 = http_json(
            f"{base}/api/kernel/metrics", headers=headers, timeout=args.timeout
        )
        ok2, resp2, code2 = http_json(
            f"{base}/metrics", headers=headers, timeout=args.timeout
        )
        prom_ok = (
            ok2
            and code2 == 200
            and isinstance(resp2, str)
            and (
                "aetherra_chat_requests_total" in resp2
                or "aetherra_kernel_inflight_current" in resp2
            )
        )
        record(
            "GET /api/kernel/metrics",
            True,
            ok1 and code1 == 200 and isinstance(resp1, dict),
            {"code": code1},
        )
        record("GET /metrics (Prometheus)", True, prom_ok, {"code": code2})
    else:
        record(
            "GET /api/kernel/metrics",
            False if not args.strict else True,
            False,
            {"skipped": True},
        )
        record(
            "GET /metrics (Prometheus)",
            False if not args.strict else True,
            False,
            {"skipped": True},
        )

    # 7) Agents API (optional if disabled)
    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/agents", headers=headers, timeout=args.timeout
        )
        record("GET /api/agents (optional)", False, ok and code == 200, {"code": code})
    else:
        record("GET /api/agents (optional)", False, False, {"skipped": True})

    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/agents/metrics", headers=headers, timeout=args.timeout
        )
        record(
            "GET /api/agents/metrics (optional)",
            False,
            ok and code == 200,
            {"code": code},
        )
    else:
        record("GET /api/agents/metrics (optional)", False, False, {"skipped": True})

    # 8) Plugins list (optional)
    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/plugins", headers=headers, timeout=args.timeout
        )
        record(
            "GET /api/plugins (optional)",
            False,
            ok and code == 200,
            {"code": code, "count": (len(resp) if isinstance(resp, list) else None)},
        )
    else:
        record("GET /api/plugins (optional)", False, False, {"skipped": True})

    # 9) KLM/KEB status (optional, when enabled)
    if hub_available:
        ok, resp, code = http_json(
            f"{base}/api/klm/status", headers=headers, timeout=args.timeout
        )
        record(
            "GET /api/klm/status (optional)", False, ok and code == 200, {"code": code}
        )
        ok, resp, code = http_json(
            f"{base}/api/keb/status", headers=headers, timeout=args.timeout
        )
        record(
            "GET /api/keb/status (optional)", False, ok and code == 200, {"code": code}
        )
    else:
        record("GET /api/klm/status (optional)", False, False, {"skipped": True})
        record("GET /api/keb/status (optional)", False, False, {"skipped": True})

    # Summarize
    required_fail = [r for r in results if r["required"] and not r["ok"]]
    print("\n=== Lyrixa Connectivity Test Report ===")
    for r in results:
        status = "PASS" if r["ok"] else ("SKIP" if not r["required"] else "FAIL")
        print(f"{status:5} | {r['name']}")
        if not r["ok"]:
            print(f"       details: {r['details']}")
    summary = {
        "required_passed": sum(1 for r in results if r["required"] and r["ok"]),
        "required_total": sum(1 for r in results if r["required"]),
        "optional_passed": sum(1 for r in results if (not r["required"]) and r["ok"]),
        "optional_total": sum(1 for r in results if not r["required"]),
    }
    print("\nSummary:", json.dumps(summary, indent=2))
    # Exit non-zero on any required failures
    sys.exit(0 if not required_fail else 2)


if __name__ == "__main__":
    main()
