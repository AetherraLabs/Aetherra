#!/usr/bin/env python3
"""
Quick test for hybrid interface components (no full initialization)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔧 Quick Hybrid Interface Test")
print("=" * 30)


def main():
    try:
        print("1. Testing Qt...")
        from PySide6.QtWidgets import QApplication

        print("   ✅ Qt available")

        print("2. Testing Web Bridge...")
        from Aetherra.lyrixa.gui.web_bridge import LyrixaWebBridge, LyrixaWebView

        print("   ✅ Web bridge available")

        print("3. Testing Data Manager...")
        from Aetherra.lyrixa.gui.data_manager import AetherraDataManager

        print("   ✅ Data manager available")

        print("4. Testing Hybrid Window...")
        # Import without full initialization
        import inspect

        from Aetherra.lyrixa.gui.aetherra_main_window_hybrid import AetherraMainWindow

        print("   ✅ Hybrid window class available")

        # Show some methods
        methods = [m for m in dir(AetherraMainWindow) if not m.startswith("_")]
        print(f"   📋 Available methods: {len(methods)}")
        print(f"   🔧 Key methods: {methods[:5]}...")

        print("\n🎉 All components ready for integration!")
        print(
            "💡 The hybrid interface can be launched with proper Qt application setup."
        )

        return 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
