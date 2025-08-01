#!/usr/bin/env python3
"""
Test UI to API Connection
=========================

Simple test script to verify the UI can successfully connect to the working API endpoints.
"""

import json
import sys

import requests

# Updated API base URL
API_BASE = "http://127.0.0.1:8005"


def test_goal_forecast():
    """Test the goal forecast endpoint"""
    print("🧠 Testing Goal Forecast Endpoint...")

    try:
        endpoint = f"{API_BASE}/api/goals/forecast"
        payload = {"goal": "Improve Lyrixa intelligence"}

        response = requests.post(endpoint, json=payload, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("✅ Goal Forecast API Working!")
            print(f"   Forecast: {data.get('forecast', {}).get('forecast', 'N/A')}")
            print(f"   Risk: {data.get('forecast', {}).get('risk', 'N/A')}")
            print(f"   Confidence: {data.get('forecast', {}).get('confidence', 'N/A')}")
            return True
        else:
            print(f"❌ Goal Forecast API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Goal Forecast API Connection Error: {e}")
        return False


def test_reasoning_context():
    """Test the reasoning context endpoint"""
    print("\n🤔 Testing Reasoning Context Endpoint...")

    try:
        endpoint = f"{API_BASE}/api/goals/reasoning_context"
        payload = {"goal": "Test reasoning capabilities"}

        response = requests.post(endpoint, json=payload, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("✅ Reasoning Context API Working!")
            print(f"   Context: {data.get('context', {}).get('reasoning', 'N/A')}")
            return True
        else:
            print(f"❌ Reasoning Context API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Reasoning Context API Connection Error: {e}")
        return False


def test_agent_collaboration():
    """Test the agent collaboration endpoint"""
    print("\n🤝 Testing Agent Collaboration Endpoint...")

    try:
        endpoint = f"{API_BASE}/api/agents/suggest_pairings"
        payload = {"task": "Test task", "n": 2}

        response = requests.post(endpoint, json=payload, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("✅ Agent Collaboration API Working!")
            print(f"   Pairings: {len(data.get('pairings', []))}")
            return True
        else:
            print(f"❌ Agent Collaboration API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Agent Collaboration API Connection Error: {e}")
        return False


def test_cognitive_monitor():
    """Test the cognitive monitor endpoint"""
    print("\n📊 Testing Cognitive Monitor Endpoint...")

    try:
        endpoint = f"{API_BASE}/api/cognitive_monitor/dashboard"

        response = requests.get(endpoint, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("✅ Cognitive Monitor API Working!")
            print(f"   Summary: {data.get('summary', 'N/A')}")
            return True
        else:
            print(f"❌ Cognitive Monitor API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Cognitive Monitor API Connection Error: {e}")
        return False


def main():
    """Run all API connection tests"""
    print("🧪 Testing UI to API Connection")
    print("=" * 50)
    print(f"API Base URL: {API_BASE}")
    print()

    results = []
    results.append(test_goal_forecast())
    results.append(test_reasoning_context())
    results.append(test_agent_collaboration())
    results.append(test_cognitive_monitor())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("✅ UI is properly configured to connect to working API endpoints")
        return 0
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("❌ UI may have connection issues with some API endpoints")
        return 1


if __name__ == "__main__":
    sys.exit(main())
