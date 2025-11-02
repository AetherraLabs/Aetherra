#!/usr/bin/env python
"""
Test script for agent task submission API.
"""

import json
import os
import sys
import time

import requests

# Enable agents API
os.environ["AETHERRA_AGENTS_API_ENABLED"] = "1"

BASE_URL = "http://localhost:3001"


def test_submit_task():
    """Test submitting a task to the agent orchestrator."""
    print("Testing agent task submission API...")
    print("=" * 60)

    # Test 1: Submit a planning task
    print("\n1. Submitting a planning task...")
    task_data = {
        "name": "Test Planning",
        "description": "Create a simple plan for OS health check",
        "required_capabilities": ["plan"],
        "input_data": {"goal": "health check"},
        "priority": "normal",
    }

    try:
        response = requests.post(f"{BASE_URL}/api/tasks", json=task_data, timeout=5)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            result = response.json()
            if result.get("ok") and "task_id" in result:
                task_id = result["task_id"]
                print(f"   ✓ Task submitted successfully: {task_id}")

                # Test 2: Get task status
                print("\n2. Checking task status...")
                time.sleep(0.5)  # Brief pause

                status_response = requests.get(
                    f"{BASE_URL}/api/tasks/{task_id}", timeout=5
                )
                print(f"   Status Code: {status_response.status_code}")
                print(f"   Response: {json.dumps(status_response.json(), indent=2)}")

                if status_response.status_code == 200:
                    print("   ✓ Task status retrieved successfully")
                else:
                    print("   ✗ Failed to get task status")
            else:
                print(f"   ✗ Task submission failed: {result}")
        else:
            print(f"   ✗ Request failed: {response.text}")

    except requests.exceptions.ConnectionError:
        print("   ✗ Could not connect to Hub. Is the OS running?")
        print("   → Run: python aetherra_os_launcher.py --mode full -v")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

    print("\n" + "=" * 60)
    return True


if __name__ == "__main__":
    success = test_submit_task()
    sys.exit(0 if success else 1)
