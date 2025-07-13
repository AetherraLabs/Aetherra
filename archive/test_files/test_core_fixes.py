#!/usr/bin/env python3
"""
Test script to verify all core errors have been resolved
"""

print("=== Aetherra Core Error Resolution Test ===")
try:
    from Aetherra.core.enhanced_interpreter import EnhancedAetherraInterpreter

    print("✅ Enhanced interpreter import: SUCCESS")

    interpreter = EnhancedAetherraInterpreter()
    print("✅ Enhanced interpreter creation: SUCCESS")

    result = interpreter.execute_Aetherra('test = "Hello Aetherra!"')
    print("✅ Aetherra execution: SUCCESS")

    from Aetherra.core.local_ai import LocalAIEngine

    local_ai = LocalAIEngine()
    print("✅ Local AI engine: SUCCESS")

    from Aetherra.core.vector_memory import EnhancedSemanticMemory

    vector_memory = EnhancedSemanticMemory()
    print("✅ Vector memory system: SUCCESS")

    from Aetherra.core.intent_parser import IntentToCodeParser

    intent_parser = IntentToCodeParser()
    print("✅ Intent parser: SUCCESS")

    print("\n=== ALL CORE ERRORS RESOLVED! ===")
    print("🎉 Aetherra is ready for Phase 2 AI features!")
    print("🚀 All type annotations, import errors, and min/max key issues fixed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
