#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Directory Documentation Generator - Creates README.md files for each major directory
"""

from __future__ import annotations

# Standard library imports
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentationWritePlan:
    file_path: Path
    content: str
    kind: str


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


def _safe_relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def _guardian_preflight_documentation_write(
    *,
    project_root: Path,
    plans: list[DocumentationWritePlan],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.documentation_generation",
            target="maintenance:documentation_generation",
            purpose="Write generated project documentation files",
            capabilities=("maintenance:cleanup", "fs:write"),
            expected_outcome="Planned documentation files are written to disk",
            reversible=False,
            rollback_plan="delete generated documentation or restore from version control",
            metadata={
                "project_root_hash": _hash_value(project_root.resolve()),
                "document_count": len(plans),
                "document_kind_counts": {
                    kind: sum(1 for plan in plans if plan.kind == kind)
                    for kind in sorted({plan.kind for plan in plans})
                },
                "document_path_hashes": [
                    _hash_value(_safe_relative_path(plan.file_path, project_root))
                    for plan in plans[:100]
                ],
                "total_document_length": sum(len(plan.content) for plan in plans),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def write_documentation_plans(
    *,
    project_root: Path,
    plans: list[DocumentationWritePlan],
) -> int:
    if not plans:
        print("No documentation files to create.")
        return 0

    decision = _guardian_preflight_documentation_write(
        project_root=project_root,
        plans=plans,
    )
    if not decision.allowed:
        print(f"Guardian denied documentation generation: {decision.reason}")
        return 1

    for plan in plans:
        plan.file_path.parent.mkdir(parents=True, exist_ok=True)
        plan.file_path.write_text(plan.content, encoding="utf-8")
        print(f"Created: {plan.file_path}")
    return 0


def load_analysis(filename="aetherra_project_analysis.json"):
    """Load the updated project analysis"""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)


def generate_directory_readme(dir_path, dir_info):
    """Generate README.md content for a directory"""

    readme_content = f"""# {Path(dir_path).name}

## Purpose
{dir_info["purpose"]}

## Contents
This directory contains **{dir_info["total_files"]} files** organized as follows:

"""

    # File type breakdown
    if dir_info["file_counts"]:
        readme_content += "### File Types\n\n"
        for file_type, count in sorted(
            dir_info["file_counts"].items(), key=lambda x: x[1], reverse=True
        ):
            readme_content += (
                f"- **{file_type.replace('_', ' ').title()}**: {count} files\n"
            )
        readme_content += "\n"

    # Subdirectories
    if dir_info["subdirectories"]:
        readme_content += "### Subdirectories\n\n"
        for subdir in sorted(dir_info["subdirectories"]):
            readme_content += f"- `{subdir}/`\n"
        readme_content += "\n"

    # Notable files (first 10)
    if dir_info["files"]:
        readme_content += "### Key Files\n\n"

        # Group files by category
        files_by_category = {}
        for file_info in dir_info["files"]:
            category = file_info["category"]
            if category not in files_by_category:
                files_by_category[category] = []
            files_by_category[category].append(file_info)

        for category, files in sorted(files_by_category.items()):
            if category == "other":
                continue  # Skip 'other' category for now

            readme_content += f"#### {category.replace('_', ' ').title()}\n\n"
            for file_info in files[:5]:  # Show first 5 files per category
                file_name = file_info["name"]

                # Add description based on file analysis
                description = ""
                if "python_analysis" in file_info and file_info["python_analysis"].get(
                    "docstring"
                ):
                    description = (
                        f" - {file_info['python_analysis']['docstring'][:100]}..."
                    )
                elif file_name.lower().startswith("test_"):
                    description = " - Test file"
                elif file_name.lower().startswith("demo_"):
                    description = " - Demonstration/example file"
                elif file_name == "__init__.py":
                    description = " - Python package initialization"
                elif file_name.endswith(".md"):
                    description = " - Documentation file"
                elif file_name.endswith(".json"):
                    description = " - Configuration file"

                readme_content += f"- `{file_name}`{description}\n"

            if len(files) > 5:
                readme_content += f"- ... and {len(files) - 5} more {category} files\n"
            readme_content += "\n"

    # Usage information
    readme_content += """## Usage

This directory is part of the Aetherra OS project. Files in this directory should be:

- **Documented**: Each significant file should have clear documentation
- **Tested**: Critical functionality should have corresponding tests
- **Maintained**: Regular review and updates as needed

## Development Notes

When working with files in this directory:

1. Follow the established naming conventions
2. Add appropriate documentation for new files
3. Update tests when modifying functionality
4. Consider the impact on other system components

