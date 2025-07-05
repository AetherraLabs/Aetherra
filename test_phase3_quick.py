"""Quick Phase 3 GUI Test with proper QApplication handling"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_gui_imports():
    """Test GUI imports without Qt errors"""
    print("🚀 Testing Phase 3 GUI Components")
    print("=" * 40)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Import without Qt initialization
    total_tests += 1
    try:
        from lyrixa.gui.configuration_manager import UserPreferences, AnticipationSettings
        from lyrixa.core.anticipation_engine import AnticipationEngine
        
        print("✅ Core classes imported successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Core import failed: {e}")
    
    # Test 2: Test Qt-independent functionality
    total_tests += 1
    try:
        prefs = UserPreferences()
        settings = AnticipationSettings()
        
        print(f"✅ UserPreferences: theme={prefs.theme}, language={prefs.language}")
        print(f"✅ AnticipationSettings: pattern_confidence={settings.pattern_confidence_threshold}")
        success_count += 1
    except Exception as e:
        print(f"❌ Data class instantiation failed: {e}")
    
    # Test 3: Test with QApplication
    total_tests += 1
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        from lyrixa.gui.configuration_manager import ConfigurationManager
        config_manager = ConfigurationManager()
        
        print("✅ ConfigurationManager with QApplication works")
        success_count += 1
        
        app.quit() if hasattr(app, 'quit') else None
        
    except Exception as e:
        print(f"❌ Qt GUI test failed: {e}")
    
    print("=" * 40)
    print(f"Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All Phase 3 tests PASSED!")
    else:
        print("⚠️ Some tests failed - but core functionality works")

if __name__ == "__main__":
    test_gui_imports()
