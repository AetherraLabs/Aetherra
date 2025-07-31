"""
Aetherra Plugin Chain Executor
Advanced plugin chain execution and orchestration system.
"""

import asyncio
import json
import logging
import sqlite3
import traceback
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of plugin chain execution"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ChainStrategy(Enum):
    """Strategy for executing plugin chains"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"


@dataclass
class PluginResult:
    """Result from a plugin execution"""

    plugin_id: str
    success: bool
    output: Any
    execution_time: float
    error_message: str | None = None
    metadata: Dict[str, Any] | None = None


@dataclass
class ChainExecution:
    """Represents a plugin chain execution"""

    chain_id: str
    strategy: ChainStrategy
    plugins: List[str]
    status: ExecutionStatus
    start_time: datetime
    end_time: datetime | None = None
    results: List[PluginResult] | None = None
    context: Dict[str, Any] | None = None


class PluginInterface:
    """Base interface for plugins"""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.dependencies = []
        self.capabilities = []

    async def execute(self, input_data: Any, context: Dict[str, Any]) -> PluginResult:
        """Execute the plugin"""
        raise NotImplementedError("Subclasses must implement execute method")

    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        return True

    async def cleanup(self):
        """Cleanup resources"""
        pass


class ConditionalExecutor:
    """Handles conditional execution logic"""

    @staticmethod
    def evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition string"""
        try:
            # Simple condition evaluation (can be extended)
            if "==" in condition:
                left, right = condition.split("==")
                left_val = context.get(left.strip())
                right_val = right.strip().strip("\"'")
                return str(left_val) == right_val
            elif "!=" in condition:
                left, right = condition.split("!=")
                left_val = context.get(left.strip())
                right_val = right.strip().strip("\"'")
                return str(left_val) != right_val
            elif ">" in condition:
                left, right = condition.split(">")
                left_val = float(context.get(left.strip(), 0))
                right_val = float(right.strip())
                return left_val > right_val
            elif "<" in condition:
                left, right = condition.split("<")
                left_val = float(context.get(left.strip(), 0))
                right_val = float(right.strip())
                return left_val < right_val
            else:
                # Simple boolean evaluation
                return bool(context.get(condition.strip(), False))
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False


class ChainOptimizer:
    """Optimizes plugin chain execution"""

    def __init__(self):
        self.performance_history = {}

    def optimize_chain(self, plugins: List[str], context: Dict[str, Any]) -> List[str]:
        """Optimize plugin execution order"""
        # Simple optimization based on historical performance
        if not self.performance_history:
            return plugins

        # Sort by average execution time (fastest first for parallel)
        def get_avg_time(plugin_id):
            history = self.performance_history.get(plugin_id, [])
            return sum(history) / len(history) if history else float("inf")

        return sorted(plugins, key=get_avg_time)

    def record_performance(self, plugin_id: str, execution_time: float):
        """Record plugin performance"""
        if plugin_id not in self.performance_history:
            self.performance_history[plugin_id] = []
        self.performance_history[plugin_id].append(execution_time)

        # Keep only recent history
        if len(self.performance_history[plugin_id]) > 100:
            self.performance_history[plugin_id] = self.performance_history[plugin_id][
                -100:
            ]


