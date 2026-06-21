# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Path policy helpers for Maintenance-generated reports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


APPROVED_GENERATED_REPORT_DIRS: tuple[str, ...] = (
    "artifacts/maintenance",
    "data/artifacts/maintenance",
    "reports/maintenance",
)

APPROVED_DURABLE_DOC_DIRS: tuple[str, ...] = (
    "docs/reports",
    "docs/prepack",
    "docs/archive/root-reports",
)

APPROVED_DURABLE_DOC_FILES: tuple[str, ...] = (
    "docs/STUB_INVENTORY.json",
)


@dataclass(frozen=True, slots=True)
class MaintenancePathPolicyResult:
    """Result of classifying a Maintenance report destination."""

    allowed: bool
    category: str
    reason: str
    normalized_path: str


def normalize_project_relative_path(path: str | Path) -> str:
    """Normalize a path for stable policy comparison."""

    raw = str(path).replace("\\", "/").strip()
    while raw.startswith("./"):
        raw = raw[2:]
    return raw.strip("/")


def normalize_path_relative_to_root(path: str | Path, project_root: str | Path) -> str:
    """Normalize a path relative to a project root when possible."""

    target = Path(path)
    root = Path(project_root)
    try:
        if target.is_absolute():
            target = target.resolve().relative_to(root.resolve())
    except ValueError:
        pass
    return normalize_project_relative_path(target)


def classify_report_destination(path: str | Path) -> MaintenancePathPolicyResult:
    """Classify whether a generated Maintenance report destination is allowed.

    Generated reports should go to ignored artifact/report directories. Durable
    records may live under approved docs report/archive paths when intentionally
    promoted. Root-level generated reports are blocked.
    """

    normalized = normalize_project_relative_path(path)
    if not normalized:
        return MaintenancePathPolicyResult(
            allowed=False,
            category="invalid",
            reason="empty_report_path",
            normalized_path=normalized,
        )

    if _is_under(normalized, APPROVED_GENERATED_REPORT_DIRS):
        return MaintenancePathPolicyResult(
            allowed=True,
            category="generated_output",
            reason="approved_generated_report_directory",
            normalized_path=normalized,
        )

    if _is_under(normalized, APPROVED_DURABLE_DOC_DIRS):
        return MaintenancePathPolicyResult(
            allowed=True,
            category="durable_docs_record",
            reason="approved_durable_docs_report_directory",
            normalized_path=normalized,
        )

    if normalized in APPROVED_DURABLE_DOC_FILES:
        return MaintenancePathPolicyResult(
            allowed=True,
            category="durable_docs_record",
            reason="approved_durable_docs_report_file",
            normalized_path=normalized,
        )

    if "/" not in normalized:
        return MaintenancePathPolicyResult(
            allowed=False,
            category="root_generated_report",
            reason="root_level_generated_reports_are_not_allowed",
            normalized_path=normalized,
        )

    return MaintenancePathPolicyResult(
        allowed=False,
        category="unapproved_destination",
        reason="report_destination_not_in_approved_maintenance_paths",
        normalized_path=normalized,
    )


def classify_report_destination_for_root(
    path: str | Path,
    project_root: str | Path,
) -> MaintenancePathPolicyResult:
    """Classify a report destination relative to a project root."""

    return classify_report_destination(
        normalize_path_relative_to_root(path=path, project_root=project_root)
    )


def require_allowed_report_destination(
    path: str | Path,
    project_root: str | Path,
) -> MaintenancePathPolicyResult:
    """Return policy details or raise ValueError for a blocked report destination."""

    result = classify_report_destination_for_root(path=path, project_root=project_root)
    if not result.allowed:
        raise ValueError(
            "Maintenance report destination is not approved: "
            f"{result.normalized_path} ({result.reason})"
        )
    return result


def _is_under(path: str, roots: tuple[str, ...]) -> bool:
    return any(path == root or path.startswith(f"{root}/") for root in roots)
