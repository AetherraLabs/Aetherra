#!/usr/bin/env python3
"""
Emergency script to force homeostasis system into ACTIVE mode
for proper self-healing capabilities.
"""

import asyncio
import sys
from pathlib import Path

# Add Aetherra to path
sys.path.append(str(Path(__file__).parent))

from Aetherra.homeostasis.homeostasis_core import ControllerMode


async def force_active_mode():
    """Force the homeostasis system into active mode."""
    try:
        # Import service registry to get homeostasis instance
        from aetherra_service_registry import get_service_registry

        registry = await get_service_registry()
        if not registry:
            print("❌ No service registry available")
            return False

        # Get homeostasis service
        homeostasis_service = registry.get_service_info("homeostasis_system")
        if not homeostasis_service:
            print("❌ Homeostasis service not found in registry")
            return False

        # Get the controller from the homeostasis integration
        homeostasis_integration = homeostasis_service.instance
        if not hasattr(homeostasis_integration, "controller"):
            print("❌ Homeostasis integration has no controller")
            return False

        controller = homeostasis_integration.controller
        if not controller:
            print("❌ No homeostasis controller found")
            return False

        # Check current mode
        current_mode = controller.mode
        print(f"🔍 Current mode: {current_mode.value}")

        # Force to ACTIVE mode
        if current_mode != ControllerMode.ACTIVE:
            controller.set_mode(ControllerMode.ACTIVE)
            print("✅ Switched homeostasis to ACTIVE mode")
            print(f"🎯 New mode: {controller.mode.value}")

            # Also clear any emergency stop
            if hasattr(controller, "_emergency_stop") and controller._emergency_stop:
                controller.reset_emergency_stop()
                print("✅ Reset emergency stop")

            return True
        print("ℹ️ Already in ACTIVE mode")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    print("🚨 EMERGENCY HOMEOSTASIS MODE OVERRIDE")
    print("=====================================")
    print("This script will force the homeostasis system into ACTIVE mode")
    print("for proper self-healing capabilities.\n")

    success = await force_active_mode()

    if success:
        print("\n✅ SUCCESS: Homeostasis system should now be in ACTIVE mode")
        print("💡 The system can now perform self-healing actions")
    else:
        print("\n❌ FAILED: Could not switch homeostasis to active mode")
        print("💡 Try running this script while the OS is running")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
