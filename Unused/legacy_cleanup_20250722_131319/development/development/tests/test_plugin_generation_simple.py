"""
Simple Plugin Generation Test
Tests just the PluginGeneratorPlugin and PluginAgent integration
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from Aetherra.lyrixa.agents.plugin_agent import PluginAgent
from Aetherra.lyrixa.plugins.plugin_generator_plugin import PluginGeneratorPlugin


class MockMemory:
    async def store_memory(self, key, value, importance=0.5):
        print(f"📝 Memory stored: {key} (importance: {importance})")
        return True


class MockPromptEngine:
    def get_prompt(self, template, context=None):
        return f"Mock prompt for {template}"


class MockLLMManager:
    async def generate_response(self, prompt, context=None):
        return "Mock LLM response"


class MockIntelligenceStack:
    def __init__(self):
        self.memory_manager = MockMemory()
        self.plugin_bridge = None


async def test_plugin_generator_only():
    """Test PluginGeneratorPlugin directly"""
    print("🔌 Testing PluginGeneratorPlugin")
    print("=" * 40)

    generator = PluginGeneratorPlugin()

    # Test template listing
    templates = generator.list_templates()
    print(f"📚 Available Templates: {len(templates)}")
    for template in templates:
        print(f"  • {template['name']} ({template['category']})")

    print("\n🎯 Generating Test Plugins...")

    test_cases = [
        {
            "name": "DataVisualizerPlugin",
            "template": "ui_widget",
            "description": "A plugin for creating data visualizations",
        },
        {
            "name": "CSVProcessorPlugin",
            "template": "data_processor",
            "description": "A plugin for processing CSV files",
        },
        {
            "name": "PredictionModelPlugin",
            "template": "ml_model",
            "description": "A machine learning prediction plugin",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Generating {test_case['name']}...")

        try:
            plugin_id = generator.generate_plugin(
                plugin_name=test_case["name"],
                template_id=test_case["template"],
                description=test_case["description"],
                config={"test": True},
            )

            generated_plugin = generator.generated_plugins.get(plugin_id)
            if generated_plugin:
                print(f"   ✅ Success! ID: {plugin_id}")
                print(f"   📄 Files: {len(generated_plugin.files)}")
                print(f"   🏷️  Template: {generated_plugin.template_id}")

                # Show first few file names
                file_names = list(generated_plugin.files.keys())[:3]
                print(f"   📝 Sample files: {', '.join(file_names)}")

            else:
                print(f"   [ERROR] Generation failed - no plugin created")

        except Exception as e:
            print(f"   [ERROR] Error: {e}")

    # Show generator stats
    info = generator.get_info()
    print(f"\n📊 Final Stats:")
    print(f"  Templates: {info['stats']['templates_available']}")
    print(f"  Generated: {info['stats']['plugins_generated']}")
    print(f"  Categories: {info['stats']['categories']}")


async def test_plugin_agent_generation():
    """Test PluginAgent plugin generation handling"""
    print("\n🤖 Testing PluginAgent Generation")
    print("=" * 40)

    # Create mock dependencies
    mock_memory = MockMemory()
    mock_prompt = MockPromptEngine()
    mock_llm = MockLLMManager()
    mock_intelligence = MockIntelligenceStack()

    # Create plugin agent
    plugin_agent = PluginAgent(
        memory=mock_memory,
        prompt_engine=mock_prompt,
        llm_manager=mock_llm,
        intelligence_stack=mock_intelligence,
    )

    # Test generation requests
    test_inputs = [
        "generate plugin for data visualization",
        "create plugin to process CSV files",
        "make plugin for machine learning predictions",
        "build plugin for REST API integration",
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n{i}. Testing: '{test_input}'")
        print("-" * 30)

        try:
            response = await plugin_agent._handle_plugin_generation(test_input, {})

            print(f"✅ Response generated")
            print(f"📊 Confidence: {response.confidence}")
            print(f"🤖 Agent: {response.agent_name}")

            # Check metadata
            metadata = response.metadata or {}
            if metadata.get("generation_successful"):
                print(f"🎯 Generation successful!")
                print(f"🆔 Plugin ID: {metadata.get('plugin_id', 'N/A')}")
                print(f"🏷️  Template: {metadata.get('template_used', 'N/A')}")
            elif "error" in metadata:
                print(f"[ERROR] Error: {metadata['error']}")
            else:
                print("ℹ️  Basic response (no actual generation)")

            # Show response preview
            preview = (
                response.content[:150] + "..."
                if len(response.content) > 150
                else response.content
            )
            print(f"📝 Preview: {preview}")

        except Exception as e:
            print(f"[ERROR] Error processing: {e}")


async def test_name_and_type_detection():
    """Test the name extraction and type detection methods"""
    print("\n🔍 Testing Name & Type Detection")
    print("=" * 40)

    mock_memory = MockMemory()
    mock_prompt = MockPromptEngine()
    mock_llm = MockLLMManager()

    plugin_agent = PluginAgent(
        memory=mock_memory, prompt_engine=mock_prompt, llm_manager=mock_llm
    )

    test_cases = [
        "data visualization dashboard",
        "CSV file processor",
        "machine learning model for predictions",
        "REST API integration tool",
        "user interface widget for forms",
        "analyze performance metrics",
    ]

    for description in test_cases:
        name = plugin_agent._extract_plugin_name(description)
        plugin_type = plugin_agent._detect_plugin_type(description)

        print(f"📝 '{description}'")
        print(f"   → Name: {name}")
        print(f"   → Type: {plugin_type}")
        print()


async def main():
    """Run all tests"""
    print("🚀 Plugin Generation Component Test Suite")
    print("=" * 60)

    try:
        await test_plugin_generator_only()
        await test_plugin_agent_generation()
        await test_name_and_type_detection()

        print("\n" + "=" * 60)
        print("✅ All component tests completed!")

    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
