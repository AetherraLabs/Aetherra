#!/usr/bin/env python3
"""
Final Cleanup Script - Move Remaining Documentation Files
========================================================

Moves any remaining documentation and report files to their proper locations.
"""

import shutil
from pathlib import Path

# Workspace root
workspace_root = Path(r"c:\Users\enigm\Desktop\New aetherra Language")
docs_dir = workspace_root / "docs"
reports_dir = docs_dir / "reports"

# Ensure directories exist
reports_dir.mkdir(parents=True, exist_ok=True)


def move_file_if_exists(src, dst):
    """Move file if it exists."""
    if src.exists():
        shutil.move(str(src), str(dst))
        print(f"📄 Moved: {src.name} -> {dst}")
        return True
    return False


# Move remaining documentation files to docs/reports/
remaining_docs = [
    "ADVANCED_SYNTAX_IMPLEMENTATION.md",
    "AI_ENHANCEMENT_IMPLEMENTATION.md",
    "AST_PARSER_FIXES.md",
    "CLEANUP_PLAN.md",
    "CLEANUP_SUMMARY.md",
    "COMPLETE_OPTIMIZATION_GUIDE.md",
    "CONTINUATION_SUMMARY.md",
    "CORE_ERROR_ANALYSIS_COMPLETE.md",
    "CORE_ERROR_RESOLUTION_COMPLETE.md",
    "CORE_FIXES_AND_ENHANCEMENTS_COMPLETE.md",
    "DEPENDENCY_ANALYSIS_v1.0.0.md",
    "DOCUMENTATION_VERIFICATION_REPORT.md",
    "ENHANCEMENT_SUMMARY.md",
    "ERROR_FIXES_v1.0.0.md",
    "FILE_ORGANIZATION_COMPLETE.md",
    "FILE_ORGANIZATION_COMPLETE_V2.md",
    "FILE_ORGANIZATION_FINAL.md",
    "FILE_ORGANIZATION_PLAN.md",
    "FINAL_GITHUB_PREPARATION.md",
    "GUI_DEPENDENCY_FIXES_COMPLETE.md",
    "GUI_FIXES_COMPLETE.md",
    "IMMEDIATE_OPTIMIZATION_SUMMARY.md",
    "IMPLEMENTATION_SUMMARY.md",
    "IMPORT_FIX_COMPLETE.md",
    "INTERPRETER_ENHANCEMENT_COMPLETE.md",
    "INTERPRETER_ENHANCEMENT_PLAN.md",
    "INTERPRETER_ERROR_ANALYSIS.md",
    "ITERATION_STATUS_REPORT.md",
    "LANGUAGE_INDEPENDENCE_ACHIEVED.md",
    "MANUAL_EXTENSION_INSTALL.md",
    "MEMORY_ENHANCEMENT_MISSION_COMPLETE.md",
    "MEMORY_TEMPORAL_ENHANCEMENT_COMPLETE.md",
    "MULTI_LLM_ACHIEVEMENT.md",
    "aetherra_FOUNDATION_ESTABLISHED.md",
    "aetherra_FUTURE_ROADMAP.md",
    "aetherra_LANGUAGE_COMPLETE.md",
    "aetherra_MANIFESTO.md",
    "aetherra_PLAYGROUND_COMPLETE.md",
    "aetherra_REVOLUTION.md",
    "aetherra_STDLIB_COMPLETE.md",
    "aetherra_UNIVERSAL_STANDARD.md",
    "aetherra_V1_ACHIEVEMENT_REPORT.md",
    "aetherra_VOICE_ACHIEVED.md",
    "NEUROPLEX_AI_ENHANCEMENT_COMPLETE.md",
    "NEUROPLEX_ANALYSIS_REPORT.md",
    "NEUROPLEX_GUI_FIXES_COMPLETE.md",
    "NEUROPLEX_GUI_GUIDE.md",
    "NEUROPLEX_GUI_STATUS.md",
    "NEUROPLEX_LAYOUT_OPTIMIZATION_COMPLETE.md",
    "NEUROPLEX_V2_DOCUMENTATION.md",
    "NEUROPLEX_V2_ENHANCEMENT_COMPLETE.md",
    "NEURO_UI_CLEANUP_SUMMARY.md",
    "OPENAI_INIT_FIX.md",
    "OPTIMIZATION_GUIDE.md",
    "PERFORMANCE_ENHANCEMENT_PLAN.md",
    "PLUGIN_ENHANCEMENT_COMPLETE.md",
    "RELEASE_NOTES_v1.0.0.md",
    "REPOSITORY_UPDATE_COMPLETE.md",
    "REVOLUTION_ACHIEVED.md",
    "RUFF_MIGRATION_COMPLETE.md",
    "SELF_AWARENESS_DEMO.md",
    "SELF_EDITING_ARCHITECTURE.md",
    "SELF_EDITING_GUIDE.md",
    "UI_ENHANCEMENT_COMPLETE.md",
    "UI_ERROR_FIXES_COMPLETE.md",
    "UI_FIXES_COMPLETE.md",
    "UNICODE_FIX_COMPLETE.md",
    "VECTORMEMORY_SETPLACEHOLDER_FIXES_COMPLETE.md",
    "VSCODE_SETUP_COMPLETE.md",
    "WORKSPACE_ORGANIZATION_COMPLETE.md",
    "WORKSPACE_ORGANIZATION_PLAN.md",
    "FINAL_ORGANIZATION_STATUS.md",
]

print("🧹 Final cleanup - Moving remaining documentation files...")

moved_count = 0
for doc_file in remaining_docs:
    src_path = workspace_root / doc_file
    dst_path = reports_dir / doc_file
    if move_file_if_exists(src_path, dst_path):
        moved_count += 1

# Move README files and other docs to main docs folder
main_docs = [
    "PLAYGROUND_README.md",
    "LANGUAGE_ACHIEVEMENT.txt",
    "GITHUB_UPLOAD_GUIDE.md",
]

for doc_file in main_docs:
    src_path = workspace_root / doc_file
    dst_path = docs_dir / doc_file
    if move_file_if_exists(src_path, dst_path):
        moved_count += 1

print(f"\n✅ Final cleanup complete! Moved {moved_count} documentation files.")
print("📚 All documentation now organized in docs/ and docs/reports/")

if __name__ == "__main__":
    pass
