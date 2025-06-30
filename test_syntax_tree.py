# test_syntax_tree.py
"""
Test script for the enhanced NeuroCode syntax tree parser
"""

from core.syntax_tree import SyntaxTreeVisitor, analyze_syntax_tree, parse_neurocode


def test_basic_parsing():
    """Test basic NeuroCode parsing"""

    code = """
# This is a test NeuroCode program
goal: optimize system performance priority: high

# Memory operations
remember("system optimized") as "maintenance"
recall "performance_data"

# Assistant interaction
assistant: "analyze current system bottlenecks"

# Plugin usage
plugin: sysmon status

# Function definition with multi-line block
define optimize_network()
    x = "network_config"
    for component in ["cpu", "memory", "disk"]
        if component == "memory"
            assistant: "optimize memory usage"
        end
    end
    remember("network optimized") as "network"
end

# Function call
run optimize_network()

# Variable assignment
threshold = 85
"""

    # Parse the code
    print("🔄 Parsing NeuroCode...")
    tree = parse_neurocode(code)

    # Analyze the tree
    print("📊 Analyzing syntax tree...")
    stats = analyze_syntax_tree(tree)

    print("✅ Parsed successfully!")
    print("📈 Statistics:")
    print(f"   Total nodes: {stats['total_nodes']}")
    print(f"   Max depth: {stats['max_depth']}")
    print(f"   Total lines: {stats['total_lines']}")
    print(f"   Node types: {stats['node_counts']}")

    # Visit the tree
    print("\n🌳 Visiting syntax tree...")
    visitor = SyntaxTreeVisitor()
    results = visitor.visit(tree)

    print("📝 Tree structure:")
    for i, result in enumerate(results[:10], 1):  # Show first 10 results
        print(f"   {i}. {result}")

    if len(results) > 10:
        print(f"   ... and {len(results) - 10} more nodes")

    return tree, stats


def test_function_definition():
    """Test function definition parsing"""

    code = """
define process_data(input_file, output_format)
    load_data = input_file
    if output_format == "json"
        assistant: "convert data to JSON format"
    else
        assistant: "convert data to standard format"
    end
    remember("data processed") as "processing"
end
"""

    print("\n🔄 Testing function definition...")
    tree = parse_neurocode(code)
    visitor = SyntaxTreeVisitor()
    results = visitor.visit(tree)

    print("📝 Function definition structure:")
    for result in results:
        print(f"   {result}")

    return tree


def test_nested_blocks():
    """Test nested block parsing"""

    code = """
for item in data_list
    if item.status == "active"
        for subitem in item.children
            assistant: "process subitem data"
            remember("subitem processed") as "nested_processing"
        end
    else
        assistant: "skip inactive item"
    end
end
"""

    print("\n🔄 Testing nested blocks...")
    tree = parse_neurocode(code)
    stats = analyze_syntax_tree(tree)

    print("📈 Nested structure stats:")
    print(f"   Max depth: {stats['max_depth']}")
    print(f"   Total nodes: {stats['total_nodes']}")

    return tree


def test_enhanced_memory_operations():
    """Test enhanced memory operations parsing"""
    print("🔄 Testing enhanced memory operations...")
    
    enhanced_memory_code = '''memory.search("optimization")
recall "maintenance" since "today" in category "system"
memory.pattern("performance", frequency="daily")'''
    
    tree = parse_neurocode(enhanced_memory_code)
    visitor = SyntaxTreeVisitor()
    
    print("📝 Enhanced memory operations:")
    results = visitor.visit(tree)
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result}")
    
    stats = analyze_syntax_tree(tree)
    print(f"📊 Enhanced memory stats: {stats['node_counts']}")
    
    print("✅ Enhanced memory operations test passed!")
    return tree


if __name__ == "__main__":
    print("🧬 NeuroCode Syntax Tree Parser Test")
    print("=" * 50)

    try:
        # Test basic parsing
        tree1, stats1 = test_basic_parsing()

        # Test function definitions
        tree2 = test_function_definition()

        # Test nested blocks
        tree3 = test_nested_blocks()

        # Test enhanced memory operations
        test_enhanced_memory_operations()

        print("\n✅ All tests completed successfully!")
        print("🎯 Enhanced parsing architecture is operational")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
