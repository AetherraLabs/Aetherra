"""Service-registry lookups (sync wrappers) extracted from monolith.

All functions are best-effort: they swallow exceptions and return None/{}.
They perform synchronous calls by spinning an event loop with asyncio.run.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import datetime as dt
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Singleton fallback memory engine instance (lazy init to prevent circular imports)
_fallback_quantum_engine: Any | None = None


def _get_fallback_quantum_engine() -> Any:
    """Get or create singleton fallback QuantumEnhancedMemoryEngine."""
    global _fallback_quantum_engine
    if _fallback_quantum_engine is None:
        try:
            # Aetherra imports
            from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
                QuantumEnhancedMemoryEngine,
            )

            _fallback_quantum_engine = QuantumEnhancedMemoryEngine()
        except Exception as exc:
            logger.debug(f"Failed to create fallback quantum engine: {exc}")
            return None
    return _fallback_quantum_engine


# Generic helper


def _run_coro(coro: Any) -> Any:
    """Run a coroutine from synchronous code safely.

    Handling:
    - Preferred path: `asyncio.run` when no loop is running.
    - If a loop is already running in this thread (e.g. inside Aetherra OS), we cannot block it.
      We submit the coroutine to that loop via `asyncio.create_task` and return None (best-effort)
      because synchronous waiting would deadlock. This avoids RuntimeWarning for un-awaited coro
      by actually creating the task.
    - Any exception returns None per best‑effort contract.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(coro)  # schedule fire-and-forget
                return None
            return loop.run_until_complete(coro)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("_run_coro fallback failed: %s", exc)
            return None
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("_run_coro failed: %s", exc)
        return None


async def _get_registry_async() -> Any:  # pragma: no cover - thin wrapper
    # Aetherra imports
    from aetherra_service_registry import get_service_registry

    return await get_service_registry()


def get_registry_status() -> dict[str, Any] | None:
    try:

        async def _go() -> Any:
            reg = await _get_registry_async()
            return reg.get_registry_status()

        r = _run_coro(_go())
        return r if isinstance(r, dict) else None
    except Exception as exc:  # pragma: no cover - best effort
        logger.debug("get_registry_status error: %s", exc)
        return None


def get_kernel_status() -> dict[str, Any] | None:
    try:
        # Prefer central Registry Daemon if configured and reachable
        try:
            from aetherra_registry_client import http_get_status
        except Exception:
            http_get_status = None

        if http_get_status is not None:
            st = http_get_status()
            if isinstance(st, dict):
                services = st.get("services") or {}
                kern = (
                    services.get("kernel_loop") if isinstance(services, dict) else None
                )
                if isinstance(kern, dict):
                    last = kern.get("last_heartbeat", 0.0)
                    status_str = str(kern.get("status") or "").lower()
                    now_ts = time.time()
                    age_sec_daemon = None
                    running = False
                    try:
                        age_sec_daemon = max(0.0, float(now_ts - float(last)))
                        running = age_sec_daemon <= 180.0
                    except Exception:
                        age_sec_daemon = None
                    if status_str in ("healthy",):
                        running = True
                    payload_daemon: dict[str, Any] = {
                        "running": bool(running),
                        "paused": False,
                        "uptime": 0,
                        "cycle_count": 0,
                        "plugin_invoke_timeout_sec": 30.0,
                        "backpressure_guard_pass": True,
                        "backpressure_guard_violations": [],
                        "night_schedule_guard_pass": True,
                        "metrics": {"_source": "registry_daemon"},
                        "queue_sizes": {
                            "high_priority": 0,
                            "normal_priority": 0,
                            "background": 0,
                        },
                        "queue_limits": {},
                        "plugin_cb_open": False,
                        "dlq_count": 0,
                        "hmr": {"fallback": True},
                        "inflight": {},
                        "_source": "registry_daemon",
                    }
                    if age_sec_daemon is not None:
                        payload_daemon["stale_sec"] = age_sec_daemon
                    return payload_daemon

        async def _go() -> Any:
            reg = await _get_registry_async()
            info = reg.get_service_info("kernel_loop")
            if not info or not info.instance:
                return None
            kern = info.instance
            if hasattr(kern, "get_status"):
                try:
                    return kern.get_status()
                except Exception as exc:  # pragma: no cover
                    logger.debug("kernel get_status failed: %s", exc)
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
        # Fallback path: attempt to infer kernel status from local metrics artifacts (dev-only)
        try:
            # Prefer root-level metrics file; fallback to data/
            candidates = [
                Path("aetherra_kernel_metrics.json"),
                Path("data") / "aetherra_kernel_metrics.json",
            ]
            for p in candidates:
                if p.exists():
                    try:
                        with p.open("r", encoding="utf-8") as f:
                            metrics = json.load(f)
                    except Exception as exc:  # pragma: no cover - defensive
                        logger.debug("kernel metrics file parse failed: %s", exc)
                        metrics = {}
                    # Determine staleness based on 'live_time' if present
                    live_iso = metrics.get("live_time") or metrics.get("shutdown_time")
                    file_age_sec: float | None = None
                    running = False
                    if isinstance(live_iso, str):
                        try:
                            ts = dt.datetime.fromisoformat(
                                live_iso.replace("Z", "+00:00")
                            )
                            if ts.tzinfo is None:
                                ts = ts.replace(tzinfo=dt.UTC)
                            file_age_sec = (
                                dt.datetime.now(dt.UTC) - ts
                            ).total_seconds()
                            # Consider ONLINE if metrics were flushed recently (<= 180s)
                            running = file_age_sec <= 180.0
                        except Exception as exc:  # pragma: no cover
                            logger.debug(
                                "kernel metrics timestamp parse failed: %s", exc
                            )
                    # Minimal compatible payload mirroring kernel.get_status keys
                    file_payload: dict[str, Any] = {
                        "running": running,
                        "paused": False,
                        "uptime": 0,
                        "cycle_count": metrics.get("cycle_count", 0),
                        "plugin_invoke_timeout_sec": metrics.get(
                            "plugin_invoke_timeout_sec", 30.0
                        ),
                        "backpressure_guard_pass": True,
                        "backpressure_guard_violations": [],
                        "night_schedule_guard_pass": True,
                        "metrics": metrics,
                        "queue_sizes": {
                            "high_priority": 0,
                            "normal_priority": 0,
                            "background": 0,
                        },
                        "queue_limits": {},
                        "plugin_cb_open": False,
                        "dlq_count": 0,
                        "hmr": {"fallback": True},
                        "inflight": {},
                        "_source": "file_fallback",
                    }
                    if file_age_sec is not None:
                        file_payload["stale_sec"] = file_age_sec
                    return file_payload
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("kernel status file fallback error: %s", exc)
        return None
    except Exception as exc:  # pragma: no cover
        logger.debug("get_kernel_status error: %s", exc)
        return None


