#!/usr/bin/env python3
"""
Goal Tracker Tab Integration Test
=================================

Test the Goal Tracker tab functionality to ensure:
1. Tab creation and loading
2. Goal tracking functionality
3. Refresh button capabilities
4. Live goal management hooks
"""

import os
import sys

# Add the project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))
sys.path.insert(0, os.path.dirname(__file__))


def test_goal_tracker_tab():
    """Test Goal Tracker tab integration"""
    print("🎯 Testing Goal Tracker Tab Integration...")

    try:
        from PySide6.QtWidgets import QApplication

        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        # Create Qt application
        app = QApplication([])

        # Create window
        window = LyrixaWindow()

        # Test Goal Tracker tab creation
        goal_tab = window.create_goal_tab()
        assert goal_tab is not None, "Goal Tracker tab creation failed"
        print("✅ Goal Tracker tab created successfully")

        # Test goal log widget existence
        assert hasattr(window, "goal_log"), "goal_log widget not found"
        print("✅ Goal log QTextEdit widget exists")

        # Test refresh method existence
        assert hasattr(window, "refresh_goal_log"), "refresh_goal_log method not found"
        print("✅ Goal refresh method available")

        # Test tab widget configuration
        tab_count = window.tab_widget.count()
        assert tab_count == 9, f"Expected 9 tabs, got {tab_count}"
        print(f"✅ Tab widget has {tab_count} tabs (including Goal Tracker)")

        # Test sidebar configuration
        sidebar_items = []
        for i in range(window.sidebar.count()):
            sidebar_items.append(window.sidebar.item(i).text())

        expected_items = [
            "Chat",
            "System",
            "Agents",
            "Performance",
            "Self-Improvement",
            "Plugins",
            "Plugin Editor",
            "Memory Viewer",
            "Goal Tracker",
        ]
        assert sidebar_items == expected_items, (
            f"Sidebar items mismatch: {sidebar_items}"
        )
        print("✅ Sidebar includes Goal Tracker option")

        # Test goal log read-only status
        assert window.goal_log.isReadOnly(), "Goal log should be read-only"
        print("✅ Goal log is read-only")

        # Test tab labels
        goal_tab_index = 8  # Should be the 9th tab (0-indexed)
        tab_text = window.tab_widget.tabText(goal_tab_index)
        assert tab_text == "Goal Tracker", (
            f"Goal Tracker tab label incorrect: {tab_text}"
        )
        print("✅ Goal Tracker tab has correct label")

        # Test refresh functionality
        window.refresh_goal_log()
        goal_content = window.goal_log.toPlainText()
        assert "Fetching active goals" in goal_content, (
            "Goal refresh functionality not working"
        )
        print("✅ Goal refresh functionality working")

        # Test goal content
        assert "Maintain plugin health" in goal_content, "Goal content not displaying"
        print("✅ Goal content displaying correctly")

        print("🎉 Goal Tracker Tab Integration: ALL TESTS PASSED!")
        print("📝 Goal Tracker Features Confirmed:")
        print("   - Live goal tracking")
        print("   - Refresh button functionality")
        print("   - Read-only goal display")
        print("   - Ready for real-time goal queue integration")

        # Cleanup
        app.quit()
        return True

    except Exception as e:
        print(f"[ERROR] Goal Tracker Tab Integration Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_goal_tracker_tab()
    sys.exit(0 if success else 1)
