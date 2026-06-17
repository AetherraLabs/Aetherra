#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Update known post-cleanup import paths after plugin and Lyrixa reorganization.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportUpdatePlan:
    file_path: Path
    content: str
    updates: int


def _hash_value(value: object) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance" and capability in {
        "maintenance:cleanup",
        "fs:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


class PostCleanupImportUpdater:
    def __init__(self, base_path: str | Path = "."):
        self.base_path = Path(base_path)
        self.specific_mappings = {
            # Plugins reorganization mappings.
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_orchestrator": "from Aetherra.plugins.agent_components.agent_orchestrator",
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_bridge": "from Aetherra.plugins.agent_components.agent_bridge",
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_discovery_and_integration": "from Aetherra.plugins.agent_components.agent_discovery_and_integration",
            r"from\s+Aetherra\.plugins\.agent_adapters\.agent_base": "from Aetherra.plugins.core.agent_base",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_orchestrator": "import Aetherra.plugins.agent_components.agent_orchestrator",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_bridge": "import Aetherra.plugins.agent_components.agent_bridge",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_discovery_and_integration": "import Aetherra.plugins.agent_components.agent_discovery_and_integration",
            r"import\s+Aetherra\.plugins\.agent_adapters\.agent_base": "import Aetherra.plugins.core.agent_base",
            # Lyrixa reorganization mappings.
            r"from\s+Aetherra\.lyrixa\.advanced_memory_integration": "from Aetherra.lyrixa.memory.advanced_memory_integration",
            r"from\s+Aetherra\.lyrixa\.agent_collaboration_manager": "from Aetherra.lyrixa.agents.agent_collaboration_manager",
            r"from\s+Aetherra\.lyrixa\.conversation_manager": "from Aetherra.lyrixa.agents.conversation_manager",
            r"from\s+Aetherra\.lyrixa\.enhanced_conversation_manager": "from Aetherra.lyrixa.agents.enhanced_conversation_manager",
            r"import\s+Aetherra\.lyrixa\.advanced_memory_integration": "import Aetherra.lyrixa.memory.advanced_memory_integration",
            r"import\s+Aetherra\.lyrixa\.agent_collaboration_manager": "import Aetherra.lyrixa.agents.agent_collaboration_manager",
            r"import\s+Aetherra\.lyrixa\.conversation_manager": "import Aetherra.lyrixa.agents.conversation_manager",
            r"import\s+Aetherra\.lyrixa\.enhanced_conversation_manager": "import Aetherra.lyrixa.agents.enhanced_conversation_manager",
            # Alternative import patterns without the Aetherra prefix.
            r"from\s+plugins\.agent_adapters\.agent_orchestrator": "from plugins.agent_components.agent_orchestrator",
            r"from\s+plugins\.agent_adapters\.agent_bridge": "from plugins.agent_components.agent_bridge",
            r"from\s+plugins\.agent_adapters\.agent_discovery_and_integration": "from plugins.agent_components.agent_discovery_and_integration",
            r"from\s+plugins\.agent_adapters\.agent_base": "from plugins.core.agent_base",
            r"from\s+lyrixa\.advanced_memory_integration": "from lyrixa.memory.advanced_memory_integration",
            r"from\s+lyrixa\.agent_collaboration_manager": "from lyrixa.agents.agent_collaboration_manager",
            r"from\s+lyrixa\.conversation_manager": "from lyrixa.agents.conversation_manager",
            r"from\s+lyrixa\.enhanced_conversation_manager": "from lyrixa.agents.enhanced_conversation_manager",
        }
        self.updated_files: list[dict[str, object]] = []
        self.updates_made = 0

    def _guardian_preflight_update(
        self,
        *,
        total_files: int,
        planned_updates: list[ImportUpdatePlan],
        report_path: Path,
    ):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        return evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="maintenance",
                action="maintenance.post_cleanup_import_update",
                target="maintenance:post_cleanup_imports",
                purpose="Rewrite known import paths after approved cleanup reorganization",
                capabilities=("maintenance:cleanup", "fs:write"),
                expected_outcome="Matching Python imports are rewritten and an update report is emitted",
                reversible=False,
                rollback_plan="restore rewritten files and report from version control or backups",
                metadata={
                    "base_path_hash": _hash_value(self.base_path),
                    "report_path_hash": _hash_value(report_path),
                    "total_files_scanned": int(total_files),
                    "files_to_update": len(planned_updates),
                    "total_updates": sum(plan.updates for plan in planned_updates),
                    "planned_file_hashes": [
                        _hash_value(plan.file_path.relative_to(self.base_path))
                        for plan in planned_updates[:100]
                    ],
                },
            ),
            approval_id=approval_id,
            capability_checker=_guardian_capability_checker,
        )

    def _python_files(self) -> list[Path]:
        python_files: list[Path] = []
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", ".vscode"}]
            for filename in files:
                if filename.endswith(".py"):
                    python_files.append(Path(root) / filename)
        return python_files

    def _plan_file_imports(self, file_path: Path) -> ImportUpdatePlan | None:
        content = file_path.read_text(encoding="utf-8")
        updated_content = content
        updates = 0

        for old_pattern, new_import in self.specific_mappings.items():
            next_content, replacements = re.subn(old_pattern, new_import, updated_content)
            if replacements:
                updated_content = next_content
                updates += replacements

        if updated_content == content:
            return None

        return ImportUpdatePlan(
            file_path=file_path,
            content=updated_content,
            updates=updates,
        )

    def _apply_plan(self, plan: ImportUpdatePlan) -> None:
        plan.file_path.write_text(plan.content, encoding="utf-8")
        self.updated_files.append({"file": plan.file_path, "updates": plan.updates})
        self.updates_made += plan.updates

    def scan_and_update_imports(self) -> int:
        print("Scanning for specific post-cleanup import statements...")
        print("=" * 60)

        python_files = self._python_files()
        print(f"Found {len(python_files)} Python files to check")
        print()

        planned_updates: list[ImportUpdatePlan] = []
        for file_path in python_files:
            try:
                plan = self._plan_file_imports(file_path)
            except OSError as exc:
                print(f"Error reading {file_path}: {exc}")
                continue

            if plan is not None:
                planned_updates.append(plan)

        report_path = self.base_path / "POST_CLEANUP_IMPORT_UPDATE_REPORT.md"
        decision = self._guardian_preflight_update(
            total_files=len(python_files),
            planned_updates=planned_updates,
            report_path=report_path,
        )
        if not decision.allowed:
            print(f"Guardian denied post-cleanup import update: {decision.reason}")
            return 1

        files_updated = 0
        for plan in planned_updates:
            rel_path = plan.file_path.relative_to(self.base_path)
            print(f"Updating: {rel_path}")
            self._apply_plan(plan)
            files_updated += 1

        self.generate_report(
            files_updated=files_updated,
            total_files=len(python_files),
            report_path=report_path,
        )
        return 0

    def generate_report(self, files_updated: int, total_files: int, report_path: Path):
        print("POST-CLEANUP IMPORT UPDATE SUMMARY")
        print("=" * 50)
        print(f"Files scanned: {total_files}")
        print(f"Files updated: {files_updated}")
        print(f"Total import updates: {self.updates_made}")
        print()

        if self.updated_files:
            print("Updated Files:")
            for item in self.updated_files:
                rel_path = item["file"].relative_to(self.base_path)
                print(f"  - {rel_path} ({item['updates']} updates)")
        else:
            print("No import updates needed for reorganized files.")

        report_lines = [
            "# POST-CLEANUP IMPORT UPDATE REPORT",
            "",
            f"**Files Scanned:** {total_files}",
            f"**Files Updated:** {files_updated}",
            f"**Total Updates:** {self.updates_made}",
            "",
            "## Targeted Reorganization Imports",
            "",
            "This scan looked for imports of files reorganized by cleanup workflows.",
            "",
            "## Search Patterns Used",
            "",
        ]

        for old_pattern, new_import in self.specific_mappings.items():
            clean_pattern = old_pattern.replace(r"\s+", " ").replace(r"\.", ".")
            report_lines.append(f"- `{clean_pattern}` -> `{new_import}`")

        if self.updated_files:
            report_lines.extend(["", "## Updated Files", ""])
            for item in self.updated_files:
                rel_path = item["file"].relative_to(self.base_path)
                report_lines.append(f"- `{rel_path}` ({item['updates']} updates)")
        else:
            report_lines.extend(
                [
                    "",
                    "## No Updates Needed",
                    "",
                    "No files currently import the reorganized modules using the searched patterns.",
                ]
            )

        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        print()
        print(f"Detailed report saved to: {report_path}")


if __name__ == "__main__":
    updater = PostCleanupImportUpdater()
    raise SystemExit(updater.scan_and_update_imports())
