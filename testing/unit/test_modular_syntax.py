# test_modular_syntax.py
"""
Test Suite for Modular AetherraCode Syntax System
==============================================

This test validates that the modular syntax system works correctly
and maintains compatibility with the legacy syntax_tree.py.
"""

from Aetherra.core.syntax import SyntaxTreeVisitor, analyze_syntax_tree, parse_neurocode
from Aetherra.core.syntax.analysis import (
    extract_functions,
    generate_summary_report,
    validate_syntax_tree,
)
from Aetherra.core.syntax.nodes import NodeType
from Aetherra.core.syntax.visitor import SyntaxTreeAnalyzer


def test_basic_parsing():
    """Test basic parsing functionality"""
    code = """
    # Simple AetherraCode test
    goal: Complete the project

    define hello_world()
        assistant: "Hello, World!"
    end

    remember("This is a test")
    recall "test_memory"
    """

    tree = parse_neurocode(code)
    assert tree.type == NodeType.PROGRAM
    assert tree.has_children()
    print("✓ Basic parsing test passed")


def test_analysis():
    """Test syntax tree analysis"""
    code = """
    goal: Test analysis priority: high

    define factorial(n)
        if n <= 1:
            return 1
        else:
            return n * factorial(n-1)
    end

    x = 5
    result = factorial(x)

    remember("Calculated factorial") as "math_result"
    agent.mode = "active"
    agent.add_goal("Calculate more factorials")
    """

    tree = parse_neurocode(code)
    analysis = analyze_syntax_tree(tree)

    print("Analysis Results:")
    print(f"  Total nodes: {analysis['total_nodes']}")
    print(f"  Function count: {analysis['function_count']}")
    print(f"  Complexity score: {analysis['complexity_score']}")
    print(f"  Memory operations: {analysis['memory_operations']}")
    print(f"  Agent operations: {analysis['agent_operations']}")

    assert analysis["function_count"] >= 1
    assert analysis["memory_operations"] >= 1
    assert analysis["agent_operations"] >= 2
    print("✓ Analysis test passed")


def test_visitor_pattern():
    """Test the visitor pattern"""
    code = """
    goal: Test visitor pattern
    define greet(name)
        assistant: "Hello " + name
    end
    """

    tree = parse_neurocode(code)
    visitor = SyntaxTreeVisitor()

    result = visitor.visit(tree)
    assert isinstance(result, list)
    print("✓ Visitor pattern test passed")


def test_advanced_analysis():
    """Test advanced analysis features"""
    code = """
    goal: Complex program test

    define process_data(input_file, output_file)
        data = load_file(input_file)

        for item in data:
            if item.valid:
                result = transform(item)
                remember(result) as "processed_data"
            else:
                assistant: "Invalid item found"
        end

        save_file(output_file, results)
    end

    x = "input.txt"
    y = "output.txt"
    run process_data(x, y)

    agent.start()
    memory.search("processed_data")
    """

    tree = parse_neurocode(code)

    # Test validation
    validation = validate_syntax_tree(tree)
    print(f"Validation: {'✓ Valid' if validation['valid'] else '✗ Invalid'}")
    if validation["errors"]:
        print(f"  Errors: {validation['errors']}")
    if validation["warnings"]:
        print(f"  Warnings: {validation['warnings']}")

    # Test function extraction
    functions = extract_functions(tree)
    print(f"Functions found: {len(functions)}")
    for func in functions:
        print(f"  - {func['name']}({', '.join(func['params'])})")

    # Test analyzer
    analyzer = SyntaxTreeAnalyzer()
    detailed_stats = analyzer.analyze(tree)
    print("Detailed analysis:")
    print(f"  Max depth: {detailed_stats['max_depth']}")
    print(f"  Node type distribution: {detailed_stats['node_counts']}")

    # Test report generation
    report = generate_summary_report(tree)
    print("\nGenerated Report:")
    print("-" * 40)
    print(report)

    print("✓ Advanced analysis test passed")


def test_compatibility():
    """Test compatibility with legacy usage patterns"""
    # Test the same interface as the old syntax_tree.py
    from Aetherra.core.syntax import parse_neurocode as new_parse

    code = """
    goal: Test compatibility
    assistant: "Testing legacy compatibility"
    remember("Legacy test") as "compatibility"
    """

    tree = new_parse(code)
    assert tree.type == NodeType.PROGRAM

    # Test analysis function
    stats = analyze_syntax_tree(tree)
    assert "total_nodes" in stats
    assert "node_counts" in stats

    print("✓ Compatibility test passed")


def test_performance():
    """Test performance with larger code samples"""
    # Generate a larger AetherraCode sample
    lines = []
    lines.append("goal: Performance test")

    for i in range(50):
        lines.append(f"# Function {i}")
        lines.append(f"define func_{i}(param)")
        lines.append(f'    assistant: "Processing {i}"')
        lines.append(f'    remember("Function {i} called") as "call_log"')
        lines.append("end")
        lines.append("")

    code = "\n".join(lines)

    import time

    start_time = time.time()
    tree = parse_neurocode(code)
    parse_time = time.time() - start_time

    start_time = time.time()
    analysis = analyze_syntax_tree(tree)
    analysis_time = time.time() - start_time

    print("Performance Results:")
    print(f"  Code lines: {len(lines)}")
    print(f"  Parse time: {parse_time:.4f}s")
    print(f"  Analysis time: {analysis_time:.4f}s")
    print(f"  Total nodes: {analysis['total_nodes']}")

    assert parse_time < 1.0  # Should parse quickly
    assert analysis_time < 1.0  # Should analyze quickly
    print("✓ Performance test passed")


if __name__ == "__main__":
    print("Running Modular Syntax System Tests")
    print("=" * 50)

    try:
        test_basic_parsing()
        test_analysis()
        test_visitor_pattern()
        test_advanced_analysis()
        test_compatibility()
        test_performance()

        print("\n" + "=" * 50)
        print("🎉 All tests passed! Modular syntax system is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
