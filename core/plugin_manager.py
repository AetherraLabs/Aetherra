# core/plugin_manager.py
import importlib.util
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PluginMetadata:
    """Plugin metadata for enhanced discovery and transparency"""

    name: str
    description: str = "No description provided"
    capabilities: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = "Unknown"
    category: str = "general"
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    last_loaded: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
            "last_loaded": self.last_loaded,
        }


@dataclass
class PluginIntent:
    """Plugin intent declaration for assistant discovery"""

    purpose: str  # What the plugin is used for (e.g., "optimization", "analysis")
    triggers: List[str] = field(
        default_factory=list
    )  # Keywords that should trigger this plugin
    scenarios: List[str] = field(
        default_factory=list
    )  # Use cases where this plugin applies
    ai_description: str = ""  # AI-friendly description for LLM understanding
    example_usage: str = ""  # Example of how to use this plugin
    confidence_boost: float = 1.0  # Multiplier for relevance scoring

    def to_dict(self) -> Dict[str, Any]:
        """Convert intent to dictionary for serialization"""
        return {
            "purpose": self.purpose,
            "triggers": self.triggers,
            "scenarios": self.scenarios,
            "ai_description": self.ai_description,
            "example_usage": self.example_usage,
            "confidence_boost": self.confidence_boost,
        }


# Enhanced plugin registry with metadata
PLUGIN_REGISTRY: Dict[str, Callable] = {}
PLUGIN_METADATA: Dict[str, PluginMetadata] = {}
PLUGIN_INTENTS: Dict[str, PluginIntent] = {}

PLUGIN_DIR = os.path.join(
    os.path.dirname(__file__), "..", "src", "neurocode", "plugins"
)
os.makedirs(PLUGIN_DIR, exist_ok=True)


def register_plugin(
    name: str,
    description: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: str = "Unknown",
    category: str = "general",
    dependencies: Optional[List[str]] = None,
    # New intent-based parameters
    intent_purpose: Optional[str] = None,
    intent_triggers: Optional[List[str]] = None,
    intent_scenarios: Optional[List[str]] = None,
    ai_description: Optional[str] = None,
    example_usage: Optional[str] = None,
    confidence_boost: float = 1.0,
):
    """
    Enhanced plugin registration decorator with intent and AI discovery support

    Args:
        name: Plugin name
        description: Human-readable description of what the plugin does
        capabilities: List of capabilities/features the plugin provides
        version: Plugin version
        author: Plugin author
        category: Plugin category for organization
        dependencies: List of required dependencies
        intent_purpose: What the plugin is intended for (AI discovery)
        intent_triggers: Keywords that should trigger this plugin
        intent_scenarios: Use cases where this plugin applies
        ai_description: AI-friendly description for LLM understanding
        example_usage: Example of how to use this plugin
        confidence_boost: Multiplier for relevance scoring (default 1.0)
    """

    def decorator(func: Callable) -> Callable:
        # Register the plugin function
        PLUGIN_REGISTRY[name] = func

        # Create and store metadata
        metadata = PluginMetadata(
            name=name,
            description=description or func.__doc__ or "No description provided",
            capabilities=capabilities or [],
            version=version,
            author=author,
            category=category,
            dependencies=dependencies or [],
            enabled=True,
            last_loaded=None,  # Will be set during loading
        )

        PLUGIN_METADATA[name] = metadata

        # Create and store intent information
        if intent_purpose or intent_triggers or intent_scenarios:
            intent = PluginIntent(
                purpose=intent_purpose or "general purpose",
                triggers=intent_triggers or [],
                scenarios=intent_scenarios or [],
                ai_description=ai_description or description or func.__doc__ or "",
                example_usage=example_usage or f"plugin: {name} <args>",
                confidence_boost=confidence_boost,
            )
            PLUGIN_INTENTS[name] = intent

        return func

    return decorator


def load_plugins():
    """Load plugins with enhanced metadata tracking"""
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(PLUGIN_DIR, filename)
            module_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(module_name, filepath)

            if spec is None:
                print(f"[Plugin Error] Could not create spec for {module_name}")
                continue

            module = importlib.util.module_from_spec(spec)

            if spec.loader is None:
                print(f"[Plugin Error] No loader available for {module_name}")
                continue

            try:
                spec.loader.exec_module(module)

                # Update metadata for all plugins loaded from this module
                current_time = str(datetime.now())
                for _, metadata in PLUGIN_METADATA.items():
                    if metadata.last_loaded is None:  # New plugin
                        metadata.last_loaded = current_time

                print(f"[Plugin] Loaded: {module_name}")
            except Exception as e:
                print(f"[Plugin Error] Failed to load {module_name}: {e}")


