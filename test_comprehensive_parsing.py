#!/usr/bin/env python3
"""
Test comprehensive NeuroCode parsing with the production grammar
"""

from core.production_neurocode_grammar import NeuroCodeProductionParser


def test_comprehensive_neurocode():
    """Test the parser with a comprehensive NeuroCode program"""

    parser = NeuroCodeProductionParser()

    # Comprehensive NeuroCode program
    neurocode_program = """# Advanced NeuroCode Program
goal: "Build an intelligent system" priority: high
agent: on

model: "gpt-4"
assistant: "Help me develop NeuroCode"

remember("NeuroCode is a cognitive programming language") as "core_concept"
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

    print("🧬 Testing Comprehensive NeuroCode Program")
    print("=" * 50)
    print(f"Program length: {len(neurocode_program)} characters")
    print()

    try:
        ast = parser.parse(neurocode_program)
        print(f"✓ Successfully parsed program with {len(ast.children)} top-level statements")

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
    test_comprehensive_neurocode()
