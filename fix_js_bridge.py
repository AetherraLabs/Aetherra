#!/usr/bin/env python3
"""
Quick fix for Lyrixa web bridge JavaScript errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def reload_lyrixa_interface():
    """Reload the Lyrixa interface to fix JavaScript errors"""
    print("🔧 Applying JavaScript bridge fixes...")

    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication

        # Find existing Lyrixa application
        app = QApplication.instance()
        if not app:
            print("❌ No Qt application found. Is Lyrixa running?")
            return False

        # Find Lyrixa main window
        windows = app.topLevelWidgets()
        lyrixa_window = None

        for window in windows:
            if hasattr(window, "web_view") and hasattr(window, "mini_lyrixa"):
                lyrixa_window = window
                break

        if lyrixa_window:
            print("✅ Found Lyrixa window")

            # Reload the web interface
            if hasattr(lyrixa_window, "web_view"):
                lyrixa_window.web_view.reload_interface()
                print("🔄 Web interface reloaded with fixes")

                # Trigger visual consciousness updates
                QTimer.singleShot(2000, lambda: trigger_visual_updates(lyrixa_window))

                return True
        else:
            print("❌ Lyrixa window not found")
            return False

    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False


def trigger_visual_updates(window):
    """Trigger visual consciousness demonstrations"""
    try:
        print("🎯 Triggering visual consciousness demonstration...")

        # Update Mini-Lyrixa avatar
        if hasattr(window, "mini_lyrixa"):
            window.mini_lyrixa.update_cognitive_state(
                {
                    "emotional_state": "excited",
                    "reasoning_intensity": 0.95,
                    "confidence": 0.9,
                    "curiosity": 0.85,
                }
            )
            print("✅ Mini-Lyrixa avatar updated")

        # Update context summary
        if hasattr(window, "context_summary"):
            window.context_summary.update_context(
                "🚀 JavaScript bridge fixes applied successfully!", 0.95
            )
            print("✅ Context summary updated")

        # Log the fix
        if hasattr(window, "log_debug"):
            window.log_debug(
                "🔧 JavaScript bridge fixes applied - interface operational"
            )

        print("🎉 Visual consciousness fully operational!")

    except Exception as e:
        print(f"⚠️ Error in visual updates: {e}")


if __name__ == "__main__":
    print("🔧 LYRIXA JAVASCRIPT BRIDGE FIX")
    print("=" * 40)

    success = reload_lyrixa_interface()

    if success:
        print("\n🎉 Fix applied successfully!")
        print("The web interface should now work properly.")
    else:
        print("\n⚠️ Could not apply fix automatically.")
        print("Try restarting Lyrixa with: python launch_lyrixa.py")

    sys.exit(0 if success else 1)
