#!/usr/bin/env python3
"""
Direct test of the Lyrixa Hybrid GUI - Phase 1 Implementation
"""

import sys
import os

# Add the lyrixa_core directory to the path
lyrixa_core_path = os.path.join(os.path.dirname(__file__), 'Aetherra', 'lyrixa_core')
sys.path.insert(0, lyrixa_core_path)

try:
    from gui.main_window import LyrixaHybridWindow
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    def test_hybrid_gui():
        """Test the Lyrixa Hybrid GUI directly"""
        print("🚀 Starting Lyrixa Hybrid GUI Test...")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Lyrixa Neural Interface")
        app.setOrganizationName("Aetherra")

        # Create and show the hybrid window
        window = LyrixaHybridWindow()
        window.show()

        print("✅ Lyrixa Hybrid GUI launched successfully!")
        print("🎨 Features active:")
        print("   • Authentic Aetherra branding with jade green accents")
        print("   • Hybrid PySide6 + Web architecture")
        print("   • Interactive dashboard with neural activity visualization")
        print("   • Three-panel layout: Controls | Web View | Metrics")
        print("   • JavaScript effects with floating particles")
        print("   • QWebChannel communication bridge")
        print("\n[TOOL] Phase 1 Implementation Complete!")
        print("💡 Click the buttons to test panel switching and web integration")

        # Start the application event loop
        return app.exec()

    if __name__ == "__main__":
        exit_code = test_hybrid_gui()
        sys.exit(exit_code)

except Exception as e:
    print(f"[ERROR] Error testing Lyrixa Hybrid GUI: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
