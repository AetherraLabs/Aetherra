"""
🧠 Lyrixa Engine Core
======================

Main execution engine for Lyrixa AI system. Provides conversational AI,
reasoning, memory management, and intelligent task orchestration.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...core.agent_orchestrator import AgentOrchestrator
from ..memory.memory_core import LyrixaMemorySystem
from .introspection_controller import IntrospectionController
from .plugin_chain_executor import PluginChainExecutor
from .reasoning_engine import ReasoningEngine
from .self_improvement_engine import SelfImprovementEngine

logger = logging.getLogger(__name__)


class LyrixaEngine:
    """
    Main Lyrixa execution engine that coordinates all subsystems
    """

    def __init__(
        self,
        memory_db_path: str = "lyrixa_memory.db",
        reasoning_db_path: str = "lyrixa_reasoning.db",
        improvement_db_path: str = "lyrixa_improvement.db",
        orchestrator_db_path: str = "lyrixa_orchestrator.db",
    ):
        self.memory_system = LyrixaMemorySystem(memory_db_path)
        self.reasoning_engine = ReasoningEngine(reasoning_db_path)
        self.improvement_engine = SelfImprovementEngine(improvement_db_path)
        self.plugin_executor = PluginChainExecutor()
        self.introspection = IntrospectionController()
        self.agent_orchestrator = AgentOrchestrator(orchestrator_db_path)

        self.conversation_context = {}
        self.session_id = None
        self.active_tasks = {}
        self.initialized = False

        logger.info("Lyrixa Engine initialized")

    async def initialize(self):
        """Initialize the Lyrixa engine and all subsystems"""
        if self.initialized:
            return

        try:
            # Start subsystems
            await self.improvement_engine.start_improvement_cycle()
            await self.introspection.start_introspection()
            await self.agent_orchestrator.start_orchestration()

            # Register system components for monitoring
            self._register_system_components()

            self.initialized = True
            logger.info("✅ Lyrixa Engine fully initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Lyrixa Engine: {e}")
            raise

    async def shutdown(self):
        """Gracefully shutdown the Lyrixa engine"""
        if not self.initialized:
            return

        try:
            await self.improvement_engine.stop_improvement_cycle()
            await self.introspection.stop_introspection()
            await self.agent_orchestrator.stop_orchestration()

            # Close memory connections
            self.memory_system.close_connection()

            self.initialized = False
            logger.info("✅ Lyrixa Engine shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def _register_system_components(self):
        """Register system components for health monitoring"""

        def check_memory_health():
            try:
                stats = asyncio.run(self.memory_system.get_memory_stats())
                return {
                    "total_memories": stats.get("total_memories", 0),
                    "response_time": 100.0,  # Would measure actual response time
                }
            except Exception as e:
                logger.error(f"Memory health check failed: {e}")
                return {"response_time": 999.0, "error": True}

        def check_reasoning_health():
            return {"active_reasoning_sessions": 0}

        def check_orchestrator_health():
            status = self.agent_orchestrator.get_system_status()
            return {
                "active_agents": status.get("total_agents", 0),
                "pending_tasks": status.get("pending_tasks", 0),
            }

        # Register components with introspection
        self.introspection.component_monitor.register_component(
            "memory_system",
            check_memory_health,
            {"response_time_threshold": 500.0, "response_time_critical": 1000.0},
        )

        self.introspection.component_monitor.register_component(
            "reasoning_engine",
            check_reasoning_health,
            {"active_sessions_threshold": 10.0},
        )

        self.introspection.component_monitor.register_component(
            "agent_orchestrator",
            check_orchestrator_health,
            {"pending_tasks_threshold": 50.0},
        )

    async def start_conversation(self, user_id: str = "default") -> str:
        """Start a new conversation session"""
        if not self.initialized:
            await self.initialize()

        self.session_id = f"session_{datetime.now().isoformat()}_{user_id}"
        self.conversation_context = {
            "user_id": user_id,
            "start_time": datetime.now(),
            "message_count": 0,
            "topics": [],
        }

        # Store conversation start in memory
        await self.memory_system.store_memory(
            content={"event": "conversation_start", "user_id": user_id},
            context=self.conversation_context,
            tags=["conversation", "session_start"],
            importance=0.5,
            memory_type="conversation",
        )

        logger.info(f"Started conversation session: {self.session_id}")
        return self.session_id

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate response"""

        if not self.session_id:
            await self.start_conversation()

        try:
            # Update conversation context
            self.conversation_context["message_count"] += 1
            message_context = {
                **self.conversation_context,
                **(context or {}),
                "message": message,
                "timestamp": datetime.now(),
            }

            # Store user message in memory
            memory_id = await self.memory_system.store_memory(
                content={"role": "user", "content": message},
                context=message_context,
                tags=["conversation", "user_message"],
                importance=0.7,
                memory_type="conversation",
            )

            # Recall relevant memories
            relevant_memories = await self.memory_system.recall_memories(
                query_text=message, limit=5, memory_type="conversation"
            )

            # Perform reasoning about the message
            reasoning_context = {
                "query": f"How should I respond to: {message}",
                "domain": "conversation",
                "context_data": {
                    "user_message": message,
                    "conversation_history": [m.content for m in relevant_memories],
                    "session_context": self.conversation_context,
                },
                "constraints": ["be_helpful", "be_conversational"],
                "objectives": ["provide_value", "maintain_engagement"],
            }

            from .reasoning_engine import ReasoningContext

            reasoning_result = await self.reasoning_engine.reason(
                ReasoningContext(**reasoning_context)
            )

            # Generate response (in a real system, this would use an LLM)
            response = self._generate_response(
                message, reasoning_result, relevant_memories
            )

            # Store assistant response in memory
            await self.memory_system.store_memory(
                content={"role": "assistant", "content": response},
                context=message_context,
                tags=["conversation", "assistant_response"],
                importance=0.8,
                memory_type="conversation",
            )

            # Record performance metrics
            self.improvement_engine.record_performance_metric(
                "response_generation_time", 0.5, "seconds"
            )

            return {
                "response": response,
                "session_id": self.session_id,
                "reasoning": reasoning_result.conclusion,
                "confidence": reasoning_result.confidence,
                "memory_id": memory_id,
                "relevant_memories_count": len(relevant_memories),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your message.",
                "error": str(e),
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_response(
        self, message: str, reasoning_result, relevant_memories: List
    ) -> str:
        """Generate response based on message and context (placeholder implementation)"""

        # This is a simple placeholder - in a real system this would use an LLM

        if "hello" in message.lower():
            return f"Hello! I'm Lyrixa, your AI assistant. I understand you said: '{message}'. How can I help you today?"

        elif "?" in message:
            return f"That's an interesting question about '{message}'. Based on my reasoning (confidence: {reasoning_result.confidence:.2f}), I believe: {reasoning_result.conclusion}"

        elif len(relevant_memories) > 0:
            return f"I remember we discussed similar topics. Regarding '{message}', I think: {reasoning_result.conclusion}"

        else:
            return f"I understand you're talking about '{message}'. {reasoning_result.conclusion} Is there anything specific you'd like to know or discuss?"

    async def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        if not self.session_id:
            return {"status": "no_active_session"}

        # Get conversation memories
        memories = await self.memory_system.get_conversation_context(
            self.session_id, limit=20
        )

        return {
            "session_id": self.session_id,
            "context": self.conversation_context,
            "message_count": len(memories),
            "duration_minutes": (
                datetime.now()
                - self.conversation_context.get("start_time", datetime.now())
            ).total_seconds()
            / 60,
            "topics": self.conversation_context.get("topics", []),
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self.initialized:
            return {"status": "not_initialized"}

        # Gather status from all subsystems
        memory_stats = await self.memory_system.get_memory_stats()
        improvement_status = self.improvement_engine.get_improvement_status()
        orchestrator_status = self.agent_orchestrator.get_system_status()
        health_status = self.introspection.get_health_status()

        return {
            "engine_status": "active" if self.initialized else "inactive",
            "session_active": self.session_id is not None,
            "memory_system": memory_stats,
            "improvement_system": improvement_status,
            "agent_orchestrator": orchestrator_status,
            "health_monitoring": health_status,
            "uptime_minutes": 0,  # Would track actual uptime
            "timestamp": datetime.now().isoformat(),
        }

    async def execute_task(
        self, task_name: str, task_data: Dict[str, Any], priority: str = "normal"
    ) -> str:
        """Execute a task using the agent orchestrator"""

        from ...core.agent_orchestrator import Task, TaskPriority

        # Map priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL,
        }

        task = Task(
            task_id=f"task_{datetime.now().isoformat()}",
            name=task_name,
            description=f"User requested task: {task_name}",
            required_capabilities=task_data.get("required_capabilities", []),
            input_data=task_data,
            priority=priority_map.get(priority, TaskPriority.NORMAL),
            max_execution_time=task_data.get("timeout", 300),
            dependencies=task_data.get("dependencies", []),
        )

        task_id = await self.agent_orchestrator.submit_task(task)
        self.active_tasks[task_id] = task

        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.agent_orchestrator.get_task_status(task_id)

    async def learn_from_feedback(self, interaction_id: str, feedback: Dict[str, Any]):
        """Learn from user feedback"""

        # Store feedback in memory
        await self.memory_system.store_learning(
            learning_content={
                "interaction_id": interaction_id,
                "feedback": feedback,
                "feedback_type": "user_rating",
            },
            learning_context={
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Update improvement system
        if feedback.get("rating", 0) >= 4:
            # Positive feedback - reinforce patterns
            self.improvement_engine.record_performance_metric(
                "user_satisfaction", feedback.get("rating", 5), "rating"
            )
        else:
            # Negative feedback - identify areas for improvement
            self.improvement_engine.record_performance_metric(
                "user_satisfaction", feedback.get("rating", 1), "rating"
            )


# Global Lyrixa engine instance
lyrixa_engine = LyrixaEngine()


async def test_lyrixa_engine():
    """Test the Lyrixa engine"""
    engine = LyrixaEngine()

    try:
        # Initialize engine
        await engine.initialize()

        # Start conversation
        session_id = await engine.start_conversation("test_user")
        print(f"Started session: {session_id}")

        # Process some messages
        messages = [
            "Hello, I'm testing the Lyrixa engine",
            "What can you tell me about artificial intelligence?",
            "How does your memory system work?",
        ]

        for message in messages:
            response = await engine.process_message(message)
            print(f"User: {message}")
            print(f"Lyrixa: {response['response']}")
            print(f"Confidence: {response['confidence']:.2f}")
            print("---")

        # Get system status
        status = await engine.get_system_status()
        print("System Status:")
        print(json.dumps(status, indent=2, default=str))

        # Get conversation summary
        summary = await engine.get_conversation_summary()
        print("Conversation Summary:")
        print(json.dumps(summary, indent=2, default=str))

    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(test_lyrixa_engine())
