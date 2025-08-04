#!/usr/bin/env python3
"""
🔗 Plugin Chain Executor
========================
Executes chains of plugins in sequence or parallel for complex operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Plugin execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class ChainStatus(Enum):
    """Chain execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PluginChainStep:
    """A single step in a plugin chain."""
    plugin_name: str
    method_name: str = "execute"
    args: tuple = ()
    kwargs: Optional[Dict[str, Any]] = None
    condition: Optional[str] = None  # For conditional execution
    timeout: Optional[float] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


@dataclass
class ChainResult:
    """Result of a plugin chain execution."""
    chain_id: str
    status: ChainStatus
    results: List[Dict[str, Any]]
    execution_time: float
    error_message: Optional[str] = None
    completed_steps: int = 0
    total_steps: int = 0


class PluginChainExecutor:
    """
    🔗 Plugin Chain Executor

    Executes sequences of plugin operations with support for
    sequential, parallel, and conditional execution modes.
    """

    def __init__(self, plugin_registry: Optional[Dict[str, Any]] = None):
        """Initialize with an optional plugin registry."""
        self.plugin_registry = plugin_registry or {}
        self.active_chains: Dict[str, ChainResult] = {}
        self._chain_counter = 0

    async def execute_chain(
        self,
        steps: List[PluginChainStep],
        mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
        chain_id: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> ChainResult:
        """Execute a chain of plugin operations."""

        if chain_id is None:
            self._chain_counter += 1
            chain_id = f"chain_{self._chain_counter}"

        start_time = datetime.now()

        result = ChainResult(
            chain_id=chain_id,
            status=ChainStatus.RUNNING,
            results=[],
            execution_time=0.0,
            total_steps=len(steps)
        )

        self.active_chains[chain_id] = result

        try:
            logger.info(f"🔗 Starting plugin chain '{chain_id}' with {len(steps)} steps ({mode.value} mode)")

            if mode == ExecutionMode.SEQUENTIAL:
                await self._execute_sequential(steps, result)
            elif mode == ExecutionMode.PARALLEL:
                await self._execute_parallel(steps, result)
            elif mode == ExecutionMode.CONDITIONAL:
                await self._execute_conditional(steps, result)

            result.status = ChainStatus.COMPLETED
            result.execution_time = (datetime.now() - start_time).total_seconds()

            logger.info(f"✅ Chain '{chain_id}' completed in {result.execution_time:.2f}s")

        except Exception as e:
            result.status = ChainStatus.FAILED
            result.error_message = str(e)
            result.execution_time = (datetime.now() - start_time).total_seconds()

            logger.error(f"❌ Chain '{chain_id}' failed: {e}")

        return result

    async def _execute_sequential(self, steps: List[PluginChainStep], result: ChainResult):
        """Execute steps sequentially."""

        for i, step in enumerate(steps):
            logger.debug(f"🔗 Executing step {i+1}/{len(steps)}: {step.plugin_name}.{step.method_name}")

            step_result = await self._execute_step(step)
            result.results.append(step_result)
            result.completed_steps += 1

            # Check if step failed and should stop chain
            if not step_result.get("success", True):
                raise Exception(f"Step {i+1} failed: {step_result.get('error', 'Unknown error')}")

    async def _execute_parallel(self, steps: List[PluginChainStep], result: ChainResult):
        """Execute steps in parallel."""

        logger.debug(f"🔗 Executing {len(steps)} steps in parallel")

        # Create tasks for all steps
        tasks = [self._execute_step(step) for step in steps]

        # Wait for all tasks to complete
        step_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, step_result in enumerate(step_results):
            if isinstance(step_result, Exception):
                result.results.append({
                    "success": False,
                    "error": str(step_result),
                    "step": i
                })
            else:
                # step_result should be Dict[str, Any] from _execute_step
                if isinstance(step_result, dict):
                    result.results.append(step_result)
                    if step_result.get("success", False):
                        result.completed_steps += 1
                else:
                    # Fallback for unexpected result types
                    result.results.append({
                        "success": False,
                        "error": f"Unexpected result type: {type(step_result)}",
                        "step": i
                    })

    async def _execute_conditional(self, steps: List[PluginChainStep], result: ChainResult):
        """Execute steps with conditional logic."""

        context = {}  # Shared context for conditions

        for i, step in enumerate(steps):
            # Check condition if specified
            if step.condition and not self._evaluate_condition(step.condition, context):
                logger.debug(f"⏭️ Skipping step {i+1}: condition '{step.condition}' not met")
                result.results.append({
                    "success": True,
                    "skipped": True,
                    "condition": step.condition
                })
                continue

            logger.debug(f"🔗 Executing conditional step {i+1}/{len(steps)}: {step.plugin_name}.{step.method_name}")

            step_result = await self._execute_step(step)
            result.results.append(step_result)
            result.completed_steps += 1

            # Update context with step result
            context[f"step_{i}_result"] = step_result
            context[f"step_{i}_success"] = step_result.get("success", True)

    async def _execute_step(self, step: PluginChainStep) -> Dict[str, Any]:
        """Execute a single plugin step."""

        try:
            # In a real implementation, this would call the actual plugin manager
            # For now, return a mock successful result

            await asyncio.sleep(0.1)  # Simulate plugin execution time

            return {
                "success": True,
                "plugin": step.plugin_name,
                "method": step.method_name,
                "result": f"Mock result from {step.plugin_name}.{step.method_name}",
                "execution_time": 0.1
            }

        except Exception as e:
            return {
                "success": False,
                "plugin": step.plugin_name,
                "method": step.method_name,
                "error": str(e),
                "execution_time": 0.0
            }

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition string against the current context."""

        try:
            # Simple condition evaluation (in production, use a safer evaluator)
            # For now, just check for basic conditions

            if "success" in condition:
                # Check if previous step was successful
                return context.get("step_0_success", True)

            # Default to True for unknown conditions
            return True

        except Exception as e:
            logger.warning(f"⚠️ Error evaluating condition '{condition}': {e}")
            return False

    def get_chain_status(self, chain_id: str) -> Optional[ChainResult]:
        """Get the status of a specific chain."""
        return self.active_chains.get(chain_id)

    def list_active_chains(self) -> List[str]:
        """List all active chain IDs."""
        return [
            chain_id for chain_id, result in self.active_chains.items()
            if result.status == ChainStatus.RUNNING
        ]

    async def cancel_chain(self, chain_id: str) -> bool:
        """Cancel a running chain."""

        if chain_id not in self.active_chains:
            return False

        result = self.active_chains[chain_id]
        if result.status == ChainStatus.RUNNING:
            result.status = ChainStatus.CANCELLED
            logger.info(f"❌ Cancelled chain '{chain_id}'")
            return True

        return False

    def cleanup_completed_chains(self, max_age_hours: int = 24):
        """Clean up old completed chains."""

        current_time = datetime.now()
        to_remove = []

        for chain_id, result in self.active_chains.items():
            if result.status in [ChainStatus.COMPLETED, ChainStatus.FAILED, ChainStatus.CANCELLED]:
                # In a real implementation, would check actual completion time
                to_remove.append(chain_id)

        for chain_id in to_remove[:10]:  # Limit cleanup to prevent large operations
            del self.active_chains[chain_id]

        if to_remove:
            logger.debug(f"🧹 Cleaned up {len(to_remove[:10])} completed chains")


# Convenience functions for common chain patterns
async def execute_plugin_sequence(plugin_calls: List[tuple]) -> ChainResult:
    """Execute a sequence of plugin calls."""

    executor = PluginChainExecutor()
    steps = []

    for call in plugin_calls:
        if len(call) == 2:
            plugin_name, method_name = call
            args, kwargs = (), {}
        elif len(call) == 3:
            plugin_name, method_name, args = call
            kwargs = {}
        elif len(call) == 4:
            plugin_name, method_name, args, kwargs = call
        else:
            raise ValueError(f"Invalid plugin call format: {call}")

        steps.append(PluginChainStep(
            plugin_name=plugin_name,
            method_name=method_name,
            args=args,
            kwargs=kwargs
        ))

    return await executor.execute_chain(steps, ExecutionMode.SEQUENTIAL)


async def execute_plugin_parallel(plugin_calls: List[tuple]) -> ChainResult:
    """Execute plugin calls in parallel."""

    executor = PluginChainExecutor()
    steps = []

    for call in plugin_calls:
        if len(call) >= 2:
            plugin_name, method_name = call[0], call[1]
            args = call[2] if len(call) > 2 else ()
            kwargs = call[3] if len(call) > 3 else {}

            steps.append(PluginChainStep(
                plugin_name=plugin_name,
                method_name=method_name,
                args=args,
                kwargs=kwargs
            ))

    return await executor.execute_chain(steps, ExecutionMode.PARALLEL)
