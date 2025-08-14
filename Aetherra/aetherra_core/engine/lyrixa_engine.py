"""
DEPRECATED for OS: Lyrixa-specific engine retained for Lyrixa UI compatibility.
Not used by Aetherra OS runtime. Will be relocated/removed in cleanup.
"""

import asyncio
import inspect
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------- Fallbacks for optional subsystems ----------
try:
    from ..memory.memory_core import AetherraMemorySystem  # type: ignore
except Exception:

    class _MemoryRecord:
        def __init__(self, content: Dict[str, Any]):
            self.content = content

    class AetherraMemorySystem:
        def __init__(self, *args, **kwargs):
            self._memories: List[Dict[str, Any]] = []

        async def store_memory(self, content=None, context=None, **kwargs):
            self._memories.append({"content": content, "context": context})
            return f"mem_{len(self._memories)}"

        async def recall_memories(self, query_text: str = "", limit: int = 5, **kwargs):
            return [
                _MemoryRecord(m.get("content", {})) for m in self._memories[-limit:]
            ]

        async def get_memory_stats(self):
            return {"total_memories": len(self._memories)}

        async def get_conversation_context(self, session_id: str, limit: int = 20):
            return self._memories[-limit:]

        async def store_learning(self, *args, **kwargs):
            return True

        def close_connection(self):
            return None


try:
    from ..reflection.introspection_controller import (
        IntrospectionController,  # type: ignore
    )
except Exception:

    class _ComponentMonitorStub:
        def register_component(self, *args, **kwargs):
            return None

    class IntrospectionController:
        def __init__(self, *args, **kwargs):
            self.component_monitor = _ComponentMonitorStub()

        async def start_introspection(self, *args, **kwargs):
            return None

        async def stop_introspection(self, *args, **kwargs):
            return None

        def get_health_status(self):
            return {"status": "not_available"}


try:
    from .reasoning_engine import ReasoningContext, ReasoningEngine  # type: ignore
except Exception:

    class ReasoningResult:
        def __init__(self, conclusion: str, confidence: float = 0.75):
            self.conclusion = conclusion
            self.confidence = confidence

    class ReasoningContext:
        def __init__(self, **kwargs):
            self.payload = kwargs

    class ReasoningEngine:
        def __init__(self, *args, **kwargs):
            pass

        async def reason(self, ctx: ReasoningContext):
            q = getattr(ctx, "payload", {}).get("query")
            return ReasoningResult(
                conclusion=f"Baseline reasoning about: {q}", confidence=0.75
            )


try:
    from .self_improvement_engine import SelfImprovementEngine  # type: ignore
except Exception:

    class SelfImprovementEngine:
        def __init__(self, *args, **kwargs):
            self._running = False

        async def start_improvement_cycle(self, *args, **kwargs):
            self._running = True

        async def stop_improvement_cycle(self, *args, **kwargs):
            self._running = False

        def record_performance_metric(self, *args, **kwargs):
            return None

        def get_improvement_status(self):
            return {"running": self._running}


try:
    from .plugin_chain_executor import PluginChainExecutor  # type: ignore
except Exception:

    class PluginChainExecutor:
        def __init__(self, *args, **kwargs):
            pass

        async def execute_chain(self, *args, **kwargs):
            return {"status": "mock", "results": []}


try:
    from ..orchestration.agent_orchestrator import AgentOrchestrator  # type: ignore
except Exception:

    class AgentOrchestrator:
        def __init__(self, *args, **kwargs):
            self._tasks: Dict[str, Dict[str, Any]] = {}
            self._running = False

        async def start_orchestration(self):
            self._running = True

        async def stop_orchestration(self):
            self._running = False

        async def submit_task(self, task):
            tid = getattr(task, "task_id", f"task_{len(self._tasks) + 1}")
            self._tasks[tid] = {"status": "queued", "task": task}
            return tid

        def get_task_status(self, task_id: str):
            return self._tasks.get(task_id, {"status": "unknown"})

        def get_system_status(self):
            return {"total_agents": 0, "pending_tasks": len(self._tasks)}


