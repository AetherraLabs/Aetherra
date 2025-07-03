#!/usr/bin/env python3
"""
🎨 Neuroplex v2.0 Feature Demo
=============================

Demonstrates the new dark mode GUI and enhanced features.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_qt_availability():
    """Test Qt library availability"""
    print("🔍 Testing Qt Library Availability...")

    # Test PySide6
    try:

        print("✅ PySide6 available")
        return True
    except ImportError:
        print("❌ PySide6 not available")

    # Test PyQt6
    try:

        print("✅ PyQt6 available")
        return True
    except ImportError:
        print("❌ PyQt6 not available")

    return False


def demo_features():
    """Demo the new features"""
    print("\n🧬 Neuroplex v2.0 Features:")
    print("━" * 50)
    print("🎨 Ultra-modern dark mode interface")
    print("🤖 Multi-LLM provider support (GPT-4, Claude, Gemini, Local)")
    print("🧠 Advanced vector memory visualization")
    print("⚡ Real-time performance monitoring")
    print("💬 Natural language programming interface")
    print("🎯 Goal-driven development tracking")
    print("🔌 Enhanced plugin ecosystem manager")
    print("📊 Live system metrics dashboard")
    print("🚀 AI-assisted code generation")
    print("💾 Modern file management")
    print("━" * 50)


def main():
    """Run the demo"""
    print("🧬 Neuroplex v2.0 Feature Demo")
    print("=" * 40)

    # Test Qt availability
    qt_available = test_qt_availability()

    if not qt_available:
        print("\n⚠️ No Qt library available!")
        print("📋 To use Neuroplex v2.0, install a Qt library:")
        print("   pip install PySide6")
        print("   or")
        print("   pip install PyQt6")
        return

    # Demo features
    demo_features()

    # Launch demo
    print("\n🚀 Launching Neuroplex v2.0 Demo...")
    try:
        from ui.aetherplex_gui_v2 import main as launch_gui

        launch_gui()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        print("💡 Try running: python launch_neuroplex_v2.py")


if __name__ == "__main__":
    main()