def get_orchestrator_status() -> dict[str, Any] | None:
    try:

        async def _go() -> Any:
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return None
            eng = info.instance
            orch = getattr(eng, "agent_orchestrator", None)
            if orch and hasattr(orch, "get_system_status"):
                try:
                    return orch.get_system_status()
                except Exception as exc:  # pragma: no cover
                    logger.debug("orch.get_system_status failed: %s", exc)
                    return None
            if hasattr(eng, "get_system_status"):
                try:
                    st = await eng.get_system_status()
                    if isinstance(st, dict):
                        return st.get("agent_orchestrator")
                except Exception as exc:
                    logger.debug("eng.get_system_status failed: %s", exc)
                    return None
            return None

        r = _run_coro(_go())
        return r if isinstance(r, dict) else None
    except Exception as exc:
        logger.debug("get_orchestrator_status error: %s", exc)
        return None


def submit_agent_task(
    name: str,
    description: str,
    required_capabilities: list[str] | None = None,
    input_data: dict[str, Any] | None = None,
    priority: str = "normal",
    max_execution_time: int = 300,
) -> str | None:
    """Submit a task to the agent orchestrator. Returns task_id on success."""
    try:
        from Aetherra.aetherra_core.agents.agent_orchestrator import Task, TaskPriority

        async def _go() -> str | None:
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return None
            eng = info.instance
            orch = getattr(eng, "agent_orchestrator", None)
            if not orch or not hasattr(orch, "submit_task"):
                return None

            # Convert priority string to enum
            priority_map = {
                "low": TaskPriority.LOW,
                "normal": TaskPriority.NORMAL,
                "high": TaskPriority.HIGH,
                "critical": TaskPriority.CRITICAL,
            }
            task_priority = priority_map.get(priority.lower(), TaskPriority.NORMAL)

            # Create task object (task_id will be auto-generated by orchestrator)
            task = Task(
                task_id="",  # Will be generated by orchestrator
                name=name,
                description=description,
                required_capabilities=required_capabilities or [],
                input_data=input_data or {},
                priority=task_priority,
                max_execution_time=max_execution_time,
            )

            try:
                return await orch.submit_task(task)
            except Exception as exc:  # pragma: no cover
                logger.debug("orch.submit_task failed: %s", exc)
                return None

        r = _run_coro(_go())
        return r if isinstance(r, str) else None
    except Exception as exc:
        logger.debug("submit_agent_task error: %s", exc)
        return None


