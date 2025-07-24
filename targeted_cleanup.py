#!/usr/bin/env python3
"""
🧹 TARGETED AETHERRA CLEANUP
============================

Moves clearly identified legacy/unused files to Unused folder.
This is a conservative cleanup focusing on obvious legacy files.
"""

import os
import shutil
from datetime import datetime


def get_legacy_files_to_move():
    """Get list of specific legacy files and patterns to move"""
    return [
        # Old backup directories
        "Aetherra_backup_20250712_184525/",
        ".backups/",
        ".safe_backups/",
        "test_backups/",
        "backups/",
        "archive/",
        # Old demo/test files (root level)
        "add_sample_goals.py",
        "complete_self_improvement_demo.py",
        "comprehensive_housekeeping_system.py",
        "comprehensive_plugin_fixer.py",
        "dark_theme_status.py",
        "debug_ollama.py",
        "demo_memory_system.py",  # Keep the new integration demo
        "direct_plugin_test.py",
        "EMERGENCY_CLEANUP.py",
        "enhanced_api_server.py",
        "enhanced_lyrixa_chat.py",
        "enhanced_plugin_capabilities.py",
        "enhanced_plugin_chain_cleaner.py",
        "enhanced_self_improvement_server.py",
        "explorer_api.py",
        "fast_api_server.py",
        "fast_lyrixa_init.py",
        "final_comprehensive_validation.py",
        "final_integration_test.py",
        "final_plugin_validator.py",
        "FINAL_VERIFICATION_COMPLETE.py",
        "fix_neuro_branding.py",
        "fix_plugin_schemas.py",
        "fix_plugin_system.py",
        "gui_proof_guide.py",
        "implementation_summary.py",
        "launcher_ui_verification.py",
        "LAUNCHER_UPDATE_COMPLETE.py",
        "lightweight_goal_tracker.py",
        "llm_gui_injection_complete_demo.py",
        "log_agent_decisions.py",
        "lyrixa_bot.py",
        "lyrixa_bot_backup.py",
        "lyrixa_intelligence_api_server.py",
        "lyrixa_plugin_editor_fixes_demo.py",
        "memory_core_fix.py",
        "memory_plugin_chain_cleaner.py",
        "meta_reasoning_integration_example.py",
        "minimal_test_api.py",
        "minimal_ui_test_server.py",
        "monitor_ai_agents.py",
        "move_plugins_to_lyrixa_plugins.py",
        "optimization_summary.py",
        "phase1_auto_population_demo.py",
        "plugin_generation_flow_demo.py",
        "POST_CLEANUP.py",
        "production_lyrixa_chat.py",
        "quick_lyrixa_launcher.py",
        "quick_server_test.py",
        "quick_test_advanced.py",
        "run_self_improvement_api.py",
        "show_agent_proof.py",
        "simple_bootstrap_test.py",
        "simple_chat_test.py",
        "simple_gui_launcher.py",
        "simple_plugin_integration_test.py",
        "simple_plugin_test.py",
        "startup_guide.py",
        "ULTIMATE_FINAL_ACHIEVEMENT.py",
        "validate_plugin_integration.py",
        "validate_recovery.py",
        "verify_goals_fix.py",
        "verify_meta_reasoning.py",
        "verify_plugin_editor_final.py",
        "verify_requirements.py",
        "verify_stage3.py",
        "verify_stage3_systems.py",
        "working_plugin_sandbox_tester.py",
        "world_class_goal_tracker.py",
        # Old launchers
        "aetherra_hybrid_launcher.py",
        "aetherra_launcher_new.py",  # Keep main aetherra_launcher.py for now
        # Old batch files
        "build-and-deploy.bat",
        "diagnose_gui.bat",
        "setup_python_env.bat",
        "start_enhanced_server.bat",
        "lyrixa.bat",
        # Web/HTML files (if not actively used)
        "404.html",
        "index.html",
        "browserconfig.xml",
        "CNAME",
        ".nojekyll",
        # SVG/media files
        "favicon.svg",
        "neural-bg.svg",
        "vite.svg",
        # Old documentation (keeping main docs)
        "ADVANCED_CODE_EDITING_IMPLEMENTATION.md",
        "AETHERRA_CORE_ORGANIZATION_COMPLETE.md",
        "aetherra_consciousness_appendix.md",
        "AGENTS_TAB_INTEGRATION_COMPLETE.md",
        "ANALYTICS_DASHBOARD_FIX.md",
        "API_SERVER_IMPORT_FIX_COMPLETE.md",
        "API_SERVER_LAUNCHER_INTEGRATION.md",
        "API_SERVER_STARTUP_FIX_COMPLETE.md",
        "API_STARTUP_FIX_SUMMARY.md",
        "CHAT_ENHANCEMENTS_COMPLETE.md",
        "CHAT_INTELLIGENCE_PATCH_COMPLETE.md",
        "CIRCULAR_IMPORT_FIX_COMPLETE.md",
        "COMMIT_MESSAGE.md",
        "COMPLETION_SUMMARY.md",
        "COMPREHENSIVE_UPDATE_COMMIT.md",
        "ENHANCED_PLUGIN_INTELLIGENCE_COMPLETE.md",
        "FINAL_FEATURE_SUMMARY.md",
        "FINAL_INTEGRATION_SUMMARY.py",
        "GOAL_FORECASTER_ENHANCEMENTS.md",
        "GOAL_TRACKER_TAB_COMPLETE.md",
        "GUI_LAUNCHER_INTEGRATION.md",
        "HYBRID_UI_COMPLETE.md",
        "HYBRID_UI_IMPLEMENTATION.md",
        "HYBRID_UI_INTEGRATION_COMPLETE.md",
        "HYBRID_UI_LAUNCHER_DOCUMENTATION.md",
        "INTELLIGENCE_METRICS_FIXED.md",
        "LAUNCHER_ERROR_RESOLVED.md",
        "LAUNCHER_TESTING_RESULTS.md",
        "LAUNCHER_TROUBLESHOOTING.md",
        "LAUNCHER_USER_GUIDE.md",
        "LYRIXA_AGENT_INTEGRATION_SUMMARY.md",
        "LYRIXA_PERSONALITY_PHASE3_PROPOSAL.md",
        "LYRIXA_PLUGIN_EDITOR_FIXES_COMPLETE.md",
        "LYRIXA_SELF_EXTENDING_GUI_SYSTEM.md",
        "MEMORY_VIEWER_TAB_COMPLETE.md",
        "META_REASONING_COMPLETE_SUMMARY.md",
        "META_REASONING_PHASE_I_COMPLETE.md",
        "METRICS_COMPLETE_FIX.md",
        "MODULAR_LAUNCHER_DOCUMENTATION.md",
        "MODULAR_VALIDATION_COMPLETE.md",
        "PERFORMANCE_DASHBOARD_COMPLETE.md",
        "PERSONALITY_ARCHITECTURE_REFACTORING.md",
        "PHASE1_AUTO_POPULATION_COMPLETE.md",
        "PHASE_2_INTEGRATION_COMPLETE.md",
        "PLUGIN_DISCOVERY_IMPLEMENTATION_COMPLETE.md",
        "PLUGIN_DISCOVERY_INTEGRATION_COMPLETE.md",
        "PLUGIN_EDITOR_GUI_COMPLETE.md",
        "PLUGIN_EDITOR_INTEGRATION_COMPLETE.md",
        "PLUGIN_EDITOR_TAB_COMPLETE.md",
        "PLUGIN_GENERATION_FLOW_COMPLETE.md",
        "PLUGIN_MEMORY_FIXES_COMPLETE.md",
        "PLUGIN_SYSTEM_REPAIR_COMPLETE.md",
        "PLUGIN_SYSTEM_RESOLUTION_COMPLETE.md",
        "PROJECT_STRUCTURE_UPDATED.md",
        "PROPOSE_CHANGES_FIX_COMPLETE.md",
        "QUICK_START_SELF_EXTENDING.md",
        "REPOSITORY_PUSH_COMPLETE.md",
        "SELF_EXTENDING_FIX_COMPLETE.md",
        "SELF_EXTENDING_GUI_USAGE_GUIDE.md",
        "SELF_IMPROVEMENT_ENHANCEMENTS.md",
        "SELF_IMPROVEMENT_TAB_COMPLETE.md",
        "SELF_REFLECTION_SYSTEM_COMPLETE.md",
        "STAGE3_DEPLOYMENT_SUCCESS.md",
        "STAGE_3_COMPLETION_SUMMARY.md",
        "UI_API_INTEGRATION_COMPLETE.md",
        "WEBSITE_DEPLOYMENT_FIX_COMPLETE.md",
        "WEBSITE_DEPLOYMENT_SIMPLIFIED.md",
        # Database files (old ones)
        "aetherra_introspection.db",
        "aetherra_self_improvement.db",
        "agent_orchestrator.db",
        "forecasts.db",
        "introspection.db",
        "lyrixa_chat_history.db",
        "lyrixa_context_memory.db",
        "lyrixa_enhanced_memory.db",
        "lyrixa_plugin_memory.db",
        "lyrixa_response_memory.db",
        "memory_manager.db",
        "plugin_analytics.db",
        "plugin_confidence.db",
        "plugin_index.db",
        "plugin_state_memory.db",
        "reasoning_engine.db",
        "self_improvement.db",
        "semantic_plugin_index.db",
        # JSON files (old ones)
        "agent_decisions_20250715_135322.json",
        "emotional_intelligence_demo_report_20250717_151204.json",
        "enhanced_plugin_metadata.json",
        "housekeeping_report_20250712_185022.json",
        "improvement_history.json",
        "latest_analysis.json",
        "lyrixa_intelligence.json",
        "multimodal_personality_demo_report_20250717_145126.json",
        "personality_demo_report_20250717_141416.md",
        "phase2_demo_report_20250717_143245.json",
        "phase2_demo_report_20250717_143328.json",
        "phase2_demo_report_20250717_155042.json",
        "phase31_demo_report_20250717_144439.json",
        "plugin_metadata.json",
        "plugin_usage_history.json",
        "social_learning_demo_report_20250717_153504.json",
        "social_learning_demo_report_20250717_154505.json",
        # Old directories
        "aetherra_hub/",
        "assets/",
        "config/",
        "continue/",
        "core/",  # Root level core, not Aetherra/core
        "data/",  # Root level data
        "demos/",
        "deployments/",
        "developer_tools/",
        "development/",
        "documentation/",
        "examples/",
        "lyrixa_plugins/",
        "media/",
        "operations/",
        "scripts/",  # Root level scripts
        "sdk/",
        "system/",  # Root level system
        "testing/",
        "tools/",
        "web/",
        # Hidden directories (old)
        ".aether/",
        ".aetherra/",
        ".plugin_history/",
        ".vite/",
        # Text files
        "complete_file_paths_20250709_114224.txt",
        "feature_status.txt",
        "project_tree_structure_20250709_114224.txt",
        # Log files
        "launcher_debug.log",
        # Misc
        "Aetherra_backup_20250712_184525_MANIFEST.md",
        "clear_plugin_chains.py",
        "configure_matplotlib.py",
        "package-lock.json",
        "plugin_chains_cleaned.flag",
        "requirements-security.txt",
        "setup_security.py",
        "validate_recovery.ps1",
        "validate_simple.ps1",
    ]


