#!/usr/bin/env python3
"""
Quick test of plugin bridge functionality
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path().absolute()))

try:
    from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

    print("🧠 Testing Intelligence Stack plugin integration...")
    intelligence_stack = LyrixaIntelligenceStack(".")

    if (
        hasattr(intelligence_stack, "plugin_bridge")
        and intelligence_stack.plugin_bridge
    ):
        print("✅ Plugin bridge available")

        # Test discovered plugins property
        discovered = intelligence_stack.plugin_bridge.discovered_plugins
        print(f"📦 Discovered plugins cache: {len(discovered)} plugins")

        if discovered:
            print("First few plugins:")
            for i, (key, data) in enumerate(list(discovered.items())[:3]):
                name = data.get("name", "Unknown")
                desc = data.get("description", "No description")
                print(f"  {i + 1}. {key}: {name} - {desc}")

        # Test plugin summary for GUI
        summary = intelligence_stack.plugin_bridge.get_plugin_summary_for_gui()
        print(f"📊 Plugin summary: {summary['total_plugins']} total")
        print(f"   By type: {summary['by_type']}")
        print(f"   By status: {summary['by_status']}")

    else:
        print("❌ Plugin bridge not available")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
