#!/usr/bin/env python3
"""
Plugin Discovery Test
====================
Test the multi-directory plugin discovery system.
"""

import asyncio

from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager


async def test_plugin_discovery():
    """Test plugin discovery with multiple directories."""
    print("🔍 TESTING PLUGIN DISCOVERY")
    print("=" * 40)

    # Initialize plugin manager with multiple directories
    plugins = LyrixaAdvancedPluginManager(
        plugin_directory="plugins",
        additional_directories=[
            "lyrixa/plugins",
            "src/aetherra/plugins",
            "sdk/plugins",
        ],
    )

    # Initialize to trigger auto-discovery
    await plugins.initialize()

    print(f"\n📊 DISCOVERY RESULTS:")
    print(f"   🔌 Total plugins loaded: {len(plugins.plugins)}")
    print(f"   📋 Plugin metadata entries: {len(plugins.plugin_metadata)}")

    if plugins.plugins:
        print(f"\n✅ DISCOVERED PLUGINS:")
        for name, plugin_info in plugins.plugins.items():
            status = plugin_info.get("status", "unknown")
            file_path = plugin_info.get("file_path", "unknown")
            print(f"   - {name} ({status}) - {file_path}")

    if plugins.plugin_metadata:
        print(f"\n📋 PLUGIN METADATA:")
        for name, metadata in plugins.plugin_metadata.items():
            print(f"   - {name}: {getattr(metadata, 'description', 'No description')}")

    # Check for plugin chains
    if hasattr(plugins, "plugin_chains"):
        print(f"\n🔗 Plugin chains: {len(plugins.plugin_chains)}")

    print(f"\n🎉 Plugin discovery test completed!")
    return len(plugins.plugins) > 0


if __name__ == "__main__":
    result = asyncio.run(test_plugin_discovery())
    print(f"\n📈 Success: {result}")
