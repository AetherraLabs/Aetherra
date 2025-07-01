#!/usr/bin/env python3
"""
Test suite for NeuroCode Modern Parser
=====================================

This module tests the new Lark-based parser against the existing regex parser
to ensure compatibility and improved functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from core.modern_parser import NeuroCodeModernParser, ASTNodeType
    from core.syntax_tree import NeuroCodeParser, NodeType
    MODERN_PARSER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modern parser: {e}")
    MODERN_PARSER_AVAILABLE = False


def test_basic_syntax():
    """Test basic NeuroCode syntax parsing"""
    test_code = '''
goal: "test basic parsing" priority: high

identity {
    name: "TestBot"
    version: "1.0"
}

remember("test memory")
agent.mode = "interactive"
agent.start()

think about "parsing capabilities"
'''
    
    if MODERN_PARSER_AVAILABLE:
        print("🧠 Testing Modern Parser...")
        try:
            modern_parser = NeuroCodeModernParser()
            modern_ast = modern_parser.parse(test_code)
            print(f"✅ Modern parser succeeded")
            print(f"   AST type: {modern_ast.type}")
            print(f"   Children: {len(modern_ast.children)}")
        except Exception as e:
            print(f"❌ Modern parser failed: {e}")
    
    print("\n🏛️ Testing Legacy Parser...")
    try:
        legacy_parser = NeuroCodeParser()
        legacy_ast = legacy_parser.parse(test_code)
        print(f"✅ Legacy parser succeeded")
        print(f"   AST type: {legacy_ast.type}")
        print(f"   Children: {len(legacy_ast.children or [])}")
    except Exception as e:
        print(f"❌ Legacy parser failed: {e}")


def test_complex_syntax():
    """Test complex NeuroCode constructs"""
    test_code = '''
goal: "complex parsing test" priority: critical deadline: "2024-12-31"

identity {
    name: "ComplexTestBot"
    personality: {
        analytical: 0.9
        creative: 0.7
    }
}

define process_data(input_data):
    analyze input_data
    optimize results
end

agent.add_goal("process user requests", priority="high")
memory.search("relevant patterns")

think about "advanced language features"
'''
    
    if MODERN_PARSER_AVAILABLE:
        print("\n🧠 Testing Modern Parser (Complex)...")
        try:
            modern_parser = NeuroCodeModernParser()
            modern_ast = modern_parser.parse(test_code)
            print(f"✅ Modern parser handled complex syntax")
            print(f"   Statements parsed: {len(modern_ast.children)}")
        except Exception as e:
            print(f"❌ Modern parser failed on complex syntax: {e}")


def test_error_handling():
    """Test parser error handling"""
    invalid_code = '''
goal: "test error handling
identity {
    name: "ErrorBot"
    # Missing closing brace
'''
    
    if MODERN_PARSER_AVAILABLE:
        print("\n🧠 Testing Modern Parser Error Handling...")
        try:
            modern_parser = NeuroCodeModernParser()
            errors = modern_parser.get_syntax_errors(invalid_code)
            if errors:
                print(f"✅ Modern parser detected errors: {len(errors)}")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"   - {error}")
            else:
                print("❌ Modern parser should have detected errors")
        except Exception as e:
            print(f"⚠️ Error in error handling test: {e}")


def test_performance():
    """Basic performance comparison"""
    large_code = '''
goal: "performance test" priority: high
identity { name: "PerfBot" }
''' + '\n'.join([f'remember("test data {i}")' for i in range(100)])
    
    import time
    
    if MODERN_PARSER_AVAILABLE:
        print("\n⚡ Performance Test...")
        
        # Test modern parser
        start_time = time.time()
        try:
            modern_parser = NeuroCodeModernParser()
            modern_ast = modern_parser.parse(large_code)
            modern_time = time.time() - start_time
            print(f"🧠 Modern parser: {modern_time:.4f}s")
        except Exception as e:
            print(f"❌ Modern parser failed: {e}")
            modern_time = float('inf')
        
        # Test legacy parser
        start_time = time.time()
        try:
            legacy_parser = NeuroCodeParser()
            legacy_ast = legacy_parser.parse(large_code)
            legacy_time = time.time() - start_time
            print(f"🏛️ Legacy parser: {legacy_time:.4f}s")
        except Exception as e:
            print(f"❌ Legacy parser failed: {e}")
            legacy_time = float('inf')
        
        if modern_time != float('inf') and legacy_time != float('inf'):
            ratio = modern_time / legacy_time
            if ratio < 1.5:
                print(f"✅ Performance acceptable (ratio: {ratio:.2f})")
            else:
                print(f"⚠️ Performance regression (ratio: {ratio:.2f})")


def test_grammar_features():
    """Test specific grammar features"""
    if not MODERN_PARSER_AVAILABLE:
        print("⏭️ Skipping grammar tests - modern parser not available")
        return
        
    print("\n🎯 Testing Grammar Features...")
    
    # Test agent syntax
    agent_code = '''
agent.mode = "autonomous"
agent.start()
agent.add_goal("test goal", priority="high")
agent.status()
'''
    
    try:
        parser = NeuroCodeModernParser()
        ast = parser.parse(agent_code)
        print("✅ Agent syntax parsing")
    except Exception as e:
        print(f"❌ Agent syntax failed: {e}")
    
    # Test memory operations
    memory_code = '''
remember("important data") as "key_info"
recall "key_info"
memory.search("patterns")
'''
    
    try:
        ast = parser.parse(memory_code)
        print("✅ Memory operations parsing")
    except Exception as e:
        print(f"❌ Memory operations failed: {e}")
    
    # Test intent actions
    intent_code = '''
think about "complex problems"
analyze system.performance
optimize resource.usage
'''
    
    try:
        ast = parser.parse(intent_code)
        print("✅ Intent actions parsing")
    except Exception as e:
        print(f"❌ Intent actions failed: {e}")


def main():
    """Run all parser tests"""
    print("🧬 NeuroCode Parser Test Suite")
    print("=" * 40)
    
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print(f"Modern parser available: {MODERN_PARSER_AVAILABLE}")
    
    if MODERN_PARSER_AVAILABLE:
        try:
            import lark
            print(f"Lark version: {lark.__version__}")
        except ImportError:
            print("Lark not available")
    
    print("\n" + "=" * 40)
    
    # Run tests
    test_basic_syntax()
    test_complex_syntax()
    test_error_handling()
    test_performance()
    test_grammar_features()
    
    print("\n" + "=" * 40)
    print("🎉 Parser tests completed!")
    
    if MODERN_PARSER_AVAILABLE:
        print("\n📋 Next Steps:")
        print("1. Review parser output and AST structure")
        print("2. Add more comprehensive test cases")
        print("3. Integrate modern parser into main codebase")
        print("4. Update documentation and examples")
    else:
        print("\n⚠️ Modern parser not available. Install requirements:")
        print("   pip install -r requirements.txt")


if __name__ == "__main__":
    main()
