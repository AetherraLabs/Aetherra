#!/usr/bin/env python3
"""Test specific PySide6 imports used in enhanced_lyrixa.py"""

try:
    print("Testing PySide6.QtCore import...")
    from PySide6.QtCore import Qt

    print("✅ QtCore.Qt imported")

    print("Testing PySide6.QtWidgets imports...")
    from PySide6.QtWidgets import (
        QAction,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMenuBar,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSplitter,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    print("✅ All QtWidgets imports successful")

    print("✅ All PySide6 imports working correctly")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
