# NeuroCode Plugin SDK Documentation

## Overview

The NeuroCode Plugin System provides a powerful and extensible way to add functionality to the NeuroCode environment. Plugins can be accessed both programmatically and through natural language `.neuro` code syntax.

## Plugin Structure

### Basic Plugin Registration

```python
from core.plugin_manager import register_plugin

@register_plugin(
    name="my_plugin",
    description="A sample plugin that demonstrates the SDK",
    capabilities=["example", "demo"],
    version="1.0.0",
    author="Your Name",
    category="utilities",
    dependencies=["requests"],  # Optional dependencies

    # Intent-based discovery (for AI integration)
    intent_purpose="demonstration and examples",
    intent_triggers=["demo", "example", "test"],
    intent_scenarios=["learning plugin development", "testing functionality"],
    ai_description="A sample plugin for demonstrating NeuroCode plugin capabilities",
    example_usage="plugin: my_plugin 'hello world'",
    confidence_boost=1.0
)
def my_plugin_function(message: str) -> Dict[str, Any]:
    """
    Main plugin function

    Args:
        message: Input message to process

    Returns:
        Dict containing result data
    """
    return {
        "success": True,
        "message": f"Plugin processed: {message}",
        "timestamp": str(datetime.now())
    }
```

### Plugin Metadata

| Field          | Type      | Description                         |
| -------------- | --------- | ----------------------------------- |
| `name`         | str       | Unique plugin identifier            |
| `description`  | str       | Human-readable description          |
| `capabilities` | List[str] | List of plugin capabilities         |
| `version`      | str       | Plugin version (semver recommended) |
| `author`       | str       | Plugin author name                  |
| `category`     | str       | Plugin category for organization    |
| `dependencies` | List[str] | Required Python packages            |

### Intent-Based Discovery

For AI integration and natural language discovery:

| Field              | Type      | Description                              |
| ------------------ | --------- | ---------------------------------------- |
| `intent_purpose`   | str       | What the plugin is designed for          |
| `intent_triggers`  | List[str] | Keywords that should trigger this plugin |
| `intent_scenarios` | List[str] | Use cases where plugin applies           |
| `ai_description`   | str       | AI-friendly description                  |
| `example_usage`    | str       | Example of how to use the plugin         |
| `confidence_boost` | float     | Relevance score multiplier (default 1.0) |

## Usage in .neuro Code

### Basic Syntax

```neuro
# Simple plugin call
plugin: my_plugin "hello world"

# Plugin with multiple arguments
plugin: calculate "2 + 3 * 4"

# File operations
plugin: create_file "output.txt" "Hello from NeuroCode!"
plugin: read_file "output.txt"
```

### Advanced Usage

```neuro
# Git workflow
plugin: git_status
plugin: git_commit "Automated commit via NeuroCode"

# Audio transcription
plugin: whisper_transcribe "meeting.wav"

# Local AI inference
plugin: ollama_chat "llama2" "Explain Python decorators"

# File management
plugin: list_files "src" "*.py"
plugin: delete_file "temp.txt" true
```

## Official Plugins

### Git Plugin (`git_plugin.py`)

**Functions:**
- `git_status()` - Get repository status
- `git_commit(message, add_all=True)` - Create commits
- `git_log(limit=10)` - View commit history

**Usage:**
```neuro
plugin: git_status
plugin: git_commit "Added new feature"
plugin: git_log 5
```

### File Tools (`file_tools.py`)

**Functions:**
- `create_file(filepath, content="")` - Create new files
- `read_file(filepath, max_lines=None)` - Read file contents
- `write_file(filepath, content)` - Write/overwrite files
- `list_files(directory=".", pattern="*")` - List directory contents
- `delete_file(filepath, confirm=False)` - Delete files safely

**Usage:**
```neuro
plugin: create_file "utils.py" "def hello(): pass"
plugin: read_file "config.json"
plugin: list_files "src" "*.py"
```

### Whisper Plugin (`whisper.py`)

**Functions:**
- `whisper_transcribe(audio_file, model="base")` - Transcribe audio
- `whisper_voice_command(command_text)` - Process voice commands

**Usage:**
```neuro
plugin: whisper_transcribe "meeting.wav"
plugin: whisper_voice_command "remember to refactor the code"
```

### Local LLM Plugin (`local_llm.py`)

**Functions:**
- `ollama_chat(model, prompt, temperature=0.7)` - Chat with Ollama models
- `ollama_list_models()` - List available models
- `huggingface_local(model_name, text)` - Use HuggingFace models
- `llamacpp_chat(model_path, prompt)` - CPU-optimized inference

**Usage:**
```neuro
plugin: ollama_chat "llama2" "How do Python generators work?"
plugin: ollama_list_models
plugin: huggingface_local "gpt2" "Once upon a time"
```

