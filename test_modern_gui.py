#!/usr/bin/env python3
"""
Quick test script to verify the modern Lyrixa GUI is working
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_modern_gui():
    """Test if the modern GUI can be imported and initialized."""
    print("🧪 Testing Modern Lyrixa GUI...")

    try:
        # Test PySide6 import
        from PySide6.QtWidgets import QApplication

        print("✅ PySide6 is available")

        # Test Lyrixa components
        from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
        from lyrixa.core.conversation import LyrixaConversationalEngine

        print("✅ Lyrixa core components available")

        # Test modern GUI import
        from modern_lyrixa_gui import ModernLyrixaGUI

        print("✅ Modern GUI can be imported")

        # Create app instance (required for Qt)
        app = QApplication.instance() or QApplication(sys.argv)

        # Test GUI creation
        window = ModernLyrixaGUI()
        print("✅ Modern GUI created successfully")

        # Test if GUI has proper components
        if hasattr(window, "chat_display") and hasattr(window, "input_field"):
            print("✅ GUI components initialized properly")
        else:
            print("⚠️ Some GUI components missing")

        if window.engine:
            print("✅ Lyrixa engine initialized")
        else:
            print("⚠️ Lyrixa engine not initialized")

        if window.memory_system:
            print("✅ Memory system initialized")
        else:
            print("⚠️ Memory system not initialized")

        print("\n🎉 Modern Lyrixa GUI test completed successfully!")
        print("💡 You can now run: python lyrixa_unified_launcher.py --gui")

        # Don't show the window, just test initialization
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install PySide6")
        return False
    except Exception as e:
        print(f"❌ Error during GUI test: {e}")
        return False


if __name__ == "__main__":
    success = test_modern_gui()
    sys.exit(0 if success else 1)
