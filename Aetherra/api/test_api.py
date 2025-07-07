#!/usr/bin/env python3
"""
Aetherra API Test Client
=======================

Simple test client to verify the FastAPI server functionality.
"""

import json
import time
from typing import Any, Dict, Optional

import requests


class AetherraAPIClient:
    """Simple client for testing the Aetherra API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> Dict[str, Any]:
        """Test health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def run_script(
        self, script_name: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test script execution endpoint"""
        data = {"script_name": script_name, "parameters": parameters or {}}
        response = requests.post(f"{self.base_url}/run", json=data)
        response.raise_for_status()
        return response.json()

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Test job status endpoint"""
        response = requests.get(f"{self.base_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()

    def list_jobs(self, status: Optional[str] = None) -> Dict[str, Any]:
        """Test job listing endpoint"""
        params = {"status": status} if status else {}
        response = requests.get(f"{self.base_url}/jobs", params=params)
        response.raise_for_status()
        return response.json()

    def list_scripts(self) -> Dict[str, Any]:
        """Test script listing endpoint"""
        response = requests.get(f"{self.base_url}/scripts")
        response.raise_for_status()
        return response.json()


def run_api_tests():
    """Run comprehensive API tests"""
    print("🧪 Starting Aetherra API Tests")
    print("=" * 50)

    client = AetherraAPIClient()

    try:
        # Test 1: Health Check
        print("📋 Test 1: Health Check")
        health = client.health_check()
        print(f"✅ Health Status: {health['status']}")
        print(f"⏱️ Uptime: {health['uptime']}")
        print(f"🔄 Active Jobs: {health['active_jobs']}")
        print()

        # Test 2: List Available Scripts
        print("📋 Test 2: List Available Scripts")
        scripts = client.list_scripts()
        print(f"✅ Found {scripts['count']} scripts:")
        for script in scripts["scripts"][:5]:  # Show first 5
            print(f"   • {script}")
        print()

        # Test 3: Run a Script
        print("📋 Test 3: Run Script")
        if scripts["scripts"]:
            script_name = scripts["scripts"][0]  # Use first available script
            print(f"🚀 Running script: {script_name}")

            run_result = client.run_script(script_name, {"test": True})
            job_id = run_result["job_id"]
            print(f"✅ Job started: {job_id}")
            print(f"📊 Status: {run_result['status']}")
            print()

            # Test 4: Check Job Status
            print("📋 Test 4: Monitor Job Status")
            for i in range(5):  # Check status for up to 5 seconds
                status = client.get_job_status(job_id)
                print(f"⏱️ Check {i + 1}: {status['status']}")

                if status["status"] in ["completed", "failed"]:
                    if status["output"]:
                        print(f"📋 Output: {json.dumps(status['output'], indent=2)}")
                    if status["error"]:
                        print(f"❌ Error: {status['error']}")
                    break

                time.sleep(1)
            print()
        else:
            print("⚠️ No scripts available to test")
            print()

        # Test 5: List Jobs
        print("📋 Test 5: List Jobs")
        jobs = client.list_jobs()
        print(f"✅ Found {jobs['total']} jobs")
        for job in jobs["jobs"][:3]:  # Show first 3
            print(
                f"   • {job['job_id'][:8]}... - {job['script_name']} - {job['status']}"
            )
        print()

        print("🎉 All API tests completed successfully!")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the API server running?")
        print("💡 Start the server with: python Aetherra/api/run_server.py")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"📋 Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    run_api_tests()
