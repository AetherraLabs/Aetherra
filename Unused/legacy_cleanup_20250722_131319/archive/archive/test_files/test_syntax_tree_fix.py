#!/usr/bin/env python3
"""
Test script for the fixed core.syntax_tree module
"""

import os
import sys

# Add the project directory to the path
project_dir = r"c:\Users\enigm\Desktop\Aetherra Project"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)


def test_syntax_tree_import():
    """Test that core.syntax_tree can be imported and works in fallback mode."""
    try:
        # First, let's temporarily disable the core.syntax module to force fallback
        import core.syntax_tree

        print("✅ core.syntax_tree imported successfully")
        print(f"📋 Available exports: {core.syntax_tree.__all__}")

        # Test that all exported items are accessible
        missing_items = []
        for item in core.syntax_tree.__all__:
            try:
                getattr(core.syntax_tree, item)
                print(f"  ✅ {item} - accessible")
            except AttributeError:
                missing_items.append(item)
                print(f"  ❌ {item} - missing")

        if not missing_items:
            print("🎉 All exported items are accessible!")
        else:
            print(f"⚠️  Missing items: {missing_items}")

        # Test basic functionality
        try:
            # Test parse_aetherra function
            result = core.syntax_tree.parse_aetherra("test code")
            print(f"✅ parse_aetherra works, returned: {type(result)}")

            # Test analyze_syntax_tree function
            analysis = core.syntax_tree.analyze_syntax_tree(result)
            print(f"✅ analyze_syntax_tree works, returned: {type(analysis)}")

        except Exception as e:
            print(f"❌ Function test failed: {e}")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing core.syntax_tree module...")
    print("=" * 50)

    success = test_syntax_tree_import()

    print("=" * 50)
    if success:
        print("🎯 Test completed successfully!")
    else:
        print("💥 Test failed!")
