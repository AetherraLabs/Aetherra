#!/usr/bin/env python3
"""
Organize directory structure by moving files to appropriate locations.

SPDX-License-Identifier: GPL-3.0-or-later
SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""

import shutil
from pathlib import Path


def organize_directory_structure(
    root_dir: Path, dry_run: bool = True
) -> dict[str, list[str]]:
    """
    Organize directory structure by moving files to appropriate locations.

    Returns a dictionary mapping operation types to lists of actions taken.
    """
    actions = {
        "moved_tests": [],
        "moved_logs": [],
        "moved_data": [],
        "moved_configs": [],
        "moved_artifacts": [],
        "created_dirs": [],
        "cleaned_temp": [],
        "errors": [],
    }

    # Create necessary directories
    dirs_to_create = [
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "data/logs",
        "data/databases",
        "data/artifacts",
        "config/environments",
        "tmp",
    ]

    for dir_path in dirs_to_create:
        full_path = root_dir / dir_path
        if not full_path.exists():
            if not dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
            actions["created_dirs"].append(str(dir_path))

    # Move test files from root to tests/
    test_files = [
        "test_consciousness_dashboards.py",
        "test_consciousness_integration.py",
        "test_hub_plugins.py",
        "test_multiple_plugins.py",
        "test_plugin_installation.py",
        "test_qiskit_direct.py",
        "test_quantum_config.py",
        "test_real_backend.py",
        "test_real_llm.py",
        "test_shared_registry.py",
    ]

    for test_file in test_files:
        src = root_dir / test_file
        if src.exists():
            # Determine target directory based on file content/name
            if "integration" in test_file or "hub" in test_file:
                target_dir = "tests/integration"
            elif "consciousness" in test_file or "quantum" in test_file:
                target_dir = "tests/unit"
            else:
                target_dir = "tests/unit"

            dst = root_dir / target_dir / test_file

            if not dry_run:
                try:
                    shutil.move(str(src), str(dst))
                    actions["moved_tests"].append(f"{test_file} -> {target_dir}")
                except Exception as e:
                    actions["errors"].append(f"Failed to move {test_file}: {e}")
            else:
                actions["moved_tests"].append(f"{test_file} -> {target_dir}")

    # Move log files to data/logs/
    log_files = ["aetherra_os.log", "lyrixa_basic.log", "lyrixa_system.log"]

    for log_file in log_files:
        src = root_dir / log_file
        if src.exists():
            dst = root_dir / "data" / "logs" / log_file
            if not dry_run:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))
                    actions["moved_logs"].append(f"{log_file} -> data/logs/")
                except Exception as e:
                    actions["errors"].append(f"Failed to move {log_file}: {e}")
            else:
                actions["moved_logs"].append(f"{log_file} -> data/logs/")

    # Move database files to data/databases/
    db_files = [
        "analytics_insights.db",
        "concept_clusters.db",
        "episodic_timeline.db",
        "fractal_memory.db",
        "gui_memory.db",
        "introspection.db",
        "lyrixa_improvement.db",
        "lyrixa_memory.db",
        "lyrixa_orchestrator.db",
        "memory_pulse.db",
        "reasoning_engine.db",
        "self_improvement.db",
    ]

    for db_file in db_files:
        src = root_dir / db_file
        if src.exists():
            dst = root_dir / "data" / "databases" / db_file
            if not dry_run:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))
                    actions["moved_data"].append(f"{db_file} -> data/databases/")
                except Exception as e:
                    actions["errors"].append(f"Failed to move {db_file}: {e}")
            else:
                actions["moved_data"].append(f"{db_file} -> data/databases/")

    # Move configuration files to config/
    config_files = [
        "config.json",
        "self_model.json",
        "advanced_project_intelligence.json",
        "lyrixa_intelligence.json",
    ]

    for config_file in config_files:
        src = root_dir / config_file
        if src.exists():
            dst = root_dir / "config" / config_file
            if not dry_run:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))
                    actions["moved_configs"].append(f"{config_file} -> config/")
                except Exception as e:
                    actions["errors"].append(f"Failed to move {config_file}: {e}")
            else:
                actions["moved_configs"].append(f"{config_file} -> config/")

    # Move artifact files to data/artifacts/
    artifact_files = [
        "coverage.json",
        "coverage.xml",
        "bandit.sarif",
        "pipaudit.sarif",
        "gate_results.json",
        "parse_baseline_local.json",
        "parse_baseline_sample.json",
        "phase2_integration_report.json",
        "workflow_failures_postpush.json",
        "workflow_failures_sample.json",
        "aether_static_report.md",
        "ui_standards_report.md",
        "gate_sign_off.md",
        "workflow_failures.md",
        "workflow_failures_postpush.md",
        "workflow_failures_sample.md",
    ]

    for artifact_file in artifact_files:
        src = root_dir / artifact_file
        if src.exists():
            dst = root_dir / "data" / "artifacts" / artifact_file
            if not dry_run:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))
                    actions["moved_artifacts"].append(
                        f"{artifact_file} -> data/artifacts/"
                    )
                except Exception as e:
                    actions["errors"].append(f"Failed to move {artifact_file}: {e}")
            else:
                actions["moved_artifacts"].append(f"{artifact_file} -> data/artifacts/")

    # Clean up temporary files that can be safely removed
    temp_patterns = [
        ".coverage-baseline",
        "diff_output.txt",
        "ruff_*.txt",
        "spdx_*.txt",
        "spdx_report.txt",
        "root_cleanup_*.json",
        "live_file_index.json",
        "wf_sample.json",
    ]

    for pattern in temp_patterns:
        if "*" in pattern:
            for file_path in root_dir.glob(pattern):
                if file_path.is_file():
                    if not dry_run:
                        try:
                            file_path.unlink()
                            actions["cleaned_temp"].append(f"Removed {file_path.name}")
                        except Exception as e:
                            actions["errors"].append(
                                f"Failed to remove {file_path.name}: {e}"
                            )
                    else:
                        actions["cleaned_temp"].append(f"Would remove {file_path.name}")
        else:
            file_path = root_dir / pattern
            if file_path.exists():
                if not dry_run:
                    try:
                        file_path.unlink()
                        actions["cleaned_temp"].append(f"Removed {pattern}")
                    except Exception as e:
                        actions["errors"].append(f"Failed to remove {pattern}: {e}")
                else:
                    actions["cleaned_temp"].append(f"Would remove {pattern}")

    return actions


def main():
    """Organize the Aetherra project directory structure."""
    root_dir = Path(__file__).parent.parent
    print(f"Organizing directory structure in: {root_dir}")

    # First do a dry run
    print("\n=== DRY RUN ===")
    dry_actions = organize_directory_structure(root_dir, dry_run=True)

    total_changes = sum(
        len(actions) for key, actions in dry_actions.items() if key != "errors"
    )
    print(f"\nSummary of planned changes: {total_changes} total operations")

    for action_type, actions in dry_actions.items():
        if actions:
            print(f"\n{action_type.replace('_', ' ').title()}:")
            for action in actions[:10]:  # Show first 10 items
                print(f"  - {action}")
            if len(actions) > 10:
                print(f"  ... and {len(actions) - 10} more")

    if dry_actions["errors"]:
        print(f"\nPotential errors: {len(dry_actions['errors'])}")
        return

    # Ask for confirmation
    print(
        f"\nThis will make {total_changes} changes to organize the directory structure."
    )
    response = input("Proceed with actual changes? (y/N): ").lower().strip()

    if response != "y":
        print("Operation cancelled.")
        return

    # Perform actual organization
    print("\n=== APPLYING CHANGES ===")
    real_actions = organize_directory_structure(root_dir, dry_run=False)

    total_applied = sum(
        len(actions) for key, actions in real_actions.items() if key != "errors"
    )
    print(f"\nCompleted {total_applied} operations successfully!")

    if real_actions["errors"]:
        print(f"\nErrors encountered: {len(real_actions['errors'])}")
        for error in real_actions["errors"]:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
