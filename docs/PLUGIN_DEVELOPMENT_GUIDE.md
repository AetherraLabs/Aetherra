# Aetherra Plugin Development Guide

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide covers everything you need to create, test, and deploy plugins for Aetherra OS. Plugins extend Aetherra's capabilities with custom functionality.

## Purpose and scope

- Understand Aetherra's plugin architecture
- Create your first plugin
- Implement different plugin types
- Test and debug plugins
- Package and distribute plugins
- Follow best practices and security guidelines

## What are Aetherra Plugins?

**Plugins** are modular extensions that add new capabilities to Aetherra OS. They can:

- **Process data** - Transform, analyze, or filter information
- **Integrate services** - Connect to external APIs and services
- **Extend UI** - Add custom panels and visualizations
- **Automate tasks** - Create workflows and scheduled operations
- **Enhance cognition** - Add reasoning and analysis capabilities

### Plugin Types

| Type                 | Purpose                          | Example                    |
| -------------------- | -------------------------------- | -------------------------- |
| **Python Plugin**    | Core logic in Python             | Data processors, analyzers |
| **Aetherplug**       | UI-enhanced with HTML/CSS/JS     | Dashboards, visualizations |
| **Service Plugin**   | Long-running background services | Monitoring, sync services  |
| **Transform Plugin** | Data transformation              | Formatters, converters     |
| **Bridge Plugin**    | External API integration         | Database connectors, APIs  |

---

## Quick Start

### Hello World Plugin

Create your first plugin in 5 minutes:

**1. Create plugin directory:**

```bash
mkdir -p Aetherra/plugins/hello_world
cd Aetherra/plugins/hello_world
```

**2. Create `hello_world.py`:**

```python
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Your Name

"""
Hello World Plugin
Simple example plugin for Aetherra OS
"""

class HelloWorldPlugin:
    """A simple hello world plugin."""

    def __init__(self):
        self.name = "hello_world"
        self.description = "Says hello to Aetherra"
        self.version = "1.0.0"

    def execute(self, name: str = "Aetherra") -> dict:
        """
        Say hello to someone.

        Args:
            name: Name to greet (default: "Aetherra")

        Returns:
            dict: Greeting message
        """
        message = f"Hello, {name}! Welcome to Aetherra OS."

        return {
            "ok": True,
            "message": message,
            "timestamp": self._get_timestamp()
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

# Required: Export plugin class
PLUGIN_CLASS = HelloWorldPlugin
```

**3. Create `plugin.json` manifest:**

```json
{
  "name": "hello_world",
  "version": "1.0.0",
  "description": "Says hello to Aetherra",
  "author": "Your Name",
  "entry": "Aetherra.plugins.hello_world.hello_world:HelloWorldPlugin",
  "category": "utility",
  "license": "GPL-3.0",
  "dependencies": {},
  "keywords": ["hello", "example", "tutorial"]
}
```

**4. Test your plugin:**

```python
# test_plugin.py
from Aetherra.plugins.hello_world.hello_world import HelloWorldPlugin

plugin = HelloWorldPlugin()
result = plugin.execute(name="Developer")
print(result)
# Output: {'ok': True, 'message': 'Hello, Developer! Welcome to Aetherra OS.', ...}
```

**5. Register with Aetherra:**

```bash
# Restart Aetherra OS to auto-discover
python aetherra_os_launcher.py
```

Your plugin is now available for use in Aether scripts!

---

## Plugin Architecture

### Plugin Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│                   Plugin Lifecycle                        │
└──────────────────────────────────────────────────────────┘

1. DISCOVERY
   ├─ Plugin Discovery Service scans Aetherra/plugins/
   ├─ Reads plugin.json manifest
   └─ Validates plugin structure

2. LOADING
   ├─ Import Python module
   ├─ Instantiate plugin class
   └─ Initialize plugin state

3. REGISTRATION
   ├─ Register with Plugin Manager
   ├─ Expose capabilities
   └─ Add to plugin catalog

4. EXECUTION
   ├─ Receive invocation request
   ├─ Execute plugin logic
   └─ Return results

5. CLEANUP
   ├─ Release resources
   ├─ Save state (if needed)
   └─ Unregister from manager
