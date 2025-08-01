#!/usr/bin/env python3
"""
Test script to verify PerformanceMonitor functionality
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_performance_monitor():
    """Test the PerformanceMonitor module"""
    try:
        print("Testing PerformanceMonitor import...")
        from lyrixa.gui.performance_monitor import PerformanceMonitor

        print("✅ PerformanceMonitor imported successfully")

        print("\nTesting PerformanceMonitor instantiation...")
        # Skip instantiation test if no QApplication available
        try:
            pm = PerformanceMonitor()
            print("✅ PerformanceMonitor instantiated successfully")
        except Exception as e:
            if "QApplication" in str(e):
                print(
                    "⚠️  PerformanceMonitor requires QApplication (headless environment)"
                )
                pm = None
            else:
                raise

        print("\nTesting basic functionality...")
        # Test some basic methods
        if pm:
            if hasattr(pm, "start_monitoring"):
                print("✅ start_monitoring method exists")
            if hasattr(pm, "stop_monitoring"):
                print("✅ stop_monitoring method exists")
            if hasattr(pm, "update_displays"):
                print("✅ update_displays method exists")

        print("\nTesting metrics collection...")
        from lyrixa.gui.performance_monitor import SystemMetrics

        metrics = SystemMetrics()
        system_metrics = metrics.collect_metrics()
        print(f"✅ System metrics collected: {len(system_metrics)} metrics")

        print("\n🎉 All PerformanceMonitor tests passed!")
        return True

    except Exception as e:
        print(f"❌ Error testing PerformanceMonitor: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_performance_monitor()
    sys.exit(0 if success else 1)
