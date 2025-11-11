#!/usr/bin/env python3
"""Unified Aetherra Stack Starter
=================================
Starts the full local Aetherra stack (Registry Daemon + Hub + OS) with one command.

Behavior:
 1. Ensures a local registry daemon is running (127.0.0.1:3030 by default)
 2. Starts Hub (AI API) with production/profile aware defaults if not reachable
 3. Launches the OS launcher (full mode) once dependencies pass health checks
 4. Streams concise progress logs; exits with OS process code.

Environment overrides (optional):
  AETHERRA_PROFILE=prod|test|dev
  AETHERRA_REGISTRY_URL=http://127.0.0.1:3030
  AETHERRA_HUB_URL=http://127.0.0.1:3012 (desired port; auto-fix if busy)

Usage:
  python start_aetherra_stack.py

"""

from __future__ import annotations

import asyncio
import os
import sys

REG_DEFAULT = "http://127.0.0.1:3030"
HUB_DEFAULT = "http://127.0.0.1:3012"


async def reachable(url: str, path: str) -> bool:
    try:
        import aiohttp  # type: ignore

        timeout = aiohttp.ClientTimeout(total=1.5)
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.get(url.rstrip("/") + path) as r,
        ):
            return r.status == 200
    except Exception:
        return False


def parse_port(url: str) -> int:
    try:
        from urllib.parse import urlparse

        p = urlparse(url)
        return p.port or (3012 if "hub" in url else 3030)
    except Exception:
        return 3012


async def ensure_registry(reg_url: str) -> None:
    if await reachable(reg_url, "/api/registry/status"):
        print(f"[STACK] Registry already running @ {reg_url}")
        return
    host_port = parse_port(reg_url)
    print(f"[STACK] Starting Registry Daemon @ {reg_url} ...")
    script = os.path.join(os.getcwd(), "aetherra_registry_daemon.py")
    await asyncio.create_subprocess_exec(
        sys.executable,
        script,
        "--host",
        "127.0.0.1",
        "--port",
        str(host_port),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    # Wait for readiness (max ~3s)
    for _ in range(15):
        if await reachable(reg_url, "/api/registry/status"):
            print("[STACK] Registry ready")
            return
        await asyncio.sleep(0.2)
    print(
        "[STACK][WARN] Registry did not respond; proceeding (in-process fallback will operate)"
    )


async def ensure_hub(hub_url: str) -> str:
    if await reachable(hub_url, "/api/ping"):
        print(f"[STACK] Hub already running @ {hub_url}")
        return hub_url
    desired_port = parse_port(hub_url)
    # Auto-pick next free port if busy
    import socket

    def port_busy(p: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(("127.0.0.1", p)) == 0

    chosen = desired_port
    if port_busy(desired_port):
        for cand in range(desired_port, desired_port + 20):
            if not port_busy(cand):
                chosen = cand
                break
        if chosen != desired_port:
            print(f"[STACK] Desired hub port {desired_port} busy; using {chosen}")
    print(f"[STACK] Starting Hub @ http://127.0.0.1:{chosen} ...")
    script = os.path.join(os.getcwd(), "tools", "run_hub_ai_api.py")
    # Minimal production hardening escalation if token present
    if os.environ.get("AETHERRA_AI_API_TOKEN"):
        os.environ.setdefault("AETHERRA_AI_API_REQUIRE_TOKEN", "1")
    await asyncio.create_subprocess_exec(
        sys.executable,
        script,
        "--port",
        str(chosen),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    hub_effective = f"http://127.0.0.1:{chosen}"
    os.environ["AETHERRA_HUB_URL"] = hub_effective
    # Wait for /api/ping (max ~4s)
    for _ in range(20):
        if await reachable(hub_effective, "/api/ping"):
            print("[STACK] Hub ready")
            return hub_effective
        await asyncio.sleep(0.2)
    print(
        "[STACK][WARN] Hub did not respond to /api/ping; continuing (launcher will attempt built-in start)"
    )
    return hub_effective


async def launch_os() -> int:
    print("[STACK] Launching Aetherra OS (full mode)...")
    script = os.path.join(os.getcwd(), "aetherra_os_launcher.py")
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        script,
        "--mode",
        "full",
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return await proc.wait()


async def main() -> int:
    os.environ.setdefault("AETHERRA_REGISTRY_URL", REG_DEFAULT)
    os.environ.setdefault("AETHERRA_HUB_URL", HUB_DEFAULT)
    reg_url = os.environ["AETHERRA_REGISTRY_URL"]
    hub_url = os.environ["AETHERRA_HUB_URL"]
    print("[STACK] One-command startup initializing...")
    await ensure_registry(reg_url)
    # Ensure hub reachable (result stored in env already by ensure_hub)
    await ensure_hub(hub_url)
    # Small grace to reduce race conditions for plugin discovery
    await asyncio.sleep(0.5)
    code = await launch_os()
    print(f"[STACK] OS exited with code {code}")
    return code


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n[STACK] Interrupted by user")
        raise SystemExit(130) from None