---
*This README was automatically generated. Last updated: {Path().cwd().name} project analysis*
"""

    return readme_content


def plan_directory_readmes(analysis) -> tuple[list[DocumentationWritePlan], int]:
    """Plan README.md files for major directories without writing them."""
    directories = analysis.get("directories", {})

    skipped_count = 0
    created_count = 0
    plans: list[DocumentationWritePlan] = []

    print("📝 Generating directory README files...")
    print("=" * 50)

    for dir_path, dir_info in directories.items():
        # Skip certain directories
        skip_dirs = [
            "frontend/Lib",
            "frontend/Scripts",
            ".git",
            "__pycache__",
            "node_modules",
        ]

        if any(skip in dir_path for skip in skip_dirs):
            continue

        # Only create READMEs for directories with a reasonable number of files
        if dir_info["total_files"] == 0 or dir_info["total_files"] > 50:
            skipped_count += 1
            continue

        # Check if README already exists
        readme_path = Path(dir_path) / "README.md"
        if readme_path.exists():
            print(f"⏭️ Skipped (exists): {dir_path}")
            skipped_count += 1
            continue

        try:
            # Generate README content
            readme_content = generate_directory_readme(dir_path, dir_info)

            # Create the README file
            plans.append(
                DocumentationWritePlan(
                    file_path=readme_path,
                    content=readme_content,
                    kind="directory_readme",
                )
            )
            print(f"✅ Created: {readme_path}")
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating README for {dir_path}: {e}")

    print()
    print("🎯 README Generation Summary:")
    print(f"   Created: {created_count} README files")
    print(f"   Skipped: {skipped_count} directories")
    print("✅ Directory documentation complete!")
    return plans, skipped_count


def create_directory_readmes(analysis=None):
    """Create README.md files for major directories after Guardian approval."""
    loaded_analysis = analysis or load_analysis()
    plans, skipped_count = plan_directory_readmes(loaded_analysis)
    result = write_documentation_plans(project_root=Path.cwd(), plans=plans)
    print()
    print("README Generation Summary:")
    print(f"   Created: {len(plans) if result == 0 else 0} README files")
    print(f"   Skipped: {skipped_count} directories")
    print("Directory documentation complete!")
    return result


def plan_main_project_breakdown(analysis, output_path="PROJECT_BREAKDOWN.md"):
    """Plan the main project breakdown document without writing it."""

    breakdown_content = f"""# 🏗️ Aetherra Project Breakdown

*Complete file and directory analysis*

## 📊 Project Overview

**Analysis Date:** {analysis["timestamp"]}
**Project Root:** {analysis["project_root"]}

### Statistics
- **Total Files:** {analysis["summary"]["total_files"]}
- **Total Directories:** {analysis["summary"]["total_directories"]}
- **File Categories:** {len(analysis["summary"]["file_categories"])}

### File Distribution
"""

    # Add file category breakdown
    for category, count in sorted(
        analysis["summary"]["file_categories"].items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / analysis["summary"]["total_files"]) * 100
        breakdown_content += f"- **{category.replace('_', ' ').title()}**: {count} files ({percentage:.1f}%)\n"

    breakdown_content += """

## 🗂️ Directory Structure

### Major Components

"""

    # Add major directory information
    directories = analysis.get("directories", {})
    major_dirs = {
        k: v
        for k, v in directories.items()
        if v["total_files"] > 5 and "/" not in k.strip(".").replace("\\", "/")
    }

    for dir_path, dir_info in sorted(major_dirs.items()):
        breakdown_content += f"""#### `{dir_path}`
**Purpose:** {dir_info["purpose"]}
**Files:** {dir_info["total_files"]} total
**Key Types:** {", ".join(f"{k} ({v})" for k, v in sorted(dir_info["file_counts"].items(), key=lambda x: x[1], reverse=True)[:3])}

"""

    breakdown_content += """## 🎯 File Utilization

### Core System Files
Files essential for Aetherra OS operation:

- **Python Modules**: Core functionality and system components
- **Configuration Files**: System and component configuration
- **Database Files**: Data storage and memory systems
- **API Components**: Interface and communication modules

### Development Files
Files supporting development and testing:

- **Test Files**: Automated testing and validation
- **Demo Files**: Examples and demonstrations
- **Documentation**: Project documentation and guides
- **Tools**: Development utilities and scripts

### Support Files
Files supporting the project ecosystem:

- **Build Files**: Compilation and deployment
- **Environment Files**: Development environment setup
- **Log Files**: System and application logs
- **Metadata**: Project metadata and package information

## 📋 Maintenance Guidelines

### File Organization
1. **Core components** should remain in `Aetherra/` directory
2. **Tests** are organized in `tests/` directory
3. **Documentation** is organized in `docs-organized/` directory
4. **Database files** are centralized in `Aetherra/data/databases/`

### Development Practices
1. **Add documentation** for new significant files
2. **Include tests** for critical functionality
3. **Follow naming conventions** established in each directory
4. **Update README files** when directory contents change significantly

### Regular Maintenance
- **Monthly review** of file organization
- **Quarterly cleanup** of unused files
- **Annual architecture review** for structural improvements

---

## 🔍 Detailed Analysis

For detailed information about specific directories and files, see:

- Individual directory `README.md` files
- `DUPLICATE_FILES_REPORT.md` - Analysis of duplicate files
- `FILE_CATEGORY_ANALYSIS.md` - Detailed file type breakdown
- `CONSOLIDATION_PLAN.md` - File consolidation recommendations

---
*This breakdown provides a comprehensive view of the Aetherra project structure and file organization.*
"""

    # Save the breakdown
    return DocumentationWritePlan(
        file_path=Path(output_path),
        content=breakdown_content,
        kind="project_breakdown",
    )

def create_main_project_breakdown(analysis=None):
    """Create the main project breakdown document after Guardian approval."""
    loaded_analysis = analysis or load_analysis()
    plan = plan_main_project_breakdown(loaded_analysis)
    return write_documentation_plans(project_root=Path.cwd(), plans=[plan])


def main():
    """Main execution function"""
    print("🏗️ Creating comprehensive project documentation...")
    print()

    analysis = load_analysis()
    readme_plans, skipped_count = plan_directory_readmes(analysis)
    breakdown_plan = plan_main_project_breakdown(analysis)
    result = write_documentation_plans(
        project_root=Path.cwd(),
        plans=[*readme_plans, breakdown_plan],
    )
    if result != 0:
        return result

    print()
    print("README Generation Summary:")
    print(f"   Created: {len(readme_plans)} README files")
    print(f"   Skipped: {skipped_count} directories")
    print()

    print("🎉 Project documentation system complete!")
    print()
    print("📚 Documentation created:")
    print("   - Individual directory README.md files")
    print("   - PROJECT_BREAKDOWN.md (master overview)")
    print("   - Analysis reports (already generated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