def get_plugin(name: str) -> Optional[Callable]:
    """Get a specific plugin by name"""
    return PLUGIN_REGISTRY.get(name)


def get_plugin_metadata(name: str) -> Optional[PluginMetadata]:
    """Get metadata for a specific plugin"""
    return PLUGIN_METADATA.get(name)


def list_plugins() -> List[str]:
    """List all available plugin names"""
    return list(PLUGIN_REGISTRY.keys())


def list_plugins_by_category(category: str) -> List[str]:
    """List plugins by category"""
    return [
        name
        for name, metadata in PLUGIN_METADATA.items()
        if metadata.category == category and metadata.enabled
    ]


def get_plugin_categories() -> List[str]:
    """Get all unique plugin categories"""
    categories = set()
    for metadata in PLUGIN_METADATA.values():
        categories.add(metadata.category)
    return sorted(categories)


def get_plugins_info() -> Dict[str, Dict[str, Any]]:
    """Get comprehensive information about all plugins for UI display"""
    plugins_info = {}

    for name, metadata in PLUGIN_METADATA.items():
        plugin_func = PLUGIN_REGISTRY.get(name)

        plugins_info[name] = {
            "metadata": metadata.to_dict(),
            "available": plugin_func is not None,
            "docstring": plugin_func.__doc__ if plugin_func else None,
            "signature": str(plugin_func.__annotations__) if plugin_func else None,
        }

    return plugins_info


def toggle_plugin(name: str, enabled: bool) -> bool:
    """Enable or disable a plugin"""
    if name in PLUGIN_METADATA:
        PLUGIN_METADATA[name].enabled = enabled
        return True
    return False


def search_plugins(query: str) -> List[str]:
    """Search plugins by name, description, or capabilities"""
    query_lower = query.lower()
    matching_plugins = []

    for name, metadata in PLUGIN_METADATA.items():
        if (
            query_lower in name.lower()
            or query_lower in metadata.description.lower()
            or any(query_lower in cap.lower() for cap in metadata.capabilities)
        ):
            matching_plugins.append(name)

    return matching_plugins


def execute_plugin(name: str, *args, **kwargs) -> Any:
    """Execute a plugin with given arguments"""
    plugin = get_plugin(name)
    metadata = get_plugin_metadata(name)

    if plugin is None:
        raise ValueError(f"Plugin '{name}' not found")

    if metadata and not metadata.enabled:
        raise ValueError(f"Plugin '{name}' is disabled")

    try:
        return plugin(*args, **kwargs)
    except Exception as e:
        print(f"[Plugin Error] Error executing {name}: {e}")
        raise


def get_plugin_ui_data() -> Dict[str, Any]:
    """Get plugin data formatted for UI display"""
    categories = {}

    for name, metadata in PLUGIN_METADATA.items():
        category = metadata.category
        if category not in categories:
            categories[category] = []

        plugin_info = {
            "name": name,
            "description": metadata.description,
            "capabilities": metadata.capabilities,
            "version": metadata.version,
            "author": metadata.author,
            "enabled": metadata.enabled,
            "last_loaded": metadata.last_loaded,
            "available": name in PLUGIN_REGISTRY,
        }

        categories[category].append(plugin_info)

    return {
        "categories": categories,
        "total_plugins": len(PLUGIN_METADATA),
        "enabled_plugins": sum(1 for m in PLUGIN_METADATA.values() if m.enabled),
        "available_plugins": len(PLUGIN_REGISTRY),
    }


def validate_plugin_dependencies(name: str) -> Dict[str, bool]:
    """Check if plugin dependencies are available"""
    metadata = get_plugin_metadata(name)
    if not metadata:
        return {}

    dependency_status = {}
    for dep in metadata.dependencies:
        # Check if dependency is available (simplified check)
        try:
            __import__(dep)
            dependency_status[dep] = True
        except ImportError:
            dependency_status[dep] = False

    return dependency_status


def reload_plugins():
    """Reload all plugins"""
    global PLUGIN_REGISTRY, PLUGIN_METADATA
    PLUGIN_REGISTRY.clear()
    PLUGIN_METADATA.clear()
    load_plugins()


