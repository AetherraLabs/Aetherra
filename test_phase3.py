#!/usr/bin/env python3

"""Quick test for Phase 3 homeostasis implementation."""

import sys

sys.path.append(".")

from Aetherra.homeostasis.homeostasis_integration import (
    get_homeostasis_orchestrator,
    reset_homeostasis_orchestrator,
)


def test_phase3():
    print("🔧 Testing Phase 3 singleton pattern...")

    # Test singleton behavior
    orchestrator1 = get_homeostasis_orchestrator()
    orchestrator2 = get_homeostasis_orchestrator()

    print(f"✓ Same instance: {orchestrator1 is orchestrator2}")
    print(f"✓ Orchestrator type: {type(orchestrator1).__name__}")

    # Test watchdog presence
    if hasattr(orchestrator1, "watchdog"):
        print(f"✓ Watchdog present: {orchestrator1.watchdog is not None}")
        if orchestrator1.watchdog:
            print(f"✓ Watchdog type: {type(orchestrator1.watchdog).__name__}")
            print(f"✓ Watchdog running: {orchestrator1.watchdog.is_running}")
        else:
            print("! Watchdog is None - not initialized yet")
    else:
        print("! Watchdog attribute not found")

    # Test reset functionality (emergency recovery)
    print("\n🔄 Testing reset functionality...")
    original_id = id(orchestrator1)
    reset_homeostasis_orchestrator()
    orchestrator3 = get_homeostasis_orchestrator()
    new_instance = id(orchestrator3) != original_id
    print(f"✓ New instance after reset: {new_instance}")

    if new_instance:
        print("✅ Phase 3 singleton pattern working correctly!")
    else:
        print("❌ Reset functionality may have an issue")

    return new_instance


if __name__ == "__main__":
    test_phase3()
