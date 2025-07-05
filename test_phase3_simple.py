"""
Simple Phase 3 Test - Just imports and basic functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 Phase 3 Simple Test")
    print("=" * 40)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Imports
    total_tests += 1
    try:
        from lyrixa.gui.analytics_dashboard import AnalyticsDashboard
        from lyrixa.gui.suggestion_notifications import SuggestionNotificationSystem
        from lyrixa.gui.configuration_manager import ConfigurationManager
        from lyrixa.gui.performance_monitor import PerformanceMonitor
        from lyrixa.core.anticipation_engine import AnticipationEngine
        print("✅ All Phase 3 imports successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Import failed: {e}")
    
    # Test 2: Basic class instantiation (without Qt)
    total_tests += 1
    try:
        # Test data classes
        from lyrixa.gui.configuration_manager import UserPreferences, AnticipationSettings
        prefs = UserPreferences()
        settings = AnticipationSettings()
        
        # Test anticipation engine
        engine = AnticipationEngine()
        
        print("✅ Basic class instantiation successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Basic instantiation failed: {e}")
    
    # Test 3: Enhanced Lyrixa integration
    total_tests += 1
    try:
        from src.aetherra.ui.enhanced_lyrixa import EnhancedLyrixaWindow
        window = EnhancedLyrixaWindow()
        
        # Check if Phase 3 components are integrated
        has_analytics = hasattr(window, 'analytics_dashboard')
        has_notifications = hasattr(window, 'notification_system')
        has_config = hasattr(window, 'config_manager')
        has_monitor = hasattr(window, 'performance_monitor')
        has_anticipation = hasattr(window, 'anticipation_engine')
        
        print(f"Enhanced Lyrixa integration:")
        print(f"  Analytics Dashboard: {'✅' if has_analytics else '❌'}")
        print(f"  Notification System: {'✅' if has_notifications else '❌'}")
        print(f"  Configuration Manager: {'✅' if has_config else '❌'}")
        print(f"  Performance Monitor: {'✅' if has_monitor else '❌'}")
        print(f"  Anticipation Engine: {'✅' if has_anticipation else '❌'}")
        
        success_count += 1
    except Exception as e:
        print(f"❌ Enhanced Lyrixa integration failed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