def discover_plugins_by_intent(
    query: str,
    context: Optional[str] = None,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    AI-powered plugin discovery based on intent and context

    Args:
        query: User's intent or goal description
        context: Additional context about the task
        max_results: Maximum number of plugins to return

    Returns:
        List of relevant plugins with relevance scores
    """
    query_lower = query.lower()
    context_lower = (context or "").lower()
    combined_text = f"{query_lower} {context_lower}".strip()

    relevant_plugins = []

    for name, intent in PLUGIN_INTENTS.items():
        metadata = PLUGIN_METADATA.get(name)
        if not metadata or not metadata.enabled:
            continue

        # Calculate relevance score
        score = 0.0

        # Check purpose match
        if intent.purpose.lower() in combined_text:
            score += 3.0

        # Check trigger words
        for trigger in intent.triggers:
            if trigger.lower() in combined_text:
                score += 2.0

        # Check scenarios
        for scenario in intent.scenarios:
            if any(word in combined_text for word in scenario.lower().split()):
                score += 1.5

        # Check capabilities
        for capability in metadata.capabilities:
            if capability.lower() in combined_text:
                score += 1.0

        # Check description and AI description
        desc_text = f"{metadata.description} {intent.ai_description}".lower()
        query_words = query_lower.split()
        for word in query_words:
            if word in desc_text:
                score += 0.5

        # Apply confidence boost
        score *= intent.confidence_boost

        if score > 0:
            relevant_plugins.append(
                {
                    "name": name,
                    "score": score,
                    "metadata": metadata.to_dict(),
                    "intent": intent.to_dict(),
                    "reason": _generate_relevance_reason(
                        query, intent, metadata, score
                    ),
                }
            )

    # Sort by relevance score and return top results
    relevant_plugins.sort(key=lambda x: x["score"], reverse=True)
    return relevant_plugins[:max_results]


def _generate_relevance_reason(
    query: str,
    intent: PluginIntent,
    metadata: PluginMetadata,
    score: float,
) -> str:
    """Generate a human-readable explanation of why a plugin is relevant"""
    reasons = []

    query_lower = query.lower()

    if intent.purpose.lower() in query_lower:
        reasons.append(f"designed for {intent.purpose}")

    trigger_matches = [t for t in intent.triggers if t.lower() in query_lower]
    if trigger_matches:
        reasons.append(f"triggered by: {', '.join(trigger_matches)}")

    capability_matches = [c for c in metadata.capabilities if c.lower() in query_lower]
    if capability_matches:
        reasons.append(f"provides: {', '.join(capability_matches)}")

    if not reasons:
        reasons.append("general relevance to query")

    return f"Relevant because it's {' and '.join(reasons)} (score: {score:.1f})"


def get_ai_plugin_recommendations(
    user_goal: str,
    current_context: Optional[str] = None,
    include_examples: bool = True,
) -> Dict[str, Any]:
    """
    Get AI-friendly plugin recommendations for assistant integration

    Args:
        user_goal: What the user wants to accomplish
        current_context: Current state or context information
        include_examples: Whether to include usage examples

    Returns:
        Structured recommendations for AI assistant consumption
    """
    discoveries = discover_plugins_by_intent(user_goal, current_context)

    recommendations = {
        "query": user_goal,
        "context": current_context,
        "total_found": len(discoveries),
        "recommendations": [],
        "summary": "",
    }

    for discovery in discoveries:
        name = discovery["name"]
        plugin_rec = {
            "plugin_name": name,
            "relevance_score": discovery["score"],
            "description": discovery["metadata"]["description"],
            "ai_description": discovery["intent"]["ai_description"],
            "purpose": discovery["intent"]["purpose"],
            "capabilities": discovery["metadata"]["capabilities"],
            "reason": discovery["reason"],
        }

        if include_examples:
            plugin_rec["example_usage"] = discovery["intent"]["example_usage"]
            plugin_rec["triggers"] = discovery["intent"]["triggers"]
            plugin_rec["scenarios"] = discovery["intent"]["scenarios"]

        recommendations["recommendations"].append(plugin_rec)

    # Generate summary
    if discoveries:
        top_plugin = discoveries[0]
        recommendations["summary"] = (
            f"Found {len(discoveries)} relevant plugins. "
            f"Top recommendation: '{top_plugin['name']}' "
            f"({top_plugin['metadata']['description']}) "
            f"with relevance score {top_plugin['score']:.1f}"
        )
    else:
        recommendations["summary"] = (
            "No plugins found matching the specified goal or context."
        )

    return recommendations


def register_plugin_intent(
    plugin_name: str,
    purpose: str,
    triggers: Optional[List[str]] = None,
    scenarios: Optional[List[str]] = None,
    ai_description: Optional[str] = None,
    example_usage: Optional[str] = None,
    confidence_boost: float = 1.0,
) -> bool:
    """
    Register intent information for an existing plugin

    This allows adding intent data to plugins that were registered without it
    """
    if plugin_name not in PLUGIN_REGISTRY:
        return False

    intent = PluginIntent(
        purpose=purpose,
        triggers=triggers or [],
        scenarios=scenarios or [],
        ai_description=ai_description or "",
        example_usage=example_usage or f"plugin: {plugin_name} <args>",
        confidence_boost=confidence_boost,
    )

    PLUGIN_INTENTS[plugin_name] = intent
    return True


def get_plugin_discovery_stats() -> Dict[str, Any]:
    """Get statistics about plugin discovery capabilities"""
    total_plugins = len(PLUGIN_REGISTRY)
    plugins_with_intent = len(PLUGIN_INTENTS)

    categories = {}
    purposes = {}

    for metadata in PLUGIN_METADATA.values():
        cat = metadata.category
        categories[cat] = categories.get(cat, 0) + 1

    for intent in PLUGIN_INTENTS.values():
        purpose = intent.purpose
        purposes[purpose] = purposes.get(purpose, 0) + 1

    return {
        "total_plugins": total_plugins,
        "plugins_with_intent": plugins_with_intent,
        "intent_coverage": f"{(plugins_with_intent / total_plugins) * 100:.1f}%"
        if total_plugins > 0
        else "0%",
        "categories": categories,
        "purposes": purposes,
        "top_purposes": sorted(purposes.items(), key=lambda x: x[1], reverse=True)[:5],
    }


def parse_plugin_command(command: str) -> Dict[str, Any]:
    """
    Parse plugin commands from .aether code syntax

    Supports formats:
    - plugin: name "arg1" "arg2"
    - plugin: name.method "arg1"
    - plugin: name arg1 arg2
    """
    # Remove 'plugin:' prefix
    command = command.strip()
    if command.startswith("plugin:"):
        command = command[8:].strip()

    # Parse quoted arguments
    quoted_pattern = r'"([^"]*)"'
    quotes = re.findall(quoted_pattern, command)

    # Remove quoted parts to get the plugin name/method
    command_without_quotes = re.sub(quoted_pattern, "", command).strip()
    parts = command_without_quotes.split()

    if not parts:
        return {"error": "No plugin name specified"}

    plugin_part = parts[0]

    # Check for method syntax (plugin.method)
    if "." in plugin_part:
        plugin_name, method = plugin_part.split(".", 1)
    else:
        plugin_name = plugin_part
        method = None

    # Combine quoted args and remaining args
    remaining_args = parts[1:]
    all_args = quotes + remaining_args

    return {
        "plugin_name": plugin_name,
        "method": method,
        "args": all_args,
        "raw_command": command,
    }


def execute_plugin_command(command: str) -> Dict[str, Any]:
    """
    Execute a plugin command from .aether code syntax
    """
    parsed = parse_plugin_command(command)

    if "error" in parsed:
        return parsed

    plugin_name = parsed["plugin_name"]
    method = parsed["method"]
    args = parsed["args"]

    # Get the plugin
    plugin = get_plugin(plugin_name)
    if not plugin:
        return {"error": f"Plugin '{plugin_name}' not found"}

    # Check if plugin is enabled
    metadata = get_plugin_metadata(plugin_name)
    if metadata and not metadata.enabled:
        return {"error": f"Plugin '{plugin_name}' is disabled"}

    try:
        # If method is specified, handle it differently
        if method:
            # For now, treat method as part of the plugin name
            # Future: Could support plugin classes with methods
            full_name = f"{plugin_name}_{method}"
            method_plugin = get_plugin(full_name)
            if method_plugin:
                result = method_plugin(*args)
            else:
                return {"error": f"Plugin method '{plugin_name}.{method}' not found"}
        else:
            # Execute the plugin with arguments
            result = plugin(*args)

        # Ensure result is always a dict
        if not isinstance(result, dict):
            result = {"result": result}

        # Add execution metadata
        result["plugin_executed"] = plugin_name
        result["execution_time"] = str(datetime.now())

        return result

    except Exception as e:
        return {
            "error": f"Plugin execution failed: {str(e)}",
            "plugin": plugin_name,
            "args": args,
        }


# Call this at startup to populate PLUGIN_REGISTRY
load_plugins()
