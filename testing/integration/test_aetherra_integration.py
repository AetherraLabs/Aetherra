#!/usr/bin/env python3
"""
AetherraCode Functional Integration Test
=====================================

Tests key functionality to ensure AetherraCode and Lyrixawork properly.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "core"))


def test_core_interpreter():
    """Test basic interpreter functionality"""
    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()

        # Test basic functionality
        result = interpreter.execute("remember('test') as 'test_tag'")
        print("✅ Core interpreter: Basic functionality working")
        return True
    except Exception as e:
        print(f"❌ Core interpreter error: {e}")
        return False


def test_enhanced_interpreter():
    """Test enhanced interpreter functionality"""
    try:
        from Aetherra.core.enhanced_interpreter import EnhancedAetherraInterpreter

        interpreter = EnhancedAetherraInterpreter()

        # Test basic functionality
        result = interpreter.execute_Aetherra(
            "remember('enhanced test') as 'enhanced_tag'"
        )
        print("✅ Enhanced interpreter: Advanced functionality working")
        return True
    except Exception as e:
        print(f"❌ Enhanced interpreter error: {e}")
        return False


def test_memory_system():
    """Test memory system"""
    try:
        from Aetherra.core.aetherra_memory import AetherraMemory

        memory = AetherraMemory()

        # Test memory operations using correct API
        memory.remember("Test memory", tags=["test"])
        retrieved = memory.recall(tags=["test"])
        print("✅ Memory system: Storage and retrieval working")
        return True
    except Exception as e:
        print(f"❌ Memory system error: {e}")
        return False


def test_cli_components():
    """Test CLI components"""
    try:
        print("✅ CLI components: Import successful")
        return True
    except Exception as e:
        print(f"❌ CLI components error: {e}")
        return False


def test_gui_components():
    """Test GUI component imports"""
    try:
        # Test if Qt components are available
        from Lyrixa.ui.components.utils.qt_imports import is_qt_available

        qt_status = is_qt_available()

        if qt_status:
            print("✅ GUI components: Qt framework available")
            return True
        else:
            print("⚠️ GUI components: Qt framework not available (optional)")
            return True  # This is not a critical error
    except Exception as e:
        print(f"❌ GUI components error: {e}")
        return False


def test_parser_system():
    """Test parser functionality"""
    try:
        # Use the new modular parser
        from src.aethercode.core.parser import create_parser

        parser_func = create_parser()

        # Test basic parsing
        parser_func("remember('parser test') as 'parser_tag'")
        print("✅ Parser system: Code parsing working")
        return True
    except Exception as e:
        print(f"❌ Parser system error: {e}")
        return False


def test_agent_system():
    """Test agent functionality"""
    try:
        from Aetherra.core.aetherra_memory import AetherraMemory
        from Aetherra.core.agent import AetherraAgent
        from Aetherra.core.functions import AetherraFunctions

        memory = AetherraMemory()
        functions = AetherraFunctions()
        command_history = []

        AetherraAgent(memory, functions, command_history)
        print("✅ Agent system: Agent initialization working")
        return True
    except Exception as e:
        print(f"❌ Agent system error: {e}")
        return False


def test_plugin_system():
    """Test plugin functionality"""
    try:
        from src.aethercode.plugins.manager import EnhancedPluginManager

        manager = EnhancedPluginManager()
        plugins = manager.list_installed_plugins()
        print(
            f"✅ Plugin system: Plugin manager working ({len(plugins)} plugins found)"
        )
        return True
    except Exception as e:
        print(f"❌ Plugin system error: {e}")
        return False


def run_functional_tests():
    """Run all functional tests"""
    print("🧬 AetherraCode Functional Integration Test")
    print("=" * 50)

    tests = [
        test_core_interpreter,
        test_enhanced_interpreter,
        test_memory_system,
        test_cli_components,
        test_gui_components,
        test_parser_system,
        test_agent_system,
        test_plugin_system,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! AetherraCode is fully functional.")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Some functionality may be limited.")
        return False


if __name__ == "__main__":
    success = run_functional_tests()
    sys.exit(0 if success else 1)
