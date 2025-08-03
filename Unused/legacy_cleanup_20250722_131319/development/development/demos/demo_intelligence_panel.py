#!/usr/bin/env python3
"""
Demo Intelligence Panel for Lyrixa
==================================

This script demonstrates the new Intelligence Panel for Lyrixa.
"""

import os
import sys

# Add the project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))
sys.path.insert(0, os.path.dirname(__file__))


def demo_intelligence_panel():
    """Demo the Lyrixa Intelligence Panel"""
    print("🧠 Lyrixa Intelligence Panel Demo")
    print("=" * 70)

    try:
        from PySide6.QtWidgets import (
            QApplication,
            QMainWindow,
            QTabWidget,
            QVBoxLayout,
            QWidget,
        )

        # Import our intelligence panel
        from Aetherra.lyrixa.gui.panels.intelligence_panel import (
            LyrixaIntelligencePanel,
        )

        # Create Qt application
        app = QApplication([])

        # Create main window
        window = QMainWindow()
        window.setWindowTitle("Lyrixa Intelligence Panel Demo")
        window.resize(1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tab_widget = QTabWidget()

        # Create our intelligence panel
        intelligence_panel = LyrixaIntelligencePanel()

        # Add intelligence panel to tab widget
        tab_widget.addTab(intelligence_panel, "🧠 Intelligence")

        # Add tab widget to layout
        layout.addWidget(tab_widget)

        # Set central widget
        window.setCentralWidget(central_widget)

        # Show window
        window.show()

        print("🎯 Intelligence Panel Features:")
        print("")
        print("1️⃣ Live Thought Stream:")
        print("   🧠 Real-time thought visualization")
        print("   ✅ Thought type categorization")
        print("   📊 Confidence metrics")

        print("\n2️⃣ Agent Status:")
        print("   🤖 Agent activity monitoring")
        print("   📈 Load and health metrics")
        print("   🔄 Detailed agent information")

        print("\n3️⃣ Goals:")
        print("   🎯 Current goal tracking")
        print("   🔮 Predicted next goals")
        print("   📊 Progress visualization")

        print("\n4️⃣ Confidence:")
        print("   📊 Confidence metrics dashboard")
        print("   🧮 Decision confidence tracking")
        print("   🧠 Inner reasoning display")

        print("\n5️⃣ Emotional Feedback:")
        print("   ❤️ Emotional state visualization")
        print("   [WARN] Risk warnings")
        print("   📝 Emotional intelligence log")

        print("\n" + "=" * 70)
        print("🌟 Intelligence Panel Demo Running!")
        print("✅ Close the window to exit the demo")

        # Start application event loop
        app.exec()
        return True

    except Exception as e:
        print(f"❌ Intelligence Panel Demo Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_intelligence_panel()
    sys.exit(0 if success else 1)
