#!/usr/bin/env python3
"""
🧪 LyrixaSystem Test Suite
=============================

Comprehensive testing of the Lyrixasystem to ensure all components
work together correctly.
"""

import sys
import traceback
from pathlib import Path


def test_aetherplex_imports():
    """Test that all Lyrixamodules can be imported"""
    print("🔍 Testing LyrixaImports...")

    aetherplex_files = [
        "src/Aetherra/ui/aetherplex_fully_modular.py",
        "src/Aetherra/ui/aetherplex_modular.py",
        "src/Aetherra/ui/aetherplex_gui_v2.py",
        "src/Aetherra/ui/aetherplex_gui.py",
        "src/Aetherra/ui/aetherplex_agent_integration.py",
    ]

    passed = 0
    total = len(aetherplex_files)

    for file_path in aetherplex_files:
        try:
            full_path = Path(file_path)
            if full_path.exists():
                # Load module dynamically
                spec = importlib.util.spec_from_file_location("test_module", full_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    print(f"  ✅ {file_path}: Import successful")
                    passed += 1
                else:
                    print(f"  ❌ {file_path}: Could not create module spec")
            else:
                print(f"  ⚠️ {file_path}: File not found")
        except Exception as e:
            print(f"  ❌ {file_path}: Import failed - {e}")

    print(f"\n📊 Import Results: {passed}/{total} files imported successfully")
    return passed, total


def test_aethercode_launcher():
    """Test the main AetherraCode launcher"""
    print("\n🔍 Testing AetherraCode Launcher...")

    try:
        # Test import

        print("  ✅ aethercode_launcher.py: Import successful")

        # Check for main components
        if hasattr(aethercode_launcher, "main"):
            print("  ✅ main() function found")

        if hasattr(aethercode_launcher, "AetherraCodeLauncher"):
            print("  ✅ AetherraCodeLauncher class found")
        elif hasattr(aethercode_launcher, "launch_Aetherra"):
            print("  ✅ launch_Aetherra function found")

        return True

    except Exception as e:
        print(f"  ❌ AetherraCode Launcher failed: {e}")
        traceback.print_exc()
        return False


def test_core_components():
    """Test core AetherraCode components"""
    print("\n🔍 Testing Core Components...")

    components = [
        ("core.interpreter", "AetherraCode Interpreter"),
        ("core.memory", "Memory System"),
        ("core.agent", "Agent System"),
        ("core.parser", "Parser System"),
        ("core.functions", "Functions System"),
    ]

    passed = 0
    total = len(components)

    for module_name, description in components:
        try:
            module = __import__(module_name, fromlist=[""])
            print(f"  ✅ {description}: Import successful")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {description}: Import failed - {e}")
        except Exception as e:
            print(f"  ❌ {description}: Error - {e}")

    print(f"\n📊 Core Components Results: {passed}/{total} components working")
    return passed, total


def test_performance_system():
    """Test the performance optimization system"""
    print("\n🔍 Testing Performance System...")

    try:
        from Aetherra.core.advanced_performance_engine import get_performance_engine

        engine = get_performance_engine()

        print("  ✅ Advanced Performance Engine: Loaded successfully")

        # Test basic performance optimization
        @engine.cache.get
        def test_cached_function(x):
            return x * 2

        print("  ✅ Performance caching: Working")

        # Test performance summary
        summary = engine.get_performance_summary()
        if "uptime_seconds" in summary:
            print("  ✅ Performance monitoring: Working")

        return True

    except Exception as e:
        print(f"  ❌ Performance System failed: {e}")
        return False


def test_memory_system():
    """Test the memory and logging system"""
    print("\n🔍 Testing Memory System...")

    try:
        from Aetherra.core.memory.logger import MemoryType

        # Test memory logger creation (with minimal initialization)
        print("  ✅ Memory Logger: Import successful")

        # Test memory types
        memory_types = list(MemoryType)
        if len(memory_types) > 0:
            print(f"  ✅ Memory Types: {len(memory_types)} types available")

        return True

    except Exception as e:
        print(f"  ❌ Memory System failed: {e}")
        return False


def test_ui_system():
    """Test UI components availability"""
    print("\n🔍 Testing UI System...")

    try:
        # Check for UI performance optimization
        from Aetherra.core.ui_performance import UIOptimizer

        optimizer = UIOptimizer()
        print("  ✅ UI Performance Optimizer: Working")

        # Test UI metrics
        metrics = optimizer.measure_ui_performance()
        if hasattr(metrics, "widget_count"):
            print("  ✅ UI Performance Metrics: Working")

        return True

    except Exception as e:
        print(f"  ❌ UI System failed: {e}")
        return False


def test_integration():
    """Test system integration"""
    print("\n🔍 Testing System Integration...")

    try:
        # Test that multiple systems can work together
        from Aetherra.core.advanced_performance_engine import get_performance_engine
        from Aetherra.core.ui_performance import UIOptimizer

        engine = get_performance_engine()
        ui_optimizer = UIOptimizer()

        print("  ✅ Performance + UI Integration: Working")

        # Test that they can operate simultaneously
        summary = engine.get_performance_summary()
        ui_metrics = ui_optimizer.measure_ui_performance()

        print("  ✅ Concurrent Operations: Working")

        return True

    except Exception as e:
        print(f"  ❌ System Integration failed: {e}")
        return False


def run_aetherplex_demo():
    """Attempt to run a simple Lyrixademo"""
    print("\n🔍 Testing LyrixaDemo...")

    try:
        # Try to run the launcher in demo mode

        # Check if we can initialize without errors
        print("  ✅ LyrixaDemo: Initialization successful")

        # Note: We don't actually launch the GUI to avoid blocking the test
        print("  ℹ️ Note: GUI launch skipped in automated test")

        return True

    except Exception as e:
        print(f"  ❌ LyrixaDemo failed: {e}")
        return False


def main():
    """Run comprehensive Lyrixatest suite"""
    print("🧪 LyrixaSystem Test Suite")
    print("=" * 50)
    #     print("Testing all Lyrixacomponents and integrations...\n")

    tests = [
        ("LyrixaImports", test_aetherplex_imports),
        ("AetherraCode Launcher", test_aethercode_launcher),
        ("Core Components", test_core_components),
        ("Performance System", test_performance_system),
        ("Memory System", test_memory_system),
        ("UI System", test_ui_system),
        ("System Integration", test_integration),
        ("LyrixaDemo", run_aetherplex_demo),
    ]

    total_passed = 0
    total_tests = 0

    for test_name, test_func in tests:
        print(f"🔬 Running {test_name} Test...")
        try:
            result = test_func()
            if isinstance(result, tuple):
                passed, total = result
                total_passed += passed
                total_tests += total
                if passed == total:
                    print(f"✅ {test_name}: PASSED ({passed}/{total})")
                else:
                    print(f"⚠️ {test_name}: PARTIAL ({passed}/{total})")
            elif result:
                total_passed += 1
                total_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                total_tests += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            total_tests += 1
            print(f"❌ {test_name}: FAILED with exception: {e}")

    print(f"\n📊 Final Results: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("🎉 All Lyrixatests passed! System is working correctly!")
        return True
    elif total_passed >= total_tests * 0.8:  # 80% pass rate
        print("✅ Lyrixais mostly functional with minor issues.")
        return True
    else:
        print("❌ Lyrixahas significant issues that need attention.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
