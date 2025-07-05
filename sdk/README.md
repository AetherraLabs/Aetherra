# Aetherra Plugin SDK

The Aetherra Plugin SDK lets you extend the language with intelligent, modular capabilities — from voice transcription to Git commits, search queries, file operations, and more.

## 🚀 What Is a Plugin?

A plugin is a Python file that registers new commands into the Aetherra runtime. These commands can be called from `.aether` files like:

```neuro
plugin: whisper.transcribe "meeting.wav"
plugin: git.commit "Refactored memory engine"
plugin: example.calculate "2 + 3 * 4"
plugin: file.create "README.md" "# My Project"
```

Each plugin defines one or more functions that perform tasks, return results, and optionally update Neuroplex's memory.

## 📁 Plugin File Structure

Place all plugins inside:

```
sdk/plugins/
```

Each plugin is a single `.py` file. Example structure:

```
sdk/plugins/
├── whisper.py          # Voice transcription
├── git.py              # Git operations
├── search.py           # Web/local search
├── file_tools.py       # File operations
├── local_llm.py        # Local AI models
└── example.py          # Template plugin
```

## ✨ Minimal Plugin Example

```python
# sdk/plugins/example.py
from core.plugin_api import register_plugin

@register_plugin("example")
def hello_world(args):
    return f"Hello from example plugin! Args: {args}"
```

## 🔧 Advanced Plugin Template

```python
# sdk/plugins/advanced_example.py
from core.plugin_api import register_plugin
from typing import Dict, Any, Optional
import datetime

@register_plugin(
    name="advanced_example",
    description="An advanced plugin demonstrating full SDK capabilities",
    capabilities=["processing", "analysis", "reporting"],
    version="1.0.0",
    author="Aetherra Team",
    category="utilities",
    dependencies=["requests", "json"],

    # AI Integration
    intent_purpose="data processing and analysis",
    intent_triggers=["process", "analyze", "report"],
    intent_scenarios=["data transformation", "analysis reporting"],
    ai_description="Advanced plugin for data processing and analysis tasks",
    example_usage="plugin: advanced_example.process 'data.json'",
    confidence_boost=1.2
)
def process_data(data: str, format: str = "json") -> Dict[str, Any]:
    """
    Process data in various formats.

    Args:
        data: Input data to process
        format: Output format (json, csv, text)

    Returns:
        Dict containing processed results
    """
    try:
        result = {
            "success": True,
            "input": data,
            "format": format,
            "processed_at": datetime.datetime.now().isoformat(),
            "result": f"Processed: {data}"
        }

        # Memory integration
        memory_update = {
            "plugin": "advanced_example",
            "action": "process_data",
            "timestamp": datetime.datetime.now().isoformat(),
            "data": data
        }

        return {
            **result,
            "memory_update": memory_update
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }

@register_plugin("advanced_example")
def analyze(data: str, method: str = "basic") -> Dict[str, Any]:
    """
    Analyze data using specified method.
    """
    return {
        "success": True,
        "analysis": f"Analyzed {data} using {method} method",
        "timestamp": datetime.datetime.now().isoformat()
    }
```

## 📋 Plugin Registration Options

| Parameter          | Type      | Description              | Required |
| ------------------ | --------- | ------------------------ | -------- |
| `name`             | str       | Plugin identifier        | ✅        |
| `description`      | str       | Plugin description       | ❌        |
| `capabilities`     | List[str] | Plugin capabilities      | ❌        |
| `version`          | str       | Plugin version           | ❌        |
| `author`           | str       | Plugin author            | ❌        |
| `category`         | str       | Plugin category          | ❌        |
| `dependencies`     | List[str] | Required packages        | ❌        |
| `intent_purpose`   | str       | AI integration purpose   | ❌        |
| `intent_triggers`  | List[str] | AI trigger words         | ❌        |
| `intent_scenarios` | List[str] | Use case scenarios       | ❌        |
| `ai_description`   | str       | AI-readable description  | ❌        |
| `example_usage`    | str       | Usage example            | ❌        |
| `confidence_boost` | float     | AI confidence multiplier | ❌        |

