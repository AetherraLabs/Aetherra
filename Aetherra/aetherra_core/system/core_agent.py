from typing import Any, Dict, Optional

try:
    # Try relative imports first (when used as a package)
    from Aetherra.aetherra_core.system.core_migrated.agents.agents.escalation_agent import (
        EscalationAgent,
    )
    from Aetherra.aetherra_core.system.core_migrated.agents.agents.goal_agent import (
        GoalAgent,
    )
    from Aetherra.aetherra_core.system.core_migrated.agents.agents.reflection_agent import (
        ReflectionAgent,
    )
    from Aetherra.aetherra_core.system.core_migrated.agents.agents.self_evaluation_agent import (
        SelfEvaluationAgent,
    )
    from Aetherra.plugins.agent_adapters.agent_base import AgentBase, AgentResponse
    from Aetherra.plugins.agent_adapters.plugin_agent import PluginAgent
except ImportError:
    # Fall back to absolute imports (when imported directly)
    try:
        from Aetherra.aetherra_core.system.core_migrated.agents.agents.escalation_agent import (
            EscalationAgent,
        )
        from Aetherra.aetherra_core.system.core_migrated.agents.agents.goal_agent import (
            GoalAgent,
        )
        from Aetherra.aetherra_core.system.core_migrated.agents.agents.reflection_agent import (
            ReflectionAgent,
        )
        from Aetherra.aetherra_core.system.core_migrated.agents.agents.self_evaluation_agent import (
            SelfEvaluationAgent,
        )
        from Aetherra.plugins.agent_adapters.agent_base import AgentBase, AgentResponse
        from Aetherra.plugins.agent_adapters.plugin_agent import PluginAgent
    except ImportError:
        # If all imports fail, create placeholder classes for graceful degradation
        print("⚠️ Agent dependencies not available, using placeholder classes")
        from datetime import datetime

        class AgentBase:
            def __init__(self, *args, **kwargs):
                self.name = kwargs.get("name", "placeholder")

            def log(self, message):
                print(f"[{self.name}] {message}")

            def process(self, input_data, context=None):
                return AgentResponse("Agent not available", "placeholder")

        class AgentResponse:
            def __init__(
                self,
                content="",
                agent_type="placeholder",
                confidence=0.0,
                agent_name="",
                metadata=None,
            ):
                self.content = content
                self.agent_type = agent_type
                self.confidence = confidence
                self.agent_name = agent_name
                self.metadata = metadata or {}
                self.timestamp = datetime.now()

        # Create placeholder classes for all agents
        EscalationAgent = GoalAgent = PluginAgent = ReflectionAgent = (
            SelfEvaluationAgent
        ) = AgentBase


