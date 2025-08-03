#!/usr/bin/env python3
"""
🧠 Aetherra Real-Time File System Monitor
Live background daemon for autonomous file system intelligence.

Monitors file changes, plugin installations, and system events
to trigger autonomous reorganization and optimization.
"""

import json
import logging
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Import our main organizer
try:
    from ..core.aetherra_self_organizer import AetherraFileIntelligence
except ImportError:
    # Handle case where it's in a different location
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
    from aetherra_self_organizer import AetherraFileIntelligence

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AetherraFileWatcher(FileSystemEventHandler):
    """
    🔍 Intelligent File System Event Handler

    Responds to file system changes with intelligent analysis
    and autonomous optimization decisions.
    """

    def __init__(self, intelligence: AetherraFileIntelligence, config: Dict[str, Any]):
        self.intelligence = intelligence
        self.config = config

        # Tracking state
        self.pending_changes: Set[str] = set()
        self.last_analysis_time = 0
        self.analysis_interval = config.get("analysis_interval", 30)  # seconds
        self.batch_size = config.get("batch_size", 10)

        # File filters
        self.monitored_extensions = {".py", ".aether", ".json", ".md", ".yml", ".yaml"}
        self.ignored_patterns = {
            ".git",
            "__pycache__",
            ".pyc",
            "node_modules",
            ".vscode",
        }

        # Event handlers
        self.event_handlers: Dict[str, Callable] = {
            "file_added": self._handle_file_added,
            "file_modified": self._handle_file_modified,
            "file_deleted": self._handle_file_deleted,
            "plugin_installed": self._handle_plugin_installed,
            "system_event": self._handle_system_event,
        }

        # Background processing
        self._start_background_processor()

    def _should_process_file(self, file_path: str) -> bool:
        """Determine if a file should be processed."""
        path = Path(file_path)

        # Check extension
        if path.suffix not in self.monitored_extensions:
            return False

        # Check ignored patterns
        for pattern in self.ignored_patterns:
            if pattern in str(path):
                return False

        return True

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            logger.info(f"📁 New file detected: {event.src_path}")
            self.pending_changes.add(event.src_path)
            self._trigger_event("file_added", event.src_path)

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            logger.debug(f"✏️ File modified: {event.src_path}")
            self.pending_changes.add(event.src_path)
            self._trigger_event("file_modified", event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            logger.info(f"🗑️ File deleted: {event.src_path}")
            self._trigger_event("file_deleted", event.src_path)

    def on_moved(self, event: FileSystemEvent):
        """Handle file move events."""
        if not event.is_directory:
            if hasattr(event, "dest_path"):
                logger.info(f"[DISC] File moved: {event.src_path} -> {event.dest_path}")
                if self._should_process_file(event.dest_path):
                    self.pending_changes.add(event.dest_path)

    def _trigger_event(self, event_type: str, file_path: str):
        """Trigger appropriate event handler."""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type](file_path)
            except Exception as e:
                logger.error(f"Error handling {event_type} for {file_path}: {e}")

    def _handle_file_added(self, file_path: str):
        """Handle new file addition."""
        # Quick analysis of new file
        try:
            metadata = self.intelligence._analyze_file(Path(file_path))

            # Check if file seems misplaced
            suggested_dir = self.intelligence._suggest_directory(metadata)
            current_dir = os.path.dirname(file_path)

            if suggested_dir and suggested_dir != current_dir:
                logger.info(
                    f"💡 Suggestion: {file_path} might belong in {suggested_dir}"
                )

                # Auto-relocate if confidence is high and enabled
                if (
                    self.config.get("auto_relocate", False)
                    and metadata.risk_level == "low"
                ):
                    self._auto_relocate_file(file_path, suggested_dir)

        except Exception as e:
            logger.warning(f"Failed to analyze new file {file_path}: {e}")

    def _handle_file_modified(self, file_path: str):
        """Handle file modification."""
        # Update file registry if it exists
        if file_path in self.intelligence.file_registry:
            try:
                # Re-analyze the modified file
                updated_metadata = self.intelligence._analyze_file(Path(file_path))
                self.intelligence.file_registry[file_path] = updated_metadata

                # Check for new issues
                if updated_metadata.risk_level == "high":
                    logger.warning(
                        f"[WARN] High risk detected in modified file: {file_path}"
                    )

            except Exception as e:
                logger.warning(f"Failed to update metadata for {file_path}: {e}")

    def _handle_file_deleted(self, file_path: str):
        """Handle file deletion."""
        # Remove from registry
        if file_path in self.intelligence.file_registry:
            del self.intelligence.file_registry[file_path]

        # Check for broken dependencies
        self._check_broken_dependencies(file_path)

    def _handle_plugin_installed(self, plugin_info: str):
        """Handle plugin installation."""
        logger.info(f"🔌 Plugin event detected: {plugin_info}")

        # Trigger comprehensive re-scan
        self._schedule_full_analysis()

    def _handle_system_event(self, event_info: str):
        """Handle system-level events."""
        logger.info(f"[TOOL] System event: {event_info}")

        # Schedule analysis based on event type
        if "critical" in event_info.lower():
            self._schedule_immediate_analysis()
        else:
            self._schedule_full_analysis()

    def _check_broken_dependencies(self, deleted_file: str):
        """Check for dependencies that might be broken by file deletion."""
        broken_deps = []

        for file_path, metadata in self.intelligence.file_registry.items():
            if deleted_file in metadata.dependencies:
                broken_deps.append(file_path)

        if broken_deps:
            logger.warning(
                f"[WARN] Deletion of {deleted_file} may break dependencies in: {broken_deps}"
            )

    def _auto_relocate_file(self, file_path: str, target_dir: str):
        """Automatically relocate a file if safe to do so."""
        try:
            source_path = Path(file_path)
            target_path = Path(self.intelligence.project_root) / target_dir
            target_path.mkdir(parents=True, exist_ok=True)

            destination = target_path / source_path.name

            # Check if destination already exists
            if destination.exists():
                logger.warning(f"Cannot auto-relocate {file_path}: destination exists")
                return

            # Move the file
            source_path.rename(destination)
            logger.info(f"🎯 Auto-relocated {file_path} to {destination}")

            # Update registry
            if file_path in self.intelligence.file_registry:
                metadata = self.intelligence.file_registry[file_path]
                del self.intelligence.file_registry[file_path]
                metadata.path = str(destination)
                self.intelligence.file_registry[str(destination)] = metadata

        except Exception as e:
            logger.error(f"Failed to auto-relocate {file_path}: {e}")

    def _schedule_full_analysis(self):
        """Schedule a full system analysis."""

        def run_analysis():
            time.sleep(5)  # Brief delay to let file operations complete
            logger.info("🧠 Running scheduled full analysis...")
            try:
                self.intelligence.scan_project_files()
                analysis = self.intelligence.analyze_system_health()
                self._process_analysis_results(analysis)
            except Exception as e:
                logger.error(f"Failed to run scheduled analysis: {e}")

        # Run in background thread
        threading.Thread(target=run_analysis, daemon=True).start()

    def _schedule_immediate_analysis(self):
        """Schedule immediate analysis for critical events."""
        logger.info("🚨 Running immediate analysis...")
        try:
            # Quick scan of recent changes
            for file_path in list(self.pending_changes):
                if os.path.exists(file_path):
                    metadata = self.intelligence._analyze_file(Path(file_path))
                    if metadata.risk_level == "high":
                        logger.warning(f"[WARN] High risk file detected: {file_path}")

            self.pending_changes.clear()
        except Exception as e:
            logger.error(f"Failed to run immediate analysis: {e}")

    def _process_analysis_results(self, analysis):
        """Process system analysis results and take action."""
        # Auto-execute low-risk optimizations
        if self.config.get("auto_optimize", False):
            low_risk_suggestions = [
                s
                for s in analysis.optimization_suggestions
                if s.get("risk_level", "medium") == "low"
            ]

            if low_risk_suggestions:
                logger.info(
                    f"[TOOL] Auto-executing {len(low_risk_suggestions)} low-risk optimizations"
                )
                results = self.intelligence.execute_safe_optimization(
                    low_risk_suggestions, dry_run=False
                )

                logger.info(
                    f"Optimization results: {len(results['executed'])} executed, {len(results['errors'])} errors"
                )

    def _start_background_processor(self):
        """Start background processing for batched operations."""

        def background_processor():
            while True:
                try:
                    current_time = time.time()

                    # Process pending changes if enough time has passed
                    if (
                        current_time - self.last_analysis_time > self.analysis_interval
                        and len(self.pending_changes) > 0
                    ):
                        logger.info(
                            f"🔄 Processing {len(self.pending_changes)} pending changes..."
                        )

                        # Batch process changes
                        changes_to_process = list(self.pending_changes)[
                            : self.batch_size
                        ]
                        self.pending_changes.clear()

                        for file_path in changes_to_process:
                            if os.path.exists(file_path):
                                try:
                                    metadata = self.intelligence._analyze_file(
                                        Path(file_path)
                                    )
                                    self.intelligence.file_registry[file_path] = (
                                        metadata
                                    )
                                except Exception as e:
                                    logger.warning(
                                        f"Failed to process {file_path}: {e}"
                                    )

                        self.last_analysis_time = current_time

                        # Update database
                        self.intelligence._update_database()

                    time.sleep(5)  # Check every 5 seconds

                except Exception as e:
                    logger.error(f"Background processor error: {e}")
                    time.sleep(10)  # Wait longer on error

        # Start background thread
        processor_thread = threading.Thread(target=background_processor, daemon=True)
        processor_thread.start()
        logger.info("🔄 Background processor started")


