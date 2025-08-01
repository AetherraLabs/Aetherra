"""
Test Plugin Generation Flow Integration
Tests the complete plugin generation workflow including:
- Core Agent enhanced routing
- PluginAgent generation handling
- PluginGeneratorPlugin integration
- Memory logging
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from Aetherra.lyrixa.agents.core_agent import LyrixaAI
from Aetherra.lyrixa.agents.plugin_agent import PluginAgent
from Aetherra.lyrixa.intelligence import LyrixaIntelligenceStack
from Aetherra.lyrixa.plugins.plugin_generator_plugin import PluginGeneratorPlugin


async def test_plugin_generation_flow():
    """Test complete plugin generation workflow"""
    print("🔧 Testing Plugin Generation Flow")
    print("=" * 50)

    # Initialize components
    intelligence_stack = LyrixaIntelligenceStack()
    await intelligence_stack.initialize()

    plugin_agent = PluginAgent(
        memory=intelligence_stack.memory_manager,
        prompt_engine=intelligence_stack.prompt_engine,
        llm_manager=intelligence_stack.llm_manager,
        intelligence_stack=intelligence_stack,
    )

    core_agent = LyrixaAI(
        runtime=None,  # Not needed for this test
        memory=intelligence_stack.memory_manager,
        prompt_engine=intelligence_stack.prompt_engine,
        llm_manager=intelligence_stack.llm_manager,
        intelligence_stack=intelligence_stack,
    )

    # Add plugin agent to core agent
    core_agent.agents["plugin"] = plugin_agent

    # Test cases
    test_cases = [
        {
            "input": "generate plugin for data visualization",
            "expected_operation": "plugin_generation",
            "expected_type": "UI Widget",
        },
        {
            "input": "create plugin to process CSV files",
            "expected_operation": "plugin_generation",
            "expected_type": "Data Processor",
        },
        {
            "input": "make plugin for machine learning predictions",
            "expected_operation": "plugin_generation",
            "expected_type": "ML Model",
        },
        {
            "input": "build plugin for REST API integration",
            "expected_operation": "plugin_generation",
            "expected_type": "API Integration",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['input']}")
        print("-" * 40)

        # Test enhanced routing
        plugin_route = await core_agent._enhanced_plugin_routing(test_case["input"])
        print(f"🔀 Enhanced Routing Result: {plugin_route}")

        if plugin_route != test_case["expected_operation"]:
            print(
                f"❌ Routing failed! Expected: {test_case['expected_operation']}, Got: {plugin_route}"
            )
            continue

        # Test full flow through core agent
        response = await core_agent.process_input(test_case["input"])
        print(f"🤖 Agent Response: {response.agent_name}")
        print(f"📊 Confidence: {response.confidence}")
        print(f"📝 Content Preview: {response.content[:200]}...")

        # Check metadata for generation success
        metadata = response.metadata or {}
        if metadata.get("generation_successful"):
            print("✅ Plugin generation completed successfully!")
            print(f"🆔 Plugin ID: {metadata.get('plugin_id', 'N/A')}")
            print(f"📄 Files Generated: {len(metadata.get('files_generated', []))}")
            print(f"🏷️  Template Used: {metadata.get('template_used', 'N/A')}")
        elif "error" in metadata:
            print(f"❌ Generation error: {metadata['error']}")
        else:
            print("⚠️  Generation status unclear")

        print()


async def test_plugin_generator_directly():
    """Test PluginGeneratorPlugin directly"""
    print("\n🔌 Testing PluginGeneratorPlugin Directly")
    print("=" * 50)

    generator = PluginGeneratorPlugin()

    # Test template listing
    templates = generator.list_templates()
    print(f"📚 Available Templates: {len(templates)}")
    for template in templates:
        print(f"  • {template['name']} ({template['type']})")

    # Test plugin generation
    print("\n🎯 Generating Test Plugin...")
    plugin_id = generator.generate_plugin(
        plugin_name="TestVisualizationPlugin",
        template_id="ui_widget",
        description="A test plugin for data visualization",
        config={"test": True},
    )

    print(f"✅ Generated Plugin ID: {plugin_id}")

    # Check generated plugin
    generated_plugin = generator.generated_plugins.get(plugin_id)
    if generated_plugin:
        print(f"📝 Plugin Name: {generated_plugin.name}")
        print(f"🏷️  Template: {generated_plugin.template_id}")
        print(f"📄 Files: {len(generated_plugin.files)}")
        print("   Generated files:")
        for filename in generated_plugin.files.keys():
            print(f"     - {filename}")

    # Test plugin info
    info = generator.get_info()
    print(f"\n📊 Generator Stats:")
    print(f"  Templates: {info['stats']['templates_available']}")
    print(f"  Generated: {info['stats']['plugins_generated']}")
    print(f"  Categories: {info['stats']['categories']}")


async def test_memory_integration():
    """Test memory logging of generated plugins"""
    print("\n🧠 Testing Memory Integration")
    print("=" * 50)

    intelligence_stack = IntelligenceStack()
    await intelligence_stack.initialize()

    plugin_agent = PluginAgent(
        memory=intelligence_stack.memory_manager,
        prompt_engine=intelligence_stack.prompt_engine,
        llm_manager=intelligence_stack.llm_manager,
        intelligence_stack=intelligence_stack,
    )

    # Test plugin generation with memory logging
    response = await plugin_agent._handle_plugin_generation(
        "create plugin for file management", {}
    )

    print(f"📝 Response: {response.content[:200]}...")
    print(f"📊 Confidence: {response.confidence}")

    metadata = response.metadata or {}
    if metadata.get("plugin_id"):
        print(f"🆔 Plugin logged with ID: {metadata['plugin_id']}")
        print("✅ Memory integration working!")
    else:
        print("⚠️  No plugin ID in metadata")


async def main():
    """Run all tests"""
    print("🚀 Plugin Generation Flow Test Suite")
    print("=" * 60)

    try:
        await test_plugin_generator_directly()
        await test_plugin_generation_flow()
        await test_memory_integration()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