```

### Plugin Class Structure

Every plugin must implement a standard interface:

```python
class MyPlugin:
    """Plugin class structure."""

    def __init__(self):
        """Initialize plugin with metadata."""
        self.name = "my_plugin"
        self.description = "Plugin description"
        self.version = "1.0.0"

    def execute(self, *args, **kwargs) -> dict:
        """
        Main execution method.

        This is the primary entry point called by Aetherra.
        Must return a dictionary with at least {'ok': bool}.
        """
        # Your logic here
        return {"ok": True, "result": "data"}

    def get_status(self) -> dict:
        """Optional: Return plugin status."""
        return {
            "healthy": True,
            "version": self.version
        }

    def cleanup(self):
        """Optional: Cleanup resources before shutdown."""
        pass
```

---

## Plugin Manifest (plugin.json)

The `plugin.json` file describes your plugin:

### Minimal Manifest

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "What my plugin does",
  "author": "Your Name",
  "entry": "Aetherra.plugins.my_plugin.my_plugin:MyPlugin"
}
```

### Complete Manifest

```json
{
  "name": "advanced_plugin",
  "version": "2.1.0",
  "description": "Advanced data processing plugin",
  "author": "Your Name",
  "email": "you@example.com",
  "license": "GPL-3.0",
  "entry": "Aetherra.plugins.advanced_plugin.plugin:AdvancedPlugin",

  "category": "data_processing",
  "keywords": ["data", "transform", "analyze"],

  "aetherra_version": ">=3.0.0",
  "dependencies": {
    "pandas": ">=1.5.0",
    "numpy": ">=1.23.0"
  },

  "capabilities": [
    "transform",
    "analyze",
    "visualize"
  ],

  "permissions": [
    "read_memory",
    "write_memory",
    "network_access"
  ],

  "settings": {
    "default_timeout": 30,
    "max_batch_size": 1000,
    "cache_enabled": true
  },

  "repository": "https://github.com/yourname/advanced-plugin",
  "documentation": "https://docs.example.com/advanced-plugin",
  "homepage": "https://example.com/advanced-plugin"
}
```

### Manifest Fields

| Field          | Required | Description                                       |
| -------------- | -------- | ------------------------------------------------- |
| `name`         | Yes      | Unique plugin identifier (lowercase, underscores) |
| `version`      | Yes      | Semantic version (e.g., "1.0.0")                  |
| `description`  | Yes      | Brief description of functionality                |
| `author`       | Yes      | Plugin author name                                |
| `entry`        | Yes      | Python import path to plugin class                |
| `category`     | No       | Category for organization                         |
| `license`      | No       | License identifier (default: GPL-3.0)             |
| `dependencies` | No       | Python package dependencies                       |
| `capabilities` | No       | List of capabilities provided                     |
| `permissions`  | No       | Required system permissions                       |
| `settings`     | No       | Default configuration settings                    |

---

## Plugin Types in Detail

### 1. Data Processing Plugin

Process and transform data:

```python
class DataProcessorPlugin:
    """Process and transform data."""

    def __init__(self):
        self.name = "data_processor"
        self.description = "Data processing and transformation"
        self.version = "1.0.0"

    def execute(self, data: list, operation: str = "clean") -> dict:
        """
        Process data with specified operation.

        Args:
            data: List of items to process
            operation: Operation type (clean, transform, filter)

        Returns:
            dict: Processed data
        """
        if operation == "clean":
            result = self._clean_data(data)
        elif operation == "transform":
            result = self._transform_data(data)
        elif operation == "filter":
            result = self._filter_data(data)
        else:
            return {"ok": False, "error": "unknown_operation"}

        return {
            "ok": True,
            "data": result,
            "operation": operation,
            "count": len(result)
        }

    def _clean_data(self, data: list) -> list:
        """Remove invalid entries."""
        return [item for item in data if item and str(item).strip()]

    def _transform_data(self, data: list) -> list:
        """Transform data format."""
        return [str(item).upper() for item in data]

    def _filter_data(self, data: list) -> list:
        """Filter data by criteria."""
        return [item for item in data if len(str(item)) > 3]

PLUGIN_CLASS = DataProcessorPlugin
```

### 2. API Integration Plugin

Connect to external services:

```python
import requests
from typing import Optional

class APIBridgePlugin:
    """Bridge to external API."""

    def __init__(self):
        self.name = "api_bridge"
        self.description = "External API integration"
        self.version = "1.0.0"
        self.base_url = "https://api.example.com/v1"
        self.timeout = 30

    def execute(self, endpoint: str, method: str = "GET",
                data: Optional[dict] = None, **kwargs) -> dict:
        """
        Call external API.

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request payload (for POST/PUT)
            **kwargs: Additional request parameters

        Returns:
            dict: API response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method == "GET":
                response = requests.get(url, timeout=self.timeout, **kwargs)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=self.timeout, **kwargs)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=self.timeout, **kwargs)
            elif method == "DELETE":
                response = requests.delete(url, timeout=self.timeout, **kwargs)
            else:
                return {"ok": False, "error": "unsupported_method"}

            response.raise_for_status()

            return {
                "ok": True,
                "status_code": response.status_code,
                "data": response.json() if response.text else {},
                "headers": dict(response.headers)
            }

        except requests.exceptions.Timeout:
            return {"ok": False, "error": "timeout"}
        except requests.exceptions.RequestException as e:
            return {"ok": False, "error": str(e)}

PLUGIN_CLASS = APIBridgePlugin
```

