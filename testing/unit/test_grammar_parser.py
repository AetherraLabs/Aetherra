#!/usr/bin/env python3
"""
Test the AetherraCode grammar parser
"""

import sys

sys.path.append(".")

from Aetherra.core.refined_aethercode_grammar import RefinedNeuroCodeParser


def test_parser():
    """Test the refined parser with basic AetherraCode constructs"""

    parser = RefinedNeuroCodeParser()

    # Test basic AetherraCode constructs
    test_cases = [
        'goal: "Create a secure system" priority: high',
        "agent: on",
        'remember("Important fact") as "fact"',
        'model: "gpt-4"',
        'assistant: "Help me code"',
        'if x > 10:\n    remember("Large value")\nend',
    ]

    print("🧬 Testing AetherraCode Grammar Parser")
    print("=" * 40)

    for i, test in enumerate(test_cases):
        print(f"\nTest {i + 1}: {test}")
        try:
            result = parser.parse(test)
            print(f"✓ Parsed successfully: {result.node_type}")
            print(f"  Value: {result.value}")
            if result.children:
                print(f"  Children: {len(result.children)}")
        except Exception as e:
            print(f"✗ Parse error: {e}")


if __name__ == "__main__":
    test_parser()
