#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Quick test script to check available plugins in Aetherra Hub
"""

import json
import urllib.request


def check_hub_plugins():
    try:
        response = urllib.request.urlopen("http://localhost:3001/api/plugins")
        data = json.loads(response.read())

        print("🔌 Available Plugins in Aetherra Hub:")
        print("=" * 50)
        print(f"Raw response type: {type(data)}")
        print(f"Raw response: {data}")

        if not data:
            print("No plugins found in Hub")
            return

        # Handle different response formats
        if isinstance(data, list):
            plugins = data
        elif isinstance(data, dict) and "plugins" in data:
            plugins = data["plugins"]
        else:
            print(f"Unexpected response format: {data}")
            return

        for i, plugin in enumerate(plugins, 1):
            if isinstance(plugin, str):
                # If plugins are just strings (names)
                print(f"{i}. {plugin}")
            elif isinstance(plugin, dict):
                name = plugin.get("name", "Unknown")
                description = plugin.get("description", "No description")
                version = plugin.get("version", "Unknown")
                category = plugin.get("category", "Uncategorized")

                print(f"{i}. {name} (v{version})")
                print(f"   Category: {category}")
                print(f"   Description: {description}")
            else:
                print(f"{i}. {plugin}")
            print()

    except Exception as e:
        print(f"Error connecting to Hub: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_hub_plugins()
