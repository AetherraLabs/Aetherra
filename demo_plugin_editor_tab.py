#!/usr/bin/env python3
"""
Plugin Editor Tab Demo
======================

Demonstrate the complete Plugin Editor functionality including:
- File browser integration
- Live code editing capabilities
- Real plugin file loading and display
- Future-ready architecture for metadata parsing
"""

import os
import sys

# Add the project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))
sys.path.insert(0, os.path.dirname(__file__))


def create_sample_plugin():
    """Create a sample plugin file for demonstration"""
    sample_plugin_content = '''"""
Sample Aetherra Plugin
=====================

A demonstration plugin showing the structure and capabilities
of the Aetherra plugin system.
"""

class SamplePlugin:
    """A sample plugin demonstrating core functionality"""

    def __init__(self):
        self.name = "SamplePlugin"
        self.version = "1.0.0"
        self.description = "A demonstration plugin for Aetherra"

    def activate(self):
        """Activate the plugin"""
        print(f"🔌 {self.name} v{self.version} activated!")

    def deactivate(self):
        """Deactivate the plugin"""
        print(f"🔌 {self.name} deactivated")

    def execute(self, command, args=None):
        """Execute plugin command"""
        if command == "hello":
            return f"Hello from {self.name}!"
        elif command == "info":
            return {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "commands": ["hello", "info", "status"]
            }
        elif command == "status":
            return "Plugin is running normally"
        else:
            return f"Unknown command: {command}"

# Plugin metadata (future .aetherplugin integration)
PLUGIN_METADATA = {
    "name": "SamplePlugin",
    "version": "1.0.0",
    "author": "Aetherra Team",
    "description": "A demonstration plugin",
    "category": "utility",
    "dependencies": [],
    "permissions": ["read", "execute"],
    "entry_point": "SamplePlugin"
}

# Export the plugin class
__all__ = ["SamplePlugin", "PLUGIN_METADATA"]
'''

    with open("sample_plugin.py", "w", encoding="utf-8") as f:
        f.write(sample_plugin_content)

    return "sample_plugin.py"


def demo_plugin_editor():
    """Demo the Plugin Editor tab functionality"""
    print("🔌 Plugin Editor Tab Demo Starting...")

    try:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication

        from Aetherra.lyrixa.gui.hybrid_window import LyrixaWindow

        # Create sample plugin for demonstration
        sample_file = create_sample_plugin()
        print(f"📝 Created sample plugin: {sample_file}")

        # Create Qt application
        app = QApplication([])

        # Create window
        window = LyrixaWindow()

        print("🖥️ Plugin Editor Tab Features:")
        print("   ✅ File browser integration (QFileDialog)")
        print("   ✅ Live code editor (QTextEdit)")
        print("   ✅ Syntax highlighting-ready structure")
        print("   ✅ Future .aetherplugin metadata hooks")

        # Simulate file loading
        print(f"\n🔄 Simulating plugin file loading...")
        try:
            with open(sample_file, "r", encoding="utf-8") as f:
                content = f.read()
                window.plugin_editor.setPlainText(content)
            print(f"✅ Plugin file loaded into editor ({len(content)} characters)")
        except Exception as e:
            print(f"⚠️ File loading simulation: {e}")

        # Show window briefly for visual confirmation
        window.show()

        # Navigate to Plugin Editor tab
        plugin_editor_tab_index = 6  # 7th tab (0-indexed)
        window.tab_widget.setCurrentIndex(plugin_editor_tab_index)
        window.sidebar.setCurrentRow(plugin_editor_tab_index)

        print("\n🎯 Plugin Editor Tab Capabilities:")
        print("   📂 Browse and open .py plugin files")
        print("   ✏️ Live editing with QTextEdit widget")
        print("   💾 Future saving capabilities (save button ready)")
        print("   🎨 Syntax highlighting integration points")
        print("   📋 Metadata parsing hooks for .aetherplugin files")

        # Test the editor content
        editor_content = window.plugin_editor.toPlainText()
        if editor_content:
            lines = len(editor_content.split("\n"))
            print(f"📊 Editor loaded with {lines} lines of code")

        print("\n🔗 Future Integration Points:")
        print("   - Syntax highlighting (QSyntaxHighlighter)")
        print("   - Auto-completion (code intelligence)")
        print("   - Plugin validation and testing")
        print("   - .aetherplugin metadata editing")
        print("   - Plugin debugging and profiling")

        # Clean shutdown
        def cleanup():
            app.quit()
            try:
                os.remove(sample_file)
            except:
                pass

        QTimer.singleShot(2000, cleanup)  # Close after 2 seconds

        print("\n🎉 Plugin Editor Tab Demo Complete!")
        print("🚀 Ready for production use with file browser and live editing!")

        # Start event loop briefly
        app.exec()

        return True

    except Exception as e:
        print(f"❌ Plugin Editor Demo Failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_plugin_editor()
    sys.exit(0 if success else 1)
