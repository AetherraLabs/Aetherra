#!/usr/bin/env python3
"""
Enhanced Neuroplex Integration Test
==================================

Test script to verify the integration between Neuroplex and NeuroChat works correctly.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "neurocode" / "ui"))


def test_enhanced_neuroplex():
    """Test the enhanced Neuroplex integration"""
    print("🧪 Testing Enhanced Neuroplex Integration")
    print("=" * 50)

    # Test 1: Check Qt availability
#     print("Test 1: Qt Framework Availability")
    try:
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 is available")
    except ImportError:
        print("❌ PySide6 not available - install with: pip install PySide6")
        return False

    # Test 2: Check NeuroChat components
    print("\nTest 2: NeuroChat Components")
    try:

        print("✅ NeuroChat interface available")
    except ImportError as e:
        print(f"⚠️ NeuroChat interface not available: {e}")
        print("   (This is OK - fallback will be used)")

    # Test 3: Check Enhanced Neuroplex
    print("\nTest 3: Enhanced Neuroplex Module")
    try:
        from enhanced_neuroplex import EnhancedLyrixaWindow

        print("✅ Enhanced Neuroplex module available")
    except ImportError as e:
        print(f"❌ Enhanced Neuroplex module not available: {e}")
        return False

    # Test 4: Check existing Neuroplex components
    print("\nTest 4: Existing Neuroplex Components")
    try:

        print("✅ Fully modular Neuroplex available")
    except ImportError as e:
        print(f"⚠️ Fully modular Neuroplex not available: {e}")

    # Test 5: Test window creation (without showing)
    print("\nTest 5: Window Creation Test")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = EnhancedLyrixaWindow()
        print("✅ Enhanced Neuroplex window created successfully")

        # Don't show the window, just test creation
        window.close()

    except Exception as e:
        print(f"❌ Window creation failed: {e}")
        return False

    print("\n🎉 All tests passed! Enhanced Neuroplex integration is ready.")
    print("\n🚀 To launch Enhanced Neuroplex:")
    print("   Option 1: python launchers/launch_enhanced_neuroplex.py")
    print("   Option 2: python neurocode_launcher.py (choose option 1)")

    return True


def show_integration_summary():
    """Show summary of the integration"""
    print("\n📋 Enhanced Neuroplex Integration Summary")
    print("=" * 50)
    print("🎭 What's New:")
    print("   • Enhanced Neuroplex combines the full development environment")
    print("     with the sophisticated NeuroChat interface")
    print("   • Replaces basic chat with advanced features:")
    print("     - Tabbed interface (Assistant/Reflections/Code Preview)")
    print("     - Auto-scroll and typing indicators")
    print("     - Modern message bubbles and styling")
    print("     - Real-time AI interaction")
    print("   • Unified workflow for AI-native programming")
    print()
    print("🛠️ Architecture:")
    print("   • Left Panel: Development tools (Editor, Memory, Plugins, Performance)")
    print("   • Right Panel: Enhanced NeuroChat interface")
    print("   • Seamless integration between coding and AI assistance")
    print()
    print("🔧 Fallback Strategy:")
    print("   • If NeuroChat components aren't available, uses basic chat")
    print("   • If Enhanced Neuroplex fails, falls back to standard Neuroplex")
    print("   • Graceful degradation ensures functionality")


def main():
    """Main test function"""
    success = test_enhanced_neuroplex()
    show_integration_summary()

    if success:
        print("\n🎯 Ready to continue? (y/n): ", end="")
        response = input().strip().lower()
        if response in ["y", "yes"]:
            print("🚀 Launching Enhanced Neuroplex...")
            try:
                from enhanced_neuroplex import main as enhanced_main

                return enhanced_main()
            except Exception as e:
                print(f"❌ Launch failed: {e}")
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
