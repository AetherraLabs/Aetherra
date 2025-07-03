#!/usr/bin/env python3
"""
🚀 Simple NeuroCode UI Demo
===========================

Quick demonstration of the UI system implementation.
"""

import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ui import CodeLanguage, NeuroplexUI, UITheme


def main():
    print("🧬 NeuroCode UI System Demo")
    print("=" * 40)

    # Create UI instance
    ui = NeuroplexUI()

    # Test basic functionality
    ui.show_info("Welcome to NeuroCode UI Demo!")

    # Test theme switching
    ui.show_text("\n🎨 Testing Themes:")
    themes = [UITheme.MATRIX, UITheme.NEON, UITheme.CYBERPUNK]
    for theme in themes:
        ui.set_theme(theme)
        ui.show_success(f"Theme: {theme.value}")
        time.sleep(0.5)

    # Test rich display
    ui.show_text("\n📺 Rich Display Features:")

    # Code highlighting
    sample_code = """
think "Hello NeuroCode!"
goal create_ai_os

function greet(name) {
    remember "Greeting: " + name
    return "Hello " + name + "!"
}

agent greeter {
    task: greet
    memory: persistent
}
"""
    ui.show_code(sample_code, CodeLanguage.NEUROCODE)

    # Table display
    ui.show_text("\n📊 System Status:")
    ui.rich_display.print_table(
        headers=["Component", "Status"],
        rows=[
            ["UI System", "✅ Active"],
            ["Theme Manager", "✅ Active"],
            ["Rich Display", "✅ Active"],
            ["Visual Feedback", "✅ Active"],
        ],
    )

    # Command suggestions
    ui.show_text("\n💡 Command Suggestions:")
    suggestions = ui.get_command_suggestions("help")
    for suggestion in suggestions[:3]:
        ui.show_text(f"  • {suggestion.command.name}: {suggestion.command.description}")

    # Visual feedback demo
    ui.show_text("\n🔄 Visual Feedback Demo:")
    ui.show_thinking("Processing request...")
    time.sleep(2)
    ui.hide_thinking()
    ui.show_success("✅ UI System Implementation Complete!")

    # Show markdown
    ui.show_text("\n📝 Markdown Support:")
    markdown = """
# Implementation Status

## ✅ Completed Features
- **Theme System**: Multiple themes with hot-swapping
- **Visual Feedback**: Loading, thinking, status indicators
- **Rich Display**: Code highlighting, tables, markdown
- **Command System**: Auto-suggestions and shortcuts

## 🎯 Ready for Integration
The UI system is ready to be integrated with the main NeuroCode engine!
"""
    ui.show_markdown(markdown)

    ui.show_info("🎉 Demo completed successfully!")

    # Cleanup
    ui.cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
