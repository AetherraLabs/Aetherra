#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[KLM] Kernel Loadable Module Manager
====================================

Lightweight in-memory module manager with a small control-plane via the
service registry. This provides a safe contract for loading/unloading/reloading
logical modules (not Python packages) and basic metrics/audit counters.

Intended to evolve alongside HMR and the kernel event bus.
"""

# Standard library imports
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ModuleRecord:
    name: str
    version: str = ""
    status: str = "inactive"  # inactive | active | disabled | failed
    loaded_at: datetime | None = None
    last_updated: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ModuleManager:
    """Minimal, safe module manager with a clear contract."""

    def __init__(self, service_registry):
        self.registry = service_registry
        self._modules: dict[str, ModuleRecord] = {}
        # Metrics counters (monotonic)
        self._metrics = {
            "loads_total": 0,
            "reloads_total": 0,
            "rollbacks_total": 0,
        }
        # Concurrency guard
        self._lock = asyncio.Lock()

    def _guardian_requester(self, spec: dict[str, Any] | None = None) -> str:
        spec = spec or {}
        requester = spec.get("guardian_requester") or spec.get("requester")
        return str(requester or "module_manager").strip() or "module_manager"

    def _guardian_capability_checker(self, requester: str, capability: str) -> bool:
        if requester == "module_manager" and capability in {
            "module:load",
            "module:reload",
            "module:unload",
            "module:rollback",
        }:
            return True
        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_preflight(
        self,
        *,
        requester: str,
        action: str,
        module_name: str,
        purpose: str,
        capability: str,
        metadata: dict[str, Any],
    ) -> None:
        from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="module_manager",
                action=action,
                target="module_manager:module",
                purpose=purpose,
                capabilities=(capability,),
                evidence=(f"module_name:{module_name}",),
                reversible=True,
                rollback_plan="reload, unload, or roll back the module to the previous logical state",
                metadata=metadata,
            ),
            capability_checker=self._guardian_capability_checker,
        )
        if decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            raise PermissionError(
                f"Guardian denied module manager action {action}: {decision.reason}"
            )

    # ---------------- Control-plane API ----------------
    async def load_module(
        self, name: str, spec: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        n = str(name).strip()
        if not n:
            return {"ok": False, "error": "invalid_name"}
        spec_data = spec if isinstance(spec, dict) else {}
        self._guardian_preflight(
            requester=self._guardian_requester(spec_data),
            action="module_manager.load",
            module_name=n,
            purpose=f"Load module {n}",
            capability="module:load",
            metadata={
                "module_name": n,
                "spec_keys": tuple(sorted(str(key) for key in spec_data)),
                "has_version": "version" in spec_data,
            },
        )
        async with self._lock:
            rec = self._modules.get(n)
            now = datetime.now()
            if rec is None:
                rec = ModuleRecord(name=n)
                self._modules[n] = rec
            rec.status = "active"
            rec.loaded_at = rec.loaded_at or now
            rec.last_updated = now
            if spec_data:
                rec.version = str(spec_data.get("version", rec.version) or rec.version)
                rec.metadata.update({k: v for k, v in spec_data.items() if k != "version"})
            self._metrics["loads_total"] += 1
        # Broadcast best-effort
        try:
            await self._broadcast("module.loaded", {"name": n, "version": rec.version})
        except Exception as exc:
            logger.debug("KLM load broadcast failed for %s: %s", n, exc)
        return {"ok": True, "module": self._to_dict(rec)}

    async def unload_module(self, name: str) -> dict[str, Any]:
        n = str(name).strip()
        if not n:
            return {"ok": False, "error": "invalid_name"}
        self._guardian_preflight(
            requester="module_manager",
            action="module_manager.unload",
            module_name=n,
            purpose=f"Unload module {n}",
            capability="module:unload",
            metadata={"module_name": n},
        )
        async with self._lock:
            rec = self._modules.get(n)
            if rec is None:
                return {"ok": False, "error": "not_found"}
            rec.status = "disabled"
            rec.last_updated = datetime.now()
        try:
            await self._broadcast("module.unloaded", {"name": n})
        except Exception as exc:
            logger.debug("KLM unload broadcast failed for %s: %s", n, exc)
        return {"ok": True}

    async def rollback_module(self, name: str) -> dict[str, Any]:
        """Record a logical rollback for a module (metrics-only placeholder).

        This simulates a rollback action in environments where a concrete
        rollback artifact isn't tracked yet. It increments the rollback
        counter and marks the module as active (best-effort no-op).
        """
        n = str(name).strip()
        if not n:
            return {"ok": False, "error": "invalid_name"}
        self._guardian_preflight(
            requester="module_manager",
            action="module_manager.rollback",
            module_name=n,
            purpose=f"Roll back module {n}",
            capability="module:rollback",
            metadata={"module_name": n},
        )
        async with self._lock:
            rec = self._modules.get(n)
            if rec is None:
                # Create an entry to reflect control-plane action
                rec = ModuleRecord(name=n, status="active", loaded_at=datetime.now())
                self._modules[n] = rec
            else:
                rec.status = "active"
            rec.last_updated = datetime.now()
            self._metrics["rollbacks_total"] += 1
        try:
            await self._broadcast("module.rolled_back", {"name": n})
        except Exception as exc:
            logger.debug("KLM rollback broadcast failed for %s: %s", n, exc)
        return {"ok": True, "module": self._to_dict(rec)}

    async def reload_module(
        self, name: str, spec: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        n = str(name).strip()
        if not n:
            return {"ok": False, "error": "invalid_name"}
        spec_data = spec if isinstance(spec, dict) else {}
        self._guardian_preflight(
            requester=self._guardian_requester(spec_data),
            action="module_manager.reload",
            module_name=n,
            purpose=f"Reload module {n}",
            capability="module:reload",
            metadata={
                "module_name": n,
                "spec_keys": tuple(sorted(str(key) for key in spec_data)),
                "has_version": "version" in spec_data,
            },
        )
        async with self._lock:
            rec = self._modules.get(n)
            if rec is None:
                # Implicit load when missing
                rec = ModuleRecord(name=n)
                self._modules[n] = rec
                self._metrics["loads_total"] += 1
            # Minimal canary: mark updating, then active
            rec.status = "active"
            rec.loaded_at = rec.loaded_at or datetime.now()
            if spec_data:
                rec.version = str(spec_data.get("version", rec.version) or rec.version)
                rec.metadata.update({k: v for k, v in spec_data.items() if k != "version"})
            rec.last_updated = datetime.now()
            self._metrics["reloads_total"] += 1
        try:
            await self._broadcast(
                "module.reloaded", {"name": n, "version": rec.version}
            )
        except Exception as exc:
            logger.debug("KLM reload broadcast failed for %s: %s", n, exc)
        return {"ok": True, "module": self._to_dict(rec)}

    async def list_modules(self) -> dict[str, Any]:
        async with self._lock:
            mods = [self._to_dict(m) for m in self._modules.values()]
        return {"ok": True, "modules": mods}

    # ---------------- Registry messaging surface ----------------
    async def handle_message(self, message_type: str, data: Any) -> Any:
        mt = (message_type or "").lower()
        payload = data or {}
        if mt.endswith("module.load"):
            return await self.load_module(payload.get("name", ""), payload.get("spec"))
        if mt.endswith("module.unload"):
            return await self.unload_module(payload.get("name", ""))
        if mt.endswith("module.reload"):
            return await self.reload_module(
                payload.get("name", ""), payload.get("spec")
            )
        if mt.endswith("module.rollback"):
            return await self.rollback_module(payload.get("name", ""))
        if mt.endswith("module.list") or mt.endswith("module.status"):
            return await self.list_modules()
        return {"ok": False, "error": "unknown_message"}

    # ---------------- Observability ----------------
    def get_metrics(self) -> dict[str, Any]:
        # Active modules count and per-module activity
        actives = 0
        per_mod = {}
        for n, rec in self._modules.items():
            if rec.status == "active":
                actives += 1
                per_mod[n] = 1
        return {
            **self._metrics.copy(),
            "active_modules": actives,
            "per_module_active": per_mod,
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "modules": [self._to_dict(m) for m in self._modules.values()],
            "metrics": self.get_metrics(),
        }

    async def shutdown(self):
        # Nothing to cleanup yet
        return True

    # ---------------- Internals ----------------
    async def _broadcast(self, msg_type: str, data: dict[str, Any]):
        if not self.registry:
            return
        try:
            await self.registry.broadcast_message(f"klm.{msg_type}", data)
        except Exception as exc:
            logger.debug("KLM broadcast failed for %s: %s", msg_type, exc)

    @staticmethod
    def _to_dict(rec: ModuleRecord) -> dict[str, Any]:
        return {
            "name": rec.name,
            "version": rec.version,
            "status": rec.status,
            "loaded_at": rec.loaded_at.isoformat() if rec.loaded_at else None,
            "last_updated": rec.last_updated.isoformat() if rec.last_updated else None,
            "metadata": rec.metadata.copy(),
        }


# Global singleton factory
_module_manager_instance: ModuleManager | None = None


async def get_module_manager(service_registry) -> ModuleManager:
    global _module_manager_instance
    if _module_manager_instance is None:
        _module_manager_instance = ModuleManager(service_registry)
    return _module_manager_instance
