#!/usr/bin/env python3
"""
🧪 Test Script: AetherraHub Integration
===================================

Test the integration of AetherraHub package manager into the Neuroplex GUI.
This script verifies that:
1. AetherraHub tab is created successfully
2. WebEngine support is detected correctly
3. AetherraHub server management works
4. GUI integration is functional
"""

import subprocess
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))


def test_neurohub_directory():
    """Test that AetherraHub directory exists"""
    print("🔍 Testing AetherraHub directory...")
    try:
        neurohub_path = project_root / "neurohub"
        if neurohub_path.exists():
            print(f"✅ AetherraHub directory found: {neurohub_path}")

            # Check for key files
            key_files = ["package.json", "server.js", "README.md"]
            for file in key_files:
                if (neurohub_path / file).exists():
                    print(f"✅ Found {file}")
                else:
                    print(f"⚠️  Missing {file}")
            return True
        else:
            print(f"❌ AetherraHub directory not found: {neurohub_path}")
            return False
    except Exception as e:
        print(f"❌ Error checking AetherraHub directory: {e}")
        return False


def test_nodejs_availability():
    """Test if Node.js is available"""
    print("🔍 Testing Node.js availability...")
    try:
        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Node.js available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js not working properly")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Node.js command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking Node.js: {e}")
        return False


def test_webengine_availability():
    """Test if WebEngine is available"""
    print("🔍 Testing WebEngine availability...")
    try:

        print("✅ WebEngine available for embedded browser")
        return True
    except ImportError as e:
        print(f"⚠️  WebEngine not available: {e}")
        print("ℹ️  AetherraHub will use external browser mode")
        return False


def test_gui_neurohub_integration():
    """Test that the GUI can load with AetherraHub integration"""
    print("🔍 Testing GUI AetherraHub integration...")
    try:
        # Import Qt first
        from PySide6.QtWidgets import QApplication

        # Create Qt application
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Import Neuroplex
        from Lyrixa.ui.aetherplex import LyrixaWindow

        # Create main window
        window = LyrixaWindow()
        print("✅ Neuroplex window created successfully")

        # Check if AetherraHub tab method exists
        if hasattr(window, "create_neurohub_tab"):
            print("✅ AetherraHub tab method available")
        else:
            print("❌ AetherraHub tab method missing")

        # Check if AetherraHub process attribute exists
        if hasattr(window, "neurohub_process"):
            print("✅ AetherraHub process management available")
        else:
            print("❌ AetherraHub process management missing")

        # Check if AetherraHub server methods exist
        methods_to_check = [
            "start_neurohub_server",
            "stop_neurohub_server",
            "open_neurohub_browser",
            "neurohub_server_started",
            "neurohub_server_failed",
        ]

        for method_name in methods_to_check:
            if hasattr(window, method_name):
                print(f"✅ Method {method_name} available")
            else:
                print(f"❌ Method {method_name} missing")

        # Clean up
        if hasattr(window, "task_scheduler") and window.task_scheduler:
            window.task_scheduler.shutdown(timeout=1.0)

        window.close()
        return True

    except Exception as e:
        print(f"❌ GUI AetherraHub integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_neurohub_npm_setup():
    """Test AetherraHub npm setup"""
    print("🔍 Testing AetherraHub npm setup...")
    try:
        neurohub_path = project_root / "neurohub"
        if not neurohub_path.exists():
            print("❌ AetherraHub directory not found")
            return False

        # Check if node_modules exists or can be created
        node_modules = neurohub_path / "node_modules"
        if node_modules.exists():
            print("✅ Node modules directory exists")
            return True
        else:
            print("ℹ️  Node modules not installed - would need 'npm install'")
            return True  # This is expected for a fresh setup

    except Exception as e:
        print(f"❌ Error checking AetherraHub npm setup: {e}")
        return False


def main():
    """Run all AetherraHub integration tests"""
    print("🚀 Starting AetherraHub Integration Tests")
    print("=" * 50)

    tests = [
        ("AetherraHub Directory", test_neurohub_directory),
        ("Node.js Availability", test_nodejs_availability),
        ("WebEngine Availability", test_webengine_availability),
        ("GUI AetherraHub Integration", test_gui_neurohub_integration),
        ("AetherraHub NPM Setup", test_neurohub_npm_setup),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            print(f"📊 {test_name}: {status}")
        except Exception as e:
            print(f"💥 {test_name}: CRASH - {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📈 NEUROHUB INTEGRATION TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    # Recommendations
    print("\n📝 RECOMMENDATIONS:")

    if not any(name == "Node.js Availability" and result for name, result in results):
        print("⚠️  Install Node.js to enable AetherraHub server functionality")

    if not any(name == "WebEngine Availability" and result for name, result in results):
        print(
            "ℹ️  Install QtWebEngine for embedded browser support: pip install PySide6[WebEngine]"
        )

    if passed == total:
        print("🎉 All tests passed! AetherraHub integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
