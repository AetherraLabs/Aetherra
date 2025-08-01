#!/usr/bin/env python3
"""
🧠 Aetherra Self-Organizing Intelligence Launcher
Convenient launcher for the file intelligence and monitoring systems.

This script provides easy access to all self-organizing capabilities:
- File system scanning and analysis
- Real-time monitoring and optimization
- Autonomous organization suggestions
- .aether script orchestration
"""

import os
import sys
from pathlib import Path

# Add Aetherra core to path
aetherra_root = Path(__file__).parent.parent
sys.path.insert(0, str(aetherra_root / "core"))
sys.path.insert(0, str(aetherra_root / "tools"))

from core.aetherra_self_organizer import AetherraFileIntelligence
from tools.aetherra_file_watcher import AetherraFileWatcherDaemon


def main():
    """Main launcher for Aetherra self-organizing intelligence."""
    import argparse

    parser = argparse.ArgumentParser(
        description="🧠 Aetherra Self-Organizing Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan                    # Scan all project files
  %(prog)s analyze                 # Perform system health analysis
  %(prog)s monitor                 # Start real-time file monitoring
  %(prog)s optimize --dry-run      # Preview optimizations
  %(prog)s optimize --execute      # Execute safe optimizations
        """,
    )

    # Main actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--scan", action="store_true", help="Scan project files and build registry"
    )
    action_group.add_argument(
        "--analyze", action="store_true", help="Perform comprehensive system analysis"
    )
    action_group.add_argument(
        "--monitor", action="store_true", help="Start real-time file system monitoring"
    )
    action_group.add_argument(
        "--optimize", action="store_true", help="Execute optimization suggestions"
    )

    # Options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing (default for --optimize)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute optimizations (use with caution)",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument("--config", help="Configuration file for monitoring daemon")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    import logging

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    # Initialize the intelligence system
    project_root = os.path.abspath(args.project_root)
    intelligence = AetherraFileIntelligence(project_root)

    print("🧠 Aetherra Self-Organizing Intelligence System")
    print(f"📂 Project Root: {project_root}")
    print("=" * 60)

    try:
        if args.scan:
            print("🔍 Scanning project files...")
            registry = intelligence.scan_project_files()
            print(f"✅ Scan complete: {len(registry)} files analyzed")
            print(f"📊 Database: {intelligence.db_path}")
            print(f"📋 Live Index: {intelligence.live_index_path}")

        elif args.analyze:
            print("🧠 Performing comprehensive system analysis...")

            # Ensure we have a current scan
            if not intelligence.file_registry:
                print("📂 No registry found, scanning first...")
                intelligence.scan_project_files()

            analysis = intelligence.analyze_system_health()

            print("\n📊 SYSTEM ANALYSIS RESULTS:")
            print(f"  📁 Total files analyzed: {analysis.total_files}")
            print(f"  🔍 Orphaned files: {len(analysis.orphaned_files)}")
            print(f"  📋 Duplicate logic instances: {len(analysis.duplicate_logic)}")
            print(f"  ⚠️  Broken imports: {len(analysis.broken_imports)}")
            print(
                f"  💡 Optimization suggestions: {len(analysis.optimization_suggestions)}"
            )
            print(f"  🎯 Critical files: {len(analysis.critical_files)}")

            if analysis.orphaned_files:
                print(f"\n🔍 Orphaned files found:")
                for orphan in analysis.orphaned_files[:5]:  # Show first 5
                    print(f"    • {orphan}")
                if len(analysis.orphaned_files) > 5:
                    print(f"    ... and {len(analysis.orphaned_files) - 5} more")

            if analysis.optimization_suggestions:
                print(f"\n💡 Optimization suggestions:")
                for suggestion in analysis.optimization_suggestions[:3]:  # Show first 3
                    print(
                        f"    • {suggestion['type']}: {suggestion.get('reason', 'No reason provided')}"
                    )
                if len(analysis.optimization_suggestions) > 3:
                    print(
                        f"    ... and {len(analysis.optimization_suggestions) - 3} more"
                    )

            print(f"\n📝 Detailed logs: {intelligence.evolution_log_path}")

        elif args.monitor:
            print("👁️  Starting real-time file system monitoring...")
            daemon = AetherraFileWatcherDaemon(project_root, args.config)
            print("🚀 Monitoring daemon started. Press Ctrl+C to stop.")
            daemon.start()

        elif args.optimize:
            if not intelligence.file_registry:
                print("📂 No registry found, scanning first...")
                intelligence.scan_project_files()

            print("🛠️  Analyzing optimization opportunities...")
            analysis = intelligence.analyze_system_health()

            if not analysis.optimization_suggestions:
                print("✅ No optimizations needed - system is well organized!")
                return

            # Default to dry run unless explicitly told to execute
            dry_run = not args.execute

            if dry_run:
                print("🔍 DRY RUN MODE - Preview of potential changes:")
            else:
                print("⚠️  EXECUTION MODE - Making actual changes:")
                confirm = input(
                    "Are you sure you want to execute optimizations? (yes/no): "
                )
                if confirm.lower() != "yes":
                    print("❌ Optimization cancelled.")
                    return

            results = intelligence.execute_safe_optimization(
                analysis.optimization_suggestions, dry_run=dry_run
            )

            print("\n🛠️  OPTIMIZATION RESULTS:")
            print(f"  ✅ Executed: {len(results['executed'])}")
            print(f"  ⏭️  Skipped: {len(results['skipped'])}")
            print(f"  ❌ Errors: {len(results['errors'])}")

            if results["executed"]:
                print("\n✅ Executed optimizations:")
                for item in results["executed"]:
                    print(
                        f"    • {item.get('type', 'Unknown')}: {item.get('reason', 'No details')}"
                    )

            if results["skipped"]:
                print("\n⏭️  Skipped (manual review required):")
                for item in results["skipped"]:
                    print(f"    • {item['reason']}")

            if results["errors"]:
                print("\n❌ Errors encountered:")
                for item in results["errors"]:
                    print(f"    • {item['error']}")

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
