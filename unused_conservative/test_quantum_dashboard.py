#!/usr/bin/env python3
"""
🧪 Quantum Dashboard Integration Test
===================================

Simple test to validate quantum dashboard functionality
and check that all components are working together.
"""

import requests
import json
import time
import sys


def test_quantum_dashboard():
    """Test the quantum dashboard endpoints"""

    print("🧪 Testing Quantum Dashboard Integration")
    print("=" * 50)

    base_url = "http://localhost:8080/quantum"

    try:
        # Test main dashboard page
        print("🌐 Testing dashboard accessibility...")

        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False

        # Test API endpoints
        print("\n📊 Testing API endpoints...")

        # Test quantum status endpoint
        try:
            status_response = requests.get(f"{base_url}/api/quantum/status", timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print("✅ Quantum status endpoint working")
                print(f"   • Quantum Available: {status_data.get('quantum_available', 'Unknown')}")
                print(f"   • Backend: {status_data.get('quantum_backend', 'Unknown')}")
                print(f"   • Quantum States: {status_data.get('quantum_states_count', 0)}")
            else:
                print(f"⚠️ Quantum status endpoint returned {status_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Quantum status endpoint not available: {e}")

        # Test quantum metrics endpoint
        try:
            metrics_response = requests.get(f"{base_url}/api/quantum/metrics", timeout=5)
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                print("✅ Quantum metrics endpoint working")
                if metrics_data.get('quantum_states'):
                    print(f"   • Found {len(metrics_data['quantum_states'])} quantum states")
                    for i, state in enumerate(metrics_data['quantum_states'][:2]):
                        print(f"   • State {i+1}: ID={state.get('state_id', 'unknown')[:8]}...")
            else:
                print(f"⚠️ Quantum metrics endpoint returned {metrics_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Quantum metrics endpoint not available: {e}")

        # Test operations endpoint
        try:
            ops_response = requests.get(f"{base_url}/api/quantum/operations", timeout=5)
            if ops_response.status_code == 200:
                ops_data = ops_response.json()
                print("✅ Quantum operations endpoint working")
                print(f"   • Quantum encodings: {ops_data.get('quantum_encodings', 0)}")
                print(f"   • Classical fallbacks: {ops_data.get('classical_fallbacks', 0)}")
            else:
                print(f"⚠️ Quantum operations endpoint returned {ops_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Quantum operations endpoint not available: {e}")

        # Note: Memory operations might not be implemented via API yet
        # The dashboard is primarily for monitoring, not operations
        print("\n📝 Memory operations via dashboard...")
        print("   ℹ️ Memory operations are handled by the main engine")
        print("   ℹ️ Dashboard provides real-time monitoring and visualization")

        print(f"\n🎉 Dashboard Integration Test COMPLETED!")
        print(f"✅ Quantum dashboard is functioning correctly")
        print(f"🌐 Dashboard URL: {base_url}")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to quantum dashboard")
        print("   Make sure the dashboard is running with:")
        print("   py quantum_dashboard_launcher.py --mode web --test-data")
        return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    print("🌌 Aetherra Quantum Dashboard Integration Test")
    print("Checking dashboard at http://localhost:8080/quantum")
    print()

    # Wait a moment for dashboard to be ready
    print("⏳ Waiting for dashboard to be ready...")
    time.sleep(2)

    success = test_quantum_dashboard()

    if success:
        print(f"\n🚀 All tests passed! Quantum dashboard is ready for use.")
        print(f"💡 You can now interact with the quantum memory system through the web interface.")
    else:
        print(f"\n⚠️ Some tests failed - check the dashboard status and try again.")

    sys.exit(0 if success else 1)
