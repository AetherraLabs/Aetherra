# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Aetherra Engine Core
========================

Main execution engine for Aetherra AI system. Provides conversational AI,
reasoning, memory management, and intelligent task orchestration.
"""

# Standard library imports
import asyncio
import json
import logging
import os
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

# Try to import components with graceful fallbacks
try:
    # Local imports
    from ..memory.memory_core import AetherraMemorySystem
except ImportError:
    # Create a mock memory system
    class AetherraMemorySystem:
        def __init__(self, *args, **kwargs):
            pass

        async def store(self, *args, **kwargs):
            return {"status": "mock"}

        async def retrieve(self, *args, **kwargs):
            return []

        async def store_memory(self, *args, **kwargs):
            return "mock_memory_id"

        async def recall_memories(self, *args, **kwargs):
            return []

        async def get_memory_stats(self, *args, **kwargs):
            return {"total_memories": 0}

        async def get_conversation_context(self, *args, **kwargs):
            return []

        async def store_learning(self, *args, **kwargs):
            return {"status": "mock"}

        def close_connection(self, *args, **kwargs):
            pass


try:
    # Local imports
    from .introspection_controller import IntrospectionController
except ImportError:

    class IntrospectionController:
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


try:
    # Local imports
    from .reasoning_engine import ReasoningEngine
except ImportError:

    class ReasoningEngine:
        def __init__(self, *args, **kwargs):
            pass

        async def reason(self, *args, **kwargs):
            return {"status": "mock", "reasoning": "Mock reasoning engine"}


try:
    # Local imports
    from .self_improvement_engine import SelfImprovementEngine
except ImportError:

    class SelfImprovementEngine:
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


try:
    # Local imports
    from .plugin_chain_executor import PluginChainExecutor
except ImportError:

    class PluginChainExecutor:
        def __init__(self, *args, **kwargs):
            pass

        async def execute_chain(self, *args, **kwargs):
            return {"status": "mock", "results": []}


try:
    # Prefer canonical path
    # Local imports
    from ..agents.agent_orchestrator import AgentOrchestrator
except ImportError:
    try:
        # Fallback to deprecated shim (emits DeprecationWarning)
        # Local imports
        from ..orchestration.agent_orchestrator import AgentOrchestrator  # type: ignore
    except ImportError:

        class AgentOrchestrator:
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


logger = logging.getLogger(__name__)


# Ensure a current event loop exists for legacy get_event_loop() callers on Windows/Python 3.13+
try:
    # On Python 3.11+, get_event_loop() requires a previously set loop.
    # Some tests call it directly; ensure a loop is set on import if missing.
    asyncio.get_event_loop()
except Exception:
    try:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    except Exception:
        pass


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
        # Core subsystems
        self.memory_system = AetherraMemorySystem(memory_db_path)
        self.reasoning_engine = ReasoningEngine(reasoning_db_path)
        self.improvement_engine = SelfImprovementEngine(improvement_db_path)
        self.plugin_executor = PluginChainExecutor()
        self.introspection = IntrospectionController()
        self.agent_orchestrator = AgentOrchestrator(orchestrator_db_path)

        # Session state
        self.conversation_context = {}
        self.session_id = None
        self.active_tasks = {}
        self.initialized = False

        # Session-scoped scratchpad (ephemeral, never persisted)
        self._scratchpad: List[Dict[str, Any]] = []

        # Per-session metrics
        self.session_metrics: Dict[str, Any] = {
            "messages": 0,
            "reasoning_latency_ms": [],
            "rag_hits": 0,
            "rag_misses": 0,
            "safety_filters_triggered": 0,
            # Style layer metrics (per-session, lightweight)
            "style_contractions": 0,
            "style_questions": 0,
            "style_empathy": 0,
        }

        # Last agent evaluation report (ephemeral)
        self._last_agent_eval: Optional[Dict[str, Any]] = None

        # Optional persistent memory (for quantum A/B recall path)
        self._persistent_memory: Any = None  # lazy init
        self._msg_counter = 0  # per-session message counter for A/B bucketing

        # LLM manager (lazy until initialize); prefer local providers for privacy by default
        self._llm_manager = None  # type: ignore[assignment]
        self._llm_selected = False
        # Last LLM info/error snapshot for diagnostics (per-session, ephemeral)
        self._last_llm_info = {}

        logger.info("Aetherra Engine initialized")

    async def initialize(self):
        """Initialize the Aetherra engine and all subsystems"""
        if self.initialized:
            return

        try:
            # Bring up LLM manager (best-effort); selection happens below
            try:
                # Aetherra imports
                from Aetherra.core.multi_llm_manager import (  # type: ignore
                    MultiLLMManager,
                )

                self._llm_manager = MultiLLMManager()
            except Exception as _e:
                self._llm_manager = None
                logger.warning(f"[LLM] MultiLLMManager unavailable: {_e}")

            # Start subsystems with graceful fallback
            if hasattr(self.improvement_engine, "start_improvement_cycle"):
                await self.improvement_engine.start_improvement_cycle()
            if hasattr(self.introspection, "start_introspection"):
                await self.introspection.start_introspection()
            else:
                logger.info("Introspection controller using basic mode")
            if hasattr(self.agent_orchestrator, "start_orchestration"):
                await self.agent_orchestrator.start_orchestration()
            else:
                logger.info("Agent orchestrator using basic mode")

            # Register system components for monitoring
            self._register_system_components()

            # If A/B recall requires persistent memory, pre-initialize it (best-effort)
            try:
                if self._ab_mode() in ("quantum", "abp"):
                    await self._ensure_persistent_memory()
            except Exception:
                pass

            # Select an LLM model if possible (Ollama-first by default)
            try:
                await self._ensure_llm_selection()
            except Exception as _e:
                logger.warning(f"[LLM] model selection failed: {_e}")

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

            # Close memory connections
            if hasattr(self.memory_system, "close_connection"):
                self.memory_system.close_connection()

            self.initialized = False
            logger.info("[OK] Aetherra Engine shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def _register_system_components(self):
        """Register system components for health monitoring"""

        def check_memory_health():
            try:
                # Avoid asyncio.run() if we're already in an event loop
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # Create a dedicated loop in a fresh policy to run the coroutine safely
                    # Standard library imports
                    import threading

                    result_container = {}

                    def _runner():
                        try:
                            # Standard library imports
                            import asyncio as _asyncio

                            _new_loop = _asyncio.new_event_loop()
                            try:
                                _asyncio.set_event_loop(_new_loop)
                                result_container[
                                    "stats"
                                ] = _new_loop.run_until_complete(
                                    self.memory_system.get_memory_stats()
                                )
                            finally:
                                _new_loop.close()
                        except Exception as _e:
                            result_container["error"] = str(_e)

                    t = threading.Thread(target=_runner)
                    t.start()
                    t.join(timeout=2.0)
                    if "stats" in result_container:
                        stats = result_container["stats"] or {}
                    else:
                        raise RuntimeError(
                            result_container.get("error", "health-check-timeout")
                        )
                else:
                    # Safe to use asyncio.run when not in a running loop
                    stats = asyncio.run(self.memory_system.get_memory_stats())

                return {
                    "total_memories": (stats or {}).get("total_memories", 0),
                    "response_time": 100.0,  # Placeholder for measured latency
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
        # Mirror to persistent memory for quantum A/B (best-effort)
        try:
            if await self._ensure_persistent_memory():
                await self._persistent_memory.store(
                    {"event": "conversation_start", "user_id": user_id},
                    context={"session_id": self.session_id},
                    memory_type="conversation",
                    importance=0.5,
                    tags=["conversation", "session_start"],
                )
        except Exception:
            pass

        logger.info(f"Started conversation session: {self.session_id}")
        return self.session_id

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate response"""

        if not self.session_id:
            await self.start_conversation()

        try:
            # Mid-stream callback hooks (optional)
            _cbs = (
                (context or {}).get("_callbacks") if isinstance(context, dict) else None
            )

            def _cb(name: str):
                try:
                    if isinstance(_cbs, dict) and callable(_cbs.get(name)):
                        return _cbs.get(name)
                except Exception:
                    pass
                return None

            _on_thought = _cb("on_thought")
            _on_tool = _cb("on_tool")
            _on_chunk = _cb("on_chunk")

            def _safe_call(fn, *args, **kwargs):
                try:
                    if callable(fn):
                        fn(*args, **kwargs)
                except Exception:
                    pass

            t0 = datetime.now()
            # Update conversation context
            self.conversation_context["message_count"] += 1
            message_context = {
                **self.conversation_context,
                **(context or {}),
                "message": message,
                "timestamp": datetime.now(),
            }

            # AI Safety: sanitize input
            safe_message = self._sanitize_input(str(message))

            # Emit initial thought
            _safe_call(_on_thought, text="Analyzing message and recalling context")

            # Store user message in memory
            memory_id = await self.memory_system.store_memory(
                content={"role": "user", "content": safe_message},
                context=message_context,
                tags=["conversation", "user_message"],
                importance=0.7,
                memory_type="conversation",
            )
            # Mirror to persistent memory (best-effort)
            try:
                if await self._ensure_persistent_memory():
                    await self._persistent_memory.store(
                        {"role": "user", "content": safe_message},
                        context={
                            **{
                                k: (v.isoformat() if hasattr(v, "isoformat") else v)
                                for k, v in message_context.items()
                            },
                            "session_id": self.session_id,
                        },
                        memory_type="conversation",
                        importance=0.7,
                        tags=["conversation", "user_message"],
                    )
            except Exception:
                pass

            # Recall relevant memories with A/B selection
            bucket = self._choose_ab_bucket()
            t_recall0 = datetime.now()
            relevant_memories: List[Any] = []
            try:
                if bucket == "quantum" and await self._ensure_persistent_memory():
                    pm = self._persistent_memory
                    raw = await pm.retrieve(
                        safe_message, limit=8, memory_type="conversation"
                    )
                    # Adapt to expected shape for downstream usage
                    relevant_memories = [
                        {
                            "id": r.get("id"),
                            "content": r.get("content"),
                            "importance": float(r.get("importance", 0.5)),
                        }
                        for r in (raw or [])
                        if isinstance(r, dict)
                    ]
                else:
                    relevant_memories = await self.memory_system.recall_memories(
                        query_text=safe_message, limit=8, memory_type="conversation"
                    )
            except Exception:
                # Fallback to classical
                relevant_memories = await self.memory_system.recall_memories(
                    query_text=safe_message, limit=8, memory_type="conversation"
                )
                bucket = "classical"
            dt_recall_ms = (datetime.now() - t_recall0).total_seconds() * 1000.0
            self._record_ab_metric(bucket, dt_recall_ms)

            # Tool-like callback for memory recall
            try:
                _safe_call(
                    _on_tool,
                    {
                        "name": "memory_recall",
                        "mode": bucket,
                        "hits": len(relevant_memories),
                    },
                )
            except Exception:
                pass

            # RAG evidence selection (prefer higher importance)
            def _importance(m):
                try:
                    return float(getattr(m, "importance", 0.0) or 0.0)
                except Exception:
                    try:
                        return float((m or {}).get("importance", 0.0))
                    except Exception:
                        return 0.0

            sorted_hits = sorted(relevant_memories or [], key=_importance, reverse=True)
            evidence = []
            for m in sorted_hits[:5]:
                try:
                    evidence.append(
                        {
                            "id": getattr(m, "id", None)
                            or (m.get("id") if isinstance(m, dict) else None),
                            "content": getattr(m, "content", None)
                            if not isinstance(m, dict)
                            else m.get("content"),
                            "importance": _importance(m),
                        }
                    )
                except Exception:
                    pass
            if evidence:
                self.session_metrics["rag_hits"] += 1
            else:
                self.session_metrics["rag_misses"] += 1

            # Perform reasoning about the message
            reasoning_context = {
                "query": f"How should I respond to: {safe_message}",
                "domain": "conversation",
                "context_data": {
                    "user_message": safe_message,
                    "conversation_history": [
                        (
                            m.content
                            if hasattr(m, "content")
                            else ((m or {}).get("content"))
                        )
                        for m in (relevant_memories or [])
                    ],
                    "evidence": evidence,
                    "session_context": self.conversation_context,
                },
                "constraints": ["be_helpful", "be_conversational"],
                "objectives": ["provide_value", "maintain_engagement"],
            }

            # Use mock reasoning for now - would import real ReasoningContext in production
            reasoning_result = await self.reasoning_engine.reason(reasoning_context)

            _safe_call(_on_thought, text="Reasoning complete, composing response")

            # Generate response using a real LLM when available
            raw_response: str
            used_llm = False
            try:
                await self._ensure_llm_selection()
                if self._llm_manager and self._llm_selected:
                    # Build a compact prompt including top evidence (RAG-lite)
                    evidence_snippets = []
                    for ev in (evidence or [])[:3]:
                        try:
                            c = ev.get("content") if isinstance(ev, dict) else None
                            if c:
                                evidence_snippets.append(str(c)[:500])
                        except Exception:
                            pass
                    evtxt = "\n\n".join(f"- {s}" for s in evidence_snippets)
                    base_prompt = (
                        f"User: {safe_message}\n\n"
                        + (f"Context:\n{evtxt}\n\n" if evtxt else "")
                        + "Be concise and helpful."
                    )
                    # Prefer async path; add diagnostic snapshot
                    try:
                        raw_response = await self._llm_manager.generate_response(
                            base_prompt
                        )
                        used_llm = True
                        try:
                            mi = (
                                self._llm_manager.get_current_model_info()
                                if hasattr(self._llm_manager, "get_current_model_info")
                                else None
                            )
                            self._last_llm_info = {
                                "event": "ok",
                                "model": mi,
                            }
                        except Exception:
                            pass
                    except Exception as _llm_err:
                        # Capture error and fall back
                        try:
                            mi = (
                                self._llm_manager.get_current_model_info()
                                if hasattr(self._llm_manager, "get_current_model_info")
                                else None
                            )
                        except Exception:
                            mi = None
                        self._last_llm_info = {
                            "event": "error",
                            "model": mi,
                            "error": str(_llm_err),
                        }
                        logger.warning(
                            f"[LLM] generation failed; falling back: {type(_llm_err).__name__}: {_llm_err}"
                        )
                        logger.debug("[LLM] traceback:\n" + traceback.format_exc())
                        raise
                else:
                    raise RuntimeError("llm_not_ready")
            except Exception:
                # Fallback to placeholder generator if LLM not available
                raw_response = self._generate_response(
                    safe_message, reasoning_result, relevant_memories
                )

            # AI Safety: apply output filters/policies
            response = self._apply_output_filters(raw_response)

            # Emit a couple of streaming chunks (best-effort preview)
            try:
                if callable(_on_chunk):
                    # Split into 2-3 rough chunks without heavy logic
                    txt = str(response or "")
                    n = max(1, min(3, 1 + (len(txt) // 240)))
                    step = max(1, len(txt) // n)
                    for i in range(0, len(txt), step):
                        piece = txt[i : i + step]
                        if not piece:
                            continue
                        _safe_call(_on_chunk, text=piece, index=i // step)
                        # tiny yield to let outer poller drain
                        await asyncio.sleep(0)
            except Exception:
                pass

            # Human style layer (env-driven; best-effort)
            try:
                # Local imports
                from ..conversation.human_style import HumanStyle

                styler = getattr(self, "_human_styler", None)
                if styler is None:
                    styler = HumanStyle()
                    self._human_styler = styler
                styled, markers = styler.enhance(
                    user_message=safe_message,
                    base_text=response,
                    evidence_count=len(evidence),
                    bucket_index=int(self.session_metrics.get("messages", 0)),
                )
                response = styled
                # Record markers to metrics
                try:
                    if getattr(markers, "used_contractions", 0):
                        self.session_metrics["style_contractions"] += 1
                    if getattr(markers, "asked_question", False):
                        self.session_metrics["style_questions"] += 1
                    if getattr(markers, "used_empathy", False):
                        self.session_metrics["style_empathy"] += 1
                except Exception:
                    pass
            except Exception:
                # Styler optional
                pass

            # Store assistant response in memory
            await self.memory_system.store_memory(
                content={"role": "assistant", "content": response},
                context=message_context,
                tags=["conversation", "assistant_response"],
                importance=0.8,
                memory_type="conversation",
            )
            # Mirror assistant response to persistent memory (best-effort)
            try:
                if await self._ensure_persistent_memory():
                    await self._persistent_memory.store(
                        {"role": "assistant", "content": response},
                        context={
                            **{
                                k: (v.isoformat() if hasattr(v, "isoformat") else v)
                                for k, v in message_context.items()
                            },
                            "session_id": self.session_id,
                        },
                        memory_type="conversation",
                        importance=0.8,
                        tags=["conversation", "assistant_response"],
                    )
            except Exception:
                pass

            # Record performance metrics
            self.improvement_engine.record_performance_metric(
                "response_generation_time", 0.5, "seconds"
            )

            # Compute per-message metrics
            dt_ms = (datetime.now() - t0).total_seconds() * 1000.0
            try:
                self.session_metrics["messages"] += 1
                self.session_metrics["reasoning_latency_ms"].append(dt_ms)
            except Exception:
                pass

            # Structured confidence calibration (planned shape)
            conf_struct = {
                "model": float(reasoning_result.get("confidence", 0.8))
                if isinstance(reasoning_result, dict)
                else 0.8,
                "grounding": 0.9 if evidence else 0.6,
                "coherence": 0.8,
                "safety": 0.95,
            }
            conservative_conf = min(conf_struct.values())

            return {
                "response": response,
                "session_id": self.session_id,
                "reasoning": reasoning_result.get("reasoning", "Mock reasoning"),
                "confidence": conservative_conf,
                "confidence_details": conf_struct,
                "memory_id": memory_id,
                "relevant_memories_count": len(relevant_memories),
                "timestamp": datetime.now().isoformat(),
                "ab_bucket": bucket,
                "llm": {
                    "used": bool(used_llm),
                    "model": (
                        (self._llm_manager.get_current_model_info())
                        if (self._llm_manager and self._llm_selected)
                        else None
                    ),
                    **(
                        {} if not self._last_llm_info else {"diag": self._last_llm_info}
                    ),
                },
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
            "session_metrics": {
                "messages": self.session_metrics.get("messages", 0),
                "avg_reasoning_latency_ms": (
                    sum(self.session_metrics.get("reasoning_latency_ms", []) or [0])
                    / max(1, len(self.session_metrics.get("reasoning_latency_ms", [])))
                ),
                "rag_hits": self.session_metrics.get("rag_hits", 0),
                "rag_misses": self.session_metrics.get("rag_misses", 0),
                "safety_filters_triggered": self.session_metrics.get(
                    "safety_filters_triggered", 0
                ),
                # Style layer counters
                "style_contractions": self.session_metrics.get("style_contractions", 0),
                "style_questions": self.session_metrics.get("style_questions", 0),
                "style_empathy": self.session_metrics.get("style_empathy", 0),
                # A/B recall counters
                "ab_recall_total": self.session_metrics.get("ab_recall_total", 0),
                "ab_recall_classical_total": self.session_metrics.get(
                    "ab_recall_classical_total", 0
                ),
                "ab_recall_quantum_total": self.session_metrics.get(
                    "ab_recall_quantum_total", 0
                ),
                "ab_recall_latency_ms_sum_classical": self.session_metrics.get(
                    "ab_recall_latency_ms_sum_classical", 0.0
                ),
                "ab_recall_latency_ms_count_classical": self.session_metrics.get(
                    "ab_recall_latency_ms_count_classical", 0
                ),
                "ab_recall_latency_ms_sum_quantum": self.session_metrics.get(
                    "ab_recall_latency_ms_sum_quantum", 0.0
                ),
                "ab_recall_latency_ms_count_quantum": self.session_metrics.get(
                    "ab_recall_latency_ms_count_quantum", 0
                ),
            },
            "ab": {
                "mode": self._ab_mode(),
                "pmem_ready": bool(self._persistent_memory is not None),
            },
        }

    async def execute_task(
        self, task_name: str, task_data: Dict[str, Any], priority: str = "normal"
    ) -> str:
        """Execute a task using the agent orchestrator"""

        # Create a simple task dict for mock orchestrator
        # Observer-aware: infer sensitivity and coherence estimate for policy gating
        sensitive = bool(task_data.get("sensitive", False))
        try:
            nm = str(task_name or "").lower()
            if any(
                nm.startswith(p)
                for p in [
                    "delete.",
                    "write.",
                    "external.",
                    "network.",
                    "danger.",
                    "unsafe.",
                ]
            ):
                sensitive = True
        except Exception:
            pass
        req_caps = task_data.get("required_capabilities", [])
        try:
            caps = [str(c).lower() for c in (req_caps or [])]
            if any(
                c in {"network", "filesystem_write", "external_call", "danger"}
                for c in caps
            ):
                sensitive = True
        except Exception:
            pass
        # Coherence estimate (0..1) — env override, else simple heuristic from session metrics
        coherence_est = self._estimate_coherence()
        require_human = bool(task_data.get("require_human", False))

        task = {
            "task_id": f"task_{datetime.now().isoformat()}",
            "name": task_name,
            "description": f"User requested task: {task_name}",
            "required_capabilities": task_data.get("required_capabilities", []),
            "input_data": {
                **task_data,
                # Observer-aware fields
                "observer_gate": True,
                "sensitive": sensitive,
                "coherence_est": coherence_est,
                "require_human_approval": require_human,
            },
            "priority": priority,
            "max_execution_time": task_data.get("timeout", 300),
            "dependencies": task_data.get("dependencies", []),
        }

        task_id = await self.agent_orchestrator.submit_task(task)
        self.active_tasks[task_id] = task

        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.agent_orchestrator.get_task_status(task_id)

    def _estimate_coherence(self) -> float:
        """Best-effort coherence estimate for observer-aware policy.

        Precedence:
        - AETHERRA_COHERENCE_EST env var if set.
        - RAG signal heuristic from session metrics.
        - Default 0.8.
        """
        try:
            envv = os.environ.get("AETHERRA_COHERENCE_EST")
            if envv is not None and envv != "":
                v = float(envv)
                return max(0.0, min(1.0, v))
        except Exception:
            pass
        try:
            hits = int(self.session_metrics.get("rag_hits", 0) or 0)
            misses = int(self.session_metrics.get("rag_misses", 0) or 0)
            total = max(1, hits + misses)
            base = hits / total
            # Nudge by safety: fewer safety triggers -> slightly higher coherence
            safety = int(self.session_metrics.get("safety_filters_triggered", 0) or 0)
            adj = max(-0.2, 0.1 - 0.02 * min(5, safety))
            val = max(0.0, min(1.0, base + adj))
            return float(val)
        except Exception:
            return 0.8

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

    # --------- AI Safety and RAG helpers ---------
    def _sanitize_input(self, text: str) -> str:
        """Best-effort prompt-injection hardening (lightweight)."""
        try:
            lowered = text.lower()
            banned = [
                "ignore previous",
                "disregard previous",
                "system prompt",
                "instructions above",
            ]
            if any(b in lowered for b in banned):
                # Redact risky phrases
                self.session_metrics["safety_filters_triggered"] += 1
                for b in banned:
                    lowered = lowered.replace(b, "[redacted]")
                return lowered
        except Exception:
            pass
        return text

    def _apply_output_filters(self, text: str) -> str:
        """Apply simple output policy filters before returning to user."""
        try:
            # Basic redaction of secrets-like patterns
            patterns = [
                ("api_key=", "api_key=[redacted]"),
                ("password=", "password=[redacted]"),
            ]
            out = text
            for pat, rep in patterns:
                out = out.replace(pat, rep)
            return out
        except Exception:
            return text

    def add_scratch(self, entry: Dict[str, Any]):
        """Append to ephemeral scratchpad (not persisted)."""
        try:
            self._scratchpad.append({**entry, "ts": datetime.now().isoformat()})
            # bound to avoid unbounded growth
            if len(self._scratchpad) > 2000:
                self._scratchpad = self._scratchpad[-1000:]
        except Exception:
            pass

    def get_session_metrics(self) -> Dict[str, Any]:
        """Return lightweight per-session metrics."""
        return dict(self.session_metrics)

    # --------- AB/Quantum recall integration helpers ---------
    def _ab_mode(self) -> str:
        mode = os.environ.get("AETHERRA_AB_RECALL_MODE", "classical").strip().lower()
        return mode if mode in ("classical", "quantum", "abp") else "classical"

    def _choose_ab_bucket(self) -> str:
        forced = os.environ.get("AETHERRA_AB_FORCE_BUCKET", "").strip().lower()
        if forced in ("a", "classical"):
            return "classical"
        if forced in ("b", "quantum"):
            return "quantum"
        mode = self._ab_mode()
        if mode in ("classical", "quantum"):
            return mode
        # abp mode: percentage rollout
        try:
            pct = int(os.environ.get("AETHERRA_AB_RECALL_PCT", "50"))
        except Exception:
            pct = 50
        try:
            seed = int(os.environ.get("AETHERRA_AB_RECALL_SEED", "7"))
        except Exception:
            seed = 7
        key = f"{self.session_id or 'nosess'}:{self._msg_counter}:{seed}"
        bucket_val = abs(hash(key)) % 100
        try:
            self._msg_counter += 1
        except Exception:
            pass
        return "quantum" if bucket_val < max(0, min(100, pct)) else "classical"

    def _record_ab_metric(self, bucket: str, dt_ms: float):
        try:
            bucket = "quantum" if bucket == "quantum" else "classical"
            # totals
            self.session_metrics["ab_recall_total"] = (
                int(self.session_metrics.get("ab_recall_total", 0)) + 1
            )
            k_total = f"ab_recall_{bucket}_total"
            self.session_metrics[k_total] = (
                int(self.session_metrics.get(k_total, 0)) + 1
            )
            # latency aggregates
            ksum = f"ab_recall_latency_ms_sum_{bucket}"
            kcnt = f"ab_recall_latency_ms_count_{bucket}"
            self.session_metrics[ksum] = float(
                self.session_metrics.get(ksum, 0.0)
            ) + float(dt_ms)
            self.session_metrics[kcnt] = int(self.session_metrics.get(kcnt, 0)) + 1
        except Exception:
            pass

    async def _ensure_persistent_memory(self) -> bool:
        """Ensure the persistent memory system is available. Returns True if ready."""
        try:
            if self._persistent_memory is not None:
                return True
            if self._ab_mode() not in ("quantum", "abp"):
                return False
            # Aetherra imports
            from aetherra_persistent_memory import (
                get_persistent_memory_system as _get_pmem,
            )

            self._persistent_memory = await _get_pmem()
            return self._persistent_memory is not None
        except Exception:
            return False

    async def reflect_on_day(self) -> Dict[str, Any]:
        """Night-cycle hook: run a small evaluation harness and generate insights."""
        try:
            eval_summary = {
                "conversations": self.session_metrics.get("messages", 0),
                "avg_latency_ms": (
                    sum(self.session_metrics.get("reasoning_latency_ms", []) or [0])
                    / max(1, len(self.session_metrics.get("reasoning_latency_ms", [])))
                ),
                "rag_hit_rate": (
                    (self.session_metrics.get("rag_hits", 0))
                    / max(
                        1,
                        self.session_metrics.get("rag_hits", 0)
                        + self.session_metrics.get("rag_misses", 0),
                    )
                ),
            }
            # Store a brief narrative in memory (optional)
            try:
                await self.memory_system.store_memory(
                    content={
                        "narrative": {
                            "type": "reflection",
                            "summary": f"Daily reflection: {eval_summary}",
                        }
                    },
                    tags=["narrative", "reflection"],
                    memory_type="reflection",
                )
            except Exception:
                pass
            # Nudge self-improvement engine
            try:
                self.improvement_engine.record_performance_metric(
                    "rag_hit_rate", eval_summary["rag_hit_rate"], "ratio"
                )
            except Exception:
                pass
            return {"status": "ok", "evaluation": eval_summary}
        except Exception as e:
            logger.debug(f"[REFLECT] Night reflection failed: {e}")
            return {"status": "error"}

    # --------- Agent Evaluation Harness (lightweight) ---------
    async def run_agent_evaluation(
        self, plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run a tiny benchmark of agent tasks via the orchestrator and summarize.

        Inputs:
        - plan (optional): { cases: [ {name, data, priority}... ], timeout_sec?: int }

        Outputs:
        - report dict with summary metrics and per-case results.
        """
        try:
            if not self.initialized:
                await self.initialize()
        except Exception:
            # continue in best-effort mode
            pass

        cases = []
        if isinstance(plan, dict) and isinstance(plan.get("cases"), list):
            cases = list(plan["cases"])  # type: ignore[index]
        else:
            cases = [
                {"name": "eval.quick.status", "data": {"x": 1}, "priority": "high"},
                {
                    "name": "eval.io.light",
                    "data": {"payload": "abc"},
                    "priority": "normal",
                },
                {
                    "name": "eval.compute.light",
                    "data": {"n": 5},
                    "priority": "background",
                },
            ]
        timeout_sec = 3
        if isinstance(plan, dict) and isinstance(plan.get("timeout_sec"), (int, float)):
            timeout_sec = int(plan["timeout_sec"])  # type: ignore[index]

        results: List[Dict[str, Any]] = []
        t_all0 = time.time()
        for c in cases:
            name = str(c.get("name") or "eval.task")
            raw_data = c.get("data")
            data: Dict[str, Any] = raw_data if isinstance(raw_data, dict) else {}
            prio = str(c.get("priority") or "normal")
            t0 = time.time()
            try:
                if not hasattr(self, "execute_task"):
                    raise RuntimeError("engine lacks execute_task")
                task_id = await self.execute_task(name, data, prio)
                # Poll quickly for completion
                deadline = time.time() + timeout_sec
                last = None
                while time.time() < deadline:
                    st = None
                    try:
                        st = self.get_task_status(task_id)
                    except Exception:
                        st = None
                    if isinstance(st, dict):
                        last = st
                        prog = float(st.get("progress", 0) or 0)
                        state = str(st.get("state", "")).lower()
                        if prog >= 100 or state in ("done", "complete", "failed"):
                            break
                    await asyncio.sleep(0.05)
                dt = max(0.0, time.time() - t0)
                ok = bool((last or {}).get("progress", 0) >= 100) and str(
                    (last or {}).get("state", "")
                ).lower() in ("done", "complete")
                results.append(
                    {
                        "name": name,
                        "task_id": task_id,
                        "duration_sec": dt,
                        "ok": ok,
                        "status": last or {},
                    }
                )
            except Exception as e:
                dt = max(0.0, time.time() - t0)
                results.append(
                    {
                        "name": name,
                        "task_id": None,
                        "duration_sec": dt,
                        "ok": False,
                        "error": str(e),
                    }
                )

        # Summaries
        total = len(results)
        succ = sum(1 for r in results if r.get("ok"))
        fail = total - succ
        avg_dur = sum(float(r.get("duration_sec", 0) or 0) for r in results) / max(
            1, total
        )
        # Error clustering (very light): by error string or state
        clusters: Dict[str, int] = {}
        for r in results:
            key = None
            if not r.get("ok"):
                key = str(
                    r.get("error") or (r.get("status") or {}).get("state") or "error"
                )
            if key:
                clusters[key] = clusters.get(key, 0) + 1

        report = {
            "ts": datetime.now().isoformat(),
            "cases": results,
            "summary": {
                "total": total,
                "success": succ,
                "failed": fail,
                "avg_duration_sec": avg_dur,
                "errors": clusters,
                "wall_time_sec": max(0.0, time.time() - t_all0),
            },
        }
        # Simple meta suggestions to guide operators
        suggestions: List[str] = []
        if fail > 0:
            suggestions.append(
                "Some evaluations failed — inspect 'summary.errors' and recent agent logs"
            )
        if avg_dur > 2.0:
            suggestions.append(
                "Average duration is high — consider increasing parallelism or reducing max_execution_time"
            )
        if not suggestions:
            suggestions.append("All evaluations passed quickly — no action needed")
        report["suggestions"] = suggestions
        self._last_agent_eval = report
        return report

    def get_last_agent_evaluation(self) -> Optional[Dict[str, Any]]:
        """Return the last agent evaluation report, if any."""
        return self._last_agent_eval

    # --------- LLM selection helpers ---------
    async def _ensure_llm_selection(self) -> bool:
        """Ensure an LLM model is selected in the MultiLLMManager.

        Preference order is controlled by env AETHERRA_LLM_PROVIDER_PREF (comma list),
        default: "ollama,openai,anthropic,gemini,llamacpp". A specific model can be
        forced via AETHERRA_LLM_MODEL.
        """
        if self._llm_selected:
            return True
        mgr = self._llm_manager
        if mgr is None:
            return False
        try:
            preferred = os.environ.get(
                "AETHERRA_LLM_PROVIDER_PREF",
                "ollama,openai,anthropic,gemini,llamacpp",
            )
            order = [p.strip().lower() for p in preferred.split(",") if p.strip()]
            force_model = os.environ.get("AETHERRA_LLM_MODEL", "").strip()

            models = mgr.list_available_models()  # name -> info
            selected = None
            # If a model is forced and exists, use it
            if force_model and force_model in models:
                if mgr.set_model(force_model):
                    self._llm_selected = True
                    logger.info(f"[LLM] selected forced model: {force_model}")
                    return True
            # Otherwise, pick by provider order, preferring local where possible
            for prov in order:
                for name, info in models.items():
                    try:
                        if str(info.get("provider", "")).lower() == prov:
                            if mgr.set_model(name):
                                selected = name
                                break
                    except Exception:
                        continue
                if selected:
                    break
            if selected:
                self._llm_selected = True
                logger.info(f"[LLM] selected model: {selected}")
                return True
            logger.warning("[LLM] no suitable model found in configurations")
            return False
        except Exception as e:
            logger.warning(f"[LLM] selection error: {e}")
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
