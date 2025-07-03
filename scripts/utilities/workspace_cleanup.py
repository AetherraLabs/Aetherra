#!/usr/bin/env python3
"""
aetherra Project Workspace Cleanup and Organization Script
===========================================================

This script will clean up and organize the cluttered root directory by:
1. Moving files into appropriate folders
2. Removing duplicate/unnecessary files
3. Creating a clean, navigable structure
"""

import json
import os
import shutil
from pathlib import Path


def create_directories():
    """Create organized directory structure"""
    dirs_to_create = [
        "documentation/reports",
        "documentation/guides",
        "documentation/status",
        "documentation/changelogs",
        "testing/integration",
        "testing/unit",
        "testing/demos",
        "testing/verification",
        "archive/old_launchers",
        "archive/old_demos",
        "archive/old_tests",
        "scripts/deployment",
        "scripts/utilities",
        "scripts/testing",
        "config/requirements",
        "config/project",
        "temp/old_files",
    ]

    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")


def move_documentation_files():
    """Move documentation files to organized folders"""

    # Status and completion reports
    status_files = [
        "AGENT_ARCHIVE_IMPLEMENTATION_COMPLETE.md",
        "AGENT_BEHAVIOR_IMPLEMENTATION_COMPLETE.md",
        "AI_OS_IMPLEMENTATION_COMPLETE.md",
        "CHANGE_MANAGEMENT_IMPLEMENTATION_COMPLETE.md",
        "CLI_REVOLUTION_COMPLETE.md",
        "CODEBASE_AUDIT_COMPLETE.md",
        "CORE_PLUGINS_ERRORS_FIXED.md",
        "DEVELOPER_ONBOARDING_SYSTEM_IMPLEMENTATION.md",
        "DUPLICATE_CLEANUP_COMPLETE.md",
        "ENHANCED_NEUROPLEX_INTEGRATION_REPORT.md",
        "ENHANCED_PARSING_COMPLETE.md",
        "ERROR_CORRECTION_COMPLETE.md",
        "FINAL_ORGANIZATION_STATUS.md",
        "FINAL_STATUS_REPORT.md",
        "GITHUB_LINKS_FINAL_FIX_COMPLETE.md",
        "IMPLEMENTATION_COMPLETE.md",
        "INTERPRETER_MODULARIZATION_COMPLETE.md",
        "MEMORY_LOGGER_FIXES_COMPLETE.md",
        "MEMORY_MODULARIZATION_COMPLETE.md",
        "MISSION_ACCOMPLISHED.md",
        "MISSION_COMPLETE_AGENT_ARCHIVE.md",
        "MODULARIZATION_COMPLETE.md",
        "aetherra_FINAL_STATUS.md",
        "aetherra_FIXES_COMPLETE.md",
        "aetherra_FOLDER_FIXES_COMPLETE.md",
        "NEUROHUB_IMPLEMENTATION_COMPLETE.md",
        "NEUROHUB_LAUNCH_READY.md",
        "NEUROPLEX_LAUNCH_RESOLUTION_COMPLETE.md",
        "NEUROPLEX_TEST_RESULTS_COMPLETE.md",
        "PERFORMANCE_ENHANCEMENT_COMPLETE.md",
        "PERFORMANCE_FIXES_COMPLETE.md",
        "PERSONA_SYSTEM_COMPLETE.md",
        "PHASE_2_COMPLETE.md",
        "PHASE_2_FINAL_COMPLETION.md",
        "PHASE_2_IMPLEMENTATION.md",
        "PHASE_2_SUCCESS_REPORT.md",
        "PROTECTION_SYSTEM_COMPLETE.md",
        "REPOSITORY_PUSH_COMPLETE.md",
        "REPOSITORY_UPDATE_COMPLETE.md",
        "REVOLUTIONARY_BREAKTHROUGH_ANNOUNCEMENT.md",
        "REVOLUTIONARY_PERSONA_LAUNCH_COMPLETE.md",
        "SRC_CORE_FIXES_SUMMARY.md",
        "SRC_FOLDER_ERROR_CHECK_COMPLETE.md",
        "SRC_FOLDER_FIXES_COMPLETE.md",
        "SUCCESS_SUMMARY.md",
        "SYSTEM_TEST_RESULTS.md",
        "WEBSITE_DEPLOYMENT_COMPLETE.md",
        "WEBSITE_LIVE_SUCCESS.md",
        "WORKSPACE_ERRORS_FIXED.md",
        "WORKSPACE_OPTIMIZATION_COMPLETE.md",
        "WORKSPACE_REORGANIZATION_PHASE1_COMPLETE.md",
    ]

    # Analysis and technical reports
    report_files = [
        "AGENT_ARCHIVE_REPLAY_SYSTEM.md",
        "CHAT_ENHANCEMENT_REPORT.md",
        "CLI_FIXES_SUMMARY.md",
        "DEEP_ANALYSIS_COMPLETE_SUMMARY.md",
        "DEPENDENCIES_ANALYSIS.md",
        "DNS_STATUS.md",
        "ENHANCED_PARSING_STATUS.md",
        "GITHUB_LINKS_FIXED.md",
        "GITHUB_REDIRECT_INVESTIGATION.md",
        "GITHUB_REDIRECT_TROUBLESHOOTING.md",
        "LANGUAGE_IDENTITY_STATUS.md",
        "MEMORY_MODULARIZATION_SUMMARY.md",
        "MODULARIZATION_SUMMARY.md",
        "aetherra_GRAMMAR_ANALYSIS.md",
        "PLUGIN_ENHANCEMENT_REPORT.md",
        "REDIRECT_ISSUE_SOLVED.md",
        "STRUCTURE_ANALYSIS.md",
    ]

    # Guides and protocols
    guide_files = [
        "CHANGE_MANAGEMENT_PROTOCOL.md",
        "DOMAIN_SETUP_GUIDE.md",
        "DUPLICATE_CLEANUP_PLAN.md",
        "IMPLEMENTATION_CHECKLIST.md",
        "aetherra_MANIFESTO_V3_UPDATE_COMPLETE.md",
        "PROGRESS_TRACKER.md",
        "PROJECT_OVERVIEW.md",
        "WORKSPACE_REORGANIZATION_PLAN.md",
    ]

    # Move files to appropriate directories
    for file in status_files:
        if Path(file).exists():
            shutil.move(file, f"documentation/status/{file}")
            print(f"📄 Moved {file} to documentation/status/")

    for file in report_files:
        if Path(file).exists():
            shutil.move(file, f"documentation/reports/{file}")
            print(f"📊 Moved {file} to documentation/reports/")

    for file in guide_files:
        if Path(file).exists():
            shutil.move(file, f"documentation/guides/{file}")
            print(f"📋 Moved {file} to documentation/guides/")

    # Move CHANGELOG
    if Path("CHANGELOG.md").exists():
        shutil.move("CHANGELOG.md", "documentation/changelogs/CHANGELOG.md")
        print("📝 Moved CHANGELOG.md to documentation/changelogs/")


