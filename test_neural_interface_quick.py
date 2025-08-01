#!/usr/bin/env python3
"""
Quick Neural Interface Integration Test
======================================

Simple integration test to verify the Neural Interface can be launched
and basic functionality works correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "Aetherra"
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_neural_interface_quick():
    """Quick test of Neural Interface functionality"""

    print("🧪 QUICK NEURAL INTERFACE TEST")
    print("=" * 40)

    try:
        # Test Qt availability
        from PySide6.QtWidgets import QApplication

        print("✅ Qt framework available")

        # Test GUI components import
        from gui.aetherra_neural_interface import (
            AetherraNeralInterface,
            create_aetherra_neural_interface,
        )

        print("✅ GUI components imported successfully")

        # Create application if needed
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        # Test interface creation
        interface = AetherraNeralInterface()
        print("✅ Main interface created")

        # Test basic properties
        assert hasattr(interface, "tabs"), "Interface should have tabs"
        assert hasattr(interface, "lyrixa_core"), "Interface should have Lyrixa Core"
        assert hasattr(interface, "chat_interface"), (
            "Interface should have Chat Interface"
        )
        assert hasattr(interface, "memory_graph"), "Interface should have Memory Graph"
        print("✅ Interface components verified")

        # Test tab count
        expected_tab_count = 10
        actual_tab_count = interface.tabs.count()
        assert actual_tab_count == expected_tab_count, (
            f"Expected {expected_tab_count} tabs, got {actual_tab_count}"
        )
        print(f"✅ All {actual_tab_count} tabs created")

        # Test Lyrixa Core functionality
        lyrixa_core = interface.lyrixa_core
        assert hasattr(lyrixa_core, "aura"), "Lyrixa Core should have aura widget"
        assert hasattr(lyrixa_core, "goals_list"), "Lyrixa Core should have goals list"
        assert lyrixa_core.goals_list.count() > 0, "Goals list should have items"
        print("✅ Lyrixa Core functional")

        # Test Chat Interface
        chat = interface.chat_interface
        assert hasattr(chat, "chat_display"), "Chat should have display"
        assert hasattr(chat, "message_input"), "Chat should have input"
        print("✅ Chat Interface functional")

        # Test Memory Graph
        memory_graph = interface.memory_graph
        assert hasattr(memory_graph, "scene"), "Memory graph should have scene"
        assert hasattr(memory_graph, "view"), "Memory graph should have view"
        assert len(memory_graph.scene.items()) > 0, "Memory graph should have nodes"
        print("✅ Memory Graph functional")

        # Test creation function
        app2, window2 = create_aetherra_neural_interface()
        assert app2 is not None, "Creation function should return app"
        assert window2 is not None, "Creation function should return window"
        print("✅ Creation function working")

        print("\n🎉 ALL TESTS PASSED!")
        print("Neural Interface is fully functional and ready for use.")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_neural_interface_quick()
    sys.exit(0 if success else 1)
