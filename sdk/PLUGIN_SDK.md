# Aetherra Plugin SDK

The Aetherra Plugin SDK lets you extend the language with intelligent, modular capabilities — from voice transcription to Git commits, search queries, file operations, and more.

## 🚀 What Is a Plugin?

A plugin is a Python file that registers new commands into the Aetherra runtime. These commands can be called from `.aether` files like:

```neuro
plugin: whisper.transcribe "meeting.wav"
plugin: git.commit "Refactored memory engine"
plugin: example.calculate "2 + 3 * 4"
```

Each plugin defines one or more functions that perform tasks, return results, and optionally update Lyrixa's memory.

## 📁 Plugin File Structure

Place all plugins inside:
```
sdk/plugins/
```

Each plugin is a single `.py` file. Example structure:
```
sdk/plugins/
├── whisper.py
├── git.py
├── search.py
├── example.py
└── calculator.py
```

## 🔧 Minimal Plugin Example

```python
# sdk/plugins/example.py
import sys
import os

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from core.plugin_api import register_plugin

@register_plugin(
    name="example",
    description="Simple example plugin",
    example_usage="plugin: example.hello_world 'Aetherra'"
)
def hello_world(args=""):
    return f"Hello from example plugin! Args: {args}"
```

Use in `.aether`:
```neuro
plugin: example.hello_world "Aetherra"
```

## ⚙️ Plugin Registration

Use the `@register_plugin("name")` decorator to expose plugin commands.

Each function becomes available as `plugin_name.function_name`.

### Registration Parameters

- **name**: Plugin identifier (required)
- **description**: Plugin description
- **capabilities**: List of plugin capabilities
- **version**: Plugin version (default: "1.0.0")
- **author**: Plugin author
- **category**: Plugin category
- **example_usage**: Usage example for documentation
- **ai_description**: AI-readable description

### Example with Full Registration

```python
@register_plugin(
    name="math",
    description="Mathematical operations and calculations",
    capabilities=["arithmetic", "algebra", "trigonometry"],
    version="1.2.0",
    author="Aetherra Team",
    category="utilities",
    example_usage="plugin: math.calculate '2 + 3 * sin(45)'",
    ai_description="Performs safe mathematical calculations"
)
def calculate(expression: str):
    # ... implementation
    pass
```

## ✅ Plugin Best Practices

### ✅ **Input Validation**
Always validate inputs before processing:

```python
def process_file(filename: str):
    if not isinstance(filename, str):
        return "Error: Filename must be a string"

    if not filename.strip():
        return "Error: Filename cannot be empty"

    # ... rest of implementation
```

### ✅ **Error Handling**
Catch and return meaningful error messages:

```python
def risky_operation(data):
    try:
        # ... risky code
        return f"Success: {result}"
    except FileNotFoundError:
        return "Error: File not found"
    except PermissionError:
        return "Error: Permission denied"
    except Exception as e:
        return f"Error: {str(e)}"
```

### ✅ **Return Values**
Always return a response (string or dict):

```python
def good_plugin():
    return "Operation completed successfully"

def also_good_plugin():
    return {
        "status": "success",
        "result": "data",
        "metadata": {"timestamp": "2025-01-01"}
    }
```

### ✅ **Memory Integration**
Optionally update memory with important events:

```python
from core.memory import remember

@register_plugin("memory_example")
def important_action(data):
    result = process(data)
    remember(f"Plugin processed {data} with result: {result}")
    return result
```

### ✅ **Security**
- Avoid plugins that execute raw shell commands unless necessary
- Use `require_user_approval()` for risky actions (e.g., file delete)
- Never silently overwrite important files
- Validate all user inputs

## 📚 Plugin Index

| Plugin          | Description             | Usage Example                              |
| --------------- | ----------------------- | ------------------------------------------ |
| **whisper**     | Audio transcription     | `plugin: whisper.transcribe "file.wav"`    |
| **git**         | Git integration         | `plugin: git.commit "message"`             |
| **search**      | Web search (DuckDuckGo) | `plugin: search.query "LLM agents"`        |
| **file_tools**  | File operations         | `plugin: file_tools.read "data.txt"`       |
| **local_llm**   | Local LLM integration   | `plugin: local_llm.chat "Hello"`           |
| **math_plugin** | Mathematical operations | `plugin: math_plugin.solve "x^2 + 2x + 1"` |
| **example**     | Example demonstrations  | `plugin: example.greet "Alice"`            |

## 🔒 Safety & Security

- **Input Validation**: Always validate and sanitize inputs
- **Error Handling**: Catch exceptions and return meaningful messages
- **File Safety**: Never overwrite critical files without confirmation
- **Shell Commands**: Avoid executing raw shell commands when possible
- **Permissions**: Check file/directory permissions before operations
- **Logging**: Use memory logging for transparency and debugging

### Security Example

```python
from core.security import require_user_approval

@register_plugin("file_manager")
def delete_file(filepath: str):
    # Validate input
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' not found"

    # Request approval for dangerous operations
    if not require_user_approval(f"Delete file '{filepath}'?"):
        return "Operation cancelled by user"

    try:
        os.remove(filepath)
        remember(f"Deleted file: {filepath}")
        return f"File '{filepath}' deleted successfully"
    except Exception as e:
        return f"Error deleting file: {str(e)}"
```

## 🧪 Testing Your Plugin

Create a test `.aether` file to verify your plugin:

```neuro
# test_plugin.aether
plugin: example.hello_world "Test"
plugin: example.greet "Developer"
plugin: example.calculate "5 + 3"
plugin: example.status
```

Run with Aetherra to test functionality.

## 🤝 Contributing Plugins

1. **Fork** the repository
2. **Add** your `.py` file to `/sdk/plugins/`
3. **Test** with sample `.aether` files
4. **Document** usage and capabilities
5. **Submit** a pull request with description

### Plugin Submission Checklist

- [ ] Plugin follows naming conventions
- [ ] All functions are properly documented
- [ ] Input validation is implemented
- [ ] Error handling is comprehensive
- [ ] Example usage is provided
- [ ] Security considerations are addressed
- [ ] Plugin is tested with sample `.aether` files

## 🔧 Advanced Features

### Memory System Integration

```python
from core.memory import remember, recall, forget

@register_plugin("advanced_example")
def remember_preference(key: str, value: str):
    remember(f"user_preference:{key}", value)
    return f"Remembered {key} = {value}"

def recall_preference(key: str):
    value = recall(f"user_preference:{key}")
    return f"{key} = {value}" if value else f"No preference set for {key}"
```

### AI Integration

```python
@register_plugin(
    name="ai_helper",
    ai_description="Helps with AI-related tasks and natural language processing",
    intent_triggers=["analyze", "understand", "explain"],
    intent_scenarios=["text analysis", "content generation"]
)
def analyze_text(text: str):
    # AI-powered text analysis
    return analysis_result
```

---

**Let Lyrixaevolve — one plugin at a time.** 🚀