### Math Plugin (`math_plugin.py`)

**Functions:**
- `calculate(expression)` - Safe mathematical evaluation

**Usage:**
```neuro
plugin: calculate "sqrt(16) + 2^3"
plugin: calculate "sin(pi/2) * 100"
```

## Creating Custom Plugins

### 1. Create Plugin File

Create a new `.py` file in `src/neurocode/plugins/`:

```python
# src/neurocode/plugins/my_custom_plugin.py
from core.plugin_manager import register_plugin
from typing import Dict, Any

@register_plugin(
    name="weather",
    description="Get weather information",
    capabilities=["weather", "api", "forecast"],
    version="1.0.0",
    author="Weather Team",
    category="utilities",
    dependencies=["requests"],
    intent_purpose="weather information retrieval",
    intent_triggers=["weather", "forecast", "temperature"],
    intent_scenarios=["checking current weather", "planning activities"],
    ai_description="Provides current weather and forecast information",
    example_usage="plugin: weather 'New York'",
)
def get_weather(location: str) -> Dict[str, Any]:
    """Get weather for a location"""
    # Your implementation here
    return {
        "success": True,
        "location": location,
        "temperature": "22°C",
        "condition": "Sunny"
    }
```

### 2. Plugin Guidelines

**Return Format:**
- Always return a `Dict[str, Any]`
- Include `"success": True/False` for status
- Include `"error": "message"` for failures
- Provide helpful `"suggestion"` for errors

**Error Handling:**
```python
try:
    # Plugin logic here
    return {"success": True, "result": data}
except ImportError:
    return {
        "error": "Required package not found",
        "suggestion": "Install with: pip install package_name"
    }
except Exception as e:
    return {"error": f"Operation failed: {str(e)}"}
```

**Safety Considerations:**
- Validate all inputs
- Use safe file operations
- Check permissions before destructive operations
- Provide confirmation for dangerous actions

### 3. Testing Plugins

```python
# Test your plugin
from core.plugin_manager import get_plugin, execute_plugin_command

# Direct execution
plugin_func = get_plugin("weather")
result = plugin_func("London")
print(result)

# Via command syntax
result = execute_plugin_command('plugin: weather "London"')
print(result)
```

## Integration with NeuroCode

### Memory Integration

```neuro
# Store plugin results in memory
$weather_data = plugin: weather "San Francisco"
remember($weather_data) as "current_weather"

# Use in conditional logic
if $weather_data.temperature > 25:
    remember("It's warm today") as "weather_note"
```

### Goal Integration

```neuro
goal("Check weather and plan day") {
    $weather = plugin: weather "Boston"
    if $weather.condition == "Sunny":
        plugin: create_file "todo.txt" "Go for a walk in the park"
    else:
        plugin: create_file "todo.txt" "Work on indoor projects"
}
```

### AI Collaboration

The plugin system integrates with NeuroCode's AI capabilities:

```neuro
# AI can suggest and execute plugins based on context
ask_ai("How's the weather looking?")
# AI might respond by executing: plugin: weather "user_location"

# Plugin discovery based on intent
discover_plugins("I need to transcribe audio")
# Returns: whisper_transcribe plugin with high relevance score
```

## Plugin Management

### Listing Plugins

```python
from core.plugin_manager import list_plugins, get_plugins_info

# Get all plugin names
plugins = list_plugins()

# Get detailed information
info = get_plugins_info()
```

### Plugin Discovery

```python
from core.plugin_manager import discover_plugins_by_intent

# Find relevant plugins
suggestions = discover_plugins_by_intent(
    "I want to commit my code changes",
    context="working on a Python project"
)
```

### Enable/Disable Plugins

```python
from core.plugin_manager import toggle_plugin

# Disable a plugin
toggle_plugin("weather", False)

# Re-enable it
toggle_plugin("weather", True)
```

## Best Practices

1. **Clear Naming**: Use descriptive plugin names
2. **Documentation**: Provide clear docstrings and examples
3. **Error Handling**: Always handle exceptions gracefully
4. **Dependencies**: List all required packages
5. **Validation**: Validate inputs and provide helpful error messages
6. **Security**: Never execute arbitrary code; sanitize inputs
7. **Performance**: Consider caching for expensive operations
8. **Testing**: Test plugins thoroughly before deployment

## Plugin Icons and Branding

The plugin system supports the NeuroCode icon for consistent branding:

```python
# Icon path is available in plugin manager
from src.neurocode.ui.components.panels.plugin_manager import PluginManagerPanel
panel = PluginManagerPanel()
icon_path = panel.icon_path  # Path to neurocode-icon.png
```

## Future Enhancements

- Plugin marketplace integration
- Hot-reloading of plugins
- Plugin dependency management
- Sandboxed plugin execution
- Plugin analytics and usage tracking
- Visual plugin builder interface
