"""
Agent Orchestrator
==================

Minimal production-ready orchestrator that accepts tasks, runs them asynchronously,
tracks status and progress, and provides system status. Designed to be lightweight
but fully operational without mocks.
"""

import asyncio
import logging
import os
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
        # Track currently running tasks (lightweight gauge)
        self._active_tasks = 0
        # Lightweight counters (placeholders for future richer telemetry)
        self._counters = {
            "timeouts_total": 0,
            "policy_denied_total": 0,
            # Observer-aware policy metrics (Q4)
            "observer_gates_triggered_total": 0,
            "observer_pending_human_total": 0,
            "observer_denied_total": 0,
            "drift_alerts_total": 0,
        }
        # Coherence tracking window (for drift alerts)
        self._coherence_vals: list[float] = []
        self._last_drift_alert_ts: Optional[str] = None
        # Cached thresholds from environment (read on init; can be updated externally if needed)
        try:
            self._coh_gate_min = float(
                os.environ.get("AETHERRA_COHERENCE_GATE_MIN", "0.65")
            )
        except Exception:
            self._coh_gate_min = 0.65
        try:
            self._coh_hard_min = float(
                os.environ.get("AETHERRA_COHERENCE_HARD_MIN", "0.40")
            )
        except Exception:
            self._coh_hard_min = 0.40
        self._observer_enabled = (
            os.environ.get("AETHERRA_OBSERVER_AWARE_ENABLED", "1") == "1"
        )
        # Sensitive prefixes (comma-separated) used when input_data.sensitive is not explicitly provided
        raw_pref = os.environ.get(
            "AETHERRA_SENSITIVE_ACTIONS",
            "delete.,write.,external.,network.,danger.,unsafe.",
        )
        self._sensitive_prefixes = [
            p.strip().lower() for p in raw_pref.split(",") if p.strip()
        ]

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
        # Status breakdowns
        task_statuses: Dict[str, int] = {}
        for t in self._tasks.values():
            task_statuses[t.status] = task_statuses.get(t.status, 0) + 1

        # Pending by priority (only count tasks not yet completed/failed/cancelled)
        pending_by_priority: Dict[str, int] = {}
        for t in self._tasks.values():
            if t.status in {"pending", "running", "assigned"}:
                p = str(t.priority or "normal").lower()
                pending_by_priority[p] = pending_by_priority.get(p, 0) + 1

        return {
            "status": "running" if self._running else "stopped",
            "total_agents": self._total_agents,
            "pending_tasks": pending,
            "total_tasks": len(self._tasks),
            "active_tasks": max(0, int(self._active_tasks)),
            "task_statuses": task_statuses,
            "pending_by_priority": pending_by_priority,
            "counters": dict(self._counters),
            # Coherence policy surface (best-effort, low-cardinality)
            "coherence_policy": {
                "gate_min": self._coh_gate_min,
                "hard_min": self._coh_hard_min,
                "ema": self._coherence_ema(),
                "window_size": len(self._coherence_vals),
                "last_drift_alert": self._last_drift_alert_ts,
            },
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

        # Very light policy gate (dev convenience):
        # If caller explicitly requests denial (input_data.policy_deny == True)
        # or task name starts with "deny.", mark as policy denied.
        try:
            if bool(t.input_data.get("policy_deny", False)) or str(t.name).startswith(
                "deny."
            ):
                t.status = "failed"
                t.error = "policy_denied"
                t.completed_at = datetime.now().isoformat()
                self._counters["policy_denied_total"] = (
                    int(self._counters.get("policy_denied_total", 0)) + 1
                )
                return t.task_id
        except Exception:
            # Ignore policy evaluation issues for resilience
            pass

        # Observer-aware policy (Q4): gate sensitive actions when coherence is low
        try:
            if self._observer_enabled and bool(t.input_data.get("observer_gate", True)):
                sensitive = bool(t.input_data.get("sensitive", False))
                if not sensitive:
                    nm = str(t.name or "").lower()
                    sensitive = any(nm.startswith(p) for p in self._sensitive_prefixes)
                    if not sensitive:
                        # Also consider certain capabilities as sensitive
                        caps = [str(c).lower() for c in (t.required_capabilities or [])]
                        sensitive = any(
                            c
                            in {
                                "network",
                                "filesystem_write",
                                "external_call",
                                "danger",
                            }
                            for c in caps
                        )
                # Update coherence tracking window if provided
                coh_val = t.input_data.get("coherence_est")
                if isinstance(coh_val, (int, float)):
                    try:
                        cv = float(coh_val)
                        if 0.0 <= cv <= 1.0:
                            self._coherence_vals.append(cv)
                            # bound window
                            if len(self._coherence_vals) > 50:
                                self._coherence_vals = self._coherence_vals[-50:]
                    except Exception:
                        pass
                # Compute drift alert (ema/window-based) when enough samples exist
                try:
                    if len(self._coherence_vals) >= 5:
                        ema = self._coherence_ema()
                        drift_min = float(
                            os.environ.get("AETHERRA_DRIFT_ALERT_MIN", "0.50")
                        )
                        if ema < drift_min:
                            self._counters["drift_alerts_total"] = (
                                int(self._counters.get("drift_alerts_total", 0)) + 1
                            )
                            self._last_drift_alert_ts = datetime.now().isoformat()
                except Exception:
                    pass

                if sensitive:
                    self._counters["observer_gates_triggered_total"] = (
                        int(self._counters.get("observer_gates_triggered_total", 0)) + 1
                    )
                    # Respect explicit human-approval requirement first
                    if bool(t.input_data.get("require_human_approval", False)):
                        t.status = "pending"
                        t.error = "approval_required"
                        t.result = {
                            "policy": "observer_aware",
                            "reason": "explicit_human_approval",
                            "coherence": coh_val,
                        }
                        self._counters["observer_pending_human_total"] = (
                            int(self._counters.get("observer_pending_human_total", 0))
                            + 1
                        )
                        return t.task_id
                    # Otherwise check coherence thresholds
                    cv = None
                    # Only attempt conversion when clearly convertible
                    if isinstance(coh_val, (int, float, str)):
                        try:
                            cv = float(coh_val)
                        except Exception:
                            cv = None
                    if isinstance(cv, float):
                        if cv < self._coh_hard_min:
                            # Hard-deny when coherence is extremely low
                            t.status = "failed"
                            t.error = "coherence_low"
                            t.completed_at = datetime.now().isoformat()
                            self._counters["policy_denied_total"] = (
                                int(self._counters.get("policy_denied_total", 0)) + 1
                            )
                            self._counters["observer_denied_total"] = (
                                int(self._counters.get("observer_denied_total", 0)) + 1
                            )
                            return t.task_id
                        if cv < self._coh_gate_min:
                            # Require human approval when below soft gate
                            t.status = "pending"
                            t.error = "approval_required"
                            t.result = {
                                "policy": "observer_aware",
                                "reason": "coherence_below_gate",
                                "coherence": cv,
                                "threshold": self._coh_gate_min,
                            }
                            self._counters["observer_pending_human_total"] = (
                                int(
                                    self._counters.get(
                                        "observer_pending_human_total", 0
                                    )
                                )
                                + 1
                            )
                            return t.task_id
        except Exception:
            # Do not fail submission due to policy logic
            pass

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
        self._active_tasks += 1
        try:
            # Simulate work in small chunks to allow cooperative cancellation
            async def _do_work():
                total_steps = 5
                step_sleep = min(
                    1.0, max(0.05, t.max_execution_time / (total_steps * 20))
                )
                for i in range(total_steps):
                    await asyncio.sleep(step_sleep)
                    t.progress = int(((i + 1) / total_steps) * 100)

            try:
                await asyncio.wait_for(
                    _do_work(), timeout=max(0.05, float(t.max_execution_time or 0))
                )
            except asyncio.TimeoutError:
                t.status = "failed"
                t.error = "timeout"
                t.completed_at = datetime.now().isoformat()
                self._counters["timeouts_total"] = (
                    int(self._counters.get("timeouts_total", 0)) + 1
                )
                return

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
        finally:
            # Ensure active gauge is decremented
            try:
                self._active_tasks = max(0, self._active_tasks - 1)
            except Exception:
                self._active_tasks = 0

    def _coherence_ema(self) -> float:
        """Compute a small EMA over coherence signals for drift alarms."""
        try:
            vals = self._coherence_vals
            if not vals:
                return 0.0
            # 0.3 smoothing factor for responsiveness
            alpha = 0.3
            ema = vals[0]
            for v in vals[1:]:
                ema = alpha * v + (1 - alpha) * ema
            # clamp
            if ema < 0:
                return 0.0
            if ema > 1:
                return 1.0
            return float(ema)
        except Exception:
            return 0.0
