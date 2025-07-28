# core/runtime/executor.py
"""
AetherraCode Code Executor
=======================

This module provides the main execution engine for AetherraCode programs,
handling syntax tree execution and runtime coordination.
"""

import time
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

from ..syntax import SyntaxNode, SyntaxTreeVisitor
from .context import ExecutionContext, ExecutionState


class ExecutionStatus(Enum):
    """Status of code execution"""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """Result of code execution"""

    status: ExecutionStatus
    value: Any = None
    error: Optional[str] = None
    output: List[str] = None
    execution_time: float = 0.0
    nodes_executed: int = 0

    def __post_init__(self):
        if self.output is None:
            self.output = []

    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self.status == ExecutionStatus.SUCCESS

    def add_output(self, message: str) -> None:
        """Add output message"""
        self.output.append(message)

    def get_output_text(self) -> str:
        """Get combined output as text"""
        return "\n".join(self.output)


class CodeExecutor(SyntaxTreeVisitor):
    """Main executor for AetherraCode syntax trees"""

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.start_time = 0.0
        self.nodes_executed = 0
        self.output_buffer = []

    def execute(self, tree: SyntaxNode) -> ExecutionResult:
        """Execute a AetherraCode syntax tree"""
        self.start_time = time.time()
        self.nodes_executed = 0
        self.output_buffer = []

        # Update context state
        self.context.state = ExecutionState.RUNNING
        self.context.reset_metrics()

        try:
            # Check for timeout
            if self.context.timeout and time.time() - self.start_time > self.context.timeout:
                return self._create_timeout_result()

            # Execute the tree
            result_value = self.visit(tree)

            # Mark completion
            execution_time = time.time() - self.start_time
            self.context.state = ExecutionState.COMPLETED
            self.context.metrics.mark_completed()

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                value=result_value,
                output=self.output_buffer.copy(),
                execution_time=execution_time,
                nodes_executed=self.nodes_executed,
            )

        except TimeoutError:
            return self._create_timeout_result()
        except Exception as e:
            return self._create_error_result(str(e))

    def _create_timeout_result(self) -> ExecutionResult:
        """Create a timeout execution result"""
        self.context.state = ExecutionState.ERROR
        execution_time = time.time() - self.start_time
        return ExecutionResult(
            status=ExecutionStatus.TIMEOUT,
            error="Execution timeout",
            output=self.output_buffer.copy(),
            execution_time=execution_time,
            nodes_executed=self.nodes_executed,
        )

    def _create_error_result(self, error_message: str) -> ExecutionResult:
        """Create an error execution result"""
        self.context.state = ExecutionState.ERROR
        self.context.add_error(error_message)
        execution_time = time.time() - self.start_time

        # Add traceback to output for debugging
        if self.context.debug_mode:
            self.output_buffer.append(f"ERROR: {error_message}")
            self.output_buffer.append(traceback.format_exc())

        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            error=error_message,
            output=self.output_buffer.copy(),
            execution_time=execution_time,
            nodes_executed=self.nodes_executed,
        )

    def visit(self, node: SyntaxNode) -> Any:
        """Override base visit to add execution tracking"""
        self.nodes_executed += 1
        self.context.metrics.nodes_executed += 1

        # Check timeout during execution
        if self.context.timeout and time.time() - self.start_time > self.context.timeout:
            raise TimeoutError("Execution timeout")

        return super().visit(node)

    def visit_program(self, node: SyntaxNode) -> List[Any]:
        """Execute a program node"""
        results = []
        for child in node.children or []:
            result = self.visit(child)
            if result is not None:
                results.append(result)
        return results

    def visit_goal(self, node: SyntaxNode) -> str:
        """Execute a goal node"""
        goal_text = node.value
        priority = node.get_metadata("priority", "medium")

        # Store goal in context
        if "goals" not in self.context.variables:
            self.context.variables["goals"] = []

        goal_data = {"text": goal_text, "priority": priority, "line": node.line_number}
        self.context.variables["goals"].append(goal_data)

        output = f"Goal set: {goal_text} (Priority: {priority})"
        self.output_buffer.append(output)
        return output

    def visit_memory(self, node: SyntaxNode) -> str:
        """Execute a memory operation node"""
        self.context.increment_counter("memory_operations")

        action = node.value.get("action")
        output = f"Memory operation: {action}"

        if self.context.memory_service:
            # Delegate to memory service
            try:
                if action == "remember":
                    content = node.value.get("content")
                    tag = node.value.get("tag", "general")
                    result = self.context.memory_service.remember(content, tag)
                    output = f"Remembered: '{content}' as '{tag}'"

                elif action == "recall":
                    tag = node.value.get("tag")
                    result = self.context.memory_service.recall(tag)
                    output = f"Recalled: {result}"

                elif action == "search":
                    keyword = node.value.get("keyword")
                    results = self.context.memory_service.search(keyword)
                    output = f"Search results for '{keyword}': {len(results)} items"

            except Exception as e:
                output = f"Memory operation failed: {e}"
                self.context.add_warning(f"Memory operation error: {e}")
        else:
            output = f"Memory service not available: {action}"
            self.context.add_warning("Memory service not configured")

        self.output_buffer.append(output)
        return output

    def visit_assistant(self, node: SyntaxNode) -> str:
        """Execute an assistant call node"""
        self.context.increment_counter("assistant_calls")

        prompt = node.value
        output = f"Assistant call: {prompt}"

        if self.context.assistant_service:
            try:
                response = self.context.assistant_service.process(prompt)
                output = f"Assistant: {response}"
            except Exception as e:
                output = f"Assistant call failed: {e}"
                self.context.add_warning(f"Assistant error: {e}")
        else:
            output = f"Assistant service not available: {prompt}"
            self.context.add_warning("Assistant service not configured")

        self.output_buffer.append(output)
        return output

    def visit_plugin(self, node: SyntaxNode) -> str:
        """Execute a plugin call node"""
        self.context.increment_counter("plugin_calls")

        plugin_name = node.value.get("name")
        plugin_args = node.value.get("args")
        output = f"Plugin call: {plugin_name} {plugin_args}"

        if self.context.plugin_manager:
            try:
                result = self.context.plugin_manager.execute(plugin_name, plugin_args)
                output = f"Plugin {plugin_name}: {result}"
            except Exception as e:
                output = f"Plugin call failed: {e}"
                self.context.add_warning(f"Plugin error: {e}")
        else:
            output = f"Plugin manager not available: {plugin_name}"
            self.context.add_warning("Plugin manager not configured")

        self.output_buffer.append(output)
        return output

    def visit_function_def(self, node: SyntaxNode) -> str:
        """Execute a function definition node"""
        func_name = node.value.get("name")
        params = node.value.get("params", [])

        # Store function in context
        func_data = {
            "name": func_name,
            "params": params,
            "body": node.children or [],
            "line": node.line_number,
        }
        self.context.register_function(func_name, func_data)

        output = f"Function defined: {func_name}({', '.join(params)})"
        self.output_buffer.append(output)
        return output

    def visit_function_call(self, node: SyntaxNode) -> Any:
        """Execute a function call node"""
        func_name = node.value.get("name")
        args = node.value.get("args", [])

        # Get function definition
        func_def = self.context.get_function(func_name)
        if not func_def:
            error = f"Undefined function: {func_name}"
            self.context.add_error(error)
            raise RuntimeError(error)

        # Check call stack
        self.context.push_call(func_name)

        try:
            # Set up function parameters
            params = func_def.get("params", [])
            if len(args) != len(params):
                error = f"Function {func_name} expects {len(params)} arguments, got {len(args)}"
                raise RuntimeError(error)

            # Save current variables
            saved_vars = self.context.variables.copy()

            # Set parameter values
            for param, arg in zip(params, args):
                self.context.set_variable(param, arg)

            # Execute function body
            result = None
            for stmt in func_def.get("body", []):
                result = self.visit(stmt)

            # Restore variables
            self.context.variables = saved_vars

            output = f"Function {func_name} executed"
            self.output_buffer.append(output)
            return result

        finally:
            self.context.pop_call()

    def visit_variable_assign(self, node: SyntaxNode) -> Any:
        """Execute a variable assignment node"""
        var_name = node.value.get("name")
        var_value = node.value.get("value")

        # For now, store the raw value - in a full implementation,
        # we'd evaluate expressions here
        self.context.set_variable(var_name, var_value)

        output = f"Variable assigned: {var_name} = {var_value}"
        self.output_buffer.append(output)
        return var_value

    def visit_agent(self, node: SyntaxNode) -> str:
        """Execute an agent operation node"""
        self.context.increment_counter("agent_operations")

        action = node.value.get("action")
        output = f"Agent operation: {action}"

        if self.context.agent_service:
            try:
                if action == "start":
                    result = self.context.agent_service.start()
                    output = f"Agent started: {result}"
                elif action == "stop":
                    result = self.context.agent_service.stop()
                    output = f"Agent stopped: {result}"
                elif action == "status":
                    result = self.context.agent_service.get_status()
                    output = f"Agent status: {result}"
            except Exception as e:
                output = f"Agent operation failed: {e}"
                self.context.add_warning(f"Agent error: {e}")
        else:
            output = f"Agent service not available: {action}"
            self.context.add_warning("Agent service not configured")

        self.output_buffer.append(output)
        return output

    def visit_comment(self, node: SyntaxNode) -> None:
        """Execute a comment node (no-op)"""
        return None

    def visit_conditional(self, node: SyntaxNode) -> Any:
        """Execute a conditional node"""
        condition_type = node.value.get("type")

        if condition_type == "if":
            condition = node.value.get("condition")
            # For now, just log the condition - full evaluation would be implemented here
            output = f"Conditional: if {condition}"
            self.output_buffer.append(output)

            # Execute children (body of if statement)
            result = None
            for child in node.children or []:
                result = self.visit(child)
            return result

        elif condition_type == "else":
            output = "Conditional: else"
            self.output_buffer.append(output)

            # Execute children (body of else statement)
            result = None
            for child in node.children or []:
                result = self.visit(child)
            return result

    def visit_loop(self, node: SyntaxNode) -> Any:
        """Execute a loop node"""
        loop_type = node.value.get("type")

        if loop_type == "for":
            var_name = node.value.get("var")
            iterable = node.value.get("iterable")
            output = f"Loop: for {var_name} in {iterable}"
            self.output_buffer.append(output)

            # For now, just execute the body once - full loop implementation would be here
            result = None
            for child in node.children or []:
                result = self.visit(child)
            return result

        elif loop_type == "while":
            condition = node.value.get("condition")
            output = f"Loop: while {condition}"
            self.output_buffer.append(output)

            # For now, just execute the body once - full loop implementation would be here
            result = None
            for child in node.children or []:
                result = self.visit(child)
            return result
