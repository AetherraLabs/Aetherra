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
import hashlib
import json
import logging
import os
import re
import time
import uuid
from contextlib import suppress
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional

# Try to import components while tracking import failures.
COMPONENT_IMPORT_ERRORS: dict[str, Exception] = {}


class ComponentUnavailableError(RuntimeError):
    """Raised when an unavailable optional component is used."""


def _component_unavailable_error(component_key: str) -> str:
    return f"component_unavailable:{component_key}"


# Core component imports with explicit degraded fallbacks.
try:
    # Local imports
    from ..memory.memory_core import AetherraMemorySystem
except ImportError as exc:
    COMPONENT_IMPORT_ERRORS["memory_system"] = exc

    class AetherraMemorySystem:
        def __init__(self, *args, **kwargs):
            self._error = COMPONENT_IMPORT_ERRORS["memory_system"]

        def _unavailable(self):
            raise ComponentUnavailableError(_component_unavailable_error("memory_system"))

        async def store(self, *args, **kwargs):
            self._unavailable()

        async def retrieve(self, *args, **kwargs):
            self._unavailable()

        async def store_memory(self, *args, **kwargs):
            self._unavailable()

        async def recall_memories(self, *args, **kwargs):
            self._unavailable()

        async def get_memory_stats(self, *args, **kwargs):
            self._unavailable()

        async def get_conversation_context(self, *args, **kwargs):
            self._unavailable()

        async def store_learning(self, *args, **kwargs):
            self._unavailable()

        def close_connection(self, *args, **kwargs):
            return None


try:
    # Prefer canonical reflection path
    # Local imports
    from ..reflection.introspection_controller import IntrospectionController
except ImportError:
    try:
        # Back-compat fallback used in older layouts
        # Local imports
        from .introspection_controller import IntrospectionController  # type: ignore
    except ImportError as exc:
        COMPONENT_IMPORT_ERRORS["introspection"] = exc

        class IntrospectionController:
            def __init__(self, *args, **kwargs):
                self._error = COMPONENT_IMPORT_ERRORS["introspection"]

            async def start_introspection(self, *args, **kwargs):
                return None

            async def stop_introspection(self, *args, **kwargs):
                return None

            def get_health_status(self, *args, **kwargs):
                return {
                    "status": "unavailable",
                    "health": "degraded",
                    "error": _component_unavailable_error("introspection"),
                }

            @property
            def component_monitor(self):
                return None


try:
    # Prefer canonical plugin package path
    # Local imports
    from ..plugins.plugin_chain_executor import PluginChainExecutor
except ImportError:
    try:
        # Back-compat fallback used in older layouts
        # Local imports
        from .plugin_chain_executor import PluginChainExecutor  # type: ignore
    except ImportError as exc:
        COMPONENT_IMPORT_ERRORS["plugin_executor"] = exc

        class PluginChainExecutor:
            def __init__(self, *args, **kwargs):
                self._error = COMPONENT_IMPORT_ERRORS["plugin_executor"]

            async def execute_chain(self, *args, **kwargs):
                return {
                    "status": "unavailable",
                    "results": [],
                    "error": _component_unavailable_error("plugin_executor"),
                }


try:
    # Local imports
    from .reasoning_engine import ReasoningContext, ReasoningEngine
except ImportError as exc:
    COMPONENT_IMPORT_ERRORS["reasoning_engine"] = exc

    class ReasoningContext:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class ReasoningEngine:
        def __init__(self, *args, **kwargs):
            self._error = COMPONENT_IMPORT_ERRORS["reasoning_engine"]

        async def reason(self, *args, **kwargs):
            return {
                "status": "unavailable",
                "reasoning": "Reasoning engine unavailable",
                "error": _component_unavailable_error("reasoning_engine"),
            }


try:
    # Local imports
    from .self_improvement_engine import SelfImprovementEngine
except ImportError as exc:
    COMPONENT_IMPORT_ERRORS["self_improvement"] = exc

    class SelfImprovementEngine:
        def __init__(self, *args, **kwargs):
            self._error = COMPONENT_IMPORT_ERRORS["self_improvement"]

        async def start_improvement_cycle(self, *args, **kwargs):
            return None

        async def stop_improvement_cycle(self, *args, **kwargs):
            return None

        def record_performance_metric(self, *args, **kwargs):
            return {
                "status": "unavailable",
                "error": _component_unavailable_error("self_improvement"),
            }

        def get_improvement_status(self, *args, **kwargs):
            return {
                "status": "unavailable",
                "improvements": 0,
                "error": _component_unavailable_error("self_improvement"),
            }


try:
    # Prefer canonical path
    # Local imports
    from ..agents.agent_orchestrator import AgentOrchestrator, Task, TaskPriority
except ImportError:
    try:
        # Fallback to deprecated shim (emits DeprecationWarning)
        # Local imports
        from ..orchestration.agent_orchestrator import (  # type: ignore
            AgentOrchestrator,
            Task,
            TaskPriority,
        )
    except ImportError as exc:
        COMPONENT_IMPORT_ERRORS["agent_orchestrator"] = exc
        Task = None  # type: ignore[assignment]
        TaskPriority = None  # type: ignore[assignment]

        class AgentOrchestrator:
            def __init__(self, *args, **kwargs):
                self._error = COMPONENT_IMPORT_ERRORS["agent_orchestrator"]

            async def start_orchestration(self, *args, **kwargs):
                return None

            async def stop_orchestration(self, *args, **kwargs):
                return None

            def get_system_status(self, *args, **kwargs):
                return {
                    "status": "unavailable",
                    "total_agents": 0,
                    "pending_tasks": 0,
                    "error": _component_unavailable_error("agent_orchestrator"),
                }

            async def submit_task(self, *args, **kwargs):
                return {
                    "status": "unavailable",
                    "task_id": None,
                    "error": _component_unavailable_error("agent_orchestrator"),
                }

            def get_task_status(self, *args, **kwargs):
                return {
                    "status": "unavailable",
                    "progress": 0,
                    "error": _component_unavailable_error("agent_orchestrator"),
                }

            async def orchestrate(self, *args, **kwargs):
                return {
                    "status": "unavailable",
                    "result": None,
                    "error": _component_unavailable_error("agent_orchestrator"),
                }


logger = logging.getLogger(__name__)

REQUIRED_COMPONENT_KEYS = {
    "memory_system",
    "reasoning_engine",
    "agent_orchestrator",
}

ENGINE_PROCESSING_ERROR_CODE = "engine_processing_failed"
ENGINE_PROCESSING_ERROR_MESSAGE = (
    "I apologize, but I encountered an internal processing error."
)
ENGINE_VALIDATION_ERROR_CODE = "engine_validation_failed"
ENGINE_VALIDATION_ERROR_MESSAGE = "I couldn't process that request because it is invalid."
MAX_MESSAGE_CHARS = 12000
MAX_USER_ID_CHARS = 64
MAX_CONTEXT_KEYS = 32
MAX_CONTEXT_VALUE_CHARS = 512
MAX_CONTEXT_LIST_ITEMS = 16
MAX_EVIDENCE_CONTENT_CHARS = 1000
MAX_REASONING_HISTORY_ITEMS = 8
MAX_REASONING_HISTORY_CHARS = 800
MAX_REASONING_TEXT_CHARS = 1000
MAX_LLM_PROMPT_CHARS = 8000
MAX_LLM_EVIDENCE_SNIPPET_CHARS = 500
DEFAULT_LLM_TIMEOUT_SEC = 30.0
MAX_LLM_TIMEOUT_SEC = 120.0
ALLOWED_INTELLIGENCE_PROVIDERS = frozenset(
    {"mock", "openai", "anthropic", "ollama", "gemini", "llamacpp"}
)
PROMPT_INJECTION_PHRASES = (
    "ignore previous",
    "disregard previous",
    "system prompt",
    "instructions above",
)
TASK_PRIORITY_VALUES = frozenset({"low", "normal", "high", "critical"})
DEFAULT_TASK_TIMEOUT_SEC = 300
MAX_TASK_TIMEOUT_SEC = 3600
MAX_TASK_NAME_CHARS = 160
MAX_TASK_LIST_ITEMS = 32
MAX_TASK_LIST_ITEM_CHARS = 128
MAX_FEEDBACK_KEYS = 24
MAX_FEEDBACK_TEXT_CHARS = 1000
MAX_INTERACTION_ID_CHARS = 128
MAX_SCRATCHPAD_ENTRIES = 1000
MAX_SCRATCHPAD_ENTRY_KEYS = 16


def _hash_value(value: Any) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _short_trace_id(*parts: Any) -> str:
    raw = "|".join(str(part) for part in parts if part is not None)
    if not raw:
        raw = str(time.time_ns())
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _safe_exception_diagnostic(exc: Exception, code: str) -> Dict[str, str]:
    return {
        "code": code,
        "type": type(exc).__name__,
        "trace_id": _short_trace_id(code, type(exc).__name__, time.time_ns()),
    }


