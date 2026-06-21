# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Persistence helpers for Maintenance cycle records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .cycle import MaintenanceCoordinator
from .paths import require_allowed_report_destination


DEFAULT_RECORD_PATH = Path("artifacts/maintenance/maintenance_cycles.jsonl")


@dataclass(frozen=True, slots=True)
class MaintenanceRecordStore:
    """JSONL record store for Maintenance cycle exports.

    The store persists coordinator records only. It does not execute maintenance
    actions or approve state changes.
    """

    file_path: Path
    project_root: Path

    @classmethod
    def default(cls, project_root: str | Path = ".") -> MaintenanceRecordStore:
        root = Path(project_root)
        return cls(file_path=root / DEFAULT_RECORD_PATH, project_root=root)

    def __post_init__(self) -> None:
        require_allowed_report_destination(self.file_path, self.project_root)

    def append_cycle_record(self, record: dict[str, Any]) -> None:
        """Append one cycle record as a JSON line."""

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    def append_cycle(self, coordinator: MaintenanceCoordinator, cycle_id: str) -> bool:
        """Append one coordinator cycle record by ID."""

        cycle = coordinator.get_cycle(cycle_id)
        if cycle is None:
            return False
        self.append_cycle_record(cycle.to_record())
        return True

    def replace_records(self, records: list[dict[str, Any]]) -> None:
        """Replace the store with the supplied records."""

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.file_path.with_suffix(f"{self.file_path.suffix}.tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
                handle.write("\n")
        tmp_path.replace(self.file_path)

    def export_from(self, coordinator: MaintenanceCoordinator) -> None:
        """Persist the coordinator's recent exported cycle records."""

        self.replace_records(coordinator.export_records())

    def load_records(self) -> list[dict[str, Any]]:
        """Load JSONL records from disk."""

        if not self.file_path.exists():
            return []

        records: list[dict[str, Any]] = []
        for line_number, line in enumerate(
            self.file_path.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid Maintenance record at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"Invalid Maintenance record at line {line_number}: expected object"
                )
            records.append(record)
        return records

    def load_into(self, coordinator: MaintenanceCoordinator) -> int:
        """Load records into a coordinator and return the count loaded."""

        count = 0
        for record in self.load_records():
            coordinator.load_cycle(record)
            count += 1
        return count
