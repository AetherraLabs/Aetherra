"""
Quick Test for Propose Changes Fix
Run this to verify the fix is working
"""

import requests
import json

def test_propose_changes():
    """Test the propose changes endpoint"""
    try:
        # Test the endpoint
        url = "http://127.0.0.1:8007/api/self_improvement/propose_changes"
        print(f"🔍 Testing: {url}")

        response = requests.post(url, timeout=10)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Response received:")
            print(json.dumps(data, indent=2))

            # Check for proposals
            if 'proposals' in data or 'proposed_changes' in data:
                print("🎯 Propose Changes endpoint is working correctly!")
                return True
            else:
                print("⚠️ Unexpected response format")
                return False

        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.ConnectionError:
        print("❌ Connection Error: Server not running on port 8007")
        print("💡 Solution: Run 'python enhanced_api_server.py' first")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Propose Changes Fix...")
    print("=" * 50)

    success = test_propose_changes()

    print("\n" + "=" * 50)
    if success:
        print("🎉 FIX CONFIRMED: Propose Changes is working!")
        print("💡 You can now click 'Propose Changes' in the UI")
    else:
        print("🔧 ACTION NEEDED: Start the enhanced API server")
        print("   Command: python enhanced_api_server.py")
