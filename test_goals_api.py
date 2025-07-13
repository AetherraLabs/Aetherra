"""
Test the Goals API Endpoints
Verify the POST /api/goals/forecast and /api/goals/reasoning_context endpoints
"""

import requests
import json

def test_goals_endpoints():
    """Test both goals endpoints"""
    base_url = "http://127.0.0.1:8007"

    print("🎯 Testing Goals API Endpoints")
    print("=" * 50)

    # Test 1: Goals Forecast
    print("\n1️⃣ Testing POST /api/goals/forecast")
    try:
        forecast_data = {
            "goal": "Enhance Plugin Intelligence System",
            "context": "Current system needs better recommendations"
        }

        response = requests.post(
            f"{base_url}/api/goals/forecast",
            json=forecast_data,
            timeout=10
        )

        print(f"   📊 Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("   ✅ SUCCESS!")
            print(f"   🎯 Goal: {result['forecast']['goal']}")
            print(f"   📈 Prediction: {result['forecast']['prediction']}")
            print(f"   🎲 Confidence: {result['forecast']['confidence']}")
        else:
            print(f"   ❌ FAILED: {response.text}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    # Test 2: Reasoning Context
    print("\n2️⃣ Testing POST /api/goals/reasoning_context")
    try:
        context_data = {
            "goal": "System Optimization",
            "current_metrics": {"performance": 0.8, "stability": 0.9}
        }

        response = requests.post(
            f"{base_url}/api/goals/reasoning_context",
            json=context_data,
            timeout=10
        )

        print(f"   📊 Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("   ✅ SUCCESS!")
            print(f"   🧠 Goal: {result['reasoning_context']['goal']}")
            print(f"   📊 Decision Factors: {len(result['reasoning_context']['decision_factors'])}")
            print(f"   🔗 Reasoning Chain: {len(result['reasoning_context']['reasoning_chain'])} steps")
        else:
            print(f"   ❌ FAILED: {response.text}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    print("\n" + "=" * 50)
    print("🏁 Goals API Test Complete!")

if __name__ == "__main__":
    test_goals_endpoints()
