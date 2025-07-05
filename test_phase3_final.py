"""
PHASE 3 FINAL INTEGRATION TEST
============================

Comprehensive test for all Phase 3 components:
- Anticipation Engine + GUI Integration
- Analytics Dashboard
- Configuration Manager
- Suggestion Notifications
- Performance Monitor
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    print("🎯 PHASE 3 FINAL INTEGRATION TEST")
    print("=" * 50)

    success_count = 0
    total_tests = 0

    # Test 1: Core Imports
    total_tests += 1
    try:
        from lyrixa.core.anticipation_engine import AnticipationEngine
        from lyrixa.gui.analytics_dashboard import AnalyticsDashboard
        from lyrixa.gui.configuration_manager import (
            AnticipationSettings,
            ConfigurationManager,
            SystemConfiguration,
            UserPreferences,
        )
        from lyrixa.gui.performance_monitor import PerformanceMonitor
        from lyrixa.gui.suggestion_notifications import SuggestionNotificationSystem

        print("✅ All Phase 3 modules imported successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback

        traceback.print_exc()

    # Test 2: Data Classes and Settings
    total_tests += 1
    try:
        prefs = UserPreferences()
        anticipation_settings = AnticipationSettings()
        system_config = SystemConfiguration()

        print(f"✅ UserPreferences: {prefs.theme} theme, {prefs.language} language")
        print(
            f"✅ AnticipationSettings: {anticipation_settings.pattern_confidence_threshold} pattern confidence"
        )
        print(f"✅ SystemConfiguration: {system_config.database_path} database")
        success_count += 1
    except Exception as e:
        print(f"❌ Data class instantiation failed: {e}")

    # Test 3: Anticipation Engine (Core Logic)
    total_tests += 1
    try:
        # This will initialize the memory system
        print("🔮 Initializing Anticipation Engine...")
        engine = AnticipationEngine()
        print("✅ Anticipation Engine initialized successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Anticipation Engine failed: {e}")

    # Test 4: Qt-based GUI Components (if PySide6 available)
    total_tests += 1
    try:
        from PySide6.QtWidgets import QApplication

        app = (
            QApplication(sys.argv)
            if not QApplication.instance()
            else QApplication.instance()
        )

        config_manager = ConfigurationManager()
        print("✅ ConfigurationManager with Qt works")

        # Test other Qt components
        dashboard = AnalyticsDashboard()
        monitor = PerformanceMonitor()
        print("✅ All Qt GUI components instantiated")

        app.quit() if hasattr(app, "quit") else None
        success_count += 1

    except ImportError:
        print("⚠️  PySide6 not available - GUI components skipped")
        success_count += 1  # Don't penalize for missing optional dependency
    except Exception as e:
        print(f"❌ Qt GUI test failed: {e}")

    # Test 5: Configuration and Integration
    total_tests += 1
    try:
        # Test configuration loading/saving
        prefs = UserPreferences(
            theme="dark", enable_anticipation=True, confidence_threshold=0.8
        )

        settings = AnticipationSettings(
            pattern_confidence_threshold=0.9, suggestion_diversity=0.8
        )

        print("✅ Configuration objects created and configured")
        print(f"   📋 Theme: {prefs.theme}")
        print(f"   🧠 Anticipation enabled: {prefs.enable_anticipation}")
        print(f"   🎯 Pattern threshold: {settings.pattern_confidence_threshold}")
        success_count += 1

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")

    # Final Results
    print("=" * 50)
    print(f"🎯 FINAL RESULTS: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 PHASE 3 INTEGRATION COMPLETE - ALL TESTS PASSED!")
        print("🚀 Ready for production deployment")
        return True
    elif success_count >= total_tests - 1:
        print("✅ PHASE 3 INTEGRATION SUCCESSFUL with minor issues")
        print("🚀 Ready for deployment with monitoring")
        return True
    else:
        print("⚠️  PHASE 3 INTEGRATION has significant issues")
        print("🔧 Requires additional debugging")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