def get_agent_task_status(task_id: str) -> dict[str, Any] | None:
    """Get the status of a specific task from the orchestrator."""
    try:

        async def _go() -> dict[str, Any] | None:
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return None
            eng = info.instance
            orch = getattr(eng, "agent_orchestrator", None)
            if not orch or not hasattr(orch, "get_task_status"):
                return None

            try:
                return orch.get_task_status(task_id)
            except Exception as exc:  # pragma: no cover
                logger.debug("orch.get_task_status failed: %s", exc)
                return None

        r = _run_coro(_go())
        return r if isinstance(r, dict) else None
    except Exception as exc:
        logger.debug("get_agent_task_status error: %s", exc)
        return None


def get_agent_task_list(
    limit: int = 50, include_completed: bool = True
) -> list[dict[str, Any]]:
    """Get a list of recent tasks from the orchestrator."""
    try:

        async def _go() -> list[dict[str, Any]]:
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return []
            eng = info.instance
            orch = getattr(eng, "agent_orchestrator", None)
            if not orch or not hasattr(orch, "tasks"):
                return []

            try:
                # Get all tasks from orchestrator
                all_tasks = []
                tasks_dict = getattr(orch, "tasks", {})

                for _task_id, task in tasks_dict.items():
                    # Convert task dataclass to dict
                    task_dict = {
                        "task_id": task.task_id,
                        "name": task.name,
                        "description": task.description,
                        "status": task.status.value
                        if hasattr(task.status, "value")
                        else str(task.status),
                        "assigned_agent": task.assigned_agent,
                        "created_at": task.created_at.isoformat()
                        if hasattr(task.created_at, "isoformat")
                        else str(task.created_at),
                        "started_at": task.started_at.isoformat()
                        if task.started_at and hasattr(task.started_at, "isoformat")
                        else None,
                        "completed_at": task.completed_at.isoformat()
                        if task.completed_at and hasattr(task.completed_at, "isoformat")
                        else None,
                        # Convenience field for UI: when was this task performed?
                        # Prefer completed_at, then started_at, else created_at
                        "performed_at": (
                            (
                                task.completed_at.isoformat()
                                if task.completed_at
                                and hasattr(task.completed_at, "isoformat")
                                else str(task.completed_at)
                            )
                            if getattr(task, "completed_at", None)
                            else (
                                task.started_at.isoformat()
                                if task.started_at
                                and hasattr(task.started_at, "isoformat")
                                else (
                                    task.created_at.isoformat()
                                    if hasattr(task.created_at, "isoformat")
                                    else str(task.created_at)
                                )
                            )
                        ),
                        # Duration in seconds if available
                        "duration_secs": (
                            (
                                (task.completed_at - task.started_at).total_seconds()
                                if task.completed_at and task.started_at
                                else None
                            )
                            if getattr(task, "started_at", None) is not None
                            else None
                        ),
                    }

                    # Filter completed tasks if requested
                    if include_completed or task_dict["status"] not in [
                        "completed",
                        "failed",
                        "cancelled",
                    ]:
                        all_tasks.append(task_dict)

                # Sort by created_at (most recent first)
                all_tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)

                # Limit results
                return all_tasks[:limit]

            except Exception as exc:  # pragma: no cover
                logger.debug("Failed to get task list: %s", exc)
                return []

        r = _run_coro(_go())
        return r if isinstance(r, list) else []
    except Exception as exc:
        logger.debug("get_agent_task_list error: %s", exc)
        return []


def get_memory_quantum_status() -> dict[str, Any]:
    try:

        async def _go() -> Any:
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return None
            eng = info.instance
            ms = getattr(eng, "memory_system", None)
            if ms is None:
                return None
            if hasattr(ms, "get_quantum_status"):
                try:
                    return {"enabled": True, **(await ms.get_quantum_status())}
                except Exception as exc:
                    logger.debug("memory_system.get_quantum_status failed: %s", exc)
            inner = getattr(ms, "engine", None)
            if inner is not None and hasattr(inner, "get_status"):
                try:
                    st = inner.get_status()
                    if isinstance(st, dict):
                        return {"enabled": True, **st}
                except Exception as exc:
                    logger.debug("memory inner.get_status failed: %s", exc)
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception as exc:
        logger.debug("get_memory_quantum_status error: %s", exc)
    try:  # fallback
        q = _get_fallback_quantum_engine()
        if q is None:
            return {"enabled": False}
        st = q.get_status()
        if isinstance(st, dict):
            st.update({"enabled": False, "ephemeral": True})
            return st
        logger.error(
            "QuantumEnhancedMemoryEngine.get_status() did not return dict! Returning minimal fallback."
        )
        return {"enabled": False, "ephemeral": True}
    except Exception as exc:  # pragma: no cover  # noqa: RET506
        logger.debug("quantum fallback status error: %s", exc)
        return {"enabled": False}


