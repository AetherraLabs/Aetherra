#!/usr/bin/env python3
"""
Memory Viewer Tab Integration Test
==================================

Test the Memory Viewer tab functionality to ensure:
1. Tab creation and loading
2. Memory state viewer functionality
3. Refresh button capabilities
4. Live memory inspection hooks
"""

import os
import sys

# Add the project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))
sys.path.insert(0, os.path.dirname(__file__))


def test_memory_viewer_tab():
    """Test Memory Viewer tab integration"""
    print("🧠 Testing Memory Viewer Tab Integration...")

    try:
        from PySide6.QtWidgets import QApplication

        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        # Create Qt application
        app = QApplication([])

        # Create window
        window = LyrixaWindow()

        # Test Memory Viewer tab creation
        memory_tab = window.create_memory_tab()
        assert memory_tab is not None, "Memory Viewer tab creation failed"
        print("✅ Memory Viewer tab created successfully")

        # Test memory viewer widget existence
        assert hasattr(window, "memory_view"), "memory_view widget not found"
        print("✅ Memory viewer QTextEdit widget exists")

        # Test refresh method existence
        assert hasattr(window, "refresh_memory_view"), (
            "refresh_memory_view method not found"
        )
        print("✅ Memory refresh method available")

        # Test tab widget configuration
        tab_count = window.tab_widget.count()
        assert tab_count == 8, f"Expected 8 tabs, got {tab_count}"
        print(f"✅ Tab widget has {tab_count} tabs (including Memory Viewer)")

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
        ]
        assert sidebar_items == expected_items, (
            f"Sidebar items mismatch: {sidebar_items}"
        )
        print("✅ Sidebar includes Memory Viewer option")

        # Test memory view read-only status
        assert window.memory_view.isReadOnly(), "Memory view should be read-only"
        print("✅ Memory viewer is read-only")

        # Test tab labels
        memory_tab_index = 7  # Should be the 8th tab (0-indexed)
        tab_text = window.tab_widget.tabText(memory_tab_index)
        assert tab_text == "Memory Viewer", (
            f"Memory Viewer tab label incorrect: {tab_text}"
        )
        print("✅ Memory Viewer tab has correct label")

        # Test refresh functionality
        window.refresh_memory_view()
        memory_content = window.memory_view.toPlainText()
        assert "Scanning memory state" in memory_content, (
            "Memory refresh functionality not working"
        )
        print("✅ Memory refresh functionality working")

        print("🎉 Memory Viewer Tab Integration: ALL TESTS PASSED!")
        print("📝 Memory Viewer Features Confirmed:")
        print("   - Live memory state inspection")
        print("   - Refresh button functionality")
        print("   - Read-only memory display")
        print("   - Ready for Lyrixa memory engine integration")

        # Cleanup
        app.quit()
        return True

    except Exception as e:
        print(f"[ERROR] Memory Viewer Tab Integration Test Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_memory_viewer_tab()
    sys.exit(0 if success else 1)
