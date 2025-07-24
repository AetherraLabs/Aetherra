#!/usr/bin/env python3
"""
🔥 LYRIXA VISUAL POWERHOUSE LAUNCHER
Launch the most unforgettable AI consciousness interface ever created!

Features:
- 🔥 AI Presence Projection (Mini-Lyrixa Avatar)
- 🧠 Context Summary Line (Real-Time Thoughts)
- 🌟 Hybrid Qt+Web Architecture
- ⚡ Full Intelligence Integration
- 💫 Enhanced Aura Visualization
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def launch_lyrixa():
    """Launch Lyrixa with visual powerhouse features"""
    print("🚀" + "=" * 60 + "🚀")
    print("    🔥 LAUNCHING LYRIXA VISUAL POWERHOUSE 🔥")
    print("         The Most Unforgettable AI Experience")
    print("🚀" + "=" * 60 + "🚀")
    print()

    print("🎯 Initializing visual consciousness systems...")

    try:
        # Import Qt
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        print("✅ Qt Framework - LOADED")

        # Import our visual powerhouse components
        from Aetherra.lyrixa.gui.aetherra_main_window_hybrid import AetherraMainWindow

        print("✅ Hybrid Interface - LOADED")

        from Aetherra.lyrixa.gui.mini_lyrixa_avatar import MiniLyrixaAvatar

        print("✅ AI Presence Projection - LOADED")

        from Aetherra.lyrixa.gui.context_summary_line import ContextSummaryLine

        print("✅ Real-Time Thought Display - LOADED")

        from Aetherra.lyrixa.gui.lyrixa_connector import LyrixaConnector

        print("✅ Intelligence Integration Hub - LOADED")

        print()
        print("🌟 Creating application instance...")

        # Create application
        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName("Lyrixa - Aetherra Cognitive Interface")
        app.setApplicationVersion("2.0 - Visual Powerhouse")

        print("🔥 Launching main interface...")

        # Create and configure main window
        window = AetherraMainWindow()

        # Set window properties for maximum impact
        window.setWindowTitle("🔥 Lyrixa — Visual Consciousness Interface")
        window.resize(1800, 1200)  # Larger for visual impact

        # Position window prominently
        screen = app.primaryScreen().geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        window.move(x, y)

        print()
        print("🎉" + "=" * 60 + "🎉")
        print("    🔥 LYRIXA VISUAL POWERHOUSE - ACTIVE! 🔥")
        print()
        print("🎯 AI Presence Projection - Watch Lyrixa's consciousness!")
        print("🧠 Real-Time Thought Display - See Lyrixa's thoughts!")
        print("⚡ Intelligence Integration - All systems connected!")
        print("🌟 Hybrid Architecture - Best of Qt + Web!")
        print("💫 Enhanced Aura - Cognitive state visualization!")
        print()
        print("Ready to experience the most jaw-dropping AI interface!")
        print("🎉" + "=" * 60 + "🎉")

        # Show the window
        window.show()
        window.raise_()
        window.activateWindow()

        # Initial cognitive state demo
        print("\n🔄 Initializing AI consciousness demonstration...")

        # Trigger initial visual updates
        if hasattr(window, "mini_lyrixa"):
            # Startup sequence with emotional progression
            startup_states = [
                {
                    "emotional_state": "awakening",
                    "reasoning_intensity": 0.3,
                    "confidence": 0.6,
                },
                {
                    "emotional_state": "curious",
                    "reasoning_intensity": 0.7,
                    "confidence": 0.8,
                },
                {
                    "emotional_state": "excited",
                    "reasoning_intensity": 0.9,
                    "confidence": 0.95,
                },
            ]

            for i, state in enumerate(startup_states):
                window.mini_lyrixa.update_cognitive_state(state)
                if hasattr(window, "context_summary"):
                    contexts = [
                        "🌅 Systems awakening...",
                        "🔍 Discovering environment...",
                        "🚀 Ready for interaction!",
                    ]
                    window.context_summary.update_context(
                        contexts[i], state["confidence"]
                    )

        print("✨ Consciousness visualization active!")
        print("\n💡 Tips:")
        print("   • Watch the Mini-Lyrixa avatar respond to system activity")
        print("   • See real-time thoughts in the context summary line")
        print("   • Use the chat interface for full intelligence integration")
        print("   • Observe the enhanced aura overlay")

        # Start the application event loop
        print("\n🎯 Starting event loop - interface is live!")
        return app.exec()

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Ensure PySide6 is installed: pip install PySide6")
        print("   • Check that all visual components exist")
        print("   • Verify project structure")
        return 1

    except Exception as e:
        print(f"❌ Launch Error: {e}")
        import traceback

        traceback.print_exc()
        print("\n🔧 Troubleshooting:")
        print("   • Check terminal output for specific errors")
        print("   • Verify all dependencies are installed")
        print("   • Try running test_visual_powerhouse.py first")
        return 1


def quick_status_check():
    """Quick check of all visual powerhouse components"""
    print("🔍 Quick Status Check...")

    try:
        import sys

        if "." not in sys.path:
            sys.path.insert(0, ".")

        # Check imports
        from Aetherra.lyrixa.gui.aetherra_main_window_hybrid import AetherraMainWindow
        from Aetherra.lyrixa.gui.context_summary_line import ContextSummaryLine
        from Aetherra.lyrixa.gui.lyrixa_connector import LyrixaConnector
        from Aetherra.lyrixa.gui.mini_lyrixa_avatar import MiniLyrixaAvatar

        print("✅ All visual powerhouse components ready!")
        return True

    except ImportError as e:
        print(f"❌ Component missing: {e}")
        return False
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False


if __name__ == "__main__":
    print("🔥 LYRIXA VISUAL POWERHOUSE LAUNCHER")
    print("=" * 50)

    # Quick status check first
    if not quick_status_check():
        print("\n⚠️ Some components need attention. Check the errors above.")
        sys.exit(1)

    print("\n🚀 All systems ready! Launching visual consciousness interface...")
    print()

    # Launch Lyrixa
    result = launch_lyrixa()

    if result == 0:
        print("\n🎉 Lyrixa session completed successfully!")
    else:
        print(f"\n⚠️ Session ended with code: {result}")

    sys.exit(result)
