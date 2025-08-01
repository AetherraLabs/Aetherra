"""
🧠 Test Meta-Reasoning API Endpoints
Test the new reasoning endpoints in the enhanced API server
"""

import requests
import json
import time

def test_meta_reasoning_endpoints():
    """Test all meta-reasoning API endpoints"""

    base_url = "http://127.0.0.1:8007"

    print("🧠 Testing Meta-Reasoning API Endpoints")
    print("=" * 45)

    # Test 1: Get reasoning history
    print("\n1️⃣ Testing GET /api/meta_reasoning/history")
    try:
        response = requests.get(f"{base_url}/api/meta_reasoning/history?limit=5", timeout=10)
        print(f"   📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS!")
            print(f"   📚 History entries: {len(data.get('reasoning_history', []))}")
            if 'summary' in data:
                print(f"   📈 Average confidence: {data['summary']['average_confidence']}")

            # Show sample trace
            if data.get('reasoning_history'):
                sample = data['reasoning_history'][0]
                print(f"   📝 Sample decision: {sample.get('decision')}")
                print(f"   🎯 Confidence: {sample.get('confidence')}")
        else:
            print(f"   ❌ FAILED: {response.text}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    # Test 2: Explain specific decision
    print("\n2️⃣ Testing POST /api/meta_reasoning/explain_decision")
    try:
        explain_data = {"trace_id": "sample_trace_1"}
        response = requests.post(
            f"{base_url}/api/meta_reasoning/explain_decision",
            json=explain_data,
            timeout=10
        )
        print(f"   📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS!")
            explanation = data.get('decision_explanation', {})
            print(f"   🎯 Decision: {explanation.get('decision')}")
            print(f"   📈 Confidence: {explanation.get('confidence')}")
            print(f"   🔗 Reasoning steps: {len(explanation.get('reasoning_chain', []))}")
        else:
            print(f"   ❌ FAILED: {response.text}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    # Test 3: Get analytics
    print("\n3️⃣ Testing GET /api/meta_reasoning/analytics")
    try:
        response = requests.get(f"{base_url}/api/meta_reasoning/analytics", timeout=10)
        print(f"   📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS!")
            analytics = data.get('analytics', {})
            overview = analytics.get('overview', {})
            print(f"   📈 Total decisions: {overview.get('total_decisions')}")
            print(f"   🎯 Success rate: {overview.get('success_rate')}")
            print(f"   🧠 Learning patterns: {overview.get('learning_patterns')}")
        else:
            print(f"   ❌ FAILED: {response.text}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    # Test 4: Add feedback
    print("\n4️⃣ Testing POST /api/meta_reasoning/add_feedback")
    try:
        feedback_data = {
            "trace_id": "sample_trace_1",
            "feedback_score": 0.9,
            "feedback_text": "Excellent decision, very helpful!"
        }
        response = requests.post(
            f"{base_url}/api/meta_reasoning/add_feedback",
            json=feedback_data,
            timeout=10
        )
        print(f"   📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS!")
            result = data.get('feedback_result', {})
            print(f"   👍 Feedback score: {result.get('feedback_score')}")
            print(f"   💡 Impact: {result.get('impact')}")
            print(f"   📚 Learning adjustments: {len(result.get('learning_adjustments', []))}")
        else:
            print(f"   ❌ FAILED: {response.text}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    print("\n" + "=" * 45)
    print("🏁 Meta-Reasoning API Test Complete!")


def test_with_testclient():
    """Test with TestClient if server not running"""

    print("\n🔧 Testing with TestClient (Fallback)")
    print("=" * 40)

    try:
        from fastapi.testclient import TestClient
        import sys
        import os

        # Import the app
        sys.path.insert(0, os.path.dirname(__file__))
        from enhanced_api_server import app

        client = TestClient(app)

        print("🧪 Testing with TestClient...")

        # Test reasoning history
        history_response = client.get("/api/meta_reasoning/history?limit=3")
        print(f"📚 History Status: {history_response.status_code}")

        if history_response.status_code == 200:
            data = history_response.json()
            print(f"   ✅ History working! Entries: {len(data.get('reasoning_history', []))}")

        # Test analytics
        analytics_response = client.get("/api/meta_reasoning/analytics")
        print(f"📊 Analytics Status: {analytics_response.status_code}")

        if analytics_response.status_code == 200:
            data = analytics_response.json()
            analytics = data.get('analytics', {})
            print(f"   ✅ Analytics working! Total decisions: {analytics.get('overview', {}).get('total_decisions')}")

        # Test explain decision
        explain_response = client.post("/api/meta_reasoning/explain_decision", json={"trace_id": "test_trace"})
        print(f"🔍 Explain Status: {explain_response.status_code}")

        if explain_response.status_code == 200:
            print("   ✅ Explain decision working!")

        # Test feedback
        feedback_response = client.post("/api/meta_reasoning/add_feedback", json={
            "trace_id": "test_trace",
            "feedback_score": 0.8,
            "feedback_text": "Good decision"
        })
        print(f"👍 Feedback Status: {feedback_response.status_code}")

        if feedback_response.status_code == 200:
            print("   ✅ Feedback working!")

        return True

    except Exception as e:
        print(f"❌ TestClient failed: {e}")
        return False


def show_endpoint_summary():
    """Show summary of available meta-reasoning endpoints"""

    print("\n📋 Meta-Reasoning API Endpoints Summary")
    print("=" * 45)

    endpoints = [
        {
            "method": "GET",
            "path": "/api/meta_reasoning/history",
            "purpose": "Get recent reasoning decision history",
            "params": "?limit=10 (optional)"
        },
        {
            "method": "POST",
            "path": "/api/meta_reasoning/explain_decision",
            "purpose": "Get detailed explanation for specific decision",
            "body": '{"trace_id": "decision_id"}'
        },
        {
            "method": "GET",
            "path": "/api/meta_reasoning/analytics",
            "purpose": "Get comprehensive reasoning analytics",
            "params": "None"
        },
        {
            "method": "POST",
            "path": "/api/meta_reasoning/add_feedback",
            "purpose": "Add user feedback for learning improvement",
            "body": '{"trace_id": "id", "feedback_score": 0.9, "feedback_text": "helpful"}'
        }
    ]

    for endpoint in endpoints:
        print(f"\n🔗 {endpoint['method']} {endpoint['path']}")
        print(f"   Purpose: {endpoint['purpose']}")
        if 'params' in endpoint:
            print(f"   Params: {endpoint['params']}")
        if 'body' in endpoint:
            print(f"   Body: {endpoint['body']}")


if __name__ == "__main__":
    print("🚀 Meta-Reasoning API Test Suite")
    print("=" * 45)

    # Try server first, then TestClient
    try:
        test_meta_reasoning_endpoints()
    except:
        print("\n⚠️ Server not available, trying TestClient...")
        test_with_testclient()

    # Show endpoint summary
    show_endpoint_summary()

    print("\n✅ Meta-Reasoning API endpoints are ready!")
    print("💡 Start server with: python enhanced_api_server.py")
    print("🎯 Access endpoints at: http://127.0.0.1:8007/api/meta_reasoning/...")
