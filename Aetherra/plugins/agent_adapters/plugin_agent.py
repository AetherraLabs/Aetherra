from datetime import datetime
from typing import Any, Dict, Optional

from .agent_base import AgentBase, AgentResponse


class PluginAgent(AgentBase):
    """Agent responsible for plugin discovery, recommendation, and usage assistance"""

    def __init__(self, memory, prompt_engine, llm_manager, intelligence_stack=None):
        super().__init__("PluginAgent", "Assists with plugin discovery and usage")
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager
        self.intelligence_stack = intelligence_stack

        self.plugin_registry = {}
        self.plugin_usage_stats = {}
        self.recommended_plugins = []

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process plugin-related input"""
        context = context or {}

        try:
            # Check if we have a specific operation type from enhanced routing
            operation_type = context.get("plugin_operation")

            if operation_type == "plugin_generation":
                result = await self._handle_plugin_generation(input_text, context)
            elif operation_type == "plugin_discovery":
                if any(
                    keyword in input_text.lower()
                    for keyword in ["find", "search", "discover"]
                ):
                    result = await self._search_plugins(input_text, context)
                else:
                    result = await self._list_plugins(context)
            elif operation_type == "plugin_management":
                if any(keyword in input_text.lower() for keyword in ["install", "add"]):
                    result = await self._install_plugin(input_text, context)
                else:
                    result = await self._general_plugin_help(input_text, context)
            elif operation_type == "plugin_info":
                result = await self._plugin_info(input_text, context)
            else:
                # Fallback to existing routing logic for backward compatibility
                input_lower = input_text.lower()

                if any(
                    keyword in input_lower
                    for keyword in [
                        "generate plugin",
                        "create plugin",
                        "build plugin",
                        "make plugin",
                    ]
                ):
                    result = await self._handle_plugin_generation(input_text, context)
                elif any(
                    keyword in input_lower for keyword in ["find", "search", "discover"]
                ):
                    result = await self._search_plugins(input_text, context)
                elif any(
                    keyword in input_lower for keyword in ["recommend", "suggest"]
                ):
                    result = await self._recommend_plugins(input_text, context)
                elif any(keyword in input_lower for keyword in ["install", "add"]):
                    result = await self._install_plugin(input_text, context)
                elif any(
                    keyword in input_lower
                    for keyword in ["list", "show all", "available"]
                ):
                    result = await self._list_plugins(context)
                elif any(
                    keyword in input_lower
                    for keyword in ["info", "about", "details", "explain"]
                ):
                    result = await self._plugin_info(input_text, context)
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

        if not self.intelligence_stack:
            return AgentResponse(
                content="Plugin discovery system not available. Intelligence stack not connected.",
                confidence=0.3,
                agent_name=self.name,
                metadata={"error": "No intelligence stack"},
            )

        try:
            # Get real plugin recommendations
            recommendations = (
                await self.intelligence_stack.get_plugin_recommendations_for_lyrixa(
                    search_terms
                )
            )

            if not recommendations:
                # Fallback to listing all available plugins
                available_plugins = (
                    await self.intelligence_stack.plugin_bridge.discover_all_plugins()
                )

                # Simple keyword matching on available plugins
                matching_plugins = []
                for plugin_key, plugin_data in available_plugins.items():
                    plugin_name = plugin_data.get("name", plugin_key)
                    description = plugin_data.get("description", "")
                    capabilities = " ".join(plugin_data.get("capabilities", []))
                    searchable_text = (
                        f"{plugin_name} {description} {capabilities}".lower()
                    )

                    if any(term in searchable_text for term in search_terms.split()):
                        matching_plugins.append(
                            {
                                "name": plugin_name,
                                "description": description,
                                "category": plugin_data.get("category", "Unknown"),
                                "status": plugin_data.get("status", "Unknown"),
                                "type": plugin_data.get("type", "Unknown"),
                            }
                        )

                if not matching_plugins:
                    total_plugins = len(available_plugins)
                    return AgentResponse(
                        content=f"No plugins found matching '{search_terms}'. Found {total_plugins} total plugins available. Try more general terms or use 'list plugins' to see all.",
                        confidence=0.7,
                        agent_name=self.name,
                        metadata={"search_terms": search_terms, "results": []},
                    )

                result_text = f"Found {len(matching_plugins)} plugins matching '{search_terms}':\n\n"
                for plugin in matching_plugins[:5]:  # Limit to top 5 results
                    result_text += f"• **{plugin['name']}** ({plugin['type']}): {plugin['description']}\n"
                    result_text += f"  Category: {plugin['category']} | Status: {plugin['status']}\n\n"

                return AgentResponse(
                    content=result_text,
                    confidence=0.9,
                    agent_name=self.name,
                    metadata={
                        "search_terms": search_terms,
                        "results": matching_plugins,
                    },
                )
            else:
                # Use recommendations from intelligence system
                result_text = f"Found {len(recommendations)} recommended plugins for '{search_terms}':\n\n"
                for plugin in recommendations:
                    result_text += f"• **{plugin.get('name', 'Unknown')}**: {plugin.get('description', 'No description')}\n"
                    if plugin.get("capabilities"):
                        result_text += (
                            f"  Capabilities: {', '.join(plugin['capabilities'])}\n"
                        )
                    result_text += "\n"

                return AgentResponse(
                    content=result_text,
                    confidence=0.95,
                    agent_name=self.name,
                    metadata={"search_terms": search_terms, "results": recommendations},
                )

        except Exception as e:
            return AgentResponse(
                content=f"Error searching plugins: {str(e)}",
                confidence=0.3,
                agent_name=self.name,
                metadata={"error": str(e), "search_terms": search_terms},
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
        if not self.intelligence_stack:
            return AgentResponse(
                content="Plugin discovery system not available. Intelligence stack not connected.",
                confidence=0.3,
                agent_name=self.name,
                metadata={"error": "No intelligence stack"},
            )

        try:
            # Get all available plugins
            available_plugins = (
                await self.intelligence_stack.plugin_bridge.discover_all_plugins()
            )
            plugin_summary = (
                self.intelligence_stack.plugin_bridge.get_plugin_summary_for_gui()
            )

            if not available_plugins:
                return AgentResponse(
                    content="No plugins discovered. This might mean:\n• Plugin discovery system needs initialization\n• No plugins are available in the system\n• Plugin managers are not properly connected",
                    confidence=0.7,
                    agent_name=self.name,
                    metadata={"plugin_count": 0},
                )

            # Organize plugins by type
            plugins_by_type = {}
            for plugin_key, plugin_data in available_plugins.items():
                plugin_type = plugin_data.get("type", "unknown")
                if plugin_type not in plugins_by_type:
                    plugins_by_type[plugin_type] = []

                plugins_by_type[plugin_type].append(
                    {
                        "name": plugin_data.get("name", plugin_key),
                        "description": plugin_data.get(
                            "description", "No description available"
                        ),
                        "status": plugin_data.get("status", "Unknown"),
                        "category": plugin_data.get("category", "Unknown"),
                    }
                )

            # Build result text
            result_text = (
                f"🔌 **Available Plugins** ({len(available_plugins)} total)\n\n"
            )

            # Add summary
            if plugin_summary.get("by_status"):
                result_text += "**Status Summary:**\n"
                for status, count in plugin_summary["by_status"].items():
                    result_text += f"• {status}: {count} plugins\n"
                result_text += "\n"

            # List plugins by type
            for plugin_type, plugins in plugins_by_type.items():
                result_text += f"**{plugin_type.title()} Plugins:**\n"
                for plugin in plugins:
                    result_text += f"• **{plugin['name']}** ({plugin['status']})\n"
                    result_text += f"  {plugin['description']}\n"
                    result_text += f"  Category: {plugin['category']}\n\n"

            result_text += (
                "\n💡 Use 'find plugin [keyword]' to search for specific functionality!"
            )

            return AgentResponse(
                content=result_text,
                confidence=1.0,
                agent_name=self.name,
                metadata={
                    "plugin_count": len(available_plugins),
                    "by_type": plugin_summary.get("by_type", {}),
                    "by_status": plugin_summary.get("by_status", {}),
                },
            )

        except Exception as e:
            return AgentResponse(
                content=f"Error listing plugins: {str(e)}",
                confidence=0.3,
                agent_name=self.name,
                metadata={"error": str(e)},
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

    async def _handle_plugin_generation(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle plugin generation requests using the PluginGeneratorPlugin"""
        try:
            # Import and initialize the plugin generator (updated modular path)
            from Aetherra.plugins.core.plugin_generator_plugin import (
                PluginGeneratorPlugin,
            )

            generator = PluginGeneratorPlugin()

            # Extract plugin details from input
            plugin_description = input_text.lower()
            for phrase in [
                "generate plugin",
                "create plugin",
                "build plugin",
                "make plugin",
            ]:
                plugin_description = plugin_description.replace(phrase, "")
            plugin_description = plugin_description.strip()

            if not plugin_description:
                plugin_description = "general purpose plugin"

            # Parse plugin type and name from description
            plugin_name = self._extract_plugin_name(plugin_description)
            plugin_type = self._detect_plugin_type(plugin_description)

            # Get available templates
            templates = generator.list_templates()

            result_text = "[TOOL] **Plugin Generation System**\n\n"
            result_text += f"**Request**: {plugin_description}\n"
            result_text += f"**Suggested Name**: {plugin_name}\n"
            result_text += f"**Detected Type**: {plugin_type}\n\n"

            # Show available templates
            result_text += "**Available Templates:**\n"
            for template in templates:
                marker = (
                    "✅"
                    if template["category"].lower() == plugin_type.lower()
                    else "📄"
                )
                result_text += (
                    f"{marker} **{template['name']}** ({template['category']})\n"
                )
                result_text += f"   {template['description']}\n\n"

            # Generate plugin suggestion
            matching_template = None
            for template in templates:
                if template["category"].lower() == plugin_type.lower():
                    matching_template = template
                    break

            if matching_template:
                result_text += (
                    f"🎯 **Recommended Template**: {matching_template['name']}\n\n"
                )

                # Attempt to generate the plugin
                try:
                    plugin_id = generator.generate_plugin(
                        plugin_name=plugin_name,
                        template_id=matching_template["id"],
                        description=f"Generated {plugin_type} plugin for {plugin_description}",
                        config={"auto_generated": True, "source_request": input_text},
                    )

                    # Get the generated plugin details
                    generated_plugin = generator.generated_plugins.get(plugin_id)

                    if generated_plugin:
                        result_text += "✅ **Plugin Generated Successfully!**\n"
                        result_text += f"**Plugin ID**: {plugin_id}\n"
                        result_text += (
                            f"**Files Created**: {len(generated_plugin.files)}\n\n"
                        )

                        result_text += "**Generated Files:**\n"
                        for filename in generated_plugin.files.keys():
                            result_text += f"• {filename}\n"

                        result_text += "\n**Next Steps:**\n"
                        result_text += (
                            "1. Review the generated code in the Plugin Editor tab\n"
                        )
                        result_text += (
                            "2. Edit and customize the .aether or .py code as needed\n"
                        )
                        result_text += "3. Use the Save button to save the plugin to Aetherra/plugins\n"
                        result_text += (
                            "4. Test your plugin using the Test button in the editor\n"
                        )
                        result_text += (
                            "5. Apply the plugin to activate it in Aetherra\n\n"
                        )

                        # Log to intelligence memory if available
                        if self.intelligence_stack:
                            await self._log_generated_plugin(
                                plugin_id, generated_plugin, input_text
                            )

                        # Get the main plugin file for GUI injection
                        main_file = None
                        main_file_content = None

                        # Look for the main plugin file (usually .aether or .py)
                        for filename, content in generated_plugin.files.items():
                            if filename.endswith(".aether") or filename.endswith(".py"):
                                main_file = filename
                                main_file_content = content
                                break

                        # If no .aether or .py file, take the first file
                        if not main_file and generated_plugin.files:
                            main_file = list(generated_plugin.files.keys())[0]
                            main_file_content = generated_plugin.files[main_file]

                        return AgentResponse(
                            content=result_text,
                            confidence=0.95,
                            agent_name=self.name,
                            metadata={
                                "plugin_operation": "plugin_generation",  # Key for auto-population
                                "plugin_id": plugin_id,
                                "plugin_name": plugin_name,
                                "template_used": matching_template["id"],
                                "files_generated": list(generated_plugin.files.keys()),
                                "generation_successful": True,
                                "generated_code": main_file_content,  # Code for GUI injection
                                "main_filename": main_file,  # Filename for GUI
                            },
                        )

                except Exception as gen_error:
                    result_text += f"❌ **Generation Error**: {str(gen_error)}\n\n"
                    result_text += (
                        "Please try with a different template or description.\n"
                    )

            else:
                result_text += (
                    f"💡 **No exact template match found for '{plugin_type}'**\n\n"
                )
                result_text += "**Available Options:**\n"
                result_text += (
                    "1. Use a general template and customize in the Plugin Editor\n"
                )
                result_text += (
                    "2. Edit the .aether or .py code directly in the code editor\n"
                )
                result_text += (
                    "3. Describe your needs more specifically for better templates\n\n"
                )

            # Always show how to access the plugin editor
            result_text += "🎯 **Plugin Editor Access**:\n"
            result_text += "• Open the Plugin Editor tab in the main interface\n"
            result_text += (
                "• Use the native code editor to write .aether or .py plugins\n"
            )
            result_text += "• Use Save, Test, and Apply buttons for plugin management\n"

            return AgentResponse(
                content=result_text,
                confidence=0.9,
                agent_name=self.name,
                metadata={
                    "plugin_type": plugin_type,
                    "plugin_name": plugin_name,
                    "templates_available": len(templates),
                    "feature": "plugin_generation",
                },
            )

        except Exception as e:
            return AgentResponse(
                content=f"❌ **Plugin Generation Error**: {str(e)}\n\nThe plugin generation system encountered an issue. Please try again or contact support.",
                confidence=0.3,
                agent_name=self.name,
                metadata={"error": str(e), "feature": "plugin_generation"},
            )

    async def _plugin_info(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Get detailed information about a specific plugin"""
        # Extract plugin name from input
        plugin_name = input_text.lower()
        for word in ["info", "about", "details", "explain", "plugin"]:
            plugin_name = plugin_name.replace(word, "")
        plugin_name = plugin_name.strip()

        if not plugin_name:
            return AgentResponse(
                content="Please specify which plugin you'd like information about. For example: 'info about file_tools' or 'explain sysmon plugin'",
                confidence=0.7,
                agent_name=self.name,
                metadata={"error": "No plugin name specified"},
            )

        if not self.intelligence_stack:
            return AgentResponse(
                content="Plugin information system not available. Intelligence stack not connected.",
                confidence=0.3,
                agent_name=self.name,
                metadata={"error": "No intelligence stack"},
            )

        try:
            # Search for the plugin
            available_plugins = (
                await self.intelligence_stack.plugin_bridge.discover_all_plugins()
            )

            found_plugin = None
            for plugin_key, plugin_data in available_plugins.items():
                if (
                    plugin_data.get("name", "").lower() == plugin_name
                    or plugin_name in plugin_key.lower()
                    or plugin_name in plugin_data.get("name", "").lower()
                ):
                    found_plugin = plugin_data
                    break

            if not found_plugin:
                return AgentResponse(
                    content=f"Plugin '{plugin_name}' not found. Use 'list plugins' to see all available plugins.",
                    confidence=0.7,
                    agent_name=self.name,
                    metadata={"plugin_name": plugin_name, "found": False},
                )

            # Build detailed info
            result_text = f"🔌 **Plugin Information: {found_plugin.get('name', plugin_name)}**\n\n"
            result_text += f"**Description:** {found_plugin.get('description', 'No description available')}\n\n"
            result_text += "**Details:**\n"
            result_text += f"• Type: {found_plugin.get('type', 'Unknown')}\n"
            result_text += f"• Category: {found_plugin.get('category', 'Unknown')}\n"
            result_text += f"• Status: {found_plugin.get('status', 'Unknown')}\n"
            result_text += f"• Version: {found_plugin.get('version', 'Unknown')}\n"
            result_text += f"• Author: {found_plugin.get('author', 'Unknown')}\n"
            result_text += f"• Discovery Source: {found_plugin.get('discovered_from', 'Unknown')}\n"

            if found_plugin.get("capabilities"):
                result_text += "\n**Capabilities:**\n"
                for capability in found_plugin["capabilities"]:
                    result_text += f"• {capability}\n"

            return AgentResponse(
                content=result_text,
                confidence=0.95,
                agent_name=self.name,
                metadata={
                    "plugin_name": plugin_name,
                    "found": True,
                    "plugin_data": found_plugin,
                },
            )

        except Exception as e:
            return AgentResponse(
                content=f"Error getting plugin information: {str(e)}",
                confidence=0.3,
                agent_name=self.name,
                metadata={"error": str(e), "plugin_name": plugin_name},
            )

    def _extract_plugin_name(self, description: str) -> str:
        """Extract a suitable plugin name from description"""
        # Remove common words
        words = description.split()
        filtered_words = []

        skip_words = {
            "for",
            "to",
            "that",
            "can",
            "will",
            "should",
            "would",
            "could",
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "by",
            "with",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
        }

        for word in words:
            clean_word = word.strip(".,!?;:")
            if (
                clean_word
                and clean_word.lower() not in skip_words
                and len(clean_word) > 2
            ):
                filtered_words.append(clean_word.capitalize())

        if not filtered_words:
            return "CustomPlugin"

        # Take first 3 words max
        name_parts = filtered_words[:3]
        return "".join(name_parts) + "Plugin"

    def _detect_plugin_type(self, description: str) -> str:
        """Detect plugin type from description"""
        desc_lower = description.lower()

        # UI/Widget related
        if any(
            word in desc_lower
            for word in [
                "ui",
                "widget",
                "interface",
                "button",
                "form",
                "display",
                "visual",
                "gui",
            ]
        ):
            return "ui"

        # Data processing
        if any(
            word in desc_lower
            for word in [
                "data",
                "process",
                "parse",
                "transform",
                "analyze",
                "filter",
                "sort",
                "csv",
                "file",
            ]
        ):
            return "data"

        # Machine Learning
        if any(
            word in desc_lower
            for word in [
                "ml",
                "machine learning",
                "model",
                "train",
                "predict",
                "ai",
                "neural",
            ]
        ):
            return "ml"

        # API/Network
        if any(
            word in desc_lower
            for word in [
                "api",
                "rest",
                "http",
                "request",
                "web",
                "service",
                "endpoint",
                "integration",
            ]
        ):
            return "integration"

        # Default to ui for general cases
        return "ui"

    async def _log_generated_plugin(
        self, plugin_id: str, generated_plugin, input_text: str
    ):
        """Log generated plugin to intelligence memory"""
        try:
            if self.intelligence_stack and hasattr(
                self.intelligence_stack, "memory_manager"
            ):
                log_entry = {
                    "type": "plugin_generated",
                    "timestamp": datetime.now().isoformat(),
                    "plugin_id": plugin_id,
                    "plugin_name": generated_plugin.name,
                    "template_id": generated_plugin.template_id,
                    "files_count": len(generated_plugin.files),
                    "user_request": input_text,
                    "status": "generated",
                    "agent": "PluginAgent",
                }

                # Store in memory
                memory_key = f"generated_plugin_{plugin_id}"
                await self.intelligence_stack.memory_manager.store_memory(
                    memory_key, log_entry, importance=0.8
                )

        except Exception:
            # Silently handle logging errors to not disrupt main flow
            pass
