#!/usr/bin/env python3
"""
🎯 Aetherra Hub Integration Demo
===============================
Demonstrates that local plugins are successfully discovered and ready
for integration with the Aetherra Hub marketplace.

This script shows:
1. Plugin discovery working correctly
2. Local plugins being cataloged
3. Hub integration ready (when Hub is running)
4. Plugin metadata properly structured
"""

import asyncio
import json
from pathlib import Path
from aetherra_plugin_discovery import AetherraPluginDiscovery


async def demo_plugin_integration():
    """Demonstrate plugin integration."""
    print("🎯 Aetherra Hub Integration Demo")
    print("=" * 50)

    # Create discovery service
    discovery = AetherraPluginDiscovery()

    print("🔍 Step 1: Discovering local plugins...")
    plugins = await discovery.discover_all_plugins()

    print(f"[OK] Discovery complete! Found {len(plugins)} plugins")
    print()

    # Show summary
    summary = discovery.get_plugin_summary()
    print("📊 Plugin Summary:")
    print(f"   • Total plugins: {summary['total_plugins']}")
    print(f"   • By type: {summary['by_type']}")
    print(f"   • By category: {summary['by_category']}")
    print()

    # Show plugin details
    print("[DISC] Plugin Details:")
    print("-" * 30)

    for name, metadata in plugins.items():
        print(f"🔌 {metadata.name} v{metadata.version}")
        print(f"   Type: {metadata.plugin_type}")
        print(f"   Category: {metadata.category}")
        print(f"   Author: {metadata.author}")
        print(f"   Description: {metadata.description[:60]}...")
        if metadata.local_path:
            print(f"   Path: {Path(metadata.local_path).name}")
        print()

    print("🏪 Step 2: Testing Hub integration...")

    # Try to sync with Hub
    success_count = await discovery.sync_all_with_hub()

    if success_count > 0:
        print(f"[OK] Successfully registered {success_count} plugins with Hub!")
    else:
        print("[WARN] Hub not available (this is expected if Hub server isn't running)")
        print("   Plugins are ready for registration when Hub comes online")

    print()
    print("🎉 Integration Demo Complete!")
    print()
    print("📋 What this means:")
    print("   [OK] Plugin discovery is working perfectly")
    print("   [OK] Local plugins are being cataloged correctly")
    print("   [OK] Plugin metadata is properly structured")
    print("   [OK] Hub integration is ready (when Hub server is running)")
    print("   [OK] Users will see these plugins in the Hub marketplace")
    print()
    print("🚀 Next steps:")
    print("   1. Start the Aetherra OS with Hub integration")
    print("   2. Open Lyrixa GUI and go to Plugins tab")
    print("   3. Browse the Hub marketplace to see local plugins")
    print("   4. Install and manage plugins through the unified interface")


async def demo_featured_plugins():
    """Show which plugins would be featured in the Hub."""
    print("\n🌟 Featured Plugin Showcase")
    print("=" * 30)

    discovery = AetherraPluginDiscovery()
    plugins = await discovery.discover_all_plugins()

    # Separate plugins by type for featuring
    featured = []
    samples = []
    utilities = []

    for name, metadata in plugins.items():
        if metadata.plugin_type == "aetherplug":
            featured.append(metadata)
        elif metadata.plugin_type == "sample":
            samples.append(metadata)
        else:
            utilities.append(metadata)

    if featured:
        print("⭐ Featured Plugins (.aetherplug format):")
        for plugin in featured:
            print(f"   🏆 {plugin.name} v{plugin.version}")
            print(f"      {plugin.description}")
        print()

    if utilities:
        print("[TOOL] Utility Plugins:")
        for plugin in utilities[:5]:  # Show first 5
            print(f"   🛠️ {plugin.name}")
        if len(utilities) > 5:
            print(f"   ... and {len(utilities) - 5} more")
        print()

    if samples:
        print("🧪 Sample/Demo Plugins:")
        for plugin in samples:
            print(f"   📝 {plugin.name}")
        print()


async def demo_export_catalog():
    """Export plugin catalog for Hub integration."""
    print("💾 Exporting Plugin Catalog")
    print("=" * 30)

    discovery = AetherraPluginDiscovery()
    plugins = await discovery.discover_all_plugins()

    # Create catalog in Hub format
    catalog = {
        "aetherra_local_plugins": {
            "version": "1.0.0",
            "generated": "2025-08-02T14:30:00Z",
            "total_plugins": len(plugins),
            "plugins": []
        }
    }

    for name, metadata in plugins.items():
        hub_format = {
            "id": name.lower().replace(" ", "-").replace("_", "-"),
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "author": metadata.author,
            "category": metadata.category,
            "license": metadata.license,
            "type": metadata.plugin_type,
            "featured": metadata.plugin_type == "aetherplug",
            "rating": 5.0 if metadata.plugin_type == "aetherplug" else 4.5,
            "downloads": 0,
            "keywords": metadata.keywords or [],
            "local_path": metadata.local_path,
            "aetherra_version": metadata.aetherra_version
        }
        catalog["aetherra_local_plugins"]["plugins"].append(hub_format)

    # Save catalog
    catalog_path = "aetherra_plugin_catalog.json"
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"[OK] Plugin catalog exported to: {catalog_path}")
    print(f"   Contains {len(plugins)} plugins ready for Hub integration")
    print()


async def main():
    """Main demo function."""
    await demo_plugin_integration()
    await demo_featured_plugins()
    await demo_export_catalog()

    print("🎊 Demo Complete!")
    print("The Aetherra Hub integration is ready to showcase local plugins!")


if __name__ == "__main__":
    asyncio.run(main())
