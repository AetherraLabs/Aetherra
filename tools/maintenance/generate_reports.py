#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Analysis Report Generator - Creates readable reports from project analysis
"""

# Standard library imports
import json
from collections import defaultdict
from pathlib import Path


def load_analysis(filename):
    """Load analysis results from JSON file"""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)


def generate_duplicate_report(analysis):
    """Generate detailed duplicate file report"""
    duplicates = analysis.get("duplicates", [])

    report = "# 🔄 Duplicate Files Report\n\n"
    report += f"**Found {len(duplicates)} groups of duplicate files**\n\n"

    total_duplicates = sum(d["count"] - 1 for d in duplicates)
    report += f"**Total duplicate files that can be removed: {total_duplicates}**\n\n"

    for i, dup_group in enumerate(duplicates[:20], 1):  # Show top 20
        report += f"## Group {i}: {dup_group['count']} identical files\n\n"
        report += f"**Hash:** `{dup_group['hash'][:16]}...`\n\n"
        report += "**Files:**\n"
        for filepath in dup_group["files"]:
            # Get file size for context
            try:
                size = Path(filepath).stat().st_size
                report += f"- `{filepath}` ({size} bytes)\n"
            except:
                report += f"- `{filepath}` (size unknown)\n"
        report += "\n"

        # Add recommendation
        if len(dup_group["files"]) > 1:
            main_file = min(dup_group["files"], key=len)  # Shortest path as main
            others = [f for f in dup_group["files"] if f != main_file]
            report += f"**Recommendation:** Keep `{main_file}`, remove:\n"
            for other in others:
                report += f"  - `{other}`\n"
            report += "\n"

    if len(duplicates) > 20:
        report += f"\n... and {len(duplicates) - 20} more duplicate groups\n"

    return report


def generate_directory_summary(analysis):
    """Generate directory-by-directory summary"""
    directories = analysis.get("directories", {})

    report = "# 📁 Directory Structure Analysis\n\n"

    # Sort directories by path depth and name
    sorted_dirs = sorted(directories.items(), key=lambda x: (x[0].count("/"), x[0]))

    for dir_path, dir_info in sorted_dirs[:30]:  # Show top 30 directories
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

        # Show notable files
        notable_files = []
        for file_info in dir_info["files"][:5]:  # Show first 5 files
            file_name = file_info["name"]
            file_cat = file_info["category"]
            notable_files.append(f"`{file_name}` ({file_cat})")

        if notable_files:
            report += f"**Notable Files:** {', '.join(notable_files)}\n"
            if len(dir_info["files"]) > 5:
                report += f" and {len(dir_info['files']) - 5} more files"
            report += "\n\n"

        report += "---\n\n"

    return report


def generate_file_category_analysis(analysis):
    """Analyze files by category"""
    summary = analysis.get("summary", {})
    file_categories = summary.get("file_categories", {})

    report = "# 📊 File Category Analysis\n\n"
    report += f"**Total Files:** {summary.get('total_files', 0)}\n\n"

    # Sort categories by count
    sorted_categories = sorted(
        file_categories.items(), key=lambda x: x[1], reverse=True
    )

    report += "## File Distribution\n\n"
    for category, count in sorted_categories:
        percentage = (count / summary.get("total_files", 1)) * 100
        report += f"- **{category}**: {count} files ({percentage:.1f}%)\n"

    report += "\n## Category Descriptions\n\n"
    category_descriptions = {
        "python_module": "Python source code modules",
        "test": "Test files and testing utilities",
        "demo": "Demonstration and example files",
        "documentation": "Documentation in Markdown format",
        "configuration": "Configuration files (JSON, YAML, etc.)",
        "database": "Database files (.db)",
        "launcher": "Application launcher scripts",
        "python_special": "Python special files (__init__.py, etc.)",
        "log": "Log files",
        "text": "Plain text files",
        "other": "Other file types",
    }

    for category, count in sorted_categories:
        description = category_descriptions.get(category, "No description available")
        report += f"**{category}** ({count} files): {description}\n\n"

    return report


def generate_consolidation_plan(analysis):
    """Generate file consolidation recommendations"""
    duplicates = analysis.get("duplicates", [])

    report = "# 🎯 File Consolidation Plan\n\n"

    # Categorize duplicates by type
    duplicate_categories = defaultdict(list)
    for dup_group in duplicates:
        # Determine category based on file extensions
        first_file = dup_group["files"][0]
        if first_file.endswith(".py"):
            if "test" in first_file.lower():
                duplicate_categories["test_files"].append(dup_group)
            elif "demo" in first_file.lower():
                duplicate_categories["demo_files"].append(dup_group)
            else:
                duplicate_categories["python_modules"].append(dup_group)
        elif first_file.endswith(".md"):
            duplicate_categories["documentation"].append(dup_group)
        elif first_file.endswith(".db"):
            duplicate_categories["databases"].append(dup_group)
        else:
            duplicate_categories["other"].append(dup_group)

    report += "## Consolidation by Category\n\n"

    for category, dup_groups in duplicate_categories.items():
        if not dup_groups:
            continue

        report += (
            f"### {category.replace('_', ' ').title()} ({len(dup_groups)} groups)\n\n"
        )

        total_files_to_remove = sum(dg["count"] - 1 for dg in dup_groups)
        report += f"**Files that can be removed:** {total_files_to_remove}\n\n"

        for i, dup_group in enumerate(dup_groups[:5], 1):  # Show top 5 per category
            main_file = min(dup_group["files"], key=len)
            others = [f for f in dup_group["files"] if f != main_file]

            report += f"{i}. **Keep:** `{main_file}`\n"
            report += f"   **Remove:** {len(others)} duplicates\n"
            for other in others[:3]:  # Show first 3 duplicates
                report += f"   - `{other}`\n"
            if len(others) > 3:
                report += f"   - ... and {len(others) - 3} more\n"
            report += "\n"

        if len(dup_groups) > 5:
            report += f"... and {len(dup_groups) - 5} more groups in this category\n\n"

    return report


def main():
    """Generate comprehensive analysis reports"""
    print("📊 Generating analysis reports...")

    # Load analysis data
    analysis = load_analysis("aetherra_project_analysis.json")

    # Generate reports
    reports = {
        "DUPLICATE_FILES_REPORT.md": generate_duplicate_report(analysis),
        "DIRECTORY_STRUCTURE_ANALYSIS.md": generate_directory_summary(analysis),
        "FILE_CATEGORY_ANALYSIS.md": generate_file_category_analysis(analysis),
        "CONSOLIDATION_PLAN.md": generate_consolidation_plan(analysis),
    }

    # Save reports
    for filename, content in reports.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Generated {filename}")

    # Print summary
    summary = analysis.get("summary", {})
    print("\n📈 Analysis Summary:")
    print(f"   Total Files: {summary.get('total_files', 0)}")
    print(f"   Total Directories: {summary.get('total_directories', 0)}")
    print(f"   Duplicate Files: {summary.get('duplicate_files', 0)}")
    print(f"   Duplicate Groups: {len(analysis.get('duplicates', []))}")


if __name__ == "__main__":
    main()
