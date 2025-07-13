#!/usr/bin/env python3
"""
Test the fast API server startup performance
"""

import time
import subprocess
import sys
import socket

def test_fast_startup():
    print("🚀 Testing Fast API Server Startup Performance")
    print("=" * 50)

    # Initialize variables
    import_time = 0.0
    setup_time = 0.0
    fast_api_server = None

    # Test 1: Import speed
    print("\n1️⃣ Testing import speed...")
    start_time = time.time()
    try:
        import fast_api_server
        app = fast_api_server.app
        import_time = time.time() - start_time
        print(f"✅ Fast API server imported in {import_time:.3f} seconds")
        fast_import = import_time < 1.0
    except Exception as e:
        print(f"❌ Import failed: {e}")
        fast_import = False
        import_time = 999.0  # Indicate failure

    # Test 2: Server startup simulation
    print("\n2️⃣ Testing server startup readiness...")
    try:
        # Test basic app creation
        start_time = time.time()
        if fast_api_server:
            app = fast_api_server.app
            health_endpoint = app.router.routes
            setup_time = time.time() - start_time
            print(f"✅ Server setup completed in {setup_time:.3f} seconds")
            fast_setup = setup_time < 0.5
        else:
            print("❌ Cannot test setup - import failed")
            fast_setup = False
            setup_time = 999.0  # Indicate failure
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        fast_setup = False
        setup_time = 999.0  # Indicate failure

    # Test 3: Port availability check
    print("\n3️⃣ Testing port availability...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8007))
            if result == 0:
                print("⚠️ Port 8007 already in use - server may be running")
                port_available = False
            else:
                print("✅ Port 8007 available for server startup")
                port_available = True
    except Exception as e:
        print(f"⚠️ Port check error: {e}")
        port_available = True  # Assume available

    # Test 4: Health endpoint simulation
    print("\n4️⃣ Testing health endpoint...")
    try:
        if fast_api_server:
            # Simulate health check
            import asyncio
            async def test_health():
                return await fast_api_server.health_check()

            health_result = asyncio.run(test_health())
            if health_result.get("status") == "healthy":
                print("✅ Health endpoint working")
                health_ok = True
            else:
                print("⚠️ Health endpoint returned unexpected result")
                health_ok = False
        else:
            print("❌ Cannot test health - import failed")
            health_ok = False
    except Exception as e:
        print(f"❌ Health test failed: {e}")
        health_ok = False

    # Results
    print("\n" + "=" * 50)
    print("🏁 FAST STARTUP TEST RESULTS:")
    print(f"   • Import Speed: {'✅ FAST' if fast_import else '⚠️ SLOW'} ({import_time:.3f}s)")
    print(f"   • Server Setup: {'✅ FAST' if fast_setup else '⚠️ SLOW'} ({setup_time:.3f}s)")
    print(f"   • Port Availability: {'✅ READY' if port_available else '⚠️ IN_USE'}")
    print(f"   • Health Endpoint: {'✅ WORKING' if health_ok else '❌ FAILED'}")

    overall_success = fast_import and fast_setup and health_ok

    if overall_success:
        print("\n🎉 FAST STARTUP TEST PASSED!")
        print("✅ API server optimized for quick startup")
        print("✅ Should start within timeout window")
        print("\n💡 Ready for launcher integration")

        # Estimate total startup time
        estimated_startup = import_time + setup_time + 2  # +2s for uvicorn startup
        print(f"📊 Estimated total startup time: {estimated_startup:.1f} seconds")

        if estimated_startup < 30:
            print("✅ Well within 60-second timeout window")
        else:
            print("⚠️ May need longer timeout for full startup")

    else:
        print("\n❌ FAST STARTUP TEST FAILED!")
        print("Issues detected - check the errors above")

    return overall_success

if __name__ == "__main__":
    success = test_fast_startup()
    sys.exit(0 if success else 1)
