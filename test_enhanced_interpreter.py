#!/usr/bin/env python3
"""
Test the enhanced interpreter with SyntaxTree integration
"""

import sys
from pathlib import Path

# Add core directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "core"))

try:
    from interpreter import NeuroCodeInterpreter
    
    def test_enhanced_interpreter():
        print("🔄 Testing Enhanced NeuroCode Interpreter with SyntaxTree Integration")
        print("=" * 70)
        
        # Create interpreter instance
        interpreter = NeuroCodeInterpreter()
        
        # Test various NeuroCode constructs
        test_commands = [
            'goal: "optimize system performance" priority: high',
            'remember("system optimized") as "maintenance"',
            'assistant: "analyze current system bottlenecks"',
            'plugin: sysmon status',
            'recall "maintenance"'
        ]
        
        print("📝 Testing NeuroCode commands:")
        for i, cmd in enumerate(test_commands, 1):
            print(f"\n{i}. Command: {cmd}")
            try:
                result = interpreter.execute(cmd)
                print(f"   ✅ Result: {result}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n🎯 Enhanced interpreter test completed!")
        
        # Test syntax tree parsing specifically
        if interpreter.syntax_parser:
            print("\n📊 Testing SyntaxTree Parser Integration:")
            test_line = 'goal: "test parsing" priority: high'
            try:
                result = interpreter._try_syntax_tree_parsing(test_line)
                if result:
                    print(f"   ✅ SyntaxTree parsed: {result}")
                else:
                    print("   ℹ️ SyntaxTree parsing fell back to standard parsing")
            except Exception as e:
                print(f"   ❌ SyntaxTree error: {e}")
        else:
            print("   ⚠️ SyntaxTree parser not available")
    
    if __name__ == "__main__":
        test_enhanced_interpreter()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all core modules are available")
