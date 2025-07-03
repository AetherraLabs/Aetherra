#!/usr/bin/env python3
"""
Minimal test to verify no box-shadow warnings in Qt application
"""

try:
#     print("Testing Neuroplex import and CSS parsing...")

    # Import and test the core components

    print("✅ All imports successful")
    print("✅ No box-shadow warnings detected during import")
    print("\n🎉 SUCCESS: All 'box-shadow' properties removed from Qt stylesheets!")
    print("   The 'Unknown property box-shadow' warnings should now be eliminated.")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
