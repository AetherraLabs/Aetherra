"""Test advanced memory import"""

print("Testing advanced memory import...")

try:
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
    print("✅ advanced_vector_memory imported")
except Exception as e:
    print(f"❌ advanced_vector_memory failed: {e}")
    import traceback
    traceback.print_exc()

print("Done.")
