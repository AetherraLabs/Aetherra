"""Service-registry lookups (sync wrappers) extracted from monolith.

All functions are best-effort: they swallow exceptions and return None/{}.
They perform synchronous calls by spinning an event loop with asyncio.run.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Generic helper


def _run_coro(coro):
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


async def _get_registry_async():  # pragma: no cover - thin wrapper
    from aetherra_service_registry import get_service_registry  # type: ignore

    return await get_service_registry()


def get_registry_status() -> dict[str, Any] | None:
    try:

        async def _go():
            reg = await _get_registry_async()
            return reg.get_registry_status()

        r = _run_coro(_go())
        return r if isinstance(r, dict) else None
    except Exception as exc:  # pragma: no cover - best effort
        logger.debug("get_registry_status error: %s", exc)
        return None


def get_kernel_status() -> dict[str, Any] | None:
    try:

        async def _go():
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
        return r if isinstance(r, dict) else None
    except Exception as exc:  # pragma: no cover
        logger.debug("get_kernel_status error: %s", exc)
        return None


def get_orchestrator_status() -> dict[str, Any] | None:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("aetherra_engine")
            if not info or not info.instance:
                return None
            eng = info.instance
            orch = getattr(eng, "agent_orchestrator", None)
            if orch and hasattr(orch, "get_system_status"):
                try:
                    return orch.get_system_status()  # type: ignore[call-arg]
                except Exception as exc:  # pragma: no cover
                    logger.debug("orch.get_system_status failed: %s", exc)
                    return None
            if hasattr(eng, "get_system_status"):
                try:
                    st = await eng.get_system_status()  # type: ignore[attr-defined]
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


def get_memory_quantum_status() -> dict[str, Any]:
    try:

        async def _go():
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
                    return {"enabled": True, **(await ms.get_quantum_status())}  # type: ignore
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
    try:  # fallback ephemeral
        from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
            QuantumEnhancedMemoryEngine,
        )

        q = QuantumEnhancedMemoryEngine()
        st = q.get_status()
        if not isinstance(st, dict):
            st = {}
        st.update({"enabled": False, "ephemeral": True})
        return st
    except Exception as exc:  # pragma: no cover
        logger.debug("quantum fallback status error: %s", exc)
        return {"enabled": False}


def get_memory_audit() -> dict[str, Any]:
    try:

        async def _go():
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
                    audit = target.audit_branch_dag()  # type: ignore[attr-defined]
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
        from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
            QuantumEnhancedMemoryEngine,
        )

        q = QuantumEnhancedMemoryEngine()
        try:
            audit = q.audit_branch_dag()
        except Exception as inner_exc:  # pragma: no cover
            logger.debug("quantum audit fallback failed: %s", inner_exc)
            audit = {}
        return {"enabled": False, "ephemeral": True, "audit": audit}
    except Exception as exc:  # pragma: no cover
        logger.debug("quantum audit engine import failed: %s", exc)
        return {"enabled": False}


def _generic_service_call(service_name: str, attr: str) -> dict[str, Any]:
    async def _go():
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
    return _generic_service_call("event_bus", "get_status")


def get_quantum_bridge_status() -> dict[str, Any]:
    return _generic_service_call("quantum_bridge", "get_status")


def get_service(service_name: str):
    """Get a service instance by name from the registry."""
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info(service_name)
            if not info or not info.instance:
                return None
            return info.instance

        return _run_coro(_go())
    except Exception as exc:
        logger.debug("get_service(%s) error: %s", service_name, exc)
        return None
