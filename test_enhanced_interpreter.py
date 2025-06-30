#!/usr/bin/env python3
"""
Enhanced Interpreter Integration Test
===================================

Test the integration of the enhanced SyntaxTree parser with the main interpreter.
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.interpreter import NeuroCodeInterpreter

def test_enhanced_interpreter():
    """Test the enhanced interpreter with SyntaxTree parsing"""
    print("🔄 Testing Enhanced Interpreter Integration...")
    print("=" * 60)
    
    # Create interpreter instance
    interpreter = NeuroCodeInterpreter()
    
    # Test data
    test_scripts = [
        {
            "name": "Basic NeuroCode",
            "code": '''goal: optimize system performance priority: high
remember("system optimized") as "maintenance"
assistant: "analyze current system bottlenecks"
plugin: sysmon status''',
        },
        {
            "name": "Enhanced Memory Operations",
            "code": '''memory.search("optimization")
recall "maintenance" since "today"
memory.pattern("performance", frequency="daily")''',
        },
        {
            "name": "Function Definition",
            "code": '''define process_data(input_file, output_format)
    result = load_data(input_file)
    return format_output(result, output_format)
end''',
        },
        {
            "name": "Control Flow",
            "code": '''if system_load > 80:
    plugin: alert high_load
else:
    remember("system normal") as "monitoring"
end''',
        }
    ]
    
    # Test each script
    for i, test in enumerate(test_scripts, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print("-" * 40)
        
        # Test enhanced parsing
        if interpreter.use_enhanced_parser:
            print("🚀 Using Enhanced Parser:")
            try:
                result = interpreter.execute_enhanced(test['code'])
                print(f"   ✅ Result: {result}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print("⚠️  Enhanced parser not available")
        
        # Test standard parsing for comparison
        print("\n🔄 Standard Parser Comparison:")
        try:
            # Test line by line for standard parser
            lines = test['code'].strip().split('\n')
            for line in lines:
                if line.strip():
                    result = interpreter.execute(line.strip())
                    if result:
                        print(f"   📤 {line.strip()} → {result}")
        except Exception as e:
            print(f"   ❌ Standard parser error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced interpreter integration test completed!")
    
    # Test syntax tree analysis
    print("\n📊 Syntax Tree Analysis:")
    if interpreter.use_enhanced_parser:
        from core.syntax_tree import parse_neurocode, analyze_syntax_tree
        
        sample_code = '''goal: test parsing priority: medium
remember("test data") as "testing"
assistant: "help with analysis"'''
        
        try:
            tree = parse_neurocode(sample_code)
            stats = analyze_syntax_tree(tree)
            print(f"   📈 Tree Statistics: {stats}")
        except Exception as e:
            print(f"   ❌ Tree analysis error: {e}")
    
    return True

if __name__ == "__main__":
    test_enhanced_interpreter()
