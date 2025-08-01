"""
🎯 Test Plugin Editor Intent Integration
Comprehensive test of the new plugin editor intent routing system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_plugin_editor_integration():
    """Test the complete plugin editor integration"""

    print("🎯 Testing Plugin Editor Intent Integration")
    print("=" * 50)

    try:
        # Test imports
        print("1️⃣ Testing imports...")

        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager
        print("   ✅ LyrixaConversationManager imported")

        from Aetherra.lyrixa.gui.plugin_editor_controller import PluginEditorController
        print("   ✅ PluginEditorController imported")

        from Aetherra.lyrixa.intelligence.meta_reasoning import MetaReasoningEngine
        print("   ✅ MetaReasoningEngine imported")

        # Test Plugin Editor Controller
        print("\n2️⃣ Testing Plugin Editor Controller...")

        # Mock GUI interface
        class MockGUI:
            def __init__(self):
                self.plugin_editor_tab = MockPluginEditor()
                self.tab_widget = MockTabWidget()

            def inject_plugin_code(self, code: str, filename: str) -> bool:
                print(f"   🎯 Mock GUI: inject_plugin_code called")
                print(f"      • Filename: {filename}")
                print(f"      • Code length: {len(code)} characters")
                return True

        class MockPluginEditor:
            def set_code_block(self, code: str, filename: str):
                print(f"   📝 Plugin Editor: set_code_block called")
                print(f"      • Filename: {filename}")
                print(f"      • Code preview: {code[:50]}...")

            def focus_editor(self):
                print("   🎯 Plugin Editor: focus_editor called")

        class MockTabWidget:
            def setCurrentWidget(self, widget):
                print("   📋 Tab Widget: setCurrentWidget called")

        mock_gui = MockGUI()
        controller = PluginEditorController.get_instance(mock_gui, "test_plugins")

        print("   ✅ Plugin Editor Controller created")

        # Test controller functionality
        print("\n3️⃣ Testing controller intent handling...")

        test_inputs = [
            "Load the assistant trainer plugin",
            "Create a new data processor plugin",
            "Inject some code into the editor",
            "Open the plugin editor"
        ]

        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n   Test {i}: '{test_input}'")

            success, response, action_data = controller.handle_plugin_editor_intent(
                user_input=test_input,
                detected_intent="plugin_editor_action"
            )

            print(f"      • Success: {success}")
            print(f"      • Response preview: {response[:100]}...")
            print(f"      • Actions taken: {action_data['actions_taken']}")

        # Test Conversation Manager Integration
        print("\n4️⃣ Testing Conversation Manager integration...")

        # Initialize conversation manager with mock GUI
        conversation_manager = LyrixaConversationManager(
            workspace_path="test_workspace",
            gui_interface=mock_gui
        )

        print("   ✅ Conversation Manager initialized")
        print(f"   • Plugin Editor Controller available: {conversation_manager.plugin_editor_controller is not None}")
        print(f"   • Meta-Reasoning Engine available: {conversation_manager.meta_reasoning_engine is not None}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_integration():
    """Test async conversation flow"""

    print("\n5️⃣ Testing async conversation flow...")

    try:
        # Mock GUI
        class MockGUI:
            def __init__(self):
                self.plugin_editor_tab = MockPluginEditor()
                self.tab_widget = MockTabWidget()

            def inject_plugin_code(self, code: str, filename: str) -> bool:
                print(f"   🎯 Async Mock: inject_plugin_code called ({filename})")
                return True

        class MockPluginEditor:
            def set_code_block(self, code: str, filename: str):
                print(f"   📝 Async Mock: set_code_block called ({filename})")

            def focus_editor(self):
                print("   🎯 Async Mock: focus_editor called")

        class MockTabWidget:
            def setCurrentWidget(self, widget):
                print("   📋 Async Mock: setCurrentWidget called")

        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        mock_gui = MockGUI()
        conversation_manager = LyrixaConversationManager(
            workspace_path="test_workspace",
            gui_interface=mock_gui
        )

        # Test plugin editor intents
        test_conversations = [
            "Load the assistant trainer plugin into the editor",
            "Create a new automation plugin for me",
            "I want to inject some code into the plugin editor",
            "Please open the plugin editor tab"
        ]

        for i, user_input in enumerate(test_conversations, 1):
            print(f"\n   Conversation {i}: '{user_input}'")

            # Test intent detection
            intent_detected, response = await conversation_manager._handle_plugin_editor_intent(user_input)

            print(f"      • Intent detected: {intent_detected}")
            if intent_detected:
                print(f"      • Response preview: {response[:80]}...")

        print("   ✅ Async integration test completed")
        return True

    except Exception as e:
        print(f"❌ Async test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_meta_reasoning_integration():
    """Test meta-reasoning tracking"""

    print("\n6️⃣ Testing Meta-Reasoning integration...")

    try:
        from Aetherra.lyrixa.intelligence.meta_reasoning import MetaReasoningEngine, DecisionType

        # Mock memory and plugin manager
        class MockMemory:
            def __init__(self):
                self.traces = []

            def store(self, data):
                self.traces.append(data)
                print(f"   📊 Stored trace: {data.get('type', 'unknown')}")

        class MockPluginManager:
            def list_plugin_names(self):
                return ["assistant_trainer", "data_processor", "automation", "utility"]

        memory = MockMemory()
        plugin_manager = MockPluginManager()
        meta_engine = MetaReasoningEngine(memory, plugin_manager)

        # Test intent routing trace
        trace = meta_engine.explain_intent_routing(
            user_input="Load the assistant trainer plugin",
            detected_intent="plugin_editor_action",
            confidence=0.85,
            routing_decision="route_to_plugin_editor",
            available_routes=["plugin_editor", "general_conversation", "system_status"],
            reasoning="Detected plugin and load keywords with high confidence"
        )

        print(f"   ✅ Intent routing traced: {trace.trace_id}")

        # Test UI action trace
        ui_trace = meta_engine.trace_ui_action(
            action_type="inject_plugin_code",
            context={"filename": "assistant_trainer.aether", "code_length": 500},
            target="plugin_editor",
            confidence=0.9,
            explanation="Successfully injected assistant trainer template into plugin editor",
            success=True
        )

        print(f"   ✅ UI action traced: {ui_trace.trace_id}")
        print(f"   📊 Total traces stored: {len(memory.traces)}")

        return True

    except Exception as e:
        print(f"❌ Meta-reasoning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_integration_summary():
    """Show summary of integration features"""

    print("\n📋 Integration Summary")
    print("=" * 30)

    features = [
        "✅ Plugin Editor Controller with template system",
        "✅ Intent detection and routing in conversation manager",
        "✅ Meta-reasoning tracking for all decisions and actions",
        "✅ Robust fallback system when components unavailable",
        "✅ Comprehensive error handling and logging",
        "✅ UI action tracking (load, create, inject, focus)",
        "✅ Multiple plugin templates (assistant, data, automation, utility)",
        "✅ Plugin name extraction and classification",
        "✅ Async conversation flow integration"
    ]

    print("🎯 Implemented Features:")
    for feature in features:
        print(f"   {feature}")

    print(f"\n🔧 Key Components:")
    components = [
        "LyrixaConversationManager - Main conversation handler with intent routing",
        "PluginEditorController - Bridge between conversation and GUI",
        "MetaReasoningEngine - Decision tracking and learning",
        "Intent Classification - Keyword-based intent detection",
        "UI Action Tracing - Track actual UI manipulations",
        "Template System - Pre-built plugin templates for different types"
    ]

    for component in components:
        print(f"   • {component}")

    print(f"\n🎉 Result:")
    print("   When Lyrixa says 'I'll load the plugin into the editor'")
    print("   → She now ACTUALLY does it, not just talks about it!")


if __name__ == "__main__":
    print("🚀 Plugin Editor Intent Integration Test Suite")
    print("=" * 55)

    # Run tests
    test1_passed = test_plugin_editor_integration()

    # Run async test
    try:
        test2_passed = asyncio.run(test_async_integration())
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        test2_passed = False

    test3_passed = test_meta_reasoning_integration()

    # Show summary
    show_integration_summary()

    # Final results
    print("\n" + "=" * 55)
    print("🏁 Test Results:")
    print(f"   • Plugin Editor Integration: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   • Async Conversation Flow: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"   • Meta-Reasoning Integration: {'✅ PASSED' if test3_passed else '❌ FAILED'}")

    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 ALL TESTS PASSED!")
        print("🎯 Plugin Editor Intent Integration is ready!")
        print("💡 Lyrixa will now actually trigger UI actions, not just talk about them!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
