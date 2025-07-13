#!/usr/bin/env python3
"""
Test the complete Lyrixa launcher API startup sequence
"""

import sys
import time
from pathlib import Path

# Add Aetherra to path
sys.path.insert(0, str(Path(__file__).parent / "Aetherra"))

def test_launcher_startup():
    print("🚀 Testing Lyrixa Launcher API Startup")
    print("=" * 45)

    try:
        # Test imports
        print("\n1️⃣ Testing imports...")
        from utils.launch_utils import run_self_improvement_api, wait_for_api_server, check_port_available
        print("✅ Launch utils imported successfully")

        # Test port checking
        print("\n2️⃣ Testing port availability check...")
        port_in_use = check_port_available(8007)
        print(f"   Port 8007 status: {'In use' if port_in_use else 'Available'}")

        # Test API startup
        print("\n3️⃣ Testing API server startup...")
        api_started = run_self_improvement_api()

        if api_started:
            print("✅ API server startup sequence completed successfully!")
            print("\n🔧 Testing port status after startup...")
            time.sleep(2)  # Give server time to fully start
            port_status = check_port_available(8007)
            print(f"   Port 8007 now: {'Active' if port_status else 'Not responding'}")

            return True
        else:
            print("❌ API server startup failed")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 LYRIXA LAUNCHER API STARTUP TEST")
    print("Testing the enhanced startup sequence...")
    print()

    success = test_launcher_startup()

    print("\n" + "=" * 45)
    if success:
        print("🎉 LAUNCHER API STARTUP TEST PASSED!")
        print("✅ Enhanced API server integration working")
        print("\n💡 Lyrixa launcher will now:")
        print("   • Start Enhanced API server on port 8007")
        print("   • Wait for server to be ready")
        print("   • Then start the GUI")
        print("\n🚀 Ready to launch Lyrixa!")
    else:
        print("❌ LAUNCHER API STARTUP TEST FAILED!")
        print("Check the errors above and fix before launching Lyrixa")

if __name__ == "__main__":
    main()