## 🎯 Plugin Usage in .aether Files

### Basic Syntax
```neuro
plugin: plugin_name.function_name "argument"
plugin: plugin_name.function_name arg1 arg2 arg3
```

### Examples
```neuro
# Voice transcription
plugin: whisper.transcribe "meeting_audio.wav"

# Git operations
plugin: git.commit "Added new features"
plugin: git.status
plugin: git.push "origin main"

# File operations
plugin: file.create "config.json" '{"debug": true}'
plugin: file.read "data.txt"
plugin: file.backup "/important/files"

# Search operations
plugin: search.web "Aetherra programming language"
plugin: search.local "TODO comments" "*.py"

# Local AI
plugin: local_llm.chat "Explain quantum computing"
plugin: local_llm.generate "Write a Python function to sort lists"
```

## 🔌 Available Official Plugins

### 🎤 Whisper Plugin (`whisper.py`)
Voice transcription using OpenAI Whisper
- `transcribe(audio_file)` - Transcribe audio to text
- `transcribe_live()` - Real-time voice input

### 🌐 Git Plugin (`git_plugin.py`)
Git repository operations
- `status()` - Show repository status
- `commit(message)` - Commit changes
- `push(remote, branch)` - Push to remote
- `pull()` - Pull latest changes
- `branch(name)` - Create/switch branch

### 📁 File Tools (`file_tools.py`)
File system operations
- `create(filename, content)` - Create file
- `read(filename)` - Read file content
- `write(filename, content)` - Write to file
- `backup(path)` - Backup files/directories
- `find(pattern, directory)` - Search files

### 🤖 Local LLM (`local_llm.py`)
Local AI model integration
- `chat(message)` - Chat with local AI
- `generate(prompt)` - Generate text
- `summarize(text)` - Summarize content
- `translate(text, target_lang)` - Translate text

### 🧮 Math Plugin (`math_plugin.py`)
Mathematical operations
- `calculate(expression)` - Evaluate math expressions
- `solve(equation)` - Solve equations
- `graph(function)` - Plot mathematical functions

## 🔧 Development Guidelines

### 1. Plugin Best Practices
- ✅ Use clear, descriptive function names
- ✅ Include comprehensive docstrings
- ✅ Handle errors gracefully
- ✅ Return structured data (Dict/JSON)
- ✅ Support both required and optional parameters

### 2. Error Handling
```python
@register_plugin("example")
def safe_function(data: str) -> Dict[str, Any]:
    try:
        # Plugin logic here
        result = process_data(data)
        return {"success": True, "result": result}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### 3. Memory Integration
```python
@register_plugin("example")
def memory_aware_function(data: str) -> Dict[str, Any]:
    result = process_data(data)

    return {
        "success": True,
        "result": result,
        "memory_update": {
            "plugin": "example",
            "action": "memory_aware_function",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    }
```

## 🚀 Getting Started

1. **Create your plugin file:**
   ```bash
   touch sdk/plugins/my_plugin.py
   ```

2. **Write your plugin:**
   ```python
   from core.plugin_api import register_plugin

   @register_plugin("my_plugin")
   def my_function(arg1, arg2="default"):
       return f"Processing {arg1} with {arg2}"
   ```

3. **Test in .aether code:**
   ```neuro
   plugin: my_plugin.my_function "test data" "custom value"
   ```

4. **Check plugin is loaded:**
   ```neuro
   system: list_plugins
   ```

## 📚 API Reference

For complete API documentation, see: `docs/PLUGIN_SDK.md`

## 🤝 Contributing

Want to contribute a plugin?
1. Fork the repository
2. Create your plugin in `sdk/plugins/`
3. Add tests and documentation
4. Submit a pull request

## 📝 License

Aetherra Plugin SDK is MIT licensed. See `LICENSE` for details.
