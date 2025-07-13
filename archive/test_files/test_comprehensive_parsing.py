#!/usr/bin/env python3
"""
Test comprehensive AetherraCode parsing with the production grammar
"""

from Aetherra.core.production_aethercode_grammar import AetherraCodeProductionParser


def test_comprehensive_Aetherra():
    """Test the parser with a comprehensive AetherraCode program"""

    parser = AetherraCodeProductionParser()

    # Comprehensive AetherraCode program
    aethercode_program = """# Advanced AetherraCode Program
goal: "Build an intelligent system" priority: high
agent: on

model: "gpt-4"
assistant: "Help me develop AetherraCode"

remember("AetherraCode is a cognitive programming language") as "core_concept"
recall "core_concept"

define process_data(input_data):
    if input_data > 0:
        analyze "positive data"
        remember("Processed positive value")
    end
    result = input_data * 2
end

for item in dataset:
    process_data(item)
end

think: "What optimizations are possible?"
optimize "performance"

debug "System working correctly"
"""

    print("🧬 Testing Comprehensive AetherraCode Program")
    print("=" * 50)
    print(f"Program length: {len(aethercode_program)} characters")
    print()

    try:
        ast = parser.parse(aethercode_program)
        print(
            f"✓ Successfully parsed program with {len(ast.children)} top-level statements"
        )

        # Print AST structure
        print("\nAST Structure:")
        print("-" * 30)
        for i, child in enumerate(ast.children):
            if hasattr(child, "node_type"):
                print(f"  {i + 1}. {child.node_type}: {child.value}")
                if hasattr(child, "metadata") and child.metadata:
                    print(f"     Metadata: {child.metadata}")
                if hasattr(child, "children") and child.children:
                    print(f"     Children: {len(child.children)}")

        print("\n" + "=" * 50)
        print("🎉 Comprehensive parsing test PASSED!")

    except Exception as e:
        print(f"✗ Parse error: {e}")
        print("\n" + "=" * 50)
        print("❌ Comprehensive parsing test FAILED!")


if __name__ == "__main__":
    test_comprehensive_Aetherra()