def move_test_files():
    """Move test files to organized testing folders"""

    # Integration tests
    integration_tests = [
        "test_agent_integration.py",
        "test_backward_compatibility.py",
        "test_enhanced_neuroplex_integration.py",
        "test_aetherra_integration.py",
        "test_aetherra_integration_fixed.py",
        "test_neuroplex_system.py",
        "test_phase2_systems.py",
        "test_phase2_verification.py",
        "test_syntax_integration.py",
    ]

    # Unit tests
    unit_tests = [
        "test_cli_fixes.py",
        "test_core_fixes.py",
        "test_enhanced_interpreter.py",
        "test_grammar_parser.py",
        "test_memory_logger_fixes.py",
        "test_memory_modular.py",
        "test_modern_parser.py",
        "test_modular_interpreter.py",
        "test_modular_syntax.py",
        "test_parser_direct.py",
        "test_performance_fixes.py",
        "test_plugin_discovery.py",
        "test_runtime_system.py",
        "test_src_core_fixes.py",
        "test_src_folder.py",
        "test_syntax_tree.py",
    ]

    # Demo/verification tests
    demo_tests = [
        "test_and_launch_neuroplex.py",
        "test_comprehensive_parsing.py",
        "test_aetherra_complete.py",
        "test_aetherra_comprehensive.py",
        "test_neuroplex_final.py",
        "test_neuroplex_gui.py",
        "test_neuro_chat.py",
        "test_phase2_basic.py",
    ]

    # Quick tests and verification
    verification_tests = [
        "quick_interpreter_test.py",
        "quick_memory_validation.py",
        "quick_runtime_test.py",
        "quick_test.py",
        "quick_test_aetherra.py",
        "simple_core_test.py",
        "simple_memory_test.py",
        "simple_plugin_test.py",
        "simple_syntax_test.py",
        "final_comprehensive_verification.py",
        "final_error_check.py",
        "final_aetherra_verification.py",
        "final_verification.py",
        "final_verification_test.py",
        "comprehensive_error_check.py",
    ]

    # Move test files
    for test in integration_tests:
        if Path(test).exists():
            shutil.move(test, f"testing/integration/{test}")
            print(f"🔗 Moved {test} to testing/integration/")

    for test in unit_tests:
        if Path(test).exists():
            shutil.move(test, f"testing/unit/{test}")
            print(f"🧪 Moved {test} to testing/unit/")

    for test in demo_tests:
        if Path(test).exists():
            shutil.move(test, f"testing/demos/{test}")
            print(f"🎭 Moved {test} to testing/demos/")

    for test in verification_tests:
        if Path(test).exists():
            shutil.move(test, f"testing/verification/{test}")
            print(f"✅ Moved {test} to testing/verification/")


