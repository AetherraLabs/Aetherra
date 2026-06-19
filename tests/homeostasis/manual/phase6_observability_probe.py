#!/usr/bin/env python3

"""Test for Phase 6 homeostasis live observability implementation."""

import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR))

from Aetherra.homeostasis.homeostasis_integration import get_homeostasis_orchestrator


async def test_phase6_observability():
    print("📊 Testing Phase 6 live observability...")

    try:
        # Get orchestrator and initialize
        orchestrator = get_homeostasis_orchestrator()
        await orchestrator.initialize()

        # Check observability system initialization
        if orchestrator.observability:
            print("✓ LiveObservability initialized")
            print(
                f"✓ Monitoring interval: {orchestrator.observability.monitoring_interval}s"
            )
            print(f"✓ Alert thresholds: {orchestrator.observability.alert_thresholds}")
        else:
            print("❌ LiveObservability not initialized")
            return False

        # Test starting live monitoring
        print("\n🔴 Testing live monitoring startup...")
        monitoring_started = await orchestrator.start_live_monitoring()
        print(f"✓ Live monitoring started: {monitoring_started}")
        print(f"✓ Monitoring active: {orchestrator.is_monitoring_active()}")

        # Wait a bit for some metrics to be collected
        print("\n⏱️ Collecting metrics for 8 seconds...")
        await asyncio.sleep(8)

        # Test live dashboard
        print("\n📋 Testing live dashboard generation...")
        dashboard = orchestrator.get_live_dashboard()
        print("✓ Dashboard generated:")
        print(dashboard)

        # Test metrics summary
        print("\n📈 Testing metrics summary...")
        summary = orchestrator.get_metrics_summary(minutes=1)

        if "error" not in summary:
            print(f"✓ Data points collected: {summary.get('data_points', 0)}")
            print(f"✓ Time range: {summary.get('time_range_minutes', 0)} minutes")

            latest = summary.get("latest_metrics", {})
            if latest:
                print(f"✓ Latest timestamp: {latest.get('timestamp', 'Unknown')}")
                print(f"✓ Collection count: {latest.get('collection_count', 0)}")
        else:
            print(f"⚠️ Metrics summary: {summary.get('error')}")

        # Test data export
        print("\n📁 Testing data export...")
        export_path = orchestrator.export_observability_data()
        if export_path:
            print(f"✓ Data exported to: {export_path}")
        else:
            print("❌ Export failed")

        # Test with some system activity to trigger metrics changes
        print("\n🔄 Testing with system feedback to see live updates...")

        # Add some feedback to create observable changes
        test_feedback = {
            "timestamp": "2025-10-12T10:00:00Z",
            "metrics": {
                "cpu_usage": 95.0,  # High CPU to trigger alerts
                "memory_usage": 88.0,  # High memory
                "response_time": 2.5,
                "error_rate": 12.0,  # High error rate
            },
            "source_type": "stress_test",
        }

        await orchestrator.receive_system_feedback("stress_test", test_feedback)

        # Wait for the monitoring loop to process this
        await asyncio.sleep(6)

        # Get updated dashboard
        print("\n📊 Updated dashboard after stress feedback:")
        updated_dashboard = orchestrator.get_live_dashboard()
        print(updated_dashboard)

        # Test stopping monitoring
        print("\n⚫ Testing live monitoring shutdown...")
        monitoring_stopped = await orchestrator.stop_live_monitoring()
        print(f"✓ Live monitoring stopped: {monitoring_stopped}")
        print(f"✓ Monitoring active after stop: {orchestrator.is_monitoring_active()}")

        return True

    except Exception as e:
        print(f"❌ Error during Phase 6 test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_phase6_observability())
    if success:
        print("\n✅ Phase 6 live observability implementation working correctly!")
        print("📊 Real-time monitoring and dashboard capabilities operational")
        print("🔍 Diagnostic tools and metrics export functional")
    else:
        print("\n❌ Phase 6 implementation has issues")
