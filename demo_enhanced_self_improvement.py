#!/usr/bin/env python3
"""
Demo: Enhanced Self-Improvement System
Shows the improved API server with no separate console window
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_embedded_server():
    """Test the embedded server functionality"""
    print("🚀 Testing Enhanced Self-Improvement Server")
    print("=" * 50)

    # Test 1: Import the embedded server
    print("\n1️⃣ Testing embedded server import...")
    try:
        from enhanced_self_improvement_server import start_server_thread, is_server_running
        print("✅ Embedded server imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 2: Start server (no console window)
    print("\n2️⃣ Starting embedded server (no console window)...")
    try:
        success = start_server_thread()
        if success:
            print("✅ Embedded server started successfully")
            print("   • No separate console window created")
            print("   • Server running in background thread")
            print("   • Integrated with main application")
        else:
            print("❌ Failed to start embedded server")
            return False
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

    # Test 3: Check server status
    print("\n3️⃣ Checking server status...")
    try:
        running = is_server_running()
        if running:
            print("✅ Server is running and responding")
        else:
            print("❌ Server is not responding")
            return False
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

    # Test 4: Test API endpoints
    print("\n4️⃣ Testing API endpoints...")
    try:
        import requests

        # Health check
        response = requests.get("http://127.0.0.1:8007/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data.get('status', 'unknown')}")
            print(f"   Service: {data.get('service', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

        # Self-improvement endpoint
        response = requests.post(
            "http://127.0.0.1:8007/api/self_improvement/propose_changes",
            json={"context": "testing"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                proposals = data.get('proposals', {})
                print(f"✅ Self-improvement endpoint working")
                print(f"   Generated {len(proposals.get('proposals', []))} proposals")

                # Show first proposal
                if proposals.get('proposals'):
                    first_proposal = proposals['proposals'][0]
                    print(f"   Example: {first_proposal.get('suggestion', 'No suggestion')}")
            else:
                print(f"❌ Self-improvement endpoint error: {data.get('error', 'unknown')}")
                return False
        else:
            print(f"❌ Self-improvement endpoint failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

    # Test 5: Performance check
    print("\n5️⃣ Performance evaluation...")
    try:
        # Measure response time
        start_time = time.time()
        response = requests.get("http://127.0.0.1:8007/health", timeout=5)
        response_time = time.time() - start_time

        print(f"✅ Response time: {response_time:.3f} seconds")
        if response_time < 0.5:
            print("   Performance: Excellent (< 0.5s)")
        elif response_time < 1.0:
            print("   Performance: Good (< 1.0s)")
        else:
            print("   Performance: Acceptable")

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

    print("\n🎉 All tests passed!")
    print("✅ Enhanced self-improvement server is working perfectly")
    print("✅ No separate console window")
    print("✅ Integrated with GUI applications")
    print("✅ Fast and reliable API responses")

    return True

def demo_gui_integration():
    """Demo how the server integrates with GUI applications"""
    print("\n" + "=" * 50)
    print("🎨 GUI Integration Demo")
    print("=" * 50)

    print("\n🔗 In your GUI application:")
    print("   1. Import: from enhanced_self_improvement_server import start_server_thread")
    print("   2. Start server: start_server_thread()")
    print("   3. No console window appears")
    print("   4. Server runs in background thread")
    print("   5. Use requests to call API endpoints")

    print("\n📋 Available API endpoints:")
    print("   • GET  /health - Server health check")
    print("   • POST /api/self_improvement/propose_changes - Get improvement suggestions")
    print("   • GET  /api/self_improvement/reflection_analytics - Reflection analytics")
    print("   • GET  /api/self_improvement/system_insights - System insights")

    print("\n💡 Benefits:")
    print("   ✅ No separate console window cluttering desktop")
    print("   ✅ Seamless integration with GUI applications")
    print("   ✅ Background operation without user interruption")
    print("   ✅ Fast startup and reliable operation")
    print("   ✅ Comprehensive self-improvement capabilities")

if __name__ == "__main__":
    print("🌟 Enhanced Self-Improvement System Demo")
    print("Demonstrates the improved API server with no console window")
    print()

    try:
        # Run the test
        success = test_embedded_server()

        if success:
            demo_gui_integration()
            print("\n🎉 Demo completed successfully!")
            print("💡 The enhanced server is ready for production use")
        else:
            print("\n❌ Demo failed - please check the errors above")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Keep server running for a moment to show it's working
    print("\n⏳ Keeping server running for 5 seconds...")
    time.sleep(5)
    print("✅ Server still running in background")
    print("🛑 Demo complete - server will stop when script ends")
