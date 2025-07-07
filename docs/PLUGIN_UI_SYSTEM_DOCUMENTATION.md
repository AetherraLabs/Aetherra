# Plugin-Driven UI System Documentation

## Overview

The Plugin-Driven UI System for Lyrixa provides a robust, modular architecture that separates core (hardcoded) features from plugin-based capabilities. This system enables dynamic loading of UI components, theme switching, mode transitions, and viewport management.

## Architecture

### Core Components

1. **PluginSchema**: Defines the schema for plugin validation
2. **PluginUIManager**: Main manager for plugin-driven UI operations

### Key Features

- **Dynamic Plugin Loading**: Register and load plugins at runtime
- **Zone-Based Layout**: Assign plugins to specific UI zones
- **Theme Switching**: Support for light/dark themes with plugin notifications
- **Mode Switching**: Developer/Simple/Live Agent modes with layout adjustments
- **Viewport Management**: Dynamic configuration and updating of viewports

## File Structure

```
lyrixa/
├── gui/
│   ├── plugin_ui_loader.py          # Main PluginUIManager and schema
│   └── test_plugin_ui_manager.py    # Test/demo script
└── plugins/
    ├── sample_plugin_1.py           # Sample plugin implementation
    └── sample_plugin_2.py           # Sample plugin implementation
```

## Usage

### Basic Usage

```python
from plugin_ui_loader import PluginUIManager

# Create UI manager instance
ui_manager = PluginUIManager()

# Initialize layout
ui_manager.initialize_layout()

# Load a plugin
plugin_data = {
    "name": "MyPlugin",
    "version": "1.0.0",
    "author": "Developer",
    "description": "A sample plugin",
    "ui_component": MyPluginComponent()
}
ui_manager.load_plugin(plugin_data)

# Assign plugin to a zone
ui_manager.set_zone("suggestion_panel", ui_manager.plugins[0])

# Render the UI
ui_manager.render()
```

### Theme Management

```python
# Switch themes
ui_manager.switch_theme("dark")  # or "light"

# Plugins with on_theme_change method will be automatically notified
```

### Mode Switching

```python
# Switch between modes
ui_manager.switch_mode("Developer")  # Developer, Simple, Live Agent
ui_manager.switch_mode("Simple")
ui_manager.switch_mode("Live Agent")
```

### Viewport Management

```python
# Configure viewports
viewports = {
    "main_view": {"width": 800, "height": 600},
    "side_panel": {"width": 300, "height": 600}
}
ui_manager.configure_viewports(viewports)

# Update specific viewport
ui_manager.update_viewport("main_view", {"width": 1024, "height": 768})
```

## Plugin Development

### Plugin Schema

Each plugin must follow the PluginSchema:

```python
plugin_data = {
    "name": str,           # Plugin name (required)
    "version": str,        # Version string (required)
    "author": str,         # Author name (required)
    "description": str,    # Plugin description
    "ui_component": Any    # UI component object (required)
}
```

### Plugin Implementation Example

```python
# sample_plugin.py
class SampleUIComponent:
    def __init__(self):
        self.name = "Sample Component"

    def on_theme_change(self, theme):
        print(f"Theme changed to: {theme}")

    def render(self):
        return "Sample plugin content"

plugin_data = {
    "name": "SamplePlugin",
    "version": "1.0.0",
    "author": "Developer",
    "description": "A sample plugin for demonstration",
    "ui_component": SampleUIComponent()
}
```

## Available Zones

The system provides the following predefined zones:

- `suggestion_panel`: For suggestion-related plugins
- `analytics_panel`: For analytics and monitoring plugins
- `plugin_slot_left`: General purpose left slot
- `plugin_slot_right`: General purpose right slot

## API Reference

### PluginUIManager Methods

#### Core Operations
- `register_plugin(plugin)`: Register a plugin
- `load_plugin(plugin_data)`: Load and register a plugin from data
- `set_zone(zone_name, plugin)`: Assign plugin to a zone
- `initialize_layout()`: Initialize default layout
- `render()`: Render current UI state

#### Theme Management
- `switch_theme(theme)`: Switch theme ("light" or "dark")
- `notify_plugins_of_theme_change()`: Notify all plugins of theme change

#### Mode Management
- `switch_mode(mode)`: Switch mode ("Developer", "Simple", "Live Agent")
- `update_layout_for_mode()`: Update layout based on current mode

#### Viewport Management
- `configure_viewports(viewports)`: Configure multiple viewports
- `update_viewport(viewport_name, configuration)`: Update specific viewport

## Testing

Run the test script to verify functionality:

```bash
python lyrixa/gui/test_plugin_ui_manager.py
```

The test demonstrates:
- Plugin registration and zone assignment
- Theme switching with plugin notifications
- Mode transitions and layout updates
- Viewport configuration and updates

## Migration from Legacy UI

### Archived Components

The following legacy UI components have been archived:
- `enhanced_lyrixa.py` → `archive/legacy_ui/enhanced_lyrixa.py`
- `analytics_dashboard.py` → `archive/legacy_ui/analytics_dashboard.py`
- `unified/` directory → `archive/legacy_ui/unified/`

### Integration Points

The new plugin-driven system is designed to work with:
- Existing configuration management
- Theme systems
- Performance monitoring
- User preferences

## Best Practices

1. **Plugin Validation**: Always validate plugins using the PluginSchema
2. **Theme Responsiveness**: Implement `on_theme_change` in plugin components
3. **Mode Awareness**: Design plugins to adapt to different modes
4. **Error Handling**: Implement proper error handling for plugin loading
5. **Performance**: Consider plugin impact on UI performance

## Future Enhancements

- Plugin dependency management
- Hot-reloading of plugins
- Plugin marketplace integration
- Advanced layout managers
- Plugin sandboxing and security

## Conclusion

The Plugin-Driven UI System provides a solid foundation for modular UI development in Lyrixa. It successfully separates core functionality from pluggable components while maintaining flexibility and performance.
