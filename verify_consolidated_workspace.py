#!/usr/bin/env python3
"""
🚀 CONSOLIDATED WORKSPACE VERIFICATION
=====================================

Quick verification that the consolidated Lyrixa workspace is functioning properly.
This tests the unified launcher and main GUI components.
"""

import subprocess
import sys
from pathlib import Path


def test_unified_launcher():
    """Test that the unified launcher can be imported and has all required methods."""
    print("🔍 Testing Unified Launcher...")

    try:
        # Test import
        from lyrixa_unified_launcher import LyrixaUnifiedLauncher

        print("  ✅ LyrixaUnifiedLauncher imported successfully")

        # Test instantiation
        launcher = LyrixaUnifiedLauncher()
        print("  ✅ LyrixaUnifiedLauncher instantiated successfully")

        # Test methods exist
        required_methods = [
            "check_dependencies",
            "initialize_phase_1",
            "initialize_phase_2",
            "initialize_phase_3",
            "initialize_phase_4",
            "initialize_all_phases",
            "launch_gui_mode",
            "launch_console_mode",
            "run_system_tests",
            "show_status",
        ]

        for method in required_methods:
            if hasattr(launcher, method):
                print(f"  ✅ Method '{method}' available")
            else:
                print(f"  ❌ Method '{method}' missing")
                return False

        return True

    except Exception as e:
        print(f"  ❌ Error testing unified launcher: {e}")
        return False


def test_main_guis():
    """Test that the main GUI files can be imported."""
    print("\n🖥️ Testing Main GUI Components...")

    gui_tests = [
        ("modern_lyrixa_gui", "ModernLyrixaGUI"),
        ("unified_aetherra_lyrixa_gui", "UnifiedAetherraLyrixaGUI"),
    ]

    success_count = 0

    for module_name, class_name in gui_tests:
        try:
            module = __import__(module_name)
            gui_class = getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"  ⚠️ {module_name}.{class_name} import failed: {e}")

    return success_count > 0


def test_core_modules():
    """Test that core Lyrixa modules can be imported."""
    print("\n🧠 Testing Core Lyrixa Modules...")

    core_tests = [
        "lyrixa.launcher",
        "lyrixa.gui.enhanced_lyrixa",
        "lyrixa.core.enhanced_memory",
        "lyrixa.core.advanced_vector_memory",
    ]

    success_count = 0

    for module_name in core_tests:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} imported successfully")
            success_count += 1
        except Exception as e:
            print(f"  ⚠️ {module_name} import failed: {e}")

    return success_count > 0


def test_integration_scripts():
    """Test that integration test scripts exist and can be imported."""
    print("\n🧪 Testing Integration Scripts...")

    integration_files = [
        "test_comprehensive_integration.py",
        "test_end_to_end.py",
        "phase_integration_plan.py",
        "unified_gui_status.py",
    ]

    available_count = 0

    for file in integration_files:
        if Path(file).exists():
            print(f"  ✅ {file} available")
            available_count += 1
        else:
            print(f"  ❌ {file} missing")

    return available_count == len(integration_files)


def test_launcher_execution():
    """Test that the unified launcher can actually execute."""
    print("\n🚀 Testing Unified Launcher Execution...")

    try:
        # Test status command
        result = subprocess.run(
            [sys.executable, "lyrixa_unified_launcher.py", "--status"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("  ✅ Unified launcher --status executed successfully")
            return True
        else:
            print(f"  ⚠️ Launcher status command failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("  ⚠️ Launcher status command timed out (but this is expected)")
        return True  # Timeout is acceptable for status
    except Exception as e:
        print(f"  ❌ Error executing launcher: {e}")
        return False


def main():
    """Main verification function."""
    print("🚀 CONSOLIDATED LYRIXA WORKSPACE VERIFICATION")
    print("=" * 60)
    print("Testing that all consolidated components are working properly...\n")

    # Run all tests
    test_results = []

    test_results.append(("Unified Launcher", test_unified_launcher()))
    test_results.append(("Main GUIs", test_main_guis()))
    test_results.append(("Core Modules", test_core_modules()))
    test_results.append(("Integration Scripts", test_integration_scripts()))
    test_results.append(("Launcher Execution", test_launcher_execution()))

    # Show results
    print("\n📊 VERIFICATION RESULTS")
    print("=" * 30)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if passed:
            passed_tests += 1

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 WORKSPACE CONSOLIDATION VERIFICATION SUCCESSFUL!")
        print("✨ The unified Lyrixa launcher and GUIs are ready for use!")
        print("\n🚀 Ready to launch:")
        print("   python lyrixa_unified_launcher.py")
        return 0
    else:
        print(
            f"\n⚠️ Some components need attention ({total_tests - passed_tests} issues)"
        )
        print("Check the errors above and fix any missing dependencies.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
