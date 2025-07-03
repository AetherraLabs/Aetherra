"""
Test script to verify the functionality of neuroplex.py in a real application context.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# print("Testing neuroplex.py module imports...")
try:
    from src.aethercode.ui.aetherplex import LyrixaWindow

    print("✓ Successfully imported LyrixaWindow")

    # Try to create a LyrixaWindow instance (will only work if PySide6 is available)
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        main_window = LyrixaWindow()
        print("✓ Successfully created LyrixaWindow instance")

        # Check if critical methods are available
        if hasattr(main_window, "init_ui"):
            print("✓ init_ui method available")
        if hasattr(main_window, "setup_dark_theme"):
            print("✓ setup_dark_theme method available")
        if hasattr(main_window, "setup_chat_panel"):
            print("✓ setup_chat_panel method available")

    except ImportError:
        print("ℹ PySide6 not available, skipping LyrixaWindow instantiation")
    except Exception as e:
        print(f"✗ Error creating LyrixaWindow instance: {e}")
except Exception as e:
    print(f"✗ Error importing from neuroplex.py: {e}")

print("\nNeuroplex testing complete.")
