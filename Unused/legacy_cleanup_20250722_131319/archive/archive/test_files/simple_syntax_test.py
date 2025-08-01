# simple_syntax_test.py
"""
Simple test for the aetherra syntax tree parser
"""

from core.syntax_tree import SyntaxTreeVisitor, analyze_syntax_tree, parse_aetherra


def test_simple_parsing():
    """Test simple aetherra parsing"""

    code = """goal: optimize system performance priority: high
remember("system optimized") as "maintenance"
assistant: "analyze current system bottlenecks"
plugin: sysmon status"""

    print("🔄 Parsing simple aetherra...")
    tree = parse_aetherra(code)

    print("📊 Analyzing syntax tree...")
    stats = analyze_syntax_tree(tree)

    print("✅ Parsed successfully!")
    print(f"📈 Statistics: {stats}")

    print("🌳 Visiting syntax tree...")
    visitor = SyntaxTreeVisitor()
    results = visitor.visit(tree)

    print("📝 Tree structure:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result}")

    return tree, stats


if __name__ == "__main__":
    print("🧬 Simple aetherra Syntax Tree Test")
    print("=" * 40)

    try:
        tree, stats = test_simple_parsing()
        print("\n✅ Simple test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
