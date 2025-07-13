#!/usr/bin/env python3
"""
Test script to verify system status panel functionality
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_system_metrics():
    """Test the system metrics functionality"""
    try:
        print("🔍 Testing System Metrics...")

        # Import the intelligence stack
        from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

        # Initialize the intelligence stack
        workspace_path = str(Path(__file__).parent)
        intelligence_stack = LyrixaIntelligenceStack(workspace_path)

        print("✅ Intelligence stack initialized")

        # Test get_real_time_metrics
        metrics = intelligence_stack.get_real_time_metrics()

        print("📊 System Metrics Retrieved:")
        print(f"   Uptime: {metrics.get('uptime', 'Unknown')}")
        print(f"   Active Agents: {metrics.get('active_agents', 0)}")
        print(f"   Performance Score: {metrics.get('performance_score', 0.0):.1%}")
        print(f"   Overall Health: {metrics.get('overall_health', 0):.1f}%")
        print(
            f"   Intelligence Health: {metrics.get('intelligence', {}).get('health', 0):.1f}%"
        )

        # Test get_status method
        status = intelligence_stack.get_status()

        print("\n🧠 Intelligence Status:")
        print(f"   Learning Iterations: {status.get('learning_iterations', 0)}")
        print(f"   Pattern Recognitions: {status.get('pattern_recognitions', 0)}")
        print(
            f"   Intelligence Available: {status.get('intelligence_available', False)}"
        )

        print("\n✅ System metrics test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ System metrics test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting System Status Panel Test...")
    success = test_system_metrics()
    if success:
        print("🎯 All tests passed! System status panel should be working.")
    else:
        print("⚠️ Tests failed. Please check the system configuration.")
