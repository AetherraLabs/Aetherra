"""
Sample Plugin 1: Demonstrates a simple plugin with a UI component.
"""


class SamplePlugin1:
    """Sample Plugin 1 for testing purposes."""

    # Required plugin metadata
    name = "sample_plugin_1"
    description = "A sample plugin for testing purposes with UI component"
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
    created_by = "Developer1"

    def execute(self, input_data):
        """Execute the plugin functionality."""
        return {
            "result": "Sample Plugin 1 executed successfully",
            "ui_component": self.sample_plugin_ui_component(),
            "status": "success",
        }

    def sample_plugin_ui_component(self):
        """Return UI component."""
        return "Sample Plugin 1 UI Component"


plugin_data = {
    "name": "SamplePlugin1",
    "version": "1.0",
    "author": "Developer1",
    "description": "A sample plugin for testing purposes.",
    "ui_component": SamplePlugin1().sample_plugin_ui_component,
}
