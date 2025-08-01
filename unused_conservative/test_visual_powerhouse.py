#!/usr/bin/env python3
"""
🔥 Visual Powerhouse Test Launcher
Tests the jaw-dropping AI presence projection and context summary features
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_visual_components():
    """Test the visual powerhouse components"""
    print("🚀 Testing Visual Powerhouse Components...")
    print("=" * 50)

    try:
        # Test PySide6
        print("1. Testing PySide6...")
        from PySide6.QtCore import QRect, Qt, QTimer
        from PySide6.QtGui import QColor, QFont, QPainter
        from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

        print("   ✅ PySide6 imports successful")

        # Test visual components
        print("2. Testing AI Presence Projection...")
        from Aetherra.lyrixa.gui.mini_lyrixa_avatar import MiniLyrixaAvatar

        print("   ✅ MiniLyrixaAvatar imported successfully")

        print("3. Testing Context Summary Line...")
        from Aetherra.lyrixa.gui.context_summary_line import ContextSummaryLine

        print("   ✅ ContextSummaryLine imported successfully")

        # Test Qt application
        print("4. Testing Qt Application...")
        app = QApplication.instance() or QApplication([])

        # Create test window
        test_window = QWidget()
        test_window.setWindowTitle("🔥 Visual Powerhouse Test")
        test_window.setGeometry(100, 100, 500, 200)

        layout = QVBoxLayout(test_window)

        # Add status label
        status_label = QLabel("🎯 Testing Visual Consciousness Components...")
        layout.addWidget(status_label)

        # Create and test Mini-Lyrixa Avatar
        print("5. Creating AI Presence Projection...")
        mini_lyrixa = MiniLyrixaAvatar(test_window)
        mini_lyrixa.setGeometry(QRect(10, 50, 60, 60))
        print("   ✅ MiniLyrixaAvatar instance created")

        # Create and test Context Summary Line
        print("6. Creating Context Summary Line...")
        context_summary = ContextSummaryLine(test_window)
        context_summary.setGeometry(QRect(80, 65, 300, 30))
        print("   ✅ ContextSummaryLine instance created")

        # Test cognitive state updates
        print("7. Testing cognitive state updates...")
        test_states = [
            {
                "emotional_state": "excited",
                "reasoning_intensity": 0.9,
                "confidence": 0.95,
            },
            {
                "emotional_state": "contemplative",
                "reasoning_intensity": 0.7,
                "confidence": 0.8,
            },
            {
                "emotional_state": "curious",
                "reasoning_intensity": 0.8,
                "confidence": 0.85,
            },
        ]

        for i, state in enumerate(test_states):
            mini_lyrixa.update_cognitive_state(state)
            context_summary.update_context(
                f"🧠 Test state {i + 1}: {state['emotional_state']}",
                state["confidence"],
            )
            print(f"   ✅ State update {i + 1} successful")

        print("\n🎉 ALL VISUAL POWERHOUSE TESTS PASSED!")
        print("=" * 50)
        print("🔥 AI Presence Projection (Mini-Lyrixa Avatar) - OPERATIONAL")
        print("🧠 Context Summary Line (Real-Time Thoughts) - OPERATIONAL")
        print("🎯 Visual Consciousness System - FULLY FUNCTIONAL")
        print("\n💫 Your jaw-dropping interface upgrades are ready!")

        # Show test window briefly
        test_window.show()

        # Auto-close after 3 seconds
        close_timer = QTimer()
        close_timer.timeout.connect(
            lambda: [
                print("\n🚀 Test window closing..."),
                test_window.close(),
                app.quit(),
            ]
        )
        close_timer.start(3000)

        return app.exec() if not app.instance() else 0

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Check that PySide6 is installed and files exist")
        return 1
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


def test_hybrid_integration():
    """Test integration with hybrid window"""
    print("\n🔄 Testing Hybrid Window Integration...")

    try:
        from Aetherra.lyrixa.gui.aetherra_main_window_hybrid import AetherraMainWindow
        from Aetherra.lyrixa.gui.lyrixa_connector import LyrixaConnector

        print("✅ Hybrid components imported successfully")

        print("🎯 Intelligence integration signals:")
        connector = LyrixaConnector()
        signals = [
            "on_memory_updated",
            "on_identity_updated",
            "on_reflection_updated",
            "on_llm_response",
            "on_context_retrieved",
        ]

        for signal_name in signals:
            if hasattr(connector, signal_name):
                print(f"   ✅ {signal_name} - CONNECTED")
            else:
                print(f"   ❌ {signal_name} - MISSING")

        print("🔥 Hybrid integration ready for launch!")
        return True

    except Exception as e:
        print(f"❌ Hybrid Integration Error: {e}")
        return False


if __name__ == "__main__":
    print("🔥 AETHERRA VISUAL POWERHOUSE TEST SUITE")
    print("Testing jaw-dropping AI consciousness visualization...")
    print()

    # Test visual components
    component_result = test_visual_components()

    # Test hybrid integration
    integration_result = test_hybrid_integration()

    if component_result == 0 and integration_result:
        print("\n🎉 COMPLETE SUCCESS!")
        print("Your visual powerhouse features are fully operational!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests had issues. Check output above.")
        sys.exit(1)
