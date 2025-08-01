#!/usr/bin/env python3
"""
Test the enhanced LyrixaAI plugin routing system
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path().absolute()))


async def test_lyrixa_plugin_routing():
    try:
        # Import the necessary components
        from Aetherra.core.memory_manager import MemoryManager
        from Aetherra.core.multi_llm_manager import MultiLLMManager
        from Aetherra.core.prompt_engine import PromptEngine
        from Aetherra.lyrixa.agents.core_agent import LyrixaAI
        from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

        print("🧠 Testing Enhanced LyrixaAI Plugin Routing...")

        # Initialize components
        memory = MemoryManager()
        prompt_engine = PromptEngine()
        llm_manager = MultiLLMManager()
        intelligence_stack = LyrixaIntelligenceStack(".")

        # Initialize LyrixaAI with intelligence stack
        lyrixa = LyrixaAI(None, memory, prompt_engine, llm_manager, intelligence_stack)
        await lyrixa.initialize()

        # Initialize plugin discovery
        await intelligence_stack.initialize_plugin_discovery_integration()

        print("✅ LyrixaAI initialized with plugin support")

        # Test different plugin-related queries
        test_queries = [
            "list plugins",
            "find plugin for file management",
            "show available plugins",
            "info about sysmon",
            "generate plugin for text processing",
            "what plugins do you have?",
        ]

        print(f"🔍 Testing {len(test_queries)} plugin queries...")

        for i, query in enumerate(test_queries, 1):
            print(f'\n--- Test {i}: "{query}" ---')
            try:
                response = await lyrixa.process_input(query)
                print(f"Agent: {response.agent_name}")
                print(f"Confidence: {response.confidence:.2f}")
                print(f"Response Preview: {response.content[:200]}...")
            except Exception as e:
                print(f"❌ Error: {e}")

        # Test utility methods
        print(f"\n🔧 Testing utility methods...")

        # Test get_available_plugins
        plugins = await lyrixa.get_available_plugins()
        print(f"Available plugins: {plugins.get('total_plugins', 0)} total")

        # Test summarize_plugin
        if plugins.get("plugins"):
            first_plugin = plugins["plugins"][0]
            plugin_name = first_plugin.get("name", "sysmon")
            summary = await lyrixa.summarize_plugin(plugin_name)
            print(
                f'Plugin summary for "{plugin_name}": {"✅ Found" if summary.get("found") else "❌ Not found"}'
            )

        print(f"\n✅ Enhanced plugin routing test complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_lyrixa_plugin_routing())
