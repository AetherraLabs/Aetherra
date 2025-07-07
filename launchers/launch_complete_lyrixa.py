#!/usr/bin/env python3
"""
🚀 LYRIXA GUI LAUNCHER - FULL FEATURE SUITE
===========================================

Launch the complete Lyrixa AI Assistant with:
✅ Plugin System Management
✅ Multi-Agent System Control
✅ Modern Dark Theme GUI
✅ All features integrated and operational

This demonstrates our MAJOR ACCOMPLISHMENT!
"""

import sys
from pathlib import Path

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")

    # Check PySide6
    try:
        import PySide6

        print("✅ PySide6 GUI framework available")
    except ImportError:
        print("❌ PySide6 not available - install with: pip install PySide6")
        return False

    # Check Lyrixa components
    try:
        from lyrixa.core.plugin_system import LyrixaPluginSystem

        print("✅ Plugin system available")
    except ImportError as e:
        print(f"❌ Plugin system not available: {e}")
        return False

    try:
        from lyrixa.core.multi_agent_system import LyrixaMultiAgentSystem

        print("✅ Multi-agent system available")
    except ImportError as e:
        print(f"❌ Multi-agent system not available: {e}")
        return False

    # Check GUI
    try:
        from modern_lyrixa_gui import ModernLyrixaGUI

        print("✅ Modern GUI available")
    except ImportError as e:
        print(f"❌ Modern GUI not available: {e}")
        return False

    print("🎉 All dependencies satisfied!")
    return True


def main():
    """Launch Lyrixa with full feature suite"""
    print("🚀 LYRIXA AI ASSISTANT - FULL FEATURE LAUNCHER")
    print("=" * 60)
    print("🔌 Plugin System: Create, install, manage plugins")
    print("🤖 Multi-Agent System: Collaborative AI agents")
    print("🌙 Modern GUI: Beautiful dark theme interface")
    print("💬 AI Chat: Advanced conversational capabilities")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot launch - missing dependencies")
        return 1

    # Launch GUI
    try:
        print("\n🌙 Launching Lyrixa GUI...")
        from modern_lyrixa_gui import main as gui_main

        return gui_main()

    except KeyboardInterrupt:
        print("\n👋 Lyrixa GUI closed by user")
        return 0

    except Exception as e:
        print(f"\n❌ Failed to launch GUI: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
