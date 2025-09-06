#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Agent Fabric Daemon
===========================
Keeps the Agent Fabric alive in a lightweight process for background work
when the full OS isn’t launched.

Notes:
- This uses the in-process Service Registry. It’s intended for tools running
  in the same process (or as a developer convenience). The full OS should be
  preferred for cross-service orchestration.
"""

from __future__ import annotations

import asyncio
import signal
import sys
from typing import Any


async def _start_fabric() -> None:
    from aetherra_agent_fabric import get_agent_fabric
    from aetherra_service_registry import get_service_registry, register_service

    reg = await get_service_registry()

    # Start or reuse
    fabric = reg.get_service("agent_fabric")
    if not fabric:
        fabric = await get_agent_fabric(reg)
        await fabric.start()
        await register_service(
            "agent_fabric",
            fabric,
            metadata={"type": "agents", "daemon": True},
        )

    # Keep process alive with a simple heartbeat loop
    print("[DAEMON] Agent Fabric online; entering idle loop (Ctrl+C to exit)")
    try:
        while True:
            # Touch heartbeat if available
            try:
                if hasattr(reg, "update_heartbeat"):
                    await reg.update_heartbeat("agent_fabric")
            except Exception:
                pass
            await asyncio.sleep(5.0)
    except asyncio.CancelledError:
        pass


def main() -> int:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    stop_event = asyncio.Event()

    def _stop(*_args: Any) -> None:
        if not stop_event.is_set():
            stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop)
        except NotImplementedError:
            # Windows may not support add_signal_handler for all signals
            pass

    async def runner() -> int:
        task = asyncio.create_task(_start_fabric())
        try:
            await stop_event.wait()
        finally:
            task.cancel()
            with contextlib.suppress(Exception):
                await task
        return 0

    import contextlib

    try:
        return loop.run_until_complete(runner())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    sys.exit(main())
