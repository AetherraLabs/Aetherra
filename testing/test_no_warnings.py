#!/usr/bin/env python3
"""
Test script to check for box-shadow warnings in Neuroplex
"""

import io
import sys
from contextlib import redirect_stderr


def test_aetherplex_no_warnings():
    """Test that Neuroplex launches without box-shadow warnings"""

    # Capture stderr to check for warnings
    captured_output = io.StringIO()

    with redirect_stderr(captured_output):
        try:
            # Import the main window
            from Lyrixa.ui.aetherplex import LyrixaWindow

            print("✅ LyrixaWindow imported successfully")

            # Try to create an instance (without showing UI)
            # This should trigger any CSS parsing that would show warnings
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app is None:
                app = QApplication([])

            # Create the window (but don't show it)
            window = LyrixaWindow()
            print("✅ LyrixaWindow created successfully")

            # Apply styling which would trigger any CSS warnings
            window.apply_delayed_chat_styling()
            print("✅ Styling applied successfully")

            # Clean up
            window.close()

        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False

    # Check captured output for box-shadow warnings
    output = captured_output.getvalue()
    if "Unknown property box-shadow" in output:
        print("❌ Found box-shadow warnings in output:")
        print(output)
        return False
    elif "box-shadow" in output.lower():
        print("⚠️  Found box-shadow mentions in output:")
        print(output)
        return False
    else:
        print("✅ No box-shadow warnings found!")
        return True


if __name__ == "__main__":
    success = test_aetherplex_no_warnings()
    if success:
        print("\n🎉 TEST PASSED: No box-shadow warnings detected!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED: box-shadow warnings still present")
        sys.exit(1)
