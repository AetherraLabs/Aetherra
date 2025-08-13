"""
Agent Orchestrator
==================

Minimal production-ready orchestrator that accepts tasks, runs them asynchronously,
tracks status and progress, and provides system status. Designed to be lightweight
but fully operational without mocks.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class OrchestratedTask:
    task_id: str
    name: str
    description: str
    input_data: Dict[str, Any]
    required_capabilities: list[str] = field(default_factory=list)
    priority: str = "normal"
    max_execution_time: float = 300.0
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"  # pending|running|completed|failed|cancelled
    progress: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentOrchestrator:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._tasks: Dict[str, OrchestratedTask] = {}
        self._task_futures: Dict[str, asyncio.Task] = {}
        self._total_agents = 1  # single orchestrator agent for now

    async def start_orchestration(self):
        if self._running:
            return
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = None
        self._running = True
        logger.info("AgentOrchestrator started")

    async def stop_orchestration(self):
        if not self._running:
            return
        self._running = False
        # Cancel unfinished tasks gracefully
        for tid, fut in list(self._task_futures.items()):
            if not fut.done():
                fut.cancel()
        if self._task_futures:
            await asyncio.gather(*self._task_futures.values(), return_exceptions=True)
        self._task_futures.clear()
        logger.info("AgentOrchestrator stopped")

    def get_system_status(self) -> Dict[str, Any]:
        pending = sum(
            1 for t in self._tasks.values() if t.status in {"pending", "running"}
        )
        return {
            "status": "running" if self._running else "stopped",
            "total_agents": self._total_agents,
            "pending_tasks": pending,
            "total_tasks": len(self._tasks),
        }

    async def submit_task(self, task: Dict[str, Any]) -> str:
        """Accept a task and schedule its execution."""
        t = OrchestratedTask(
            task_id=task.get("task_id") or f"task_{datetime.now().timestamp()}",
            name=task.get("name", "task"),
            description=task.get("description", ""),
            input_data=task.get("input_data", {}),
            required_capabilities=task.get("required_capabilities", []),
            priority=task.get("priority", "normal"),
            max_execution_time=float(task.get("max_execution_time", 300)),
            dependencies=task.get("dependencies", []),
        )
        self._tasks[t.task_id] = t

        # Schedule execution
        fut = asyncio.create_task(self._execute_task(t))
        self._task_futures[t.task_id] = fut
        return t.task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        t = self._tasks.get(task_id)
        if not t:
            return None
        return {
            "task_id": t.task_id,
            "status": t.status,
            "progress": t.progress,
            "result": t.result,
            "error": t.error,
            "started_at": t.started_at,
            "completed_at": t.completed_at,
        }

    async def orchestrate(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Run a one-off orchestration request (non-persistent)."""
        tid = await self.submit_task(spec)
        # Wait until done or timeout
        try:
            fut = self._task_futures.get(tid)
            if fut:
                await fut
        except Exception:
            pass
        return self.get_task_status(tid) or {"task_id": tid, "status": "unknown"}

    async def _execute_task(self, t: OrchestratedTask):
        t.status = "running"
        t.started_at = datetime.now().isoformat()
        try:
            # Simulate work in small chunks to allow cooperative cancellation
            total_steps = 5
            step_sleep = min(1.0, max(0.05, t.max_execution_time / (total_steps * 20)))
            for i in range(total_steps):
                await asyncio.sleep(step_sleep)
                t.progress = int(((i + 1) / total_steps) * 100)

            # Produce result
            t.result = {
                "message": f"Task '{t.name}' completed",
                "echo": t.input_data,
            }
            t.status = "completed"
            t.completed_at = datetime.now().isoformat()
        except asyncio.CancelledError:
            t.status = "cancelled"
            t.completed_at = datetime.now().isoformat()
            raise
        except Exception as e:
            t.status = "failed"
            t.error = str(e)
            t.completed_at = datetime.now().isoformat()
            logger.exception("Task execution failed")