def _stable_percent_bucket(key: str) -> int:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % 100


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "ai:engine" and capability in {
        "agent:execute_task",
        "ai:execute_task",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_engine_task(
    *,
    task_name: str,
    task_data: Dict[str, Any],
    priority: str,
    sensitive: bool,
    coherence_est: float,
    require_human: bool,
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "ai:engine"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    required_capabilities = task_data.get("required_capabilities", [])
    if not isinstance(required_capabilities, list):
        required_capabilities = [str(required_capabilities)]
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="artificial_intelligence",
            action="ai.engine_execute_task",
            target=f"ai_task:{_hash_value(task_name)}",
            purpose="Submit an AI-engine task to the agent orchestrator",
            capabilities=("ai:execute_task", "agent:execute_task"),
            evidence=("ai.engine_execute_task:request",),
            reversible=True,
            rollback_plan="cancel queued task or stop task before side effects",
            metadata={
                "task_name_hash": _hash_value(task_name),
                "task_data_keys": sorted(str(key) for key in task_data),
                "required_capability_count": len(required_capabilities),
                "required_capability_hashes": [
                    _hash_value(capability) for capability in required_capabilities
                ],
                "priority": priority,
                "sensitive": sensitive,
                "coherence_est": coherence_est,
                "require_human": require_human,
                "timeout_present": "timeout" in task_data,
                "dependency_count": len(task_data.get("dependencies", []) or []),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


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
        self._profile = str(os.getenv("AETHERRA_PROFILE", "dev")).lower()

        missing_required = {
            key: err
            for key, err in COMPONENT_IMPORT_ERRORS.items()
            if key in REQUIRED_COMPONENT_KEYS
        }
        if self._profile in {"prod", "production"} and missing_required:
            details = ", ".join(sorted(missing_required))
            raise RuntimeError(
                "Required engine dependencies unavailable in production profile: " + details
            )

        if COMPONENT_IMPORT_ERRORS:
            logger.warning(
                "Engine running with degraded components: %s",
                ", ".join(sorted(COMPONENT_IMPORT_ERRORS.keys())),
            )

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
        self._last_input_persistence_info: Dict[str, Any] = {}
        self._last_recall_info: Dict[str, Any] = {}
        self._last_optional_processing_info: Dict[str, Any] = {}
        self._last_response_persistence_info: Dict[str, Any] = {}
        self._last_session_start_info: Dict[str, Any] = {}
        self._last_persistent_memory_info: Dict[str, Any] = {}
        self._last_task_execution_info: Dict[str, Any] = {}
        self._last_scratchpad_info: Dict[str, Any] = {"status": "empty", "entries": 0}
        self._last_coherence_info: Dict[str, Any] = {"status": "not_estimated"}
        self._last_reflection_info: Dict[str, Any] = {"status": "not_run"}
        self._lifecycle_diagnostics: List[Dict[str, str]] = []

        logger.info("Aetherra Engine initialized")

        # Engine metrics (lightweight, in-process)
        self._metrics_lock = Lock()
        # Message latency histogram (ms)
        self._msg_latency_hist: Dict[int, int] = {
            50: 0,
            100: 0,
            250: 0,
            500: 0,
            1000: 0,
            2000: 0,
            5000: 0,
        }
        self._msg_latency_sum_ms: float = 0.0
        self._msg_latency_count: int = 0
        # Recall latency histogram (ms)
        self._recall_latency_hist: Dict[int, int] = {
            10: 0,
            20: 0,
            50: 0,
            100: 0,
            200: 0,
            500: 0,
            1000: 0,
        }
        self._recall_latency_sum_ms: float = 0.0
        self._recall_latency_count: int = 0
        # Recall success/failure counters
        self._recall_success_total: int = 0
        self._recall_failure_total: int = 0
        # STORM canary (shadow) metrics
        self._storm_canary_comparisons: int = 0
        self._storm_canary_divergences: int = 0
        self._storm_canary_shadow_latency_sum_ms: float = 0.0
        self._storm_canary_shadow_latency_count: int = 0

    async def initialize(self):
        """Initialize the Aetherra engine and all subsystems"""
        if self.initialized:
            return

        try:
            # Bring up LLM manager (best-effort); selection happens below
            try:
                # Aetherra imports
                from Aetherra.core.multi_llm_manager import (  # type: ignore
                    get_llm_manager,
                )

                self._llm_manager = get_llm_manager()
            except Exception as exc:
                self._llm_manager = None
                self._record_lifecycle_failure("llm_manager", exc)

            # Start subsystems with graceful fallback
            await self._start_optional_subsystem(
                "improvement_system",
                self.improvement_engine,
                "start_improvement_cycle",
            )
            await self._start_optional_subsystem(
                "introspection",
                self.introspection,
                "start_introspection",
            )
            await self._start_optional_subsystem(
                "agent_orchestrator",
                self.agent_orchestrator,
                "start_orchestration",
            )

            # Register system components for monitoring
            self._register_system_components()

            # If A/B recall requires persistent memory, pre-initialize it (best-effort)
            try:
                if self._ab_mode() in ("quantum", "abp"):
                    await self._ensure_persistent_memory()
            except Exception as exc:
                self._record_lifecycle_failure("persistent_memory", exc)

            # Select an LLM model if possible (Ollama-first by default)
            try:
                await self._ensure_llm_selection()
            except Exception as exc:
                self._record_lifecycle_failure("llm_selection", exc)

            self.initialized = True
            logger.info("[OK] Aetherra Engine fully initialized")

        except Exception as exc:
            diagnostic = self._record_lifecycle_failure("engine_initialization", exc)
            logger.error(
                "Aetherra Engine initialization failed trace_id=%s",
                diagnostic["trace_id"],
            )
            raise RuntimeError("Aetherra Engine initialization failed") from exc

    async def shutdown(self):
        """Gracefully shutdown the Aetherra engine"""
        if not self.initialized:
            return

        try:
            # Stop subsystems with graceful fallback
            await self._stop_optional_subsystem(
                "improvement_system",
                self.improvement_engine,
                "stop_improvement_cycle",
            )
            await self._stop_optional_subsystem(
                "introspection",
                self.introspection,
                "stop_introspection",
            )
            await self._stop_optional_subsystem(
                "agent_orchestrator",
                self.agent_orchestrator,
                "stop_orchestration",
            )

            # Close memory connections
            try:
                if hasattr(self.memory_system, "close_connection"):
                    self.memory_system.close_connection()
            except Exception as exc:
                self._record_lifecycle_failure("memory_close", exc)

            self.initialized = False
            logger.info("[OK] Aetherra Engine shutdown complete")

        except Exception as exc:
            diagnostic = self._record_lifecycle_failure("engine_shutdown", exc)
            logger.error(
                "Aetherra Engine shutdown failed trace_id=%s",
                diagnostic["trace_id"],
            )

    async def _start_optional_subsystem(
        self, component: str, instance: Any, method_name: str
    ) -> bool:
        if not hasattr(instance, method_name):
            self._record_lifecycle_event(
                component,
                "lifecycle_method_unavailable",
                "degraded",
            )
            return False

        try:
            await getattr(instance, method_name)()
            self._record_lifecycle_event(component, "started", "ok")
            return True
        except Exception as exc:
            self._record_lifecycle_failure(f"{component}_start", exc)
            return False

    async def _stop_optional_subsystem(
        self, component: str, instance: Any, method_name: str
    ) -> bool:
        if not hasattr(instance, method_name):
            self._record_lifecycle_event(
                component,
                "lifecycle_method_unavailable",
                "degraded",
            )
            return False

        try:
            await getattr(instance, method_name)()
            self._record_lifecycle_event(component, "stopped", "ok")
            return True
        except Exception as exc:
            self._record_lifecycle_failure(f"{component}_stop", exc)
            return False

    def _record_lifecycle_failure(
        self, component: str, exc: Exception
    ) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, f"{component}_failed")
        self._record_lifecycle_event(
            component,
            diagnostic["code"],
            "degraded",
            diagnostic,
        )
        logger.warning(
            "Engine lifecycle component failed: %s trace_id=%s",
            component,
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_lifecycle_event(
        self,
        component: str,
        code: str,
        status: str,
        diagnostic: Optional[Dict[str, str]] = None,
    ) -> None:
        event = {
            "component": component,
            "code": code,
            "status": status,
        }
        if diagnostic:
            event["trace_id"] = diagnostic["trace_id"]
            event["type"] = diagnostic["type"]
        self._lifecycle_diagnostics.append(event)
        if len(self._lifecycle_diagnostics) > 64:
            self._lifecycle_diagnostics = self._lifecycle_diagnostics[-64:]

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
                                result_container["stats"] = _new_loop.run_until_complete(
                                    self.memory_system.get_memory_stats()
                                )
                            finally:
                                _new_loop.close()
                        except Exception as _e:
                            result_container["error"] = _safe_exception_diagnostic(
                                _e, "memory_health_failed"
                            )

                    t = threading.Thread(target=_runner)
                    t.start()
                    t.join(timeout=2.0)
                    if "stats" in result_container:
                        stats = result_container["stats"] or {}
                    elif "error" in result_container:
                        diagnostic = result_container["error"]
                        logger.warning(
                            "Memory health check failed trace_id=%s",
                            diagnostic["trace_id"],
                        )
                        return {
                            "response_time": 999.0,
                            "error": True,
                            "diagnostic": diagnostic,
                        }
                    else:
                        raise TimeoutError("memory_health_timeout")
                else:
                    # Safe to use asyncio.run when not in a running loop
                    stats = asyncio.run(self.memory_system.get_memory_stats())

                return {
                    "total_memories": (stats or {}).get("total_memories", 0),
                    "response_time": 100.0,  # Baseline until measured latency is available
                }
            except Exception as exc:
                diagnostic = _safe_exception_diagnostic(exc, "memory_health_failed")
                logger.warning(
                    "Memory health check failed trace_id=%s",
                    diagnostic["trace_id"],
                )
                return {
                    "response_time": 999.0,
                    "error": True,
                    "diagnostic": diagnostic,
                }

        def check_reasoning_health():
            return {"active_reasoning_sessions": 0}

        def check_orchestrator_health():
            try:
                status = self.agent_orchestrator.get_system_status()
                return {
                    "active_agents": status.get("total_agents", 0),
                    "pending_tasks": status.get("pending_tasks", 0),
                }
            except Exception as exc:
                diagnostic = _safe_exception_diagnostic(
                    exc, "orchestrator_health_failed"
                )
                logger.warning(
                    "Orchestrator health check failed trace_id=%s",
                    diagnostic["trace_id"],
                )
                return {
                    "active_agents": 0,
                    "pending_tasks": 0,
                    "error": True,
                    "diagnostic": diagnostic,
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
                logger.info("[INFO] Component monitoring not available - using basic health checks")
        except Exception as exc:
            self._record_lifecycle_failure("component_monitoring_setup", exc)
            logger.info("[INFO] Continuing with basic health checks")

    async def start_conversation(self, user_id: str = "default") -> str:
        """Start a new conversation session"""
        if not self.initialized:
            await self.initialize()

        normalized_user_id = self._normalize_user_id(user_id)
        self.session_id = f"session_{datetime.now().isoformat()}_{normalized_user_id}"
        self.conversation_context = {
            "user_id": normalized_user_id,
            "start_time": datetime.now(),
            "message_count": 0,
            "topics": [],
        }
        self._last_session_start_info = {"event": "started", "memory": {"status": "pending"}}

        # Store conversation start in memory
        try:
            await self.memory_system.store_memory(
                content={"event": "conversation_start", "user_id": normalized_user_id},
                context=self.conversation_context,
                tags=["conversation", "session_start"],
                importance=0.5,
                memory_type="conversation",
            )
            self._last_session_start_info["memory"] = {"status": "stored"}
        except Exception as exc:
            diagnostic = self._record_session_start_failure("session_memory_store_failed", exc)
            self._last_session_start_info["memory"] = {
                "status": "degraded",
                "error": diagnostic,
            }
        # Mirror to persistent memory for quantum A/B (best-effort)
        try:
            if await self._ensure_persistent_memory():
                await self._persistent_memory.store(
                    {"event": "conversation_start", "user_id": normalized_user_id},
                    context={"session_id": self.session_id},
                    memory_type="conversation",
                    importance=0.5,
                    tags=["conversation", "session_start"],
                )
                self._last_session_start_info["persistent_memory"] = {"status": "stored"}
        except Exception as exc:
            diagnostic = self._record_session_start_failure(
                "session_persistent_memory_store_failed", exc
            )
            self._last_session_start_info["persistent_memory"] = {
                "status": "degraded",
                "error": diagnostic,
            }

        logger.info(f"Started conversation session: {self.session_id}")
        return self.session_id

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate response"""

        if not self.session_id:
            await self.start_conversation()

        try:
            normalized_message = self._validate_message_input(message)
            self._last_optional_processing_info = {
                "callbacks": [],
                "streaming": {"status": "not_requested"},
                "style": {"status": "pending"},
                "session_metrics": {"status": "pending"},
            }
            # Mid-stream callback hooks (optional)
            _cbs = (context or {}).get("_callbacks") if isinstance(context, dict) else None

            def _cb(name: str):
                if isinstance(_cbs, dict) and callable(_cbs.get(name)):
                    return _cbs.get(name)
                return None

            _on_thought = _cb("on_thought")
            _on_tool = _cb("on_tool")
            _on_chunk = _cb("on_chunk")

            def _safe_call(name: str, fn, *args, **kwargs):
                try:
                    if callable(fn):
                        fn(*args, **kwargs)
                        return True
                except Exception as exc:
                    diagnostic = self._record_optional_processing_failure(
                        f"callback_{name}_failed", exc
                    )
                    self._last_optional_processing_info.setdefault("callbacks", []).append(
                        {
                            "name": name,
                            "status": "degraded",
                            "error": diagnostic,
                        }
                    )
                    return False
                return False

            t0 = datetime.now()
            # Update conversation context
            self.conversation_context["message_count"] += 1
            safe_external_context = self._sanitize_persisted_context(context)
            message_context = {
                **self.conversation_context,
                **safe_external_context,
                "message": normalized_message,
                "timestamp": datetime.now(),
            }

            # AI Safety: sanitize input
            safe_message = self._sanitize_input(normalized_message)

            # Emit initial thought
            _safe_call(
                "on_thought",
                _on_thought,
                text="Analyzing message and recalling context",
            )

            # Store user message in memory
            memory_id = await self.memory_system.store_memory(
                content={"role": "user", "content": safe_message},
                context=message_context,
                tags=["conversation", "user_message"],
                importance=0.7,
                memory_type="conversation",
            )
            self._last_input_persistence_info = {
                "memory": {"status": "stored"},
                "persistent_memory": {"status": "not_attempted"},
            }
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
                    self._last_input_persistence_info["persistent_memory"] = {
                        "status": "stored"
                    }
            except Exception as exc:
                diagnostic = self._record_input_persistence_failure(
                    "user_persistent_memory_store_failed", exc
                )
                self._last_input_persistence_info["persistent_memory"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }

            # Recall relevant memories with A/B selection
            bucket = self._choose_ab_bucket()
            t_recall0 = datetime.now()
            relevant_memories: List[Any] = []
            recall_success = True
            self._last_recall_info = {"event": "ok", "mode": bucket}
            try:
                if bucket == "quantum" and await self._ensure_persistent_memory():
                    pm = self._persistent_memory
                    raw = await pm.retrieve(safe_message, limit=8, memory_type="conversation")
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
            except Exception as exc:
                diagnostic = self._record_recall_failure("primary_recall_failed", exc)
                recall_success = False
                relevant_memories = []
                if bucket == "quantum":
                    with suppress(Exception):
                        relevant_memories = await self.memory_system.recall_memories(
                            query_text=safe_message, limit=8, memory_type="conversation"
                        )
                        recall_success = True
                        self._last_recall_info = {
                            "event": "degraded",
                            "mode": "classical",
                            "fallback_from": "quantum",
                            "error": diagnostic,
                        }
                bucket = "classical"
                if not relevant_memories:
                    self._last_recall_info = {
                        "event": "degraded",
                        "mode": bucket,
                        "error": diagnostic,
                    }
            dt_recall_ms = (datetime.now() - t_recall0).total_seconds() * 1000.0
            self._last_recall_info["ab_metric"] = self._record_ab_metric(
                bucket, dt_recall_ms
            )
            # Observe recall latency
            with suppress(Exception):
                self._observe_recall_latency(dt_recall_ms, success=recall_success)

            # Tool-like callback for memory recall
            with suppress(Exception):
                _safe_call(
                    "on_tool",
                    _on_tool,
                    {
                        "name": "memory_recall",
                        "mode": bucket,
                        "hits": len(relevant_memories),
                    },
                )

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
                with suppress(Exception):
                    content = (
                        getattr(m, "content", None)
                        if not isinstance(m, dict)
                        else m.get("content")
                    )
                    evidence.append(
                        {
                            "id": getattr(m, "id", None)
                            or (m.get("id") if isinstance(m, dict) else None),
                            "content": self._sanitize_evidence_content(content),
                            "importance": _importance(m),
                        }
                    )
            if evidence:
                self.session_metrics["rag_hits"] += 1
            else:
                self.session_metrics["rag_misses"] += 1

            # Optional STORM canary / shadow recall sampling (best-effort)
            storm_canary_info: Dict[str, Any] = {"status": "not_sampled"}
            try:
                pct_raw = os.getenv("AETHERRA_STORM_CANARY_PCT", "0").strip()
                pct = int(pct_raw) if pct_raw.isdigit() else 0
                if 0 < pct <= 100:
                    import random as _rand

                    if _rand.randint(1, 100) <= pct:
                        shadow_bucket = "quantum" if bucket == "classical" else "classical"
                        t_shadow0 = datetime.now()
                        shadow_hits: List[Any] = []
                        try:
                            if (
                                shadow_bucket == "quantum"
                                and await self._ensure_persistent_memory()
                            ):
                                pm = self._persistent_memory
                                raw_shadow = await pm.retrieve(
                                    safe_message, limit=8, memory_type="conversation"
                                )
                                shadow_hits = [r for r in (raw_shadow or []) if isinstance(r, dict)]
                            else:
                                shadow_hits = await self.memory_system.recall_memories(
                                    query_text=safe_message, limit=8, memory_type="conversation"
                                )

                            # Compare simple top-id equality (if both present)
                            def _get_id(x):
                                try:
                                    if isinstance(x, dict):
                                        return x.get("id")
                                    return getattr(x, "id", None)
                                except Exception:
                                    return None

                            top_a = _get_id(relevant_memories[0]) if relevant_memories else None
                            top_b = _get_id(shadow_hits[0]) if shadow_hits else None
                            with self._metrics_lock:
                                self._storm_canary_comparisons += 1
                                if top_a and top_b and top_a != top_b:
                                    self._storm_canary_divergences += 1
                                shadow_dt_ms = (datetime.now() - t_shadow0).total_seconds() * 1000.0
                                self._storm_canary_shadow_latency_sum_ms += shadow_dt_ms
                                self._storm_canary_shadow_latency_count += 1
                            storm_canary_info = {
                                "status": "sampled",
                                "mode": shadow_bucket,
                                "hits": len(shadow_hits),
                            }
                        except Exception as exc:
                            diagnostic = self._record_storm_canary_failure(
                                "storm_canary_shadow_recall_failed", exc
                            )
                            storm_canary_info = {
                                "status": "degraded",
                                "mode": shadow_bucket,
                                "error": diagnostic,
                            }
            except Exception as exc:
                diagnostic = self._record_storm_canary_failure(
                    "storm_canary_failed", exc
                )
                storm_canary_info = {
                    "status": "degraded",
                    "error": diagnostic,
                }
            self._last_recall_info["storm_canary"] = storm_canary_info

            # Perform reasoning about the message
            reasoning_context = ReasoningContext(
                query=f"How should I respond to: {safe_message}",
                domain="conversation",
                context_data={
                    "user_message": safe_message,
                    "conversation_history": [
                        self._sanitize_reasoning_history_content(
                            m.content if hasattr(m, "content") else ((m or {}).get("content"))
                        )
                        for m in (relevant_memories or [])[:MAX_REASONING_HISTORY_ITEMS]
                    ],
                    "evidence": evidence,
                    "session_context": self.conversation_context,
                },
                constraints=["be_helpful", "be_conversational"],
                objectives=["provide_value", "maintain_engagement"],
            )

            reasoning_result = await self.reasoning_engine.reason(reasoning_context)

            _safe_call(
                "on_thought",
                _on_thought,
                text="Reasoning complete, composing response",
            )

            # Generate response using a real LLM when available
            raw_response: str
            used_llm = False
            self._last_llm_info = {}
            # Provider router (Wave A): if AETHERRA_INTELLIGENCE_PROVIDER set, prefer provider adapters
            try:
                prov_name = self._normalize_intelligence_provider(
                    os.environ.get("AETHERRA_INTELLIGENCE_PROVIDER", "")
                )
            except Exception:
                self._record_llm_failure(
                    "provider_not_allowed",
                    ValueError("intelligence provider is not allowed"),
                )
                prov_name = ""
            try:
                if prov_name:
                    try:
                        # Local imports
                        from ..cognitive.reasoning_providers import call_provider  # type: ignore

                        base_prompt = self._build_llm_prompt(
                            safe_message,
                            evidence,
                            snippet_chars=300,
                        )
                        pr = await asyncio.wait_for(
                            call_provider(
                                base_prompt, evidence=evidence, provider_name=prov_name
                            ),
                            timeout=self._llm_timeout_seconds(),
                        )
                        raw_response = pr.text or ""
                        used_llm = True
                        self._last_llm_info = {
                            "event": "ok",
                            "provider": self._sanitize_context_value(pr.provider),
                            "model": self._sanitize_context_value(pr.model),
                        }
                    except Exception as _prov_err:
                        self._record_llm_failure(
                            "provider_adapter_failed",
                            _prov_err,
                            provider=prov_name,
                        )
                        raise
                else:
                    await self._ensure_llm_selection()
                    if self._llm_manager and self._llm_selected:
                        base_prompt = self._build_llm_prompt(safe_message, evidence)
                        # Prefer async path; add diagnostic snapshot
                        try:
                            raw_response = await asyncio.wait_for(
                                self._llm_manager.generate_response(base_prompt),
                                timeout=self._llm_timeout_seconds(),
                            )
                            used_llm = True
                            with suppress(Exception):
                                self._last_llm_info = {
                                    "event": "ok",
                                    "model": self._get_public_llm_model_info(),
                                }
                        except Exception as _llm_err:
                            self._record_llm_failure(
                                "llm_generation_failed",
                                _llm_err,
                            )
                            raise
                    else:
                        raise RuntimeError("llm_not_ready")
            except Exception as exc:
                if not self._last_llm_info or self._last_llm_info.get("event") != "error":
                    self._record_llm_failure("llm_unavailable", exc)
                # Fallback to built-in generator if LLM is unavailable
                raw_response = self._generate_response(
                    safe_message, reasoning_result, relevant_memories
                )

            # AI Safety: apply output filters/policies
            response = self._apply_output_filters(raw_response)

            # Emit a couple of streaming chunks (best-effort preview)
            try:
                if callable(_on_chunk):
                    emitted_chunks = 0
                    # Split into 2-3 rough chunks without heavy logic
                    txt = str(response or "")
                    n = max(1, min(3, 1 + (len(txt) // 240)))
                    step = max(1, len(txt) // n)
                    for i in range(0, len(txt), step):
                        piece = txt[i : i + step]
                        if not piece:
                            continue
                        _safe_call("on_chunk", _on_chunk, text=piece, index=i // step)
                        emitted_chunks += 1
                        # tiny yield to let outer poller drain
                        await asyncio.sleep(0)
                    self._last_optional_processing_info["streaming"] = {
                        "status": "emitted",
                        "chunks": emitted_chunks,
                    }
            except Exception as exc:
                diagnostic = self._record_optional_processing_failure(
                    "streaming_preview_failed", exc
                )
                self._last_optional_processing_info["streaming"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }

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
                self._last_optional_processing_info["style"] = {"status": "applied"}
                # Record markers to metrics
                try:
                    if getattr(markers, "used_contractions", 0):
                        self.session_metrics["style_contractions"] += 1
                    if getattr(markers, "asked_question", False):
                        self.session_metrics["style_questions"] += 1
                    if getattr(markers, "used_empathy", False):
                        self.session_metrics["style_empathy"] += 1
                except Exception as exc:
                    diagnostic = self._record_optional_processing_failure(
                        "style_metrics_failed", exc
                    )
                    self._last_optional_processing_info["style_metrics"] = {
                        "status": "degraded",
                        "error": diagnostic,
                    }
            except Exception as exc:
                # Styler optional
                diagnostic = self._record_optional_processing_failure("style_failed", exc)
                self._last_optional_processing_info["style"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }

            # Store assistant response in memory
            self._last_response_persistence_info = {
                "assistant_memory": {"status": "pending"},
                "metrics": {"status": "pending"},
            }
            try:
                await self.memory_system.store_memory(
                    content={"role": "assistant", "content": response},
                    context=message_context,
                    tags=["conversation", "assistant_response"],
                    importance=0.8,
                    memory_type="conversation",
                )
                self._last_response_persistence_info["assistant_memory"] = {
                    "status": "stored"
                }
            except Exception as exc:
                diagnostic = self._record_response_persistence_failure(
                    "assistant_memory_store_failed", exc
                )
                self._last_response_persistence_info["assistant_memory"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }
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
                    self._last_response_persistence_info["persistent_memory"] = {
                        "status": "stored"
                    }
            except Exception as exc:
                diagnostic = self._record_response_persistence_failure(
                    "assistant_persistent_memory_store_failed", exc
                )
                self._last_response_persistence_info["persistent_memory"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }

            # Record performance metrics
            try:
                self.improvement_engine.record_performance_metric(
                    "response_generation_time", 0.5, "seconds"
                )
                self._last_response_persistence_info["metrics"] = {"status": "recorded"}
            except Exception as exc:
                diagnostic = self._record_response_persistence_failure(
                    "response_metric_record_failed", exc
                )
                self._last_response_persistence_info["metrics"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }

            # Compute per-message metrics
            dt_ms = (datetime.now() - t0).total_seconds() * 1000.0
            try:
                self.session_metrics["messages"] += 1
                self.session_metrics["reasoning_latency_ms"].append(dt_ms)
                self._last_optional_processing_info["session_metrics"] = {
                    "status": "recorded"
                }
            except Exception as exc:
                diagnostic = self._record_optional_processing_failure(
                    "session_metrics_failed", exc
                )
                self._last_optional_processing_info["session_metrics"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }

            # Structured confidence calibration (planned shape)
            reasoning_confidence = (
                float(reasoning_result.get("confidence", 0.8))
                if isinstance(reasoning_result, dict)
                else float(getattr(reasoning_result, "confidence", 0.8))
            )
            reasoning_text = (
                reasoning_result.get("reasoning", "Mock reasoning")
                if isinstance(reasoning_result, dict)
                else getattr(reasoning_result, "conclusion", "Mock reasoning")
            )
            public_reasoning_text = self._sanitize_reasoning_text(reasoning_text)
            conf_struct = {
                "model": reasoning_confidence,
                "grounding": 0.9 if evidence else 0.6,
                "coherence": 0.8,
                "safety": 0.95,
            }
            conservative_conf = min(conf_struct.values())

            return {
                "response": response,
                "session_id": self.session_id,
                "reasoning": public_reasoning_text,
                "confidence": conservative_conf,
                "confidence_details": conf_struct,
                "memory_id": memory_id,
                "input_persistence": self._last_input_persistence_info,
                "relevant_memories_count": len(relevant_memories),
                "evidence": evidence,  # surfaced for hub responses/stream (redacted by policy when needed)
                "timestamp": datetime.now().isoformat(),
                "ab_bucket": bucket,
                "recall": self._last_recall_info,
                "persistence": self._last_response_persistence_info,
                "optional_processing": self._last_optional_processing_info,
                "llm": {
                    "used": bool(used_llm),
                    "model": self._get_public_llm_model_info(),
                    **({} if not self._last_llm_info else {"diag": self._last_llm_info}),
                },
            }

        except ValueError as exc:
            return self._build_validation_error_response(exc)
        except Exception as exc:
            return self._build_processing_error_response(exc)

    def _generate_response(self, message: str, reasoning_result, relevant_memories: List) -> str:
        """Generate response based on message and context (baseline implementation)."""

        # This is a simple baseline; a production profile should prefer LLM output.
        reasoning_confidence = (
            float(reasoning_result.get("confidence", 0.8))
            if isinstance(reasoning_result, dict)
            else float(getattr(reasoning_result, "confidence", 0.8))
        )
        reasoning_text = (
            reasoning_result.get("reasoning", "Mock reasoning")
            if isinstance(reasoning_result, dict)
            else getattr(reasoning_result, "conclusion", "Mock reasoning")
        )

        if "hello" in message.lower():
            return f"Hello! I'm Lyrixa, your AI assistant. I understand you said: '{message}'. How can I help you today?"

        elif "?" in message:
            return f"That's an interesting question about '{message}'. Based on my reasoning (confidence: {reasoning_confidence:.2f}), I believe: {reasoning_text}"

        elif len(relevant_memories) > 0:
            return f"I remember we discussed similar topics. Regarding '{message}', I think: {reasoning_text}"

        else:
            return f"I understand you're talking about '{message}'. {reasoning_text} Is there anything specific you'd like to know or discuss?"

    async def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        if not self.session_id:
            return {"status": "no_active_session"}

        memory_status: Dict[str, Any] = {"status": "ok"}
        try:
            memories = await self.memory_system.get_conversation_context(
                self.session_id, limit=20
            )
        except Exception as exc:
            diagnostic = _safe_exception_diagnostic(
                exc, "conversation_summary_memory_failed"
            )
            logger.warning(
                "Conversation summary memory lookup failed trace_id=%s",
                diagnostic["trace_id"],
            )
            memories = []
            memory_status = {
                "status": "degraded",
                "error": diagnostic,
            }

        context = self._public_conversation_context()

        return {
            "session_id": self.session_id,
            "context": context,
            "message_count": len(memories) if isinstance(memories, list) else 0,
            "duration_minutes": self._conversation_duration_minutes(),
            "topics": context.get("topics", []),
            "memory": memory_status,
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self.initialized:
            return {"status": "not_initialized"}

        # Gather status from all subsystems. Status reporting must stay available
        # even when an underlying component is degraded.
        memory_stats = await self._collect_async_component_status(
            "memory_system", self.memory_system.get_memory_stats
        )
        improvement_status = self._collect_component_status(
            "improvement_system", self.improvement_engine.get_improvement_status
        )
        orchestrator_status = self._collect_component_status(
            "agent_orchestrator", self.agent_orchestrator.get_system_status
        )
        health_status = self._collect_component_status(
            "health_monitoring", self.introspection.get_health_status
        )

        return {
            "engine_status": "active" if self.initialized else "inactive",
            "session_active": self.session_id is not None,
            "memory_system": memory_stats,
            "improvement_system": improvement_status,
            "agent_orchestrator": orchestrator_status,
            "health_monitoring": health_status,
            "lifecycle": {
                "diagnostics": list(self._lifecycle_diagnostics),
            },
            "session_start": dict(self._last_session_start_info),
            "persistent_memory": dict(self._last_persistent_memory_info),
            "input_persistence": dict(self._last_input_persistence_info),
            "response_persistence": dict(self._last_response_persistence_info),
            "optional_processing": dict(self._last_optional_processing_info),
            "task_execution": dict(self._last_task_execution_info),
            "scratchpad": dict(self._last_scratchpad_info),
            "coherence": dict(self._last_coherence_info),
            "reflection": dict(self._last_reflection_info),
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
                "safety_filters_triggered": self.session_metrics.get("safety_filters_triggered", 0),
                # Style layer counters
                "style_contractions": self.session_metrics.get("style_contractions", 0),
                "style_questions": self.session_metrics.get("style_questions", 0),
                "style_empathy": self.session_metrics.get("style_empathy", 0),
                # A/B recall counters
                "ab_recall_total": self.session_metrics.get("ab_recall_total", 0),
                "ab_recall_classical_total": self.session_metrics.get(
                    "ab_recall_classical_total", 0
                ),
                "ab_recall_quantum_total": self.session_metrics.get("ab_recall_quantum_total", 0),
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

    async def _collect_async_component_status(self, component: str, fn) -> Dict[str, Any]:
        try:
            status = await fn()
            return status if isinstance(status, dict) else {"status": "unknown"}
        except Exception as exc:
            return self._component_status_failure(component, exc)

    def _collect_component_status(self, component: str, fn) -> Dict[str, Any]:
        try:
            status = fn()
            return status if isinstance(status, dict) else {"status": "unknown"}
        except Exception as exc:
            return self._component_status_failure(component, exc)

    def _component_status_failure(self, component: str, exc: Exception) -> Dict[str, Any]:
        diagnostic = _safe_exception_diagnostic(exc, f"{component}_status_failed")
        logger.warning(
            "Engine component status collection failed: %s trace_id=%s",
            component,
            diagnostic["trace_id"],
        )
        return {
            "status": "unavailable",
            "health": "degraded",
            "error": diagnostic,
        }

    async def get_alpha_readiness(self) -> Dict[str, Any]:
        """Return the Engine's public alpha-readiness contract."""
        from .readiness import build_ai_readiness_payload

        return build_ai_readiness_payload(await self.get_system_status())

    async def execute_task(
        self, task_name: str, task_data: Dict[str, Any], priority: str = "normal"
    ) -> str:
        """Execute a task using the agent orchestrator"""

        if not isinstance(task_data, dict):
            raise TypeError("task_data must be a dictionary")
        normalized_name = self._normalize_task_name(task_name)
        if not normalized_name:
            raise ValueError("task_name is required")
        normalized_priority = self._normalize_task_priority(priority)
        required_capabilities = self._normalize_string_list(
            task_data.get("required_capabilities", [])
        )
        dependencies = self._normalize_string_list(task_data.get("dependencies", []))
        timeout_sec = self._normalize_task_timeout(task_data.get("timeout"))

        # Observer-aware: infer sensitivity and coherence estimate for policy gating
        sensitive = bool(task_data.get("sensitive", False))
        try:
            nm = normalized_name.lower()
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
        try:
            caps = [cap.lower() for cap in required_capabilities]
            if any(c in {"network", "filesystem_write", "external_call", "danger"} for c in caps):
                sensitive = True
        except Exception:
            pass
        # Coherence estimate (0..1) — env override, else simple heuristic from session metrics
        coherence_est = self._estimate_coherence()
        require_human = bool(task_data.get("require_human", False))
        policy_task_data = {
            **task_data,
            "required_capabilities": required_capabilities,
            "dependencies": dependencies,
            "timeout": timeout_sec,
        }
        self._last_task_execution_info = {
            "status": "preflight",
            "task_name_hash": _hash_value(normalized_name),
            "required_capability_count": len(required_capabilities),
            "dependency_count": len(dependencies),
            "priority": normalized_priority,
            "sensitive": sensitive,
            "require_human": require_human,
        }
        try:
            decision = _guardian_preflight_engine_task(
                task_name=normalized_name,
                task_data=policy_task_data,
                priority=normalized_priority,
                sensitive=sensitive,
                coherence_est=coherence_est,
                require_human=require_human,
            )
        except Exception as exc:
            diagnostic = self._record_task_execution_failure(
                "task_preflight_failed", exc
            )
            self._last_task_execution_info.update(
                {"status": "preflight_failed", "error": diagnostic}
            )
            raise RuntimeError(
                f"task_preflight_failed:{diagnostic['trace_id']}"
            ) from None
        if not decision.allowed:
            self._last_task_execution_info.update(
                {
                    "status": "denied",
                    "reason": self._sanitize_context_value(decision.reason),
                }
            )
            raise PermissionError(decision.reason)
        self._last_task_execution_info.update(
            {
                "status": "approved",
                "decision": {
                    "status": str(decision.status),
                    "reason": self._sanitize_context_value(decision.reason),
                },
            }
        )

        task_record = {
            "task_id": f"task_{uuid.uuid4().hex}",
            "name": normalized_name,
            "description": f"User requested task: {normalized_name}",
            "required_capabilities": required_capabilities,
            "input_data": {
                **policy_task_data,
                # Observer-aware fields
                "observer_gate": True,
                "sensitive": sensitive,
                "coherence_est": coherence_est,
                "require_human_approval": require_human,
            },
            "priority": normalized_priority,
            "max_execution_time": timeout_sec,
            "dependencies": dependencies,
        }

        orchestrator_task = self._build_orchestrator_task(task_record)
        try:
            task_id = await self.agent_orchestrator.submit_task(orchestrator_task)
        except Exception as exc:
            diagnostic = self._record_task_execution_failure(
                "task_submission_failed", exc
            )
            self._last_task_execution_info.update(
                {"status": "submission_failed", "error": diagnostic}
            )
            raise RuntimeError(
                f"task_submission_failed:{diagnostic['trace_id']}"
            ) from None
        self.active_tasks[task_id] = task_record
        self._last_task_execution_info.update(
            {
                "status": "submitted",
                "task_id_hash": _hash_value(task_id),
            }
        )

        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.agent_orchestrator.get_task_status(task_id)

    def _normalize_task_priority(self, priority: Any) -> str:
        value = str(priority or "normal").strip().lower()
        return value if value in TASK_PRIORITY_VALUES else "normal"

    def _normalize_task_name(self, task_name: Any) -> str:
        normalized = str(task_name or "").strip()
        if len(normalized) > MAX_TASK_NAME_CHARS:
            raise ValueError("task_name exceeds maximum length")
        return normalized

    def _normalize_task_timeout(self, timeout: Any) -> int:
        if timeout is None:
            return DEFAULT_TASK_TIMEOUT_SEC
        try:
            timeout_sec = int(timeout)
        except (TypeError, ValueError):
            return DEFAULT_TASK_TIMEOUT_SEC
        return max(1, min(MAX_TASK_TIMEOUT_SEC, timeout_sec))

    def _normalize_string_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str | bytes):
            values = [value]
        else:
            try:
                values = list(value)
            except TypeError:
                values = [value]
        normalized: List[str] = []
        seen = set()
        for item in values:
            text = str(item).strip()
            if not text:
                continue
            text = text[:MAX_TASK_LIST_ITEM_CHARS]
            if text in seen:
                continue
            seen.add(text)
            normalized.append(text)
            if len(normalized) >= MAX_TASK_LIST_ITEMS:
                break
        return normalized

    def _build_orchestrator_task(self, task_record: Dict[str, Any]) -> Any:
        if Task is None or TaskPriority is None:
            return task_record
        priority = TaskPriority(task_record["priority"])
        return Task(
            task_id=task_record["task_id"],
            name=task_record["name"],
            description=task_record["description"],
            required_capabilities=list(task_record["required_capabilities"]),
            input_data=dict(task_record["input_data"]),
            priority=priority,
            max_execution_time=int(task_record["max_execution_time"]),
            dependencies=list(task_record["dependencies"]),
        )

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
                coherence = max(0.0, min(1.0, v))
                self._last_coherence_info = {
                    "status": "estimated",
                    "source": "environment",
                    "value": coherence,
                }
                return coherence
        except Exception as exc:
            diagnostic = self._record_coherence_failure(
                "coherence_env_parse_failed", exc
            )
            self._last_coherence_info = {
                "status": "degraded",
                "source": "environment",
                "fallback": 0.8,
                "error": diagnostic,
            }
            return 0.8
        try:
            hits = int(self.session_metrics.get("rag_hits", 0) or 0)
            misses = int(self.session_metrics.get("rag_misses", 0) or 0)
            total = max(1, hits + misses)
            base = hits / total
            # Nudge by safety: fewer safety triggers -> slightly higher coherence
            safety = int(self.session_metrics.get("safety_filters_triggered", 0) or 0)
            adj = max(-0.2, 0.1 - 0.02 * min(5, safety))
            val = max(0.0, min(1.0, base + adj))
            coherence = float(val)
            self._last_coherence_info = {
                "status": "estimated",
                "source": "session_metrics",
                "value": coherence,
            }
            return coherence
        except Exception as exc:
            diagnostic = self._record_coherence_failure(
                "coherence_metric_estimate_failed", exc
            )
            self._last_coherence_info = {
                "status": "degraded",
                "source": "session_metrics",
                "fallback": 0.8,
                "error": diagnostic,
            }
            return 0.8

    async def learn_from_feedback(self, interaction_id: str, feedback: Dict[str, Any]):
        """Learn from user feedback"""
        normalized_interaction_id = self._normalize_interaction_id(interaction_id)
        sanitized_feedback = self._sanitize_feedback_payload(feedback)
        rating = self._normalize_feedback_rating(sanitized_feedback.get("rating", 0))
        sanitized_feedback["rating"] = rating

        try:
            await self.memory_system.store_learning(
                learning_content={
                    "interaction_id": normalized_interaction_id,
                    "feedback": sanitized_feedback,
                    "feedback_type": "user_rating",
                },
                learning_context={
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as exc:
            diagnostic = _safe_exception_diagnostic(exc, "feedback_store_failed")
            logger.warning(
                "Engine feedback storage failed trace_id=%s",
                diagnostic["trace_id"],
            )
            return {
                "status": "error",
                "error": diagnostic,
            }

        # Update improvement system
        improvement_status: Dict[str, Any] = {"status": "recorded"}
        try:
            self.improvement_engine.record_performance_metric(
                "user_satisfaction", rating, "rating"
            )
        except Exception as exc:
            diagnostic = _safe_exception_diagnostic(exc, "feedback_metric_failed")
            logger.warning(
                "Engine feedback metric recording failed trace_id=%s",
                diagnostic["trace_id"],
            )
            improvement_status = {
                "status": "degraded",
                "error": diagnostic,
            }

        return {
            "status": "recorded",
            "interaction_id": normalized_interaction_id,
            "rating": rating,
            "improvement": improvement_status,
        }

    # --------- AI Safety and RAG helpers ---------
    def _sanitize_input(self, text: str) -> str:
        """Best-effort prompt-injection hardening (lightweight)."""
        try:
            sanitized = str(text)
            matched = False
            for phrase in PROMPT_INJECTION_PHRASES:
                sanitized, replacements = re.subn(
                    re.escape(phrase),
                    "[redacted]",
                    sanitized,
                    flags=re.IGNORECASE,
                )
                matched = matched or replacements > 0
            if matched:
                self.session_metrics["safety_filters_triggered"] += 1
                return sanitized
        except Exception:
            pass
        return text

    def _apply_output_filters(self, text: str) -> str:
        """Apply simple output policy filters before returning to user."""
        try:
            out = str(text)
            patterns = (
                (r"(?i)\b(api[_-]?key)\s*=\s*([^\s,;]+)", r"\1=[redacted]"),
                (r"(?i)\b(password)\s*=\s*([^\s,;]+)", r"\1=[redacted]"),
                (r"(?i)\b(token)\s*=\s*([^\s,;]+)", r"\1=[redacted]"),
                (r"(?i)\b(secret)\s*=\s*([^\s,;]+)", r"\1=[redacted]"),
            )
            for pattern, replacement in patterns:
                out = re.sub(pattern, replacement, out)
            return out
        except Exception:
            return text

    def _validate_message_input(self, message: Any) -> str:
        if not isinstance(message, str):
            raise ValueError("message must be text")
        if len(message) > MAX_MESSAGE_CHARS:
            raise ValueError("message exceeds maximum length")
        return message

    def _normalize_user_id(self, user_id: Any) -> str:
        if not isinstance(user_id, str):
            raise ValueError("user_id must be text")
        raw = user_id.strip() or "default"
        if len(raw) > MAX_USER_ID_CHARS:
            return f"user_{_short_trace_id('user_id', raw)}"
        if not re.fullmatch(r"[A-Za-z0-9_.@-]+", raw):
            return f"user_{_short_trace_id('user_id', raw)}"
        return raw

    def _sanitize_persisted_context(self, context: Any) -> Dict[str, Any]:
        if not isinstance(context, dict):
            return {}

        sanitized: Dict[str, Any] = {}
        for key, value in context.items():
            if len(sanitized) >= MAX_CONTEXT_KEYS:
                break
            key_text = str(key).strip()
            if not key_text or key_text.startswith("_"):
                continue
            key_text = key_text[:MAX_CONTEXT_VALUE_CHARS]
            sanitized[key_text] = self._sanitize_context_value(value)
        return sanitized

    def _sanitize_context_value(self, value: Any) -> Any:
        if value is None or isinstance(value, bool | int | float):
            return value
        if isinstance(value, str):
            return self._apply_output_filters(value[:MAX_CONTEXT_VALUE_CHARS])
        if isinstance(value, list | tuple):
            return [
                self._sanitize_context_value(item)
                for item in list(value)[:MAX_CONTEXT_LIST_ITEMS]
            ]
        if isinstance(value, dict):
            nested: Dict[str, Any] = {}
            for key, item in value.items():
                if len(nested) >= MAX_CONTEXT_LIST_ITEMS:
                    break
                key_text = str(key).strip()
                if not key_text or key_text.startswith("_"):
                    continue
                nested[key_text[:MAX_CONTEXT_VALUE_CHARS]] = self._sanitize_context_value(item)
            return nested
        if hasattr(value, "isoformat"):
            with suppress(Exception):
                return value.isoformat()
        return {"type": type(value).__name__}

    def _sanitize_evidence_content(self, content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, dict | list | tuple):
            with suppress(TypeError, ValueError):
                content = json.dumps(content, sort_keys=True)
        filtered = self._apply_output_filters(str(content))
        return filtered[:MAX_EVIDENCE_CONTENT_CHARS]

    def _sanitize_reasoning_history_content(self, content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, dict | list | tuple):
            with suppress(TypeError, ValueError):
                content = json.dumps(content, sort_keys=True)
        filtered = self._apply_output_filters(str(content))
        return filtered[:MAX_REASONING_HISTORY_CHARS]

    def _sanitize_reasoning_text(self, content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, dict | list | tuple):
            with suppress(TypeError, ValueError):
                content = json.dumps(content, sort_keys=True)
        filtered = self._apply_output_filters(str(content))
        return filtered[:MAX_REASONING_TEXT_CHARS]

    def _normalize_intelligence_provider(self, provider_name: Any) -> str:
        provider = str(provider_name or "").strip().lower()
        if not provider:
            return ""
        if provider not in ALLOWED_INTELLIGENCE_PROVIDERS:
            raise ValueError("intelligence provider is not allowed")
        return provider

    def _llm_timeout_seconds(self) -> float:
        raw_timeout = os.getenv("AETHERRA_LLM_TIMEOUT_SEC", "").strip()
        if not raw_timeout:
            return DEFAULT_LLM_TIMEOUT_SEC
        try:
            timeout = float(raw_timeout)
        except ValueError:
            return DEFAULT_LLM_TIMEOUT_SEC
        return max(1.0, min(MAX_LLM_TIMEOUT_SEC, timeout))

    def _build_llm_prompt(
        self,
        safe_message: str,
        evidence: List[Dict[str, Any]],
        *,
        snippet_chars: int = MAX_LLM_EVIDENCE_SNIPPET_CHARS,
    ) -> str:
        evidence_snippets = []
        for ev in (evidence or [])[:3]:
            if not isinstance(ev, dict):
                continue
            content = ev.get("content")
            if content:
                evidence_snippets.append(
                    self._apply_output_filters(str(content))[:snippet_chars]
                )
        evidence_text = "\n\n".join(f"- {snippet}" for snippet in evidence_snippets)
        prompt = (
            f"User: {safe_message}\n\n"
            + (f"Context:\n{evidence_text}\n\n" if evidence_text else "")
            + "Be concise and helpful."
        )
        return prompt[:MAX_LLM_PROMPT_CHARS]

    def _record_recall_failure(self, code: str, exc: Exception) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine memory recall failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_llm_failure(
        self,
        code: str,
        exc: Exception,
        *,
        provider: str | None = None,
    ) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        model_info = None
        with suppress(Exception):
            model_info = self._get_public_llm_model_info()
        self._last_llm_info = {
            "event": "error",
            "model": model_info,
            "error": diagnostic,
        }
        if provider:
            self._last_llm_info["provider"] = self._sanitize_context_value(provider)
        logger.warning(
            "Engine LLM path failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_session_start_failure(self, code: str, exc: Exception) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine session start persistence failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_response_persistence_failure(
        self, code: str, exc: Exception
    ) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine response persistence failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_input_persistence_failure(
        self, code: str, exc: Exception
    ) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine input persistence failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_storm_canary_failure(self, code: str, exc: Exception) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine STORM canary failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_persistent_memory_failure(
        self, code: str, exc: Exception
    ) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine persistent memory setup failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_task_execution_failure(
        self, code: str, exc: Exception
    ) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine task execution failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_scratchpad_failure(self, code: str, exc: Exception) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine scratchpad update failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_coherence_failure(self, code: str, exc: Exception) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine coherence estimation failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_reflection_failure(self, code: str, exc: Exception) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine reflection failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _record_optional_processing_failure(
        self, code: str, exc: Exception
    ) -> Dict[str, str]:
        diagnostic = _safe_exception_diagnostic(exc, code)
        logger.warning(
            "Engine optional processing failed code=%s type=%s trace_id=%s",
            diagnostic["code"],
            diagnostic["type"],
            diagnostic["trace_id"],
        )
        return diagnostic

    def _public_conversation_context(self) -> Dict[str, Any]:
        return self._sanitize_persisted_context(self.conversation_context)

    def _conversation_duration_minutes(self) -> float:
        start_time = self.conversation_context.get("start_time")
        if hasattr(start_time, "timestamp"):
            with suppress(Exception):
                return max(0.0, (datetime.now() - start_time).total_seconds() / 60)
        return 0.0

    def _normalize_interaction_id(self, interaction_id: Any) -> str:
        if not isinstance(interaction_id, str):
            raise ValueError("interaction_id must be text")
        raw = interaction_id.strip()
        if not raw:
            raise ValueError("interaction_id is required")
        if len(raw) > MAX_INTERACTION_ID_CHARS:
            return f"interaction_{_short_trace_id('interaction_id', raw)}"
        if not re.fullmatch(r"[A-Za-z0-9_.:@-]+", raw):
            return f"interaction_{_short_trace_id('interaction_id', raw)}"
        return raw

    def _normalize_feedback_rating(self, rating: Any) -> int:
        try:
            value = int(float(rating))
        except (TypeError, ValueError):
            value = 0
        return max(1, min(5, value))

    def _sanitize_feedback_payload(self, feedback: Any) -> Dict[str, Any]:
        if not isinstance(feedback, dict):
            raise ValueError("feedback must be a dictionary")

        sanitized: Dict[str, Any] = {}
        for key, value in feedback.items():
            if len(sanitized) >= MAX_FEEDBACK_KEYS:
                break
            key_text = str(key).strip()
            if not key_text or key_text.startswith("_"):
                continue
            key_text = key_text[:MAX_CONTEXT_VALUE_CHARS]
            sanitized[key_text] = self._sanitize_feedback_value(value)
        return sanitized

    def _sanitize_feedback_value(self, value: Any) -> Any:
        if value is None or isinstance(value, bool | int | float):
            return value
        if isinstance(value, str):
            return self._apply_output_filters(value)[:MAX_FEEDBACK_TEXT_CHARS]
        if isinstance(value, list | tuple):
            return [
                self._sanitize_feedback_value(item)
                for item in list(value)[:MAX_CONTEXT_LIST_ITEMS]
            ]
        if isinstance(value, dict):
            nested: Dict[str, Any] = {}
            for key, item in value.items():
                if len(nested) >= MAX_CONTEXT_LIST_ITEMS:
                    break
                key_text = str(key).strip()
                if not key_text or key_text.startswith("_"):
                    continue
                nested[key_text[:MAX_CONTEXT_VALUE_CHARS]] = self._sanitize_feedback_value(item)
            return nested
        if hasattr(value, "isoformat"):
            with suppress(Exception):
                return value.isoformat()
        return {"type": type(value).__name__}

    def _get_public_llm_model_info(self) -> Any:
        if not (self._llm_manager and self._llm_selected):
            return None
        if not hasattr(self._llm_manager, "get_current_model_info"):
            return None
        info = self._llm_manager.get_current_model_info()
        return self._sanitize_context_value(info)

    def _build_validation_error_response(self, exc: ValueError) -> Dict[str, Any]:
        """Return a stable validation error without echoing invalid input."""
        trace_id = _short_trace_id(
            ENGINE_VALIDATION_ERROR_CODE,
            type(exc).__name__,
            self.session_id,
            time.time_ns(),
        )
        return {
            "response": ENGINE_VALIDATION_ERROR_MESSAGE,
            "error": {
                "code": ENGINE_VALIDATION_ERROR_CODE,
                "reason": str(exc),
                "trace_id": trace_id,
            },
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
        }

    def _build_processing_error_response(self, exc: Exception) -> Dict[str, Any]:
        """Return a stable user-safe processing error without leaking internals."""
        trace_id = _short_trace_id(
            type(exc).__name__,
            self.session_id,
            time.time_ns(),
        )
        logger.exception("Aetherra Engine message processing failed trace_id=%s", trace_id)
        return {
            "response": ENGINE_PROCESSING_ERROR_MESSAGE,
            "error": {
                "code": ENGINE_PROCESSING_ERROR_CODE,
                "trace_id": trace_id,
            },
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
        }

    def add_scratch(self, entry: Dict[str, Any]) -> bool:
        """Append to ephemeral scratchpad (not persisted)."""
        try:
            if not isinstance(entry, dict):
                raise ValueError("scratchpad entry must be a dictionary")
            sanitized_entry: Dict[str, Any] = {}
            for key, value in entry.items():
                if len(sanitized_entry) >= MAX_SCRATCHPAD_ENTRY_KEYS:
                    break
                key_text = str(key).strip()
                if not key_text or key_text.startswith("_"):
                    continue
                sanitized_entry[key_text[:MAX_CONTEXT_VALUE_CHARS]] = (
                    self._sanitize_context_value(value)
                )
            sanitized_entry["ts"] = datetime.now().isoformat()
            self._scratchpad.append(sanitized_entry)
            if len(self._scratchpad) > MAX_SCRATCHPAD_ENTRIES:
                self._scratchpad = self._scratchpad[-MAX_SCRATCHPAD_ENTRIES:]
            self._last_scratchpad_info = {
                "status": "recorded",
                "entries": len(self._scratchpad),
            }
            return True
        except Exception as exc:
            diagnostic = self._record_scratchpad_failure(
                "scratchpad_update_failed", exc
            )
            self._last_scratchpad_info = {
                "status": "degraded",
                "error": diagnostic,
            }
            return False

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
        bucket_val = _stable_percent_bucket(key)
        with suppress(Exception):
            self._msg_counter += 1
        return "quantum" if bucket_val < max(0, min(100, pct)) else "classical"

    def _record_ab_metric(self, bucket: str, dt_ms: float) -> Dict[str, Any]:
        try:
            bucket = "quantum" if bucket == "quantum" else "classical"
            # totals
            self.session_metrics["ab_recall_total"] = (
                int(self.session_metrics.get("ab_recall_total", 0)) + 1
            )
            k_total = f"ab_recall_{bucket}_total"
            self.session_metrics[k_total] = int(self.session_metrics.get(k_total, 0)) + 1
            # latency aggregates
            ksum = f"ab_recall_latency_ms_sum_{bucket}"
            kcnt = f"ab_recall_latency_ms_count_{bucket}"
            self.session_metrics[ksum] = float(self.session_metrics.get(ksum, 0.0)) + float(dt_ms)
            self.session_metrics[kcnt] = int(self.session_metrics.get(kcnt, 0)) + 1
            return {"status": "recorded", "bucket": bucket}
        except Exception as exc:
            diagnostic = self._record_recall_failure("ab_metric_record_failed", exc)
            return {"status": "degraded", "error": diagnostic}

    async def _ensure_persistent_memory(self) -> bool:
        """Ensure the persistent memory system is available. Returns True if ready."""
        try:
            if self._persistent_memory is not None:
                self._last_persistent_memory_info = {"status": "ready"}
                return True
            if self._ab_mode() not in ("quantum", "abp"):
                self._last_persistent_memory_info = {"status": "disabled"}
                return False
            # Aetherra imports
            from aetherra_persistent_memory import (
                get_persistent_memory_system as _get_pmem,
            )

            self._persistent_memory = await _get_pmem()
            if self._persistent_memory is not None:
                self._last_persistent_memory_info = {"status": "ready"}
                return True
            self._last_persistent_memory_info = {"status": "unavailable"}
            return False
        except Exception as exc:
            diagnostic = self._record_persistent_memory_failure(
                "persistent_memory_setup_failed", exc
            )
            self._last_persistent_memory_info = {
                "status": "degraded",
                "error": diagnostic,
            }
            return False

    async def reflect_on_day(self) -> Dict[str, Any]:
        """Night-cycle hook: run a small evaluation harness and generate insights."""
        try:
            self._last_reflection_info = {
                "status": "running",
                "memory": {"status": "pending"},
                "metrics": {"status": "pending"},
            }
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
                self._last_reflection_info["memory"] = {"status": "stored"}
            except Exception as exc:
                diagnostic = self._record_reflection_failure(
                    "reflection_memory_store_failed", exc
                )
                self._last_reflection_info["memory"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }
            # Nudge self-improvement engine
            try:
                self.improvement_engine.record_performance_metric(
                    "rag_hit_rate", eval_summary["rag_hit_rate"], "ratio"
                )
                self._last_reflection_info["metrics"] = {"status": "recorded"}
            except Exception as exc:
                diagnostic = self._record_reflection_failure(
                    "reflection_metric_record_failed", exc
                )
                self._last_reflection_info["metrics"] = {
                    "status": "degraded",
                    "error": diagnostic,
                }
            self._last_reflection_info["status"] = "ok"
            return {"status": "ok", "evaluation": eval_summary}
        except Exception as exc:
            diagnostic = self._record_reflection_failure("reflection_failed", exc)
            self._last_reflection_info = {
                "status": "error",
                "error": diagnostic,
            }
            return {"status": "error", "error": diagnostic}

    # --------- Engine metrics helpers ---------
    def _observe_message_latency(self, ms: float):
        try:
            if ms <= 0:
                return
            with self._metrics_lock:
                self._msg_latency_sum_ms += ms
                self._msg_latency_count += 1
                for b in (50, 100, 250, 500, 1000, 2000, 5000):
                    if ms <= b:
                        self._msg_latency_hist[b] = int(self._msg_latency_hist.get(b, 0)) + 1
                        break
                else:
                    self._msg_latency_hist[5000] = int(self._msg_latency_hist.get(5000, 0)) + 1
        except Exception:
            pass

    def _observe_recall_latency(self, ms: float, success: bool):
        try:
            if ms <= 0:
                return
            with self._metrics_lock:
                self._recall_latency_sum_ms += ms
                self._recall_latency_count += 1
                for b in (10, 20, 50, 100, 200, 500, 1000):
                    if ms <= b:
                        self._recall_latency_hist[b] = int(self._recall_latency_hist.get(b, 0)) + 1
                        break
                else:
                    self._recall_latency_hist[1000] = (
                        int(self._recall_latency_hist.get(1000, 0)) + 1
                    )
                if success:
                    self._recall_success_total += 1
                else:
                    self._recall_failure_total += 1
        except Exception:
            pass

    def get_engine_metrics_snapshot(self) -> Dict[str, Any]:
        """Return a snapshot of engine metrics for export."""
        try:
            with self._metrics_lock:
                return {
                    "message_latency_sum_ms": self._msg_latency_sum_ms,
                    "message_latency_count": self._msg_latency_count,
                    "message_latency_hist": dict(self._msg_latency_hist),
                    "recall_latency_sum_ms": self._recall_latency_sum_ms,
                    "recall_latency_count": self._recall_latency_count,
                    "recall_latency_hist": dict(self._recall_latency_hist),
                    "recall_success_total": self._recall_success_total,
                    "recall_failure_total": self._recall_failure_total,
                    "storm_canary_comparisons_total": self._storm_canary_comparisons,
                    "storm_canary_divergences_total": self._storm_canary_divergences,
                    "storm_canary_shadow_latency_sum_ms": self._storm_canary_shadow_latency_sum_ms,
                    "storm_canary_shadow_latency_count": self._storm_canary_shadow_latency_count,
                }
        except Exception:
            return {}

    # --------- Agent Evaluation Harness (lightweight) ---------
    async def run_agent_evaluation(self, plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        if isinstance(plan, dict) and isinstance(plan.get("timeout_sec"), int | float):
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
                diagnostic = _safe_exception_diagnostic(
                    e, "agent_evaluation_case_failed"
                )
                results.append(
                    {
                        "name": name,
                        "task_id": None,
                        "duration_sec": dt,
                        "ok": False,
                        "error": diagnostic,
                    }
                )

        # Summaries
        total = len(results)
        succ = sum(1 for r in results if r.get("ok"))
        fail = total - succ
        avg_dur = sum(float(r.get("duration_sec", 0) or 0) for r in results) / max(1, total)
        # Error clustering (very light): by error string or state
        clusters: Dict[str, int] = {}
        for r in results:
            key = None
            if not r.get("ok"):
                error = r.get("error")
                if isinstance(error, dict):
                    key = str(error.get("code") or "error")
                else:
                    key = str(error or (r.get("status") or {}).get("state") or "error")
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
        default: policy-driven. If AETHERRA_LLM_AUTO_POLICY=cloud-first, default is
        "openai,anthropic,gemini,ollama,llamacpp"; otherwise default is
        "ollama,openai,anthropic,gemini,llamacpp". A specific model can be
        forced via AETHERRA_LLM_MODEL.
        """
        if self._llm_selected:
            return True
        mgr = self._llm_manager
        if mgr is None:
            return False
        try:
            # Honor explicit provider order if provided
            preferred_env = os.environ.get("AETHERRA_LLM_PROVIDER_PREF", "").strip()
            # Policy can flip the default order without requiring an explicit list
            auto_policy = (os.environ.get("AETHERRA_LLM_AUTO_POLICY", "") or "").strip().lower()
            if preferred_env:
                preferred = preferred_env
            else:
                if auto_policy == "cloud-first":
                    preferred = "openai,anthropic,gemini,ollama,llamacpp"
                else:
                    # default local-first for privacy/residency
                    preferred = "ollama,openai,anthropic,gemini,llamacpp"
            order = [p.strip().lower() for p in preferred.split(",") if p.strip()]
            force_model = os.environ.get("AETHERRA_LLM_MODEL", "").strip()

            models = mgr.list_available_models()  # name -> info
            selected = None
            # If a model is forced and exists, use it
            if force_model and force_model in models and mgr.set_model(force_model):
                self._llm_selected = True
                logger.info(f"[LLM] selected forced model: {force_model}")
                return True
            # Otherwise, pick by provider order, preferring local where possible
            for prov in order:
                for name, info in models.items():
                    try:
                        if str(info.get("provider", "")).lower() == prov and mgr.set_model(name):
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
        except Exception as exc:
            self._record_llm_failure("llm_selection_failed", exc)
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
