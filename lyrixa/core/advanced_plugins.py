#!/usr/bin/env python3
"""
🧩 LYRIXA ADVANCED PLUGIN ECOSYSTEM
===================================

Enhanced plugin system with auto-discovery, chaining, scaffolding,
and intelligent routing based on natural language intent.
"""

import asyncio
import importlib
import importlib.util
import inspect
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class PluginType(Enum):
    UTILITY = "utility"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    INTEGRATION = "integration"
    AUTOMATION = "automation"
    ENHANCEMENT = "enhancement"


class PluginStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    LOADING = "loading"
    DEPRECATED = "deprecated"


@dataclass
class PluginMetadata:
    """Enhanced metadata for plugins"""

    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    tags: List[str]
    dependencies: List[str]
    capabilities: List[str]
    usage_examples: List[str]
    configuration_schema: Dict[str, Any]
    performance_metrics: Dict[str, float]
    compatibility: Dict[str, str]
    documentation_url: str
    last_updated: str
    usage_count: int = 0
    success_rate: float = 1.0
    average_execution_time: float = 0.0


@dataclass
class PluginExecution:
    """Tracks plugin execution details"""

    plugin_name: str
    input_data: Any
    output_data: Any
    execution_time: float
    success: bool
    error_message: Optional[str]
    timestamp: str
    context: Dict[str, Any]


@dataclass
class PluginChain:
    """Defines a chain of plugin executions"""

    name: str
    description: str
    plugins: List[Dict[str, Any]]  # [{plugin: name, config: {}, input_transform: func}]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    created_by: str
    usage_count: int = 0


