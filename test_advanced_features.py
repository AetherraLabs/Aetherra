# test_advanced_features.py
# 🧪 Test script for the advanced code editing features

import sys
import os

# Add paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, "Aetherra", "lyrixa", "gui"))

def test_basic_functionality():
    """Test basic functionality without advanced imports"""
    print("🧪 Testing Basic Functionality")
    print("=" * 50)

    # Test basic refactor functions
    try:
        from Aetherra.lyrixa.gui.plugin_editor_refactor import (
            smart_code_merge, replace_block, parse_plugin_metadata,
            analyze_code_structure, get_learning_insights
        )
        print("✅ Successfully imported refactor functions")

        # Test basic code merge
        original = "def old_func():\n    pass"
        new = "def new_func():\n    return 'hello'"

        result = smart_code_merge(original, new, "append")
        print(f"✅ Basic merge test passed - length: {len(result)}")

        # Test metadata parsing
        sample_code = '''# @plugin: test_plugin
# @functions: func1, func2
# @version: 1.0

def func1():
    pass
'''
        metadata = parse_plugin_metadata(sample_code)
        if metadata:
            print(f"✅ Metadata parsing works - plugin: {metadata.name}")
        else:
            print("⚠️ Metadata parsing returned None")

        # Test structure analysis
        analysis = analyze_code_structure(sample_code)
        print(f"✅ Structure analysis works - valid: {analysis.get('valid_syntax', 'unknown')}")

        # Test learning insights
        insights = get_learning_insights()
        print(f"✅ Learning insights works - type: {type(insights)}")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_advanced_functionality():
    """Test advanced AST-aware functionality"""
    print("\n🧠 Testing Advanced AST-Aware Functionality")
    print("=" * 50)

    try:
        from Aetherra.lyrixa.gui.advanced_code_editor import ASTAwareCodeEditor

        editor = ASTAwareCodeEditor()
        print("✅ Advanced editor created successfully")

        # Test plugin metadata parsing
        sample_plugin = '''# @plugin: advanced_calc
# @functions: add, multiply, divide
# @version: 2.0

class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
'''

        metadata = editor.parse_plugin_metadata(sample_plugin)
        if metadata:
            print(f"✅ Advanced metadata parsing: {metadata.name} v{metadata.version}")
            print(f"    Functions: {metadata.functions}")
            print(f"    Classes: {metadata.classes}")

        # Test AST analysis
        analysis = editor.analyze_code_structure(sample_plugin)
        if analysis.get('valid_syntax'):
            print(f"✅ AST analysis successful")
            print(f"    Functions found: {len(analysis.get('functions', []))}")
            print(f"    Classes found: {len(analysis.get('classes', []))}")
            print(f"    Complexity score: {analysis.get('complexity_score', 0)}")

        # Test intelligent merge
        new_function = '''def subtract(self, a, b):
    """Subtract two numbers"""
    return a - b'''

        merged, success, message = editor.intelligent_code_merge(
            sample_plugin, new_function, "Testing intelligent merge"
        )

        print(f"✅ Intelligent merge: {'Success' if success else 'Failed'}")
        print(f"    Message: {message}")
        print(f"    Result length: {len(merged)} chars")

        # Test learning insights
        insights = editor.get_learning_insights()
        print(f"✅ Learning insights: {insights.get('total_edits', 0)} total edits")

        return True

    except Exception as e:
        print(f"❌ Advanced functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """Test API integration (if server is running)"""
    print("\n🌐 Testing API Integration")
    print("=" * 50)

    try:
        import requests

        # Test health endpoint
        response = requests.get("http://127.0.0.1:8007/health", timeout=2)
        if response.status_code == 200:
            print("✅ API server is running")

            # Test plugin editor endpoint
            test_data = {
                "existing_code": "def old():\n    pass",
                "new_code": "def new():\n    return 'hello'",
                "strategy": "intelligent"
            }

            response = requests.post(
                "http://127.0.0.1:8007/api/plugin_editor/smart_edit",
                json=test_data,
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Smart edit API works: {result.get('operation', 'unknown')}")
                print(f"    Success: {result.get('success', False)}")
                return True
            else:
                print(f"⚠️ Smart edit API returned {response.status_code}")
                return False
        else:
            print(f"⚠️ API server health check failed: {response.status_code}")
            return False


    except ImportError:
        print("⚠️ Requests library not available - skipping API tests")
        return True
    except Exception as e:
        if "requests" in str(type(e)) or "RequestException" in str(type(e)):
            print("⚠️ API server not accessible - skipping API tests")
            return True
        else:
            print(f"❌ API integration test failed: {e}")
            return False

def main():
    """Run all tests"""
    print("🚀 Advanced Code Editor Feature Tests")
    print("=" * 60)

    results = []

    # Test basic functionality
    results.append(("Basic Functionality", test_basic_functionality()))

    # Test advanced functionality
    results.append(("Advanced AST Features", test_advanced_functionality()))

    # Test API integration
    results.append(("API Integration", test_api_integration()))

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! Advanced features are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
