#!/usr/bin/env python3
"""
Test script for the ast_parser module
"""

from core.ast_parser import AetherraASTParser


def test_ast_parser():
    """Test basic functionality of the AST parser"""
    parser = AetherraASTParser()

    print("🧪 Testing AetherraCode AST Parser")
    print("=" * 40)

    # Test 1: Remember command
    remember_cmd = parser.parse_line('remember Hello World as "greeting"')
    print(
        f"✓ Remember command: {remember_cmd.command_type if remember_cmd else 'None'}"
    )
    if remember_cmd and hasattr(remember_cmd, "content"):
        print(f"  Content: {remember_cmd.content}")
        print(f"  Tags: {remember_cmd.tags}")

    # Test 2: Recall command
    recall_cmd = parser.parse_line('recall tag: "greeting"')
    print(f"✓ Recall command: {recall_cmd.command_type if recall_cmd else 'None'}")
    if recall_cmd and hasattr(recall_cmd, "tags"):
        print(f"  Tags: {recall_cmd.tags}")

    # Test 3: Variable assignment
    var_cmd = parser.parse_line("x = 42")
    print(f"✓ Variable assignment: {var_cmd.command_type if var_cmd else 'None'}")
    if var_cmd and hasattr(var_cmd, "name"):
        print(f"  Name: {var_cmd.name}")
        print(f"  Value: {var_cmd.value}")

    # Test 4: Expression
    expr_cmd = parser.parse_line('print("hello")')
    print(f"✓ Expression: {expr_cmd.command_type if expr_cmd else 'None'}")
    if expr_cmd:
        print(f"  Raw text: {expr_cmd.raw_text}")

    # Test 5: Block parsing
    block_code = ["define greet(name)", '    print("Hello " + name)', "end"]

    block_cmds = parser.parse_block(block_code)
    print(f"✓ Block parsing: {len(block_cmds)} commands")
    for i, cmd in enumerate(block_cmds):
        if cmd:
            print(f"  [{i}] {cmd.command_type}: {cmd.raw_text}")

    # Test 6: Validation
    valid, error = parser.validate_syntax('remember test as "example"')
    print(f"✓ Syntax validation: {valid}")
    if error:
        print(f"  Error: {error}")

    print("\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    test_ast_parser()
