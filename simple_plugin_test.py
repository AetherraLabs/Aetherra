#!/usr/bin/env python3
"""
Simple Plugin System Test
========================
Test the current plugin system without complex initialization.
"""

import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager


async def simple_plugin_test():
    """Simple test of plugin discovery."""
    print("🔧 SIMPLE PLUGIN DISCOVERY TEST")
    print("=" * 40)

    try:
        # Create plugin manager with multiple directories
        print("📁 Creating plugin manager...")
        manager = LyrixaAdvancedPluginManager(
            plugin_directory="plugins",
            additional_directories=[
                "lyrixa/plugins",
                "src/aetherra/plugins",
                "sdk/plugins",
            ],
        )

        print("🔄 Initializing plugin manager...")
        await manager.initialize()

        print(f"✅ Plugin manager initialized!")
        print(f"   🔌 Plugins loaded: {len(manager.plugins)}")
        print(f"   📋 Metadata entries: {len(manager.plugin_metadata)}")
        print(f"   🔗 Plugin chains: {len(manager.plugin_chains)}")

        # List discovered plugins
        if manager.plugins:
            print("\n📋 Discovered plugins:")
            for name in manager.plugins.keys():
                print(f"   - {name}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(simple_plugin_test())
    print(f"\n📊 Test result: {'SUCCESS' if success else 'FAILED'}")
