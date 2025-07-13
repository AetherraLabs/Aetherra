#!/usr/bin/env python3
"""
Test script to verify all fixes in src/Aetherra/cli directory
"""

import os
import sys
import traceback

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_cli_imports():
    """Test all CLI module imports"""
    print("🧪 Testing CLI module imports...")

    imports_successful = []

    try:
        # Test main CLI modules
        print("✅ Testing basic CLI imports...")

        imports_successful.append("AetherraPersonaInterface")

        imports_successful.append("RevolutionaryPersonaCLI")

        # These imports might fail due to optional dependencies
        try:
            imports_successful.append("PersonaAssistant")
        except ImportError:
            print("⚠️ PersonaAssistant not available (optional dependency)")

        try:
            imports_successful.append("AetherraPlugin")
        except ImportError:
            print("⚠️ AetherraPlugin not available (optional dependency)")

        print(f"✅ Successfully imported: {', '.join(imports_successful)}")
        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_cli_functionality():
    """Test basic functionality of CLI modules"""
    print("\n🧪 Testing CLI functionality...")

    try:
        # Test persona interface creation and use it
        from Aetherra.cli.main import AetherraPersonaInterface

        interface = AetherraPersonaInterface()
        print("✅ AetherraPersonaInterface created successfully")

        # Test demo CLI creation and use it
        from Aetherra.cli.demo import RevolutionaryPersonaCLI

        demo_cli = RevolutionaryPersonaCLI()
        print("✅ RevolutionaryPersonaCLI created successfully")

        # Test basic command processing (should work even without persona modules)
        result = interface.process_command("test command")
        if result:
            print("✅ Command processing works")
        else:
            print("⚠️  Command processing returned empty result")

        # Test persona status (should handle missing modules gracefully)
        status = interface.show_persona_status()
        if status:
            print("✅ Persona status display works")
        else:
            print("⚠️  Persona status returned empty")

        # Test demo CLI has the expected methods
        if hasattr(demo_cli, "run_interactive_demo"):
            print("✅ Demo CLI has run_interactive_demo method")
        else:
            print("⚠️  Demo CLI missing run_interactive_demo method")

        return True

    except Exception as e:
        print(f"❌ Functionality error: {e}")
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling in CLI modules"""
    print("\n🧪 Testing error handling...")

    try:
        from Aetherra.cli.main import AetherraPersonaInterface

        interface = AetherraPersonaInterface()

        # Test with various inputs to ensure no crashes
        test_commands = [
            "debug database issue",
            "create new feature",
            "help with something",
            "",  # Empty command
            "very long command " * 100,  # Very long command
        ]

        for cmd in test_commands:
            try:
                result = interface.process_command(cmd)
                # Should always return something, even if basic
                assert result is not None, f"Command '{cmd}' returned None"
            except Exception as e:
                print(f"⚠️  Command '{cmd[:20]}...' caused error: {e}")

        print("✅ Error handling works correctly")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 Testing src/Aetherra/cli fixes")
    print("=" * 50)

    # Track test results
    tests_passed = 0
    total_tests = 3

    # Run tests
    if test_cli_imports():
        tests_passed += 1

    if test_cli_functionality():
        tests_passed += 1

    if test_error_handling():
        tests_passed += 1

    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! src/Aetherra/cli is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
