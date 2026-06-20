#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Generate readable Markdown reports from project analysis JSON."""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from Aetherra.maintenance import require_allowed_report_destination


@dataclass(frozen=True)
class AnalysisReportPlan:
    file_path: Path
    content: str


def _hash_value(value) -> str | None:
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


def _guardian_preflight_report_generation(
    *,
    output_dir: Path,
    plans: list[AnalysisReportPlan],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.analysis_report_generation",
            target="maintenance:analysis_reports",
            purpose="Write generated project analysis Markdown reports",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Planned analysis reports are written to the output directory",
            reversible=False,
            rollback_plan="delete generated reports or restore from version control",
            metadata={
                "output_dir_hash": _hash_value(output_dir),
                "report_count": len(plans),
                "report_name_hashes": [
                    _hash_value(plan.file_path.name) for plan in plans[:100]
                ],
                "total_report_length": sum(len(plan.content) for plan in plans),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def load_analysis(filename):
    """Load analysis results from JSON file."""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)


def generate_duplicate_report(analysis):
    """Generate detailed duplicate file report."""
    duplicates = analysis.get("duplicates", [])
    report = "# Duplicate Files Report\n\n"
    report += f"**Found {len(duplicates)} groups of duplicate files**\n\n"
    total_duplicates = sum(d["count"] - 1 for d in duplicates)
    report += f"**Total duplicate files that can be removed: {total_duplicates}**\n\n"

    for index, dup_group in enumerate(duplicates[:20], 1):
        report += f"## Group {index}: {dup_group['count']} identical files\n\n"
        report += f"**Hash:** `{dup_group['hash'][:16]}...`\n\n"
        report += "**Files:**\n"
        for filepath in dup_group["files"]:
            try:
                size = Path(filepath).stat().st_size
                report += f"- `{filepath}` ({size} bytes)\n"
            except OSError:
                report += f"- `{filepath}` (size unknown)\n"
        report += "\n"

        if len(dup_group["files"]) > 1:
            main_file = min(dup_group["files"], key=len)
            others = [path for path in dup_group["files"] if path != main_file]
            report += f"**Recommendation:** Keep `{main_file}`, remove:\n"
            for other in others:
                report += f"  - `{other}`\n"
            report += "\n"

    if len(duplicates) > 20:
        report += f"\n... and {len(duplicates) - 20} more duplicate groups\n"
    return report


def generate_directory_summary(analysis):
    """Generate directory-by-directory summary."""
    directories = analysis.get("directories", {})
    report = "# Directory Structure Analysis\n\n"
    sorted_dirs = sorted(directories.items(), key=lambda item: (item[0].count("/"), item[0]))

    for dir_path, dir_info in sorted_dirs[:30]:
        if dir_info["total_files"] == 0:
            continue
        report += f"## `{dir_path}`\n\n"
        report += f"**Purpose:** {dir_info['purpose']}\n\n"
        report += f"**Files:** {dir_info['total_files']} total\n\n"

        if dir_info["file_counts"]:
            report += "**File Types:**\n"
            for file_type, count in sorted(dir_info["file_counts"].items()):
                report += f"- {file_type}: {count} files\n"
            report += "\n"

        if dir_info["subdirectories"]:
            report += f"**Subdirectories:** {', '.join(dir_info['subdirectories'][:5])}"
            if len(dir_info["subdirectories"]) > 5:
                report += f" and {len(dir_info['subdirectories']) - 5} more"
            report += "\n\n"

        notable_files = [
            f"`{file_info['name']}` ({file_info['category']})"
            for file_info in dir_info["files"][:5]
        ]
        if notable_files:
            report += f"**Notable Files:** {', '.join(notable_files)}\n"
            if len(dir_info["files"]) > 5:
                report += f" and {len(dir_info['files']) - 5} more files"
            report += "\n\n"
        report += "---\n\n"
    return report


def generate_file_category_analysis(analysis):
    """Analyze files by category."""
    summary = analysis.get("summary", {})
    file_categories = summary.get("file_categories", {})
    total_files = summary.get("total_files", 0)

    report = "# File Category Analysis\n\n"
    report += f"**Total Files:** {total_files}\n\n"
    sorted_categories = sorted(file_categories.items(), key=lambda item: item[1], reverse=True)

    report += "## File Distribution\n\n"
    for category, count in sorted_categories:
        percentage = (count / max(total_files, 1)) * 100
        report += f"- **{category}**: {count} files ({percentage:.1f}%)\n"

    descriptions = {
        "python_module": "Python source code modules",
        "test": "Test files and testing utilities",
        "demo": "Demonstration and example files",
        "documentation": "Documentation in Markdown format",
        "configuration": "Configuration files",
        "database": "Database files",
        "launcher": "Application launcher scripts",
        "python_special": "Python special files",
        "log": "Log files",
        "text": "Plain text files",
        "other": "Other file types",
    }

    report += "\n## Category Descriptions\n\n"
    for category, count in sorted_categories:
        report += f"**{category}** ({count} files): {descriptions.get(category, 'No description available')}\n\n"
    return report


def generate_consolidation_plan(analysis):
    """Generate file consolidation recommendations."""
    duplicate_categories = defaultdict(list)
    for dup_group in analysis.get("duplicates", []):
        first_file = dup_group["files"][0]
        if first_file.endswith(".py"):
            key = "test_files" if "test" in first_file.lower() else "python_modules"
        elif first_file.endswith(".md"):
            key = "documentation"
        elif first_file.endswith(".db"):
            key = "databases"
        else:
            key = "other"
        duplicate_categories[key].append(dup_group)

    report = "# File Consolidation Plan\n\n"
    report += "## Consolidation by Category\n\n"
    for category, dup_groups in duplicate_categories.items():
        report += f"### {category.replace('_', ' ').title()} ({len(dup_groups)} groups)\n\n"
        total_remove = sum(group["count"] - 1 for group in dup_groups)
        report += f"**Files that can be removed:** {total_remove}\n\n"
        for index, dup_group in enumerate(dup_groups[:5], 1):
            main_file = min(dup_group["files"], key=len)
            others = [path for path in dup_group["files"] if path != main_file]
            report += f"{index}. **Keep:** `{main_file}`\n"
            report += f"   **Remove:** {len(others)} duplicates\n"
            for other in others[:3]:
                report += f"   - `{other}`\n"
            if len(others) > 3:
                report += f"   - ... and {len(others) - 3} more\n"
            report += "\n"
        if len(dup_groups) > 5:
            report += f"... and {len(dup_groups) - 5} more groups in this category\n\n"
    return report


def plan_analysis_reports(analysis, output_dir=".") -> list[AnalysisReportPlan]:
    """Build report write plans without mutating files."""
    out = Path(output_dir)
    reports = {
        "DUPLICATE_FILES_REPORT.md": generate_duplicate_report(analysis),
        "DIRECTORY_STRUCTURE_ANALYSIS.md": generate_directory_summary(analysis),
        "FILE_CATEGORY_ANALYSIS.md": generate_file_category_analysis(analysis),
        "CONSOLIDATION_PLAN.md": generate_consolidation_plan(analysis),
    }
    return [
        AnalysisReportPlan(file_path=out / filename, content=content)
        for filename, content in reports.items()
    ]


def write_analysis_reports(
    plans: list[AnalysisReportPlan],
    output_dir=".",
    *,
    project_root: Path | str | None = None,
) -> int:
    """Write planned reports after Guardian approval."""
    output_path = Path(output_dir)
    policy_root = Path(project_root) if project_root is not None else Path.cwd()
    if not plans:
        print("No analysis reports to generate.")
        return 0

    try:
        for plan in plans:
            require_allowed_report_destination(plan.file_path, policy_root)
    except ValueError as exc:
        print(f"Maintenance report path blocked: {exc}")
        return 1

    decision = _guardian_preflight_report_generation(
        output_dir=output_path,
        plans=plans,
    )
    if not decision.allowed:
        print(f"Guardian denied analysis report generation: {decision.reason}")
        return 1

    for plan in plans:
        plan.file_path.parent.mkdir(parents=True, exist_ok=True)
        plan.file_path.write_text(plan.content, encoding="utf-8")
        print(f"Generated {plan.file_path}")
    return 0


def main(
    analysis_file="artifacts/maintenance/aetherra_project_analysis.json",
    output_dir="reports/maintenance",
) -> int:
    """Generate comprehensive analysis reports."""
    print("Generating analysis reports...")
    analysis = load_analysis(analysis_file)
    result = write_analysis_reports(
        plan_analysis_reports(analysis, output_dir=output_dir),
        output_dir=output_dir,
        project_root=Path.cwd(),
    )
    if result != 0:
        return result

    summary = analysis.get("summary", {})
    print("\nAnalysis Summary:")
    print(f"   Total Files: {summary.get('total_files', 0)}")
    print(f"   Total Directories: {summary.get('total_directories', 0)}")
    print(f"   Duplicate Files: {summary.get('duplicate_files', 0)}")
    print(f"   Duplicate Groups: {len(analysis.get('duplicates', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
