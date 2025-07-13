#!/usr/bin/env python3
"""
Phase 1 Auto-Population System Test
===================================
Test the complete flow of AI-generated plugin code being auto-populated into the GUI
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_auto_population_flow():
    """Test the complete auto-population system"""
    print("🎯 PHASE 1: AUTO-POPULATE PLUGIN EDITOR TEST")
    print("=" * 60)

    try:
        # Import required components
        from Aetherra.intelligence.lyrixa_intelligence_stack import (
            LyrixaIntelligenceStack,
        )
        from Aetherra.llm.multi_llm_manager import MultiLLMManager
        from Aetherra.lyrixa.agents.core_agent import LyrixaAI
        from Aetherra.memory.base_memory import LyrixaMemory
        from Aetherra.prompt.prompt_engine import PromptEngine
        from Aetherra.runtime.aether_runtime import AetherRuntime

        print("✅ All imports successful")

        # Initialize components
        memory = LyrixaMemory()
        prompt_engine = PromptEngine()
        llm_manager = MultiLLMManager()
        workspace_path = str(Path(__file__).parent)
        intelligence_stack = LyrixaIntelligenceStack(workspace_path)
        runtime = AetherRuntime()

        # Mock GUI window (for testing without actual GUI)
        class MockGUIWindow:
            def __init__(self):
                self.injected_code = None
                self.injected_filename = None
                self.injection_success = False

            def inject_plugin_code(
                self, code: str, filename: str = "generated_plugin.aether"
            ):
                """Mock injection method that stores the data"""
                self.injected_code = code
                self.injected_filename = filename
                self.injection_success = True
                print(f"🎯 Mock GUI: Received code injection for {filename}")
                print(f"📄 Code length: {len(code)} characters")
                return True

        # Create LyrixaAI with mock GUI interface
        mock_gui = MockGUIWindow()
        lyrixa = LyrixaAI(
            runtime, memory, prompt_engine, llm_manager, intelligence_stack, mock_gui
        )

        print("✅ Components initialized with mock GUI interface")

        # Initialize the system
        await lyrixa.initialize()
        await intelligence_stack.initialize_plugin_discovery_integration()

        print("✅ System initialization complete")
        print()

        # Test plugin generation with auto-population
        print("🚀 Testing Plugin Generation with Auto-Population")
        print("-" * 50)

        test_request = "generate plugin for data visualization charts"
        print(f"📝 Request: '{test_request}'")

        # Process the request
        response = await lyrixa.process_input(test_request)

        print(f"✅ Response received:")
        print(f"   🎯 Agent: {response.agent_name}")
        print(f"   📊 Confidence: {response.confidence}")
        print(
            f"   🏷️  Metadata keys: {list(response.metadata.keys()) if response.metadata else 'None'}"
        )

        # Check if auto-population occurred
        print()
        print("🔍 Checking Auto-Population Results")
        print("-" * 40)

        if mock_gui.injection_success:
            print("🎉 AUTO-POPULATION SUCCESS!")
            print(f"✅ Code injected: {mock_gui.injected_code is not None}")
            print(f"✅ Filename: {mock_gui.injected_filename}")
            if mock_gui.injected_code:
                print(f"✅ Code length: {len(mock_gui.injected_code)} characters")
                print("📋 Code preview:")
                print(
                    mock_gui.injected_code[:200] + "..."
                    if len(mock_gui.injected_code) > 200
                    else mock_gui.injected_code
                )
        else:
            print("❌ AUTO-POPULATION FAILED!")
            print("   No code was injected into mock GUI")

        # Check response metadata for auto-population indicators
        if response.metadata:
            plugin_operation = response.metadata.get("plugin_operation")
            generated_code = response.metadata.get("generated_code")
            plugin_name = response.metadata.get("plugin_name")

            print()
            print("📊 Metadata Analysis:")
            print(f"   🔀 Plugin Operation: {plugin_operation}")
            print(f"   📄 Generated Code Available: {generated_code is not None}")
            print(f"   🏷️  Plugin Name: {plugin_name}")

            if plugin_operation == "plugin_generation" and generated_code:
                print("✅ All metadata requirements met for auto-population")
            else:
                print("⚠️ Missing metadata requirements for auto-population")

        print()
        print("=" * 60)
        print("🎯 AUTO-POPULATION SYSTEM TEST COMPLETE")

        # Summary
        if (
            mock_gui.injection_success
            and response.metadata
            and response.metadata.get("generated_code")
        ):
            print("🎉 PHASE 1 AUTO-POPULATION: FULLY OPERATIONAL!")
            print("✅ AI generates plugin code")
            print("✅ Metadata includes generated code")
            print("✅ GUI injection method works")
            print("✅ Auto-population bridge functional")
            return True
        else:
            print("❌ PHASE 1 AUTO-POPULATION: NEEDS DEBUGGING")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_auto_population_flow())
    sys.exit(0 if success else 1)
