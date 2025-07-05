"""
Test Unified Launcher
====================
Quick test of the unified launcher functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_unified_launcher():
    """Test the unified launcher."""
    print("🚀 Testing Unified Launcher...")

    try:
        from lyrixa.gui.unified.main import UnifiedLyrixaLauncher

        launcher = UnifiedLyrixaLauncher()
        print("✅ Launcher created")

        # Test async initialization
        success = await launcher.async_initialize()

        if success:
            print("🎉 Unified launcher initialization successful!")

            # Check components
            if launcher.memory_system:
                print("✅ Memory system initialized")
            if launcher.anticipation_engine:
                print("✅ Anticipation engine initialized")
            if launcher.main_window:
                print("✅ GUI application initialized")
            if launcher.context_bridge:
                print("✅ Context bridge initialized")

            return True
        else:
            print("❌ Unified launcher initialization failed")
            return False

    except Exception as e:
        print(f"❌ Launcher test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_unified_launcher())
    sys.exit(0 if success else 1)
