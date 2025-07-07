#!/usr/bin/env python3
"""
🧬 Aetherra Standard Library - Executor Plugin
Built-in plugin for command scheduling and execution management
"""

import subprocess
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timedelta
from queue import PriorityQueue
from typing import Any, Dict, List, Optional


class ExecutorPlugin:
    """Command scheduling and execution management for Aetherra"""

    def __init__(self):
        self.name = "executor"
        self.description = "Command scheduling and execution management"
        self.available_actions = [
            "schedule_command",
            "execute_now",
            "execute_async",
            "schedule_recurring",
            "cancel_scheduled",
            "list_scheduled",
            "execute_batch",
            "monitor_execution",
            "set_timeout",
            "execute_with_retry",
            "status",
        ]

        # Execution management
        self.scheduled_tasks = {}
        self.running_tasks = {}
        self.completed_tasks = {}
        self.task_queue = PriorityQueue()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.execution_history = []

        # Background scheduler
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True
        )
        self.scheduler_thread.start()

    def schedule_command(
        self,
        command: str,
        execution_time: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule a command for future execution"""
        task_id = str(uuid.uuid4())

        # Parse execution time
        if execution_time.startswith("+"):
            # Relative time (e.g., "+5m", "+1h", "+30s")
            delay = self._parse_relative_time(execution_time)
            scheduled_time = datetime.now() + delay
        else:
            # Absolute time (e.g., "2025-06-29 15:30:00")
            scheduled_time = datetime.fromisoformat(execution_time)

        task = {
            "id": task_id,
            "command": command,
            "scheduled_time": scheduled_time,
            "context": context or {},
            "status": "scheduled",
            "created_at": datetime.now(),
            "attempts": 0,
            "max_attempts": context.get("max_attempts", 1) if context else 1,
        }

        self.scheduled_tasks[task_id] = task

        # Add to priority queue (earlier times have higher priority)
        priority = int(scheduled_time.timestamp())
        self.task_queue.put((priority, task_id))

        return f"Command scheduled with ID: {task_id} for {scheduled_time}"

    def execute_now(
        self, command: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a command immediately"""
        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "command": command,
            "context": context or {},
            "status": "executing",
            "started_at": datetime.now(),
        }

        self.running_tasks[task_id] = task

        try:
            result = self._execute_command(command, context or {})
            task["status"] = "completed"
            task["completed_at"] = datetime.now()
            task["result"] = result

            # Move to completed tasks
            self.completed_tasks[task_id] = task
            del self.running_tasks[task_id]

            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "execution_time": (
                    task["completed_at"] - task["started_at"]
                ).total_seconds(),
            }

        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            task["completed_at"] = datetime.now()

            self.completed_tasks[task_id] = task
            del self.running_tasks[task_id]

            return {"task_id": task_id, "status": "failed", "error": str(e)}

    def execute_async(
        self, command: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a command asynchronously"""
        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "command": command,
            "context": context or {},
            "status": "queued",
            "created_at": datetime.now(),
        }

        # Submit to thread pool
        future = self.thread_pool.submit(self._execute_command, command, context or {})
        task["future"] = future

        self.running_tasks[task_id] = task

        # Set up completion callback
        future.add_done_callback(lambda f: self._handle_async_completion(task_id, f))

        return f"Async execution started with ID: {task_id}"

    def schedule_recurring(
        self, command: str, interval: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Schedule a command for recurring execution"""
        task_id = str(uuid.uuid4())

        interval_seconds = self._parse_interval(interval)

        task = {
            "id": task_id,
            "command": command,
            "interval": interval_seconds,
            "context": context or {},
            "status": "recurring",
            "created_at": datetime.now(),
            "next_execution": datetime.now() + timedelta(seconds=interval_seconds),
            "execution_count": 0,
        }

        self.scheduled_tasks[task_id] = task

        return f"Recurring command scheduled with ID: {task_id} (interval: {interval})"

    def cancel_scheduled(self, task_id: str) -> str:
        """Cancel a scheduled task"""
        if task_id in self.scheduled_tasks:
            task = self.scheduled_tasks[task_id]
            task["status"] = "cancelled"
            task["cancelled_at"] = datetime.now()

            # Move to completed tasks
            self.completed_tasks[task_id] = task
            del self.scheduled_tasks[task_id]

            return f"Task {task_id} cancelled successfully"

        return f"Task {task_id} not found in scheduled tasks"

    def list_scheduled(self) -> Dict[str, Any]:
        """List all scheduled tasks"""
        return {
            "scheduled_count": len(self.scheduled_tasks),
            "running_count": len(self.running_tasks),
            "scheduled_tasks": [
                {
                    "id": task["id"],
                    "command": task["command"],
                    "scheduled_time": task.get("scheduled_time"),
                    "status": task["status"],
                    "next_execution": task.get("next_execution"),
                }
                for task in self.scheduled_tasks.values()
            ],
            "running_tasks": [
                {
                    "id": task["id"],
                    "command": task["command"],
                    "status": task["status"],
                    "started_at": task.get("started_at"),
                }
                for task in self.running_tasks.values()
            ],
        }

    def execute_batch(
        self, commands: List[str], execution_mode: str = "sequential"
    ) -> Dict[str, Any]:
        """Execute multiple commands in batch"""
        batch_id = str(uuid.uuid4())

        if execution_mode == "sequential":
            return self._execute_sequential_batch(batch_id, commands)
        elif execution_mode == "parallel":
            return self._execute_parallel_batch(batch_id, commands)
        else:
            return {"error": f"Unknown execution mode: {execution_mode}"}

    def monitor_execution(self, task_id: str) -> Dict[str, Any]:
        """Monitor the execution status of a task"""
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task["status"],
                "command": task["command"],
                "started_at": task.get("started_at"),
                "running_time": (
                    datetime.now() - task.get("started_at", datetime.now())
                ).total_seconds(),
            }

        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task["status"],
                "command": task["command"],
                "result": task.get("result"),
                "error": task.get("error"),
                "execution_time": task.get("execution_time"),
            }

        # Check scheduled tasks
        if task_id in self.scheduled_tasks:
            task = self.scheduled_tasks[task_id]
            return {
                "task_id": task_id,
                "status": task["status"],
                "command": task["command"],
                "scheduled_time": task.get("scheduled_time"),
                "next_execution": task.get("next_execution"),
            }

        return {"error": f"Task {task_id} not found"}

    def set_timeout(self, task_id: str, timeout_seconds: int) -> str:
        """Set a timeout for a running task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task["timeout"] = timeout_seconds
            task["timeout_at"] = datetime.now() + timedelta(seconds=timeout_seconds)
            return f"Timeout set for task {task_id}: {timeout_seconds} seconds"

        return f"Task {task_id} not found in running tasks"

    def execute_with_retry(
        self, command: str, max_attempts: int = 3, retry_delay: int = 1
    ) -> Dict[str, Any]:
        """Execute a command with retry logic"""
        task_id = str(uuid.uuid4())

        for attempt in range(max_attempts):
            try:
                result = self._execute_command(command, {"attempt": attempt + 1})

                return {
                    "task_id": task_id,
                    "status": "completed",
                    "result": result,
                    "attempts": attempt + 1,
                    "success": True,
                }

            except Exception as e:
                if attempt < max_attempts - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "task_id": task_id,
                        "status": "failed",
                        "error": str(e),
                        "attempts": max_attempts,
                        "success": False,
                    }

    def status(self) -> Dict[str, Any]:
        """Get current executor status"""
        return {
            "name": self.name,
            "description": self.description,
            "available_actions": self.available_actions,
            "scheduled_tasks": len(self.scheduled_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "thread_pool_active": self.thread_pool._threads,
            "scheduler_running": self.scheduler_running,
        }

    # Private helper methods
    def _scheduler_loop(self):
        """Background scheduler loop"""
        while self.scheduler_running:
            try:
                current_time = datetime.now()

                # Check for tasks ready to execute
                tasks_to_execute = []
                for task_id, task in list(self.scheduled_tasks.items()):
                    if (
                        task.get("scheduled_time")
                        and task["scheduled_time"] <= current_time
                    ):
                        tasks_to_execute.append(task_id)
                    elif (
                        task.get("next_execution")
                        and task["next_execution"] <= current_time
                    ):
                        tasks_to_execute.append(task_id)

                # Execute ready tasks
                for task_id in tasks_to_execute:
                    self._execute_scheduled_task(task_id)

                time.sleep(1)  # Check every second

            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(5)  # Wait longer on error

    def _execute_scheduled_task(self, task_id: str):
        """Execute a scheduled task"""
        if task_id not in self.scheduled_tasks:
            return

        task = self.scheduled_tasks[task_id]

        # Move to running tasks
        task["status"] = "executing"
        task["started_at"] = datetime.now()
        self.running_tasks[task_id] = task

        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]

        # Execute asynchronously
        future = self.thread_pool.submit(
            self._execute_command, task["command"], task["context"]
        )
        task["future"] = future
        future.add_done_callback(
            lambda f: self._handle_scheduled_completion(task_id, f)
        )

    def _execute_command(self, command: str, context: Dict[str, Any]) -> Any:
        """Execute a single command"""
        # Record execution start
        execution_record = {
            "command": command,
            "context": context,
            "started_at": datetime.now(),
        }

        try:
            # Determine command type and execute accordingly
            if command.startswith("neuro:"):
                # Aetherra-specific command
                result = self._execute_neuro_command(command[6:], context)
            elif command.startswith("sys:"):
                # System command
                result = self._execute_system_command(command[4:], context)
            elif command.startswith("python:"):
                # Python code execution
                result = self._execute_python_code(command[7:], context)
            else:
                # Default: treat as Aetherra command
                result = self._execute_neuro_command(command, context)

            execution_record["completed_at"] = datetime.now()
            execution_record["result"] = result
            execution_record["status"] = "success"

            self.execution_history.append(execution_record)
            return result

        except Exception as e:
            execution_record["completed_at"] = datetime.now()
            execution_record["error"] = str(e)
            execution_record["status"] = "error"

            self.execution_history.append(execution_record)
            raise e

    def _execute_neuro_command(self, command: str, context: Dict[str, Any]) -> str:
        """Execute a Aetherra-specific command"""
        # This would integrate with the main Aetherra interpreter
        # For now, return a mock response
        return f"Aetherra command executed: {command}"

    def _execute_system_command(self, command: str, context: Dict[str, Any]) -> str:
        """Execute a system command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=context.get("timeout", 30),
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(
                    f"Command failed with exit code {result.returncode}: {result.stderr}"
                )

        except subprocess.TimeoutExpired:
            raise Exception("Command timed out")

    def _execute_python_code(self, code: str, context: Dict[str, Any]) -> Any:
        """Execute Python code safely"""
        # Limited Python execution for security
        allowed_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
            }
        }

        try:
            # Execute in restricted environment
            exec(code, allowed_globals, context)
            return "Python code executed successfully"
        except Exception as e:
            raise Exception(f"Python execution error: {e}")

    def _handle_async_completion(self, task_id: str, future: Future):
        """Handle completion of async task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]

            try:
                result = future.result()
                task["status"] = "completed"
                task["result"] = result
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)

            task["completed_at"] = datetime.now()

            # Move to completed tasks
            self.completed_tasks[task_id] = task
            del self.running_tasks[task_id]

    def _handle_scheduled_completion(self, task_id: str, future: Future):
        """Handle completion of scheduled task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]

            try:
                result = future.result()
                task["status"] = "completed"
                task["result"] = result
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)

            task["completed_at"] = datetime.now()

            # Handle recurring tasks
            if task.get("interval"):
                task["execution_count"] = task.get("execution_count", 0) + 1
                task["next_execution"] = datetime.now() + timedelta(
                    seconds=task["interval"]
                )
                task["status"] = "recurring"

                # Move back to scheduled tasks
                self.scheduled_tasks[task_id] = task
            else:
                # Move to completed tasks
                self.completed_tasks[task_id] = task

            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

    def _execute_sequential_batch(
        self, batch_id: str, commands: List[str]
    ) -> Dict[str, Any]:
        """Execute commands sequentially"""
        results = []

        for i, command in enumerate(commands):
            try:
                result = self._execute_command(
                    command, {"batch_id": batch_id, "index": i}
                )
                results.append(
                    {"command": command, "result": result, "status": "success"}
                )
            except Exception as e:
                results.append(
                    {"command": command, "error": str(e), "status": "failed"}
                )
                break  # Stop on first failure

        return {
            "batch_id": batch_id,
            "mode": "sequential",
            "total_commands": len(commands),
            "executed_commands": len(results),
            "results": results,
        }

    def _execute_parallel_batch(
        self, batch_id: str, commands: List[str]
    ) -> Dict[str, Any]:
        """Execute commands in parallel"""
        futures = []

        for i, command in enumerate(commands):
            future = self.thread_pool.submit(
                self._execute_command, command, {"batch_id": batch_id, "index": i}
            )
            futures.append((command, future))

        results = []
        for command, future in futures:
            try:
                result = future.result(timeout=60)  # 60 second timeout
                results.append(
                    {"command": command, "result": result, "status": "success"}
                )
            except Exception as e:
                results.append(
                    {"command": command, "error": str(e), "status": "failed"}
                )

        return {
            "batch_id": batch_id,
            "mode": "parallel",
            "total_commands": len(commands),
            "results": results,
        }

    def _parse_relative_time(self, time_str: str) -> timedelta:
        """Parse relative time string like '+5m', '+1h', '+30s'"""
        time_str = time_str.strip("+")

        if time_str.endswith("s"):
            return timedelta(seconds=int(time_str[:-1]))
        elif time_str.endswith("m"):
            return timedelta(minutes=int(time_str[:-1]))
        elif time_str.endswith("h"):
            return timedelta(hours=int(time_str[:-1]))
        elif time_str.endswith("d"):
            return timedelta(days=int(time_str[:-1]))
        else:
            # Default to seconds
            return timedelta(seconds=int(time_str))

    def _parse_interval(self, interval_str: str) -> int:
        """Parse interval string and return seconds"""
        if interval_str.endswith("s"):
            return int(interval_str[:-1])
        elif interval_str.endswith("m"):
            return int(interval_str[:-1]) * 60
        elif interval_str.endswith("h"):
            return int(interval_str[:-1]) * 3600
        elif interval_str.endswith("d"):
            return int(interval_str[:-1]) * 86400
        else:
            # Default to seconds
            return int(interval_str)

    def execute_action(self, action: str, memory_system=None, **kwargs) -> str:
        """Execute an executor action with standardized interface"""
        try:
            if action == "schedule" or action == "schedule_command":
                command = kwargs.get("command", 'echo "test"')
                exec_time = kwargs.get("execution_time", "+1m")
                context = kwargs.get("context", {})
                task_id = self.schedule_command(command, exec_time, context)
                return f"Command scheduled with ID: {task_id}"

            elif action == "execute" or action == "execute_now":
                command = kwargs.get("command", 'echo "test"')
                context = kwargs.get("context", {})
                result = self.execute_now(command, context)
                return (
                    f"Command executed. Exit code: {result.get('exit_code', 'unknown')}"
                )

            elif action == "async" or action == "execute_async":
                command = kwargs.get("command", 'echo "test"')
                context = kwargs.get("context", {})
                task_id = self.execute_async(command, context)
                return f"Async command started with ID: {task_id}"

            elif action == "list" or action == "list_scheduled":
                tasks = self.list_scheduled()
                return f"Found {len(tasks)} scheduled tasks."

            elif action == "status":
                scheduled = len(self.scheduled_tasks)
                running = len(self.running_tasks)
                completed = len(self.completed_tasks)
                return f"Executor status: {scheduled} scheduled, {running} running, {completed} completed tasks."

            else:
                available = ", ".join(self.available_actions)
                return f"Unknown action '{action}'. Available: {available}"

        except Exception as e:
            return f"Error in executor.{action}: {str(e)}"


# Plugin registration
PLUGIN_CLASS = ExecutorPlugin
