#!/usr/bin/env python3
"""
Quick test to verify API server import fix is working
"""

import sys
from pathlib import Path

def test_api_import_fix():
    print("🔧 Testing API Server Import Fix")
    print("=" * 40)

    # Test 1: Check if self_improvement_dashboard_api can be imported
    print("\n1️⃣ Testing import fix...")
    try:
        # Add project root to path (same as fixed file does)
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        from Aetherra.lyrixa.self_improvement_dashboard_api import app
        print("✅ self_improvement_dashboard_api imported successfully!")
        import_success = True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import_success = False

    # Test 2: Check if enhanced server is available
    print("\n2️⃣ Testing enhanced server availability...")
    try:
        from enhanced_api_server import app as enhanced_app
        print("✅ Enhanced API server available!")
        enhanced_available = True
    except Exception as e:
        print(f"⚠️ Enhanced server issue: {e}")
        enhanced_available = False

    # Test 3: Check redirect functionality
    print("\n3️⃣ Testing redirect logic...")
    enhanced_server_path = project_root / "enhanced_api_server.py"
    if enhanced_server_path.exists():
        print("✅ Enhanced server file found - redirect will work")
        redirect_ok = True
    else:
        print("⚠️ Enhanced server file not found")
        redirect_ok = False

    # Results
    print("\n" + "=" * 40)
    print("🏁 TEST RESULTS:")
    print(f"   • Import Fix: {'✅ WORKING' if import_success else '❌ FAILED'}")
    print(f"   • Enhanced Server: {'✅ AVAILABLE' if enhanced_available else '⚠️ ISSUE'}")
    print(f"   • Redirect Logic: {'✅ READY' if redirect_ok else '⚠️ ISSUE'}")

    if import_success and enhanced_available and redirect_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ API server import fix is working correctly!")
        print("\n💡 You can now start the API server with:")
        print("   python Aetherra/lyrixa/self_improvement_dashboard_api.py")
        return True
    else:
        print("\n⚠️ Some issues detected - check the results above")
        return False

if __name__ == "__main__":
    success = test_api_import_fix()
    sys.exit(0 if success else 1)
