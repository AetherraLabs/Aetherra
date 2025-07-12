#!/usr/bin/env python3
"""
aetherra Workspace Organization Script
=====================================

Organizes and cleans up the entire aetherra workspace according to the
modular architecture plan. Moves files to appropriate folders and
cleans up obsolete files.
"""

import shutil
from pathlib import Path

# Get the workspace root directory
WORKSPACE_ROOT = Path(r"c:\Users\enigm\Desktop\New aetherra Language")
print(f"🔧 Organizing aetherra workspace: {WORKSPACE_ROOT}")


def create_directory_if_not_exists(path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created directory: {path}")


def move_file_if_exists(src, dst):
    """Move file if it exists, create destination directory if needed."""
    src_path = Path(src)
    dst_path = Path(dst)

    if src_path.exists():
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        print(f"📄 Moved: {src_path.name} -> {dst_path}")
        return True
    return False


def main():
    """Main organization function."""

    # 1. Move all documentation files
    print("\n📚 Organizing documentation...")
    docs_dir = WORKSPACE_ROOT / "docs"

    # Move guides and tutorials
    move_file_if_exists(
        WORKSPACE_ROOT / "TUTORIAL.md", docs_dir / "guides" / "TUTORIAL.md"
    )
    move_file_if_exists(
        WORKSPACE_ROOT / "INSTALLATION.md", docs_dir / "guides" / "INSTALLATION.md"
    )
    move_file_if_exists(
        WORKSPACE_ROOT / "CONTRIBUTING.md", docs_dir / "guides" / "CONTRIBUTING.md"
    )
    move_file_if_exists(
        WORKSPACE_ROOT / "DOCUMENTATION.md", docs_dir / "DOCUMENTATION.md"
    )

    # Move architecture and spec docs
    move_file_if_exists(
        WORKSPACE_ROOT / "ARCHITECTURE.md", docs_dir / "ARCHITECTURE.md"
    )
    move_file_if_exists(
        WORKSPACE_ROOT / "MODULAR_ARCHITECTURE.md", docs_dir / "MODULAR_ARCHITECTURE.md"
    )
    move_file_if_exists(
        WORKSPACE_ROOT / "aetherra_LANGUAGE_SPEC.md",
        docs_dir / "aetherra_LANGUAGE_SPEC.md",
    )

    # Move completion reports to docs/reports
    reports = [
        "AI_ENHANCEMENT_COMPLETION_REPORT.md",
        "COMPLETE_MODULARIZATION_REPORT.md",
        "MODULARIZATION_SUCCESS_REPORT.md",
        "FINAL_STATUS_REPORT.md",
        "FINAL_VERIFICATION_SUMMARY.md",
        "WORKSPACE_ANALYSIS_COMPLETE.md",
        "DEPENDENCY_RESOLUTION_COMPLETE.md",
        "ERROR_ANALYSIS_AND_RESOLUTION_COMPLETE.md",
        "IMPLEMENTATION_COMPLETE.md",
        "PRODUCTION_READY_SUMMARY.md",
    ]

    for report in reports:
        move_file_if_exists(WORKSPACE_ROOT / report, docs_dir / "reports" / report)

    # 2. Move launcher files
    print("\n🚀 Organizing launchers...")
    launchers_dir = WORKSPACE_ROOT / "launchers"
    create_directory_if_not_exists(launchers_dir)

    launcher_files = [
        "launch_fully_modular_aetherplex.py",
        "launch_modular_aetherplex.py",
        "launch_aetherplex.py",
        "launch_aetherplex_v2.py",
        "launch_gui.py",
        "launch_aetherra_ui.py",
        "launch_playground.py",
        "main.py",
        "startup.py",
        "simple_gui_launcher.py",
        "safe_launcher.py",
    ]

    for launcher in launcher_files:
        move_file_if_exists(WORKSPACE_ROOT / launcher, launchers_dir / launcher)

    # 3. Move script files
    print("\n🔧 Organizing scripts...")
    scripts_dir = WORKSPACE_ROOT / "scripts"
    create_directory_if_not_exists(scripts_dir / "setup")
    create_directory_if_not_exists(scripts_dir / "tools")
    create_directory_if_not_exists(scripts_dir / "build")

    setup_scripts = [
        "setup_enhancements.py",
        "setup_multi_llm.py",
        "setup_optimization.py",
        "setup_vscode_extensions.py",
        "resolve_dependencies.py",
        "resolve_dependencies_clean.py",
    ]

    for script in setup_scripts:
        move_file_if_exists(WORKSPACE_ROOT / script, scripts_dir / "setup" / script)

    tool_scripts = [
        "check_qt.py",
        "fix_merge_conflicts.py",
        "workspace_analysis.py",
        "status_check.py",
        "prepare_for_github.py",
        "prepare_github_publication.py",
    ]

    for script in tool_scripts:
        move_file_if_exists(WORKSPACE_ROOT / script, scripts_dir / "tools" / script)

    # 4. Move test files
    print("\n🧪 Organizing tests...")
    tests_dir = WORKSPACE_ROOT / "tests"
    create_directory_if_not_exists(tests_dir / "unit")
    create_directory_if_not_exists(tests_dir / "integration")
    create_directory_if_not_exists(tests_dir / "performance")

    test_files = [
        "test_advanced_syntax.py",
        "test_core_features.py",
        "test_core_fixes.py",
        "test_debug_system.py",
        "test_demo_syntax.py",
        "test_enhanced_interpreter.py",
        "test_enhancements.py",
        "test_final_import.py",
        "test_fixes.py",
        "test_grammar_fix.py",
        "test_gui.py",
        "test_gui_import.py",
        "test_import_fix.py",
        "test_interpreter_errors.py",
        "test_launch.py",
        "test_memory_reflection.py",
        "test_multi_llm_integration.py",
        "test_aetherra_parser.py",
        "test_new_enhancements.py",
        "test_openai_fix.py",
        "test_playground_components.py",
        "test_simple_import.py",
        "test_stdlib_integration.py",
        "test_suite.py",
        "test_temporal_features.py",
        "test_temporal_memory_integration.py",
        "test_ui_deps.py",
    ]

    for test_file in test_files:
        if test_file.startswith("test_"):
            move_file_if_exists(
                WORKSPACE_ROOT / test_file, tests_dir / "unit" / test_file
            )

    # Move integration tests
    integration_tests = [
        "integration_test.py",
        "analysis_test.py",
        "comprehensive_analysis.py",
    ]

    for test_file in integration_tests:
        move_file_if_exists(
            WORKSPACE_ROOT / test_file, tests_dir / "integration" / test_file
        )

    # 5. Move example and demo files
    print("\n🎯 Organizing examples...")
    examples_dir = WORKSPACE_ROOT / "examples"
    create_directory_if_not_exists(examples_dir / "basic")
    create_directory_if_not_exists(examples_dir / "advanced")
    create_directory_if_not_exists(examples_dir / "demos")

    demo_files = [
        "demo_code.py",
        "demo_aetherplex_v2.py",
        "demo_ui_features.py",
        "comprehensive_demo.py",
        "debug_demo.py",
        "enhanced_aetherra_demo.py",
        "interpreter_enhancement_demo.py",
        "memory_temporal_demo.py",
        "natural_translation_demo.py",
        "aetherra_language_demo.py",
        "plugin_metadata_demo.py",
    ]

    for demo in demo_files:
        move_file_if_exists(WORKSPACE_ROOT / demo, examples_dir / "demos" / demo)

    # Move .aether example files
    aetherra_files = [
        "advanced_syntax_demo.aether",
        "independence_demo.aether",
        "monitor.aether",
        "plugin_test.aether",
        "revolution_demo.aether",
        "stdlib_test.aether",
        "test_program.aether",
        "universal_ai_demo.aether",
    ]

    for aetherra_file in aetherra_files:
        if aetherra_file.endswith("demo.aether") or aetherra_file.endswith("test.aether"):
            move_file_if_exists(
                WORKSPACE_ROOT / aetherra_file, examples_dir / "basic" / aetherra_file
            )
        else:
            move_file_if_exists(
                WORKSPACE_ROOT / aetherra_file, examples_dir / "advanced" / aetherra_file
            )

    # 6. Move data files
    print("\n💾 Organizing data files...")
    data_dir = WORKSPACE_ROOT / "data"

    data_files = [
        "memory_store.json.example",
        "goals_store.json.example",
        "aetherra_functions.json.example",
        "enhanced_memory.json",
        "vector_memory.json",
    ]

    for data_file in data_files:
        move_file_if_exists(WORKSPACE_ROOT / data_file, data_dir / data_file)

    # Keep current data files in root but copy examples to data
    if (WORKSPACE_ROOT / "memory_store.json").exists():
        print("📄 Keeping active memory_store.json in root")
    if (WORKSPACE_ROOT / "goals_store.json").exists():
        print("📄 Keeping active goals_store.json in root")

    # 7. Archive obsolete files
    print("\n🗄️ Archiving obsolete files...")
    archive_dir = WORKSPACE_ROOT / "archive" / "legacy"
    create_directory_if_not_exists(archive_dir)

    # Files to archive (old versions, duplicates, etc.)
    obsolete_files = [
        "aetherra.py",  # Old main file
        "aetherra_engine.py",
        "aetherra_playground.py",
        "aetherplex.py",  # Old monolithic GUI
        "aetherra_runner.py",
        "aetherra_runner_standalone.py",
        "natural_translator.py",
        "quickstart.py",
        "quick_debug_test.py",
        "quick_verify.py",
        "agent_reflection_loop.py",
        "aetherplex_cli.py",
        "performance_monitor.py",
        "tokenize_debug.py",
        "parse_debug.py",
        "parse_debug2.py",
        "parse_debug3.py",
        "parse_debug4.py",
    ]

    for obsolete in obsolete_files:
        move_file_if_exists(WORKSPACE_ROOT / obsolete, archive_dir / obsolete)

    # 8. Move verification scripts to tools
    verification_scripts = [
        "verify_modular_components.py",
        "verify_ai_enhancements_complete.py",
        "verify_enhancements.py",
    ]

    for script in verification_scripts:
        move_file_if_exists(WORKSPACE_ROOT / script, scripts_dir / "tools" / script)

    print("\n✅ Workspace organization completed!")
    print("📊 Organized files into:")
    print("   📚 docs/")
    print("   🚀 launchers/")
    print("   🔧 scripts/")
    print("   🧪 tests/")
    print("   🎯 examples/")
    print("   💾 data/")
    print("   🗄️ archive/")
    print("   🏗️ src/aetherra/")


if __name__ == "__main__":
    main()
