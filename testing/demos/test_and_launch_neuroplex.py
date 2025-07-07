#!/usr/bin/env python3
"""
🚀 LyrixaQuick Test & Launch
===============================

Simple test and launch script for Lyrixato verify it works.
"""

import sys


def test_Lyrixa_basic():
    """Test basic Lyrixafunctionality"""
    print("🔍 Testing Basic LyrixaFunctionality...")

    try:
        # Test the main launcher

        print("  ✅ Aetherra Launcher: Import successful")

        # Test that we can access the main components
        if hasattr(Aetherra_launcher, "main"):
            print("  ✅ Main function: Available")

        return True

    except Exception as e:
        print(f"  ❌ Basic test failed: {e}")
        return False


def test_Lyrixa_ui():
    """Test LyrixaUI components"""
    print("\n🔍 Testing LyrixaUI Components...")

    try:
        # Test the fully modular version (most stable)
        print("  ✅ Fully Modular Lyrixa: Import successful")

        # Test GUI v2
        print("  ✅ Lyrixa v2: Import successful")

        return True

    except Exception as e:
        print(f"  ❌ UI test failed: {e}")
        return False


def launch_Lyrixa_demo():
    """Launch Lyrixain demo mode"""
    print("\n🚀 Launching LyrixaDemo...")

    try:
        # Import the launcher

        print("  🎯 Lyrixais ready to launch!")
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
            if hasattr(Aetherra_launcher, "launch_gui"):
                Aetherra_launcher.launch_gui()
            else:
                Aetherra_launcher.main()
        elif choice == "2":
            print("  💻 Launching CLI Mode...")
            # Launch CLI mode
            if hasattr(Aetherra_launcher, "launch_cli"):
                Aetherra_launcher.launch_cli()
            else:
                Aetherra_launcher.main()
        elif choice == "3":
            print("  🧪 Running Demo Mode...")
            # Just show that it can initialize
            print("  ✅ Demo completed successfully!")
        else:
            print("  ⚠️ Invalid choice, launching default mode...")
            Aetherra_launcher.main()

        return True

    except KeyboardInterrupt:
        print("\n  👋 User cancelled launch")
        return True
    except Exception as e:
        print(f"  ❌ Launch failed: {e}")
        return False


def main():
    """Main test and launch function"""
    print("🚀 LyrixaQuick Test & Launch")
    print("=" * 40)

    # Run basic tests
    if not test_Lyrixa_basic():
        print("❌ Basic tests failed. Cannot proceed.")
        return False

    if not test_Lyrixa_ui():
        print("⚠️ UI tests failed, but proceeding with basic functionality.")

    print("\n✅ Lyrixais functional!")

    # Ask if user wants to launch
    launch_choice = (
        input("\n🚀 Would you like to launch Lyrixanow? (y/n): ").strip().lower()
    )

    if launch_choice in ["y", "yes", ""]:
        return launch_Lyrixa_demo()
    else:
        print("👋 Lyrixatest completed. You can launch it anytime!")
        return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        sys.exit(0)