# ---------- Engine ----------
class AetherraEngine:
    """Main Lyrixa execution engine that coordinates all subsystems"""

    def __init__(
        self,
        memory_db_path: str = "lyrixa_memory.db",
        reasoning_db_path: str = "lyrixa_reasoning.db",
        improvement_db_path: str = "lyrixa_improvement.db",
        orchestrator_db_path: str = "lyrixa_orchestrator.db",
    ):
        # Subsystems
        self.memory_system = AetherraMemorySystem(memory_db_path)
        self.reasoning_engine = ReasoningEngine(reasoning_db_path)
        self.improvement_engine = SelfImprovementEngine(improvement_db_path)
        self.plugin_executor = PluginChainExecutor()
        self.introspection = IntrospectionController()
        self.agent_orchestrator = AgentOrchestrator(orchestrator_db_path)

        # State
        self.conversation_context: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
        self.active_tasks: Dict[str, Any] = {}
        self.initialized: bool = False

        # Lifecycle flags
        self._started_improvement = False
        self._started_introspection = False
        self._started_orchestration = False

        logger.info("Lyrixa Engine initialized")

        # Minimal goal orchestration and event bus scaffolding
        self._goals: Dict[str, Dict[str, Any]] = {}
        self._subscribers: Dict[str, List] = {  # topic -> callbacks
            "goal.update": [],
            "agent.event": [],
            "plugin.event": [],
            "memory.hit": [],
            "suggestion.new": [],
            "ethics.alert": [],
        }

    async def initialize(self):
        """Initialize the Lyrixa engine and all subsystems"""
        if self.initialized:
            return

        try:
            # Start subsystems (guarded)
            if hasattr(self.improvement_engine, "start_improvement_cycle"):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                await self.improvement_engine.start_improvement_cycle(loop=loop)
                self._started_improvement = True

            start_intro = getattr(self.introspection, "start_introspection", None)
            if callable(start_intro):
                if asyncio.iscoroutinefunction(start_intro):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None
                    await start_intro(loop=loop)
                else:
                    start_intro()
                self._started_introspection = True

            start_orch = getattr(self.agent_orchestrator, "start_orchestration", None)
            if callable(start_orch):
                if asyncio.iscoroutinefunction(start_orch):
                    await start_orch()
                else:
                    start_orch()
                self._started_orchestration = True

            # Register system components for monitoring
            self._register_system_components()

            self.initialized = True
            logger.info("✅ Lyrixa Engine fully initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Lyrixa Engine: {e}")
            # Best-effort cleanup for partially started subsystems
            try:
                if self._started_orchestration and hasattr(
                    self.agent_orchestrator, "stop_orchestration"
                ):
                    stop_orch = self.agent_orchestrator.stop_orchestration
                    try:
                        res = stop_orch()
                        if inspect.isawaitable(res):
                            await res
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                if self._started_introspection and hasattr(
                    self.introspection, "stop_introspection"
                ):
                    stop_intro = self.introspection.stop_introspection
                    try:
                        res = stop_intro()
                        if inspect.isawaitable(res):
                            await res
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                if self._started_improvement and hasattr(
                    self.improvement_engine, "stop_improvement_cycle"
                ):
                    res = self.improvement_engine.stop_improvement_cycle()
                    if inspect.isawaitable(res):
                        await res
            except Exception:
                pass
            raise

    async def shutdown(self):
        """Gracefully shutdown the Lyrixa engine"""
        if not self.initialized:
            return

        try:
            if hasattr(self.improvement_engine, "stop_improvement_cycle"):
                await self.improvement_engine.stop_improvement_cycle()
            if hasattr(self.introspection, "stop_introspection"):
                stop_intro = self.introspection.stop_introspection
                try:
                    res = stop_intro()
                    if inspect.isawaitable(res):
                        await res
                except Exception:
                    pass
            if hasattr(self.agent_orchestrator, "stop_orchestration"):
                stop_orch = self.agent_orchestrator.stop_orchestration
                try:
                    res = stop_orch()
                    if inspect.isawaitable(res):
                        await res
                except Exception:
                    pass

            if hasattr(self.memory_system, "close_connection"):
                try:
                    self.memory_system.close_connection()
                except Exception:
                    pass

            self.initialized = False
            logger.info("✅ Lyrixa Engine shutdown complete")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def _register_system_components(self):
        """Register system components for health monitoring"""
        # Only register if a component monitor is available
        monitor = getattr(self.introspection, "component_monitor", None)
        if not monitor:
            return

        def check_memory_health():
            # Minimal non-blocking snapshot
            return {"total_memories": 0, "response_time": 100.0}

        def check_reasoning_health():
            return {"active_reasoning_sessions": 0}

        def check_orchestrator_health():
            try:
                status = self.agent_orchestrator.get_system_status()
                return {
                    "active_agents": status.get("total_agents", 0),
                    "pending_tasks": status.get("pending_tasks", 0),
                }
            except Exception:
                return {"active_agents": 0, "pending_tasks": 0}

        try:
            monitor.register_component(
                "memory_system",
                check_memory_health,
                {"response_time_threshold": 500.0, "response_time_critical": 1000.0},
            )
            monitor.register_component(
                "reasoning_engine",
                check_reasoning_health,
                {"active_sessions_threshold": 10.0},
            )
            monitor.register_component(
                "agent_orchestrator",
                check_orchestrator_health,
                {"pending_tasks_threshold": 50.0},
            )
        except Exception:
            # If the monitor API is different, skip silently (fallback mode)
            pass

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
            self.conversation_context["message_count"] += 1
            message_context = {
                **self.conversation_context,
                **(context or {}),
                "message": message,
                "timestamp": datetime.now(),
            }

            memory_id = await self.memory_system.store_memory(
                content={"role": "user", "content": message},
                context=message_context,
                tags=["conversation", "user_message"],
                importance=0.7,
                memory_type="conversation",
            )

            relevant_memories = await self.memory_system.recall_memories(
                query_text=message, limit=5, memory_type="conversation"
            )

            # Build reasoning context if available; otherwise pass-through
            try:
                rc = ReasoningContext(
                    **{
                        "query": f"How should I respond to: {message}",
                        "domain": "conversation",
                        "context_data": {
                            "user_message": message,
                            "conversation_history": [
                                getattr(m, "content", {}) for m in relevant_memories
                            ],
                            "session_context": self.conversation_context,
                        },
                        "constraints": ["be_helpful", "be_conversational"],
                        "objectives": ["provide_value", "maintain_engagement"],
                    }
                )  # type: ignore
            except Exception:
                rc = {"query": message}

            try:
                reasoning_result = await self.reasoning_engine.reason(rc)  # type: ignore[arg-type]
            except Exception:

                class _RR:
                    conclusion = "Baseline response"
                    confidence = 0.7

                reasoning_result = _RR()

            response = self._generate_response(
                message, reasoning_result, relevant_memories
            )

            await self.memory_system.store_memory(
                content={"role": "assistant", "content": response},
                context=message_context,
                tags=["conversation", "assistant_response"],
                importance=0.8,
                memory_type="conversation",
            )

            if hasattr(self.improvement_engine, "record_performance_metric"):
                self.improvement_engine.record_performance_metric(
                    "response_generation_time", 0.5, "seconds"
                )

            return {
                "response": response,
                "session_id": self.session_id,
                "reasoning": getattr(reasoning_result, "conclusion", ""),
                "confidence": getattr(reasoning_result, "confidence", 0.0),
                "memory_id": memory_id,
                "relevant_memories_count": len(relevant_memories),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I encountered an error processing your message.",
                "error": str(e),
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_response(
        self, message: str, reasoning_result, relevant_memories: List
    ) -> str:
        """Generate response based on message and context (placeholder)."""
        if "hello" in message.lower():
            return (
                f"Hello! I'm Lyrixa, your AI assistant. I understand you said: '{message}'. "
                "How can I help you today?"
            )
        if "?" in message:
            return (
                f"That's an interesting question about '{message}'. "
                f"Based on my reasoning (confidence: {getattr(reasoning_result, 'confidence', 0.0):.2f}), "
                f"I believe: {getattr(reasoning_result, 'conclusion', '')}"
            )
        if len(relevant_memories) > 0:
            return (
                f"I remember we discussed similar topics. Regarding '{message}', I think: "
                f"{getattr(reasoning_result, 'conclusion', '')}"
            )
        return (
            f"I understand you're talking about '{message}'. "
            f"{getattr(reasoning_result, 'conclusion', '')} "
            "Is there anything specific you'd like to know or discuss?"
        )

    async def get_conversation_summary(self) -> Dict[str, Any]:
        if not self.session_id:
            return {"status": "no_active_session"}
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
        if not self.initialized:
            return {"status": "not_initialized"}
        memory_stats = await self.memory_system.get_memory_stats()
        improvement_status = getattr(
            self.improvement_engine, "get_improvement_status", lambda: {}
        )()
        orchestrator_status = getattr(
            self.agent_orchestrator, "get_system_status", lambda: {}
        )()
        health_status = getattr(
            self.introspection, "get_health_status", lambda: {"status": "unknown"}
        )()
        return {
            "engine_status": "active" if self.initialized else "inactive",
            "session_active": self.session_id is not None,
            "memory_system": memory_stats,
            "improvement_system": improvement_status,
            "agent_orchestrator": orchestrator_status,
            "health_monitoring": health_status,
            "uptime_minutes": 0,
            "timestamp": datetime.now().isoformat(),
        }

    # ---------- Event bus ----------
    def subscribe(self, topic: str, callback):
        self._subscribers.setdefault(topic, []).append(callback)

    def _emit(self, topic: str, payload: Dict[str, Any]):
        for cb in self._subscribers.get(topic, []):
            try:
                cb(payload)
            except Exception:
                pass

    # ---------- Minimal Goal Orchestration ----------
    async def create_goal(
        self,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        deadline: Optional[str] = None,
    ) -> str:
        gid = f"goal_{datetime.now().timestamp()}"
        self._goals[gid] = {
            "id": gid,
            "intent": intent,
            "context": context or {},
            "priority": priority,
            "deadline": deadline,
            "status": "created",
            "steps": [],
        }
        self._emit("goal.update", {"id": gid, "status": "created"})
        return gid

    async def plan(self, goal_id: str) -> List[Dict[str, Any]]:
        goal = self._goals.get(goal_id)
        if not goal:
            return []
        # naive 2-step plan
        steps = [
            {"id": f"{goal_id}_step1", "name": "analyze_intent", "status": "pending"},
            {
                "id": f"{goal_id}_step2",
                "name": "execute_best_action",
                "status": "pending",
            },
        ]
        goal["steps"] = steps
        goal["status"] = "planned"
        self._emit("goal.update", {"id": goal_id, "status": "planned", "steps": steps})
        return steps

    async def execute(self, goal_id: str):
        goal = self._goals.get(goal_id)
        if not goal:
            return {"status": "unknown_goal"}
        goal["status"] = "running"
        self._emit("goal.update", {"id": goal_id, "status": "running"})
        for step in goal.get("steps", []):
            step["status"] = "running"
            self._emit("goal.update", {"id": goal_id, "step": step})
            await asyncio.sleep(0)  # yield
            step["status"] = "done"
            self._emit("goal.update", {"id": goal_id, "step": step})
        goal["status"] = "done"
        self._emit("goal.update", {"id": goal_id, "status": "done"})
        return {"status": "done"}

    async def pause(self, goal_id: str):
        goal = self._goals.get(goal_id)
        if not goal:
            return {"status": "unknown_goal"}
        goal["status"] = "paused"
        self._emit("goal.update", {"id": goal_id, "status": "paused"})
        return {"status": "paused"}

    async def cancel(self, goal_id: str):
        goal = self._goals.get(goal_id)
        if not goal:
            return {"status": "unknown_goal"}
        goal["status"] = "canceled"
        self._emit("goal.update", {"id": goal_id, "status": "canceled"})
        return {"status": "canceled"}

    def status(self, goal_id: str) -> Dict[str, Any]:
        return self._goals.get(goal_id, {"status": "unknown_goal"})

    async def execute_task(
        self, task_name: str, task_data: Dict[str, Any], priority: str = "normal"
    ) -> str:
        class _Task:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        task = _Task(
            task_id=f"task_{datetime.now().isoformat()}",
            name=task_name,
            description=f"User requested task: {task_name}",
            required_capabilities=task_data.get("required_capabilities", []),
            input_data=task_data,
            priority=priority,
            max_execution_time=task_data.get("timeout", 300),
            dependencies=task_data.get("dependencies", []),
        )
        task_id = await self.agent_orchestrator.submit_task(task)
        self.active_tasks[task_id] = task
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.agent_orchestrator.get_task_status(task_id)

    async def learn_from_feedback(self, interaction_id: str, feedback: Dict[str, Any]):
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
        if hasattr(self.improvement_engine, "record_performance_metric"):
            metric_val = feedback.get("rating", 0)
            self.improvement_engine.record_performance_metric(
                "user_satisfaction", metric_val, "rating"
            )


# Global Lyrixa engine instance
aetherra_engine = AetherraEngine()


async def boot():
    """Boot the global Aetherra engine instance"""
    global aetherra_engine
    if not aetherra_engine.initialized:
        await aetherra_engine.initialize()
    return aetherra_engine


async def test_aetherra_engine():
    engine = AetherraEngine()
    try:
        await engine.initialize()
        session_id = await engine.start_conversation("test_user")
        print(f"Started session: {session_id}")
        for message in [
            "Hello, I'm testing the Lyrixa engine",
            "What can you tell me about artificial intelligence?",
            "How does your memory system work?",
        ]:
            response = await engine.process_message(message)
            print(f"User: {message}")
            print(f"Lyrixa: {response['response']}")
            print(f"Confidence: {response.get('confidence', 0.0):.2f}")
            print("---")
        status = await engine.get_system_status()
        print("System Status:")
        print(json.dumps(status, indent=2, default=str))
        summary = await engine.get_conversation_summary()
        print("Conversation Summary:")
        print(json.dumps(summary, indent=2, default=str))
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(test_aetherra_engine())
