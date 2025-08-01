# Aetherra Modular Launcher System

## Overview

The Aetherra Modular Launcher System provides a unified way to initialize and run the Aetherra platform with all its components, including the GUI, API server, and plugin system.

## Components

### 1. Launcher Module (`Aetherra/lyrixa/launcher.py`)

The core launcher module responsible for:
- Discovering and loading all Aetherra modules and plugins
- Tracking the state of loaded and unlinked modules
- Providing API compatibility functions
- Supporting both GUI and API server modes

### 2. GUI Integration (`aetherra_launcher.py`)

The main entry point that:
- Initializes the system with both GUI and API server support
- Provides proper error handling and logging
- Creates a unified experience for end users

### 3. Batch Launcher (`launch_aetherra.bat`)

A simple batch file for Windows users to launch the system with a double-click.

## Usage

### Running the Complete System

To launch Aetherra with both GUI and API server:
```
python aetherra_launcher.py
```

Or simply double-click the `launch_aetherra.bat` file.

### Command-Line Options (launcher.py)

The launcher supports these command-line options:
- `--gui` - Launch in GUI mode
- `--api` - Launch with API server

Example:
```
python -m Aetherra.lyrixa.launcher --gui --api
```

## Plugin System

The launcher automatically discovers and loads all valid plugins from:
- Python modules (.py files)
- Aetherra plugin files (.aether and .aetherplugin)

Plugins are discovered from:
- src/ directory
- plugins/ directory
- stdlib/ directory
- Any directory with valid Python or Aetherra plugin files

## API Functions

For developers, the launcher provides these key functions:

### `initialize_system(project_root, gui_mode=False, api_mode=False)`

Initializes the Aetherra system with specified options.

Parameters:
- `project_root`: Path to the project root directory
- `gui_mode`: Set to True to initialize GUI components
- `api_mode`: Set to True to start the API server

Returns:
- `(loaded_modules, unlinked_modules, api_server)` tuple

### `launch_all_features(project_root, gui_mode=False, api_mode=False)`

Core function that discovers and loads all Aetherra components.

Parameters:
- `project_root`: Path to the project root directory
- `gui_mode`: Whether to initialize in GUI mode
- `api_mode`: Whether to initialize in API mode

Returns:
- `(loaded_modules, unlinked_modules)` tuple

### `get_plugin_paths()`

Retrieves the paths of all discovered plugins (for GUI display).

Returns:
- List of plugin paths

## Integration with Existing Systems

The launcher system maintains backward compatibility through:
- The `initialize_system()` function that older code expects
- Error handling for different API server import paths
- Support for both GUI and headless operation