class PluginChainExecutor:
    """
    Advanced plugin chain executor with multiple execution strategies
    """

    def __init__(self, db_path: str = "plugin_chains.db"):
        self.db_path = Path(db_path)
        self.registered_plugins: Dict[str, PluginInterface] = {}
        self.active_executions: Dict[str, ChainExecution] = {}
        self.conditional_executor = ConditionalExecutor()
        self.optimizer = ChainOptimizer()
        self.max_concurrent_chains = 5
        self.execution_timeout = 300  # 5 minutes default
        self._init_database()

    def _init_database(self):
        """Initialize plugin chain database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chain_executions (
                    id TEXT PRIMARY KEY,
                    strategy TEXT NOT NULL,
                    plugins TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    results TEXT,
                    context TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_performance (
                    plugin_id TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    chain_id TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS chain_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    strategy TEXT NOT NULL,
                    plugins TEXT NOT NULL,
                    conditions TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()
        finally:
            conn.close()

    def register_plugin(self, plugin: PluginInterface):
        """Register a plugin for chain execution"""
        self.registered_plugins[plugin.plugin_id] = plugin
        logger.info(f"Registered plugin: {plugin.plugin_id}")

    def unregister_plugin(self, plugin_id: str):
        """Unregister a plugin"""
        if plugin_id in self.registered_plugins:
            del self.registered_plugins[plugin_id]
            logger.info(f"Unregistered plugin: {plugin_id}")

    async def execute_chain(
        self,
        plugins: List[str],
        strategy: ChainStrategy = ChainStrategy.SEQUENTIAL,
        context: Dict[str, Any] | None = None,
        conditions: Dict[str, str] | None = None,
    ) -> ChainExecution:
        """Execute a plugin chain with specified strategy"""

        chain_id = str(uuid.uuid4())
        execution = ChainExecution(
            chain_id=chain_id,
            strategy=strategy,
            plugins=plugins,
            status=ExecutionStatus.PENDING,
            start_time=datetime.now(),
            context=context or {},
        )

        self.active_executions[chain_id] = execution

        try:
            logger.info(
                f"Starting chain execution {chain_id} with strategy {strategy.value}"
            )
            execution.status = ExecutionStatus.RUNNING

            # Validate all plugins are registered
            missing_plugins = [p for p in plugins if p not in self.registered_plugins]
            if missing_plugins:
                raise ValueError(f"Plugins not registered: {missing_plugins}")

            # Execute based on strategy
            if strategy == ChainStrategy.SEQUENTIAL:
                results = await self._execute_sequential(
                    plugins, execution.context, conditions
                )
            elif strategy == ChainStrategy.PARALLEL:
                results = await self._execute_parallel(
                    plugins, execution.context, conditions
                )
            elif strategy == ChainStrategy.CONDITIONAL:
                results = await self._execute_conditional(
                    plugins, execution.context, conditions
                )
            elif strategy == ChainStrategy.PIPELINE:
                results = await self._execute_pipeline(
                    plugins, execution.context, conditions
                )
            elif strategy == ChainStrategy.ADAPTIVE:
                results = await self._execute_adaptive(
                    plugins, execution.context, conditions
                )
            else:
                raise ValueError(f"Unsupported strategy: {strategy}")

            execution.results = results
            execution.status = ExecutionStatus.COMPLETED
            execution.end_time = datetime.now()

            logger.info(f"Chain execution {chain_id} completed successfully")

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.end_time = datetime.now()
            logger.error(f"Chain execution {chain_id} failed: {e}")
            logger.debug(traceback.format_exc())

        finally:
            await self._store_execution(execution)
            if chain_id in self.active_executions:
                del self.active_executions[chain_id]

        return execution

    async def _execute_sequential(
        self,
        plugins: List[str],
        context: Dict[str, Any],
        conditions: Dict[str, str] | None = None,
    ) -> List[PluginResult]:
        """Execute plugins sequentially"""
        results = []
        current_input = context.get("initial_input")

        for plugin_id in plugins:
            if conditions and plugin_id in conditions:
                if not self.conditional_executor.evaluate_condition(
                    conditions[plugin_id], context
                ):
                    logger.info(f"Skipping plugin {plugin_id} due to condition")
                    continue

            plugin = self.registered_plugins[plugin_id]
            start_time = asyncio.get_event_loop().time()

            try:
                result = await asyncio.wait_for(
                    plugin.execute(current_input, context),
                    timeout=self.execution_timeout,
                )
                execution_time = asyncio.get_event_loop().time() - start_time

                # Update context with result
                context[f"{plugin_id}_result"] = result.output
                current_input = result.output  # Chain output to next input

                # Record performance
                self.optimizer.record_performance(plugin_id, execution_time)

                results.append(result)
                logger.debug(
                    f"Plugin {plugin_id} executed successfully in {execution_time:.2f}s"
                )

            except Exception as e:
                execution_time = asyncio.get_event_loop().time() - start_time
                error_result = PluginResult(
                    plugin_id=plugin_id,
                    success=False,
                    output=None,
                    execution_time=execution_time,
                    error_message=str(e),
                )
                results.append(error_result)
                logger.error(f"Plugin {plugin_id} failed: {e}")

                # Stop chain on failure (sequential behavior)
                break

        return results

    async def _execute_parallel(
        self,
        plugins: List[str],
        context: Dict[str, Any],
        conditions: Dict[str, str] | None = None,
    ) -> List[PluginResult]:
        """Execute plugins in parallel"""
        tasks = []

        for plugin_id in plugins:
            if conditions and plugin_id in conditions:
                if not self.conditional_executor.evaluate_condition(
                    conditions[plugin_id], context
                ):
                    continue

            plugin = self.registered_plugins[plugin_id]
            task = asyncio.create_task(
                self._execute_single_plugin(
                    plugin, context.get("initial_input"), context
                )
            )
            tasks.append((plugin_id, task))

        results = []
        for plugin_id, task in tasks:
            try:
                result = await task
                results.append(result)
                logger.debug(f"Plugin {plugin_id} completed in parallel execution")
            except Exception as e:
                error_result = PluginResult(
                    plugin_id=plugin_id,
                    success=False,
                    output=None,
                    execution_time=0,
                    error_message=str(e),
                )
                results.append(error_result)

        return results

    async def _execute_conditional(
        self,
        plugins: List[str],
        context: Dict[str, Any],
        conditions: Dict[str, str] | None = None,
    ) -> List[PluginResult]:
        """Execute plugins based on conditions"""
        results = []

        for plugin_id in plugins:
            condition = conditions.get(plugin_id, "true") if conditions else "true"

            if self.conditional_executor.evaluate_condition(condition, context):
                plugin = self.registered_plugins[plugin_id]
                try:
                    result = await self._execute_single_plugin(
                        plugin, context.get("initial_input"), context
                    )
                    results.append(result)

                    # Update context for subsequent conditions
                    context[f"{plugin_id}_result"] = result.output
                    context[f"{plugin_id}_success"] = result.success

                except Exception as e:
                    error_result = PluginResult(
                        plugin_id=plugin_id,
                        success=False,
                        output=None,
                        execution_time=0,
                        error_message=str(e),
                    )
                    results.append(error_result)

        return results

    async def _execute_pipeline(
        self,
        plugins: List[str],
        context: Dict[str, Any],
        conditions: Dict[str, str] | None = None,
    ) -> List[PluginResult]:
        """Execute plugins in pipeline mode with data flowing through"""
        results = []
        current_data = context.get("initial_input")

        for plugin_id in plugins:
            if conditions and plugin_id in conditions:
                if not self.conditional_executor.evaluate_condition(
                    conditions[plugin_id], context
                ):
                    continue

            plugin = self.registered_plugins[plugin_id]

            try:
                result = await self._execute_single_plugin(
                    plugin, current_data, context
                )
                results.append(result)

                # Pipeline: output becomes input for next stage
                if result.success:
                    current_data = result.output
                    context[f"{plugin_id}_output"] = result.output
                else:
                    # Stop pipeline on failure
                    break

            except Exception as e:
                error_result = PluginResult(
                    plugin_id=plugin_id,
                    success=False,
                    output=None,
                    execution_time=0,
                    error_message=str(e),
                )
                results.append(error_result)
                break

        return results

    async def _execute_adaptive(
        self,
        plugins: List[str],
        context: Dict[str, Any],
        conditions: Dict[str, str] | None = None,
    ) -> List[PluginResult]:
        """Execute plugins adaptively based on performance and conditions"""
        # Optimize plugin order
        optimized_plugins = self.optimizer.optimize_chain(plugins, context)

        # Start with parallel execution but fall back to sequential on failures
        try:
            return await self._execute_parallel(optimized_plugins, context, conditions)
        except Exception:
            logger.warning("Parallel execution failed, falling back to sequential")
            return await self._execute_sequential(
                optimized_plugins, context, conditions
            )

    async def _execute_single_plugin(
        self, plugin: PluginInterface, input_data: Any, context: Dict[str, Any]
    ) -> PluginResult:
        """Execute a single plugin with timing and error handling"""
        start_time = asyncio.get_event_loop().time()

        try:
            # Validate input
            if not await plugin.validate_input(input_data):
                raise ValueError(f"Invalid input for plugin {plugin.plugin_id}")

            # Execute plugin
            result = await plugin.execute(input_data, context)
            execution_time = asyncio.get_event_loop().time() - start_time

            # Update result with timing
            result.execution_time = execution_time

            # Record performance
            self.optimizer.record_performance(plugin.plugin_id, execution_time)

            return result

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return PluginResult(
                plugin_id=plugin.plugin_id,
                success=False,
                output=None,
                execution_time=execution_time,
                error_message=str(e),
            )

    async def _store_execution(self, execution: ChainExecution):
        """Store execution results in database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO chain_executions
                (id, strategy, plugins, status, start_time, end_time, results, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    execution.chain_id,
                    execution.strategy.value,
                    json.dumps(execution.plugins),
                    execution.status.value,
                    execution.start_time.isoformat(),
                    execution.end_time.isoformat() if execution.end_time else None,
                    json.dumps(
                        [asdict(r) for r in execution.results]
                        if execution.results
                        else [],
                        default=str,
                    ),
                    json.dumps(execution.context, default=str),
                    datetime.now().isoformat(),
                ),
            )

            # Store individual plugin performance
            if execution.results:
                for result in execution.results:
                    conn.execute(
                        """
                        INSERT INTO plugin_performance
                        (plugin_id, execution_time, success, timestamp, chain_id)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (
                            result.plugin_id,
                            result.execution_time,
                            result.success,
                            datetime.now().isoformat(),
                            execution.chain_id,
                        ),
                    )

            conn.commit()
        finally:
            conn.close()

    async def cancel_chain(self, chain_id: str) -> bool:
        """Cancel a running chain execution"""
        if chain_id in self.active_executions:
            execution = self.active_executions[chain_id]
            execution.status = ExecutionStatus.CANCELLED
            execution.end_time = datetime.now()
            logger.info(f"Cancelled chain execution {chain_id}")
            return True
        return False

    def get_execution_status(self, chain_id: str) -> ExecutionStatus | None:
        """Get status of a chain execution"""
        if chain_id in self.active_executions:
            return self.active_executions[chain_id].status
        return None

    def get_plugin_performance(self, plugin_id: str) -> Dict[str, Any]:
        """Get performance statistics for a plugin"""
        history = self.optimizer.performance_history.get(plugin_id, [])
        if not history:
            return {"avg_time": 0, "min_time": 0, "max_time": 0, "execution_count": 0}

        return {
            "avg_time": sum(history) / len(history),
            "min_time": min(history),
            "max_time": max(history),
            "execution_count": len(history),
        }


# Example plugin implementation
class ExamplePlugin(PluginInterface):
    """Example plugin for testing"""

    def __init__(self, plugin_id: str, processing_time: float = 1.0):
        super().__init__(plugin_id)
        self.processing_time = processing_time

    async def execute(self, input_data: Any, context: Dict[str, Any]) -> PluginResult:
        """Execute the example plugin"""
        await asyncio.sleep(self.processing_time)  # Simulate processing

        output = f"Processed by {self.plugin_id}: {input_data}"

        return PluginResult(
            plugin_id=self.plugin_id,
            success=True,
            output=output,
            execution_time=self.processing_time,
            metadata={"processed_at": datetime.now().isoformat()},
        )


# Testing and example usage
async def test_plugin_chain_executor():
    """Test the plugin chain executor"""
    executor = PluginChainExecutor()

    # Register test plugins
    plugins = [
        ExamplePlugin("tokenizer", 0.5),
        ExamplePlugin("analyzer", 1.0),
        ExamplePlugin("formatter", 0.3),
    ]

    for plugin in plugins:
        executor.register_plugin(plugin)

    # Test sequential execution
    execution = await executor.execute_chain(
        plugins=["tokenizer", "analyzer", "formatter"],
        strategy=ChainStrategy.SEQUENTIAL,
        context={"initial_input": "Hello, world!"},
    )

    print(f"Sequential execution: {execution.status.value}")
    if execution.results:
        for result in execution.results:
            print(
                f"  {result.plugin_id}: {result.success} ({result.execution_time:.2f}s)"
            )

    # Test parallel execution
    execution = await executor.execute_chain(
        plugins=["tokenizer", "analyzer", "formatter"],
        strategy=ChainStrategy.PARALLEL,
        context={"initial_input": "Hello, world!"},
    )

    print(f"Parallel execution: {execution.status.value}")
    if execution.results:
        for result in execution.results:
            print(
                f"  {result.plugin_id}: {result.success} ({result.execution_time:.2f}s)"
            )


if __name__ == "__main__":
    asyncio.run(test_plugin_chain_executor())
