# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Runtime-facing Maintenance service facade."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .cycle import (
    MaintenanceCoordinator,
    MaintenanceDecision,
    MaintenanceEvidence,
    MaintenanceExecution,
    MaintenanceProposal,
    MaintenanceVerification,
)
from .store import MaintenanceRecordStore

logger = logging.getLogger(__name__)


MAINTENANCE_SERVICE_NAME = "maintenance_system"
MAINTENANCE_SERVICE_ALIASES = ("aetherra_maintenance",)


def maintenance_service_metadata() -> dict[str, Any]:
    """Return stable service metadata for registry registration."""

    return {
        "version": "1.0",
        "description": "Aetherra Maintenance coordination and outcome record service",
        "authority": "coordinate_route_record_outcome",
        "authority_boundaries": {
            "observe": "homeostasis",
            "diagnose": "self_improvement",
            "propose": "self_improvement",
            "approve": "guardian",
            "enforce": "security",
            "execute": "self_incorporation",
            "verify": "homeostasis",
            "record_outcome": "maintenance",
        },
        "endpoints": {
            "status": "/api/maintenance/status",
        },
        "guardian_requester": "service_registry",
    }


class MaintenanceService:
    """Registerable Maintenance service facade.

    The service owns coordinator lifecycle and optional persistence. It does not
    observe, diagnose, approve, enforce, execute, or verify on behalf of the
    systems that own those authorities.
    """

    def __init__(
        self,
        *,
        coordinator: MaintenanceCoordinator | None = None,
        record_store: MaintenanceRecordStore | None = None,
        autoload: bool = True,
        autosave: bool = True,
    ) -> None:
        self.coordinator = coordinator or MaintenanceCoordinator()
        self.record_store = record_store
        self.autosave = bool(autosave)
        self._loaded_records = 0
        self._last_persist_error: str | None = None

        if self.record_store is not None and autoload:
            self.load_records()

    @classmethod
    def with_default_store(
        cls,
        project_root: str | Path = ".",
        *,
        autoload: bool = True,
        autosave: bool = True,
    ) -> MaintenanceService:
        """Create a service with the default approved record store."""

        return cls(
            record_store=MaintenanceRecordStore.default(project_root),
            autoload=autoload,
            autosave=autosave,
        )

    def create_cycle(self, cycle_id: str | None = None):
        cycle = self.coordinator.create_cycle(cycle_id)
        self._persist_best_effort()
        return cycle

    def get_cycle(self, cycle_id: str):
        return self.coordinator.get_cycle(cycle_id)

    def route_proposal(
        self,
        proposal: MaintenanceProposal,
        *,
        diagnosis: MaintenanceEvidence,
        observations: list[MaintenanceEvidence] | None = None,
        guardian_decision: MaintenanceDecision | None = None,
        security_allowed: bool | None = None,
        security_reason: str | None = None,
        cycle_id: str | None = None,
    ):
        cycle = self.coordinator.route_proposal(
            proposal,
            diagnosis=diagnosis,
            observations=observations,
            guardian_decision=guardian_decision,
            security_allowed=security_allowed,
            security_reason=security_reason,
            cycle_id=cycle_id,
        )
        self._persist_best_effort()
        return cycle

    def record_outcome(
        self,
        cycle_id: str,
        *,
        execution: MaintenanceExecution,
        verification: MaintenanceVerification | None = None,
        learning_record: dict[str, Any] | None = None,
    ):
        cycle = self.coordinator.record_outcome(
            cycle_id,
            execution=execution,
            verification=verification,
            learning_record=learning_record,
        )
        if cycle is not None:
            self._persist_best_effort()
        return cycle

    def export_records(self) -> list[dict[str, Any]]:
        return self.coordinator.export_records()

    def save_records(self) -> bool:
        """Persist coordinator records if a record store is configured."""

        if self.record_store is None:
            return False
        try:
            self.record_store.export_from(self.coordinator)
            self._last_persist_error = None
            return True
        except Exception as exc:
            self._last_persist_error = exc.__class__.__name__
            logger.debug("[MAINT] failed to persist maintenance records: %s", exc)
            return False

    def load_records(self) -> int:
        """Load persisted records into the coordinator if configured."""

        if self.record_store is None:
            self._loaded_records = 0
            return 0
        try:
            self._loaded_records = self.record_store.load_into(self.coordinator)
            self._last_persist_error = None
            return self._loaded_records
        except Exception as exc:
            self._loaded_records = 0
            self._last_persist_error = exc.__class__.__name__
            logger.debug("[MAINT] failed to load maintenance records: %s", exc)
            return 0

    def get_status(self) -> dict[str, Any]:
        status = self.coordinator.get_status()
        status["service"] = {
            "available": True,
            "record_store_configured": self.record_store is not None,
            "record_store_path": (
                str(self.record_store.file_path) if self.record_store else None
            ),
            "autosave": self.autosave,
            "loaded_records": self._loaded_records,
            "last_persist_error": self._last_persist_error,
        }
        return status

    def _persist_best_effort(self) -> None:
        if self.autosave:
            self.save_records()


async def register_maintenance_service(
    *,
    service: MaintenanceService | None = None,
    registry: Any | None = None,
    project_root: str | Path = ".",
    register_aliases: bool = True,
) -> MaintenanceService:
    """Register the Maintenance service with the service registry.

    The helper only registers the facade. It does not start maintenance actions.
    """

    instance = service or MaintenanceService.with_default_store(project_root)
    metadata = maintenance_service_metadata()

    if registry is not None and hasattr(registry, "register_service"):
        registered = await registry.register_service(
            MAINTENANCE_SERVICE_NAME,
            instance,
            metadata=metadata,
        )
    else:
        from aetherra_service_registry import register_service

        registered = await register_service(
            MAINTENANCE_SERVICE_NAME,
            instance,
            metadata=metadata,
        )

    if not registered:
        raise RuntimeError("failed_to_register_maintenance_service")

    if register_aliases:
        for alias in MAINTENANCE_SERVICE_ALIASES:
            try:
                alias_metadata = {**metadata, "alias_for": MAINTENANCE_SERVICE_NAME}
                if registry is not None and hasattr(registry, "register_service"):
                    await registry.register_service(
                        alias,
                        instance,
                        metadata=alias_metadata,
                    )
                else:
                    from aetherra_service_registry import register_service

                    await register_service(alias, instance, metadata=alias_metadata)
            except Exception as exc:
                logger.debug("[MAINT] failed to register alias %s: %s", alias, exc)

    return instance
