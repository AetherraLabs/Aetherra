#!/usr/bin/env python3
"""
Test Plugin Capabilities Fix
============================

Test the fix for the plugin capabilities endpoint.
"""

import json

import requests


def test_plugin_capabilities_fix():
    """Test the plugin capabilities endpoint that was returning 404."""

    print("Testing Plugin Capabilities API Fix...")
    print("=" * 45)

    try:
        response = requests.get(
            "http://127.0.0.1:8005/api/plugins/capabilities", timeout=5
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Plugin capabilities endpoint working!")
            print(f"   Found {data.get('count', 0)} plugins")
            print(f"   Status: {data.get('status', 'unknown')}")

            # Show first few plugins as examples
            plugins = data.get("plugins", [])
            if plugins:
                print(f"\n📋 Sample plugins:")
                for i, plugin in enumerate(plugins[:3]):
                    print(f"   {i + 1}. {plugin.get('name', 'Unknown')}")
                    print(f"      Type: {plugin.get('type', 'unknown')}")
                    print(f"      Status: {plugin.get('status', 'unknown')}")

                if len(plugins) > 3:
                    print(f"   ... and {len(plugins) - 3} more plugins")

            return True

        elif response.status_code == 404:
            print("❌ ERROR: Endpoint still returning 404 - Not Found")
            print("   The endpoint might not be implemented or the path is incorrect")
            return False

        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Could not connect to API server")
        print("   Make sure the server is running on http://127.0.0.1:8005")
        return False

    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False


if __name__ == "__main__":
    success = test_plugin_capabilities_fix()
    print("\n" + "=" * 45)
    if success:
        print("🎉 Plugin capabilities endpoint is working!")
        print("✅ The 'Refresh Plugin Capabilities' button should now work in the UI.")
    else:
        print("❌ Plugin capabilities endpoint still has issues.")

    print("\nTo test in UI:")
    print("1. Open Lyrixa launcher")
    print("2. Go to 'Plugin Intelligence' tab")
    print("3. Click 'Refresh Plugin Capabilities'")
    print("4. Should see list of available plugins instead of 404 error")
