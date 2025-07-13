#!/usr/bin/env python3
"""
🧩➡️🧠 PLUGIN-INTELLIGENCE BRIDGE
=================================

This module bridges the gap between plugin discovery and Lyrixa's intelligence system.
It ensures that Lyrixa is aware of all available plugins and can reference, rank,
and recommend them through her memory system.

CRITICAL INTEGRATION:
- Discovers plugins using existing plugin managers
- Stores plugin metadata in intelligence memory under type: "plugin"
- Enables Lyrixa to query and recommend plugins intelligently
- Integrates with GUI components for user-facing plugin awareness
"""

import logging
import sys
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginIntelligenceBridge:
    """
    🔗 Bridge between Plugin Discovery and Intelligence Memory

    This class solves the critical architectural gap by:
    1. Discovering plugins using existing plugin managers
    2. Converting plugin data to intelligence memory patterns
    3. Storing plugin metadata for AI awareness and recommendations
    4. Providing GUI integration for user-facing plugin displays
    """

    def __init__(self, intelligence_system=None):
        self.intelligence_system = intelligence_system
        self.plugin_managers = []
        self.discovered_plugins = {}
        self.plugin_metadata_cache = {}
        self.retry_count = 3  # Number of retries for intermittent failures
        self.retry_delay = 1.0  # Seconds to wait between retries

        # Initialize plugin managers
        self._initialize_plugin_managers()
        logger.info("🔗 Plugin-Intelligence Bridge initialized")

    async def _retry_operation(self, operation, *args, **kwargs):
        """Retry an operation with exponential backoff to handle intermittent failures"""
        last_exception = None

        for attempt in range(self.retry_count):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                else:
                    return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.retry_count - 1:
                    wait_time = self.retry_delay * (2**attempt)  # Exponential backoff
                    logger.warning(
                        f"⚠️ Operation failed (attempt {attempt + 1}/{self.retry_count}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"❌ Operation failed after {self.retry_count} attempts: {e}"
                    )

        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Operation failed without specific exception")

    def _validate_manager_connection(self, manager_type: str, manager) -> bool:
        """Validate that a plugin manager is properly connected and responsive"""
        try:
            # Basic connectivity tests for different manager types
            if manager_type == "enhanced":
                return hasattr(manager, "list_plugins") or hasattr(manager, "discover_plugins")
            elif manager_type == "core":
                return hasattr(manager, "plugin_info") or hasattr(manager, "plugins")
            elif manager_type == "system":
                return hasattr(manager, "list_all_plugins") or hasattr(manager, "get_plugins")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Manager validation failed for {manager_type}: {e}")
            return False

    def _initialize_plugin_managers(self):
        """Initialize all available plugin managers"""
        try:
            # Enhanced Plugin Manager
            try:
                from Aetherra.lyrixa.plugins.enhanced_plugin_manager import (
                    PluginManager,
                )

                manager = PluginManager()
                self.plugin_managers.append(("enhanced", manager))
                logger.info("✅ Enhanced Plugin Manager connected")
            except ImportError as e:
                logger.debug(f"Enhanced Plugin Manager not available: {e}")

            # Core Plugin Manager
            try:
                from Aetherra.lyrixa.core.plugins import LyrixaPluginManager

                manager = LyrixaPluginManager()
                self.plugin_managers.append(("core", manager))
                logger.info("✅ Core Plugin Manager connected")
            except ImportError as e:
                logger.debug(f"Core Plugin Manager not available: {e}")

            # Plugin System Manager
            try:
                from Aetherra.lyrixa.core.plugin_system import LyrixaPluginSystem

                manager = LyrixaPluginSystem()
                self.plugin_managers.append(("system", manager))
                logger.info("✅ Plugin System Manager connected")
            except ImportError as e:
                logger.debug(f"Plugin System Manager not available: {e}")

        except Exception as e:
            logger.error(f"❌ Error initializing plugin managers: {e}")

    async def discover_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover plugins from all available managers

        Returns:
            Dict mapping plugin names to comprehensive metadata
        """
        all_plugins = {}

        for manager_type, manager in self.plugin_managers:
            try:
                # Validate manager connection before discovery
                if not self._validate_manager_connection(manager_type, manager):
                    logger.warning(
                        f"⚠️ Skipping {manager_type} manager - connection not valid"
                    )
                    continue

                # Use retry logic for discovery to handle intermittent failures
                plugins = await self._retry_operation(
                    self._discover_from_manager, manager_type, manager
                )

                # Merge discovered plugins with namespace prefix
                for plugin_name, plugin_data in plugins.items():
                    # Add manager source info
                    plugin_data["discovered_from"] = manager_type
                    plugin_data["discovery_timestamp"] = datetime.now().isoformat()

                    # Use namespaced key to avoid conflicts
                    key = f"{manager_type}:{plugin_name}"
                    all_plugins[key] = plugin_data

                logger.info(
                    f"✅ Discovered {len(plugins)} plugins from {manager_type} manager"
                )

            except Exception as e:
                logger.error(f"❌ Error discovering plugins from {manager_type}: {e}")

        self.discovered_plugins = all_plugins
        logger.info(f"🔍 Total plugins discovered: {len(all_plugins)}")
        return all_plugins

    async def _discover_from_manager(
        self, manager_type: str, manager
    ) -> Dict[str, Dict[str, Any]]:
        """Discover plugins from a specific manager"""
        plugins = {}

        try:
            if manager_type == "enhanced":
                # Enhanced plugin manager methods
                if hasattr(manager, "list_plugins"):
                    plugin_list = manager.list_plugins()
                    for plugin_name in plugin_list:
                        metadata = await self._get_enhanced_plugin_metadata(
                            manager, plugin_name
                        )
                        plugins[plugin_name] = metadata

            elif manager_type == "core":
                # Core plugin manager methods
                if hasattr(manager, "plugin_info"):
                    for plugin_name, plugin_info in manager.plugin_info.items():
                        metadata = await self._get_core_plugin_metadata(
                            manager, plugin_name, plugin_info
                        )
                        plugins[plugin_name] = metadata

            elif manager_type == "system":
                # Plugin system methods
                if hasattr(manager, "installed_plugins"):
                    for (
                        plugin_name,
                        plugin_instance,
                    ) in manager.installed_plugins.items():
                        metadata = await self._get_system_plugin_metadata(
                            manager, plugin_name, plugin_instance
                        )
                        plugins[plugin_name] = metadata

        except Exception as e:
            logger.error(
                f"❌ Error in manager-specific discovery for {manager_type}: {e}"
            )

        return plugins

    async def _get_enhanced_plugin_metadata(
        self, manager, plugin_name: str
    ) -> Dict[str, Any]:
        """Extract metadata from enhanced plugin manager"""
        metadata = {
            "name": plugin_name,
            "type": "enhanced",
            "status": "unknown",
            "description": "",
            "capabilities": [],
            "version": "unknown",
            "author": "unknown",
            "category": "utility",
        }

        try:
            # Try to get plugin info if available
            if hasattr(manager, "get_plugin_info"):
                info = manager.get_plugin_info(plugin_name)
                if info:
                    metadata.update(
                        {
                            "description": info.get("description", ""),
                            "version": info.get("version", "unknown"),
                            "author": info.get("author", "unknown"),
                            "category": info.get("category", "utility"),
                            "status": "available"
                            if info.get("enabled", False)
                            else "disabled",
                        }
                    )

            # Try to get capabilities
            if hasattr(manager, "get_plugin_capabilities"):
                capabilities = manager.get_plugin_capabilities(plugin_name)
                if capabilities:
                    metadata["capabilities"] = capabilities

        except Exception as e:
            logger.debug(
                f"Could not get full metadata for enhanced plugin {plugin_name}: {e}"
            )

        return metadata

    async def _get_core_plugin_metadata(
        self, manager, plugin_name: str, plugin_info
    ) -> Dict[str, Any]:
        """Extract metadata from core plugin manager"""
        metadata = {
            "name": plugin_name,
            "type": "core",
            "status": "loaded" if plugin_info.loaded else "available",
            "description": plugin_info.description or "",
            "capabilities": plugin_info.capabilities or [],
            "version": plugin_info.version or "unknown",
            "author": plugin_info.author or "Lyrixa Team",
            "category": plugin_info.category or "utility",
            "enabled": plugin_info.enabled,
        }

        return metadata

    async def _get_system_plugin_metadata(
        self, manager, plugin_name: str, plugin_instance
    ) -> Dict[str, Any]:
        """Extract metadata from plugin system manager"""
        metadata = {
            "name": plugin_name,
            "type": "system",
            "status": "installed",
            "description": "",
            "capabilities": [],
            "version": "unknown",
            "author": "unknown",
            "category": "system",
        }

        try:
            # Try to extract metadata from plugin instance
            if hasattr(plugin_instance, "metadata"):
                instance_metadata = plugin_instance.metadata
                metadata.update(
                    {
                        "description": instance_metadata.get("description", ""),
                        "version": instance_metadata.get("version", "unknown"),
                        "author": instance_metadata.get("author", "unknown"),
                        "category": instance_metadata.get("category", "system"),
                    }
                )

        except Exception as e:
            logger.debug(
                f"Could not get full metadata for system plugin {plugin_name}: {e}"
            )

        return metadata

    async def store_plugins_in_intelligence_memory(self) -> bool:
        """
        Store discovered plugin metadata in intelligence memory system

        This is the KEY integration that enables Lyrixa to be aware of plugins
        """
        if not self.intelligence_system:
            logger.warning("⚠️ No intelligence system available for plugin storage")
            return False

        try:
            # Discover all plugins first
            await self.discover_all_plugins()

            stored_count = 0
            for plugin_key, plugin_data in self.discovered_plugins.items():
                try:
                    # Create memory pattern for plugin
                    memory_pattern = {
                        "type": "plugin",
                        "plugin_id": plugin_key,
                        "plugin_name": plugin_data["name"],
                        "plugin_type": plugin_data["type"],
                        "status": plugin_data["status"],
                        "description": plugin_data["description"],
                        "capabilities": plugin_data["capabilities"],
                        "category": plugin_data["category"],
                        "version": plugin_data["version"],
                        "author": plugin_data["author"],
                        "discovered_from": plugin_data["discovered_from"],
                        "last_updated": datetime.now().isoformat(),
                        "searchable_content": self._create_searchable_content(
                            plugin_data
                        ),
                        "recommendation_score": self._calculate_recommendation_score(
                            plugin_data
                        ),
                    }

                    # Store in intelligence memory
                    if hasattr(self.intelligence_system, "store_memory_pattern"):
                        success = self.intelligence_system.store_memory_pattern(
                            memory_pattern
                        )
                        if success:
                            stored_count += 1
                    elif hasattr(self.intelligence_system, "add_memory"):
                        success = self.intelligence_system.add_memory(
                            content=memory_pattern,
                            memory_type="plugin",
                            context={"plugin_discovery": True},
                        )
                        if success:
                            stored_count += 1

                except Exception as e:
                    logger.error(
                        f"❌ Failed to store plugin {plugin_key} in memory: {e}"
                    )

            logger.info(f"✅ Stored {stored_count} plugins in intelligence memory")
            return stored_count > 0

        except Exception as e:
            logger.error(f"❌ Error storing plugins in intelligence memory: {e}")
            return False

    def _create_searchable_content(self, plugin_data: Dict[str, Any]) -> str:
        """Create searchable content string for plugin"""
        searchable_parts = [
            plugin_data.get("name", ""),
            plugin_data.get("description", ""),
            plugin_data.get("category", ""),
            " ".join(plugin_data.get("capabilities", [])),
            plugin_data.get("author", ""),
        ]

        return " ".join(filter(None, searchable_parts)).lower()

    def _calculate_recommendation_score(self, plugin_data: Dict[str, Any]) -> float:
        """Calculate a recommendation score for the plugin"""
        score = 0.5  # Base score

        # Boost for active/loaded plugins
        if plugin_data.get("status") in ["loaded", "active", "installed"]:
            score += 0.2

        # Boost for plugins with good descriptions
        if len(plugin_data.get("description", "")) > 20:
            score += 0.1

        # Boost for plugins with capabilities
        capabilities_count = len(plugin_data.get("capabilities", []))
        score += min(capabilities_count * 0.05, 0.2)

        # Boost for core/system plugins (more stable)
        if plugin_data.get("type") in ["core", "system"]:
            score += 0.1

        return min(score, 1.0)

    async def query_plugins_for_lyrixa(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query plugins for Lyrixa to use in conversations

        This enables Lyrixa to search and recommend relevant plugins
        """
        if not self.intelligence_system:
            return []

        try:
            # Try to query from intelligence memory system
            if hasattr(self.intelligence_system, "query_memories"):
                results = await self.intelligence_system.query_memories(
                    query=query, memory_type="plugin", limit=limit
                )
                return results
            elif hasattr(self.intelligence_system, "search_memory"):
                results = await self.intelligence_system.search_memory(
                    query=query, limit=limit, filter_type="plugin"
                )
                return results
            else:
                # Fallback to local search
                return self._local_plugin_search(query, limit)

        except Exception as e:
            logger.error(f"❌ Error querying plugins: {e}")
            return []

    def _local_plugin_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback local search of discovered plugins"""
        query_lower = query.lower()
        matches = []

        for plugin_key, plugin_data in self.discovered_plugins.items():
            searchable = self._create_searchable_content(plugin_data)

            # Simple relevance scoring
            score = 0
            query_words = query_lower.split()
            for word in query_words:
                if word in searchable:
                    score += 1

            if score > 0:
                plugin_result = plugin_data.copy()
                plugin_result["relevance_score"] = score
                matches.append(plugin_result)

        # Sort by relevance and recommendation score
        matches.sort(
            key=lambda x: (x["relevance_score"], x.get("recommendation_score", 0)),
            reverse=True,
        )

        return matches[:limit]

    def get_plugin_summary_for_gui(self) -> Dict[str, Any]:
        """
        Get plugin summary for GUI display

        This provides data for plugin management interfaces
        """
        summary = {
            "total_plugins": len(self.discovered_plugins),
            "by_type": {},
            "by_status": {},
            "by_category": {},
            "featured_plugins": [],
            "recently_discovered": [],
        }

        # Analyze discovered plugins
        for plugin_key, plugin_data in self.discovered_plugins.items():
            # Count by type
            plugin_type = plugin_data.get("type", "unknown")
            summary["by_type"][plugin_type] = summary["by_type"].get(plugin_type, 0) + 1

            # Count by status
            status = plugin_data.get("status", "unknown")
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

            # Count by category
            category = plugin_data.get("category", "uncategorized")
            summary["by_category"][category] = (
                summary["by_category"].get(category, 0) + 1
            )

        # Get featured plugins (high recommendation score)
        featured = [
            plugin_data
            for plugin_data in self.discovered_plugins.values()
            if plugin_data.get("recommendation_score", 0) >= 0.7
        ]
        featured.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
        summary["featured_plugins"] = featured[:5]

        # Get recently discovered plugins
        recent = sorted(
            self.discovered_plugins.values(),
            key=lambda x: x.get("discovery_timestamp", ""),
            reverse=True,
        )
        summary["recently_discovered"] = recent[:5]

        return summary

    async def integrate_with_gui(self, gui_manager=None) -> bool:
        """
        Integrate plugin discovery with GUI components

        This updates GUI plugin displays with real discovery data
        """
        try:
            # Update plugin summary
            summary = self.get_plugin_summary_for_gui()

            # If GUI manager provided, update it
            if gui_manager and hasattr(gui_manager, "update_plugin_display"):
                gui_manager.update_plugin_display(summary)

            logger.info(
                f"✅ GUI integration complete - {summary['total_plugins']} plugins available"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error integrating with GUI: {e}")
            return False


# Convenience functions for easy integration
async def initialize_plugin_intelligence_bridge(
    intelligence_system=None,
) -> PluginIntelligenceBridge:
    """Initialize and setup the plugin-intelligence bridge"""
    bridge = PluginIntelligenceBridge(intelligence_system)

    # Discover and store plugins in intelligence memory
    await bridge.store_plugins_in_intelligence_memory()

    return bridge


async def update_lyrixa_plugin_awareness(intelligence_system) -> bool:
    """Update Lyrixa's plugin awareness - call this periodically"""
    bridge = PluginIntelligenceBridge(intelligence_system)
    return await bridge.store_plugins_in_intelligence_memory()


# Export main classes and functions
__all__ = [
    "PluginIntelligenceBridge",
    "initialize_plugin_intelligence_bridge",
    "update_lyrixa_plugin_awareness",
]