def move_to_unused(project_root: str, files_to_move: list) -> int:
    """Move files to Unused folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unused_dir = os.path.join(project_root, "Unused", f"legacy_cleanup_{timestamp}")

    os.makedirs(unused_dir, exist_ok=True)
    moved_count = 0

    print("🚀 Moving legacy files to Unused folder...")
    print(f"📁 Target: Unused/legacy_cleanup_{timestamp}/")
    print()

    for file_path in files_to_move:
        source = os.path.join(project_root, file_path)

        if not os.path.exists(source):
            continue

        # Create destination path
        dest = os.path.join(unused_dir, file_path)
        dest_dir = os.path.dirname(dest)

        try:
            os.makedirs(dest_dir, exist_ok=True)

            if os.path.isdir(source):
                shutil.move(source, dest)
                print(f"📁 Moved directory: {file_path}")
            else:
                shutil.move(source, dest)
                print(f"📄 Moved file: {file_path}")

            moved_count += 1

        except Exception as e:
            print(f"❌ Error moving {file_path}: {e}")

    return moved_count


def update_gitignore(project_root: str):
    """Update .gitignore to exclude Unused folder"""
    gitignore_path = os.path.join(project_root, ".gitignore")

    # Read current content
    content = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()

    # Add Unused folder if not present
    if "Unused/" not in content:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\\n# Legacy files moved during cleanup\\n")
            f.write("Unused/\\n")
        print("✅ Added Unused/ to .gitignore")
    else:
        print("ℹ️ Unused/ already in .gitignore")


def main():
    """Main cleanup function"""
    project_root = os.getcwd()
    print("🧹 AETHERRA PROJECT CLEANUP")
    print("=" * 50)
    print(f"📍 Project root: {project_root}")
    print()

    # Get files to move
    legacy_files = get_legacy_files_to_move()

    # Filter to only existing files
    existing_files = [
        f for f in legacy_files if os.path.exists(os.path.join(project_root, f))
    ]

    print(f"📋 Found {len(existing_files)} legacy files/folders to move:")
    for file_path in existing_files[:15]:  # Show first 15
        print(f"  • {file_path}")
    if len(existing_files) > 15:
        print(f"  ... and {len(existing_files) - 15} more")

    print()
    print("⚠️ This will move these files to the 'Unused' folder.")
    print("✅ Core project files and the new memory system will remain untouched.")

    response = input("\\nProceed with cleanup? (y/N): ").lower().strip()

    if response in ["y", "yes"]:
        moved_count = move_to_unused(project_root, existing_files)

        if moved_count > 0:
            print(f"\\n✅ Successfully moved {moved_count} legacy files!")
            update_gitignore(project_root)
            print("\\n🎯 Project cleanup complete! Your workspace is now cleaner.")
            print("💡 Only active files remain in the main directories.")
        else:
            print("\\n❌ No files were moved.")
    else:
        print("\\n❌ Cleanup cancelled.")


if __name__ == "__main__":
    main()
