# quick_interpreter_test.py
"""Quick test of the modular interpreter system"""

try:
    print("Testing modular interpreter import...")
    from core.interpreter import AetherraInterpreter

    print("✅ Import successful")

    print("Testing interpreter initialization...")
    interpreter = AetherraInterpreter()
    print("✅ Initialization successful")

    print("Testing basic command execution...")
    result = interpreter.execute('remember("Hello modular world!")')
    print(f"✅ Command result: {result}")

    print("Testing system status...")
    status = interpreter.get_system_status()
    print(f"✅ System status available: {len(status)} sections")

    print("\n🎉 Modular interpreter is working correctly!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
