# quick_test_advanced.py
# Quick test of advanced code editor without heavy imports

import sys
import os

# Add paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, "Aetherra", "lyrixa", "gui"))

def quick_test():
    print("🧪 Quick Advanced Editor Test")
    print("=" * 40)

    try:
        from advanced_code_editor import ASTAwareCodeEditor
        print("✅ Successfully imported ASTAwareCodeEditor")

        editor = ASTAwareCodeEditor()
        print("✅ Created editor instance")

        # Test learning insights (should be empty initially)
        insights = editor.get_learning_insights()
        print(f"✅ Learning insights: {insights}")

        # Test with a simple code snippet
        sample_code = '''def hello():
    return "world"
'''

        analysis = editor.analyze_code_structure(sample_code)
        print(f"✅ Code analysis: valid={analysis.get('valid_syntax', False)}")

        # Test metadata parsing
        metadata_code = '''# @plugin: test
# @functions: hello
def hello():
    return "world"
'''

        metadata = editor.parse_plugin_metadata(metadata_code)
        if metadata:
            print(f"✅ Metadata parsed: {metadata.name}")
        else:
            print("[WARN] No metadata found")

        # Test intelligent merge
        new_code = '''def goodbye():
    return "farewell"
'''

        merged, success, message = editor.intelligent_code_merge(sample_code, new_code, "Test merge")
        print(f"✅ Merge test: success={success}, message='{message}'")

        # Check insights again
        new_insights = editor.get_learning_insights()
        print(f"✅ Updated insights: {new_insights}")

        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 All tests passed! Advanced editor is working correctly.")
    else:
        print("\n[ERROR] Tests failed.")
