#!/usr/bin/env python3
"""
Direct Plugin Test
================
Test plugin discovery without memory system complications.
"""

import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager


async def test_plugin_discovery_direct():
    """Test plugin discovery directly without memory system."""
    print("[TOOL] DIRECT PLUGIN DISCOVERY TEST")
    print("=" * 40)

    try:
        # Create plugin manager without memory system
        print("📁 Creating plugin manager (no memory system)...")
        manager = LyrixaAdvancedPluginManager(
            plugin_directory="plugins",
            memory_system=None,  # No memory system to avoid chain loading issues
            additional_directories=[
                "lyrixa/plugins",
                "src/aetherra/plugins",
                "sdk/plugins",
            ],
        )

        print("🔄 Starting plugin discovery...")
        await manager._auto_discover_plugins()

        print(f"📊 Discovery Results:")
        print(f"   🔌 Plugins loaded: {len(manager.plugins)}")
        print(f"   📋 Metadata entries: {len(manager.plugin_metadata)}")

        # List discovered plugins
        if manager.plugins:
            print("\n📋 Discovered plugins:")
            for name, info in manager.plugins.items():
                status = info.get("status", "unknown")
                print(f"   - {name} ({status})")
        else:
            print("\n❌ No plugins discovered!")

        return len(manager.plugins) > 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_plugin_discovery_direct())
    print(f"\n📊 Test result: {'SUCCESS' if success else 'FAILED'}")
    print(f"🎯 Expected: Should find ~20 plugins based on our repair tool results")
