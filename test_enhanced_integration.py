#!/usr/bin/env python3
"""
Test the enhanced plugin capabilities integration
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from enhanced_plugin_capabilities import PluginCapabilityExtractor

    print("✅ Enhanced capability extractor imported successfully")

    extractor = PluginCapabilityExtractor()

    # Test with a known plugins directory
    plugins_dirs = [
        "Aetherra/plugins",
        "src/aetherra/plugins",
        "plugins"
    ]

    all_plugins = []

    for plugins_dir in plugins_dirs:
        if os.path.exists(plugins_dir):
            print(f"🧩 Found plugins directory: {plugins_dir}")
            plugins_in_dir = extractor.bulk_extract_plugins(plugins_dir)
            print(f"   Extracted {len(plugins_in_dir)} plugins")
            all_plugins.extend(plugins_in_dir)

    # Create API response format
    summary = {
        "total_plugins": len(all_plugins),
        "high_confidence": len([p for p in all_plugins if p.get("confidence_score", 0) > 0.8]),
        "categories": {},
        "top_capabilities": {}
    }

    # Calculate category distribution
    for plugin in all_plugins:
        category = plugin.get("category", "unknown")
        summary["categories"][category] = summary["categories"].get(category, 0) + 1

    response = {
        "plugins": all_plugins[:3],  # Show first 3 for testing
        "summary": summary,
        "status": "success",
        "extraction_method": "enhanced_capability_extractor"
    }

    print("\n📊 API Response Sample:")
    print(json.dumps(response, indent=2))

    print(f"\n✅ Enhanced capabilities system working! Found {len(all_plugins)} plugins total")

except Exception as e:
    print(f"❌ Error testing enhanced capabilities: {e}")
    import traceback
    traceback.print_exc()
