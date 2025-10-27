#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Start Aetherra Hub with AI API enabled for local testing.

Usage:
  python tools/run_hub_ai_api.py --port 3012 [--require-token] [--token SECRET]

This sets in-process environment flags:
  AETHERRA_AI_API_ENABLED=1
  AETHERRA_AI_API_STREAM=1
  AETHERRA_AI_API_REQUIRE_TOKEN=0 or 1
  AETHERRA_AI_API_TOKEN=... (if provided)

Then starts the Hub on the given port and keeps it running.
"""

from __future__ import annotations

# Standard library imports
import argparse
import os
import sys
import threading
import time


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=3001)
    p.add_argument(
        "--auto-port",
        action="store_true",
        help="Auto-select next free port if requested port is busy",
    )
    p.add_argument("--require-token", action="store_true")
    p.add_argument("--token", default="")
    args = p.parse_args()

    # Desired flags for this run (store first; some loaders may override later)
    desired_flags = {
        "AETHERRA_AI_API_ENABLED": "1",
        "AETHERRA_AI_API_STREAM": "1",
        "AETHERRA_AI_API_REQUIRE_TOKEN": "1" if args.require_token else "0",
    }
    if args.token:
        desired_flags["AETHERRA_AI_API_TOKEN"] = args.token
    # Apply before imports
    os.environ.update(desired_flags)

    try:
        # Aetherra imports
        from aetherra_hub.app import create_app
    except Exception as e:
        print(f"[ERR] failed to import hub app: {e}")
        return 1

    # Re-apply after imports in case a .env loader overwrote them
    os.environ.update(desired_flags)

    app = create_app()

    # Port guard: avoid conflicts with other Hub instances or services
    def _port_in_use(port: int) -> bool:
        try:
            import socket

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.25)
                return s.connect_ex(("127.0.0.1", port)) == 0
        except Exception:
            # If we cannot check, assume not in use to avoid false negatives
            return False

    desired_port = int(args.port)
    if _port_in_use(desired_port):
        if args.auto_port or os.environ.get("AETHERRA_HUB_PORT_AUTOFIX", "0") == "1":
            # Try a small range to find an open port
            new_port = None
            for candidate in range(desired_port + 1, desired_port + 11):
                if not _port_in_use(candidate):
                    new_port = candidate
                    break
            if new_port is not None:
                print(f"[PORT] {desired_port} is busy; auto-selecting {new_port}")
                desired_port = new_port
            else:
                print(
                    f"[ERR] Requested port {desired_port} is busy and no free port found in +10 range"
                )
                return 2
        else:
            print(
                f"[ERR] Requested port {desired_port} is already in use. Use --auto-port or set AETHERRA_HUB_PORT_AUTOFIX=1 to auto-select."
            )
            return 2

    # Register required services so /api/selfinc/* and /api/ai/* work end-to-end
    # Standard library imports
    import asyncio

    class _DemoEngine:
        async def process_message(self, msg: str, ctx: dict) -> dict:
            text = f"Echo: {msg}"
            return {
                "result": {
                    "response": text
                    + "\n[demo-engine] Provide your own engine for real answers.",
                    "context": ctx or {},
                }
            }

    async def _register() -> None:
        # Import lazily inside task so failures are caught by the wrapper below
        # Aetherra imports
        from aetherra_self_incorporation import SelfIncorporationService
        from aetherra_service_registry import (
            ServiceStatus,
            get_service_registry,
            register_service,
            update_heartbeat,
        )

        # Register self-incorporation service for /api/selfinc/* endpoints
        await register_service("self_incorporation", SelfIncorporationService())
        # Register demo engine for /api/ai/* endpoints
        await register_service("aetherra_engine", _DemoEngine())

        # Register the Hub itself so supervisors can track it and avoid hub_link degradation
        class _HubService:
            def __init__(self, port: int):
                self.port = port
                self._running = True

            def is_alive(self) -> bool:  # registry may poll this
                return self._running

            def stop(self) -> None:
                self._running = False

        hub = _HubService(desired_port)
        await register_service(
            "aetherra_hub",
            hub,
            metadata={"port": desired_port, "self_heartbeat": True},
            dependencies=["aetherra_engine"],
        )
        try:
            reg = await get_service_registry()
            await reg.update_service_status("aetherra_hub", ServiceStatus.HEALTHY)
        except Exception:
            pass

        # Background self-heartbeat every 30s (daemon thread calling async API)
        def _hb_loop() -> None:
            while True:
                try:
                    asyncio.run(update_heartbeat("aetherra_hub"))
                except Exception:
                    pass
                time.sleep(30)

        threading.Thread(target=_hb_loop, daemon=True).start()

    try:
        asyncio.run(_register())
        print("[OK] Registered self_incorporation and demo engine in-process")
    except Exception as e:
        print(f"[WARN] Could not register required services: {e}")

    # Export chosen port for other tools
    os.environ["AETHERRA_HUB_PORT"] = str(desired_port)
    print(f"[OK] Hub with AI API on http://127.0.0.1:{desired_port}")
    # Re-apply flags one more time in case start_server triggered a .env reload
    os.environ.update(desired_flags)
    print(
        f"      AI enabled={os.environ.get('AETHERRA_AI_API_ENABLED')} stream={os.environ.get('AETHERRA_AI_API_STREAM')} require_token={os.environ.get('AETHERRA_AI_API_REQUIRE_TOKEN')}"
    )

    # Run Flask app
    try:
        app.run(host="127.0.0.1", port=desired_port, debug=False, use_reloader=False)
        return 0
    except KeyboardInterrupt:
        print("[STOP] Hub exiting")
        return 0


if __name__ == "__main__":
    sys.exit(main())
