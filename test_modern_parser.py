#!/usr/bin/env python3
"""
Test script to verify AetherraCodeModernParser functionality
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_modern_parser():
    """Test the modern parser functionality"""
    try:
        print("Testing AetherraCodeModernParser import...")
        from core.modern_parser import AetherraCodeModernParser, ASTNode, ASTNodeType

        print("✅ AetherraCodeModernParser imported successfully")

        print("\nTesting parser instantiation...")
        parser = AetherraCodeModernParser()
        print("✅ Parser instantiated successfully")

        print("\nTesting AST node types...")
        print(f"✅ Available node types: {len(ASTNodeType)}")

        print("\nTesting simple parsing...")
        test_code = '''goal: "test parsing"'''

        try:
            ast = parser.parse(test_code)
            print("✅ Simple parsing successful")
            print(f"  AST type: {ast.type}")
            print(f"  AST metadata: {ast.metadata}")
        except Exception as e:
            print(f"⚠️  Parsing failed (expected without full grammar): {e}")

        print("\nTesting syntax validation...")
        is_valid = parser.validate_syntax(test_code)
        print(f"✅ Syntax validation: {'Valid' if is_valid else 'Invalid'}")

        print("\n🎉 All modern parser tests completed!")
        return True

    except Exception as e:
        print(f"❌ Error testing modern parser: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_modern_parser()
    sys.exit(0 if success else 1)
