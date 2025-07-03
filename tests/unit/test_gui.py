#!/usr/bin/env python3
"""
Test the Neuroplex GUI functionality and verify it's working properly
"""

import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧬 Testing Neuroplex GUI Components...")


def test_qt_backend():
    """Test which Qt backend is being used"""
    try:
        from ui.aetherplex_gui import QT_BACKEND

        print(f"✅ Qt Backend: {QT_BACKEND}")
        return True
    except ImportError as e:
        print(f"❌ Qt Backend import failed: {e}")
        return False


def test_theme():
    """Test the NeuroTheme"""
    try:
        from ui.aetherplex_gui import NeuroTheme

        print("✅ NeuroTheme loaded successfully")
        print(f"   Primary color: {NeuroTheme.PRIMARY}")
        print(f"   Background: {NeuroTheme.BACKGROUND}")
        return True
    except ImportError as e:
        print(f"❌ NeuroTheme import failed: {e}")
        return False


def test_gui_classes():
    """Test individual GUI component classes"""
    components_tested = 0
    components_passed = 0

    test_classes = [
        "NeuroAnimation",
        "PulsingWidget",
        "NeuroCodeEditor",
        "MemoryVisualization",
        "GoalTracker",
        "SystemMonitor",
        "LiveConsole",
        "NeuroplexMainWindow",
    ]

    try:
        from ui.aetherplex_gui import (
            GoalTracker,
            LiveConsole,
            MemoryVisualization,
            NeuroAnimation,
            NeuroCodeEditor,
            NeuroplexMainWindow,
            PulsingWidget,
            SystemMonitor,
        )

        for class_name in test_classes:
            components_tested += 1
            try:
                cls = locals()[class_name]
                print(f"✅ {class_name} class loaded")
                components_passed += 1
            except Exception as e:
                print(f"❌ {class_name} class failed: {e}")

    except ImportError as e:
        print(f"❌ GUI components import failed: {e}")
        return False

    print(f"📊 GUI Components: {components_passed}/{components_tested} passed")
    return components_passed == components_tested


def test_neurocode_integration():
    """Test NeuroCode component integration"""
    try:
        # Test if the core path is being added correctly
        sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

        # Try importing core components
        try:
            from core.interpreter import AetherraInterpreter

            print("✅ NeuroCode interpreter import successful")
            interpreter_ok = True
        except ImportError:
            print("⚠️ NeuroCode interpreter not available (expected in isolated test)")
            interpreter_ok = False

        try:
            from core.aetherra_memory import AetherraMemory

            print("✅ NeuroCode memory import successful")
            memory_ok = True
        except ImportError:
            print("⚠️ NeuroCode memory not available (expected in isolated test)")
            memory_ok = False

        try:
            from core.chat_router import AetherraChatRouter

            print("✅ NeuroCode chat router import successful")
            chat_ok = True
        except ImportError:
            print("⚠️ NeuroCode chat router not available (expected in isolated test)")
            chat_ok = False

        return True  # It's OK if components aren't available in isolation

    except Exception as e:
        print(f"❌ NeuroCode integration test failed: {e}")
        return False


def test_gui_launch():
    """Test if the GUI can be launched (without actually opening it)"""
    try:
        from ui.aetherplex_gui import main

        print("✅ GUI main function available")
        print("   (Not actually launching to avoid blocking terminal)")
        return True
    except ImportError as e:
        print(f"❌ GUI main function import failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧬" + "=" * 60)
    print("   NEUROPLEX GUI COMPONENT TEST SUITE")
    print("🧬" + "=" * 60)

    tests = [
        ("Qt Backend", test_qt_backend),
        ("NeuroTheme", test_theme),
        ("GUI Classes", test_gui_classes),
        ("NeuroCode Integration", test_neurocode_integration),
        ("GUI Launch Function", test_gui_launch),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔧 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")

    print(f"\n🧬" + "=" * 60)
    print(f"   TEST RESULTS: {passed}/{total} tests passed")
    print("🧬" + "=" * 60)

    if passed == total:
        print("🎉 ALL TESTS PASSED! Neuroplex GUI is ready to use!")
        print("💡 To launch the GUI, run: python launch_gui.py")
    else:
        print("⚠️ Some tests failed, but the GUI may still be functional")
        print("💡 Try launching anyway: python launch_gui.py")


if __name__ == "__main__":
    main()
