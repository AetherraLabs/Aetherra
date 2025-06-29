#!/usr/bin/env python3
"""
Modular Component Verification Test
==================================

This script verifies that all modular components can be imported
and instantiated correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_component_imports():
    """Test that all components can be imported"""
    print("🧪 Testing Component Imports...")

    try:
        # Test Qt imports
        from ui.components.utils.qt_imports import QT_AVAILABLE, QT_BACKEND

        print(f"✅ Qt imports: {QT_BACKEND} ({'Available' if QT_AVAILABLE else 'Not Available'})")

        # Test theme
        from ui.components.theme import ModernTheme

        print("✅ ModernTheme imported successfully")

        # Test base card
        from ui.components.cards import ModernCard

        print("✅ ModernCard imported successfully")

        # Test all panels
        from ui.components.panels import (
            GoalTrackingPanel,
            LLMProviderPanel,
            MemoryVisualizationPanel,
            NaturalLanguagePanel,
            PerformanceMonitorPanel,
            PluginManagerPanel,
        )

        print("✅ All 6 panel components imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_component_instantiation():
    """Test that components can be instantiated"""
    print("\n🏗️ Testing Component Instantiation...")

    if not test_component_imports():
        return False

    try:
        from ui.components.utils.qt_imports import QT_AVAILABLE

        if not QT_AVAILABLE:
            print("⚠️ Qt not available - skipping instantiation tests")
            return True

        from ui.components.panels import (
            GoalTrackingPanel,
            LLMProviderPanel,
            MemoryVisualizationPanel,
            NaturalLanguagePanel,
            PerformanceMonitorPanel,
            PluginManagerPanel,
        )
        from ui.components.utils.qt_imports import ensure_qt_app

        # Ensure Qt app exists
        app = ensure_qt_app()

        # Test instantiation of each panel
        panels = [
            ("LLM Provider", LLMProviderPanel),
            ("Memory Visualization", MemoryVisualizationPanel),
            ("Performance Monitor", PerformanceMonitorPanel),
            ("Goal Tracking", GoalTrackingPanel),
            ("Plugin Manager", PluginManagerPanel),
            ("Natural Language", NaturalLanguagePanel),
        ]

        created_panels = []

        for name, panel_class in panels:
            try:
                panel = panel_class()
                created_panels.append(panel)
                print(f"✅ {name} panel instantiated successfully")
            except Exception as e:
                print(f"❌ {name} panel failed: {e}")
                return False

        print(f"✅ All {len(created_panels)} panels instantiated successfully")

        # Clean up
        for panel in created_panels:
            panel.deleteLater() if hasattr(panel, "deleteLater") else None

        return True

    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        return False


def test_modular_architecture():
    """Test the modular architecture"""
    print("\n🏛️ Testing Modular Architecture...")

    try:
        # Test main modular window import
        from ui.neuroplex_fully_modular import FullyModularNeuroplexWindow

        print("✅ Fully modular main window imported successfully")

        # Test launcher import
        from launch_fully_modular_neuroplex import main as launcher_main

        print("✅ Fully modular launcher imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Modular architecture import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Modular architecture error: {e}")
        return False


def run_verification():
    """Run all verification tests"""
    print("🔍 Neuroplex Modular Component Verification")
    print("=" * 50)

    tests = [
        ("Component Imports", test_component_imports),
        ("Component Instantiation", test_component_instantiation),
        ("Modular Architecture", test_modular_architecture),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Modular architecture is working perfectly!")
        print("\n🚀 You can now run the modular Neuroplex with confidence:")
        print("   python launch_fully_modular_neuroplex.py")
    else:
        print("⚠️ Some tests failed - please check the error messages above")

    return passed == total


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
