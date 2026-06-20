# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Maintenance loop contracts and lightweight coordination helpers."""

from .cycle import (
    AUTHORITY_OWNERSHIP,
    FAILURE_HANDLING,
    MaintenanceCycle,
    MaintenanceCoordinator,
    MaintenanceCycleStatus,
    MaintenanceDecision,
    MaintenanceEvidence,
    MaintenanceEvent,
    MaintenanceExecution,
    MaintenanceProposal,
    MaintenanceVerification,
    get_maintenance_contract,
    get_maintenance_loop,
)
from .paths import (
    APPROVED_DURABLE_DOC_DIRS,
    APPROVED_DURABLE_DOC_FILES,
    APPROVED_GENERATED_REPORT_DIRS,
    MaintenancePathPolicyResult,
    classify_report_destination,
    classify_report_destination_for_root,
    normalize_path_relative_to_root,
    normalize_project_relative_path,
    require_allowed_report_destination,
)
from .store import DEFAULT_RECORD_PATH, MaintenanceRecordStore
from .service import (
    MAINTENANCE_SERVICE_ALIASES,
    MAINTENANCE_SERVICE_NAME,
    MaintenanceService,
    maintenance_service_metadata,
    register_maintenance_service,
)

__all__ = [
    "AUTHORITY_OWNERSHIP",
    "FAILURE_HANDLING",
    "MaintenanceCycle",
    "MaintenanceCoordinator",
    "MaintenanceCycleStatus",
    "MaintenanceDecision",
    "MaintenanceEvidence",
    "MaintenanceEvent",
    "MaintenanceExecution",
    "MaintenanceProposal",
    "MaintenanceVerification",
    "get_maintenance_contract",
    "get_maintenance_loop",
    "APPROVED_DURABLE_DOC_DIRS",
    "APPROVED_DURABLE_DOC_FILES",
    "APPROVED_GENERATED_REPORT_DIRS",
    "MaintenancePathPolicyResult",
    "classify_report_destination",
    "classify_report_destination_for_root",
    "normalize_path_relative_to_root",
    "normalize_project_relative_path",
    "require_allowed_report_destination",
    "DEFAULT_RECORD_PATH",
    "MAINTENANCE_SERVICE_ALIASES",
    "MAINTENANCE_SERVICE_NAME",
    "MaintenanceRecordStore",
    "MaintenanceService",
    "maintenance_service_metadata",
    "register_maintenance_service",
]
