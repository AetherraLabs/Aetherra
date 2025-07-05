"""Very simple import test"""

print("Starting import test...")

try:
    print("Step 1: Testing anticipation_engine...")
    from lyrixa.core.anticipation_engine import AnticipationEngine
    print("✅ anticipation_engine imported")
except Exception as e:
    print(f"❌ anticipation_engine failed: {e}")
    import traceback
    traceback.print_exc()

print("Done.")
