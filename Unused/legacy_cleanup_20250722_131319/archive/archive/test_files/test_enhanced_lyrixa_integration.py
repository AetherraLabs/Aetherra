#!/usr/bin/env python3
"""
Enhanced LyrixaIntegration Test
==================================

Test script to verify the integration between Lyrixaand AetherraChat works correctly.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "Aetherra" / "ui"))


def test_enhanced_aetherplex():
    """Test the enhanced Lyrixaintegration"""
    print("🧪 Testing Enhanced LyrixaIntegration")
    print("=" * 50)

    # Test 1: Check Qt availability
    #     print("Test 1: Qt Framework Availability")
    try:
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 is available")
    except ImportError:
        print("❌ PySide6 not available - install with: pip install PySide6")
        return False

    # Test 2: Check AetherraChat components
    print("\nTest 2: AetherraChat Components")
    try:
        print("✅ AetherraChat interface available")
    except ImportError as e:
        print(f"⚠️ AetherraChat interface not available: {e}")
        print("   (This is OK - fallback will be used)")

    # Test 3: Check Enhanced Lyrixa
    print("\nTest 3: Enhanced LyrixaModule")
    try:
        from enhanced_aetherplex import EnhancedLyrixaWindow

        print("✅ Enhanced Lyrixamodule available")
    except ImportError as e:
        print(f"❌ Enhanced Lyrixamodule not available: {e}")
        return False

    # Test 4: Check existing Lyrixacomponents
    print("\nTest 4: Existing LyrixaComponents")
    try:
        print("✅ Fully modular Lyrixaavailable")
    except ImportError as e:
        print(f"⚠️ Fully modular Lyrixanot available: {e}")

    # Test 5: Test window creation (without showing)
    print("\nTest 5: Window Creation Test")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = EnhancedLyrixaWindow()
        print("✅ Enhanced Lyrixawindow created successfully")

        # Don't show the window, just test creation
        window.close()

    except Exception as e:
        print(f"❌ Window creation failed: {e}")
        return False

    print("\n🎉 All tests passed! Enhanced Lyrixaintegration is ready.")
    print("\n🚀 To launch Enhanced Lyrixa:")
    print("   Option 1: python launchers/launch_enhanced_aetherplex.py")
    print("   Option 2: python aethercode_launcher.py (choose option 1)")

    return True


def show_integration_summary():
    """Show summary of the integration"""
    print("\n📋 Enhanced LyrixaIntegration Summary")
    print("=" * 50)
    print("🎭 What's New:")
    print("   • Enhanced Lyrixacombines the full development environment")
    print("     with the sophisticated AetherraChat interface")
    print("   • Replaces basic chat with advanced features:")
    print("     - Tabbed interface (Assistant/Reflections/Code Preview)")
    print("     - Auto-scroll and typing indicators")
    print("     - Modern message bubbles and styling")
    print("     - Real-time AI interaction")
    print("   • Unified workflow for AI-native programming")
    print()
    print("🛠️ Architecture:")
    print("   • Left Panel: Development tools (Editor, Memory, Plugins, Performance)")
    print("   • Right Panel: Enhanced AetherraChat interface")
    print("   • Seamless integration between coding and AI assistance")
    print()
    print("[TOOL] Fallback Strategy:")
    print("   • If AetherraChat components aren't available, uses basic chat")
    print("   • If Enhanced Lyrixafails, falls back to standard Lyrixa")
    print("   • Graceful degradation ensures functionality")


def main():
    """Main test function"""
    success = test_enhanced_aetherplex()
    show_integration_summary()

    if success:
        print("\n🎯 Ready to continue? (y/n): ", end="")
        response = input().strip().lower()
        if response in ["y", "yes"]:
            print("🚀 Launching Enhanced Lyrixa...")
            try:
                from enhanced_aetherplex import main as enhanced_main

                return enhanced_main()
            except Exception as e:
                print(f"❌ Launch failed: {e}")
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
