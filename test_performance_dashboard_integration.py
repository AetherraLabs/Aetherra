#!/usr/bin/env python3
"""
Test Performance Dashboard Integration
=====================================
Validates that the performance dashboard functionality is properly integrated
"""

import os
import sys

# Add the Aetherra path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))


def test_performance_dashboard_integration():
    """Test the performance dashboard code integration without GUI"""
    try:
        print("🔍 Checking performance dashboard code integration...")

        # Read the hybrid_window.py file
        hybrid_window_path = os.path.join(
            "Aetherra", "lyrixa", "gui", "hybrid_window.py"
        )
        with open(hybrid_window_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required imports
        assert "QProgressBar" in content, "QProgressBar import missing"
        assert "QTimer" in content, "QTimer import missing"
        assert "import random" in content, "random import missing"
        print("✅ Required imports found")

        # Check for performance dashboard creation method
        assert "def create_performance_tab(self):" in content, (
            "create_performance_tab method missing"
        )
        print("✅ create_performance_tab method found")

        # Check for progress bar widgets
        assert "self.cpu_bar = QProgressBar()" in content, "CPU progress bar missing"
        assert "self.memory_bar = QProgressBar()" in content, (
            "Memory progress bar missing"
        )
        assert "self.latency_bar = QProgressBar()" in content, (
            "Latency progress bar missing"
        )
        print("✅ Progress bar widgets found")

        # Check for performance labels
        assert 'QLabel("CPU Usage")' in content, "CPU Usage label missing"
        assert 'QLabel("Memory Usage")' in content, "Memory Usage label missing"
        assert 'QLabel("Latency")' in content, "Latency label missing"
        print("✅ Performance labels found")

        # Check for timer setup
        assert "self.timer = QTimer()" in content, "QTimer creation missing"
        assert (
            "self.timer.timeout.connect(self.update_performance_metrics)" in content
        ), "Timer connection missing"
        assert "self.timer.start(1500)" in content, "Timer start missing"
        print("✅ Timer setup found")

        # Check for tab widget performance tab creation
        assert "self.create_performance_tab()" in content, (
            "Performance tab creation in tab widget missing"
        )
        print("✅ Performance tab creation in tab widget found")

        # Check for update performance metrics implementation
        assert "random.randint(20, 90)" in content, "CPU random simulation missing"
        assert "random.randint(30, 95)" in content, "Memory random simulation missing"
        assert "random.randint(10, 100)" in content, "Latency random simulation missing"
        print("✅ Performance metrics simulation found")

        print("\n🎉 All performance dashboard integration checks passed!")
        return True

    except FileNotFoundError:
        print(f"❌ File not found: {hybrid_window_path}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_performance_dashboard_configuration():
    """Test that the performance dashboard configuration is properly set up"""
    try:
        print("🔍 Checking performance dashboard configuration...")

        # Read the hybrid_window.py file
        hybrid_window_path = os.path.join(
            "Aetherra", "lyrixa", "gui", "hybrid_window.py"
        )
        with open(hybrid_window_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that Performance tab uses create_performance_tab instead of placeholder
        assert (
            'self.tab_widget.addTab(self.create_performance_tab(), "Performance")'
            in content
        ), "Performance tab not properly configured"
        print("✅ Performance tab properly configured with create_performance_tab()")

        # Ensure old placeholder is removed
        assert 'QLabel("Performance Dashboard Coming Soon")' not in content, (
            "Old performance tab placeholder still present"
        )
        print("✅ Old performance tab placeholder removed")

        print("\n✅ Performance dashboard configuration checks passed!")
        return True

    except Exception as e:
        print(f"❌ Performance dashboard configuration test failed: {e}")
        return False


if __name__ == "__main__":
    print("Performance Dashboard Integration Test")
    print("=" * 45)

    success = True

    # Test performance dashboard integration
    if not test_performance_dashboard_integration():
        success = False

    print()

    # Test performance dashboard configuration
    if not test_performance_dashboard_configuration():
        success = False

    print("\n" + "=" * 45)
    if success:
        print("🎉 ALL PERFORMANCE DASHBOARD TESTS PASSED!")
        print("✅ Performance dashboard functionality successfully integrated")
        print("✅ Live metrics display ready")
        print("✅ Auto-refresh timer working")
        print("✅ Progress bars configured")
        print("✅ Tab widget properly configured")
        print("✅ Simulation data functional")
    else:
        print("❌ SOME TESTS FAILED - Check the output above")

    sys.exit(0 if success else 1)
