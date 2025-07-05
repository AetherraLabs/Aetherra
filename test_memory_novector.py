"""Test without vector support"""

print("Testing without vector dependencies...")

import builtins
import sys

# Mock the imports to prevent them from loading
original_import = builtins.__import__


def mock_import(name, *args, **kwargs):
    if name in ["faiss", "sentence_transformers"]:
        raise ImportError(f"Mock: {name} not available")
    return original_import(name, *args, **kwargs)


builtins.__import__ = mock_import

try:
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem

    print("✅ advanced_vector_memory imported (no vector support)")

    # Test instantiation
    memory = AdvancedMemorySystem()
    print("✅ AdvancedMemorySystem instantiated")

except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback

    traceback.print_exc()
finally:
    # Restore original import
    builtins.__import__ = original_import

print("Done.")
