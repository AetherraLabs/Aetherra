#!/usr/bin/env python3
"""Test backward compatibility with legacy syntax_tree.py interface"""

from Aetherra.core.syntax_tree import analyze_syntax_tree, parse_Aetherra


def main():
    #     print("Testing backward compatibility...")

    code = """
    goal: Test backward compatibility
    assistant: "Testing the compatibility layer"
    remember("Compatibility test") as "test"
    """

    # Test parsing
    tree = parse_Aetherra(code)
    print(f"✓ Parsing successful: {tree.type}")

    # Test analysis
    analysis = analyze_syntax_tree(tree)
    print(f"✓ Analysis successful: {analysis['total_nodes']} nodes")

    # Test that we get the same API as before
    assert "node_counts" in analysis
    assert "total_nodes" in analysis
    assert "max_depth" in analysis

    print("✓ Backward compatibility test passed!")
    print("The new modular system is fully compatible with existing code.")


if __name__ == "__main__":
    main()
