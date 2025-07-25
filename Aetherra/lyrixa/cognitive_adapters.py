#!/usr/bin/env python3
"""
🔗 UNIFIED COGNITIVE ARCHITECTURE ADAPTERS
===========================================

Adapter classes to bridge compatibility between different cognitive systems
and ensure seamless integration across the unified architecture.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FractalMeshToLyrixaAdapter:
    """
    Adapter to make FractalMeshCore compatible with LyrixaMemoryEngine interface
    """

    def __init__(self, fractal_mesh_core):
        self.fractal_mesh = fractal_mesh_core
        logger.info("🔗 FractalMesh-to-Lyrixa adapter initialized")

    async def store_memory(
        self,
        content: str,
        memory_type: str = "episodic",
        metadata: Dict[str, Any] = None,
    ):
        """Adapter method for memory storage"""
        if metadata is None:
            metadata = {}
        try:
            # This would need actual implementation based on FractalMesh API
            logger.info(f"📝 Storing memory via adapter: {content[:50]}...")
            return f"memory_{hash(content)}"
        except Exception as e:
            logger.error(f"❌ Memory storage failed: {e}")
            return None

    async def retrieve_memories(self, query: str, limit: int = 10):
        """Adapter method for memory retrieval"""
        try:
            # This would need actual implementation based on FractalMesh API
            logger.info(f"🔍 Retrieving memories via adapter: {query[:50]}...")
            return []
        except Exception as e:
            logger.error(f"❌ Memory retrieval failed: {e}")
            return []


class MockConceptClusterManager:
    """
    Mock implementation of ConceptClusterManager for compatibility
    """

    def __init__(self):
        self.clusters = {}
        logger.info("🧩 Mock ConceptClusterManager initialized")

    def get_relevant_clusters(self, context: str, limit: int = 5):
        """Get relevant concept clusters for given context"""
        try:
            # Mock implementation - would need real clustering logic
            mock_clusters = [
                {
                    "name": f"cluster_{i}",
                    "relevance": 0.8 - (i * 0.1),
                    "concepts": [context],
                }
                for i in range(min(limit, 3))
            ]
            return mock_clusters
        except Exception as e:
            logger.error(f"❌ Cluster retrieval failed: {e}")
            return []

    def add_concept(self, concept: str, cluster_name: Optional[str] = None):
        """Add concept to cluster"""
        if cluster_name is None:
            cluster_name = f"auto_cluster_{len(self.clusters)}"

        if cluster_name not in self.clusters:
            self.clusters[cluster_name] = []

        self.clusters[cluster_name].append(concept)
        logger.info(f"➕ Added concept '{concept}' to cluster '{cluster_name}'")


class CompatiblePluginRouter:
    """
    Compatible plugin router that works with the enhanced plugin manager
    """

    def __init__(self, plugin_manager, memory_adapter=None, concept_manager=None):
        self.plugin_manager = plugin_manager
        self.memory_adapter = memory_adapter or None
        self.concept_manager = concept_manager or MockConceptClusterManager()

        # Plugin execution tracking
        self.execution_history = []

        logger.info("🔌 Compatible Plugin Router initialized")

    async def execute_plugin_with_context(
        self,
        plugin_name: str,
        context: str,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Execute plugin with memory and concept context"""
        try:
            if parameters is None:
                parameters = {}

            # Get memory context if available
            if self.memory_adapter:
                memory_context = await self.memory_adapter.retrieve_memories(
                    context, limit=5
                )
                parameters["memory_context"] = memory_context

            # Get concept context
            concept_clusters = self.concept_manager.get_relevant_clusters(context)
            parameters["concept_clusters"] = concept_clusters

            # Execute plugin (mock implementation for now)
            logger.info(f"🚀 Executing plugin '{plugin_name}' with enhanced context")

            # Track execution
            execution_record = {
                "plugin_name": plugin_name,
                "context": context,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
            }
            self.execution_history.append(execution_record)

            return {
                "status": "success",
                "result": f"Plugin '{plugin_name}' executed successfully with enhanced context",
                "context_used": {
                    "memory_fragments": len(parameters.get("memory_context", [])),
                    "concept_clusters": len(concept_clusters),
                },
            }

        except Exception as e:
            logger.error(f"❌ Plugin execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def get_execution_stats(self):
        """Get plugin execution statistics"""
        total_executions = len(self.execution_history)
        successful_executions = len(
            [ex for ex in self.execution_history if ex["status"] == "success"]
        )

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions
            if total_executions > 0
            else 0,
            "recent_executions": self.execution_history[-5:]
            if self.execution_history
            else [],
        }


