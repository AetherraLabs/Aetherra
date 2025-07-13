from typing import Any, Dict, Optional

from .agent_base import AgentBase, AgentResponse


class PluginAgent(AgentBase):
    """Agent responsible for plugin discovery, recommendation, and usage assistance"""

    def __init__(self, memory, prompt_engine, llm_manager):
        super().__init__("PluginAgent", "Assists with plugin discovery and usage")
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager

        self.plugin_registry = {}
        self.plugin_usage_stats = {}
        self.recommended_plugins = []

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process plugin-related input"""
        context = context or {}

        try:
            input_lower = input_text.lower()

            if "find" in input_lower or "search" in input_lower:
                result = await self._search_plugins(input_text, context)
            elif "recommend" in input_lower or "suggest" in input_lower:
                result = await self._recommend_plugins(input_text, context)
            elif "install" in input_lower:
                result = await self._install_plugin(input_text, context)
            elif "list" in input_lower:
                result = await self._list_plugins(context)
            else:
                result = await self._general_plugin_help(input_text, context)

            self._increment_success()
            return result

        except Exception as e:
            self.log(f"Error processing plugin input: {e}", "ERROR")
            self._increment_error()

            return AgentResponse(
                content=f"I encountered an error with plugin operations: {str(e)}",
                confidence=0.0,
                agent_name=self.name,
                metadata={"error": str(e)},
            )

    async def _search_plugins(
        self, query: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Search for plugins based on query"""
        # Extract search terms from query
        search_terms = query.lower().replace("find", "").replace("search", "").strip()

        # Mock plugin search results
        mock_plugins = [
            {
                "name": "file_tools",
                "description": "File manipulation and management tools",
            },
            {
                "name": "math_plugin",
                "description": "Mathematical calculations and operations",
            },
            {
                "name": "memory_plugin",
                "description": "Enhanced memory storage and retrieval",
            },
            {
                "name": "search_plugin",
                "description": "Web search and information retrieval",
            },
            {
                "name": "system_plugin",
                "description": "System monitoring and management",
            },
        ]

        # Simple keyword matching
        matching_plugins = []
        for plugin in mock_plugins:
            if any(
                term in plugin["description"].lower() for term in search_terms.split()
            ):
                matching_plugins.append(plugin)

        if not matching_plugins:
            return AgentResponse(
                content=f"No plugins found matching '{search_terms}'. Try searching for 'file', 'math', 'memory', 'search', or 'system'.",
                confidence=0.7,
                agent_name=self.name,
                metadata={"search_terms": search_terms, "results": []},
            )

        result_text = (
            f"Found {len(matching_plugins)} plugins matching '{search_terms}':\n\n"
        )
        for plugin in matching_plugins:
            result_text += f"• {plugin['name']}: {plugin['description']}\n"

        return AgentResponse(
            content=result_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"search_terms": search_terms, "results": matching_plugins},
        )

    async def _recommend_plugins(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Recommend plugins based on user needs"""
        # Analyze user input to understand what they need
        needs = input_text.lower()

        recommendations = []

        if "file" in needs or "document" in needs:
            recommendations.append(
                {
                    "name": "file_tools",
                    "reason": "Helps with file operations and document management",
                }
            )

        if "calculate" in needs or "math" in needs:
            recommendations.append(
                {
                    "name": "math_plugin",
                    "reason": "Provides mathematical calculation capabilities",
                }
            )

        if "remember" in needs or "memory" in needs:
            recommendations.append(
                {
                    "name": "memory_plugin",
                    "reason": "Enhances memory storage and recall functionality",
                }
            )

        if "search" in needs or "find" in needs:
            recommendations.append(
                {
                    "name": "search_plugin",
                    "reason": "Enables web search and information retrieval",
                }
            )

        if not recommendations:
            recommendations = [
                {
                    "name": "system_plugin",
                    "reason": "Good general-purpose system monitoring tool",
                }
            ]

        result_text = "Plugin Recommendations:\n\n"
        for rec in recommendations:
            result_text += f"• {rec['name']}: {rec['reason']}\n"

        return AgentResponse(
            content=result_text,
            confidence=0.8,
            agent_name=self.name,
            metadata={"recommendations": recommendations},
        )

    async def _install_plugin(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Install a plugin"""
        # Extract plugin name from input
        plugin_name = input_text.lower().replace("install", "").strip()

        # Mock installation process
        result_text = f"Installing plugin: {plugin_name}\n"
        result_text += "✅ Plugin installed successfully!\n"
        result_text += "The plugin is now available for use."

        return AgentResponse(
            content=result_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"installed_plugin": plugin_name},
        )

    async def _list_plugins(self, context: Dict[str, Any]) -> AgentResponse:
        """List available plugins"""
        # Mock plugin list
        plugins = [
            "file_tools - File manipulation and management",
            "math_plugin - Mathematical calculations",
            "memory_plugin - Enhanced memory operations",
            "search_plugin - Web search capabilities",
            "system_plugin - System monitoring",
        ]

        result_text = "Available Plugins:\n\n"
        for plugin in plugins:
            result_text += f"• {plugin}\n"

        return AgentResponse(
            content=result_text,
            confidence=1.0,
            agent_name=self.name,
            metadata={"plugin_count": len(plugins)},
        )

    async def _general_plugin_help(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Provide general plugin help"""
        help_text = """Plugin Assistant Help:

I can help you with:
• Search for plugins: "find plugins for file management"
• Get recommendations: "recommend plugins for my needs"
• Install plugins: "install math_plugin"
• List available plugins: "list all plugins"

What would you like to do with plugins?"""

        return AgentResponse(
            content=help_text,
            confidence=0.9,
            agent_name=self.name,
            metadata={"help_type": "general"},
        )