class AetherraFileWatcherDaemon:
    """
    🔍 Main daemon for Aetherra file system monitoring.
    """

    def __init__(self, project_root: str | None = None, config_file: str | None = None):
        self.project_root = Path(project_root or os.getcwd())
        self.config = self._load_config(config_file)

        # Initialize core intelligence
        self.intelligence = AetherraFileIntelligence(str(self.project_root))

        # Initialize file watcher
        self.watcher = AetherraFileWatcher(self.intelligence, self.config)

        # Setup observer
        self.observer = Observer()
        self._setup_monitoring()

        # Status tracking
        self.is_running = False
        self.start_time = None

    def _load_config(self, config_file: str | None = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "analysis_interval": 30,
            "batch_size": 10,
            "auto_relocate": False,
            "auto_optimize": False,
            "monitored_directories": ["."],
            "log_level": "INFO",
            "enable_aether_triggers": True,
        }

        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_file}: {e}")

        return default_config

    def _setup_monitoring(self):
        """Setup file system monitoring."""
        monitored_dirs = self.config.get("monitored_directories", ["."])

        for directory in monitored_dirs:
            watch_path = self.project_root / directory
            if watch_path.exists():
                self.observer.schedule(self.watcher, str(watch_path), recursive=True)
                logger.info(f"👁️ Monitoring directory: {watch_path}")

    def start(self):
        """Start the file watcher daemon."""
        if self.is_running:
            logger.warning("Daemon is already running")
            return

        logger.info("🚀 Starting Aetherra File Watcher Daemon...")

        # Initial system scan
        logger.info("🔍 Performing initial system scan...")
        self.intelligence.scan_project_files()
        initial_analysis = self.intelligence.analyze_system_health()

        logger.info(
            f"Initial scan complete: {initial_analysis.total_files} files analyzed"
        )
        if initial_analysis.orphaned_files:
            logger.info(f"Found {len(initial_analysis.orphaned_files)} orphaned files")
        if initial_analysis.duplicate_logic:
            logger.info(
                f"Found {len(initial_analysis.duplicate_logic)} potential duplicates"
            )

        # Start file system monitoring
        self.observer.start()
        self.is_running = True
        self.start_time = datetime.now()

        logger.info("[OK] Aetherra File Watcher Daemon started successfully")

        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the file watcher daemon."""
        if not self.is_running:
            return

        logger.info("🛑 Stopping Aetherra File Watcher Daemon...")

        self.observer.stop()
        self.observer.join()
        self.is_running = False

        # Final update
        self.intelligence._update_database()

        runtime = datetime.now() - self.start_time if self.start_time else None
        logger.info(f"[OK] Daemon stopped. Runtime: {runtime}")

    def status(self) -> Dict[str, Any]:
        """Get daemon status information."""
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "monitored_files": len(self.intelligence.file_registry),
            "pending_changes": len(self.watcher.pending_changes)
            if hasattr(self.watcher, "pending_changes")
            else 0,
            "project_root": str(self.project_root),
            "config": self.config,
        }

    def trigger_analysis(self):
        """Manually trigger system analysis."""
        logger.info("🧠 Manual analysis triggered...")
        analysis = self.intelligence.analyze_system_health()
        self.watcher._process_analysis_results(analysis)
        return analysis

    def trigger_aether_script(self, script_name: str):
        """Trigger an .aether optimization script."""
        if not self.config.get("enable_aether_triggers", True):
            logger.warning("Aether script triggers are disabled")
            return False

        script_path = self.project_root / f"{script_name}.aether"
        if not script_path.exists():
            logger.error(f"Aether script not found: {script_path}")
            return False

        try:
            # This would need integration with the Aetherra runtime
            # For now, just log the trigger
            logger.info(f"[TOOL] Triggering Aether script: {script_name}")

            # Example: Execute refactor_orphan_modules.aether
            if script_name == "refactor_orphan_modules":
                orphaned = self.intelligence.detect_orphaned_modules()
                if orphaned:
                    logger.info(f"Processing {len(orphaned)} orphaned modules...")
                    # Process orphaned modules

            return True

        except Exception as e:
            logger.error(f"Failed to execute Aether script {script_name}: {e}")
            return False


def main():
    """Main entry point for the file watcher daemon."""
    import argparse

    parser = argparse.ArgumentParser(description="Aetherra File Watcher Daemon")
    parser.add_argument("--start", action="store_true", help="Start the daemon")
    parser.add_argument("--stop", action="store_true", help="Stop the daemon")
    parser.add_argument("--status", action="store_true", help="Show daemon status")
    parser.add_argument(
        "--analyze", action="store_true", help="Trigger manual analysis"
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument(
        "--daemon", action="store_true", help="Run as background daemon"
    )

    args = parser.parse_args()

    daemon = AetherraFileWatcherDaemon(args.project_root, args.config)

    if args.status:
        status = daemon.status()
        print(json.dumps(status, indent=2))
    elif args.analyze:
        analysis = daemon.trigger_analysis()
        print(
            f"Analysis complete: {analysis.total_files} files, {len(analysis.orphaned_files)} orphaned"
        )
    elif args.start:
        if args.daemon:
            # Run as background daemon (would need additional daemon setup)
            logger.info("Running in daemon mode...")
        daemon.start()
    else:
        # Default: start monitoring
        daemon.start()


if __name__ == "__main__":
    main()