### 3. Analysis Plugin

Analyze data and generate insights:

```python
from collections import Counter
from typing import Any, List

class DataAnalyzerPlugin:
    """Analyze data and generate insights."""

    def __init__(self):
        self.name = "data_analyzer"
        self.description = "Data analysis and insights"
        self.version = "1.0.0"

    def execute(self, data: List[Any], analysis_type: str = "summary") -> dict:
        """
        Analyze data.

        Args:
            data: Data to analyze
            analysis_type: Type of analysis (summary, frequency, patterns)

        Returns:
            dict: Analysis results
        """
        if analysis_type == "summary":
            results = self._summarize(data)
        elif analysis_type == "frequency":
            results = self._frequency_analysis(data)
        elif analysis_type == "patterns":
            results = self._pattern_analysis(data)
        else:
            return {"ok": False, "error": "unknown_analysis_type"}

        return {
            "ok": True,
            "analysis_type": analysis_type,
            "results": results,
            "confidence": self._calculate_confidence(results)
        }

    def _summarize(self, data: List[Any]) -> dict:
        """Generate summary statistics."""
        return {
            "count": len(data),
            "unique": len(set(data)),
            "sample": data[:5] if data else []
        }

    def _frequency_analysis(self, data: List[Any]) -> dict:
        """Analyze frequency distribution."""
        counter = Counter(data)
        return {
            "most_common": counter.most_common(10),
            "unique_count": len(counter)
        }

    def _pattern_analysis(self, data: List[Any]) -> dict:
        """Identify patterns in data."""
        # Simplified pattern detection
        patterns = {
            "has_duplicates": len(data) != len(set(data)),
            "is_sorted": data == sorted(data),
            "all_unique": len(data) == len(set(data))
        }
        return patterns

    def _calculate_confidence(self, results: dict) -> float:
        """Calculate confidence score for analysis."""
        # Simple confidence based on data quality
        return 0.95

PLUGIN_CLASS = DataAnalyzerPlugin
```

### 4. Memory-Integrated Plugin

Work with Aetherra's memory system:

```python
class MemoryPluginExample:
    """Plugin with memory system integration."""

    def __init__(self, memory_system=None):
        self.name = "memory_plugin"
        self.description = "Memory-integrated plugin"
        self.version = "1.0.0"
        self.memory = memory_system

    def execute(self, operation: str, **kwargs) -> dict:
        """
        Execute memory operations.

        Args:
            operation: Operation type (store, query, analyze)
            **kwargs: Operation-specific parameters

        Returns:
            dict: Operation results
        """
        if not self.memory:
            return {"ok": False, "error": "memory_not_available"}

        if operation == "store":
            return self._store_event(kwargs)
        elif operation == "query":
            return self._query_events(kwargs)
        elif operation == "analyze":
            return self._analyze_memory(kwargs)
        else:
            return {"ok": False, "error": "unknown_operation"}

    def _store_event(self, params: dict) -> dict:
        """Store event in memory."""
        event = params.get("event", {})
        tag = params.get("tag", "plugin_data")

        try:
            self.memory.store_event({
                **event,
                "source": self.name,
                "timestamp": self._get_timestamp()
            })

            return {"ok": True, "stored": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _query_events(self, params: dict) -> dict:
        """Query events from memory."""
        event_type = params.get("event_type")
        limit = params.get("limit", 10)

        try:
            events = self.memory.query_events(
                event_type=event_type,
                limit=limit
            )

            return {
                "ok": True,
                "events": events,
                "count": len(events)
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _analyze_memory(self, params: dict) -> dict:
        """Analyze memory patterns."""
        # Analyze recent events
        events = self.memory.query_events(limit=100)

        analysis = {
            "total_events": len(events),
            "event_types": len(set(e.get("type") for e in events)),
            "time_range": self._calculate_time_range(events)
        }

        return {"ok": True, "analysis": analysis}

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def _calculate_time_range(self, events: list) -> dict:
        if not events:
            return {}
        # Simplified time range calculation
        return {"events": len(events)}

PLUGIN_CLASS = MemoryPluginExample
```

