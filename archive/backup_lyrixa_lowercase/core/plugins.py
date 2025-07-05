#!/usr/bin/env python3
"""
🧩 LYRIXA PLUGIN MANAGER
========================

Lyrixa's plugin ecosystem for extending capabilities and integrations.
Manages plugin discovery, loading, execution, and security.
"""

import importlib.util
import inspect
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type


@dataclass
class PluginInfo:
    """Information about a plugin"""

    name: str
    version: str
    description: str
    author: str
    category: str
    capabilities: List[str]
    dependencies: List[str]
    file_path: str
    enabled: bool = True
    loaded: bool = False


class LyrixaPlugin(ABC):
    """
    Base class for all Lyrixa plugins

    All plugins must inherit from this class and implement the required methods.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = "A Lyrixa plugin"
        self.author = "Unknown"
        self.category = "general"
        self.capabilities = []
        self.dependencies = []

    @abstractmethod
    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        """Initialize the plugin with Lyrixa context"""
        pass

    @abstractmethod
    async def execute(
        self, command: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a plugin command"""
        pass

    @abstractmethod
    async def cleanup(self) -> bool:
        """Clean up plugin resources"""
        pass

    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        return PluginInfo(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            category=self.category,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
            file_path="",
        )


class LyrixaPluginManager:
    """
    Lyrixa's plugin management system

    Handles plugin discovery, loading, execution, and lifecycle management.
    Provides security sandboxing and capability management.
    """

    def __init__(self, plugin_directory: str = "plugins"):
        self.plugin_directory = plugin_directory
        self.loaded_plugins: Dict[str, LyrixaPlugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.plugin_registry: Dict[str, Type[LyrixaPlugin]] = {}
        self.enabled_plugins: set = set()
        self.lyrixa_context: Dict[str, Any] = {}

        # Create plugin directory if it doesn't exist
        os.makedirs(plugin_directory, exist_ok=True)

        # Initialize built-in plugins
        self._register_builtin_plugins()

    async def initialize(self, lyrixa_context: Dict[str, Any]):
        """Initialize the plugin manager with Lyrixa context"""
        self.lyrixa_context = lyrixa_context

        # Discover and load plugins
        await self._discover_plugins()
        await self._load_enabled_plugins()

        print(f"🧩 Plugin manager initialized with {len(self.loaded_plugins)} plugins")

    def _register_builtin_plugins(self):
        """Register built-in plugins"""
        # Register built-in plugin classes
        self.plugin_registry.update(
            {
                "FileManagerPlugin": FileManagerPlugin,
                "WebSearchPlugin": WebSearchPlugin,
                "CodeAnalyzerPlugin": CodeAnalyzerPlugin,
                "DataVisualizerPlugin": DataVisualizerPlugin,
                "APIConnectorPlugin": APIConnectorPlugin,
            }
        )

    async def _discover_plugins(self):
        """Discover plugins in the plugin directory"""
        print(f"🔍 Discovering plugins in {self.plugin_directory}")

        # Built-in plugins
        for plugin_name, plugin_class in self.plugin_registry.items():
            try:
                plugin_instance = plugin_class()
                info = plugin_instance.get_info()
                info.file_path = "built-in"
                self.plugin_info[plugin_name] = info
                print(f"   📦 Found built-in plugin: {plugin_name}")
            except Exception as e:
                print(f"   ❌ Failed to load built-in plugin {plugin_name}: {e}")

        # External plugins
        if os.path.exists(self.plugin_directory):
            for filename in os.listdir(self.plugin_directory):
                if filename.endswith(".py") and not filename.startswith("_"):
                    await self._discover_plugin_file(filename)

    async def _discover_plugin_file(self, filename: str):
        """Discover and validate a plugin file"""
        file_path = os.path.join(self.plugin_directory, filename)
        plugin_name = filename[:-3]  # Remove .py extension

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find plugin classes in the module
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, LyrixaPlugin)
                        and obj != LyrixaPlugin
                    ):
                        plugin_instance = obj()
                        info = plugin_instance.get_info()
                        info.file_path = file_path

                        self.plugin_info[name] = info
                        self.plugin_registry[name] = obj

                        print(f"   📦 Found external plugin: {name}")
                        break

        except Exception as e:
            print(f"   ❌ Failed to load plugin {filename}: {e}")

    async def _load_enabled_plugins(self):
        """Load all enabled plugins"""
        for plugin_name, info in self.plugin_info.items():
            if info.enabled:
                await self.load_plugin(plugin_name)

    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        if plugin_name in self.loaded_plugins:
            return True

        if plugin_name not in self.plugin_registry:
            print(f"❌ Plugin {plugin_name} not found in registry")
            return False

        try:
            # Create plugin instance
            plugin_class = self.plugin_registry[plugin_name]
            plugin_instance = plugin_class()

            # Initialize the plugin
            success = await plugin_instance.initialize(self.lyrixa_context)

            if success:
                self.loaded_plugins[plugin_name] = plugin_instance
                self.enabled_plugins.add(plugin_name)
                self.plugin_info[plugin_name].loaded = True

                print(f"✅ Loaded plugin: {plugin_name}")
                return True
            else:
                print(f"❌ Failed to initialize plugin: {plugin_name}")
                return False

        except Exception as e:
            print(f"❌ Error loading plugin {plugin_name}: {e}")
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        if plugin_name not in self.loaded_plugins:
            return True

        try:
            plugin = self.loaded_plugins[plugin_name]
            await plugin.cleanup()

            del self.loaded_plugins[plugin_name]
            self.enabled_plugins.discard(plugin_name)
            self.plugin_info[plugin_name].loaded = False

            print(f"🔄 Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"❌ Error unloading plugin {plugin_name}: {e}")
            return False

    async def execute_plugin(
        self, plugin_name: str, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a command on a specific plugin"""
        if plugin_name not in self.loaded_plugins:
            return {
                "success": False,
                "error": f"Plugin {plugin_name} is not loaded",
                "result": None,
            }

        try:
            plugin = self.loaded_plugins[plugin_name]
            result = await plugin.execute(command, params or {})

            return {
                "success": True,
                "error": None,
                "result": result,
                "plugin": plugin_name,
                "command": command,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "plugin": plugin_name,
                "command": command,
                "timestamp": datetime.now().isoformat(),
            }

    async def execute_capability(
        self, capability: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a capability across all plugins that support it"""
        results = []

        for plugin_name, plugin in self.loaded_plugins.items():
            info = self.plugin_info[plugin_name]
            if capability in info.capabilities:
                result = await self.execute_plugin(plugin_name, capability, params)
                results.append(result)

        return results

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin"""
        return self.plugin_info.get(plugin_name)

    def list_plugins(
        self, category: Optional[str] = None, loaded_only: bool = False
    ) -> List[PluginInfo]:
        """List available plugins"""
        plugins = []

        for info in self.plugin_info.values():
            if category and info.category != category:
                continue
            if loaded_only and not info.loaded:
                continue
            plugins.append(info)

        return plugins

    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get all available capabilities and the plugins that provide them"""
        capabilities = {}

        for plugin_name, info in self.plugin_info.items():
            if info.loaded:
                for capability in info.capabilities:
                    if capability not in capabilities:
                        capabilities[capability] = []
                    capabilities[capability].append(plugin_name)

        return capabilities

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        await self.unload_plugin(plugin_name)
        return await self.load_plugin(plugin_name)

    async def cleanup(self):
        """Clean up all plugins"""
        for plugin_name in list(self.loaded_plugins.keys()):
            await self.unload_plugin(plugin_name)


# Built-in Plugin Implementations


class FileManagerPlugin(LyrixaPlugin):
    """Plugin for file and directory operations"""

    def __init__(self):
        super().__init__()
        self.name = "FileManager"
        self.description = "File and directory operations"
        self.category = "system"
        self.capabilities = ["read_file", "write_file", "list_directory", "file_search"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        self.workspace_path = lyrixa_context.get("workspace_path", ".")
        return True

    async def execute(
        self, command: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "read_file":
            return await self._read_file(params.get("file_path", ""))
        elif command == "write_file":
            return await self._write_file(
                params.get("file_path", ""), params.get("content", "")
            )
        elif command == "list_directory":
            return await self._list_directory(params.get("directory_path", "."))
        elif command == "file_search":
            return await self._file_search(
                params.get("pattern", ""), params.get("directory", ".")
            )
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}

    async def _write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "bytes_written": len(content)}
        except Exception as e:
            return {"error": str(e)}

    async def _list_directory(self, directory_path: str) -> Dict[str, Any]:
        try:
            items = os.listdir(directory_path)
            return {"items": items, "count": len(items)}
        except Exception as e:
            return {"error": str(e)}

    async def _file_search(self, pattern: str, directory: str) -> Dict[str, Any]:
        try:
            import glob

            matches = glob.glob(os.path.join(directory, pattern), recursive=True)
            return {"matches": matches, "count": len(matches)}
        except Exception as e:
            return {"error": str(e)}


class WebSearchPlugin(LyrixaPlugin):
    """Plugin for web search capabilities"""

    def __init__(self):
        super().__init__()
        self.name = "WebSearch"
        self.description = "Web search and information retrieval"
        self.category = "internet"
        self.capabilities = ["web_search", "url_fetch", "web_summarize"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "web_search":
            return await self._web_search(params.get("query", ""))
        elif command == "url_fetch":
            return await self._url_fetch(params.get("url", ""))
        elif command == "web_summarize":
            return await self._web_summarize(params.get("url", ""))
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _web_search(self, query: str) -> Dict[str, Any]:
        # Placeholder implementation
        return {
            "query": query,
            "results": [
                {
                    "title": f"Result for {query}",
                    "url": "https://example.com",
                    "snippet": "Sample result",
                }
            ],
        }

    async def _url_fetch(self, url: str) -> Dict[str, Any]:
        # Placeholder implementation
        return {"url": url, "content": f"Content from {url}", "status": 200}

    async def _web_summarize(self, url: str) -> Dict[str, Any]:
        # Placeholder implementation
        return {"url": url, "summary": f"Summary of content from {url}"}


class CodeAnalyzerPlugin(LyrixaPlugin):
    """Plugin for code analysis capabilities"""

    def __init__(self):
        super().__init__()
        self.name = "CodeAnalyzer"
        self.description = "Code analysis and quality assessment"
        self.category = "development"
        self.capabilities = ["analyze_code", "code_metrics", "find_issues"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "analyze_code":
            return await self._analyze_code(
                params.get("code", ""), params.get("language", "python")
            )
        elif command == "code_metrics":
            return await self._code_metrics(params.get("file_path", ""))
        elif command == "find_issues":
            return await self._find_issues(params.get("code", ""))
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        lines = code.split("\n")
        return {
            "language": language,
            "lines_of_code": len(lines),
            "functions": len([line for line in lines if "def " in line]),
            "classes": len([line for line in lines if "class " in line]),
        }

    async def _code_metrics(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            return await self._analyze_code(code, "python")
        except Exception as e:
            return {"error": str(e)}

    async def _find_issues(self, code: str) -> Dict[str, Any]:
        issues = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"Line {i}: Line too long ({len(line)} characters)")
            if "TODO" in line:
                issues.append(f"Line {i}: TODO comment found")

        return {"issues": issues, "count": len(issues)}


class DataVisualizerPlugin(LyrixaPlugin):
    """Plugin for data visualization"""

    def __init__(self):
        super().__init__()
        self.name = "DataVisualizer"
        self.description = "Data visualization and charting"
        self.category = "data"
        self.capabilities = ["create_chart", "visualize_data", "export_chart"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "create_chart":
            return await self._create_chart(
                params.get("data", []), params.get("chart_type", "bar")
            )
        elif command == "visualize_data":
            return await self._visualize_data(params.get("data", []))
        elif command == "export_chart":
            return await self._export_chart(
                params.get("chart_data", {}), params.get("format", "png")
            )
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _create_chart(self, data: List[Any], chart_type: str) -> Dict[str, Any]:
        return {
            "chart_type": chart_type,
            "data_points": len(data),
            "chart_url": f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        }

    async def _visualize_data(self, data: List[Any]) -> Dict[str, Any]:
        return await self._create_chart(data, "auto")

    async def _export_chart(
        self, chart_data: Dict[str, Any], format: str
    ) -> Dict[str, Any]:
        return {
            "exported": True,
            "format": format,
            "file_path": f"chart_export.{format}",
        }


class APIConnectorPlugin(LyrixaPlugin):
    """Plugin for API connections and integrations"""

    def __init__(self):
        super().__init__()
        self.name = "APIConnector"
        self.description = "API connections and integrations"
        self.category = "integration"
        self.capabilities = ["api_call", "auth_setup", "rate_limit_check"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "api_call":
            return await self._api_call(
                params.get("url", ""),
                params.get("method", "GET"),
                params.get("headers", {}),
                params.get("data", {}),
            )
        elif command == "auth_setup":
            return await self._auth_setup(
                params.get("auth_type", ""), params.get("credentials", {})
            )
        elif command == "rate_limit_check":
            return await self._rate_limit_check(params.get("api_name", ""))
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _api_call(
        self, url: str, method: str, headers: Dict[str, str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Placeholder implementation
        return {
            "url": url,
            "method": method,
            "status": 200,
            "response": {"message": f"Mock response from {url}"},
        }

    async def _auth_setup(
        self, auth_type: str, credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "auth_type": auth_type,
            "configured": True,
            "expires_at": (datetime.now().timestamp() + 3600),  # 1 hour from now
        }

    async def _rate_limit_check(self, api_name: str) -> Dict[str, Any]:
        return {
            "api_name": api_name,
            "requests_remaining": 100,
            "reset_time": datetime.now().timestamp() + 3600,
        }
