#!/usr/bin/env python3
"""
Get detailed response from propose_changes endpoint
"""

import sys
import os
import json
from fastapi.testclient import TestClient

# Add the project path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from enhanced_api_server import app

    print("🧪 Testing propose_changes with detailed output...")

    # Create test client
    client = TestClient(app)

    # Test the propose_changes endpoint
    response = client.post("/api/self_improvement/propose_changes", json={})

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ Response received:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: {response.text}")

except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()
