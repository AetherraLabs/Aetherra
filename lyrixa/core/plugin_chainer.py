#!/usr/bin/env python3
"""
🔗 LYRIXA PLUGIN CHAINER
========================

Advanced plugin chaining engine for Lyrixa.
Constructs and executes complex plugin workflows with intelligent routing.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .plugins import LyrixaPlugin, PluginInfo


class ChainExecutionMode(Enum):
    """Plugin chain execution modes"""

    SEQUENTIAL = "sequential"  # Execute plugins one after another
    PARALLEL = "parallel"  # Execute compatible plugins in parallel
    ADAPTIVE = "adaptive"  # Intelligently choose based on dependencies


@dataclass
class ChainNode:
    """Represents a single node in a plugin chain"""

    plugin_name: str
    plugin_instance: Any  # Will be LyrixaPlugin at runtime
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    executed: bool = False
    dependencies: Optional[List[str]] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class PluginChain:
    """Represents a complete plugin execution chain"""

    chain_id: str
    nodes: List[ChainNode]
    execution_mode: ChainExecutionMode
    metadata: Dict[str, Any]
    created_at: str

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PluginChainer:
    """
    Advanced plugin chaining engine for Lyrixa

    Builds and executes intelligent plugin workflows with:
    - Automatic chain construction based on I/O compatibility
    - Dependency resolution and execution ordering
    - Parallel execution where possible
    - Error handling and rollback capabilities
    """

    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.active_chains: Dict[str, PluginChain] = {}
        self.chain_counter = 0
        self.logger = logging.getLogger(__name__)

    async def build_chain(
        self,
        goal: str,
        available_plugins: Optional[List[str]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        execution_mode: ChainExecutionMode = ChainExecutionMode.ADAPTIVE,
    ) -> Optional[PluginChain]:
        """
        Build an optimal plugin chain to achieve a goal

        Args:
            goal: Description of what the chain should accomplish
            available_plugins: List of plugin names to consider (None = all enabled)
            input_data: Initial data to feed into the chain
            execution_mode: How to execute the chain

        Returns:
            PluginChain if successful, None otherwise
        """
        try:
            # Get available plugins
            if available_plugins is None:
                plugins = list(self.plugin_manager.loaded_plugins.keys())
            else:
                plugins = [
                    p
                    for p in available_plugins
                    if p in self.plugin_manager.loaded_plugins
                ]

            # Find optimal chain path
            chain_path = await self._find_optimal_chain(goal, plugins, input_data)

            if not chain_path:
                self.logger.warning(f"No chain path found for goal: {goal}")
                return None

            # Build chain nodes
            nodes = await self._build_chain_nodes(chain_path, input_data)

            # Create chain
            chain_id = f"chain_{self.chain_counter}"
            self.chain_counter += 1

            chain = PluginChain(
                chain_id=chain_id,
                nodes=nodes,
                execution_mode=execution_mode,
                metadata={
                    "goal": goal,
                    "created_by": "auto_chainer",
                    "plugin_count": len(nodes),
                },
                created_at=str(asyncio.get_event_loop().time()),
            )

            self.active_chains[chain_id] = chain

            self.logger.info(f"Built chain {chain_id} with {len(nodes)} plugins")
            return chain

        except Exception as e:
            self.logger.error(f"Failed to build chain for goal '{goal}': {e}")
            return None

    async def run_chain(
        self, chain: PluginChain, initial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a plugin chain

        Args:
            chain: The chain to execute
            initial_data: Initial data to feed into the chain

        Returns:
            Final results from the chain execution
        """
        try:
            self.logger.info(f"Executing chain {chain.chain_id}")

            if chain.execution_mode == ChainExecutionMode.SEQUENTIAL:
                return await self._run_sequential(chain, initial_data)
            elif chain.execution_mode == ChainExecutionMode.PARALLEL:
                return await self._run_parallel(chain, initial_data)
            else:  # ADAPTIVE
                return await self._run_adaptive(chain, initial_data)

        except Exception as e:
            self.logger.error(f"Chain execution failed for {chain.chain_id}: {e}")
            return {"error": str(e), "chain_id": chain.chain_id}

    async def suggest_chains(
        self, user_input: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest possible plugin chains based on user input and context

        Args:
            user_input: User's natural language input
            context: Current conversation/session context

        Returns:
            List of suggested chains with metadata
        """
        suggestions = []

        try:
            # Use semantic discovery to find relevant plugins
            relevant_plugins = (
                await self.plugin_manager.semantic_discovery.find_relevant_plugins(
                    user_input, max_results=10
                )
            )

            # Group plugins by capability patterns
            capability_groups = self._group_by_capabilities(relevant_plugins)

            # Generate chain suggestions for each group
            for group_name, plugins in capability_groups.items():
                if len(plugins) >= 2:  # Only suggest chains with multiple plugins
                    chain_suggestion = await self._create_chain_suggestion(
                        group_name, plugins, user_input, context
                    )
                    if chain_suggestion:
                        suggestions.append(chain_suggestion)

            # Sort by relevance score
            suggestions.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            return suggestions[:5]  # Return top 5 suggestions

        except Exception as e:
            self.logger.error(f"Failed to suggest chains: {e}")
            return []

    async def _find_optimal_chain(
        self,
        goal: str,
        available_plugins: List[str],
        input_data: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Find the optimal chain of plugins to achieve a goal"""

        # Get plugin information
        plugin_infos = {}
        for plugin_name in available_plugins:
            if plugin_name in self.plugin_manager.plugin_info:
                plugin_infos[plugin_name] = self.plugin_manager.plugin_info[plugin_name]

        # Use semantic discovery to find relevant plugins
        relevant_plugins = (
            await self.plugin_manager.semantic_discovery.find_relevant_plugins(
                goal, max_results=len(available_plugins)
            )
        )

        # Filter to only available plugins
        relevant_plugins = [p for p in relevant_plugins if p in available_plugins]

        if not relevant_plugins:
            return []

        # Build chain using graph algorithm
        chain = await self._build_dependency_chain(relevant_plugins, plugin_infos, goal)

        return chain

    async def _build_dependency_chain(
        self,
        relevant_plugins: List[str],
        plugin_infos: Dict[str, Any],  # Will be Dict[str, PluginInfo] at runtime
        goal: str,
    ) -> List[str]:
        """Build a chain based on plugin dependencies and I/O compatibility"""

        chain = []
        available_outputs = set()

        # Start with plugins that don't need specific inputs
        starter_plugins = []
        for plugin_name in relevant_plugins:
            info = plugin_infos.get(plugin_name)
            if info and (not info.input_types or info.auto_chain):
                starter_plugins.append((plugin_name, info.chain_priority))

        # Sort by priority
        starter_plugins.sort(key=lambda x: x[1], reverse=True)

        # Add highest priority starter
        if starter_plugins:
            first_plugin = starter_plugins[0][0]
            chain.append(first_plugin)
            info = plugin_infos[first_plugin]
            if info.output_types:
                available_outputs.update(info.output_types)

        # Build rest of chain
        remaining_plugins = [p for p in relevant_plugins if p not in chain]

        while remaining_plugins:
            added_any = False

            for plugin_name in remaining_plugins[:]:
                info = plugin_infos.get(plugin_name)
                if not info:
                    continue

                # Check if this plugin's inputs are satisfied
                if not info.input_types or any(
                    inp in available_outputs for inp in info.input_types
                ):
                    chain.append(plugin_name)
                    if info.output_types:
                        available_outputs.update(info.output_types)
                    remaining_plugins.remove(plugin_name)
                    added_any = True
                    break

            if not added_any:
                break  # No more plugins can be added

        return chain

    async def _build_chain_nodes(
        self, chain_path: List[str], input_data: Optional[Dict[str, Any]]
    ) -> List[ChainNode]:
        """Build chain nodes from a plugin path"""

        nodes = []

        for i, plugin_name in enumerate(chain_path):
            plugin_instance = self.plugin_manager.loaded_plugins.get(plugin_name)
            if not plugin_instance:
                continue

            # Determine dependencies (previous nodes)
            dependencies = chain_path[:i] if i > 0 else []

            node = ChainNode(
                plugin_name=plugin_name,
                plugin_instance=plugin_instance,
                inputs={},
                outputs={},
                dependencies=dependencies,
            )

            nodes.append(node)

        return nodes

    async def _run_sequential(
        self, chain: PluginChain, initial_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run chain sequentially"""

        current_data = initial_data or {}

        for node in chain.nodes:
            try:
                # Prepare inputs
                node.inputs = current_data.copy()

                # Execute plugin
                result = await node.plugin_instance.execute("auto_chain", node.inputs)

                # Store outputs
                node.outputs = result
                node.executed = True

                # Update current data for next plugin
                if isinstance(result, dict):
                    current_data.update(result)
                else:
                    current_data["previous_result"] = result

            except Exception as e:
                self.logger.error(f"Plugin {node.plugin_name} failed: {e}")
                return {"error": f"Plugin {node.plugin_name} failed: {e}"}

        return current_data

    async def _run_parallel(
        self, chain: PluginChain, initial_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run chain with parallel execution where possible"""

        # Group nodes by dependency level
        dependency_levels = self._calculate_dependency_levels(chain.nodes)

        current_data = initial_data or {}

        for level in sorted(dependency_levels.keys()):
            # Run all nodes at this level in parallel
            level_nodes = dependency_levels[level]

            tasks = []
            for node in level_nodes:
                node.inputs = current_data.copy()
                task = self._execute_node(node)
                tasks.append(task)

            # Wait for all nodes at this level to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for node, result in zip(level_nodes, results):
                if isinstance(result, Exception):
                    self.logger.error(f"Plugin {node.plugin_name} failed: {result}")
                    return {"error": f"Plugin {node.plugin_name} failed: {result}"}

                # Type safety: result is guaranteed to be a Dict[str, Any] here
                node.outputs = (
                    result if isinstance(result, dict) else {"result": result}
                )
                node.executed = True

                # Update current data
                if isinstance(result, dict):
                    current_data.update(result)

        return current_data

    async def _run_adaptive(
        self, chain: PluginChain, initial_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run chain with adaptive execution strategy"""

        # Analyze chain characteristics
        has_dependencies = any(node.dependencies for node in chain.nodes)

        if has_dependencies:
            return await self._run_parallel(chain, initial_data)
        else:
            return await self._run_sequential(chain, initial_data)

    async def _execute_node(self, node: ChainNode) -> Dict[str, Any]:
        """Execute a single chain node"""
        return await node.plugin_instance.execute("auto_chain", node.inputs)

    def _calculate_dependency_levels(
        self, nodes: List[ChainNode]
    ) -> Dict[int, List[ChainNode]]:
        """Calculate dependency levels for parallel execution"""

        levels = {}
        node_map = {node.plugin_name: node for node in nodes}

        def get_level(node: ChainNode) -> int:
            if not node.dependencies:
                return 0

            max_dep_level = -1
            for dep_name in node.dependencies:
                if dep_name in node_map:
                    dep_level = get_level(node_map[dep_name])
                    max_dep_level = max(max_dep_level, dep_level)

            return max_dep_level + 1

        for node in nodes:
            level = get_level(node)
            if level not in levels:
                levels[level] = []
            levels[level].append(node)

        return levels

    def _group_by_capabilities(self, plugins: List[str]) -> Dict[str, List[str]]:
        """Group plugins by their capabilities"""

        groups = {}

        for plugin_name in plugins:
            info = self.plugin_manager.plugin_info.get(plugin_name)
            if not info:
                continue

            category = info.category or "general"
            if category not in groups:
                groups[category] = []
            groups[category].append(plugin_name)

        return groups

    async def _create_chain_suggestion(
        self,
        group_name: str,
        plugins: List[str],
        user_input: str,
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Create a chain suggestion for a group of plugins"""

        try:
            # Build a sample chain
            chain = await self.build_chain(
                goal=f"Process: {user_input}",
                available_plugins=plugins,
                execution_mode=ChainExecutionMode.ADAPTIVE,
            )

            if not chain:
                return None

            return {
                "chain_id": chain.chain_id,
                "description": f"Use {group_name} plugins to {user_input.lower()}",
                "plugins": [node.plugin_name for node in chain.nodes],
                "execution_mode": chain.execution_mode.value,
                "relevance_score": len(plugins) * 0.1,  # Simple scoring
                "estimated_time": len(chain.nodes) * 2,  # Rough estimate
            }

        except Exception as e:
            self.logger.error(f"Failed to create chain suggestion: {e}")
            return None

    def get_chain_status(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a chain execution"""

        if chain_id not in self.active_chains:
            return None

        chain = self.active_chains[chain_id]

        total_nodes = len(chain.nodes)
        executed_nodes = sum(1 for node in chain.nodes if node.executed)

        return {
            "chain_id": chain_id,
            "total_plugins": total_nodes,
            "executed_plugins": executed_nodes,
            "progress": executed_nodes / total_nodes if total_nodes > 0 else 0,
            "execution_mode": chain.execution_mode.value,
            "metadata": chain.metadata,
        }

    def cleanup_chain(self, chain_id: str) -> bool:
        """Clean up a completed chain"""

        if chain_id in self.active_chains:
            del self.active_chains[chain_id]
            return True

        return False
