#!/usr/bin/env python3
"""
Simple test to identify where the blocking occurs
"""

import sys
from pathlib import Path

print("Step 1: Starting import test...")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Step 2: Testing Qt imports only...")

try:
    from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
    from PySide6.QtGui import QAction, QBrush, QColor, QFont, QPainter, QPen
    from PySide6.QtWidgets import (
        QApplication,
        QFileDialog,
        QFrame,
        QGraphicsOpacityEffect,
        QGroupBox,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    
    print("Step 3: Qt imports successful!")
    
except ImportError as e:
    print(f"Step 3: Qt import failed: {e}")
    sys.exit(1)

print("Step 4: Testing individual core module imports...")

# Test interpreter module
try:
    print("Step 4a: Importing interpreter...")
    import core.interpreter
    print("Step 4a: Interpreter imported successfully!")
except Exception as e:
    print(f"Step 4a: Interpreter import failed: {e}")

# Test memory module
try:
    print("Step 4b: Importing memory...")
    import core.memory
    print("Step 4b: Memory imported successfully!")
except Exception as e:
    print(f"Step 4b: Memory import failed: {e}")

# Test chat router module
try:
    print("Step 4c: Importing chat router...")
    import core.chat_router
    print("Step 4c: Chat router imported successfully!")
except Exception as e:
    print(f"Step 4c: Chat router import failed: {e}")

print("Step 5: All tests completed!")
