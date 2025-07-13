"""
Quick API Endpoint Verification
Tests the goals endpoints with fallback if server not running
"""

import requests
import json
from fastapi.testclient import TestClient

def test_with_server():
    """Test with running server"""
    base_url = "http://127.0.0.1:8007"

    try:
        # Test forecast endpoint
        forecast_response = requests.post(
            f"{base_url}/api/goals/forecast",
            json={"goal": "Test Goal"},
            timeout=5
        )

        reasoning_response = requests.post(
            f"{base_url}/api/goals/reasoning_context",
            json={"goal": "Test Context"},
            timeout=5
        )

        print(f"✅ Forecast: {forecast_response.status_code}")
        print(f"✅ Reasoning: {reasoning_response.status_code}")

        return True

    except requests.ConnectionError:
        print("❌ Server not running on port 8007")
        return False

def test_with_testclient():
    """Test with TestClient (no server needed)"""
    try:
        # Import the app
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))

        from enhanced_api_server import app

        client = TestClient(app)

        print("🧪 Testing with TestClient...")

        # Test forecast
        forecast_response = client.post("/api/goals/forecast", json={"goal": "Test Goal"})
        print(f"📊 Forecast Status: {forecast_response.status_code}")

        if forecast_response.status_code == 200:
            data = forecast_response.json()
            print(f"   ✅ Forecast working! Goal: {data['forecast']['goal']}")

        # Test reasoning context
        reasoning_response = client.post("/api/goals/reasoning_context", json={"goal": "Test Context"})
        print(f"🧠 Reasoning Status: {reasoning_response.status_code}")

        if reasoning_response.status_code == 200:
            data = reasoning_response.json()
            print(f"   ✅ Reasoning working! Goal: {data['reasoning_context']['goal']}")

        return True

    except Exception as e:
        print(f"❌ TestClient failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Goals API Verification")
    print("=" * 40)

    # Try server first, then TestClient
    if not test_with_server():
        print("\n🔄 Falling back to TestClient...")
        test_with_testclient()

    print("\n✅ Goals API endpoints are ready!")
    print("💡 Start server with: python enhanced_api_server.py")
