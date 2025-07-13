#!/usr/bin/env python3
"""
Test script to verify PerformanceMonitor functionality
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_performance_monitor_imports():
    """Test the PerformanceMonitor module imports"""
    try:
        print("Testing PerformanceMonitor imports...")
        from lyrixa.gui.performance_monitor import (
            HealthIndicator,
            MetricsChart,
            MetricsCollectorThread,
            MetricsTable,
            PerformanceMonitor,
            SystemMetrics,
        )

        print("✅ All PerformanceMonitor classes imported successfully")

        print("\nTesting SystemMetrics (no GUI required)...")
        metrics = SystemMetrics()
        system_metrics = metrics.collect_metrics()
        print(f"✅ System metrics collected: {len(system_metrics)} metrics")

        # Show some sample metrics
        for key, value in list(system_metrics.items())[:5]:  # Show first 5 metrics
            print(f"  • {key}: {value}")

        print("\n🎉 All PerformanceMonitor import tests passed!")
        return True

    except Exception as e:
        print(f"❌ Error testing PerformanceMonitor: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_performance_monitor_imports()
    sys.exit(0 if success else 1)
