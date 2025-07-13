from typing import Any, Dict, Optional

from .agent_base import AgentBase, AgentResponse
from .escalation_agent import EscalationAgent
from .goal_agent import GoalAgent
from .plugin_agent import PluginAgent
from .reflection_agent import ReflectionAgent
from .self_evaluation_agent import SelfEvaluationAgent


class LyrixaAI(AgentBase):
    """
    Main LyrixaAI interface agent - coordinates all other agents
    """

    def __init__(self, runtime, memory, prompt_engine, llm_manager):
        super().__init__("LyrixaAI", "Main AI coordination agent")
        self.runtime = runtime
        self.memory = memory
        self.prompt_engine = prompt_engine
        self.llm_manager = llm_manager

        # Initialize sub-agents
        self.goal_agent = GoalAgent(memory, prompt_engine, llm_manager)
        self.plugin_agent = PluginAgent(memory, prompt_engine, llm_manager)
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

        # Goal-related keywords - Only route to goal agent for specific goal commands
        if any(
            keyword in input_lower
            for keyword in ["create goal", "new goal", "set goal", "add goal", "goal:", "my goal is", "i want to achieve"]
        ):
            return "goal"

        # Plugin-related keywords
        if any(
            keyword in input_lower
            for keyword in ["show plugins", "list plugins", "find plugin", "plugin for", "what plugins", "available tools"]
        ):
            return "plugin"

        # Reflection-related keywords - More specific
        if any(
            keyword in input_lower
            for keyword in ["reflect on", "analyze my", "review my performance", "how am i doing", "performance report"]
        ):
            return "reflection"

        # Self-evaluation keywords - More specific
        if any(
            keyword in input_lower
            for keyword in ["evaluate my", "assess my", "how can i improve", "self assessment", "learning progress"]
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
        if any(greeting in input_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            response_content = f"Hello! 👋 I'm Lyrixa, your modular AI assistant. Nice to meet you! I'm ready to help with anything you need. What's on your mind today?"

        elif any(word in input_lower for word in ["how are you", "how's it going", "what's up"]):
            response_content = "I'm doing great! All my systems are running smoothly and I'm ready to assist. My 5 specialist agents are standing by to help with goals, plugins, analysis, problem-solving, and self-improvement. How are you doing?"

        elif any(word in input_lower for word in ["what can you do", "what are your capabilities", "help me", "what do you do"]):
            response_content = """I'm Lyrixa, a modular AI assistant with specialized capabilities! Here's what I can help you with:

🎯 **Goal Management** - Create, track, and manage your objectives
🔌 **Plugin Discovery** - Find and recommend tools for your tasks
� **Performance Analysis** - Analyze and reflect on your progress
⚠️ **Problem Solving** - Help troubleshoot issues and escalate when needed
📊 **Self-Improvement** - Learn from feedback and continuously improve

I use multiple AI models (currently GPT-4o) and can switch between them as needed. Just tell me what you'd like to work on!"""

        elif any(word in input_lower for word in ["thanks", "thank you", "appreciate"]):
            response_content = "You're very welcome! I'm here whenever you need assistance. Feel free to ask me anything - whether it's casual conversation or help with specific tasks. 😊"

        elif any(word in input_lower for word in ["bye", "goodbye", "see you", "talk later"]):
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
