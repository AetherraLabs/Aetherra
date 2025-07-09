#!/usr/bin/env python3
"""
Comprehensive test for core/ast_parser.py
Tests all functionality and integration with the AetherraCode system
"""

import sys

from core.ast_parser import (
    AetherraASTParser,
    AetherraCommand,
    FunctionCallCommand,
    FunctionDefineCommand,
    RecallCommand,
    RememberCommand,
    VariableAssignment,
)


def test_ast_parser_comprehensive():
    """Comprehensive test of all AST parser functionality"""
    print("🚀 Starting Comprehensive AST Parser Tests")
    print("=" * 50)

    parser = AetherraASTParser()
    passed = 0
    total = 0

    # Test 1: Basic Command Parsing
    print("\n📝 Test 1: Basic Command Parsing")
    test_cases = [
        ('remember Hello World as "greeting"', "remember", RememberCommand),
        ('recall tag: "greeting"', "recall", RecallCommand),
        ("x = 42", "assignment", VariableAssignment),
        ('print("hello")', "expression", AetherraCommand),
        ("define add(a, b): return a + b", "function_def", FunctionDefineCommand),
        ("run add(5, 3)", "function_call", FunctionCallCommand),
    ]

    for code, expected_type, expected_class in test_cases:
        total += 1
        cmd = parser.parse_line(code)
        if (
            cmd
            and cmd.command_type == expected_type
            and isinstance(cmd, expected_class)
        ):
            print(f"✓ {code} -> {expected_type}")
            passed += 1
        else:
            print(
                f"✗ {code} -> Expected {expected_type}, got {cmd.command_type if cmd else 'None'}"
            )

    # Test 2: Complex Block Parsing
    print("\n🔧 Test 2: Complex Block Parsing")
    complex_block = [
        "define factorial(n)",
        "    if n <= 1",
        "        return 1",
        "    else",
        "        return n * factorial(n - 1)",
        "    end",
        "end",
        "x = 5",
        "result = factorial(x)",
        'remember result as "math"',
    ]

    total += 1
    block_cmds = parser.parse_block(complex_block)
    if len(block_cmds) >= 3:  # Should have function, assignment, and remember
        print(f"✓ Complex block parsed: {len(block_cmds)} commands")
        passed += 1
    else:
        print(f"✗ Complex block parsing failed: {len(block_cmds)} commands")

    # Test 3: Variable System
    print("\n💾 Test 3: Variable System")
    total += 1
    parser.set_variable("test_var", 100)
    value = parser.get_variable("test_var")
    if value == 100:
        print("✓ Variable storage and retrieval")
        passed += 1
    else:
        print(f"✗ Variable system failed: {value}")

    # Test 4: Condition Evaluation
    print("\n🧮 Test 4: Condition Evaluation")
    test_conditions = [
        ("test_var > 50", True),
        ("test_var == 100", True),
        ("test_var < 50", False),
        ("test_var != 100", False),
    ]

    for condition, expected in test_conditions:
        total += 1
        result = parser.evaluate_condition(condition)
        if result == expected:
            print(f"✓ {condition} -> {result}")
            passed += 1
        else:
            print(f"✗ {condition} -> Expected {expected}, got {result}")

    # Test 5: Iterable Expansion
    print("\n📋 Test 5: Iterable Expansion")
    iterable_tests = [
        ("1..5", [1, 2, 3, 4, 5]),
        ("[a, b, c]", ["a", "b", "c"]),
        ("single", ["single"]),
    ]

    for iterable_str, expected in iterable_tests:
        total += 1
        result = parser.expand_iterable(iterable_str)
        if result == expected:
            print(f"✓ {iterable_str} -> {result}")
            passed += 1
        else:
            print(f"✗ {iterable_str} -> Expected {expected}, got {result}")

    # Test 6: Syntax Validation
    print("\n✅ Test 6: Syntax Validation")
    validation_tests = [
        ('remember test as "example"', True),
        ('recall tag: "test"', True),
        ("", False),  # Empty string should be invalid
        ("x = 10", True),
        ("   ", False),  # Whitespace only should be invalid
    ]

    for code, expected in validation_tests:
        total += 1
        valid, error = parser.validate_syntax(code)
        if (valid and expected) or (not valid and not expected):
            print(f"✓ '{code}' -> {'Valid' if valid else 'Invalid'}")
            passed += 1
        else:
            print(
                f"✗ '{code}' -> Expected {'Valid' if expected else 'Invalid'}, got {'Valid' if valid else 'Invalid'}"
            )

    # Test 7: Error Handling
    print("\n🛡️ Test 7: Error Handling")
    total += 1
    try:
        # Test with malformed input
        cmd = parser.parse_line("malformed remember command")
        print("✓ Error handling: Gracefully handled malformed input")
        passed += 1
    except Exception as e:
        print(f"✗ Error handling failed: {e}")

    # Final Results
    print(f"\n{'=' * 50}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print(f"{'=' * 50}")
    print(f"Passed: {passed}/{total} tests ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED! ast_parser.py is production-ready!")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False


def main():
    """Run comprehensive tests"""
    try:
        success = test_ast_parser_comprehensive()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