def move_demo_files():
    """Move demo files to archive or appropriate locations"""

    demo_files = [
        "agent_archive_demo.py",
        "COMPLETE_DEBUG_DEMO.py",
        "DEEP_ANALYSIS_COMPLETE.py",
        "demo_aetherra.py",
        "enhanced_parsing_demo.py",
        "implementation_demo.py",
        "aetherra_ai_os_complete.py",
        "aetherra_ai_os_demo.py",
        "aetherra_persona_demo.py",
        "aetherra_plugin_demo.py",
        "aetherra_revolutionary_demo.py",
        "performance_enhancement_demo.py",
        "performance_revolution_demo.py",
        "phase2_comprehensive_demo.py",
        "phase2_final_demo.py",
        "simple_ui_demo.py",
        "ui_foundation_demo.py",
        "neuro_chat_standalone.py",
    ]

    for demo in demo_files:
        if Path(demo).exists():
            shutil.move(demo, f"archive/old_demos/{demo}")
            print(f"🎪 Moved {demo} to archive/old_demos/")


def move_launcher_files():
    """Move launcher files to archive (keeping only the main one)"""

    old_launchers = [
        "aetherra.py",
        "aetherra_ai_os_launcher.py",
        "aetherra_cli.py",
        "aetherra_persona_cli.py",
        "aetherra_persona_interpreter.py",
        "aetherra_plugin_cli.py",
        "aetherra_unified_cli.py",
    ]

    for launcher in old_launchers:
        if Path(launcher).exists():
            shutil.move(launcher, f"archive/old_launchers/{launcher}")
            print(f"🚀 Moved {launcher} to archive/old_launchers/")


