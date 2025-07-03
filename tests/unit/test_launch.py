#!/usr/bin/env python3
"""
Simple test to run Neuroplex v2.0 and catch any errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    print("🔍 Testing Neuroplex v2.0 launch...")

    # Test import
    print("📦 Importing modules...")
    from ui.aetherplex_gui_v2 import QT_AVAILABLE, ModernNeuroplexWindow, QApplication

    print(f"✅ Qt Available: {QT_AVAILABLE}")

    if not QT_AVAILABLE:
        print("❌ Qt not available")
        sys.exit(1)

    # Test application creation
    print("🚀 Creating application...")
    app = QApplication(sys.argv)

    print("🏗️ Creating window...")
    try:
        window = ModernNeuroplexWindow()
        print("✅ Window created successfully!")
    except Exception as e:
        print(f"❌ Error creating window: {e}")
        import traceback

        traceback.print_exc()
        raise
    print("👁️ Showing window...")
    window.show()

    print("🎉 Launch successful! Window should be visible.")

    # Don't start the event loop, just test creation

except Exception as e:
    print(f"❌ Error during launch: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