---

## Aetherplug Format (UI Plugins)

Create plugins with custom UI panels:

### Directory Structure

```
my_ui_plugin/
├── aetherra-plugin.json    # Manifest
├── plugin.py               # Backend logic
├── panel.html             # UI template
├── styles.css             # Styling
└── script.js              # Frontend logic
```

### aetherra-plugin.json

```json
{
  "id": "my_ui_plugin",
  "name": "My UI Plugin",
  "version": "1.0.0",
  "description": "Plugin with custom UI",
  "author": "Your Name",

  "ui_panel": "panel.html",
  "panel_title": "🎨 My Panel",
  "panel_type": "widget",
  "panel_size": "medium",

  "update_frequency": 1000,
  "css_files": ["styles.css"],
  "js_files": ["script.js"],

  "capabilities": ["visualization", "monitoring"],
  "permissions": ["read_system_stats"],

  "settings": {
    "refresh_rate": 1000,
    "show_graphs": true
  }
}
```

### panel.html

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Plugin Panel</title>
</head>
<body>
    <div class="plugin-container">
        <h2>My Plugin Dashboard</h2>
        <div id="data-display"></div>
        <button onclick="refreshData()">Refresh</button>
    </div>

    <script>
        async function refreshData() {
            const response = await fetch('/api/plugins/my_ui_plugin/data');
            const data = await response.json();
            document.getElementById('data-display').textContent =
                JSON.stringify(data, null, 2);
        }

        // Auto-refresh
        setInterval(refreshData, 1000);
        refreshData();
    </script>
</body>
</html>
```

---

## Testing Plugins

### Unit Testing

```python
# test_my_plugin.py
import pytest
from Aetherra.plugins.my_plugin.my_plugin import MyPlugin

def test_plugin_initialization():
    """Test plugin initializes correctly."""
    plugin = MyPlugin()
    assert plugin.name == "my_plugin"
    assert plugin.version == "1.0.0"

def test_plugin_execution():
    """Test plugin executes successfully."""
    plugin = MyPlugin()
    result = plugin.execute(data="test")

    assert result["ok"] is True
    assert "result" in result

def test_plugin_error_handling():
    """Test plugin handles errors gracefully."""
    plugin = MyPlugin()
    result = plugin.execute(invalid_param=123)

    assert result["ok"] is False
    assert "error" in result

@pytest.mark.parametrize("input_data,expected", [
    ("hello", {"ok": True}),
    ("", {"ok": False}),
    (None, {"ok": False}),
])
def test_plugin_with_various_inputs(input_data, expected):
    """Test plugin with different inputs."""
    plugin = MyPlugin()
    result = plugin.execute(data=input_data)
    assert result["ok"] == expected["ok"]
```

### Integration Testing

```python
# test_plugin_integration.py
import pytest
from aetherra_plugin_discovery import AetherraPluginDiscovery

@pytest.mark.integration
def test_plugin_discovery():
    """Test plugin is discovered by plugin system."""
    discovery = AetherraPluginDiscovery()
    plugins = await discovery.discover_all_plugins()

    assert "my_plugin" in plugins
    assert plugins["my_plugin"].version == "1.0.0"

@pytest.mark.integration
def test_plugin_invocation():
    """Test plugin can be invoked through plugin manager."""
    from aetherra_plugin_manager import PluginManager

    manager = PluginManager()
    result = await manager.invoke_plugin("my_plugin", data="test")

    assert result["ok"] is True
```

### Manual Testing

```python
# manual_test.py
"""Manual testing script for plugin development."""

from Aetherra.plugins.my_plugin.my_plugin import MyPlugin

def main():
    print("=== Plugin Manual Test ===")

    # Initialize plugin
    plugin = MyPlugin()
    print(f"Plugin: {plugin.name} v{plugin.version}")
    print(f"Description: {plugin.description}")

    # Test basic execution
    print("\n--- Test 1: Basic Execution ---")
    result = plugin.execute(data="test_data")
    print(f"Result: {result}")

    # Test with different parameters
    print("\n--- Test 2: Different Parameters ---")
    result = plugin.execute(data="test", option="value")
    print(f"Result: {result}")

    # Test error handling
    print("\n--- Test 3: Error Handling ---")
    result = plugin.execute()  # No parameters
    print(f"Result: {result}")

    print("\n=== Tests Complete ===")

if __name__ == "__main__":
    main()
