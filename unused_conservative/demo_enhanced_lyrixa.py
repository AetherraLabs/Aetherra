#!/usr/bin/env python3
"""
Live Demo - Aetherra Enhanced Features
=====================================

This script demonstrates the enhanced Lyrixa features with live web interface.
Shows model switching, real-time chat, and auto-scrolling in action.
"""

import sys
import time
import asyncio
import webbrowser
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_conversation_manager():
    """Quick demo of conversation manager capabilities"""
    print("🚀 AETHERRA ENHANCED LYRIXA DEMO")
    print("=" * 50)

    # Test conversation manager directly
    from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

    print("📝 Initializing Conversation Manager...")
    cm = LyrixaConversationManager(workspace_path=str(project_root))

    # Show current setup
    model_info = cm.get_available_models()
    print(f"✅ Current Model: {model_info['current_model']}")
    print(f"🔢 Available Models: {len(model_info['available_models'])} models")
    print(f"⚡ Primary Models: {model_info['preferred_models'][:3]}")

    return cm

def demo_web_interface():
    """Launch and demo the web interface"""
    print("\n🌐 LAUNCHING WEB INTERFACE")
    print("=" * 50)

    try:
        from Aetherra.lyrixa.gui.web_interface_server import start_web_interface

        print("🚀 Starting Aetherra Neural Web Interface...")
        print("📱 Features available:")
        print("   • Model selector dropdown (top of page)")
        print("   • Real-time AI chat with auto-scroll")
        print("   • Enter key for quick messaging")
        print("   • Live model switching without restart")
        print("   • Cyberpunk neural interface design")

        print("\n⏳ Server starting... (this may take a moment)")
        print("🔗 Opening browser at http://127.0.0.1:8686")

        # Start the web interface (this will open a browser automatically)
        start_web_interface(auto_open=True)

    except KeyboardInterrupt:
        print("\n👋 Demo ended by user")
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")

if __name__ == "__main__":
    print("🎯 Starting Enhanced Lyrixa Live Demo")
    print("🕐 This demo will show:")
    print("   1. Conversation Manager with Ollama primary")
    print("   2. Model switching capabilities")
    print("   3. Live web interface with real AI chat")
    print("   4. All new features in action")

    input("\n⏎ Press Enter to continue...")

    # Demo 1: Conversation Manager
    cm = demo_conversation_manager()

    input("\n⏎ Press Enter to launch web interface...")

    # Demo 2: Web Interface
    demo_web_interface()
