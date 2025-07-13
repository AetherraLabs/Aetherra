"""
Test script for PluginUIManager.
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from plugin_ui_loader import PluginUIManager

# Import plugin data directly or create sample data
try:
    # Try to import from the correct path
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../plugins"))
    )
    from sample_plugin_1 import plugin_data as plugin1_data
    from sample_plugin_2 import plugin_data as plugin2_data
except ImportError:
    # Create sample plugin data if imports fail
    class SampleUIComponent:
        def __init__(self, name="SamplePlugin"):
            self.name = name

        def on_theme_change(self, theme):
            print(f"Plugin {self.name} received theme change: {theme}")

    plugin1_data = {
        "name": "SamplePlugin",
        "version": "1.0.0",
        "author": "Developer",
        "description": "A sample plugin for demonstration",
        "ui_component": SampleUIComponent("SamplePlugin"),
    }

    plugin2_data = {
        "name": "SamplePlugin1",
        "version": "1.0.0",
        "author": "Developer",
        "description": "Another sample plugin for demonstration",
        "ui_component": SampleUIComponent("SamplePlugin1"),
    }

# Debugging: Print the Python path to verify
print("Python Path:", sys.path)

# Create an instance of PluginUIManager
ui_manager = PluginUIManager()

# Initialize layout
ui_manager.initialize_layout()


# Define a sample plugin
def sample_plugin_ui_component():
    return "Sample UI Component"


sample_plugin_data = {
    "name": "SamplePlugin",
    "version": "1.0",
    "author": "TestAuthor",
    "description": "A sample plugin for testing purposes.",
    "ui_component": sample_plugin_ui_component,
}

# Load the sample plugin
ui_manager.load_plugin(sample_plugin_data)

# Load sample plugins
ui_manager.load_plugin(plugin1_data)
ui_manager.load_plugin(plugin2_data)

# Assign plugins to zones
ui_manager.set_zone("suggestion_panel", ui_manager.plugins[0])
ui_manager.set_zone("analytics_panel", ui_manager.plugins[1])

# Switch theme to dark
ui_manager.switch_theme("dark")

# Render the UI
ui_manager.render()

# Demonstrate mode switching
print("\nSwitching to Developer mode:")
ui_manager.switch_mode("Developer")
ui_manager.render()

print("\nSwitching to Live Agent mode:")
ui_manager.switch_mode("Live Agent")
ui_manager.render()

print("\nSwitching back to Simple mode:")
ui_manager.switch_mode("Simple")
ui_manager.render()

# Demonstrate dynamic viewport management
print("\nConfiguring viewports:")
ui_manager.configure_viewports(
    {
        "main_view": {"width": 800, "height": 600},
        "side_panel": {"width": 300, "height": 600},
    }
)

print("\nUpdating viewport 'main_view':")
ui_manager.update_viewport("main_view", {"width": 1024, "height": 768})

print("\nUpdating viewport 'side_panel':")
ui_manager.update_viewport("side_panel", {"width": 400, "height": 600})
