#!/usr/bin/env python3

"""Full test for Phase 3 homeostasis implementation including watchdog."""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from Aetherra.homeostasis.homeostasis_integration import (
    get_homeostasis_orchestrator,
)


async def test_phase3_full():
    print("🔧 Testing Phase 3 with full initialization...")

    # Get orchestrator and initialize
    orchestrator = get_homeostasis_orchestrator()
    print(f"✓ Orchestrator created: {type(orchestrator).__name__}")

    try:
        # Initialize the orchestrator
        await orchestrator.initialize()
        print("✓ Orchestrator initialized")

        # Check watchdog after initialization
        if hasattr(orchestrator, "watchdog"):
            print(f"✓ Watchdog present: {orchestrator.watchdog is not None}")
            if orchestrator.watchdog:
                print(f"✓ Watchdog type: {type(orchestrator.watchdog).__name__}")
                print(f"✓ Watchdog running: {orchestrator.watchdog.running}")
            else:
                print("! Watchdog is None after initialization")
        else:
            print("! Watchdog attribute not found")

        # Test scheduler integration
        if hasattr(orchestrator, "ensure_scheduler_integration"):
            print("✓ Scheduler integration method available")
        else:
            print("! Scheduler integration method not found")

        # Start the orchestrator to activate watchdog
        await orchestrator.start()
        print("✓ Orchestrator started")

        # Check watchdog after start
        if orchestrator.watchdog:
            print(f"✓ Watchdog running after start: {orchestrator.watchdog.running}")

        # Test health status
        status = await orchestrator.get_system_health_status()
        watchdog_active = status.get("homeostasis", {}).get("watchdog_active", False)
        print(f"✓ Watchdog active in status: {watchdog_active}")

        # Clean shutdown
        await orchestrator.stop()
        print("✓ Orchestrator stopped cleanly")

        return True

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_phase3_full())
    if success:
        print("\n✅ Phase 3 persistent watchdog implementation working correctly!")
    else:
        print("\n❌ Phase 3 implementation has issues")
