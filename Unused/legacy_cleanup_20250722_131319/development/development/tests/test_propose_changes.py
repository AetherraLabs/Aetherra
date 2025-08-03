#!/usr/bin/env python3
"""
Test the propose_changes endpoint directly
"""

import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add the project path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from enhanced_api_server import app

    print("🧪 Testing propose_changes endpoint...")

    # Create test client
    client = TestClient(app)

    # Test the propose_changes endpoint
    response = client.post("/api/self_improvement/propose_changes", json={})

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ propose_changes endpoint working!")
        print(f"📊 Proposals: {len(data.get('proposals', []))}")

        for i, proposal in enumerate(data.get("proposals", [])[:3], 1):
            print(f"   {i}. {proposal.get('action', 'Unknown action')}")
            print(f"      Category: {proposal.get('category', 'Unknown')}")
            print(f"      Priority: {proposal.get('priority', 'Unknown')}")
    else:
        print(f"[ERROR] Error: {response.text}")

    # Test enhanced capabilities too
    print("\n🧩 Testing enhanced capabilities...")
    response = client.get("/api/plugins/enhanced_capabilities")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Enhanced capabilities working! Found {data.get('summary', {}).get('total_plugins', 0)} plugins")
    else:
        print(f"[ERROR] Enhanced capabilities error: {response.text}")

    print("\n🎉 API server is ready for use!")
    print("Start with: python enhanced_api_server.py")
    print("UI will connect to: http://127.0.0.1:8007")

except ImportError as e:
    print(f"[ERROR] Import error: {e}")
except Exception as e:
    print(f"[ERROR] Test error: {e}")
    import traceback
    traceback.print_exc()
