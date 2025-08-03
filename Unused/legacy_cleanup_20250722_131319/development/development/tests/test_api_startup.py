#!/usr/bin/env python3
"""
Test the enhanced API server startup sequence for Lyrixa
"""

import sys
import time
import requests
import subprocess
from pathlib import Path

def test_api_startup():
    print("🚀 Testing Enhanced API Server Startup Sequence")
    print("=" * 50)

    # Test 1: Check if enhanced_api_server can be imported
    print("\n1️⃣ Testing imports...")
    try:
        import enhanced_api_server
        print("✅ enhanced_api_server imports successfully")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

    # Test 2: Check if we can start the server
    print("\n2️⃣ Testing server startup...")
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "run_self_improvement_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("⏳ Waiting for server to start...")
        time.sleep(5)  # Give server time to start

        # Test if server is responding
        try:
            response = requests.get("http://127.0.0.1:8007/api/plugins/enhanced_capabilities", timeout=5)
            if response.status_code == 200:
                print("✅ Server started and responding on port 8007")
                server_working = True
            else:
                print(f"[WARN] Server responding but with status {response.status_code}")
                server_working = False
        except requests.exceptions.ConnectionError:
            print("[ERROR] Server not responding")
            server_working = False

        # Cleanup
        process.terminate()
        process.wait()

        return server_working

    except Exception as e:
        print(f"[ERROR] Server startup failed: {e}")
        return False

def test_launch_utils():
    print("\n3️⃣ Testing launch utils...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "Aetherra"))
        from utils.launch_utils import run_self_improvement_api, wait_for_api_server
        print("✅ Launch utils imported successfully")

        # Test the wait function (without actually starting server)
        print("⏳ Testing wait_for_api_server function...")
        # This should fail quickly since no server is running
        result = wait_for_api_server(port=8007, timeout=3)
        if not result:
            print("✅ wait_for_api_server correctly detected no server")
        else:
            print("[WARN] wait_for_api_server unexpected result")

        return True
    except Exception as e:
        print(f"[ERROR] Launch utils test failed: {e}")
        return False

def main():
    print("[TOOL] ENHANCED API SERVER STARTUP TEST")
    print("Testing the complete startup sequence...")
    print()

    # Run tests
    test1 = test_api_startup()
    test2 = test_launch_utils()

    print("\n" + "=" * 50)
    print("🏁 TEST RESULTS:")
    print(f"   • API Server Startup: {'✅ PASSED' if test1 else '[ERROR] FAILED'}")
    print(f"   • Launch Utils: {'✅ PASSED' if test2 else '[ERROR] FAILED'}")

    if test1 and test2:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced API server startup sequence is ready!")
        print("\n💡 To start Lyrixa with API server:")
        print("   python Aetherra/lyrixa/launcher.py")
    else:
        print("\n[ERROR] Some tests failed - check the errors above")

if __name__ == "__main__":
    main()
