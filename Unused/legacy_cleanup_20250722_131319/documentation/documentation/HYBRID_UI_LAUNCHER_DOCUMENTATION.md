# Aetherra Hybrid UI Launcher

## Overview

The `aetherra_launcher.py` script provides a unified way to launch the Aetherra system with both the hybrid GUI and API server. This launcher supports multiple operation modes to accommodate different needs and troubleshooting scenarios.

## Features

### 1. Hybrid UI

- Modern PySide6-based user interface with WebView integration
- Dark theme with Aetherra green accents
- Tabbed interface for different functionality
- Neural Chat interface for conversational AI
- Plugin editor and management
- Memory visualization
- Goal tracking

### 2. API Server

- Automatic API server initialization
- Multiple fallback options for API server modules
- Port 8007 for self-improvement API
- Port 8008 for Lyrixa API
- Error handling and status reporting

### 3. Plugin System

- Automatic discovery of plugins and modules
- Support for Python modules (.py)
- Support for Aetherra plugin files (.aether, .aetherplugin)
- Integration with the GUI plugin browser

### 4. Multiple Operation Modes

- **Full Mode**: Complete functionality with all features
- **Minimal Mode**: Core functionality with essential plugins only
- **Safe Mode**: Basic window with minimal initialization for maximum stability
- **API-Only Mode**: Headless operation without GUI components
- **Diagnostic Mode**: System checks to identify configuration issues

## Launch Modes

### Full Mode (Default)

```bash
python aetherra_launcher.py
```

The standard launch mode that initializes all Aetherra components:
- Complete hybrid UI with all tabs
- Full plugin system
- API server with all capabilities
- Autonomous agent functionality
- Self-improvement systems

### Minimal Mode

```bash
python aetherra_launcher.py --minimal
```

A streamlined mode that focuses on stability:
- Core hybrid UI functionality
- Essential plugins only
- Basic API server capabilities
- Limited autonomous functionality
- Reduced system initialization

### Safe Mode

```bash
python aetherra_launcher.py --safe-mode
```

A diagnostic mode with minimal initialization:
- Basic window only
- No plugin loading
- Minimal system initialization
- Maximum stability for troubleshooting

### API-Only Mode

```bash
python aetherra_launcher.py --api-only
```

Runs Aetherra without the GUI:
- Full API server functionality
- Command-line interface
- No GUI components
- Suitable for headless operation

### Diagnostic Mode

```bash
python aetherra_launcher.py --diagnostic
```

A special mode for troubleshooting:
- Performs comprehensive system checks
- Verifies all required components
- Tests GUI environment
- Reports detailed diagnostics

## Interactive Launcher

The `launch_aetherra.bat` script provides an interactive menu to choose between the different modes:

1. Full Mode
2. Minimal Mode
3. Safe Mode
4. API-Only Mode
5. Diagnostics

## Technical Details

The launcher performs these key functions:

1. Sets up the environment for hybrid UI mode
2. Starts the API server in a background thread
3. Initializes the PySide6 Qt application
4. Creates the main window using the window factory
5. Initializes the Aetherra system with both GUI and API
6. Attaches components to the GUI (intelligence stack, runtime, lyrixa)
7. Initializes autonomous capabilities
8. Starts the Qt event loop

## Error Handling

The launcher includes robust error handling:

- If PySide6 is not installed, falls back to API-only mode
- Multiple fallback paths for API server modules
- Detailed logging of initialization steps and errors
- Graceful degradation when components are missing

## Troubleshooting

If the launcher doesn't start correctly:

1. Check that PySide6 is installed: `pip install PySide6`
2. Ensure the project structure is intact
3. Look at the terminal output for error messages
4. Check if API ports are already in use (8007, 8008)

## Requirements

- Python 3.8+
- PySide6
- OpenAI API key (for AI functionality)
- Local models (optional) via Ollama

## Customization

You can modify the behavior by editing these parts:

- Environment variables in the launcher script
- API server settings in the launcher
- QT style settings in the GUI modules

## Next Steps

1. **Additional Tabs**: The hybrid UI supports up to 10 tabs for different functionality
2. **Plugin Development**: Create new plugins for the Aetherra ecosystem
3. **AI Model Integration**: Connect more AI models to the system
4. **Memory System Enhancement**: Expand the knowledge and memory capabilities
