#!/usr/bin/env python3
"""
Test script to verify core interpreter functionality
"""

def test_interpreter():
    try:
        from Aetherra.core.interpreter import AetherraInterpreter
        interpreter = AetherraInterpreter()

        # Test basic memory functionality
        result = interpreter.execute('remember("test memory") as "test"')
        print(f"Memory test: {result}")

        # Test recall functionality
        result = interpreter.execute('recall tag: "test"')
        print(f"Recall test: {result}")

        # Test function definition
        result = interpreter.execute('define test_func(x) { remember(x) as "func_test" }')
        print(f"Function test: {result}")

        print("✅ Core interpreter works correctly")
        return True

    except Exception as e:
        print(f"❌ Error testing interpreter: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_interpreter()
    exit(0 if success else 1)
