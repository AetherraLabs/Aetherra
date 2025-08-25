#!/usr/bin/env python3
"""
Headless boot smoke test for Aetherra OS.
- Boots the launcher in quiet, no-GUI mode
- Waits a short interval to allow services to register
- Asserts core services are healthy, then exits

Deterministic profile:
- If AETHERRA_PROFILE=test or --profile test, we set deterministic seeds and env.
"""

import argparse
import asyncio
import contextlib
import os
import random
import sys

try:
    import numpy as _np  # type: ignore
except Exception:
    _np = None
try:
    import torch as _torch  # type: ignore
except Exception:
    _torch = None

# Ensure project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from aetherra_os_launcher import AetherraOSLauncher  # noqa: E402
from aetherra_service_registry import get_service_registry  # noqa: E402


def apply_deterministic_profile(profile: str | None):
    if not profile:
        profile = os.getenv("AETHERRA_PROFILE", "").lower() or None
    if profile != "test":
        return
    # Set deterministic-related env and seeds
    os.environ.setdefault("AETHERRA_PROFILE", "test")
    os.environ.setdefault("AETHERRA_DETERMINISTIC", "1")
    os.environ.setdefault("PYTHONHASHSEED", "0")
    try:
        random.seed(0)
    except Exception:
        pass
    if _np is not None:
        try:
            _np.random.seed(0)
        except Exception:
            pass
    if _torch is not None:
        try:
            _torch.manual_seed(0)
            _torch.use_deterministic_algorithms(True)  # type: ignore[attr-defined]
        except Exception:
            pass


async def run_smoke():
    # CLI args for profile (optional)
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--profile", default=os.getenv("AETHERRA_PROFILE", ""))
    try:
        args, _ = ap.parse_known_args()
    except SystemExit:

        class _A:  # fallback if parsing fails under tasks
            profile = os.getenv("AETHERRA_PROFILE", "")

        args = _A()

    apply_deterministic_profile(getattr(args, "profile", None))
    # Force no GUI and quiet logs
    cfg = {"gui_enabled": False, "quiet": True, "hub_enabled": False}

    launcher = AetherraOSLauncher()

    async def boot():
        await launcher.launch_full_os(cfg)

    # Try to catch early boot failures quickly
    task = asyncio.create_task(boot())
    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=2.5)
        # If we get here without TimeoutError, boot returned early (unexpected)
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        print(f"[SMOKE][FAIL] Boot error: {e}")
        os._exit(2)

    # Check registry
    reg = await get_service_registry()
    status = reg.get_registry_status()

    # Minimal core set we expect
    expected = {"memory_system", "plugin_manager", "aetherra_engine"}
    registered = set(status.get("services", {}).keys())

    missing = expected - registered
    if missing:
        print(f"[SMOKE][FAIL] Missing services: {sorted(missing)}")
        os._exit(2)

    print("[SMOKE][OK] Core services registered:", sorted(expected))

    # Stop the main loop cleanly
    launcher.running = False
    try:
        await asyncio.sleep(0.1)
    finally:
        # Cancel boot task if still running
        if not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task


if __name__ == "__main__":
    try:
        asyncio.run(run_smoke())
    except KeyboardInterrupt:
        sys.exit(0)
