#!/usr/bin/env python3
"""
Simplified Plugin Discovery Test
Tests the enhanced plugin system without external dependencies
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_plugin_discovery_simple():
    """Simple test of plugin discovery functionality"""
    print("🚀 aetherra PLUGIN DISCOVERY SYSTEM")
    print("=" * 50)

    try:
        # Import the plugin manager
        from core.plugin_manager import (
            PLUGIN_INTENTS,
            PLUGIN_METADATA,
            PLUGIN_REGISTRY,
            get_plugin_discovery_stats,
            list_plugins,
        )

        print("✅ Plugin manager imported successfully")
        print(f"[DISC] Registry: {len(PLUGIN_REGISTRY)} plugins")
        print(f"📋 Metadata: {len(PLUGIN_METADATA)} entries")
        print(f"🎯 Intents: {len(PLUGIN_INTENTS)} entries")

        # List available plugins
        plugins = list_plugins()
        print(f"\n📝 Available plugins: {plugins}")

        # Show plugin metadata
        for name in plugins:
            from core.plugin_manager import get_plugin_metadata

            meta = get_plugin_metadata(name)
            if meta:
                print(f"  • {name}: {meta.description}")
                print(f"    Category: {meta.category}")
                print(f"    Capabilities: {meta.capabilities}")

        # Show intent information
        print("\n🎯 Plugin Intents:")
        for name, intent in PLUGIN_INTENTS.items():
            print(f"  • {name}: {intent.purpose}")
            print(f"    Triggers: {intent.triggers}")

        # Get discovery stats
        stats = get_plugin_discovery_stats()
        print("\n📊 Discovery Statistics:")
        print(f"  Total plugins: {stats['total_plugins']}")
        print(f"  Plugins with intent: {stats['plugins_with_intent']}")
        print(f"  Intent coverage: {stats['intent_coverage']}")

        # Test simple discovery
        from core.plugin_manager import discover_plugins_by_intent

        test_queries = ["calculate math", "analyze text sentiment", "format code"]

        print("\n🔍 Testing Discovery:")
        for query in test_queries:
            results = discover_plugins_by_intent(query, max_results=2)
            print(f"  Query: '{query}' -> {len(results)} matches")
            for result in results:
                print(f"    - {result['name']} (score: {result['score']:.1f})")

        print("\n✅ Plugin discovery system is working!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_plugin_discovery_simple()
