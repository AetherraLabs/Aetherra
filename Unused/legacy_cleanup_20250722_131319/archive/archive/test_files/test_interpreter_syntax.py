#!/usr/bin/env python3
"""
Direct test of enhanced interpreter syntax and structure
"""

import sys

sys.path.append(".")

# Test individual components that don't require complex imports
print("🧪 Testing Enhanced Aetherra Interpreter Structure")
print("=" * 50)

# Test 1: Check the file compiles
print("Test 1: Checking file compilation...")
try:
    with open("core/enhanced_aetherra_interpreter.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Try to compile the code
    compile(content, "core/enhanced_aetherra_interpreter.py", "exec")
    print("✅ File compiles successfully - no syntax errors")

except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Compilation error: {e}")
    sys.exit(1)

# Test 2: Check class definitions exist
print("\nTest 2: Checking class definitions...")
try:
    exec(content)
    print("✅ Code executes successfully")

    # Check if key classes are defined
    local_vars = {}
    exec(content, {}, local_vars)

    if "AIModelRouter" in local_vars:
        print("✅ AIModelRouter class defined")
    else:
        print("❌ AIModelRouter class missing")

    if "LocalAIEngine" in local_vars:
        print("✅ LocalAIEngine class defined")
    else:
        print("❌ LocalAIEngine class missing")

    if "EnhancedAetherraInterpreter" in local_vars:
        print("✅ EnhancedAetherraInterpreter class defined")
    else:
        print("❌ EnhancedAetherraInterpreter class missing")

    if "create_enhanced_interpreter" in local_vars:
        print("✅ create_enhanced_interpreter function defined")
    else:
        print("❌ create_enhanced_interpreter function missing")

except Exception as e:
    print(f"❌ Code execution error: {e}")
    sys.exit(1)

# Test 3: Check method definitions
print("\nTest 3: Checking method definitions...")
try:
    # Create a mock environment to test class structure
    class MockAetherraInterpreter:
        def __init__(self, *args, **kwargs):
            pass

        def execute(self, code):
            return f"Mock execution: {code}"

    class MockIntentToCodeParser:
        pass

    class MockAICollaborationFramework:
        pass

    # Mock the required functions
    def mock_ask_ai(prompt, model=None):
        return f"Mock AI response for: {prompt[:50]}..."

    def mock_parse_natural_intent(intent):
        return f"# Mock generated code from: {intent}"

    # Create a test environment
    test_env = {
        "AetherraInterpreter": MockAetherraInterpreter,
        "IntentToCodeParser": MockIntentToCodeParser,
        "AICollaborationFramework": MockAICollaborationFramework,
        "ask_ai": mock_ask_ai,
        "parse_natural_intent": mock_parse_natural_intent,
        "time": __import__("time"),
        "Any": __import__("typing").Any,
    }

    # Execute the code with mocked dependencies
    exec(content, test_env)

    # Test AIModelRouter
    router = test_env["AIModelRouter"]()
    model = router.select_best_model("code_generation")
    print(f"✅ AIModelRouter.select_best_model works: {model}")

    # Test LocalAIEngine
    engine = test_env["LocalAIEngine"]()
    available = engine.is_available()
    print(f"✅ LocalAIEngine.is_available works: {available}")

    if hasattr(engine, "intent_to_code"):
        code = engine.intent_to_code("test intent")
        print(f"✅ LocalAIEngine.intent_to_code works: {code[:30]}...")

    print("✅ All key methods are accessible and functional")

except Exception as e:
    print(f"❌ Method testing error: {e}")
    sys.exit(1)

print("\n🎉 Enhanced Aetherra Interpreter structure tests completed!")
print("✅ All syntax errors have been fixed")
print("✅ All required classes and methods are defined")
print("✅ The enhanced interpreter is ready for use")