class LyrixaAI(AgentBase):
    """
    Main LyrixaAI interface agent - coordinates all other agents
    """

    def __init__(
        self,
        runtime,
        memory,
        prompt_engine,
        llm_manager,
        intelligence_stack=None,
        gui_interface=None,
    ):
        super().__init__("LyrixaAI", "Main AI coordination agent")
        self.runtime = runtime
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager
        self.intelligence_stack = intelligence_stack
        self.gui_interface = (
            gui_interface  # Reference to GUI window for auto-population
        )

        # Initialize sub-agents
        self.goal_agent = GoalAgent(memory, prompt_engine, llm_manager)
        self.plugin_agent = PluginAgent(
            memory, prompt_engine, llm_manager, intelligence_stack
        )
        self.reflection_agent = ReflectionAgent(memory, prompt_engine, llm_manager)
        self.escalation_agent = EscalationAgent(memory, prompt_engine, llm_manager)
        self.self_evaluation_agent = SelfEvaluationAgent(
            memory, prompt_engine, llm_manager
        )

        self.agents = {
            "goal": self.goal_agent,
            "plugin": self.plugin_agent,
            "reflection": self.reflection_agent,
            "escalation": self.escalation_agent,
            "self_evaluation": self.self_evaluation_agent,
        }

        self.active_tasks = {}
        self.conversation_history = []

    async def initialize(self):
        """Initialize all sub-agents"""
        self.log("Initializing LyrixaAI and sub-agents...")

        for agent_name, agent in self.agents.items():
            try:
                await agent.initialize()
                self.log(f"✅ {agent_name} agent initialized")
            except Exception as e:
                self.log(f"❌ Failed to initialize {agent_name} agent: {e}")

        self.log("✅ LyrixaAI initialization complete")

    async def process_input(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process user input and route to appropriate agent"""
        context = context or {}

        # Determine which agent should handle this input
        agent_name = await self._route_to_agent(input_text, context)
        agent = self.agents.get(agent_name)

        if not agent or agent_name == "main":
            agent = self  # Use main agent for general conversation
            agent_name = "LyrixaAI"

        try:
            if agent == self:
                response = await self._handle_general_input(input_text, context)
            else:
                response = await agent.process_input(input_text, context)

            # Store in conversation history
            self.conversation_history.append(
                {
                    "input": input_text,
                    "response": response.content,
                    "agent": agent_name,
                    "timestamp": response.timestamp.isoformat()
                    if response.timestamp
                    else None,
                }
            )

            # Check and auto-populate GUI if needed
            await self._check_and_auto_populate_gui(response, input_text)

            return response

        except Exception as e:
            self.log(f"❌ Error processing input with {agent_name}: {e}")
            return AgentResponse(
                content=f"I encountered an error processing your request: {str(e)}",
                confidence=0.0,
                agent_name=agent_name,
                metadata={"error": str(e)},
            )

    async def _route_to_agent(self, user_input: str, context: Dict[str, Any]) -> str:
        """Determine which agent should handle the input"""
        input_lower = user_input.lower()

        # Enhanced plugin routing
        plugin_route = await self._enhanced_plugin_routing(user_input)
        if plugin_route:
            # Pass the specific plugin operation type as context
            context["plugin_operation"] = plugin_route
            return "plugin"

        # Goal-related keywords - Only route to goal agent for specific goal commands
        if any(
            keyword in input_lower
            for keyword in [
                "create goal",
                "new goal",
                "set goal",
                "add goal",
                "goal:",
                "my goal is",
                "i want to achieve",
            ]
        ):
            return "goal"

        # Plugin-related keywords (fallback for basic plugin requests)
        if any(
            keyword in input_lower
            for keyword in [
                "show plugins",
                "list plugins",
                "find plugin",
                "plugin for",
                "what plugins",
                "available tools",
            ]
        ):
            return "plugin"

        # Reflection-related keywords - More specific
        if any(
            keyword in input_lower
            for keyword in [
                "reflect on",
                "analyze my",
                "review my performance",
                "how am i doing",
                "performance report",
            ]
        ):
            return "reflection"

        # Self-evaluation keywords - More specific
        if any(
            keyword in input_lower
            for keyword in [
                "evaluate my",
                "assess my",
                "how can i improve",
                "self assessment",
                "learning progress",
            ]
        ):
            return "self_evaluation"

        # Escalation keywords - Only for actual problems
        if any(
            keyword in input_lower
            for keyword in [
                "error occurred",
                "system failed",
                "not working",
                "broken",
                "critical error",
                "urgent issue",
                "something wrong",
            ]
        ):
            return "escalation"

        # Default to main agent for general conversation
        return "main"

    async def _handle_general_input(
        self, input_text: str, context: Dict[str, Any]
    ) -> AgentResponse:
        """Handle general input that doesn't route to specific agents"""
        input_lower = input_text.lower().strip()

        # Handle common greetings and casual conversation
        if any(
            greeting in input_lower
            for greeting in [
                "hello",
                "hi",
                "hey",
                "good morning",
                "good afternoon",
                "good evening",
            ]
        ):
            response_content = f"Hello! 👋 I'm Lyrixa, your modular AI assistant. Nice to meet you! I'm ready to help with anything you need. What's on your mind today?"

        elif any(
            word in input_lower
            for word in ["how are you", "how's it going", "what's up"]
        ):
            response_content = "I'm doing great! All my systems are running smoothly and I'm ready to assist. My 5 specialist agents are standing by to help with goals, plugins, analysis, problem-solving, and self-improvement. How are you doing?"

        elif any(
            word in input_lower
            for word in [
                "what can you do",
                "what are your capabilities",
                "help me",
                "what do you do",
            ]
        ):
            response_content = """I'm Lyrixa, a modular AI assistant with specialized capabilities! Here's what I can help you with:

🎯 **Goal Management** - Create, track, and manage your objectives
🔌 **Plugin Discovery** - Find and recommend tools for your tasks
� **Performance Analysis** - Analyze and reflect on your progress
⚠️ **Problem Solving** - Help troubleshoot issues and escalate when needed
📊 **Self-Improvement** - Learn from feedback and continuously improve

I use multiple AI models (currently GPT-4o) and can switch between them as needed. Just tell me what you'd like to work on!"""

        elif any(word in input_lower for word in ["thanks", "thank you", "appreciate"]):
            response_content = "You're very welcome! I'm here whenever you need assistance. Feel free to ask me anything - whether it's casual conversation or help with specific tasks. 😊"

        elif any(
            word in input_lower for word in ["bye", "goodbye", "see you", "talk later"]
        ):
            response_content = "Goodbye! It was great talking with you. I'll be here whenever you need me. Have a wonderful day! 👋"

        else:
            # For other general conversation, provide a thoughtful response
            response_content = f"I understand you said: \"{input_text}\"\n\nI'm here to help! While I specialize in goal management, plugin assistance, and performance analysis, I'm also happy to have a conversation. Is there something specific I can help you with, or would you like to know more about my capabilities?"

        return AgentResponse(
            content=response_content,
            confidence=0.9,
            agent_name=self.name,
            metadata={"conversation_type": "general", "input": input_text},
        )

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status from all agents"""
        status = {
            "main_agent": {
                "active_tasks": len(self.active_tasks),
                "conversation_history": len(self.conversation_history),
            }
        }

        for agent_name, agent in self.agents.items():
            try:
                agent_status = await agent.get_status()
                status[agent_name] = agent_status
            except Exception as e:
                status[agent_name] = {"error": str(e), "status": "error"}

        return status

    async def shutdown(self):
        """Shutdown all agents gracefully"""
        self.log("Shutting down LyrixaAI...")

        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
                self.log(f"✅ {agent_name} agent shutdown")
            except Exception as e:
                self.log(f"❌ Error shutting down {agent_name} agent: {e}")

        self.log("✅ LyrixaAI shutdown complete")

    def set_intelligence_stack(self, intelligence_stack):
        """Set the intelligence stack for plugin access"""
        self.intelligence_stack = intelligence_stack
        if self.plugin_agent:
            self.plugin_agent.intelligence_stack = intelligence_stack

    async def get_available_plugins(self) -> Dict[str, Any]:
        """Get all available plugins from the intelligence stack"""
        if not self.intelligence_stack or not hasattr(
            self.intelligence_stack, "plugin_bridge"
        ):
            return {"error": "Plugin bridge not available", "plugins": []}

        try:
            if self.intelligence_stack.plugin_bridge:
                discovered_plugins = (
                    await self.intelligence_stack.plugin_bridge.discover_all_plugins()
                )
                plugin_summary = (
                    self.intelligence_stack.plugin_bridge.get_plugin_summary_for_gui()
                )

                return {
                    "total_plugins": len(discovered_plugins),
                    "plugins": list(discovered_plugins.values()),
                    "summary": plugin_summary,
                    "by_type": plugin_summary.get("by_type", {}),
                    "by_status": plugin_summary.get("by_status", {}),
                }
            else:
                return {"error": "Plugin bridge not initialized", "plugins": []}
        except Exception as e:
            return {"error": f"Failed to get plugins: {str(e)}", "plugins": []}

    async def summarize_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Get detailed summary of a specific plugin"""
        if not self.intelligence_stack or not hasattr(
            self.intelligence_stack, "plugin_bridge"
        ):
            return {"error": "Plugin bridge not available"}

        try:
            if self.intelligence_stack.plugin_bridge:
                discovered_plugins = (
                    await self.intelligence_stack.plugin_bridge.discover_all_plugins()
                )

                # Find plugin by name (search in different namespace formats)
                for plugin_key, plugin_data in discovered_plugins.items():
                    if (
                        plugin_data.get("name", "").lower() == plugin_name.lower()
                        or plugin_key.lower().endswith(f":{plugin_name.lower()}")
                        or plugin_name.lower() in plugin_key.lower()
                    ):
                        return {
                            "found": True,
                            "name": plugin_data.get("name", plugin_name),
                            "description": plugin_data.get(
                                "description", "No description available"
                            ),
                            "category": plugin_data.get("category", "Unknown"),
                            "status": plugin_data.get("status", "Unknown"),
                            "type": plugin_data.get("type", "Unknown"),
                            "capabilities": plugin_data.get("capabilities", []),
                            "version": plugin_data.get("version", "Unknown"),
                            "author": plugin_data.get("author", "Unknown"),
                            "discovery_source": plugin_data.get(
                                "discovered_from", "Unknown"
                            ),
                        }

                return {"found": False, "error": f"Plugin '{plugin_name}' not found"}
            else:
                return {"error": "Plugin bridge not initialized"}
        except Exception as e:
            return {"error": f"Failed to summarize plugin: {str(e)}"}

    async def get_plugin_recommendations(self, query: str) -> Dict[str, Any]:
        """Get plugin recommendations based on a query"""
        if not self.intelligence_stack:
            return {"error": "Intelligence stack not available", "recommendations": []}

        try:
            recommendations = (
                await self.intelligence_stack.get_plugin_recommendations_for_lyrixa(
                    query
                )
            )
            return {
                "query": query,
                "recommendations": recommendations,
                "count": len(recommendations),
            }
        except Exception as e:
            return {
                "error": f"Failed to get recommendations: {str(e)}",
                "recommendations": [],
            }

    async def _enhanced_plugin_routing(self, user_input: str) -> Optional[str]:
        """Enhanced plugin routing with intelligent detection"""
        input_lower = user_input.lower()

        # Plugin generation/creation requests
        if any(
            keyword in input_lower
            for keyword in [
                "generate plugin",
                "create plugin",
                "build plugin",
                "make plugin",
                "develop plugin",
                "write plugin",
                "new plugin",
                "make a plugin",
                "make a machine learning",
                "make ml",
            ]
        ):
            return "plugin_generation"

        # Plugin discovery requests
        if any(
            keyword in input_lower
            for keyword in [
                "find plugin",
                "search plugin",
                "discover plugin",
                "available plugins",
                "what plugins",
                "show plugins",
                "list plugins",
                "plugin for",
            ]
        ):
            return "plugin_discovery"

        # Plugin management requests
        if any(
            keyword in input_lower
            for keyword in [
                "install plugin",
                "install the",
                "remove plugin",
                "enable plugin",
                "disable plugin",
                "configure plugin",
                "plugin settings",
                "manage plugins",
            ]
        ):
            return "plugin_management"

        # Plugin help/info requests
        if any(
            keyword in input_lower
            for keyword in [
                "plugin help",
                "how to use",
                "plugin documentation",
                "explain plugin",
                "plugin info",
                "about plugin",
            ]
        ):
            return "plugin_info"

        return None

    async def _check_and_auto_populate_gui(
        self, response: AgentResponse, input_text: str
    ):
        """Check if response contains plugin code and auto-populate GUI if available"""
        if not self.gui_interface:
            return  # No GUI available

        # Check if this was a plugin generation request and response contains code
        if (
            response.agent_name == "PluginAgent"
            and response.metadata
            and response.metadata.get("plugin_operation") == "plugin_generation"
        ):
            # Extract generated code from response
            generated_code = response.metadata.get("generated_code")
            plugin_name = response.metadata.get("plugin_name", "generated_plugin")

            if generated_code:
                # Auto-populate the Plugin Editor with the generated code
                filename = f"{plugin_name}.aether"
                success = self.gui_interface.inject_plugin_code(
                    generated_code, filename
                )

                if success:
                    self.log(f"✅ Auto-populated Plugin Editor with {filename}")
                    # Add a note to the response with accurate Plugin Editor description
                    response.content += "\n\n🎯 **Plugin Editor Updated**: The generated .aether plugin code has been automatically loaded into your native Plugin Editor tab! You can now review, edit, save, test, and apply the plugin using the code editor interface."
                else:
                    self.log("⚠️ Failed to auto-populate Plugin Editor")

    def inject_plugin(self, code: str, filename: str = "generated_plugin.aether"):
        """
        Inject plugin code directly into the Plugin Editor GUI

        Args:
            code: The plugin code to inject
            filename: The filename to use (defaults to generated_plugin.aether)

        Returns:
            bool: True if injection was successful, False otherwise
        """
        if self.gui_interface and hasattr(self.gui_interface, "inject_plugin_code"):
            try:
                success = self.gui_interface.inject_plugin_code(code, filename)
                self.log(
                    f"🎯 Plugin injection {'successful' if success else 'failed'}: {filename}"
                )
                return success
            except Exception as e:
                self.log(f"❌ Plugin injection error: {e}")
                return False
        else:
            self.log("⚠️ No GUI interface available for plugin injection")
            return False