def move_script_files():
    """Move script files to organized script folders"""

    # Deployment scripts
    deployment_scripts = [
        "commit.bat",
        "diagnose-github-links.bat",
        "force-cache-clear.bat",
        "github_upload_commands.sh",
        "overview.bat",
        "protect.ps1",
        "test-domain.ps1",
        "verify-deployment.bat",
        "verify-deployment.ps1",
        "verify-domain-setup.ps1",
    ]

    # Utility scripts
    utility_scripts = [
        "final_cleanup.py",
        "fix_demo.py",
        "organize_workspace.py",
        "IMPORT_FIX_COMPLETE.py",
    ]

    for script in deployment_scripts:
        if Path(script).exists():
            shutil.move(script, f"scripts/deployment/{script}")
            print(f"🛠️ Moved {script} to scripts/deployment/")

    for script in utility_scripts:
        if Path(script).exists():
            shutil.move(script, f"scripts/utilities/{script}")
            print(f"🔧 Moved {script} to scripts/utilities/")


def move_config_files():
    """Move configuration files to config folders"""

    # Requirements files
    req_files = [
        "requirements_dev.txt",
        "requirements_enhanced.txt",
        "requirements_fixed.txt",
        "requirements_minimal.txt",
        "playground_requirements.txt",
    ]

    # Project config files
    project_files = ["package.json", "pyproject.toml"]

    for req in req_files:
        if Path(req).exists():
            shutil.move(req, f"config/requirements/{req}")
            print(f"📦 Moved {req} to config/requirements/")

    for proj in project_files:
        if Path(proj).exists():
            shutil.move(proj, f"config/project/{proj}")
            print(f"⚙️ Moved {proj} to config/project/")


def move_data_files():
    """Move data files to temp folder if they're old"""

    old_data_files = [
        "environment_report.txt",
        "error_analysis_report.txt",
        "goals_store.json",
        "memory_store.json",
        "aetherra_functions.json",
        "plugin_test_output.txt",
        "repl_test_input.txt",
        "simple_test.aether",
        "test_script.aether",
    ]

    for data_file in old_data_files:
        if Path(data_file).exists():
            shutil.move(data_file, f"temp/old_files/{data_file}")
            print(f"📁 Moved {data_file} to temp/old_files/")


def cleanup_html_files():
    """Move HTML files to website folder"""
    if Path("live_site_content.html").exists():
        if not Path("website").exists():
            Path("website").mkdir()
        shutil.move("live_site_content.html", "website/live_site_content.html")
        print("🌐 Moved live_site_content.html to website/")


def main():
    """Main cleanup function"""
    print("🧹 aetherra Workspace Cleanup Starting...")
    print("=" * 50)

    # Create directory structure
    print("\n📁 Creating organized directory structure...")
    create_directories()

    # Move different types of files
    print("\n📚 Moving documentation files...")
    move_documentation_files()

    print("\n🧪 Moving test files...")
    move_test_files()

    print("\n🎪 Moving demo files...")
    move_demo_files()

    print("\n🚀 Moving old launcher files...")
    move_launcher_files()

    print("\n🛠️ Moving script files...")
    move_script_files()

    print("\n⚙️ Moving configuration files...")
    move_config_files()

    print("\n📁 Moving old data files...")
    move_data_files()

    print("\n🌐 Moving HTML files...")
    cleanup_html_files()

    print("\n" + "=" * 50)
    print("✅ Workspace cleanup completed!")
    print("\n📊 New organized structure:")
    print("├── documentation/")
    print("│   ├── reports/")
    print("│   ├── guides/")
    print("│   ├── status/")
    print("│   └── changelogs/")
    print("├── testing/")
    print("│   ├── integration/")
    print("│   ├── unit/")
    print("│   ├── demos/")
    print("│   └── verification/")
    print("├── archive/")
    print("│   ├── old_launchers/")
    print("│   └── old_demos/")
    print("├── scripts/")
    print("│   ├── deployment/")
    print("│   └── utilities/")
    print("├── config/")
    print("│   ├── requirements/")
    print("│   └── project/")
    print("└── temp/")
    print("    └── old_files/")

    print("\n🎯 Key files remaining in root:")
    print("- README.md")
    print("- LICENSE")
    print("- requirements.txt (main)")
    print("- aetherra_launcher.py (main launcher)")
    print("- neuroplex.bat / neuroplex.ico")
    print("- Core folders: src/, core/, data/, etc.")


if __name__ == "__main__":
    main()
