#!/usr/bin/env python3
"""
⚡ Aetherra Scheduler
=====================
Task scheduling and orchestration system for Aetherra AI OS.

Manages background tasks, system maintenance, and coordinated execution
of various Aetherra subsystems.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """A scheduled task with execution details."""
    task_id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: Optional[dict] = None
    priority: TaskPriority = TaskPriority.NORMAL
    interval: Optional[float] = None  # For recurring tasks
    next_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: Optional[datetime] = None
    last_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.next_run is None:
            self.next_run = datetime.now()


class AetherraScheduler:
    """
    🗓️ Aetherra Task Scheduler

    Manages the execution of scheduled tasks across the Aetherra system.
    Supports one-time tasks, recurring tasks, and priority-based execution.
    """

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._task_counter = 0

    async def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return

        logger.info("🗓️ Starting Aetherra Scheduler...")
        self.running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("✅ Aetherra Scheduler started")

    async def stop(self):
        """Stop the scheduler."""
        if not self.running:
            return

        logger.info("🛑 Stopping Aetherra Scheduler...")
        self.running = False

        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ Aetherra Scheduler stopped")

    def schedule_task(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay: float = 0,
        interval: Optional[float] = None,
        max_runs: Optional[int] = None
    ) -> str:
        """
        Schedule a task for execution.

        Args:
            name: Human-readable task name
            func: Function to execute
            args: Arguments for the function
            kwargs: Keyword arguments for the function
            priority: Task priority level
            delay: Delay before first execution (seconds)
            interval: Interval for recurring tasks (seconds)
            max_runs: Maximum number of executions (None for unlimited)

        Returns:
            Task ID
        """
        self._task_counter += 1
        task_id = f"task_{self._task_counter}_{name.replace(' ', '_').lower()}"

        next_run = datetime.now() + timedelta(seconds=delay)

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            interval=interval,
            next_run=next_run,
            max_runs=max_runs
        )

        self.tasks[task_id] = task
        logger.info(f"📋 Scheduled task '{name}' (ID: {task_id})")

        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
            logger.info(f"❌ Cancelled task {task_id}")
            return True
        return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        task = self.tasks.get(task_id)
        return task.status if task else None

    def list_tasks(self) -> List[Dict[str, Any]]:
        """List all tasks with their status."""
        task_list = []
        for task in self.tasks.values():
            task_info = {
                "id": task.task_id,
                "name": task.name,
                "status": task.status.value,
                "priority": task.priority.name,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "run_count": task.run_count,
                "max_runs": task.max_runs,
                "interval": task.interval
            }
            task_list.append(task_info)

        return task_list

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        logger.info("🔄 Scheduler loop started")

        while self.running:
            try:
                await self._process_pending_tasks()
                await asyncio.sleep(1)  # Check every second

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _process_pending_tasks(self):
        """Process tasks that are ready to run."""
        now = datetime.now()
        ready_tasks = []

        # Find tasks ready to run
        for task in self.tasks.values():
            if (task.status == TaskStatus.PENDING and
                task.next_run and
                task.next_run <= now):
                ready_tasks.append(task)

        # Sort by priority
        ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)

        # Execute ready tasks
        for task in ready_tasks:
            if not self.running:
                break

            await self._execute_task(task)

    async def _execute_task(self, task: ScheduledTask):
        """Execute a single task."""
        try:
            logger.debug(f"🏃 Executing task '{task.name}' (ID: {task.task_id})")
            task.status = TaskStatus.RUNNING
            task.last_run = datetime.now()
            task.run_count += 1

            # Execute the task function
            kwargs_to_use = task.kwargs or {}
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **kwargs_to_use)
            else:
                result = task.func(*task.args, **kwargs_to_use)

            task.status = TaskStatus.COMPLETED
            logger.debug(f"✅ Task '{task.name}' completed")

            # Schedule next run if recurring
            if task.interval and (not task.max_runs or task.run_count < task.max_runs):
                task.next_run = datetime.now() + timedelta(seconds=task.interval)
                task.status = TaskStatus.PENDING
                logger.debug(f"🔄 Rescheduled recurring task '{task.name}' for {task.next_run}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            logger.error(f"❌ Task '{task.name}' failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status information."""
        task_counts = {}
        for status in TaskStatus:
            task_counts[status.value] = sum(1 for t in self.tasks.values() if t.status == status)

        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "task_counts": task_counts,
            "next_task": self._get_next_task_info()
        }

    def _get_next_task_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the next task to run."""
        pending_tasks = [t for t in self.tasks.values()
                        if t.status == TaskStatus.PENDING and t.next_run is not None]

        if not pending_tasks:
            return None

        next_task = min(pending_tasks, key=lambda t: t.next_run)  # type: ignore

        return {
            "id": next_task.task_id,
            "name": next_task.name,
            "next_run": next_task.next_run.isoformat(),
            "priority": next_task.priority.name
        }


# Default scheduler instance
_default_scheduler: Optional[AetherraScheduler] = None


async def get_scheduler() -> AetherraScheduler:
    """Get the default scheduler instance."""
    global _default_scheduler

    if _default_scheduler is None:
        _default_scheduler = AetherraScheduler()
        await _default_scheduler.start()

    return _default_scheduler


# Convenience functions
async def schedule_task(*args, **kwargs) -> str:
    """Schedule a task using the default scheduler."""
    scheduler = await get_scheduler()
    return scheduler.schedule_task(*args, **kwargs)


async def cancel_task(task_id: str) -> bool:
    """Cancel a task using the default scheduler."""
    scheduler = await get_scheduler()
    return scheduler.cancel_task(task_id)


async def list_tasks() -> List[Dict[str, Any]]:
    """List all tasks using the default scheduler."""
    scheduler = await get_scheduler()
    return scheduler.list_tasks()
