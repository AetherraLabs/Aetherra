#!/usr/bin/env python3
"""
GUI Error Detection and Fixing Script
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_individual_imports():
    """Test each GUI module individually to identify specific errors"""

    modules_to_test = [
        "lyrixa.gui.__init__",
        "lyrixa.gui.analytics_dashboard",
        "lyrixa.gui.suggestion_notifications",
        "lyrixa.gui.configuration_manager",
        "lyrixa.gui.performance_monitor",
    ]

    errors = []

    for module in modules_to_test:
        try:
            print(f"Testing {module}...")
            __import__(module)
            print(f"✅ {module} imported successfully")
        except Exception as e:
            print(f"❌ {module} failed: {e}")
            errors.append((module, str(e)))
            import traceback

            traceback.print_exc()

    return errors


def test_class_instantiation():
    """Test instantiating main classes"""

    try:
        from lyrixa.gui.configuration_manager import (
            AnticipationSettings,
            UserPreferences,
        )

        prefs = UserPreferences()
        settings = AnticipationSettings()
        print("✅ Data classes work")
    except Exception as e:
        print(f"❌ Data class error: {e}")
        return False

    try:
        # Test with PySide6 available
        from PySide6.QtWidgets import QApplication

        app = (
            QApplication(sys.argv)
            if not QApplication.instance()
            else QApplication.instance()
        )

        from lyrixa.gui.configuration_manager import ConfigurationManager

        config = ConfigurationManager()
        print("✅ Qt classes work")

        return True
    except ImportError:
        print("⚠️ PySide6 not available - Qt tests skipped")
        return True
    except Exception as e:
        print(f"❌ Qt class error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 GUI Error Detection")
    print("=" * 40)

    # Test imports
    import_errors = test_individual_imports()

    print("\n🧪 Testing Class Instantiation")
    print("=" * 40)
    instantiation_success = test_class_instantiation()

    print("\n📊 Summary")
    print("=" * 40)

    if import_errors:
        print("❌ Import errors found:")
        for module, error in import_errors:
            print(f"   • {module}: {error}")
    else:
        print("✅ All imports successful")

    if instantiation_success:
        print("✅ Class instantiation successful")
    else:
        print("❌ Class instantiation failed")

    if not import_errors and instantiation_success:
        print("\n🎉 No errors found in GUI modules!")
    else:
        print("\n🔧 Errors need to be fixed")
