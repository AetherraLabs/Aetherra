#!/usr/bin/env python3
"""
🎙️ LYRIXA AI ASSISTANT
======================

The main Lyrixa AI Assistant class that orchestrates all core systems.
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

from .core.advanced_plugins import LyrixaAdvancedPluginManager
from .core.aether_interpreter import AetherInterpreter
from .core.agents import AgentOrchestrator
from .core.conversation import LyrixaConversationalEngine
from .core.enhanced_memory import LyrixaEnhancedMemorySystem
from .core.goals import GoalPriority, LyrixaGoalSystem
from .core.memory import LyrixaMemorySystem
from .core.plugins import LyrixaPluginManager


class LyrixaAI:
    """
    Lyrixa - The AI Assistant for Aetherra

    She is the voice and presence of Aetherra — a conversational AI agent
    designed to understand, generate, and evolve .aether code.

    Rather than being a command parser or chatbot, Lyrixa is a collaborator,
    translator, and guide who brings conversation and intuition to programming.
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.name = "Lyrixa"
        self.version = "3.0.0-aetherra-assistant"
        self.personality = "Intelligent, intuitive, collaborative AI assistant"

        # Workspace setup
        self.workspace_path = workspace_path or os.getcwd()
        self.session_id = self._create_session_id()

        # Initialize core systems
        print("🎙️ Initializing Lyrixa AI Assistant for Aetherra...")

        self.aether_interpreter = AetherInterpreter()
        self.memory = LyrixaEnhancedMemorySystem(
            memory_db_path=os.path.join(
                self.workspace_path, "lyrixa_enhanced_memory.db"
            )
        )
        self.plugins = LyrixaAdvancedPluginManager(
            plugin_directory=os.path.join(self.workspace_path, "plugins"),
            memory_system=self.memory,
        )
        self.goals = LyrixaGoalSystem(
            goals_file=os.path.join(self.workspace_path, "lyrixa_goals.json")
        )
        self.agents = AgentOrchestrator()
        self.conversation = LyrixaConversationalEngine(memory_system=self.memory)

        # Conversation state
        self.conversation_context = []
        self.active_aether_session = None
        self.current_project_context = {}

        self._display_welcome_message()

    def _create_session_id(self) -> str:
        """Create unique session identifier"""
        return f"lyrixa_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _display_welcome_message(self):
        """Display Lyrixa's welcome message"""
        print(f"""
🎙️ LYRIXA AI ASSISTANT FOR AETHERRA
===================================
Version: {self.version}
Session: {self.session_id}
Workspace: {self.workspace_path}

✅ .aether interpreter ready
✅ Memory system active
✅ Plugin ecosystem loaded
✅ Goal tracking initialized
✅ Agent orchestration ready

Hello! I'm Lyrixa, your AI assistant for Aetherra. I understand .aether code,
can help you build projects, manage memory, and collaborate on development.
I'm ready to translate your ideas into .aether workflows!

What would you like to work on today?
""")

    async def initialize(self):
        """Initialize all systems asynchronously"""
        print("🔄 Initializing Lyrixa systems...")

        # Initialize plugin manager
        await self.plugins.initialize(
            {
                "workspace_path": self.workspace_path,
                "session_id": self.session_id,
                "memory_system": self.memory,
                "aether_interpreter": self.aether_interpreter,
            }
        )

        # Initialize agent orchestrator
        await self.agents.initialize(
            {
                "workspace_path": self.workspace_path,
                "session_id": self.session_id,
                "memory_system": self.memory,
                "plugin_manager": self.plugins,
                "aether_interpreter": self.aether_interpreter,
            }
        )

        print("✅ Lyrixa AI Assistant fully initialized")

    async def process_natural_language(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process natural language input and convert to appropriate .aether workflows

        This is Lyrixa's core capability - understanding human intent and
        translating it into executable .aether code and system actions.
        """
        print(f"🎙️ Lyrixa processing: '{user_input}'")

        # Analyze intent
        intent_analysis = await self._analyze_intent(user_input, context or {})

        # Get relevant context from memory
        memory_context = await self.memory.recall_memories(user_input, limit=5)

        # Create response structure
        response = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "user_input": user_input,
            "intent": intent_analysis,
            "memory_context": memory_context,
            "aether_code": None,
            "plugin_executions": [],
            "lyrixa_response": "",
            "actions_taken": [],
            "suggestions": [],
        }

        # Route based on intent
        if intent_analysis["type"] == "aether_code_generation":
            response = await self._handle_aether_generation(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "memory_operation":
            response = await self._handle_memory_operation(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "plugin_execution":
            response = await self._handle_plugin_execution(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "goal_management":
            response = await self._handle_goal_management(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "project_exploration":
            response = await self._handle_project_exploration(
                user_input, intent_analysis, response
            )
        elif intent_analysis["type"] == "workflow_orchestration":
            response = await self._handle_workflow_orchestration(
                user_input, intent_analysis, response
            )
        else:
            response = await self._handle_conversation(
                user_input, intent_analysis, response
            )

        # Store interaction in memory
        await self.memory.store_memory(
            content={"input": user_input, "response": response["lyrixa_response"]},
            context={"intent": intent_analysis["type"], "session": self.session_id},
            tags=["conversation", intent_analysis["type"]],
            importance=0.7 if intent_analysis["confidence"] > 0.8 else 0.5,
        )

        # Update conversation context
        self.conversation_context.append(
            {
                "timestamp": response["timestamp"],
                "user_input": user_input,
                "lyrixa_response": response["lyrixa_response"],
                "intent": intent_analysis["type"],
            }
        )

        # Keep only recent context
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]

        return response

    async def _analyze_intent(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user intent from natural language input"""
        user_lower = user_input.lower()

        # Simple rule-based intent analysis (in real implementation, use AI/ML)
        if any(
            keyword in user_lower
            for keyword in ["create", "generate", "build", "make", ".aether"]
        ):
            return {
                "type": "aether_code_generation",
                "confidence": 0.8,
                "keywords": ["create", "generate"],
            }
        elif any(
            keyword in user_lower
            for keyword in ["remember", "recall", "memory", "save"]
        ):
            return {
                "type": "memory_operation",
                "confidence": 0.7,
                "keywords": ["memory"],
            }
        elif any(keyword in user_lower for keyword in ["plugin", "execute", "run"]):
            return {
                "type": "plugin_execution",
                "confidence": 0.8,
                "keywords": ["plugin", "execute"],
            }
        elif any(
            keyword in user_lower for keyword in ["goal", "task", "todo", "project"]
        ):
            return {
                "type": "goal_management",
                "confidence": 0.7,
                "keywords": ["goal", "task"],
            }
        elif any(
            keyword in user_lower for keyword in ["explore", "find", "search", "show"]
        ):
            return {
                "type": "project_exploration",
                "confidence": 0.6,
                "keywords": ["explore", "find"],
            }
        elif any(
            keyword in user_lower
            for keyword in ["workflow", "orchestrate", "coordinate", "agents"]
        ):
            return {
                "type": "workflow_orchestration",
                "confidence": 0.8,
                "keywords": ["workflow", "agents"],
            }
        else:
            return {"type": "conversation", "confidence": 0.5, "keywords": []}

    async def _handle_aether_generation(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle .aether code generation requests"""
        try:
            # Generate .aether code from intent
            aether_code = await self.aether_interpreter.generate_aether_from_intent(
                user_input,
                {
                    "session_id": self.session_id,
                    "conversation_context": self.conversation_context[
                        -3:
                    ],  # Recent context
                    "project_context": self.current_project_context,
                },
            )

            # Parse and validate the generated code
            workflow = await self.aether_interpreter.parse_aether_code(aether_code)
            validation = self.aether_interpreter.validate_workflow(workflow)

            response["aether_code"] = aether_code
            response["workflow"] = {
                "name": workflow.name,
                "nodes": len(workflow.nodes),
                "connections": len(workflow.connections),
                "validation": validation,
            }

            # Generate explanation
            explanation = await self.aether_interpreter.explain_workflow(workflow)

            response[
                "lyrixa_response"
            ] = f"""I've generated an .aether workflow for you:

{explanation}

**Generated .aether Code:**
```aether
{aether_code}
```

{f"⚠️ Validation warnings: {', '.join(validation['warnings'])}" if validation.get("warnings") else "✅ Workflow validated successfully"}

Would you like me to execute this workflow or make any modifications?"""

            response["actions_taken"].append("Generated .aether workflow")
            response["suggestions"].append("Execute the generated workflow")
            response["suggestions"].append("Modify the workflow parameters")

        except Exception as e:
            response["lyrixa_response"] = (
                f"I encountered an issue generating the .aether code: {str(e)}. Let me try a different approach or could you provide more specific details?"
            )
            response["actions_taken"].append(
                f"Failed to generate .aether code: {str(e)}"
            )

        return response

    async def _handle_memory_operation(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle memory-related operations"""
        try:
            if "remember" in user_input.lower() or "save" in user_input.lower():
                # Extract content to remember
                content_to_save = (
                    user_input.replace("remember", "").replace("save", "").strip()
                )

                memory_id = await self.memory.store_memory(
                    content={
                        "user_request": content_to_save,
                        "timestamp": datetime.now().isoformat(),
                    },
                    context={"session": self.session_id, "type": "user_request"},
                    tags=["user_request", "manual_save"],
                    importance=0.8,
                )

                response["lyrixa_response"] = (
                    f"✅ I've saved that to memory. Memory ID: {memory_id[:8]}..."
                )
                response["actions_taken"].append("Stored information in memory")

            elif (
                "recall" in user_input.lower()
                or "what do you remember" in user_input.lower()
            ):
                # Search memories
                query = (
                    user_input.replace("recall", "")
                    .replace("what do you remember about", "")
                    .strip()
                )
                memories = await self.memory.recall_memories(query, limit=5)

                if memories:
                    memory_summary = "\n".join(
                        [
                            f"• {mem.content.get('user_request', str(mem.content)[:100])}"
                            for mem in memories[:3]
                        ]
                    )
                    response["lyrixa_response"] = (
                        f"Here's what I remember:\n\n{memory_summary}"
                    )
                else:
                    response["lyrixa_response"] = (
                        "I don't have any specific memories about that topic yet."
                    )

                response["actions_taken"].append(f"Recalled {len(memories)} memories")

        except Exception as e:
            response["lyrixa_response"] = (
                f"I had trouble with the memory operation: {str(e)}"
            )
            response["actions_taken"].append(f"Memory operation failed: {str(e)}")

        return response

    async def _handle_plugin_execution(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle plugin execution requests"""
        try:
            # Simple plugin command parsing
            if "file" in user_input.lower():
                result = await self.plugins.execute_plugin(
                    "FileManager", "list_directory", {"directory_path": "."}
                )
                response["plugin_executions"].append(result)

                if result["success"]:
                    files = result["result"].get("items", [])
                    response["lyrixa_response"] = (
                        "Here are the files in the current directory:\n\n"
                        + "\n".join(f"• {file}" for file in files[:10])
                    )
                else:
                    response["lyrixa_response"] = (
                        f"I couldn't list the files: {result.get('error', 'Unknown error')}"
                    )

            elif "search" in user_input.lower() and "web" in user_input.lower():
                query = user_input.replace("search", "").replace("web", "").strip()
                result = await self.plugins.execute_plugin(
                    "WebSearch", "web_search", {"query": query}
                )
                response["plugin_executions"].append(result)

                response["lyrixa_response"] = (
                    f"I searched for '{query}' but this is a placeholder implementation. In a full version, I would return actual search results."
                )

            else:
                # List available capabilities
                capabilities = self.plugins.get_capabilities()
                cap_list = "\n".join(
                    [
                        f"• {cap}: {', '.join(plugins)}"
                        for cap, plugins in capabilities.items()
                    ]
                )
                response["lyrixa_response"] = (
                    f"I have these plugin capabilities available:\n\n{cap_list}\n\nWhat would you like me to do?"
                )

            response["actions_taken"].append("Executed plugin operation")

        except Exception as e:
            response["lyrixa_response"] = (
                f"I encountered an issue with the plugin: {str(e)}"
            )
            response["actions_taken"].append(f"Plugin execution failed: {str(e)}")

        return response

    async def _handle_goal_management(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle goal and task management"""
        try:
            if "create" in user_input.lower() and "goal" in user_input.lower():
                # Extract goal title
                goal_title = (
                    user_input.replace("create", "").replace("goal", "").strip()
                )

                goal_id = await self.goals.create_goal(
                    title=goal_title or "New Development Goal",
                    description=f"Goal created from user input: {user_input}",
                    priority=GoalPriority.MEDIUM,
                    tags=["user_created"],
                )

                response["lyrixa_response"] = (
                    f"✅ Created goal: '{goal_title}' (ID: {goal_id[:8]}...)"
                )
                response["actions_taken"].append("Created new goal")

            elif "list" in user_input.lower() or "show" in user_input.lower():
                active_goals = self.goals.get_active_goals()

                if active_goals:
                    goal_list = "\n".join(
                        [
                            f"• {goal.title} ({goal.priority.value} priority, {goal.progress * 100:.0f}% complete)"
                            for goal in active_goals[:5]
                        ]
                    )
                    response["lyrixa_response"] = f"Your active goals:\n\n{goal_list}"
                else:
                    response["lyrixa_response"] = (
                        "You don't have any active goals yet. Would you like to create one?"
                    )

                response["actions_taken"].append("Listed active goals")

            elif "suggest" in user_input.lower():
                suggestions = await self.goals.suggest_next_actions()

                if suggestions:
                    suggestion_list = "\n".join(
                        [
                            f"• {sug['title']}: {sug['description']}"
                            for sug in suggestions[:3]
                        ]
                    )
                    response["lyrixa_response"] = (
                        f"Here are my suggestions for your next actions:\n\n{suggestion_list}"
                    )
                else:
                    response["lyrixa_response"] = (
                        "You're all caught up! Consider creating new goals or taking a break."
                    )

                response["actions_taken"].append("Generated goal suggestions")

        except Exception as e:
            response["lyrixa_response"] = (
                f"I had trouble with goal management: {str(e)}"
            )
            response["actions_taken"].append(f"Goal management failed: {str(e)}")

        return response

    async def _handle_project_exploration(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle project exploration and navigation"""
        try:
            # Use file manager plugin to explore
            result = await self.plugins.execute_plugin(
                "FileManager", "list_directory", {"directory_path": self.workspace_path}
            )

            if result["success"]:
                items = result["result"].get("items", [])

                # Categorize items
                directories = [
                    item for item in items if "." not in item or item.startswith(".")
                ]
                files = [
                    item for item in items if "." in item and not item.startswith(".")
                ]

                response["lyrixa_response"] = f"""📁 **Project Structure:**

**Directories ({len(directories)}):**
{chr(10).join(f"• {dir}" for dir in directories[:8])}

**Files ({len(files)}):**
{chr(10).join(f"• {file}" for file in files[:10])}

{f"... and {len(items) - 18} more items" if len(items) > 18 else ""}

What would you like to explore further?"""

                response["actions_taken"].append("Explored project structure")
                response["suggestions"].extend(
                    [
                        "Explore a specific directory",
                        "Analyze code files",
                        "Search for specific patterns",
                    ]
                )
            else:
                response["lyrixa_response"] = (
                    "I couldn't explore the project structure. Make sure I have access to the workspace."
                )

        except Exception as e:
            response["lyrixa_response"] = (
                f"I encountered an issue exploring the project: {str(e)}"
            )
            response["actions_taken"].append(f"Project exploration failed: {str(e)}")

        return response

    async def _handle_workflow_orchestration(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle complex workflow orchestration using agents"""
        try:
            # Execute workflow using agent orchestrator
            workflow_result = await self.agents.execute_workflow(
                user_input,
                {
                    "user_input": user_input,
                    "session_id": self.session_id,
                    "workspace_path": self.workspace_path,
                },
            )

            if workflow_result.get("success"):
                response["lyrixa_response"] = f"""🎭 **Workflow Orchestration Complete**

Executed {workflow_result["tasks_executed"]} tasks successfully.

I coordinated multiple specialized agents to handle your request:
{chr(10).join(f"• {result.get('plugin', 'Agent')}: {result.get('result', {}).get('summary', 'Completed')}" for result in workflow_result.get("results", [])[:3])}

The workflow has been completed successfully!"""
            else:
                response["lyrixa_response"] = (
                    f"I started the workflow orchestration but encountered some issues. I was able to plan and execute {workflow_result.get('tasks_executed', 0)} tasks."
                )

            response["actions_taken"].append("Orchestrated multi-agent workflow")
            response["workflow_result"] = workflow_result

        except Exception as e:
            response["lyrixa_response"] = (
                f"I had trouble orchestrating the workflow: {str(e)}. Let me try a simpler approach."
            )
            response["actions_taken"].append(f"Workflow orchestration failed: {str(e)}")

        return response

    async def _handle_conversation(
        self, user_input: str, intent: Dict[str, Any], response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general conversation"""
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        questions = ["how are you", "what can you do", "help"]

        user_lower = user_input.lower()

        if any(greeting in user_lower for greeting in greetings):
            response[
                "lyrixa_response"
            ] = """Hello! I'm Lyrixa, your AI assistant for Aetherra.

I can help you with:
• Creating and executing .aether workflows
• Managing your development goals and tasks
• Exploring and analyzing your project
• Orchestrating complex multi-step workflows
• Remembering important information
• Connecting to external services through plugins

What would you like to work on today?"""

        elif any(question in user_lower for question in questions):
            response[
                "lyrixa_response"
            ] = """I'm Lyrixa, your intelligent AI assistant for the Aetherra development environment!

🎙️ **My Core Capabilities:**
• **Natural Language to .aether**: I translate your ideas into executable .aether workflows
• **Memory & Context**: I remember our conversations and your preferences
• **Goal Management**: I help you set, track, and achieve development goals
• **Plugin Ecosystem**: I can execute various tools and integrations
• **Agent Orchestration**: I coordinate specialized AI agents for complex tasks
• **Project Intelligence**: I understand your codebase and can provide insights

I'm designed to be collaborative, intuitive, and helpful. Just tell me what you want to accomplish, and I'll figure out how to make it happen using .aether workflows and my various capabilities!"""

        else:
            response["lyrixa_response"] = f"""I understand you said: "{user_input}"

I'm not entirely sure how to help with that specific request, but I'm always learning! Here are some things I can definitely help you with:

• Create .aether workflows from your descriptions
• Manage your development goals and tasks
• Explore and analyze your project files
• Execute plugins for various operations
• Remember important information for future reference

Could you be more specific about what you'd like to accomplish?"""

        response["actions_taken"].append("Engaged in conversation")

        return response

    async def execute_aether_workflow(self, aether_code: str) -> Dict[str, Any]:
        """Execute an .aether workflow"""
        try:
            # Parse the .aether code
            workflow = await self.aether_interpreter.parse_aether_code(aether_code)

            # Execute the workflow
            execution_result = await self.aether_interpreter.execute_workflow(
                workflow,
                {
                    "session_id": self.session_id,
                    "workspace_path": self.workspace_path,
                    "plugin_manager": self.plugins,
                    "memory_system": self.memory,
                },
            )

            # Store execution in memory
            await self.memory.store_memory(
                content={
                    "workflow_name": workflow.name,
                    "execution_result": execution_result,
                    "aether_code": aether_code,
                },
                context={"session": self.session_id, "type": "workflow_execution"},
                tags=["workflow", "execution", "aether"],
                importance=0.8,
            )

            return execution_result

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        memory_stats = await self.memory.get_memory_stats()
        goal_stats = self.goals.get_goal_statistics()
        agent_status = self.agents.get_agent_status()
        plugin_status = await self.plugins.get_ecosystem_status()

        return {
            "session_id": self.session_id,
            "workspace_path": self.workspace_path,
            "conversation_length": len(self.conversation_context),
            "memory_system": memory_stats,
            "goal_system": goal_stats,
            "plugin_system": plugin_status,
            "agent_system": agent_status,
            "aether_interpreter": {
                "active_workflows": len(
                    getattr(self.aether_interpreter, "active_workflows", [])
                ),
                "status": "active",
            },
            "status": "operational",
        }

    async def cleanup(self):
        """Clean up resources"""
        await self.memory.consolidate_memories()
        print("🎙️ Lyrixa AI Assistant shutdown complete")
