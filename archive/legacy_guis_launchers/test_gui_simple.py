#!/usr/bin/env python3
"""Simple Qt GUI test with proper cleanup"""

try:
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    from lyrixa.gui.performance_monitor import PerformanceMonitor

    monitor = PerformanceMonitor()
    print("✅ Performance Monitor working")

    from lyrixa.gui.analytics_dashboard import AnalyticsDashboard

    dashboard = AnalyticsDashboard()
    print("✅ Analytics Dashboard working")

    from lyrixa.gui.configuration_manager import ConfigurationManager

    config = ConfigurationManager()
    print("✅ Configuration Manager working")

    # Proper cleanup
    print("🧹 Cleaning up...")
    monitor.stop_monitoring()
    del monitor
    del dashboard
    del config

    app.quit()
    print("✅ All GUI components working fine")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
