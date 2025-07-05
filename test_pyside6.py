#!/usr/bin/env python3
"""Test PySide6 availability"""

try:
    import PySide6

    print("✅ PySide6 is available")
    print("Version:", PySide6.__version__)

    from PySide6.QtWidgets import QApplication

    print("✅ QtWidgets imported successfully")

    # Test creating an application
    app = QApplication([])
    print("✅ QApplication created successfully")

except ImportError as e:
    print("❌ PySide6 not available:", e)
except Exception as e:
    print("❌ Error with PySide6:", e)
