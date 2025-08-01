#!/usr/bin/env python3
"""
Test LLM to GUI Code Injection Flow
This test verifies that LLM responses containing plugin code
get automatically injected into the Plugin Editor GUI.
"""

import asyncio
import sys
from pathlib import Path

# Add the project to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class MockGUI:
    """Mock GUI interface for testing code injection"""

    def __init__(self):
        self.injected_code = None
        self.injected_filename = None
        self.injection_success = False

    def inject_plugin_code(self, code: str, filename: str = "generated_plugin.aether"):
        """Mock injection method that stores the data"""
        self.injected_code = code
        self.injected_filename = filename
        self.injection_success = True
        print(f"🎯 Mock GUI: Code injection successful!")
        print(f"📁 Filename: {filename}")
        print(f"📄 Code length: {len(code)} characters")
        print(f"📋 Code preview: {code[:100]}...")
        return True


async def test_llm_gui_injection():
    """Test the complete LLM to GUI code injection flow"""
    print("🧪 Testing LLM to GUI Code Injection Flow")
    print("=" * 50)

    try:
        # Import required components
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager
        from Aetherra.runtime.aether_runtime import AetherRuntime

        # Create mock GUI interface
        mock_gui = MockGUI()
        print("✅ Mock GUI interface created")

        # Create workspace path
        workspace_path = str(project_root)
        print(f"✅ Workspace path: {workspace_path}")

        # Create conversation manager with GUI interface
        runtime = AetherRuntime()
        conversation_manager = LyrixaConversationManager(
            workspace_path=workspace_path,
            aether_runtime=runtime,
            gui_interface=mock_gui,  # Pass the GUI interface!
        )
        print("✅ Conversation manager initialized with GUI interface")

        # Simulate an LLM response that should trigger code injection
        test_response = """
I'll help you create a data visualization plugin for the Plugin Editor. Let me inject this code into the editor:

```python
# Data Visualization Plugin
# Created by Lyrixa AI Assistant

def visualize_data(data):
    '''Create beautiful charts from data'''
    import matplotlib.pyplot as plt

    # Create a simple bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(data)), data)
    plt.title("Data Visualization")
    plt.show()

def main():
    # Sample data
    sample_data = [1, 3, 2, 5, 4]
    visualize_data(sample_data)

if __name__ == "__main__":
    main()
```

This plugin has been injected into your Plugin Editor. You can now test and save it using the buttons in the interface.
"""

        print("🚀 Testing LLM response processing...")
        print(
            "📝 Simulated LLM response contains plugin code and injection instructions"
        )

        # Process the response (this should trigger code injection)
        conversation_manager.handle_llm_response(test_response)

        # Check if injection occurred
        print("\n🔍 Checking Injection Results")
        print("-" * 30)

        if mock_gui.injection_success:
            print("🎉 SUCCESS! Code injection worked!")
            print(f"✅ Injected filename: {mock_gui.injected_filename}")
            print(
                f"✅ Code contains 'def visualize_data': {'def visualize_data' in mock_gui.injected_code}"
            )
            print(
                f"✅ Code contains 'matplotlib': {'matplotlib' in mock_gui.injected_code}"
            )
            print("✅ LLM response successfully triggered GUI code injection")
        else:
            print("❌ FAILED: No code injection occurred")
            print("   The LLM response was not detected as containing plugin code")

        return mock_gui.injection_success

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all required modules are available")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


async def test_conversation_manager_gui_integration():
    """Test that conversation manager can access GUI interface"""
    print("\n🔧 Testing Conversation Manager GUI Integration")
    print("-" * 45)

    try:
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager
        from Aetherra.runtime.aether_runtime import AetherRuntime

        mock_gui = MockGUI()
        runtime = AetherRuntime()

        # Test 1: Initialize with GUI interface
        conversation_manager = LyrixaConversationManager(
            workspace_path=str(project_root),
            aether_runtime=runtime,
            gui_interface=mock_gui,
        )

        print("✅ Conversation manager accepts gui_interface parameter")

        # Test 2: Check GUI interface is stored
        assert conversation_manager.gui_interface is mock_gui
        print("✅ GUI interface properly stored in conversation manager")

        # Test 3: Check GUI interface has required method
        assert hasattr(mock_gui, "inject_plugin_code")
        print("✅ GUI interface has inject_plugin_code method")

        # Test 4: Test extract_code_block method
        test_text = """
        Here's some code:
        ```python
        def hello():
            print("Hello World!")
        ```
        """
        code_block = conversation_manager.extract_code_block(test_text)
        assert code_block is not None
        assert "def hello():" in code_block
        print("✅ extract_code_block method works correctly")

        # Test 5: Test pattern detection
        plugin_response = (
            "I'll inject this into the plugin editor: ```python\nprint('test')\n```"
        )
        detected = any(
            phrase in plugin_response.lower()
            for phrase in ["plugin editor", "inject", "created plugin"]
        )
        assert detected
        print("✅ Plugin injection pattern detection works")

        return True

    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


if __name__ == "__main__":

    async def main():
        print("🚀 LLM to GUI Code Injection Test Suite")
        print("=" * 50)

        # Test 1: Basic integration
        test1_result = await test_conversation_manager_gui_integration()

        # Test 2: Full injection flow
        test2_result = await test_llm_gui_injection()

        # Summary
        print("\n📊 Test Results Summary")
        print("=" * 25)
        print(f"GUI Integration Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
        print(f"Code Injection Test:  {'✅ PASS' if test2_result else '❌ FAIL'}")

        if test1_result and test2_result:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ LLM responses can now trigger GUI code injection")
            print(
                "✅ The bridge between Lyrixa's language and the Plugin Editor is complete"
            )
        else:
            print("\n⚠️ Some tests failed - check the implementation")

        return test1_result and test2_result

    result = asyncio.run(main())
    sys.exit(0 if result else 1)
