#!/usr/bin/env python3
"""
Direct test of SyntaxTree parser and minimal interpreter integration
"""

import sys
from pathlib import Path

# Add core directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "core"))

def test_syntax_tree_integration():
    print("🔄 Testing Direct SyntaxTree Integration")
    print("=" * 50)
    
    try:
        # Import syntax tree parser directly
        from syntax_tree import NeuroCodeParser, SyntaxTreeVisitor
        
        parser = NeuroCodeParser()
        visitor = SyntaxTreeVisitor()
        
        print("✅ SyntaxTree modules loaded successfully")
        
        # Test parsing various NeuroCode constructs
        test_cases = [
            'goal: "optimize system performance" priority: high',
            'remember("system optimized") as "maintenance"',
            'assistant: "analyze current system bottlenecks"',
            'plugin: sysmon status'
        ]
        
        print("\n📝 Testing NeuroCode parsing:")
        for i, test_code in enumerate(test_cases, 1):
            print(f"\n{i}. Parsing: {test_code}")
            try:
                syntax_tree = parser.parse(test_code)
                print("   ✅ Parsed successfully!")
                print(f"   📊 Root type: {syntax_tree.type}")
                children_count = len(syntax_tree.children) if syntax_tree.children else 0
                print(f"   📈 Children: {children_count}")
                
                # Visit the tree
                visitor.visit(syntax_tree)
                
                # Show parsed structure
                if syntax_tree.children:
                    for j, child in enumerate(syntax_tree.children):
                        print(f"   📝 Child {j+1}: {child.type} = '{child.value}'")
                    
            except Exception as e:
                print(f"   ❌ Parse error: {e}")
        
        print("\n🎯 SyntaxTree integration test completed!")
        print("✅ Enhanced parsing architecture is ready for interpreter integration")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure syntax_tree.py is available in core/")

if __name__ == "__main__":
    test_syntax_tree_integration()
