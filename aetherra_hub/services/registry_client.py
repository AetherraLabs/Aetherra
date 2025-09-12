"""Service-registry lookups (sync wrappers) extracted from monolith.

All functions are best-effort: they swallow exceptions and return None/{}.
They perform synchronous calls by spinning an event loop with asyncio.run.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

# Generic helper


def _run_coro(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:  # already running loop
        loop = asyncio.get_event_loop()
        if loop.is_running():  # fallback: create temp loop in thread not needed here
            # In an active loop, we avoid nested run; return None for safety.
            return None
        return loop.run_until_complete(coro)
    except Exception:
        return None


async def _get_registry_async():  # pragma: no cover - thin wrapper
    from aetherra_service_registry import get_service_registry  # type: ignore

    return await get_service_registry()


def get_registry_status() -> Optional[Dict[str, Any]]:
    try:

        async def _go():
            reg = await _get_registry_async()
            return reg.get_registry_status()

        r = _run_coro(_go())
        return r if isinstance(r, dict) else None
    except Exception:
        return None


def get_kernel_status() -> Optional[Dict[str, Any]]:
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
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        return r if isinstance(r, dict) else None
    except Exception:
        return None


def get_orchestrator_status() -> Optional[Dict[str, Any]]:
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
                except Exception:
                    return None
            if hasattr(eng, "get_system_status"):
                try:
                    st = await eng.get_system_status()  # type: ignore[attr-defined]
                    if isinstance(st, dict):
                        return st.get("agent_orchestrator")
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        return r if isinstance(r, dict) else None
    except Exception:
        return None


def get_memory_quantum_status() -> Dict[str, Any]:
    # service registry path
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
                except Exception:
                    pass
            inner = getattr(ms, "engine", None)
            if inner is not None and hasattr(inner, "get_status"):
                try:
                    st = inner.get_status()
                    if isinstance(st, dict):
                        return {"enabled": True, **st}
                except Exception:
                    pass
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    # fallback ephemeral
    try:  # pragma: no cover - optional dependency heavy
        from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
            QuantumEnhancedMemoryEngine as _Q,
        )

        q = _Q()
        st = q.get_status()
        if not isinstance(st, dict):
            st = {}
        st.update({"enabled": False, "ephemeral": True})
        return st
    except Exception:
        return {"enabled": False}


def get_memory_audit() -> Dict[str, Any]:
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
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    # fallback
    try:  # pragma: no cover - optional heavy
        from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
            QuantumEnhancedMemoryEngine as _Q,
        )

        q = _Q()
        try:
            audit = q.audit_branch_dag()
        except Exception:
            audit = {}
        return {"enabled": False, "ephemeral": True, "audit": audit}
    except Exception:
        return {"enabled": False}


def get_hmr_audit_counters() -> Dict[str, Any]:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("hmr_controller")
            if not info or not info.instance:
                return None
            inst = info.instance
            if hasattr(inst, "get_audit_counters"):
                try:
                    return inst.get_audit_counters()
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return {}


def get_hmr_config_metrics() -> Dict[str, Any]:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("hmr_controller")
            if not info or not info.instance:
                return None
            inst = info.instance
            if hasattr(inst, "get_config_metrics"):
                try:
                    return inst.get_config_metrics()
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return {}


def get_klm_metrics() -> Dict[str, Any]:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("module_manager")
            if not info or not info.instance:
                return None
            inst = info.instance
            if hasattr(inst, "get_metrics"):
                try:
                    return inst.get_metrics()
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return {}


def get_klm_status() -> Dict[str, Any]:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("module_manager")
            if not info or not info.instance:
                return None
            inst = info.instance
            if hasattr(inst, "get_status"):
                try:
                    return inst.get_status()
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return {}


def get_keb_metrics() -> Dict[str, Any]:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("event_bus")
            if not info or not info.instance:
                return None
            inst = info.instance
            if hasattr(inst, "get_metrics"):
                try:
                    return inst.get_metrics()
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return {}


def get_keb_status() -> Dict[str, Any]:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("event_bus")
            if not info or not info.instance:
                return None
            inst = info.instance
            if hasattr(inst, "get_status"):
                try:
                    return inst.get_status()
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return {}


def get_quantum_bridge_status() -> Dict[str, Any]:
    try:

        async def _go():
            reg = await _get_registry_async()
            info = reg.get_service_info("quantum_bridge")
            if not info or not info.instance:
                return None
            inst = info.instance
            if hasattr(inst, "get_status"):
                try:
                    return inst.get_status()
                except Exception:
                    return None
            return None

        r = _run_coro(_go())
        if isinstance(r, dict):
            return r
    except Exception:
        pass
    return {}
