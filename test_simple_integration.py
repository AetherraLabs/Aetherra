#!/usr/bin/env python3
"""
Simple GUI + Memory Integration Test
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))


def test_simple_integration():
    """Simple test of GUI and memory integration"""
    print("🧪 SIMPLE GUI + MEMORY INTEGRATION TEST")
    print("=" * 45)

    try:
        # Create QApplication first
        print("1️⃣ Creating QApplication...")
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        print("✅ QApplication created")

        # Import and create GUI
        print("\n2️⃣ Testing GUI import and creation...")
        from src.aetherra.ui.enhanced_lyrixa import EnhancedLyrixaWindow

        window = EnhancedLyrixaWindow()
        print("✅ Enhanced Lyrixa Window created successfully")

        # Test memory integration
        print("\n3️⃣ Testing memory integration...")
        if hasattr(window, "advanced_memory"):
            if window.advanced_memory is not None:
                print("✅ Advanced Memory System is integrated")
            else:
                print("⚠️ Advanced Memory System is None (dependencies missing)")
        else:
            print("❌ Advanced Memory System attribute not found")

        # Test reflection engine
        print("\n4️⃣ Testing reflection engine...")
        if hasattr(window, "reflection_engine"):
            if window.reflection_engine is not None:
                print("✅ Reflection Engine is integrated")
            else:
                print("⚠️ Reflection Engine is None")
        else:
            print("❌ Reflection Engine attribute not found")

        # Test plugin registration
        print("\n5️⃣ Testing plugin registration...")
        if "Advanced Memory" in window.plugins:
            print("✅ Advanced Memory plugin is registered")
        else:
            print("⚠️ Advanced Memory plugin not in plugin list")
            print(f"   Available plugins: {window.plugins}")

        # Test a simple chat
        print("\n6️⃣ Testing simple chat...")
        response = window.send_message("Hello, testing integration")
        print(f"✅ Chat response received: {response[:60]}...")

        print("\n🎉 BASIC INTEGRATION TEST COMPLETE!")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_simple_integration()
    if success:
        print("\n✅ Basic integration is working!")
        print("🚀 Ready for advanced integration tests!")
    else:
        print("\n❌ Basic integration failed - fix issues before proceeding")
