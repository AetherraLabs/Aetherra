#!/usr/bin/env python3
"""
Simple API test script to validate the implementation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all API components can be imported"""
    try:
        print("🧪 Testing API imports...")

        # Test models
        from Aetherra.api.models import RunRequest, RunResponse, StatusResponse

        print("✅ Models imported successfully")

        # Test job store
        from Aetherra.api.job_store import job_store

        print("✅ Job store imported successfully")

        # Test job controller
        from Aetherra.api.job_controller import job_controller

        print("✅ Job controller imported successfully")

        # Test main server
        from Aetherra.api.aether_server import app

        print("✅ FastAPI server imported successfully")

        print("\n🎉 All components imported successfully!")
        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without starting server"""
    try:
        print("\n🧪 Testing basic functionality...")

        from Aetherra.api.job_controller import job_controller
        from Aetherra.api.models import RunRequest

        # Test creating a run request
        request = RunRequest(
            script_name="test.aether", parameters={"test": "value"}, context=None
        )
        print(f"✅ Created run request: {request.script_name}")

        # Test job controller basic operations
        jobs = job_controller.list_jobs()
        print(f"✅ Retrieved jobs list: {len(jobs)} jobs")

        print("\n🎉 Basic functionality test passed!")
        return True

    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Aetherra API Validation Test")
    print("=" * 50)

    success = test_imports()
    if success:
        success = test_basic_functionality()

    if success:
        print("\n✅ All tests passed! API is ready to use.")
        print("\n📋 Next steps:")
        print("1. Start the server: python Aetherra/api/run_server.py")
        print("2. Test the API: python Aetherra/api/test_api.py")
        print("3. View docs: http://localhost:8000/docs")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
