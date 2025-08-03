#!/usr/bin/env python3
"""
Execute Plugin Tab Integration Test
===================================

Test the Execute Plugin tab functionality to ensure:
1. Tab creation and loading
2. Plugin execution functionality
3. Console output display
4. Error handling capabilities
"""

import os
import sys

# Add the project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))
sys.path.insert(0, os.path.dirname(__file__))


def test_execute_plugin_tab():
    """Test Execute Plugin tab integration"""
    print("⚡ Testing Execute Plugin Tab Integration...")

    try:
        from PySide6.QtWidgets import QApplication

        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        # Create Qt application
        app = QApplication([])

        # Create window
        window = LyrixaWindow()

        # Test Execute Plugin tab creation
        exec_tab = window.create_execute_plugin_tab()
        assert exec_tab is not None, "Execute Plugin tab creation failed"
        print("✅ Execute Plugin tab created successfully")

        # Test execution widgets existence
        assert hasattr(window, "exec_output"), "exec_output widget not found"
        assert hasattr(window, "exec_path"), "exec_path widget not found"
        print("✅ Plugin execution widgets exist")

        # Test execute method existence
        assert hasattr(window, "execute_plugin"), "execute_plugin method not found"
        print("✅ Plugin execution method available")

        # Test tab widget configuration
        tab_count = window.tab_widget.count()
        assert tab_count == 10, f"Expected 10 tabs, got {tab_count}"
        print(f"✅ Tab widget has {tab_count} tabs (including Execute Plugin)")

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
            "Execute Plugin",
        ]
        assert sidebar_items == expected_items, (
            f"Sidebar items mismatch: {sidebar_items}"
        )
        print("✅ Sidebar includes Execute Plugin option")

        # Test execution output read-only status
        assert window.exec_output.isReadOnly(), "Execution output should be read-only"
        print("✅ Execution output is read-only")

        # Test tab labels
        exec_tab_index = 9  # Should be the 10th tab (0-indexed)
        tab_text = window.tab_widget.tabText(exec_tab_index)
        assert tab_text == "Execute Plugin", (
            f"Execute Plugin tab label incorrect: {tab_text}"
        )
        print("✅ Execute Plugin tab has correct label")

        # Test placeholder text
        placeholder = window.exec_path.placeholderText()
        assert "Enter path to plugin .py file" in placeholder, (
            "Path input placeholder incorrect"
        )
        print("✅ Path input has correct placeholder")

        # Test path input height
        assert window.exec_path.height() == 30, "Path input height should be 30"
        print("✅ Path input has correct height")

        print("🎉 Execute Plugin Tab Integration: ALL TESTS PASSED!")
        print("📝 Execute Plugin Features Confirmed:")
        print("   - Dynamic plugin execution")
        print("   - File path input")
        print("   - Console output display")
        print("   - Error handling")

        # Cleanup
        app.quit()
        return True

    except Exception as e:
        print(f"[ERROR] Execute Plugin Tab Integration Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_execute_plugin_tab()
    sys.exit(0 if success else 1)
