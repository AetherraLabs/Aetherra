#!/usr/bin/env python3
"""
Simple test to verify the enhanced API server can start
"""

import time
import requests
import threading
import uvicorn
from enhanced_api_server import app

def start_server():
    """Start server in a thread"""
    uvicorn.run(app, host="127.0.0.1", port=8008, log_level="error")

def test_server():
    """Test if server responds"""
    print("🚀 Testing Enhanced API Server...")

    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("⏳ Waiting for server...")
    time.sleep(3)

    # Test endpoint
    try:
        response = requests.get("http://127.0.0.1:8008/api/plugins/enhanced_capabilities", timeout=5)
        if response.status_code == 200:
            print("✅ Server is working!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {len(response.json())} items")
            return True
        else:
            print(f"[WARN] Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Server test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 Enhanced API Server test PASSED!")
        print("✅ Ready to integrate with Lyrixa launcher")
    else:
        print("\n[ERROR] Enhanced API Server test FAILED!")

    time.sleep(1)  # Give server time to cleanup
