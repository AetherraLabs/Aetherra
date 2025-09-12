"""HTTP / Flask interop helpers decoupled from legacy hub server."""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Dict


def run_coro_blocking(coro):
    """Run an async coroutine from a sync context (e.g., Flask route).

    If already inside an event loop, spin a new loop in a helper thread to avoid
    nested loop errors. Returns the coroutine result or raises the underlying
    exception.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        holder: Dict[str, Any] = {}

        def _runner():
            try:
                new_loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(new_loop)
                    holder["result"] = new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            except Exception as e:  # pragma: no cover - defensive
                holder["error"] = e

        t = threading.Thread(target=_runner)
        t.start()
        t.join(timeout=3.0)
        if "result" in holder:
            return holder["result"]
        raise holder.get("error", RuntimeError("async-run-timeout"))
    return asyncio.run(coro)
