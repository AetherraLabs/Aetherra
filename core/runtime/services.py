# core/runtime/services.py
"""
NeuroCode Runtime Services
==========================

This module provides runtime services coordination and management
for the NeuroCode execution environment.
"""

from typing import Any, Dict, Optional
import logging

from .context import RuntimeEnvironment, ExecutionContext, ExecutionMode
from .executor import CodeExecutor, ExecutionResult, ExecutionStatus
from ..syntax import parse_neurocode


class RuntimeServices:
    """Central coordinator for NeuroCode runtime services"""

    def __init__(self):
        self.environment = RuntimeEnvironment()
        self.logger = logging.getLogger('neurocode.runtime')
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up runtime logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_memory_service(self, memory_service: Any) -> None:
        """Register the memory service"""
        self.environment.register_service('memory', memory_service)
        self.logger.info("Memory service registered")

    def register_assistant_service(self, assistant_service: Any) -> None:
        """Register the assistant service"""
        self.environment.register_service('assistant', assistant_service)
        self.logger.info("Assistant service registered")

    def register_plugin_manager(self, plugin_manager: Any) -> None:
        """Register the plugin manager"""
        self.environment.register_service('plugins', plugin_manager)
        self.logger.info("Plugin manager registered")

    def register_agent_service(self, agent_service: Any) -> None:
        """Register the agent service"""
        self.environment.register_service('agent', agent_service)
        self.logger.info("Agent service registered")

    def create_execution_context(self,
                                mode: ExecutionMode = ExecutionMode.INTERACTIVE,
                                debug_mode: bool = False) -> ExecutionContext:
        """Create a new execution context"""
        context = self.environment.create_context(mode=mode, debug_mode=debug_mode)
        self.logger.info(f"Created execution context: {context.session_id}")
        return context

    def get_context(self, session_id: str) -> Optional[ExecutionContext]:
        """Get an execution context by session ID"""
        return self.environment.get_context(session_id)

    def set_active_context(self, session_id: str) -> bool:
        """Set the active execution context"""
        success = self.environment.set_active_context(session_id)
        if success:
            self.logger.info(f"Set active context: {session_id}")
        else:
            self.logger.warning(f"Failed to set active context: {session_id}")
        return success

    def execute_code(self, code: str, context: Optional[ExecutionContext] = None) -> ExecutionResult:
        """Execute NeuroCode and return results"""
        # Use provided context or active context
        if context is None:
            context = self.environment.get_active_context()
            if context is None:
                context = self.create_execution_context()

        try:
            # Parse the code
            self.logger.debug(f"Parsing code in context {context.session_id}")
            syntax_tree = parse_neurocode(code)

            # Execute the syntax tree
            self.logger.debug(f"Executing syntax tree in context {context.session_id}")
            executor = CodeExecutor(context)
            result = executor.execute(syntax_tree)

            # Log execution results
            if result.is_success():
                self.logger.info(f"Execution completed successfully in {result.execution_time:.3f}s")
            else:
                self.logger.error(f"Execution failed: {result.error}")

            return result

        except Exception as e:
            self.logger.error(f"Execution error: {e}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=str(e),
                execution_time=0.0
            )

    def execute_file(self, file_path: str, context: Optional[ExecutionContext] = None) -> ExecutionResult:
        """Execute a NeuroCode file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            self.logger.info(f"Executing file: {file_path}")
            return self.execute_code(code, context)

        except FileNotFoundError:
            error = f"File not found: {file_path}"
            self.logger.error(error)
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=error
            )
        except Exception as e:
            error = f"Error reading file {file_path}: {e}"
            self.logger.error(error)
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=error
            )

    def get_runtime_status(self) -> Dict[str, Any]:
        """Get comprehensive runtime status"""
        env_status = self.environment.get_status()
        active_context = self.environment.get_active_context()

        status = {
            'environment': env_status,
            'active_context': active_context.get_status() if active_context else None,
            'services': {
                'memory': self.environment.get_service('memory') is not None,
                'assistant': self.environment.get_service('assistant') is not None,
                'plugins': self.environment.get_service('plugins') is not None,
                'agent': self.environment.get_service('agent') is not None
            }
        }

        return status

    def configure_runtime(self, **kwargs) -> None:
        """Configure runtime settings"""
        self.environment.configure(**kwargs)
        self.logger.info(f"Runtime configured: {kwargs}")

    def cleanup_contexts(self) -> int:
        """Clean up old execution contexts and return count removed"""
        initial_count = len(self.environment.contexts)
        self.environment._cleanup_old_contexts()
        removed_count = initial_count - len(self.environment.contexts)

        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old execution contexts")

        return removed_count

    def reset_runtime(self) -> None:
        """Reset the entire runtime environment"""
        self.environment = RuntimeEnvironment()
        self.logger.info("Runtime environment reset")

    def get_context_list(self) -> list:
        """Get a list of all execution contexts"""
        contexts = []
        for session_id, context in self.environment.contexts.items():
            contexts.append({
                'session_id': session_id,
                'mode': context.mode.value,
                'state': context.state.value,
                'variables_count': len(context.variables),
                'functions_count': len(context.functions),
                'execution_time': context.metrics.duration,
                'nodes_executed': context.metrics.nodes_executed
            })
        return contexts

    def export_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export a context for serialization/backup"""
        context = self.environment.get_context(session_id)
        if not context:
            return None

        return {
            'session_id': context.session_id,
            'mode': context.mode.value,
            'variables': context.variables,
            'functions': context.functions,
            'metrics': {
                'start_time': context.metrics.start_time,
                'nodes_executed': context.metrics.nodes_executed,
                'memory_operations': context.metrics.memory_operations,
                'assistant_calls': context.metrics.assistant_calls,
                'agent_operations': context.metrics.agent_operations,
                'plugin_calls': context.metrics.plugin_calls,
                'errors': context.metrics.errors.copy(),
                'warnings': context.metrics.warnings.copy()
            }
        }