class LyrixaAdvancedPluginManager:
    """
    Advanced plugin management system for Lyrixa

    Features:
    - Auto-discovery and dynamic loading
    - Plugin chaining and workflow creation
    - Natural language plugin scaffolding
    - Performance monitoring and optimization
    - Intelligent routing based on intent
    """

    def __init__(
        self,
        plugin_directory: str = "plugins",
        memory_system=None,
        additional_directories: Optional[List[str]] = None,
    ):
        self.plugin_directory = Path(plugin_directory)
        self.additional_directories = [Path(d) for d in (additional_directories or [])]
        self.all_plugin_directories = [
            self.plugin_directory
        ] + self.additional_directories
        self.memory_system = memory_system

        # Plugin registry
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_instances: Dict[str, Any] = {}

        # Execution tracking
        self.execution_history: List[PluginExecution] = []
        self.plugin_chains: Dict[str, PluginChain] = {}

        # Auto-discovery
        self.auto_discovery_enabled = True
        self.load_order = []

        # Performance monitoring
        self.performance_stats = {}

        print("🧩 Lyrixa Advanced Plugin Manager initialized")

    async def initialize(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the plugin system with auto-discovery"""
        print("🔄 Initializing advanced plugin ecosystem...")

        # Create plugin directory if it doesn't exist
        self.plugin_directory.mkdir(exist_ok=True)

        # Auto-discover plugins
        if self.auto_discovery_enabled:
            await self._auto_discover_plugins()

        # Load plugin chains from memory
        await self._load_plugin_chains()

        # Initialize performance monitoring
        await self._initialize_performance_monitoring()

        print(f"✅ Plugin ecosystem ready: {len(self.plugins)} plugins loaded")

    async def _auto_discover_plugins(self):
        """Automatically discover and register plugins from all configured directories"""
        print("🔍 Auto-discovering plugins...")

        discovered_count = 0

        # Scan all plugin directories
        for plugin_dir in self.all_plugin_directories:
            if not plugin_dir.exists():
                print(f"   📂 Directory not found: {plugin_dir}")
                continue

            print(f"   📁 Scanning: {plugin_dir}")

            # Scan for Python files
            for plugin_file in plugin_dir.glob("*.py"):
                if plugin_file.name.startswith("__"):
                    continue

                try:
                    await self._load_plugin_from_file(plugin_file)
                    discovered_count += 1
                except Exception as e:
                    print(f"⚠️ Failed to load plugin {plugin_file.name}: {e}")

            # Scan for plugin packages
            for plugin_subdir in plugin_dir.iterdir():
                if plugin_subdir.is_dir() and not plugin_subdir.name.startswith("__"):
                    init_file = plugin_subdir / "__init__.py"
                    if init_file.exists():
                        try:
                            await self._load_plugin_from_package(plugin_subdir)
                            discovered_count += 1
                        except Exception as e:
                            print(
                                f"⚠️ Failed to load plugin package {plugin_subdir.name}: {e}"
                            )

        print(f"🔍 Auto-discovery complete: {discovered_count} plugins found")

    async def _load_plugin_from_file(self, plugin_file: Path):
        """Load a plugin from a Python file"""
        plugin_name = plugin_file.stem

        # Dynamic import
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        if spec is None:
            raise ImportError("Module specification could not be found.")

        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ImportError("Spec loader is not defined.")

        spec.loader.exec_module(module)

        # Extract plugin metadata and functions
        metadata = await self._extract_plugin_metadata(module, plugin_name)

        # Register plugin
        self.plugins[plugin_name] = {
            "module": module,
            "file_path": str(plugin_file),
            "status": PluginStatus.ACTIVE,
            "functions": self._extract_plugin_functions(module),
        }

        self.plugin_metadata[plugin_name] = metadata
        print(f"✅ Loaded plugin: {plugin_name}")

    async def _load_plugin_from_package(self, plugin_dir: Path):
        """Load a plugin from a Python package"""
        plugin_name = plugin_dir.name

        # Add to Python path temporarily
        import sys

        sys.path.insert(0, str(self.plugin_directory))

        try:
            module = importlib.import_module(plugin_name)

            # Extract plugin metadata and functions
            metadata = await self._extract_plugin_metadata(module, plugin_name)

            # Register plugin
            self.plugins[plugin_name] = {
                "module": module,
                "package_path": str(plugin_dir),
                "status": PluginStatus.ACTIVE,
                "functions": self._extract_plugin_functions(module),
            }

            self.plugin_metadata[plugin_name] = metadata
            print(f"✅ Loaded plugin package: {plugin_name}")

        finally:
            sys.path.remove(str(self.plugin_directory))

    async def _extract_plugin_metadata(
        self, module, plugin_name: str
    ) -> PluginMetadata:
        """Extract metadata from a plugin module"""

        # Default metadata
        metadata = PluginMetadata(
            name=plugin_name,
            version=getattr(module, "__version__", "1.0.0"),
            description=getattr(module, "__description__", f"Plugin: {plugin_name}"),
            author=getattr(module, "__author__", "Unknown"),
            plugin_type=PluginType(getattr(module, "__plugin_type__", "utility")),
            tags=getattr(module, "__tags__", []),
            dependencies=getattr(module, "__dependencies__", []),
            capabilities=getattr(module, "__capabilities__", []),
            usage_examples=getattr(module, "__examples__", []),
            configuration_schema=getattr(module, "__config_schema__", {}),
            performance_metrics=getattr(module, "__performance_metrics__", {}),
            compatibility=getattr(module, "__compatibility__", {}),
            documentation_url=getattr(module, "__docs__", ""),
            last_updated=getattr(module, "__updated__", ""),
        )

        return metadata

    def _extract_plugin_functions(self, module) -> Dict[str, Callable]:
        """Extract callable functions from a plugin module"""
        functions = {}

        for name, obj in inspect.getmembers(module):
            if (
                inspect.isfunction(obj)
                and not name.startswith("_")
                and hasattr(obj, "__call__")
            ):
                functions[name] = obj

        return functions

    async def route_intent_to_plugins(
        self, intent: str, user_input: str, context: Dict[str, Any]
    ) -> List[str]:
        """Intelligently route user intent to appropriate plugins"""
        suitable_plugins = []

        # Intent-based routing
        intent_mappings = {
            "file_analysis": ["file_analyzer", "code_scanner", "document_reader"],
            "code_generation": ["code_generator", "template_engine", "scaffolder"],
            "text_processing": ["text_processor", "summarizer", "translator"],
            "data_analysis": ["data_analyzer", "csv_processor", "json_parser"],
            "web_integration": ["web_scraper", "api_client", "browser_automation"],
            "automation": ["task_automator", "workflow_engine", "scheduler"],
        }

        # Check direct mappings
        for intent_type, plugin_names in intent_mappings.items():
            if intent_type in intent.lower():
                for plugin_name in plugin_names:
                    if plugin_name in self.plugins:
                        suitable_plugins.append(plugin_name)

        # Capability-based matching
        intent_keywords = intent.lower().split()
        for plugin_name, metadata in self.plugin_metadata.items():
            capability_match = any(
                keyword in " ".join(metadata.capabilities).lower()
                for keyword in intent_keywords
            )
            tag_match = any(
                keyword in " ".join(metadata.tags).lower()
                for keyword in intent_keywords
            )

            if capability_match or tag_match:
                if plugin_name not in suitable_plugins:
                    suitable_plugins.append(plugin_name)

        # Sort by performance and usage
        suitable_plugins.sort(
            key=lambda p: (
                self.plugin_metadata[p].success_rate,
                -self.plugin_metadata[p].average_execution_time,
                self.plugin_metadata[p].usage_count,
            ),
            reverse=True,
        )

        return suitable_plugins[:5]  # Return top 5 matches

    async def execute_plugin(
        self, plugin_name: str, function_name: str, *args, **kwargs
    ) -> PluginExecution:
        """Execute a specific plugin function with tracking"""
        start_time = asyncio.get_event_loop().time()

        execution = PluginExecution(
            plugin_name=plugin_name,
            input_data={"args": args, "kwargs": kwargs},
            output_data=None,
            execution_time=0.0,
            success=False,
            error_message=None,
            timestamp=str(asyncio.get_event_loop().time()),
            context={},
        )

        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"Plugin '{plugin_name}' not found")

            plugin = self.plugins[plugin_name]
            if function_name not in plugin["functions"]:
                raise ValueError(
                    f"Function '{function_name}' not found in plugin '{plugin_name}'"
                )

            # Execute function
            func = plugin["functions"][function_name]
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            execution.output_data = result
            execution.success = True

            # Update plugin usage stats
            self.plugin_metadata[plugin_name].usage_count += 1

        except Exception as e:
            execution.error_message = str(e)
            execution.success = False

        finally:
            execution.execution_time = asyncio.get_event_loop().time() - start_time

            # Update performance metrics
            metadata = self.plugin_metadata[plugin_name]
            if execution.success:
                # Update average execution time
                total_time = metadata.average_execution_time * (
                    metadata.usage_count - 1
                )
                metadata.average_execution_time = (
                    total_time + execution.execution_time
                ) / metadata.usage_count

                # Update success rate
                successful_executions = metadata.usage_count * metadata.success_rate
                metadata.success_rate = (successful_executions + 1) / (
                    metadata.usage_count + 1
                )
            else:
                # Update success rate for failed execution
                successful_executions = metadata.usage_count * metadata.success_rate
                metadata.success_rate = successful_executions / (
                    metadata.usage_count + 1
                )

        self.execution_history.append(execution)
        return execution

    async def create_plugin_chain(
        self, chain_name: str, description: str, plugin_sequence: List[Dict[str, Any]]
    ) -> PluginChain:
        """Create a new plugin execution chain"""
        chain = PluginChain(
            name=chain_name,
            description=description,
            plugins=plugin_sequence,
            input_schema={},
            output_schema={},
            created_by="user",
        )

        self.plugin_chains[chain_name] = chain

        # Store in memory system
        if self.memory_system:
            await self.memory_system.store_memory(
                content={"plugin_chain": asdict(chain)},
                context={"type": "plugin_chain", "name": chain_name},
                tags=["plugin", "chain", "workflow"],
                importance=0.8,
            )

        print(f"✅ Created plugin chain: {chain_name}")
        return chain

    async def execute_plugin_chain(
        self, chain_name: str, initial_input: Any
    ) -> Dict[str, Any]:
        """Execute a plugin chain"""
        if chain_name not in self.plugin_chains:
            raise ValueError(f"Plugin chain '{chain_name}' not found")

        chain = self.plugin_chains[chain_name]
        current_data = initial_input
        execution_log = []

        for step_config in chain.plugins:
            plugin_name = step_config["plugin"]
            function_name = step_config.get("function", "main")
            config = step_config.get("config", {})

            # Apply input transformation if specified
            if "input_transform" in step_config:
                transform_func = step_config["input_transform"]
                current_data = transform_func(current_data)

            # Execute plugin
            execution = await self.execute_plugin(
                plugin_name, function_name, current_data, **config
            )

            execution_log.append(
                {
                    "step": len(execution_log) + 1,
                    "plugin": plugin_name,
                    "function": function_name,
                    "success": execution.success,
                    "execution_time": execution.execution_time,
                    "error": execution.error_message,
                }
            )

            if not execution.success:
                break

            current_data = execution.output_data

        # Update chain usage
        chain.usage_count += 1

        return {
            "chain_name": chain_name,
            "final_output": current_data,
            "execution_log": execution_log,
            "success": all(step["success"] for step in execution_log),
            "total_time": sum(step["execution_time"] for step in execution_log),
        }

    def execute_chain(self, user_message: str) -> str:
        """Execute a chain of plugins based on the user message (synchronous wrapper)."""
        try:
            # Try to find relevant plugins for the message
            for plugin_name, plugin_data in self.plugins.items():
                # Simple keyword matching for now
                if hasattr(plugin_data.get("instance"), "process_message"):
                    try:
                        response = plugin_data["instance"].process_message(user_message)
                        if response:
                            return response
                    except Exception as e:
                        print(f"❌ Error executing plugin {plugin_name}: {e}")
                        continue

            # Try to route to plugins using intent routing
            try:
                # Use async method in sync context carefully
                import asyncio

                if asyncio.get_event_loop().is_running():
                    # Create a simple response using available plugins
                    if self.plugins:
                        available_plugins = list(self.plugins.keys())[:3]
                        return f"I have access to these plugins that might help: {', '.join(available_plugins)}. What specific task would you like me to help with?"
                    else:
                        return "I'm ready to help! What can I assist you with today?"
                else:
                    # If no event loop is running, we can use asyncio.run
                    result = asyncio.run(
                        self.route_intent_to_plugins("general_query", user_message, {})
                    )
                    if result:
                        return f"I can help you with that using these capabilities: {', '.join(result[:3])}"
            except Exception as e:
                print(f"❌ Error in async plugin routing: {e}")

            # Fallback response
            return "I'm ready to help! What would you like me to assist you with?"
        except Exception as e:
            return f"I encountered an error: {str(e)}"

    async def scaffold_plugin_from_nl(self, description: str, plugin_name: str) -> str:
        """Generate plugin scaffolding from natural language description"""

        # Analyze the description to determine plugin type and capabilities
        analysis = await self._analyze_plugin_description(description)

        # Generate plugin template
        template = self._generate_plugin_template(plugin_name, analysis)

        # Save to file
        plugin_file = self.plugin_directory / f"{plugin_name}.py"
        with open(plugin_file, "w") as f:
            f.write(template)

        print(f"✅ Generated plugin scaffold: {plugin_file}")
        return str(plugin_file)

    async def _analyze_plugin_description(self, description: str) -> Dict[str, Any]:
        """Analyze natural language description to extract plugin requirements"""
        description_lower = description.lower()

        analysis = {
            "plugin_type": PluginType.UTILITY,
            "capabilities": [],
            "dependencies": [],
            "functions": [],
            "input_types": [],
            "output_types": [],
        }

        # Determine plugin type
        if any(
            word in description_lower
            for word in ["analyze", "scan", "inspect", "check"]
        ):
            analysis["plugin_type"] = PluginType.ANALYSIS
            analysis["capabilities"].extend(["analysis", "inspection", "validation"])

        if any(
            word in description_lower
            for word in ["generate", "create", "build", "make"]
        ):
            analysis["plugin_type"] = PluginType.GENERATION
            analysis["capabilities"].extend(["generation", "creation", "building"])

        if any(word in description_lower for word in ["file", "document", "text"]):
            analysis["capabilities"].extend(["file_processing", "text_handling"])
            analysis["input_types"].append("file_path")
            analysis["output_types"].append("processed_data")

        if any(word in description_lower for word in ["api", "web", "http", "request"]):
            analysis["capabilities"].extend(["web_integration", "api_communication"])
            analysis["dependencies"].extend(["requests", "aiohttp"])

        if any(word in description_lower for word in ["database", "sql", "mongo"]):
            analysis["capabilities"].extend(["database_operations"])
            analysis["dependencies"].extend(["sqlite3", "pymongo"])

        # Extract potential function names
        action_words = [
            "process",
            "analyze",
            "generate",
            "create",
            "parse",
            "convert",
            "transform",
        ]
        for word in action_words:
            if word in description_lower:
                analysis["functions"].append(f"{word}_data")

        if not analysis["functions"]:
            analysis["functions"] = ["main", "process"]

        return analysis

    def _generate_plugin_template(
        self, plugin_name: str, analysis: Dict[str, Any]
    ) -> str:
        """Generate plugin code template based on analysis"""

        template = f'''#!/usr/bin/env python3
"""
🧩 {plugin_name.upper()} PLUGIN
{("=" * (len(plugin_name) + 9))}

Auto-generated plugin scaffold for Lyrixa.
TODO: Implement the actual functionality.
"""

__version__ = "1.0.0"
__author__ = "Generated by Lyrixa"
__description__ = "Auto-generated plugin for {plugin_name}"
__plugin_type__ = "{analysis["plugin_type"].value}"
__tags__ = {analysis["capabilities"]}
__dependencies__ = {analysis["dependencies"]}
__capabilities__ = {analysis["capabilities"]}
__examples__ = [
    "# Example usage:",
    "# result = await plugin.{analysis["functions"][0] if analysis["functions"] else "main"}(input_data)"
]

import asyncio
from typing import Any, Dict, List
{f"import {', '.join(analysis['dependencies'])}" if analysis["dependencies"] else ""}


class {plugin_name.title()}Plugin:
    """
    Main plugin class for {plugin_name}

    TODO: Implement the plugin functionality based on requirements.
    """

    def __init__(self):
        self.name = "{plugin_name}"
        self.version = __version__
        self.capabilities = __capabilities__

'''

        # Generate function templates
        for func_name in analysis["functions"]:
            template += f'''
    async def {func_name}(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        TODO: Implement {func_name} functionality

        Args:
            input_data: The input data to process
            **kwargs: Additional configuration options

        Returns:
            Dict containing the processed results
        """
        try:
            # TODO: Implement actual functionality here
            result = {{
                "status": "success",
                "data": input_data,  # Replace with actual processing
                "message": "Processing completed successfully"
            }}
            return result

        except Exception as e:
            return {{
                "status": "error",
                "error": str(e),
                "message": "Processing failed"
            }}
'''

        # Add instance creation
        template += f'''

# Create plugin instance
{plugin_name}_plugin = {plugin_name.title()}Plugin()

# Main execution function (required by Lyrixa)
async def main(input_data: Any, **kwargs) -> Dict[str, Any]:
    """Main plugin execution function"""
    return await {plugin_name}_plugin.{analysis["functions"][0] if analysis["functions"] else "main"}(input_data, **kwargs)

# Export functions for Lyrixa
'''

        for func_name in analysis["functions"]:
            template += f"""
async def {func_name}(input_data: Any, **kwargs) -> Dict[str, Any]:
    return await {plugin_name}_plugin.{func_name}(input_data, **kwargs)
"""

        return template

    async def get_plugin_suggestions(
        self, user_input: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get plugin suggestions based on user input and context"""
        suggestions = []

        # Find relevant plugins
        relevant_plugins = await self.route_intent_to_plugins(
            user_input, user_input, context
        )

        for plugin_name in relevant_plugins:
            metadata = self.plugin_metadata[plugin_name]
            plugin_info = self.plugins[plugin_name]

            suggestion = {
                "plugin": plugin_name,
                "description": metadata.description,
                "capabilities": metadata.capabilities,
                "functions": list(plugin_info["functions"].keys()),
                "usage_examples": metadata.usage_examples,
                "confidence": self._calculate_relevance_score(user_input, metadata),
                "performance": {
                    "success_rate": metadata.success_rate,
                    "avg_execution_time": metadata.average_execution_time,
                    "usage_count": metadata.usage_count,
                },
            }
            suggestions.append(suggestion)

        return suggestions

    def _calculate_relevance_score(
        self, user_input: str, metadata: PluginMetadata
    ) -> float:
        """Calculate how relevant a plugin is to the user input"""
        score = 0.0
        user_words = user_input.lower().split()

        # Check capabilities
        capability_matches = sum(
            1
            for word in user_words
            if any(word in cap.lower() for cap in metadata.capabilities)
        )
        score += capability_matches * 0.3

        # Check tags
        tag_matches = sum(
            1
            for word in user_words
            if any(word in tag.lower() for tag in metadata.tags)
        )
        score += tag_matches * 0.2

        # Check description
        desc_matches = sum(
            1 for word in user_words if word in metadata.description.lower()
        )
        score += desc_matches * 0.1

        # Performance bonus
        score += metadata.success_rate * 0.2
        score += min(metadata.usage_count / 100, 0.2)  # Usage popularity bonus

        return min(score, 1.0)

    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the plugin ecosystem"""
        return {
            "total_plugins": len(self.plugins),
            "active_plugins": sum(
                1 for p in self.plugins.values() if p["status"] == PluginStatus.ACTIVE
            ),
            "plugin_chains": len(self.plugin_chains),
            "total_executions": len(self.execution_history),
            "success_rate": sum(1 for ex in self.execution_history if ex.success)
            / len(self.execution_history)
            if self.execution_history
            else 1.0,
            "plugins_by_type": {
                ptype.value: sum(
                    1 for m in self.plugin_metadata.values() if m.plugin_type == ptype
                )
                for ptype in PluginType
            },
            "top_plugins": sorted(
                [
                    (name, meta.usage_count)
                    for name, meta in self.plugin_metadata.items()
                ],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "recent_executions": self.execution_history[-10:]
            if self.execution_history
            else [],
        }

    async def _load_plugin_chains(self):
        """Load plugin chains from memory system"""
        if not self.memory_system:
            print("📋 No memory system configured, skipping plugin chain loading")
            return

        try:
            # Search for plugin chain memories using tags
            chain_memories = await self.memory_system.get_memories_by_tags(
                tags=["plugin_chain"], limit=100
            )

            print(f"🔍 Found {len(chain_memories)} plugin chain memories to process")

            for memory in chain_memories:
                # Handle both dict and object memory structures
                if hasattr(memory, "content"):
                    content = memory.content
                else:
                    content = memory

                # Extract chain data from content
                if isinstance(content, dict):
                    chain_data = content.get("plugin_chain") or content
                else:
                    chain_data = content

                if chain_data and isinstance(chain_data, dict):
                    # Validate required fields in chain_data
                    required_fields = {
                        "name",
                        "description",
                        "plugins",
                        "input_schema",
                        "output_schema",
                        "created_by",
                    }
                    missing_fields = required_fields - chain_data.keys()

                    if missing_fields:
                        print(
                            f"⚠️ Found corrupted plugin chain: Missing fields: {', '.join(missing_fields)}"
                        )
                        print(f"🧹 Attempting to clean corrupted chain data...")
                        # Try to delete the corrupted memory entry
                        try:
                            if hasattr(memory, "id"):
                                # If we can identify the memory entry, we could delete it
                                # For now, just skip and continue
                                pass
                        except Exception:
                            pass
                        continue

                    # Filter out unexpected keys from chain_data
                    valid_keys = required_fields | {"usage_count"}
                    filtered_chain_data = {
                        k: v for k, v in chain_data.items() if k in valid_keys
                    }

                    try:
                        chain = PluginChain(**filtered_chain_data)
                        self.plugin_chains[chain.name] = chain
                    except Exception as chain_error:
                        print(
                            f"⚠️ Failed to create plugin chain from data: {chain_error}"
                        )
                        continue

            print(f"✅ Loaded {len(self.plugin_chains)} plugin chains from memory")

        except Exception as e:
            print(f"⚠️ Failed to load plugin chains: {e}")

    async def _initialize_performance_monitoring(self):
        """Initialize performance monitoring for plugins"""
        self.performance_stats = {
            "startup_time": asyncio.get_event_loop().time(),
            "memory_usage": {},
            "execution_patterns": {},
            "error_tracking": {},
        }
        print("📊 Performance monitoring initialized")

    def discover_plugins(self) -> list:
        """Discover available plugins in all plugin directories."""
        discovered = set()
        for directory in self.all_plugin_directories:
            if not directory.exists():
                continue
            for file in directory.iterdir():
                if file.suffix == ".py" and not file.name.startswith("__"):
                    plugin_name = file.stem
                    discovered.add(plugin_name)
        return sorted(discovered)
