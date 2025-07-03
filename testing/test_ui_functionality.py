"""
Test script to verify the functionality of neuro_chat.py and neuroplex.py in a real application context.
This script attempts to import and initialize the key UI components from both modules.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# print("Testing UI module imports...")
try:
        LyrixaAssistantInterface,
        create_embeddable_neurochat,
    )

    print("✓ Successfully imported LyrixaAssistantInterface and create_embeddable_neurochat")

    # Try to create a LyrixaAssistantInterface instance (will only work if PySide6 is available)
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        chat = LyrixaAssistantInterface()
        print("✓ Successfully created LyrixaAssistantInterface instance")
    except ImportError:
        print("ℹ PySide6 not available, skipping LyrixaAssistantInterface instantiation")
    except Exception as e:
        print(f"✗ Error creating LyrixaAssistantInterface instance: {e}")
except Exception as e:
    print(f"✗ Error importing from neuro_chat.py: {e}")

try:
    from src.aethercode.ui.aetherplex import LyrixaWindow

    print("✓ Successfully imported LyrixaWindow")

    # Try to create a LyrixaWindow instance (will only work if PySide6 is available)
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        main_window = LyrixaWindow()
        print("✓ Successfully created LyrixaWindow instance")
    except ImportError:
        print("ℹ PySide6 not available, skipping LyrixaWindow instantiation")
    except Exception as e:
        print(f"✗ Error creating LyrixaWindow instance: {e}")
except Exception as e:
    print(f"✗ Error importing from neuroplex.py: {e}")

print("\nUI module testing complete.")
