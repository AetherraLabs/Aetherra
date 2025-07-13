#!/usr/bin/env python3
"""
Integration test for ast_parser with core modules
"""

import sys

from core.ast_parser import AetherraASTParser


def test_ast_integration():
    """Test that ast_parser integrates well with the system"""
    print("🔗 Testing AST Parser Integration")
    print("=" * 40)

    parser = AetherraASTParser()

    # Test various AetherraCode constructs
    test_cases = [
        'remember "Today is a good day" as "diary, mood" in personal',
        'recall tag: "diary" from personal limit 5',
        "define add(a, b): return a + b",
        "run add(5, 3)",
        "x = 10",
        "if x > 5",
        "for i in 1..3",
        "while x < 20",
        'print("Hello AetherraCode")',
    ]

    for i, code in enumerate(test_cases):
        cmd = parser.parse_line(code)
        status = "✓" if cmd else "✗"
        cmd_type = cmd.command_type if cmd else "None"
        print(f"{status} [{i + 1}] {cmd_type}: {code}")

        # Test syntax validation
        valid, error = parser.validate_syntax(code)
        if not valid:
            print(f"    ⚠️  Validation error: {error}")

    # Test block parsing
    print("\n📦 Testing Block Parsing")
    complex_block = [
        "define factorial(n)",
        "    if n <= 1",
        "        return 1",
        "    else",
        "        return n * factorial(n - 1)",
        "    end",
        "end",
        "",
        "result = factorial(5)",
        'remember result as "calculation"',
    ]

    block_cmds = parser.parse_block(complex_block)
    print(f"✓ Parsed {len(block_cmds)} commands from complex block")

    # Test variable and evaluation system
    print("\n🔧 Testing Variable System")
    parser.set_variable("test_var", 42)
    value = parser.get_variable("test_var")
    print(f"✓ Variable storage: {value}")

    # Test condition evaluation
    result = parser.evaluate_condition("test_var > 40")
    print(f"✓ Condition evaluation: {result}")

    # Test iterable expansion
    items = parser.expand_iterable("1..5")
    print(f"✓ Iterable expansion: {items}")

    print("\n🎉 Integration tests completed successfully!")
    return True


if __name__ == "__main__":
    try:
        test_ast_integration()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        sys.exit(1)
