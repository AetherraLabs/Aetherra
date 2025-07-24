"""
Sample Plugin 2: Demonstrates another plugin with a different UI component.
"""


class SamplePlugin2:
    """Sample Plugin 2 for testing purposes."""

    # Required plugin metadata
    name = "sample_plugin_2"
    description = "Another sample plugin for testing purposes with UI component"
    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "Action to perform"}
        },
        "required": ["action"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Plugin result"},
            "ui_component": {"type": "string", "description": "UI component"},
        },
    }
    created_by = "Developer2"

    def execute(self, input_data):
        """Execute the plugin functionality."""
        return {
            "result": "Sample Plugin 2 executed successfully",
            "ui_component": self.sample_plugin_ui_component(),
            "status": "success",
        }

    def sample_plugin_ui_component(self):
        """Return UI component."""
        return "Sample Plugin 2 UI Component"


plugin_data = {
    "name": "SamplePlugin2",
    "version": "1.0",
    "author": "Developer2",
    "description": "Another sample plugin for testing purposes.",
    "ui_component": SamplePlugin2().sample_plugin_ui_component,
}
