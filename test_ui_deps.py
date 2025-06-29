#!/usr/bin/env python3
"""Test UI dependencies"""

print("Testing NeuroCode UI dependencies...")

# Test Qt availability
try:
    import PySide6
    from PySide6.QtWidgets import QApplication

    print("✅ PySide6 available")
    QT_AVAILABLE = True
except ImportError:
    try:
        import PyQt6
        from PyQt6.QtWidgets import QApplication

        print("✅ PyQt6 available")
        QT_AVAILABLE = True
    except ImportError:
        print("❌ Neither PySide6 nor PyQt6 available")
        QT_AVAILABLE = False

# Test NeuroCode components
try:
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "core"))

    from memory import NeuroMemory

    print("✅ NeuroMemory available")

    from plugin_manager import get_plugin_ui_data, get_plugins_info

    print("✅ Plugin manager available")

except ImportError as e:
    print(f"❌ NeuroCode components error: {e}")

print(f"\nQt Available: {QT_AVAILABLE}")

if QT_AVAILABLE:
    print("🎉 UI can be launched!")
else:
    print("📦 Install Qt with: pip install PySide6")
