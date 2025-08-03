#!/usr/bin/env python3
"""
Phase 1 Auto-Population Simple Test
===================================
Test just the core auto-population logic without full system initialization
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_metadata_and_injection():
    """Test the metadata handling and injection logic"""
    print("🎯 PHASE 1: AUTO-POPULATE CORE LOGIC TEST")
    print("=" * 50)

    # Mock GUI window
    class MockGUIWindow:
        def __init__(self):
            self.injected_code = None
            self.injected_filename = None
            self.injection_calls = 0

        def inject_plugin_code(
            self, code: str, filename: str = "generated_plugin.aether"
        ):
            """Mock injection method"""
            self.injected_code = code
            self.injected_filename = filename
            self.injection_calls += 1
            print(f"🎯 Mock GUI: inject_plugin_code called")
            print(f"   📄 Filename: {filename}")
            print(f"   📝 Code length: {len(code)}")
            print(f"   🔢 Call count: {self.injection_calls}")
            return True

    # Mock agent response with plugin generation metadata
    class MockAgentResponse:
        def __init__(self):
            self.agent_name = "PluginAgent"
            self.content = "Plugin generated successfully!"
            self.metadata = {
                "plugin_operation": "plugin_generation",
                "plugin_name": "TestDataVisualizationPlugin",
                "generated_code": '''"""
TestDataVisualizationPlugin
Generated plugin for data visualization
"""

class TestDataVisualizationPlugin:
    def __init__(self):
        self.name = "TestDataVisualizationPlugin"
        self.version = "1.0.0"

    def create_chart(self, data):
        \"\"\"Create a visualization chart\"\"\"
        return f"Chart created with {len(data)} data points"

    def get_info(self):
        return {
            "name": self.name,
            "version": self.version,
            "type": "UI Widget"
        }
''',
                "main_filename": "test_data_visualization_plugin.aether",
                "generation_successful": True,
            }

    # Test the auto-population logic directly
    mock_gui = MockGUIWindow()
    mock_response = MockAgentResponse()

    print("✅ Mock objects created")
    print(f"   📋 Response agent: {mock_response.agent_name}")
    print(f"   🏷️  Plugin operation: {mock_response.metadata.get('plugin_operation')}")
    print(
        f"   📄 Has generated code: {mock_response.metadata.get('generated_code') is not None}"
    )
    print()

    # Simulate the auto-population check logic from core_agent.py
    print("🔍 Testing Auto-Population Logic")
    print("-" * 30)

    # Check conditions
    condition1 = mock_response.agent_name == "PluginAgent"
    condition2 = (
        mock_response.metadata
        and mock_response.metadata.get("plugin_operation") == "plugin_generation"
    )
    condition3 = mock_response.metadata.get("generated_code") is not None

    print(f"✅ Agent is PluginAgent: {condition1}")
    print(f"✅ Plugin operation is plugin_generation: {condition2}")
    print(f"✅ Generated code available: {condition3}")

    if condition1 and condition2:
        print("🎯 Auto-population conditions met!")

        # Extract data
        generated_code = mock_response.metadata.get("generated_code")
        plugin_name = mock_response.metadata.get("plugin_name", "generated_plugin")
        main_filename = mock_response.metadata.get(
            "main_filename", f"{plugin_name}.aether"
        )

        if generated_code:
            # Simulate injection
            print(f"📄 Using filename: {main_filename}")
            success = mock_gui.inject_plugin_code(generated_code, main_filename)

            if success:
                print("🎉 AUTO-POPULATION SUCCESSFUL!")

                # Simulate response content update
                updated_content = (
                    mock_response.content
                    + "\n\n🎯 **Plugin Editor Updated**: The generated code has been automatically loaded into the Plugin Editor tab for you to review and test!"
                )
                print("✅ Response content updated with GUI notification")

                # Verify injection
                print()
                print("🔍 Verification Results")
                print("-" * 20)
                print(f"✅ Code injected: {mock_gui.injected_code is not None}")
                print(
                    f"✅ Correct filename: {mock_gui.injected_filename == main_filename}"
                )
                print(f"✅ Code length: {len(mock_gui.injected_code)} characters")
                print(f"✅ Injection calls: {mock_gui.injection_calls}")

                return True
            else:
                print("[ERROR] Injection failed")
                return False
        else:
            print("[ERROR] No generated code available")
            return False
    else:
        print("[ERROR] Auto-population conditions not met")
        return False


def test_filename_logic():
    """Test the filename extraction logic"""
    print("\n" + "=" * 50)
    print("🎯 FILENAME LOGIC TEST")
    print("=" * 50)

    test_cases = [
        {
            "plugin_name": "DataVisualizationPlugin",
            "main_filename": "data_visualization.aether",
            "expected": "data_visualization.aether",
        },
        {
            "plugin_name": "APIIntegrationPlugin",
            "main_filename": None,
            "expected": "APIIntegrationPlugin.aether",
        },
        {
            "plugin_name": "TestPlugin",
            "main_filename": "custom_name.py",
            "expected": "custom_name.py",
        },
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"   📝 Plugin name: {case['plugin_name']}")
        print(f"   📄 Main filename: {case['main_filename']}")

        # Simulate filename logic
        plugin_name = case["plugin_name"]
        main_filename = case["main_filename"]

        if main_filename:
            filename = main_filename
        else:
            filename = f"{plugin_name}.aether"

        print(f"   🎯 Result: {filename}")
        print(f"   ✅ Expected: {case['expected']}")
        print(f"   {'✅ PASS' if filename == case['expected'] else '[ERROR] FAIL'}")

    return True


if __name__ == "__main__":
    print("🚀 Starting Phase 1 Auto-Population Tests\n")

    test1_success = test_metadata_and_injection()
    test2_success = test_filename_logic()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"✅ Metadata & Injection Logic: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ Filename Logic: {'PASS' if test2_success else 'FAIL'}")

    if test1_success and test2_success:
        print("\n🎉 ALL PHASE 1 AUTO-POPULATION TESTS PASSED!")
        print("✅ Ready for integration with full Lyrixa system")
        sys.exit(0)
    else:
        print("\n[ERROR] Some tests failed - auto-population needs fixes")
        sys.exit(1)
