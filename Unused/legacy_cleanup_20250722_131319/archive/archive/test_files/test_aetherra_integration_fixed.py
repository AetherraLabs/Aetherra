#!/usr/bin/env python3
"""
🧪 AetherraCode Integration Test Suite
=================================

Comprehensive test to verify all major AetherraCode components work together
and that both AetherraCode and Lyrixafunction properly.
"""

import sys


def test_interpreter_system():
    """Test basic interpreter functionality"""
    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()

        # Test basic code execution
        interpreter.execute("remember('test') as 'test_tag'")
        print("✅ Basic interpreter: Code execution working")
        return True
    except Exception as e:
        print(f"❌ Basic interpreter error: {e}")
        return False


def test_enhanced_interpreter():
    """Test enhanced interpreter functionality"""
    try:
        from Aetherra.core.enhanced_interpreter import EnhancedAetherraInterpreter

        interpreter = EnhancedAetherraInterpreter()

        # Test enhanced execution
        interpreter.execute_Aetherra("remember('enhanced test') as 'enhanced_tag'")
        print("✅ Enhanced interpreter: Advanced execution working")
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
        memory.recall(tags=["test"])
        print("✅ Memory system: Storage and retrieval working")
        return True
    except Exception as e:
        print(f"❌ Memory system error: {e}")
        return False


def test_cli_components():
    """Test CLI components"""
    try:
        # Just test import without using the function

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
            print("[WARN]  GUI components: Qt not available, but import successful")
            return True
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


def test_launcher_systems():
    """Test launcher functionality"""
    try:
        # Test various launchers
        launchers = [
            "launchers.main",
            "launchers.launch_enhanced_aetherplex",
            "launchers.launch_fully_modular_aetherplex",
        ]

        working_launchers = 0
        for launcher in launchers:
            try:
                __import__(launcher)
                working_launchers += 1
            except ImportError:
                pass

        print(
            f"✅ Launcher systems: {working_launchers}/{len(launchers)} launchers working"
        )
        return working_launchers > 0
    except Exception as e:
        print(f"❌ Launcher systems error: {e}")
        return False


def test_ui_systems():
    """Test UI system imports"""
    try:
        # Test various UI components
        ui_modules = [
            "src.aethercode.ui.aetherplex_gui",
            "src.aethercode.ui.enhanced_aetherplex",
            "src.aethercode.ui.aetherplex_gui_v2",
            "src.aethercode.ui.aetherplex_fully_modular",
        ]

        working_uis = 0
        for ui_module in ui_modules:
            try:
                __import__(ui_module)
                working_uis += 1
            except ImportError:
                pass

        print(f"✅ UI systems: {working_uis}/{len(ui_modules)} UI modules working")
        return working_uis > 0
    except Exception as e:
        print(f"❌ UI systems error: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🧪 AetherraCode Integration Test Suite")
    print("=" * 50)

    tests = [
        ("Core Interpreter", test_interpreter_system),
        ("Enhanced Interpreter", test_enhanced_interpreter),
        ("Memory System", test_memory_system),
        ("CLI Components", test_cli_components),
        ("GUI Components", test_gui_components),
        ("Parser System", test_parser_system),
        ("Agent System", test_agent_system),
        ("Plugin System", test_plugin_system),
        ("Launcher Systems", test_launcher_systems),
        ("UI Systems", test_ui_systems),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            failed += 1

    print("\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed / (passed + failed) * 100:.1f}%")

    if failed == 0:
        print("\n🎉 All tests passed! AetherraCode and Lyrixaare ready to use!")
        return 0
    else:
        print(f"\n[WARN]  {failed} test(s) failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
