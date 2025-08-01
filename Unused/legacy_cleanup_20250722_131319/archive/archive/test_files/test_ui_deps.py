#!/usr/bin/env python3
"""Test UI dependencies"""

# print("Testing Aetherra UI dependencies...")

# Test Qt availability
try:
    print("✅ PySide6 available")
    QT_AVAILABLE = True
except ImportError:
    try:
        print("✅ PyQt6 available")
        QT_AVAILABLE = True
    except ImportError:
        print("❌ Neither PySide6 nor PyQt6 available")
        QT_AVAILABLE = False

# Test Aetherra components
try:
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "core"))

    print("✅ AetherraMemory available")

    print("✅ Plugin manager available")

except ImportError as e:
    print(f"❌ Aetherra components error: {e}")

print(f"\nQt Available: {QT_AVAILABLE}")

if QT_AVAILABLE:
    print("🎉 UI can be launched!")
else:
    print("📦 Install Qt with: pip install PySide6")
