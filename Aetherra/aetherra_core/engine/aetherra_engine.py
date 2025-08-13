"""
🧠 Aetherra Engine Core
========================

Main execution engine for Aetherra AI system. Provides conversational AI,
reasoning, memory management, and intelligent task orchestration.
"""

import asyncio
import json
import logging
import time
import uuid
from contextlib import suppress
from datetime import datetime
from typing import Any, Dict, List, Optional

# Try to import components with graceful fallbacks
# Prefer real LyrixaMemorySystem/MemoryEngine; alias as AetherraMemorySystem
try:
    from ..memory.memory_core import LyrixaMemorySystem as AetherraMemorySystem
except Exception:
    try:
        from ..memory.memory_core import MemoryEngine as AetherraMemorySystem
    except Exception:

        class AetherraMemorySystem:
            def __init__(self, *args, **kwargs):
                pass

            async def store_memory(self, *args, **kwargs):
                return "mock_memory_id"

            async def recall_memories(self, *args, **kwargs):
                return []

            async def get_memory_stats(self, *args, **kwargs):
                return {"total_memories": 0}

            async def get_conversation_context(self, *args, **kwargs):
                return []

            async def store_learning(self, *args, **kwargs):
                return "mock_learning_id"

            def close_connection(self, *args, **kwargs):
                pass


try:
    from ..cognitive.reasoning_engine import (
        ReasoningContext as _ReasoningContext,
    )
    from ..cognitive.reasoning_engine import (
        ReasoningEngine as _ReasoningEngine,
    )
except Exception:
    _ReasoningContext = None

    class _ReasoningEngine:
        def __init__(self, *args, **kwargs):
            pass

        async def reason(self, *args, **kwargs):
            return {"reasoning": "Mock reasoning engine", "confidence": 0.8}


ReasoningEngine = _ReasoningEngine
ReasoningContext = _ReasoningContext


# Optional quantum memory integration
QUANTUM_MEM_AVAILABLE = False
try:
    # Preferred: factory function from integration module
    from ..memory.quantum_memory_integration import (
        create_quantum_enhanced_memory_engine as _create_qmem,
    )

    QUANTUM_MEM_AVAILABLE = True
except Exception:
    try:
        # Fallback: construct engine directly from shim
        from ..memory.quantum_memory_engine import QuantumEnhancedMemoryEngine as _QEM

        def _create_qmem():
            return _QEM()

        QUANTUM_MEM_AVAILABLE = True
    except Exception:
        _create_qmem = None

try:
    # Introspection controller lives under reflection package
    from ..reflection.introspection_controller import (
        IntrospectionController as _IntrospectionController,
    )
except Exception:

    class _IntrospectionController:
        def __init__(self, *args, **kwargs):
            pass

        async def start_introspection(self, *args, **kwargs):
            pass

        async def stop_introspection(self, *args, **kwargs):
            pass

        def get_health_status(self, *args, **kwargs):
            return {"status": "mock", "health": "good"}

        @property
        def component_monitor(self):
            return None


IntrospectionController = _IntrospectionController


try:
    from .self_improvement_engine import SelfImprovementEngine as _SelfImprovementEngine
except Exception:

    class _SelfImprovementEngine:
        def __init__(self, *args, **kwargs):
            pass

        async def start_improvement_cycle(self, *args, **kwargs):
            pass

        async def stop_improvement_cycle(self, *args, **kwargs):
            pass

        def record_performance_metric(self, *args, **kwargs):
            return {"status": "mock"}

        def get_improvement_status(self, *args, **kwargs):
            return {"status": "mock", "improvements": 0}


SelfImprovementEngine = _SelfImprovementEngine

try:
    from ..plugins.plugin_chain_executor import (
        ExecutionMode as _ExecutionMode,
    )
    from ..plugins.plugin_chain_executor import (
        PluginChainExecutor as _PluginChainExecutor,
    )
    from ..plugins.plugin_chain_executor import (
        PluginChainStep as _PluginChainStep,
    )
except Exception:
    from dataclasses import dataclass
    from enum import Enum

    class _ExecutionMode(Enum):
        SEQUENTIAL = "sequential"
        PARALLEL = "parallel"

    @dataclass
    class _PluginChainStep:
        plugin_name: str
        method_name: str = "execute"
        args: tuple = ()
        kwargs: dict | None = None

    class _PluginChainExecutor:
        async def execute_chain(self, steps, mode=None, chain_id=None, timeout=None):
            # Minimal stub: echo plugin names
            results = []
            for s in steps:
                name = getattr(s, "plugin_name", None) or (
                    s[0] if isinstance(s, tuple) and s else "unknown"
                )
                results.append({"plugin": name, "success": True})
            return {"status": "mock", "results": results}


