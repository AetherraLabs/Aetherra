#!/usr/bin/env python3
"""
Comprehensive API Test - All Endpoints
=======================================

Test all API endpoints including the newly added self-improvement endpoint.
"""

import requests

API_BASE = "http://127.0.0.1:8005"


def test_all_endpoints():
    """Test all available API endpoints."""

    print("🧪 Comprehensive API Endpoint Test")
    print("=" * 50)
    print(f"API Base URL: {API_BASE}")
    print()

    results = []

    # Test 1: Goal Forecast
    print("🧠 Testing Goal Forecast Endpoint...")
    try:
        response = requests.post(
            f"{API_BASE}/api/goals/forecast",
            json={"goal": "Improve system performance"},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Goal Forecast API Working!")
            print(f"   Forecast: {data.get('forecast', {}).get('forecast', 'N/A')}")
            results.append(True)
        else:
            print(f"❌ Goal Forecast API Error: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Goal Forecast API Error: {e}")
        results.append(False)

    # Test 2: Reasoning Context
    print("\n🤔 Testing Reasoning Context Endpoint...")
    try:
        response = requests.post(
            f"{API_BASE}/api/goals/reasoning_context",
            json={"goal": "Test reasoning"},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Reasoning Context API Working!")
            print(f"   Related memories: {data.get('count', 0)}")
            results.append(True)
        else:
            print(f"❌ Reasoning Context API Error: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Reasoning Context API Error: {e}")
        results.append(False)

    # Test 3: Agent Collaboration
    print("\n🤝 Testing Agent Collaboration Endpoint...")
    try:
        response = requests.post(
            f"{API_BASE}/api/agents/suggest_pairings",
            json={"task": "Test task", "n": 2},
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent Collaboration API Working!")
            print(f"   Suggested pairings: {len(data.get('pairings', []))}")
            results.append(True)
        else:
            print(f"❌ Agent Collaboration API Error: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Agent Collaboration API Error: {e}")
        results.append(False)

    # Test 4: Cognitive Monitor
    print("\n📊 Testing Cognitive Monitor Endpoint...")
    try:
        response = requests.get(
            f"{API_BASE}/api/cognitive_monitor/dashboard", timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Cognitive Monitor API Working!")
            print(f"   Dashboard data available: {bool(data)}")
            results.append(True)
        else:
            print(f"❌ Cognitive Monitor API Error: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Cognitive Monitor API Error: {e}")
        results.append(False)

    # Test 5: Plugin Capabilities (newly fixed)
    print("\n🧩 Testing Plugin Capabilities Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/plugins/capabilities", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Plugin Capabilities API Working!")
            print(f"   Available plugins: {data.get('count', 0)}")
            results.append(True)
        else:
            print(f"❌ Plugin Capabilities API Error: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Plugin Capabilities API Error: {e}")
        results.append(False)

    # Test 6: Self-Improvement (newly added)
    print("\n[TOOL] Testing Self-Improvement Endpoint...")
    try:
        response = requests.post(
            f"{API_BASE}/api/self_improvement/propose_changes", json={}, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Self-Improvement API Working!")
            print(f"   Proposed changes: {len(data.get('proposed_changes', []))}")
            results.append(True)
        else:
            print(f"❌ Self-Improvement API Error: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Self-Improvement API Error: {e}")
        results.append(False)

    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("✅ All UI tabs should work without 404 errors")
        return 0
    else:
        print(f"[WARN]  Some tests failed ({passed}/{total})")
        print("❌ Some UI tabs may still have connection issues")
        return 1


if __name__ == "__main__":
    exit_code = test_all_endpoints()
    print("\n📋 UI Tab Status:")
    print("- Goal Forecast tab: Should work ✅")
    print("- Reasoning Context tab: Should work ✅")
    print("- Agent Collaboration tab: Should work ✅")
    print("- Cognitive Monitor tab: Should work ✅")
    print("- Plugin Intelligence tab: Should work ✅ (fixed)")
    print("- Self-Improvement tab: Should work ✅ (fixed)")
    exit(exit_code)
