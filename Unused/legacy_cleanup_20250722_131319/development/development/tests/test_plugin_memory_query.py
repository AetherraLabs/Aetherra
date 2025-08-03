#!/usr/bin/env python3
"""
Test plugin memory integration - check if plugins are queryable from memory
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path().absolute()))


async def test_plugin_memory_query():
    try:
        from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

        print("🧠 Testing plugin memory integration...")
        intelligence_stack = LyrixaIntelligenceStack(".")

        # Initialize plugin discovery integration
        if (
            hasattr(intelligence_stack, "plugin_bridge")
            and intelligence_stack.plugin_bridge
        ):
            print("🔗 Initializing plugin discovery integration...")
            success = await intelligence_stack.initialize_plugin_discovery_integration()
            print(
                f"Plugin discovery integration: {'✅ Success' if success else '[ERROR] Failed'}"
            )

            if success and intelligence_stack.intelligence:
                print("🔍 Querying plugins from intelligence memory...")
                try:
                    # Query for plugin patterns in memory
                    plugin_memories = (
                        intelligence_stack.intelligence.get_memory_patterns("plugin")
                    )
                    print(f"Found {len(plugin_memories)} plugin patterns in memory")

                    if plugin_memories:
                        print("First 3 plugins found in memory:")
                        for i, (pattern_id, memory_data) in enumerate(
                            list(plugin_memories.items())[:3]
                        ):
                            content = memory_data.get("content", {})
                            plugin_name = content.get("plugin_name", "Unknown")
                            plugin_type = content.get("plugin_type", "Unknown")
                            description = content.get("description", "No description")
                            print(
                                f"  {i + 1}. {plugin_name} ({plugin_type}): {description}"
                            )

                    # Test plugin recommendations
                    print("🎯 Testing plugin recommendations...")
                    recommendations = (
                        await intelligence_stack.get_plugin_recommendations_for_lyrixa(
                            "file management"
                        )
                    )
                    print(
                        f'Recommendations for "file management": {len(recommendations)} plugins'
                    )

                    for rec in recommendations[:2]:
                        print(
                            f"  - {rec.get('name', 'Unknown')}: {rec.get('description', 'No description')}"
                        )

                except Exception as e:
                    print(f"[ERROR] Error querying plugin memory: {e}")
            else:
                print("[ERROR] Intelligence system not available")
        else:
            print("[ERROR] Plugin bridge not available")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_plugin_memory_query())
