#!/usr/bin/env python3
"""
Simple Brain Loop Test
"""

def test_brain_loop_simple():
    """Simple test of the brain loop"""
    print("🧠 Testing Lyrixa Brain Loop (Simple)...")

    try:
        # Test import
        print("[DISC] Importing LyrixaAI...")
        from lyrixa.assistant import LyrixaAI
        print("✅ Import successful!")

        # Test initialization
        print("🎯 Initializing LyrixaAI...")
        lyrixa = LyrixaAI()
        print(f"✅ LyrixaAI initialized: {lyrixa.name} v{lyrixa.version}")

        # Test basic brain loop method exists
        print("🧠 Checking brain_loop method...")
        if hasattr(lyrixa, 'brain_loop'):
            print("✅ brain_loop method found!")
        else:
            print("❌ brain_loop method not found!")
            return False

        print("🎉 Basic Brain Loop test passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_brain_loop_simple()
    if success:
        print("\n✅ Brain Loop is ready!")
    else:
        print("\n❌ Brain Loop needs fixes.")
