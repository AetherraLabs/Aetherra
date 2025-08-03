"""
Memory & Workflow Backup - Versioned memory snapshots and workflow state preservation.

This module provides comprehensive backup and versioning capabilities for memory
states and workflow configurations, enabling rollback and state restoration.
"""

import json
import shutil
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import threading


@dataclass
class BackupMetadata:
    """Metadata for a backup snapshot."""
    backup_id: str
    timestamp: str
    backup_type: str  # 'memory', 'workflow', 'combined'
    description: str
    size_bytes: int
    checksum: str
    auto_created: bool
    tags: List[str]


@dataclass
class MemorySnapshot:
    """Memory state snapshot data."""
    memory_data: Dict[str, Any]
    memory_tags: Dict[str, List[str]]
    memory_pins: List[str]
    total_entries: int
    snapshot_time: str


@dataclass
class WorkflowSnapshot:
    """Workflow state snapshot data."""
    workflow_config: Dict[str, Any]
    active_workflows: List[str]
    workflow_history: List[Dict[str, Any]]
    plugin_states: Dict[str, Any]
    snapshot_time: str


class MemoryWorkflowBackup:
    """Comprehensive backup system for memory and workflow states."""

    def __init__(self, backup_dir: str = "data/backups"):
        """Initialize the backup system.

        Args:
            backup_dir: Directory to store backup files
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup storage directories
        self.snapshots_dir = self.backup_dir / "snapshots"
        self.archives_dir = self.backup_dir / "archives"
        self.metadata_dir = self.backup_dir / "metadata"

        for directory in [self.snapshots_dir, self.archives_dir, self.metadata_dir]:
            directory.mkdir(exist_ok=True)

        self.metadata_file = self.metadata_dir / "backup_registry.json"
        self.auto_backup_config = self.backup_dir / "auto_backup_config.json"

        # Auto-backup settings
        self.auto_backup_enabled = False
        self.auto_backup_interval = 3600  # 1 hour default
        self.max_auto_backups = 24  # Keep 24 hourly backups
        self.auto_backup_thread: Optional[threading.Thread] = None

        # Initialize metadata
        if not self.metadata_file.exists():
            self._save_metadata([])

        # Load auto-backup configuration
        self._load_auto_backup_config()

    def create_memory_backup(self, memory_store_path: str, description: str = "",
                           tags: Optional[List[str]] = None) -> str:
        """Create a backup of memory state.

        Args:
            memory_store_path: Path to memory store file
            description: Backup description
            tags: Optional tags for the backup

        Returns:
            Backup ID
        """
        backup_id = f"memory_{int(time.time())}"
        tags = tags or []

        try:
            # Load memory data
            memory_data = self._load_memory_store(memory_store_path)

            # Create memory snapshot
            snapshot = MemorySnapshot(
                memory_data=memory_data.get('memory', {}),
                memory_tags=memory_data.get('tags', {}),
                memory_pins=memory_data.get('pins', []),
                total_entries=len(memory_data.get('memory', {})),
                snapshot_time=datetime.now().isoformat()
            )

            # Save snapshot
            snapshot_path = self.snapshots_dir / f"{backup_id}.json"
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(snapshot), f, indent=2, ensure_ascii=False)

            # Calculate checksum
            checksum = self._calculate_checksum(snapshot_path)

            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now().isoformat(),
                backup_type='memory',
                description=description or f"Memory backup - {snapshot.total_entries} entries",
                size_bytes=snapshot_path.stat().st_size,
                checksum=checksum,
                auto_created=False,
                tags=tags
            )

            # Save metadata
            self._add_backup_metadata(metadata)

            print(f"✅ Memory backup created: {backup_id}")
            print(f"   Entries: {snapshot.total_entries}")
            print(f"   Size: {metadata.size_bytes / 1024:.1f} KB")

            return backup_id

        except Exception as e:
            print(f"❌ Failed to create memory backup: {e}")
            raise

    def create_workflow_backup(self, workflow_config_path: str = "config",
                             description: str = "", tags: Optional[List[str]] = None) -> str:
        """Create a backup of workflow state.

        Args:
            workflow_config_path: Path to workflow configuration
            description: Backup description
            tags: Optional tags for the backup

        Returns:
            Backup ID
        """
        backup_id = f"workflow_{int(time.time())}"
        tags = tags or []

        try:
            # Load workflow data
            workflow_data = self._load_workflow_state(workflow_config_path)

            # Create workflow snapshot
            snapshot = WorkflowSnapshot(
                workflow_config=workflow_data.get('config', {}),
                active_workflows=workflow_data.get('active_workflows', []),
                workflow_history=workflow_data.get('history', []),
                plugin_states=workflow_data.get('plugin_states', {}),
                snapshot_time=datetime.now().isoformat()
            )

            # Save snapshot
            snapshot_path = self.snapshots_dir / f"{backup_id}.json"
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(snapshot), f, indent=2, ensure_ascii=False)

            # Calculate checksum
            checksum = self._calculate_checksum(snapshot_path)

            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now().isoformat(),
                backup_type='workflow',
                description=description or f"Workflow backup - {len(snapshot.active_workflows)} active",
                size_bytes=snapshot_path.stat().st_size,
                checksum=checksum,
                auto_created=False,
                tags=tags
            )

            # Save metadata
            self._add_backup_metadata(metadata)

            print(f"✅ Workflow backup created: {backup_id}")
            print(f"   Active workflows: {len(snapshot.active_workflows)}")
            print(f"   Size: {metadata.size_bytes / 1024:.1f} KB")

            return backup_id

        except Exception as e:
            print(f"❌ Failed to create workflow backup: {e}")
            raise

    def create_combined_backup(self, memory_store_path: str,
                             workflow_config_path: str = "config",
                             description: str = "", tags: Optional[List[str]] = None) -> str:
        """Create a combined backup of memory and workflow states.

        Args:
            memory_store_path: Path to memory store file
            workflow_config_path: Path to workflow configuration
            description: Backup description
            tags: Optional tags for the backup

        Returns:
            Backup ID
        """
        backup_id = f"combined_{int(time.time())}"
        tags = tags or []

        try:
            # Load both memory and workflow data
            memory_data = self._load_memory_store(memory_store_path)
            workflow_data = self._load_workflow_state(workflow_config_path)

            # Create combined snapshot
            combined_data = {
                'memory_snapshot': MemorySnapshot(
                    memory_data=memory_data.get('memory', {}),
                    memory_tags=memory_data.get('tags', {}),
                    memory_pins=memory_data.get('pins', []),
                    total_entries=len(memory_data.get('memory', {})),
                    snapshot_time=datetime.now().isoformat()
                ),
                'workflow_snapshot': WorkflowSnapshot(
                    workflow_config=workflow_data.get('config', {}),
                    active_workflows=workflow_data.get('active_workflows', []),
                    workflow_history=workflow_data.get('history', []),
                    plugin_states=workflow_data.get('plugin_states', {}),
                    snapshot_time=datetime.now().isoformat()
                )
            }

            # Save combined snapshot
            snapshot_path = self.snapshots_dir / f"{backup_id}.json"
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(combined_data['memory_snapshot']), f, indent=2)
                f.write('\n--- WORKFLOW SNAPSHOT ---\n')
                json.dump(asdict(combined_data['workflow_snapshot']), f, indent=2)

            # Calculate checksum
            checksum = self._calculate_checksum(snapshot_path)

            # Create metadata
            memory_entries = combined_data['memory_snapshot'].total_entries
            active_workflows = len(combined_data['workflow_snapshot'].active_workflows)

            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.now().isoformat(),
                backup_type='combined',
                description=description or f"Combined backup - {memory_entries} memory entries, {active_workflows} workflows",
                size_bytes=snapshot_path.stat().st_size,
                checksum=checksum,
                auto_created=False,
                tags=tags
            )

            # Save metadata
            self._add_backup_metadata(metadata)

            print(f"✅ Combined backup created: {backup_id}")
            print(f"   Memory entries: {memory_entries}")
            print(f"   Active workflows: {active_workflows}")
            print(f"   Size: {metadata.size_bytes / 1024:.1f} KB")

            return backup_id

        except Exception as e:
            print(f"❌ Failed to create combined backup: {e}")
            raise

    def restore_backup(self, backup_id: str, target_memory_path: Optional[str] = None,
                      target_workflow_path: Optional[str] = None, confirm: bool = False) -> bool:
        """Restore a backup to the specified locations.

        Args:
            backup_id: ID of the backup to restore
            target_memory_path: Target path for memory restoration
            target_workflow_path: Target path for workflow restoration
            confirm: Skip confirmation prompt if True

        Returns:
            True if restoration successful
        """
        # Get backup metadata
        metadata = self._get_backup_metadata(backup_id)
        if not metadata:
            print(f"❌ Backup '{backup_id}' not found")
            return False

        # Confirm restoration
        if not confirm:
            print(f"[WARN] About to restore backup: {backup_id}")
            print(f"   Type: {metadata['backup_type']}")
            print(f"   Created: {metadata['timestamp']}")
            print(f"   Description: {metadata['description']}")

            response = input("Continue with restoration? (yes/no): ").lower()
            if response not in ['yes', 'y']:
                print("❌ Restoration cancelled")
                return False

        try:
            # Load snapshot data
            snapshot_path = self.snapshots_dir / f"{backup_id}.json"
            if not snapshot_path.exists():
                print(f"❌ Backup file not found: {snapshot_path}")
                return False

            # Verify checksum
            current_checksum = self._calculate_checksum(snapshot_path)
            if current_checksum != metadata['checksum']:
                print(f"[WARN] Checksum mismatch for backup {backup_id}")
                print("   The backup file may be corrupted")
                return False

            with open(snapshot_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Handle different backup types
            if metadata['backup_type'] == 'memory':
                if not target_memory_path:
                    print("❌ Target memory path required for memory backup restoration")
                    return False

                snapshot_data = json.loads(content)
                self._restore_memory_snapshot(snapshot_data, target_memory_path)

            elif metadata['backup_type'] == 'workflow':
                if not target_workflow_path:
                    print("❌ Target workflow path required for workflow backup restoration")
                    return False

                snapshot_data = json.loads(content)
                self._restore_workflow_snapshot(snapshot_data, target_workflow_path)

            elif metadata['backup_type'] == 'combined':
                # Parse combined backup format
                parts = content.split('\n--- WORKFLOW SNAPSHOT ---\n')
                if len(parts) != 2:
                    print("❌ Invalid combined backup format")
                    return False

                memory_data = json.loads(parts[0])
                workflow_data = json.loads(parts[1])

                if target_memory_path:
                    self._restore_memory_snapshot(memory_data, target_memory_path)

                if target_workflow_path:
                    self._restore_workflow_snapshot(workflow_data, target_workflow_path)

            print(f"✅ Backup '{backup_id}' restored successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to restore backup: {e}")
            return False

    def list_backups(self, backup_type: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List available backups with optional filtering.

        Args:
            backup_type: Filter by backup type ('memory', 'workflow', 'combined')
            tags: Filter by tags

        Returns:
            List of backup information
        """
        all_metadata = self._load_metadata()
        filtered_backups = []

        for backup in all_metadata:
            # Filter by type
            if backup_type and backup['backup_type'] != backup_type:
                continue

            # Filter by tags
            if tags:
                backup_tags = set(backup.get('tags', []))
                if not set(tags).issubset(backup_tags):
                    continue

            filtered_backups.append(backup)

        # Sort by timestamp (newest first)
        filtered_backups.sort(key=lambda x: x['timestamp'], reverse=True)

        return filtered_backups

    def delete_backup(self, backup_id: str, confirm: bool = False) -> bool:
        """Delete a backup.

        Args:
            backup_id: ID of the backup to delete
            confirm: Skip confirmation prompt if True

        Returns:
            True if deletion successful
        """
        metadata = self._get_backup_metadata(backup_id)
        if not metadata:
            print(f"❌ Backup '{backup_id}' not found")
            return False

        if not confirm:
            print(f"[WARN] About to delete backup: {backup_id}")
            print(f"   Type: {metadata['backup_type']}")
            print(f"   Created: {metadata['timestamp']}")

            response = input("Continue with deletion? (yes/no): ").lower()
            if response not in ['yes', 'y']:
                print("❌ Deletion cancelled")
                return False

        try:
            # Remove snapshot file
            snapshot_path = self.snapshots_dir / f"{backup_id}.json"
            if snapshot_path.exists():
                snapshot_path.unlink()

            # Remove from metadata
            all_metadata = self._load_metadata()
            updated_metadata = [m for m in all_metadata if m['backup_id'] != backup_id]
            self._save_metadata(updated_metadata)

            print(f"✅ Backup '{backup_id}' deleted successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to delete backup: {e}")
            return False

    def archive_old_backups(self, days_old: int = 30, keep_count: int = 10) -> int:
        """Archive old backups to reduce storage usage.

        Args:
            days_old: Archive backups older than this many days
            keep_count: Keep at least this many recent backups

        Returns:
            Number of backups archived
        """
        try:
            all_metadata = self._load_metadata()

            # Sort by timestamp
            all_metadata.sort(key=lambda x: x['timestamp'], reverse=True)

            # Keep recent backups
            to_archive = []
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)

            for i, backup in enumerate(all_metadata):
                if i < keep_count:
                    continue  # Keep recent backups

                backup_time = datetime.fromisoformat(backup['timestamp']).timestamp()
                if backup_time < cutoff_time:
                    to_archive.append(backup)

            # Create archive
            if to_archive:
                archive_name = f"archived_{int(time.time())}.zip"
                archive_path = self.archives_dir / archive_name

                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                    for backup in to_archive:
                        backup_id = backup['backup_id']
                        snapshot_path = self.snapshots_dir / f"{backup_id}.json"

                        if snapshot_path.exists():
                            archive.write(snapshot_path, f"{backup_id}.json")
                            snapshot_path.unlink()

                # Update metadata
                remaining_metadata = [m for m in all_metadata if m not in to_archive]
                self._save_metadata(remaining_metadata)

                print(f"✅ Archived {len(to_archive)} old backups to {archive_name}")
                return len(to_archive)

            return 0

        except Exception as e:
            print(f"❌ Failed to archive backups: {e}")
            return 0

    def enable_auto_backup(self, interval_minutes: int = 60, max_backups: int = 24):
        """Enable automatic backup creation.

        Args:
            interval_minutes: Backup interval in minutes
            max_backups: Maximum number of auto-backups to keep
        """
        self.auto_backup_enabled = True
        self.auto_backup_interval = interval_minutes * 60
        self.max_auto_backups = max_backups

        self._save_auto_backup_config()

        if not self.auto_backup_thread or not self.auto_backup_thread.is_alive():
            self.auto_backup_thread = threading.Thread(target=self._auto_backup_worker)
            self.auto_backup_thread.daemon = True
            self.auto_backup_thread.start()

        print(f"✅ Auto-backup enabled: every {interval_minutes} minutes, keep {max_backups} backups")

    def disable_auto_backup(self):
        """Disable automatic backup creation."""
        self.auto_backup_enabled = False
        self._save_auto_backup_config()
        print("✅ Auto-backup disabled")

    def _load_memory_store(self, memory_path: str) -> Dict[str, Any]:
        """Load memory store data."""
        memory_file = Path(memory_path)
        if memory_file.is_file():
            with open(memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif memory_file.is_dir():
            # Load from memory_store.json in directory
            store_file = memory_file / "memory_store.json"
            if store_file.exists():
                with open(store_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

        return {}

    def _load_workflow_state(self, workflow_path: str) -> Dict[str, Any]:
        """Load workflow state data."""
        workflow_dir = Path(workflow_path)
        workflow_data = {
            'config': {},
            'active_workflows': [],
            'history': [],
            'plugin_states': {}
        }

        if workflow_dir.exists() and workflow_dir.is_dir():
            # Load various workflow configuration files
            config_files = [
                'workflow_config.json',
                'active_workflows.json',
                'workflow_history.json',
                'plugin_states.json'
            ]

            for config_file in config_files:
                file_path = workflow_dir / config_file
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            key = config_file.replace('.json', '').replace('workflow_', '')
                            workflow_data[key] = json.load(f)
                    except Exception as e:
                        print(f"[WARN] Warning: Could not load {config_file}: {e}")

        return workflow_data

    def _restore_memory_snapshot(self, snapshot_data: Dict[str, Any], target_path: str):
        """Restore memory snapshot to target location."""
        target_file = Path(target_path)

        # Create backup of existing file
        if target_file.exists():
            backup_name = f"{target_file.name}.backup_{int(time.time())}"
            backup_path = target_file.parent / backup_name
            shutil.copy2(target_file, backup_path)
            print(f"   Created backup: {backup_name}")

        # Restore memory data
        restored_data = {
            'memory': snapshot_data.get('memory_data', {}),
            'tags': snapshot_data.get('memory_tags', {}),
            'pins': snapshot_data.get('memory_pins', [])
        }

        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(restored_data, f, indent=2, ensure_ascii=False)

        print(f"   Memory restored: {len(restored_data['memory'])} entries")

    def _restore_workflow_snapshot(self, snapshot_data: Dict[str, Any], target_path: str):
        """Restore workflow snapshot to target location."""
        target_dir = Path(target_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Restore workflow configuration files
        config_mappings = {
            'workflow_config': snapshot_data.get('workflow_config', {}),
            'active_workflows': snapshot_data.get('active_workflows', []),
            'workflow_history': snapshot_data.get('workflow_history', []),
            'plugin_states': snapshot_data.get('plugin_states', {})
        }

        for config_name, config_data in config_mappings.items():
            config_file = target_dir / f"{config_name}.json"

            # Create backup if exists
            if config_file.exists():
                backup_name = f"{config_file.name}.backup_{int(time.time())}"
                backup_path = config_file.parent / backup_name
                shutil.copy2(config_file, backup_path)

            # Write restored data
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        print(f"   Workflow restored: {len(config_mappings)} configuration files")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _add_backup_metadata(self, metadata: BackupMetadata):
        """Add backup metadata to registry."""
        all_metadata = self._load_metadata()
        all_metadata.append(asdict(metadata))
        self._save_metadata(all_metadata)

    def _get_backup_metadata(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific backup."""
        all_metadata = self._load_metadata()
        return next((m for m in all_metadata if m['backup_id'] == backup_id), None)

    def _load_metadata(self) -> List[Dict[str, Any]]:
        """Load backup metadata from registry."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Error loading backup metadata: {e}")
        return []

    def _save_metadata(self, metadata: List[Dict[str, Any]]):
        """Save backup metadata to registry."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[WARN] Error saving backup metadata: {e}")

    def _load_auto_backup_config(self):
        """Load auto-backup configuration."""
        try:
            if self.auto_backup_config.exists():
                with open(self.auto_backup_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.auto_backup_enabled = config.get('enabled', False)
                    self.auto_backup_interval = config.get('interval', 3600)
                    self.max_auto_backups = config.get('max_backups', 24)
        except Exception as e:
            print(f"[WARN] Error loading auto-backup config: {e}")

    def _save_auto_backup_config(self):
        """Save auto-backup configuration."""
        try:
            config = {
                'enabled': self.auto_backup_enabled,
                'interval': self.auto_backup_interval,
                'max_backups': self.max_auto_backups
            }
            with open(self.auto_backup_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[WARN] Error saving auto-backup config: {e}")

    def _auto_backup_worker(self):
        """Background worker for automatic backups."""
        while self.auto_backup_enabled:
            try:
                time.sleep(self.auto_backup_interval)

                if not self.auto_backup_enabled:
                    break

                # Create auto-backup
                memory_path = "memory_store.json"
                if Path(memory_path).exists():
                    backup_id = self.create_memory_backup(
                        memory_path,
                        description="Auto-backup",
                        tags=["auto"]
                    )

                    # Clean up old auto-backups
                    auto_backups = [b for b in self._load_metadata()
                                  if 'auto' in b.get('tags', [])]

                    if len(auto_backups) > self.max_auto_backups:
                        # Delete oldest auto-backups
                        auto_backups.sort(key=lambda x: x['timestamp'])
                        for old_backup in auto_backups[:-self.max_auto_backups]:
                            self.delete_backup(old_backup['backup_id'], confirm=True)

            except Exception as e:
                print(f"[WARN] Auto-backup error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying


def main():
    """Main function for CLI usage."""
    import sys

    backup_system = MemoryWorkflowBackup()

    if len(sys.argv) < 2:
        print("Usage: python memory_workflow_backup.py <command> [args]")
        print("Commands:")
        print("  backup-memory <path> [description]    - Backup memory store")
        print("  backup-workflow [path] [description]  - Backup workflow state")
        print("  backup-combined <memory> [workflow]   - Combined backup")
        print("  restore <backup_id> [memory] [workflow] - Restore backup")
        print("  list [type] [tag]                     - List backups")
        print("  delete <backup_id>                    - Delete backup")
        print("  archive [days] [keep]                 - Archive old backups")
        print("  auto-enable [interval] [max]          - Enable auto-backup")
        print("  auto-disable                          - Disable auto-backup")
        return

    command = sys.argv[1]

    try:
        if command == "backup-memory":
            if len(sys.argv) < 3:
                print("❌ Memory store path required")
                return

            path = sys.argv[2]
            description = sys.argv[3] if len(sys.argv) > 3 else ""
            backup_id = backup_system.create_memory_backup(path, description)
            print(f"Backup created: {backup_id}")

        elif command == "backup-workflow":
            path = sys.argv[2] if len(sys.argv) > 2 else "config"
            description = sys.argv[3] if len(sys.argv) > 3 else ""
            backup_id = backup_system.create_workflow_backup(path, description)
            print(f"Backup created: {backup_id}")

        elif command == "backup-combined":
            if len(sys.argv) < 3:
                print("❌ Memory store path required")
                return

            memory_path = sys.argv[2]
            workflow_path = sys.argv[3] if len(sys.argv) > 3 else "config"
            backup_id = backup_system.create_combined_backup(memory_path, workflow_path)
            print(f"Backup created: {backup_id}")

        elif command == "restore":
            if len(sys.argv) < 3:
                print("❌ Backup ID required")
                return

            backup_id = sys.argv[2]
            memory_path = sys.argv[3] if len(sys.argv) > 3 else None
            workflow_path = sys.argv[4] if len(sys.argv) > 4 else None

            success = backup_system.restore_backup(backup_id, memory_path, workflow_path)
            if success:
                print("Restoration completed")

        elif command == "list":
            backup_type = sys.argv[2] if len(sys.argv) > 2 else None
            tag = [sys.argv[3]] if len(sys.argv) > 3 else None

            backups = backup_system.list_backups(backup_type, tag)
            print(f"[DISC] Found {len(backups)} backups:")

            for backup in backups:
                print(f"  {backup['backup_id']}: {backup['backup_type']} - {backup['description']}")
                print(f"    Created: {backup['timestamp']}")
                print(f"    Size: {backup['size_bytes'] / 1024:.1f} KB")
                print()

        elif command == "delete":
            if len(sys.argv) < 3:
                print("❌ Backup ID required")
                return

            backup_id = sys.argv[2]
            success = backup_system.delete_backup(backup_id)
            if success:
                print("Backup deleted")

        elif command == "archive":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            keep = int(sys.argv[3]) if len(sys.argv) > 3 else 10

            count = backup_system.archive_old_backups(days, keep)
            print(f"Archived {count} backups")

        elif command == "auto-enable":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            max_backups = int(sys.argv[3]) if len(sys.argv) > 3 else 24

            backup_system.enable_auto_backup(interval, max_backups)

        elif command == "auto-disable":
            backup_system.disable_auto_backup()

        else:
            print(f"Unknown command: {command}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
