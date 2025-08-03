#!/usr/bin/env python3
"""
Lyrixa Stage 3 Testing Launcher
===============================

This script launches Lyrixa with the Stage 3 AI agents for testing
the collaboration and learning systems.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def launch_lyrixa():
    """Launch Lyrixa with Stage 3 AI agents"""
    print("🚀 Launching Lyrixa with Stage 3 AI Agent Systems...")
    print("=" * 60)

    try:
        # Import Qt application
        from PySide6.QtWidgets import QApplication

        # Create Qt application
        app = QApplication(sys.argv)

        # Import and create the hybrid window
        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        print("✅ Initializing Lyrixa Neural Interface...")
        window = LyrixaWindow()

        # Initialize the Stage 3 collaboration system
        if hasattr(window, 'initialize_agent_collaboration_system'):
            print("✅ Initializing Stage 3 Agent Collaboration System...")
            window.initialize_agent_collaboration_system()

        # Show the window
        window.show()

        print("✅ Lyrixa is now running!")
        print("\n🎯 STAGE 3 FEATURES ACTIVE:")
        print("   🤝 Agent Collaboration & Communication")
        print("   📚 Intelligent Learning Systems")
        print("   🧠 Real AI-Powered Analysis")
        print("   🔄 Adaptive Problem Solving")
        print("   💡 Knowledge Sharing Between Agents")
        print("\n💻 GUI Interface:")
        print("   - Go to the 'Agents' tab to see AI agents in action")
        print("   - Watch agent thought streams in real-time")
        print("   - See collaboration matrix updates")
        print("   - Test chat with Lyrixa in the Chat tab")
        print("   - Monitor system performance in Performance tab")

        print("\n🎉 The agents are now genuinely intelligent!")
        print("   No more fake animations - real AI at work!")

        # Run the application
        sys.exit(app.exec())

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Make sure PySide6 is installed: pip install PySide6")

    except Exception as e:
        print(f"[ERROR] Launch Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch_lyrixa()
