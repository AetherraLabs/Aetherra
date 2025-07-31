# core/runtime/context.py
"""
AetherraCode Runtime Context and Environment
=========================================

This module defines the execution context and runtime environment
for AetherraCode programs.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionMode(Enum):
    """Execution modes for AetherraCode runtime"""

    INTERACTIVE = "interactive"
    BATCH = "batch"
    AGENT = "agent"
    DEBUG = "debug"


class ExecutionState(Enum):
    """Current state of execution"""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class ExecutionMetrics:
    """Metrics for execution tracking"""

    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    nodes_executed: int = 0
    memory_operations: int = 0
    assistant_calls: int = 0
    agent_operations: int = 0
    plugin_calls: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Calculate execution duration"""
        end = self.end_time or time.time()
        return end - self.start_time

    def mark_completed(self) -> None:
        """Mark execution as completed"""
        self.end_time = time.time()


@dataclass
class ExecutionContext:
    """Runtime execution context for AetherraCode"""

    # Core identification
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Runtime state
    mode: ExecutionMode = ExecutionMode.INTERACTIVE
    state: ExecutionState = ExecutionState.IDLE

    # Variables and scope
    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Any] = field(default_factory=dict)

    # Runtime services
    memory_service: Optional[Any] = None
    assistant_service: Optional[Any] = None
    plugin_manager: Optional[Any] = None
    agent_service: Optional[Any] = None

    # Execution tracking
    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)
    call_stack: List[str] = field(default_factory=list)

    # Configuration
    max_depth: int = 100
    timeout: Optional[float] = None
    debug_mode: bool = False

    def __post_init__(self):
        """Initialize context after creation"""
        if self.debug_mode:
            self.mode = ExecutionMode.DEBUG

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable value safely"""
        return self.variables.get(name, default)

    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable value"""
        self.variables[name] = value

    def has_variable(self, name: str) -> bool:
        """Check if a variable exists"""
        return name in self.variables

    def get_function(self, name: str) -> Optional[Any]:
        """Get a function definition"""
        return self.functions.get(name)

    def register_function(self, name: str, func: Any) -> None:
        """Register a function"""
        self.functions[name] = func

    def push_call(self, function_name: str) -> None:
        """Push a function call onto the stack"""
        self.call_stack.append(function_name)
        if len(self.call_stack) > self.max_depth:
            raise RuntimeError(f"Maximum call depth ({self.max_depth}) exceeded")

    def pop_call(self) -> Optional[str]:
        """Pop a function call from the stack"""
        return self.call_stack.pop() if self.call_stack else None

    def current_call(self) -> Optional[str]:
        """Get the current function call"""
        return self.call_stack[-1] if self.call_stack else None

    def call_depth(self) -> int:
        """Get current call stack depth"""
        return len(self.call_stack)

    def reset_metrics(self) -> None:
        """Reset execution metrics"""
        self.metrics = ExecutionMetrics()

    def add_error(self, error: str) -> None:
        """Add an error to metrics"""
        self.metrics.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning to metrics"""
        self.metrics.warnings.append(warning)

    def increment_counter(self, counter_name: str) -> None:
        """Increment a metric counter"""
        if hasattr(self.metrics, counter_name):
            current_value = getattr(self.metrics, counter_name)
            setattr(self.metrics, counter_name, current_value + 1)

    def get_status(self) -> Dict[str, Any]:
        """Get current context status"""
        return {
            "session_id": self.session_id,
            "execution_id": self.execution_id,
            "mode": self.mode.value,
            "state": self.state.value,
            "variables_count": len(self.variables),
            "functions_count": len(self.functions),
            "call_depth": self.call_depth(),
            "metrics": {
                "duration": self.metrics.duration,
                "nodes_executed": self.metrics.nodes_executed,
                "memory_operations": self.metrics.memory_operations,
                "assistant_calls": self.metrics.assistant_calls,
                "agent_operations": self.metrics.agent_operations,
                "plugin_calls": self.metrics.plugin_calls,
                "errors": len(self.metrics.errors),
                "warnings": len(self.metrics.warnings),
            },
        }


class RuntimeEnvironment:
    """Global runtime environment for AetherraCode"""

    def __init__(self):
        self.contexts: Dict[str, ExecutionContext] = {}
        self.active_context: Optional[str] = None
        self.global_services: Dict[str, Any] = {}
        self.configuration: Dict[str, Any] = {
            "default_timeout": 300.0,  # 5 minutes
            "max_contexts": 10,
            "debug_enabled": False,
            "memory_limit_mb": 512,
        }

    def create_context(
        self, mode: ExecutionMode = ExecutionMode.INTERACTIVE, debug_mode: bool = False
    ) -> ExecutionContext:
        """Create a new execution context"""
        context = ExecutionContext(mode=mode, debug_mode=debug_mode)

        # Link global services
        context.memory_service = self.global_services.get("memory")
        context.assistant_service = self.global_services.get("assistant")
        context.plugin_manager = self.global_services.get("plugins")
        context.agent_service = self.global_services.get("agent")

        # Apply global configuration
        context.timeout = self.configuration.get("default_timeout")

        # Store context
        self.contexts[context.session_id] = context

        # Clean up old contexts if limit exceeded
        if len(self.contexts) > self.configuration["max_contexts"]:
            self._cleanup_old_contexts()

        return context

    def get_context(self, session_id: str) -> Optional[ExecutionContext]:
        """Get an execution context by session ID"""
        return self.contexts.get(session_id)

    def set_active_context(self, session_id: str) -> bool:
        """Set the active execution context"""
        if session_id in self.contexts:
            self.active_context = session_id
            return True
        return False

    def get_active_context(self) -> Optional[ExecutionContext]:
        """Get the currently active execution context"""
        if self.active_context:
            return self.contexts.get(self.active_context)
        return None

    def register_service(self, name: str, service: Any) -> None:
        """Register a global service"""
        self.global_services[name] = service

    def get_service(self, name: str) -> Optional[Any]:
        """Get a global service"""
        return self.global_services.get(name)

    def configure(self, **kwargs) -> None:
        """Update runtime configuration"""
        self.configuration.update(kwargs)

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.configuration.copy()

    def _cleanup_old_contexts(self) -> None:
        """Clean up old execution contexts"""
        # Sort by start time and remove oldest
        sorted_contexts = sorted(self.contexts.items(), key=lambda x: x[1].metrics.start_time)

        while len(sorted_contexts) > self.configuration["max_contexts"]:
            session_id, _ = sorted_contexts.pop(0)
            del self.contexts[session_id]

            # Update active context if it was removed
            if self.active_context == session_id:
                self.active_context = None

    def get_status(self) -> Dict[str, Any]:
        """Get runtime environment status"""
        return {
            "total_contexts": len(self.contexts),
            "active_context": self.active_context,
            "services": list(self.global_services.keys()),
            "configuration": self.configuration,
            "memory_usage": self._estimate_memory_usage(),
        }

    def _estimate_memory_usage(self) -> Dict[str, Any]:
        """Estimate memory usage of the runtime environment"""
        import sys

        total_vars = sum(len(ctx.variables) for ctx in self.contexts.values())
        total_functions = sum(len(ctx.functions) for ctx in self.contexts.values())

        return {
            "contexts": len(self.contexts),
            "total_variables": total_vars,
            "total_functions": total_functions,
            "estimated_mb": (
                sys.getsizeof(self.contexts)
                + sum(sys.getsizeof(ctx) for ctx in self.contexts.values())
            )
            / 1024
            / 1024,
        }