def get_memory_audit() -> dict[str, Any]:
    try:

        async def _go() -> Any:
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return None
            eng = info.instance
            ms = getattr(eng, "memory_system", None)
            if ms is None:
                return None
            inner = getattr(ms, "engine", None)
            target = inner or ms
            if hasattr(target, "audit_branch_dag"):
                try:
                    audit = target.audit_branch_dag()
                    if isinstance(audit, dict):
                        return {"enabled": True, "audit": audit}
                except Exception as exc:
                    logger.debug("audit_branch_dag failed: %s", exc)
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception as exc:
        logger.debug("get_memory_audit error: %s", exc)
    try:  # fallback
        q = _get_fallback_quantum_engine()
        if q is None:
            return {"enabled": False}
        try:
            audit = q.audit_branch_dag()
        except Exception as inner_exc:  # pragma: no cover
            logger.debug("quantum audit fallback failed: %s", inner_exc)
            audit = {}
        return {"enabled": False, "ephemeral": True, "audit": audit}
    except Exception as exc:  # pragma: no cover
        logger.debug("quantum audit engine import failed: %s", exc)
        return {"enabled": False}


def get_storm_metrics() -> dict[str, Any]:
    """Fetch STORM metrics snapshot from memory system.

    Returns dict with STORM metrics or empty dict if unavailable.
    STORM is feature-flagged and may not be enabled.
    """
    try:

        async def _go() -> Any:
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return None
            eng = info.instance
            ms = getattr(eng, "memory_system", None)
            if ms is None:
                return None
            # Access STORM engine via memory_system.engine._storm_engine
            engine = getattr(ms, "engine", None)
            if engine is None:
                return None
            storm_engine = getattr(engine, "_storm_engine", None)
            if storm_engine is None:
                return None
            # Get metrics snapshot from STORM engine
            if hasattr(storm_engine, "metrics") and hasattr(
                storm_engine.metrics, "snapshot"
            ):
                try:
                    snapshot = storm_engine.metrics.snapshot()
                    if isinstance(snapshot, dict):
                        return {"enabled": True, **snapshot}
                except Exception as exc:
                    logger.debug("storm metrics.snapshot failed: %s", exc)
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception as exc:
        logger.debug("get_storm_metrics error: %s", exc)
    return {"enabled": False}


def _generic_service_call(service_name: str, attr: str) -> dict[str, Any]:
    async def _go() -> Any:
        reg = await _get_registry_async()
        info = reg.get_service_info(service_name)
        if not info or not info.instance:
            return None
        inst = info.instance
        if hasattr(inst, attr):
            try:
                return getattr(inst, attr)()
            except Exception as exc:  # pragma: no cover
                logger.debug(
                    "service %s attr %s call failed: %s", service_name, attr, exc
                )
                return None
        return None

    r = _run_coro(_go())
    return r if isinstance(r, dict) else {}


def get_hmr_audit_counters() -> dict[str, Any]:
    return _generic_service_call("hmr_controller", "get_audit_counters")


def get_hmr_config_metrics() -> dict[str, Any]:
    return _generic_service_call("hmr_controller", "get_config_metrics")


def get_klm_metrics() -> dict[str, Any]:
    return _generic_service_call("module_manager", "get_metrics")


def get_klm_status() -> dict[str, Any]:
    return _generic_service_call("module_manager", "get_status")


def get_keb_metrics() -> dict[str, Any]:
    return _generic_service_call("event_bus", "get_metrics")


def get_keb_status() -> dict[str, Any]:
    # Prefer Registry Daemon status if available
    try:
        from aetherra_registry_client import http_get_status
    except Exception:
        http_get_status = None
    if http_get_status is not None:
        st = http_get_status()
        if isinstance(st, dict):
            services = st.get("services") or {}
            eb = services.get("event_bus") if isinstance(services, dict) else None
            if isinstance(eb, dict):
                # Enabled if present and recent heartbeat
                last = eb.get("last_heartbeat", 0.0)
                enabled = False
                try:
                    enabled = (time.time() - float(last)) <= 180.0
                except Exception:
                    enabled = False
                return {"enabled": enabled, "source": "registry_daemon"}
    return _generic_service_call("event_bus", "get_status")


def get_quantum_bridge_status() -> dict[str, Any]:
    return _generic_service_call("quantum_bridge", "get_status")


def get_service(service_name: str) -> Any:
    """Get a service instance by name from the registry."""
    try:

        async def _go() -> Any:
            reg = await _get_registry_async()
            info = reg.get_service_info(service_name)
            if not info or not info.instance:
                return None
            return info.instance

        return _run_coro(_go())
    except Exception as exc:
        logger.debug("get_service(%s) error: %s", service_name, exc)
        return None