PluginChainExecutor = _PluginChainExecutor
PluginChainStep = _PluginChainStep
ExecutionMode = _ExecutionMode

try:
    from ..orchestration.agent_orchestrator import (
        AgentOrchestrator as _AgentOrchestrator,
    )
except Exception:

    class _AgentOrchestrator:
        def __init__(self, *args, **kwargs):
            pass

        async def start_orchestration(self, *args, **kwargs):
            pass

        async def stop_orchestration(self, *args, **kwargs):
            pass

        def get_system_status(self, *args, **kwargs):
            return {"status": "mock", "total_agents": 0, "pending_tasks": 0}

        async def submit_task(self, *args, **kwargs):
            return "mock_task_id"

        def get_task_status(self, *args, **kwargs):
            return {"status": "mock", "progress": 100}

        async def orchestrate(self, *args, **kwargs):
            return {"status": "mock", "result": "Mock orchestration"}


AgentOrchestrator = _AgentOrchestrator

logger = logging.getLogger(__name__)


class AetherraEngine:
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
        # Prefer quantum-enhanced memory if available, otherwise classical
        if QUANTUM_MEM_AVAILABLE and _create_qmem is not None:
            # Thin adapter to map quantum API to engine expectations (supports both async remember/recall and sync store/retrieve variants)
            class _QuantumMemoryAdapter:
                def __init__(self):
                    self._q = _create_qmem()
                    self._has_remember = hasattr(self._q, "remember")
                    self._remember_is_async = False
                    if self._has_remember:
                        try:
                            import inspect

                            self._remember_is_async = inspect.iscoroutinefunction(
                                getattr(self._q, "remember")
                            )
                        except Exception:
                            self._remember_is_async = False
                    self._has_recall = hasattr(self._q, "recall")
                    self._recall_is_async = False
                    if self._has_recall:
                        try:
                            import inspect

                            self._recall_is_async = inspect.iscoroutinefunction(
                                getattr(self._q, "recall")
                            )
                        except Exception:
                            self._recall_is_async = False
                    self._has_store = hasattr(self._q, "store")
                    self._has_retrieve = hasattr(self._q, "retrieve")

                async def store_memory(
                    self,
                    content: Dict[str, Any],
                    context: Optional[Dict[str, Any]] = None,
                    tags: Optional[List[str]] = None,
                    importance: float = 0.5,
                    memory_type: str = "conversation",
                ) -> str:
                    # Prefer advanced remember API when present
                    if self._has_remember:
                        try:
                            if self._remember_is_async:
                                res = await self._q.remember(
                                    content=content,
                                    tags=tags or [],
                                    category=memory_type,
                                    confidence=max(0.0, min(1.0, float(importance))),
                                )
                            else:
                                res = self._q.remember(
                                    content=content,
                                    tags=tags or [],
                                    category=memory_type,
                                    confidence=max(0.0, min(1.0, float(importance))),
                                )
                            # Prefer fragment_id when available
                            return getattr(res, "fragment_id", f"mem_{uuid.uuid4()}")
                        except Exception:
                            # Fall through to store()
                            pass

                    # Fallback to basic store() API
                    if self._has_store:
                        mem_id = f"mem_{uuid.uuid4()}"
                        try:
                            entry = {
                                "id": mem_id,
                                "content": content,
                                "context": context or {},
                                "tags": tags or [],
                                "importance": float(importance),
                                "category": memory_type,
                                "timestamp": datetime.now().isoformat(),
                            }
                            ok = self._q.store(entry)
                            return mem_id if ok else mem_id
                        except Exception:
                            return mem_id

                    # As last resort, synthesize an ID
                    return f"mem_{uuid.uuid4()}"

                async def recall_memories(
                    self,
                    query_text: str,
                    limit: int = 5,
                    memory_type: Optional[str] = None,
                ) -> List[Dict[str, Any]]:
                    # Prefer advanced recall API
                    if self._has_recall:
                        try:
                            if self._recall_is_async:
                                results = await self._q.recall(
                                    query=query_text,
                                    recall_strategy="quantum_hybrid",
                                    limit=limit,
                                )
                            else:
                                results = self._q.recall(
                                    query=query_text,
                                    recall_strategy="quantum_hybrid",
                                    limit=limit,
                                )
                            # Normalize into simple dicts with 'content'
                            norm = []
                            for r in results or []:
                                if isinstance(r, dict):
                                    norm.append(
                                        {
                                            "content": r.get("content")
                                            or r.get("text")
                                            or str(r)
                                        }
                                    )
                                else:
                                    norm.append({"content": str(r)})
                            return norm[:limit]
                        except Exception:
                            pass

                    # Fallback to basic retrieve() API
                    if self._has_retrieve:
                        try:
                            single = self._q.retrieve(
                                query_text,
                                context={"category": memory_type}
                                if memory_type
                                else None,
                            )
                            if not single:
                                return []
                            if isinstance(single, dict):
                                # Best-effort text extraction
                                content = (
                                    single.get("content")
                                    or single.get("data")
                                    or single
                                )
                                return [{"content": content}]
                            return [{"content": str(single)}]
                        except Exception:
                            return []

                    return []

                async def get_memory_stats(self) -> Dict[str, Any]:
                    # Try enhanced status first
                    try:
                        if hasattr(self._q, "get_enhanced_system_status"):
                            status = await self._q.get_enhanced_system_status()  # type: ignore[attr-defined]
                            return {
                                "total_memories": status.get("operation_stats", {}).get(
                                    "total_operations", 0
                                )
                            }
                    except Exception:
                        pass
                    # Try basic status
                    try:
                        if hasattr(self._q, "get_status"):
                            status = self._q.get_status()
                            # Prefer fragments count if available
                            total = (
                                status.get("fragments")
                                if isinstance(status, dict)
                                else None
                            )
                            return {
                                "total_memories": int(total)
                                if isinstance(total, int)
                                else 0
                            }
                    except Exception:
                        pass
                    return {"total_memories": 0}

                async def get_conversation_context(
                    self, session_id: str, limit: int = 10
                ) -> List[Dict[str, Any]]:
                    return await self.recall_memories(
                        query_text=session_id, limit=limit, memory_type="conversation"
                    )

                async def store_learning(
                    self,
                    learning_content: Dict[str, Any],
                    learning_context: Optional[Dict[str, Any]] = None,
                ) -> str:
                    # Prefer remember() if available
                    if self._has_remember:
                        try:
                            if self._remember_is_async:
                                res = await self._q.remember(
                                    content=learning_content,
                                    tags=["learning"],
                                    category="learning",
                                    confidence=0.9,
                                )
                            else:
                                res = self._q.remember(
                                    content=learning_content,
                                    tags=["learning"],
                                    category="learning",
                                    confidence=0.9,
                                )
                            return getattr(res, "fragment_id", f"learn_{uuid.uuid4()}")
                        except Exception:
                            pass

                    # Fallback to store()
                    if self._has_store:
                        mem_id = f"learn_{uuid.uuid4()}"
                        try:
                            entry = {
                                "id": mem_id,
                                "content": learning_content,
                                "context": learning_context or {},
                                "tags": ["learning"],
                                "importance": 0.9,
                                "category": "learning",
                                "timestamp": datetime.now().isoformat(),
                            }
                            self._q.store(entry)
                            return mem_id
                        except Exception:
                            return mem_id

                    return f"learn_{uuid.uuid4()}"

                def close_connection(self):
                    return

            self.memory_system = _QuantumMemoryAdapter()
            logger.info("Using Quantum-Enhanced Memory system")
        else:
            self.memory_system = AetherraMemorySystem(memory_db_path)
            logger.info("Using Classical Memory system")
        self.reasoning_engine = ReasoningEngine(reasoning_db_path)
        self.improvement_engine = SelfImprovementEngine(improvement_db_path)
        self.plugin_executor = PluginChainExecutor()
        self.introspection = IntrospectionController()
        self.agent_orchestrator = AgentOrchestrator(orchestrator_db_path)

        # Runtime state
        self.conversation_context = {}
        self.session_id = None
        self.active_tasks = {}
        self.initialized = False
        self._boot_ts = None
        self._bg_tasks = []
        self._task_cancels = {}

        logger.info("Aetherra Engine initialized")

    async def initialize(self):
        """Initialize the Aetherra engine and all subsystems"""
        if self.initialized:
            return

        try:
            # Start subsystems with graceful fallback
            if hasattr(self.improvement_engine, "start_improvement_cycle"):
                # Bind tasks to current loop
                loop = None
                with suppress(RuntimeError):
                    loop = asyncio.get_running_loop()
                await self.improvement_engine.start_improvement_cycle(loop=loop)
            if hasattr(self.introspection, "start_introspection"):
                loop = None
                with suppress(RuntimeError):
                    loop = asyncio.get_running_loop()
                await self.introspection.start_introspection(loop=loop)
            else:
                logger.info("Introspection controller using basic mode")
            if hasattr(self.agent_orchestrator, "start_orchestration"):
                await self.agent_orchestrator.start_orchestration()
            else:
                logger.info("Agent orchestrator using basic mode")

            # Register system components for monitoring
            self._register_system_components()

            # Uptime tracking
            self._boot_ts = datetime.now()

            # Background anticipation loop (proactive suggestions)
            try:
                self._bg_tasks.append(asyncio.create_task(self._anticipation_loop()))
            except Exception:
                pass

            self.initialized = True
            logger.info("[OK] Aetherra Engine fully initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Aetherra Engine: {e}")
            raise

    async def shutdown(self):
        """Gracefully shutdown the Aetherra engine"""
        if not self.initialized:
            return

        try:
            # Stop subsystems with graceful fallback
            if hasattr(self.improvement_engine, "stop_improvement_cycle"):
                await self.improvement_engine.stop_improvement_cycle()
            if hasattr(self.introspection, "stop_introspection"):
                await self.introspection.stop_introspection()
            if hasattr(self.agent_orchestrator, "stop_orchestration"):
                await self.agent_orchestrator.stop_orchestration()

            # Stop background tasks
            try:
                for t in list(self._bg_tasks):
                    t.cancel()
                if self._bg_tasks:
                    with suppress(Exception):
                        await asyncio.gather(*self._bg_tasks, return_exceptions=True)
            finally:
                self._bg_tasks.clear()

            # Close memory connections
            if hasattr(self.memory_system, "close_connection"):
                self.memory_system.close_connection()

            self.initialized = False
            logger.info("[OK] Aetherra Engine shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def _register_system_components(self):
        """Register system components for health monitoring"""

        async def check_memory_health():
            try:
                stats = await asyncio.wait_for(
                    self.memory_system.get_memory_stats(), timeout=2
                )
                return {
                    "total_memories": stats.get("total_memories", 0),
                    "response_time": 100.0,
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

        # Register components with introspection (if available)
        try:
            if (
                hasattr(self.introspection, "component_monitor")
                and self.introspection.component_monitor is not None
            ):
                self.introspection.component_monitor.register_component(
                    "memory_system",
                    check_memory_health,
                    {
                        "response_time_threshold": 500.0,
                        "response_time_critical": 1000.0,
                    },
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
                logger.info("[OK] Component monitoring enabled")
            else:
                logger.info(
                    "[INFO] Component monitoring not available - using basic health checks"
                )
        except Exception as e:
            logger.warning(f"[WARN] Component monitoring setup failed: {e}")
            logger.info("[INFO] Continuing with basic health checks")

    async def start_conversation(self, user_id: str = "default") -> str:
        """Start a new conversation session"""
        if not self.initialized:
            await self.initialize()

        self.session_id = f"session_{datetime.now().isoformat()}_{user_id}"
        self.conversation_context = {
            "session_id": self.session_id,
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
            corr_id = str(uuid.uuid4())
            t0 = time.perf_counter()
            # Update conversation context
            self.conversation_context["message_count"] += 1
            message_context = {
                **self.conversation_context,
                **(context or {}),
                "message": message,
                "timestamp": datetime.now(),
                "corr_id": corr_id,
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
            try:
                relevant_memories = await asyncio.wait_for(
                    self.memory_system.recall_memories(
                        query_text=message, limit=5, memory_type="conversation"
                    ),
                    timeout=3,
                )
            except Exception:
                relevant_memories = []

            # Perform reasoning about the message
            if ReasoningContext is not None:
                rctx = ReasoningContext(
                    query=f"How should I respond to: {message}",
                    domain="conversation",
                    context_data={
                        "user_message": message,
                        "conversation_history": self._normalize_memories(
                            relevant_memories
                        ),
                        "session_context": self.conversation_context,
                    },
                    constraints=["be_helpful", "be_conversational"],
                    objectives=["provide_value", "maintain_engagement"],
                )
            else:
                rctx = {
                    "query": f"How should I respond to: {message}",
                    "domain": "conversation",
                    "context_data": {
                        "user_message": message,
                        "conversation_history": self._normalize_memories(
                            relevant_memories
                        ),
                        "session_context": self.conversation_context,
                    },
                    "constraints": ["be_helpful", "be_conversational"],
                    "objectives": ["provide_value", "maintain_engagement"],
                }

            # Reasoning with timeout
            try:
                reasoning_obj = await asyncio.wait_for(
                    self.reasoning_engine.reason(rctx),
                    timeout=12,
                )
                if hasattr(reasoning_obj, "conclusion"):
                    reasoning_result = {
                        "reasoning": getattr(reasoning_obj, "conclusion", ""),
                        "confidence": getattr(reasoning_obj, "confidence", 0.8),
                    }
                else:
                    reasoning_result = reasoning_obj
            except Exception as e:
                logger.warning(f"Reasoning timeout/failure: {e}")
                reasoning_result = {"reasoning": "I'm not sure yet; using best effort."}

            # Simple goal/plan scaffold and plugin execution when requested
            goal = {
                "intent": "conversational_response",
                "user_text": message,
                "context": message_context,
                "steps": [
                    {"type": "retrieve_context"},
                    {"type": "reason"},
                    {"type": "act_if_needed"},
                    {"type": "draft_reply"},
                    {"type": "critique_and_finalize"},
                ],
                "priority": "normal",
                "corr_id": corr_id,
            }
            with suppress(Exception):
                await self.agent_orchestrator.submit_task({"kind": "goal", **goal})

            # Execute plugin chain if plan suggests actions
            chain_out = None
            try:
                plan = (
                    reasoning_result.get("plan", [])
                    if isinstance(reasoning_result, dict)
                    else []
                )
                plugin_steps = [
                    {
                        "plugin_id": s.get("plugin_id"),
                        "input": s.get("input", {}),
                        "required_capabilities": s.get("required_capabilities", []),
                    }
                    for s in plan
                    if isinstance(s, dict)
                    and s.get("action") == "plugin"
                    and s.get("plugin_id")
                ]
                if plugin_steps:
                    for step in plugin_steps:
                        self._enforce_caps(step)
                    # Build real PluginChainStep list when available
                    steps = []
                    for s in plugin_steps:
                        plugin_name = s["plugin_id"]
                        kwargs = s.get("input", {})
                        try:
                            pcs = PluginChainStep(
                                plugin_name=plugin_name,
                                method_name="execute",
                                args=(),
                                kwargs=kwargs,
                            )
                        except Exception:
                            # Fallback: simple tuple
                            pcs = (plugin_name, "execute", (), kwargs)
                        steps.append(pcs)
                    try:
                        chain_out = await asyncio.wait_for(
                            self.plugin_executor.execute_chain(steps), timeout=15
                        )
                    except TypeError:
                        # Executor expects different signature; try sequential
                        chain_out = await asyncio.wait_for(
                            self.plugin_executor.execute_chain(
                                steps, ExecutionMode.SEQUENTIAL
                            ),
                            timeout=15,
                        )
            except PermissionError as pe:
                logger.warning(f"Guardrail blocked plugin action: {pe}")
            except Exception as e:
                logger.warning(f"Plugin chain failed: {e}")

            # Generate response (in a real system, this would use an LLM)
            response = self._generate_response(
                message, reasoning_result, relevant_memories
            )

            # Fuse plugin outputs if any
            if chain_out:
                try:
                    if isinstance(chain_out, dict):
                        summary = json.dumps(chain_out)[:800]
                    else:
                        # Likely ChainResult dataclass
                        summary = json.dumps(
                            getattr(chain_out, "__dict__", {}), default=str
                        )[:800]
                    response = f"{response}\n\n[Plugin results]\n{summary}"
                except Exception:
                    pass

            # Store assistant response in memory
            await self.memory_system.store_memory(
                content={"role": "assistant", "content": response},
                context=message_context,
                tags=["conversation", "assistant_response"],
                importance=0.8,
                memory_type="conversation",
            )

            # Record performance metrics
            lat_ms = (time.perf_counter() - t0) * 1000
            with suppress(Exception):
                self.improvement_engine.record_performance_metric(
                    "latency_ms", lat_ms, "ms", {"corr_id": corr_id}
                )

            return {
                "response": response,
                "session_id": self.session_id,
                "reasoning": reasoning_result.get("reasoning", "Mock reasoning")
                if isinstance(reasoning_result, dict)
                else str(reasoning_result),
                "confidence": reasoning_result.get("confidence", 0.8)
                if isinstance(reasoning_result, dict)
                else 0.8,
                "memory_id": memory_id,
                "relevant_memories_count": len(relevant_memories),
                "timestamp": datetime.now().isoformat(),
                "corr_id": corr_id,
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
            return f"That's an interesting question about '{message}'. Based on my reasoning (confidence: {reasoning_result.get('confidence', 0.8):.2f}), I believe: {reasoning_result.get('reasoning', 'Mock reasoning')}"

        elif len(relevant_memories) > 0:
            return f"I remember we discussed similar topics. Regarding '{message}', I think: {reasoning_result.get('reasoning', 'Mock reasoning')}"

        else:
            return f"I understand you're talking about '{message}'. {reasoning_result.get('reasoning', 'Mock reasoning')} Is there anything specific you'd like to know or discuss?"

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

        # Gather status from all subsystems (with timeouts)
        try:
            memory_stats = await asyncio.wait_for(
                self.memory_system.get_memory_stats(), timeout=3
            )
        except Exception:
            memory_stats = {"error": True}
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
            "uptime_minutes": ((datetime.now() - self._boot_ts).total_seconds() / 60.0)
            if self._boot_ts
            else 0,
            "timestamp": datetime.now().isoformat(),
        }

    async def execute_task(
        self, task_name: str, task_data: Dict[str, Any], priority: str = "normal"
    ) -> str:
        """Execute a task using the agent orchestrator"""

        # Create a simple task dict for mock orchestrator
        task = {
            "task_id": f"task_{datetime.now().isoformat()}",
            "name": task_name,
            "description": f"User requested task: {task_name}",
            "required_capabilities": task_data.get("required_capabilities", []),
            "input_data": task_data,
            "priority": priority,
            "max_execution_time": task_data.get("timeout", 300),
            "dependencies": task_data.get("dependencies", []),
        }

        # Add cancel token for task
        cancel_evt = asyncio.Event()
        task_id = await self.agent_orchestrator.submit_task(task)
        self.active_tasks[task_id] = task
        self._task_cancels[task_id] = cancel_evt

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

    # -------- Helpers & background loops --------
    def _normalize_memories(self, memories: List[Any]) -> List[Any]:
        def _mem_text(m: Any):
            try:
                if isinstance(m, dict):
                    return m.get("content") or m.get("text") or json.dumps(m)[:500]
                return getattr(m, "content", str(m))
            except Exception:
                return str(m)

        return [_mem_text(m) for m in memories]

    def _enforce_caps(self, step: Dict[str, Any]):
        allowed = {"read_memory", "write_memory", "web_fetch", "file_temp"}
        required = set(step.get("required_capabilities", []))
        if not required.issubset(allowed):
            raise PermissionError("Capability not allowed")

    async def _anticipation_loop(self):
        while self.initialized:
            try:
                recent = []
                with suppress(Exception):
                    recent = await asyncio.wait_for(
                        self.memory_system.recall_memories(query_text="", limit=10),
                        timeout=3,
                    )
                query = {
                    "query": "What proactive suggestions should I surface now?",
                    "domain": "anticipation",
                    "context_data": {"recent": self._normalize_memories(recent)},
                }
                with suppress(Exception):
                    await asyncio.wait_for(
                        self.reasoning_engine.reason(query), timeout=8
                    )
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("anticipation loop error")
            await asyncio.sleep(30)

    def cancel_task(self, task_id: str) -> bool:
        evt = self._task_cancels.get(task_id)
        if evt and not evt.is_set():
            evt.set()
            return True
        return False


# Global Aetherra engine instance
aetherra_engine = AetherraEngine()


async def boot():
    """Boot the global Aetherra engine instance"""
    global aetherra_engine
    if not aetherra_engine.initialized:
        await aetherra_engine.initialize()
    return aetherra_engine


async def test_aetherra_engine():
    """Test the Aetherra engine"""
    engine = AetherraEngine()

    try:
        # Initialize engine
        await engine.initialize()

        # Start conversation
        session_id = await engine.start_conversation("test_user")
        print(f"Started session: {session_id}")

        # Process some messages
        messages = [
            "Hello, I'm testing the Aetherra engine",
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
    asyncio.run(test_aetherra_engine())
