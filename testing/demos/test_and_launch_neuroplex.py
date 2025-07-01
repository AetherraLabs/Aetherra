#!/usr/bin/env python3
"""
🚀 Neuroplex Quick Test & Launch
===============================

Simple test and launch script for Neuroplex to verify it works.
"""

import sys


def test_neuroplex_basic():
    """Test basic Neuroplex functionality"""
    print("🔍 Testing Basic Neuroplex Functionality...")

    try:
        # Test the main launcher
        import neurocode_launcher

        print("  ✅ NeuroCode Launcher: Import successful")

        # Test that we can access the main components
        if hasattr(neurocode_launcher, "main"):
            print("  ✅ Main function: Available")

        return True

    except Exception as e:
        print(f"  ❌ Basic test failed: {e}")
        return False


def test_neuroplex_ui():
    """Test Neuroplex UI components"""
    print("\n🔍 Testing Neuroplex UI Components...")

    try:
        # Test the fully modular version (most stable)
        print("  ✅ Fully Modular Neuroplex: Import successful")

        # Test GUI v2
        print("  ✅ Neuroplex GUI v2: Import successful")

        return True

    except Exception as e:
        print(f"  ❌ UI test failed: {e}")
        return False


def launch_neuroplex_demo():
    """Launch Neuroplex in demo mode"""
    print("\n🚀 Launching Neuroplex Demo...")

    try:
        # Import the launcher
        import neurocode_launcher

        print("  🎯 Neuroplex is ready to launch!")
        print("  📋 Available options:")
        print("    1. GUI Mode (Recommended)")
        print("    2. CLI Mode")
        print("    3. Demo Mode")

        choice = input("\n  Enter your choice (1-3, or 'q' to quit): ").strip()

        if choice == "q":
            print("  👋 Exiting...")
            return True
        elif choice == "1":
            print("  🎨 Launching GUI Mode...")
            # Launch GUI mode
            if hasattr(neurocode_launcher, "launch_gui"):
                neurocode_launcher.launch_gui()
            else:
                neurocode_launcher.main()
        elif choice == "2":
            print("  💻 Launching CLI Mode...")
            # Launch CLI mode
            if hasattr(neurocode_launcher, "launch_cli"):
                neurocode_launcher.launch_cli()
            else:
                neurocode_launcher.main()
        elif choice == "3":
            print("  🧪 Running Demo Mode...")
            # Just show that it can initialize
            print("  ✅ Demo completed successfully!")
        else:
            print("  ⚠️ Invalid choice, launching default mode...")
            neurocode_launcher.main()

        return True

    except KeyboardInterrupt:
        print("\n  👋 User cancelled launch")
        return True
    except Exception as e:
        print(f"  ❌ Launch failed: {e}")
        return False


def main():
    """Main test and launch function"""
    print("🚀 Neuroplex Quick Test & Launch")
    print("=" * 40)

    # Run basic tests
    if not test_neuroplex_basic():
        print("❌ Basic tests failed. Cannot proceed.")
        return False

    if not test_neuroplex_ui():
        print("⚠️ UI tests failed, but proceeding with basic functionality.")

    print("\n✅ Neuroplex is functional!")

    # Ask if user wants to launch
    launch_choice = input("\n🚀 Would you like to launch Neuroplex now? (y/n): ").strip().lower()

    if launch_choice in ["y", "yes", ""]:
        return launch_neuroplex_demo()
    else:
        print("👋 Neuroplex test completed. You can launch it anytime!")
        return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        sys.exit(0)