```

---

## Best Practices

### Code Quality

✅ **Follow Python style guidelines:**

```python
# Good: Clear, documented, typed
class DataProcessor:
    """Process and clean data."""

    def process(self, data: list[str], mode: str = "clean") -> dict:
        """
        Process data with specified mode.

        Args:
            data: Input data list
            mode: Processing mode (clean, transform)

        Returns:
            dict: Processed results
        """
        # Implementation
        pass

# Bad: Unclear, undocumented
class dp:
    def p(self, d, m="c"):
        # what does this do?
        pass
```

✅ **Use descriptive names:**

```python
# Good
def analyze_customer_behavior(events: list) -> dict:
    pass

# Bad
def acb(e: list) -> dict:
    pass
```

✅ **Handle errors gracefully:**

```python
def execute(self, **kwargs) -> dict:
    try:
        result = self._process(kwargs)
        return {"ok": True, "result": result}
    except ValueError as e:
        return {"ok": False, "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Plugin execution failed: {e}")
        return {"ok": False, "error": "internal_error"}
```

### Security

✅ **Validate all inputs:**

```python
def execute(self, data: Any, **kwargs) -> dict:
    # Validate data type
    if not isinstance(data, (str, list, dict)):
        return {"ok": False, "error": "invalid_data_type"}

    # Validate data size
    if isinstance(data, (list, dict)) and len(data) > 10000:
        return {"ok": False, "error": "data_too_large"}

    # Sanitize strings
    if isinstance(data, str):
        data = data.strip()[:1000]  # Limit length

    # Process validated data
    return self._process(data)
```

✅ **Use environment variables for secrets:**

```python
import os

class APIPlugin:
    def __init__(self):
        # Good: Load from environment
        self.api_key = os.environ.get("API_KEY", "")

        # Bad: Hardcoded
        # self.api_key = "secret123"
```

✅ **Implement timeouts:**

```python
import requests

def fetch_data(self, url: str) -> dict:
    try:
        response = requests.get(url, timeout=30)  # 30 second timeout
        return {"ok": True, "data": response.json()}
    except requests.Timeout:
        return {"ok": False, "error": "timeout"}
```

### Performance

✅ **Cache expensive operations:**

```python
from functools import lru_cache

class OptimizedPlugin:
    @lru_cache(maxsize=128)
    def expensive_calculation(self, param: str) -> int:
        # Cached result for repeated calls
        return complex_calculation(param)
```

✅ **Use generators for large datasets:**

```python
def process_large_dataset(self, data: list) -> dict:
    # Bad: Loads everything into memory
    # results = [self.process_item(item) for item in data]

    # Good: Generator for memory efficiency
    results = (self.process_item(item) for item in data)
    return {"ok": True, "results": list(results)}
```

✅ **Implement progress reporting:**

```python
def execute(self, items: list, progress_callback=None) -> dict:
    results = []
    total = len(items)

    for i, item in enumerate(items):
        result = self.process_item(item)
        results.append(result)

        # Report progress
        if progress_callback and i % 10 == 0:
            progress_callback(i / total)

    return {"ok": True, "results": results}
```

---

## Packaging and Distribution

### Package Structure

```
my_plugin_package/
├── Aetherra/
│   └── plugins/
│       └── my_plugin/
│           ├── __init__.py
│           ├── my_plugin.py
│           └── plugin.json
├── tests/
│   ├── test_my_plugin.py
│   └── test_integration.py
├── docs/
│   ├── README.md
│   └── USAGE.md
├── setup.py
├── requirements.txt
├── LICENSE
└── README.md
```

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="aetherra-my-plugin",
    version="1.0.0",
    description="My custom Aetherra plugin",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/yourname/my-plugin",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
)
```

### Publishing

```bash
# 1. Build package
python setup.py sdist bdist_wheel

# 2. Test installation
pip install dist/aetherra-my-plugin-1.0.0.tar.gz

# 3. Publish to PyPI (optional)
twine upload dist/*
```

---

## Related Documentation

- [AETHER_SCRIPT_TUTORIAL.md](./AETHER_SCRIPT_TUTORIAL.md) - Use plugins in scripts
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Test your plugins
- [AETHERRA_MEMORY_SYSTEM.md](./AETHERRA_MEMORY_SYSTEM.md) - Memory integration
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Debug plugins
- [AETHERRA_HUB_API_REFERENCE.md](./AETHERRA_HUB_API_REFERENCE.md) - Plugin APIs

---

Status: ✅ Complete - Comprehensive plugin development guide from basics to advanced

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