class UnifiedCognitiveArchitectureManager:
    """
    High-level manager for the unified cognitive architecture
    Coordinates all cognitive systems with proper adapters
    """

    def __init__(self, workspace_path: str = ""):
        self.workspace_path = workspace_path
        self.systems = {}
        self.adapters = {}

        logger.info("🧠 Unified Cognitive Architecture Manager initialized")

    def register_system(
        self, system_name: str, system_instance: Any, adapter_class=None
    ):
        """Register a cognitive system with optional adapter"""
        self.systems[system_name] = system_instance

        if adapter_class:
            adapter = adapter_class(system_instance)
            self.adapters[system_name] = adapter
            logger.info(f"🔗 Registered system '{system_name}' with adapter")
        else:
            logger.info(f"📝 Registered system '{system_name}' directly")

    def get_system(self, system_name: str, use_adapter: bool = True):
        """Get system instance, optionally through adapter"""
        if use_adapter and system_name in self.adapters:
            return self.adapters[system_name]
        return self.systems.get(system_name)

    def get_system_status(self):
        """Get status of all registered systems"""
        status = {
            "registered_systems": list(self.systems.keys()),
            "adapted_systems": list(self.adapters.keys()),
            "total_systems": len(self.systems),
        }

        # Add individual system health checks if available
        for system_name, system in self.systems.items():
            try:
                if hasattr(system, "get_health_status"):
                    status[f"{system_name}_health"] = system.get_health_status()
                else:
                    status[f"{system_name}_health"] = "operational"
            except Exception as e:
                status[f"{system_name}_health"] = f"error: {e}"

        return status

    async def process_with_unified_context(
        self, request: str, system_preferences: Optional[List[str]] = None
    ):
        """Process request using unified cognitive context from all systems"""
        try:
            context = {
                "request": request,
                "timestamp": datetime.now().isoformat(),
                "systems_involved": [],
            }

            # Collect context from all available systems
            for system_name, system in self.systems.items():
                if system_preferences and system_name not in system_preferences:
                    continue

                try:
                    if hasattr(system, "get_context"):
                        system_context = (
                            await system.get_context()
                            if asyncio.iscoroutinefunction(system.get_context)
                            else system.get_context()
                        )
                        context[f"{system_name}_context"] = system_context
                        context["systems_involved"].append(system_name)
                except Exception as e:
                    logger.warning(f"⚠️ Could not get context from {system_name}: {e}")

            return {
                "status": "success",
                "unified_context": context,
                "systems_used": len(context["systems_involved"]),
            }

        except Exception as e:
            logger.error(f"❌ Unified context processing failed: {e}")
            return {"status": "error", "error": str(e)}


# Convenience function to set up the complete unified architecture
def create_unified_cognitive_architecture(workspace_path: str = ""):
    """
    Factory function to create a complete unified cognitive architecture
    with all adapters and compatibility layers
    """
    manager = UnifiedCognitiveArchitectureManager(workspace_path)

    # This would be called by the main integration code to set up everything
    logger.info("🎯 Creating unified cognitive architecture with all adapters")

    return manager


if __name__ == "__main__":
    # Demo of adapter usage
    print("🔗 Unified Cognitive Architecture Adapters Demo")
    print("=" * 50)

    # Create mock systems for testing
    class MockFractalMesh:
        def __init__(self):
            self.name = "FractalMesh"

    class MockPluginManager:
        def __init__(self):
            self.name = "PluginManager"

    # Test the adapters
    manager = create_unified_cognitive_architecture("test_workspace")

    # Register systems with adapters
    mock_fractal = MockFractalMesh()
    mock_plugins = MockPluginManager()

    manager.register_system("fractal_memory", mock_fractal, FractalMeshToLyrixaAdapter)
    manager.register_system("plugin_system", mock_plugins)

    # Show status
    status = manager.get_system_status()
    print("System Status:", status)

    print("✅ Adapter demo complete!")
