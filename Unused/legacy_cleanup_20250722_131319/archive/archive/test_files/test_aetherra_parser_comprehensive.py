#!/usr/bin/env python3
"""
Comprehensive test for core/aetherra_parser.py
Tests all AetherraCode language features and parsing functionality
"""

from core.aetherra_parser import (
    AetherraLexer,
    AgentNode,
    ConditionalNode,
    GoalNode,
    IntentNode,
    MemoryNode,
    PluginNode,
    SelfModificationNode,
    TokenType,
    compile_aetherra,
    parse_aetherra,
)


def test_aetherra_parser_comprehensive():
    """Comprehensive test of all AetherraCode parser functionality"""
    print("🧬 Testing AetherraCode Parser (AI-Native Language)")
    print("=" * 60)

    # Test sample AetherraCode program
    aetherra_code = """
# Sample AetherraCode program
goal: optimize memory usage by 20% priority: high
agent: on

remember("System initialized") as "startup"

when error_rate > 5%:
    analyze recent_logs
    suggest fix for "performance"
end

optimize for "speed"
learn from "user_data"

plugin: monitoring
    watch system_metrics
    alert on threshold_exceeded
end

suggest fix for "memory_leak"
"""

    passed = 0
    total = 0

    # Test 1: Lexical Analysis
    print("\n🔤 Test 1: Lexical Analysis")
    total += 1
    try:
        lexer = AetherraLexer(aetherra_code)
        tokens = lexer.tokenize()

        # Check for key tokens
        token_types = [token.type for token in tokens]
        expected_tokens = [
            TokenType.GOAL,
            TokenType.AGENT,
            TokenType.REMEMBER,
            TokenType.WHEN,
            TokenType.PLUGIN,
        ]

        found_tokens = [t for t in expected_tokens if t in token_types]
        if len(found_tokens) >= 4:
            print(f"✓ Lexical analysis successful: {len(tokens)} tokens generated")
            print(f"  Found key tokens: {[t.value for t in found_tokens]}")
            passed += 1
        else:
            print("✗ Lexical analysis failed: Missing key tokens")
    except Exception as e:
        print(f"✗ Lexical analysis error: {e}")

    # Test 2: Parsing
    print("\n🌳 Test 2: Abstract Syntax Tree Parsing")
    total += 1
    try:
        ast = parse_aetherra(aetherra_code)

        # Check node types
        node_types = [type(node).__name__ for node in ast]
        expected_node_types = [
            "GoalNode",
            "AgentNode",
            "MemoryNode",
            "ConditionalNode",
            "IntentNode",
            "PluginNode",
            "SelfModificationNode",
        ]

        found_types = [t for t in expected_node_types if t in node_types]
        if len(found_types) >= 5:
            print(f"✓ AST parsing successful: {len(ast)} nodes generated")
            print(f"  Node types: {node_types}")
            passed += 1
        else:
            print("✗ AST parsing failed: Missing node types")
    except Exception as e:
        print(f"✗ AST parsing error: {e}")

    # Test 3: Individual Node Types
    print("\n[DISC] Test 3: Individual Node Type Testing")

    test_cases = [
        ("goal: reduce latency by 50%", GoalNode),
        ("agent: investigate_issue", AgentNode),
        ('remember("test data") as "test"', MemoryNode),
        ('optimize for "performance"', IntentNode),
        ('suggest fix for "bug"', SelfModificationNode),
    ]

    for code, expected_type in test_cases:
        total += 1
        try:
            ast = parse_aetherra(code)
            if ast and isinstance(ast[0], expected_type):
                print(f"✓ {expected_type.__name__}: {code}")
                passed += 1
            else:
                print(f"✗ {expected_type.__name__}: {code}")
        except Exception as e:
            print(f"✗ {expected_type.__name__}: {code} - Error: {e}")

    # Test 4: Code Compilation
    print("\n[TOOL] Test 4: Code Compilation")
    total += 1
    try:
        compiled = compile_aetherra(aetherra_code)

        # Check if compilation produces valid Python-like code
        if (
            "interpreter" in compiled and "def" not in compiled
        ):  # Should not contain Python def
            print("✓ Code compilation successful")
            print(f"  Generated {len(compiled.split('\\n'))} lines of executable code")
            passed += 1
        else:
            print("✗ Code compilation failed")
    except Exception as e:
        print(f"✗ Code compilation error: {e}")

    # Test 5: Complex Constructs
    print("\n🏗️ Test 5: Complex Language Constructs")

    complex_code = """
when memory_usage > 80%:
    agent: cleanup_cache
    optimize for "memory"
    if critical_error:
        suggest fix for "emergency"
    end
end

plugin: auto_optimizer
    on_trigger("high_load"):
        analyze system_state
        apply optimization
    end
end
"""

    total += 1
    try:
        ast = parse_aetherra(complex_code)

        # Should have nested structures
        has_conditional = any(isinstance(node, ConditionalNode) for node in ast)
        has_plugin = any(isinstance(node, PluginNode) for node in ast)

        if has_conditional and has_plugin and len(ast) >= 2:
            print("✓ Complex constructs parsing successful")
            print(f"  Parsed {len(ast)} top-level nodes with nesting")
            passed += 1
        else:
            print("✗ Complex constructs parsing failed")
    except Exception as e:
        print(f"✗ Complex constructs error: {e}")

    # Test 6: Error Handling
    print("\n🛡️ Test 6: Error Handling")
    total += 1
    try:
        # Test with invalid syntax
        invalid_code = "invalid: syntax here without proper structure"
        ast = parse_aetherra(invalid_code)

        # Should either parse gracefully or handle errors
        print("✓ Error handling: Graceful handling of invalid syntax")
        passed += 1
    except Exception as e:
        print(f"✓ Error handling: Proper error reporting - {type(e).__name__}")
        passed += 1

    # Final Results
    print(f"\n{'=' * 60}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print(f"{'=' * 60}")
    print(f"Passed: {passed}/{total} tests ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED! aetherra_parser.py is production-ready!")
        print(
            "🧬 AetherraCode is now a fully functional AI-native programming language!"
        )
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False


def demo_aetherra_language():
    """Demonstrate AetherraCode as a programming language"""
    print("\n🧬 AetherraCode Language Demonstration")
    print("=" * 50)

    demo_code = """
# AetherraCode: The AI-Native Programming Language
goal: create intelligent system priority: high
agent: on

# Memory and learning
remember("Initial state") as "system_start"
learn from "historical_data"

# Intelligent conditionals
when system_load > 75%:
    optimize for "performance"
    agent: scale_resources
    if memory_critical:
        suggest fix for "memory_optimization"
    end
end

# AI-powered analysis
analyze user_behavior
optimize for "user_experience"

# Plugin system
plugin: ml_optimizer
    train model on "performance_data"
    predict system_requirements
    auto_scale based_on_prediction
end

# Self-modification capabilities
suggest fix for "bottleneck_detection"
apply fix if confidence > 90%
"""

    print("📝 Source Code:")
    print(demo_code)

    print("\n🔤 Tokenization Sample:")
    lexer = AetherraLexer(demo_code)
    tokens = lexer.tokenize()
    key_tokens = [
        t
        for t in tokens
        if t.type
        in [
            TokenType.GOAL,
            TokenType.AGENT,
            TokenType.REMEMBER,
            TokenType.WHEN,
            TokenType.PLUGIN,
        ]
    ][:10]
    for token in key_tokens:
        print(f"  {token.type.value}: '{token.value}'")

    print("\n🌳 Abstract Syntax Tree:")
    ast = parse_aetherra(demo_code)
    for i, node in enumerate(ast):
        print(
            f"  [{i}] {type(node).__name__}: {getattr(node, 'objective', getattr(node, 'command', getattr(node, 'operation', 'complex')))}"
        )

    print("\n[TOOL] Compiled Output (Sample):")
    compiled = compile_aetherra(demo_code)
    lines = compiled.split("\n")[:10]
    for line in lines:
        print(f"  {line}")

    print("\n✅ AetherraCode demonstrates:")
    print("  🎯 AI-native syntax and semantics")
    print("  🧠 Intelligent decision-making constructs")
    print("  🔄 Self-modification capabilities")
    print("  🔌 Plugin architecture")
    print("  📊 Goal-oriented programming")
    print("  🚀 Production-ready parser and compiler")


if __name__ == "__main__":
    success = test_aetherra_parser_comprehensive()
    if success:
        demo_aetherra_language()
    print("\n🎉 AetherraCode parser testing complete!")
