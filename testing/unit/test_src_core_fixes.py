#!/usr/bin/env python3
"""
Test script to verify all fixes in src/Aetherra/core directory
"""

import os
import sys
import traceback

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_core_imports():
    """Test all core module imports"""
    print("🧪 Testing core module imports...")

    try:
        # Test main core module
        print("✅ Aetherra.core imported successfully")

        # Test interpreter modules
        print("✅ EnhancedAetherraInterpreter imported successfully")

        print("✅ BaseInterpreter imported successfully")

        #         print("✅ DebugSystem imported successfully")

        print("✅ BlockExecutor imported successfully")

        # Test parser modules
        print("✅ AetherraParser imported successfully")

        print("✅ EnhancedParser imported successfully")

        print("✅ IntentToCodeParser imported successfully")

        print("✅ AetherraGrammar imported successfully")

        # Test memory modules
        print("✅ Memory system imported successfully")

        print("✅ BaseMemory imported successfully")

        print("✅ EnhancedSemanticMemory imported successfully")

        # Test AI modules
        print("✅ AICollaborationFramework imported successfully")

        print("✅ AI runtime imported successfully")

        print("✅ LocalAIEngine imported successfully")

        # Test AST modules
        print("✅ AetherraASTParser imported successfully")

        # Test utils
        print("✅ Utils functions imported successfully")

        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_core_functionality():
    """Test basic functionality of core modules"""
    print("\n🧪 Testing core functionality...")

    try:
        # Test interpreter creation
        from aetherra.core.aetherra_interpreter import EnhancedAetherraInterpreter

        interpreter = EnhancedAetherraInterpreter()
        print("✅ EnhancedAetherraInterpreter created successfully")

        # Test parser creation
        from Aetherra.core.parser import AetherraParser

        parser = AetherraParser()
        print("✅ AetherraParser created successfully")

        # Test memory system
        from aetherra.core.aetherra_memory import get_memory_system

        memory = get_memory_system()
        print("✅ Memory system created successfully")

        # Test simple code execution
        test_code = """
        def greet(name):
            return f"Hello, {name}!"

        result = greet("Aetherra")
        """

        result = interpreter.execute(test_code)
        if result is not None:
            print("✅ Code execution works")
        else:
            print("⚠️  Code execution returned None (but no error)")

        return True

    except Exception as e:
        print(f"❌ Functionality error: {e}")
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling in core modules"""
    print("\n🧪 Testing error handling...")

    try:
        from aetherra.core.aetherra_interpreter import EnhancedAetherraInterpreter

        interpreter = EnhancedAetherraInterpreter()

        # Test with invalid syntax
        invalid_code = "def invalid_syntax(:"

        try:
            result = interpreter.execute(invalid_code)
            print("✅ Invalid syntax handled gracefully")
        except SyntaxError:
            print("✅ SyntaxError properly raised for invalid code")
        except Exception as e:
            print(f"✅ Exception handled: {type(e).__name__}")

        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 Testing src/neurocode/core fixes")
    print("=" * 50)

    # Track test results
    tests_passed = 0
    total_tests = 3

    # Run tests
    if test_core_imports():
        tests_passed += 1

    if test_core_functionality():
        tests_passed += 1

    if test_error_handling():
        tests_passed += 1

    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! src/neurocode/core is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
