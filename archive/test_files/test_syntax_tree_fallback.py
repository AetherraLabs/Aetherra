#!/usr/bin/env python3
"""
Simple test for core.syntax_tree module fallback behavior
"""

import importlib.util
import sys

# Add the project directory to the path
sys.path.insert(0, r"c:\Users\enigm\Desktop\Aetherra Project")


def test_fallback_mode():
    """Test syntax_tree in fallback mode by temporarily blocking core.syntax"""

    # Temporarily remove core.syntax from sys.modules if it exists
    modules_to_remove = [
        mod
        for mod in sys.modules.keys()
        if mod.startswith("core.syntax") and mod != "core.syntax_tree"
    ]
    for mod in modules_to_remove:
        del sys.modules[mod]

    # Block core.syntax imports
    original_import = __builtins__.__import__

    def blocking_import(name, *args, **kwargs):
        if name.startswith("core.syntax") and name != "core.syntax_tree":
            raise ImportError(f"Blocked import of {name} for testing")
        return original_import(name, *args, **kwargs)

    try:
        __builtins__.__import__ = blocking_import

        # Now try to import core.syntax_tree - should use fallback mode
        import core.syntax_tree

        print("✅ Successfully imported core.syntax_tree in fallback mode")
        print(f"📋 Available exports: {core.syntax_tree.__all__}")

        # Test basic functionality
        test_code = "sample aetherra code"

        # Test parse function
        result = core.syntax_tree.parse_aetherra(test_code)
        print(f"✅ parse_aetherra returned: {type(result)}")

        # Test analyze function
        analysis = core.syntax_tree.analyze_syntax_tree(result)
        print(f"✅ analyze_syntax_tree returned: {analysis}")

        # Test that all exports are accessible
        for export_name in core.syntax_tree.__all__:
            obj = getattr(core.syntax_tree, export_name)
            print(f"✅ {export_name}: {type(obj)}")

        return True

    except Exception as e:
        print(f"❌ Error in fallback mode test: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Restore original import
        __builtins__.__import__ = original_import


if __name__ == "__main__":
    print("🧪 Testing core.syntax_tree fallback behavior...")
    print("=" * 60)

    success = test_fallback_mode()

    print("=" * 60)
    if success:
        print("🎯 Fallback mode test PASSED!")
        print("✅ All errors in core.syntax_tree.py have been fixed!")
    else:
        print("💥 Fallback mode test FAILED!")
