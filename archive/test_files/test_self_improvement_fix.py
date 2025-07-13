#!/usr/bin/env python3
"""
Test Self-Improvement Propose Changes Fix
==========================================

Test the fix for the self-improvement propose changes endpoint.
"""

import json

import requests


def test_self_improvement_fix():
    """Test the self-improvement propose changes endpoint that was returning 404."""

    print("Testing Self-Improvement Propose Changes API Fix...")
    print("=" * 50)

    try:
        response = requests.post(
            "http://127.0.0.1:8005/api/self_improvement/propose_changes",
            json={},
            timeout=10,
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Self-improvement endpoint working!")
            print(f"   Analysis timestamp: {data.get('timestamp', 'N/A')}")
            print(f"   Status: {data.get('status', 'unknown')}")

            # Show current capabilities
            capabilities = data.get("analysis", {}).get("current_capabilities", [])
            if capabilities:
                print(f"\n🧠 Current Capabilities ({len(capabilities)}):")
                for i, cap in enumerate(capabilities[:3], 1):
                    print(f"   {i}. {cap}")
                if len(capabilities) > 3:
                    print(f"   ... and {len(capabilities) - 3} more")

            # Show proposed changes
            changes = data.get("proposed_changes", [])
            if changes:
                print(f"\n🔧 Proposed Changes ({len(changes)}):")
                for i, change in enumerate(changes[:3], 1):
                    print(f"   {i}. {change.get('title', 'Unknown')}")
                    print(f"      Category: {change.get('category', 'N/A')}")
                    print(f"      Priority: {change.get('priority', 'N/A')}")
                if len(changes) > 3:
                    print(f"   ... and {len(changes) - 3} more changes")

            # Show next steps
            next_steps = data.get("next_steps", [])
            if next_steps:
                print(f"\n📋 Next Steps ({len(next_steps)}):")
                for i, step in enumerate(next_steps[:2], 1):
                    print(f"   {i}. {step}")

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
    success = test_self_improvement_fix()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Self-improvement propose changes endpoint is working!")
        print("✅ The 'Propose Changes' button should now work in the UI.")
    else:
        print("❌ Self-improvement endpoint still has issues.")

    print("\nTo test in UI:")
    print("1. Open Lyrixa launcher")
    print("2. Go to 'Self-Improvement' tab")
    print("3. Click 'Propose Changes'")
    print(
        "4. Should see detailed analysis and improvement proposals instead of 404 error"
    )
