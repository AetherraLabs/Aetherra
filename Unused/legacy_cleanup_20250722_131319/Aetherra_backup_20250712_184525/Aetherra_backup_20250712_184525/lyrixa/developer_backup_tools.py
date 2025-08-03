#!/usr/bin/env python3
"""
[TOOL] LYRIXA DEVELOPER BACKUP TOOLS
===============================

Comprehensive backup system for Lyrixa intelligence and core modules.
Provides versioned backups, restoration capabilities, and backup management.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class LyrixaDeveloperBackupTools:
    """
    [TOOL] Developer tools for backing up and managing Lyrixa components
    """

    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize the backup tools."""
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.backup_root = self.workspace_path / "backups"
        self.backup_metadata_file = self.backup_root / "backup_metadata.json"

        # Ensure backup directory exists
        self.backup_root.mkdir(exist_ok=True)

        # Load backup metadata
        self.backup_metadata = self._load_backup_metadata()

        print(f"[TOOL] Developer Backup Tools initialized")
        print(f"📁 Backup location: {self.backup_root}")

    def _load_backup_metadata(self) -> Dict:
        """Load backup metadata from file."""
        try:
            if self.backup_metadata_file.exists():
                with open(self.backup_metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not load backup metadata: {e}")

        return {
            "backups": {},
            "backup_history": [],
            "settings": {
                "max_backups_per_file": 10,
                "auto_backup_enabled": True,
                "compression_enabled": False
            }
        }

    def _save_backup_metadata(self):
        """Save backup metadata to file."""
        try:
            with open(self.backup_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed to save backup metadata: {e}")

    def create_backup(self,
                     file_path: str,
                     backup_type: str = "manual",
                     description: str = "",
                     tag: str = "") -> str:
        """
        Create a backup of the specified file.

        Args:
            file_path: Path to file to backup
            backup_type: Type of backup (manual, auto, milestone)
            description: Description of the backup
            tag: Optional tag for the backup

        Returns:
            Path to the created backup file
        """
        source_file = Path(file_path)
        if not source_file.exists():
            print(f"[ERROR] File not found: {file_path}")
            return ""

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{source_file.stem}_backup_{timestamp}{source_file.suffix}"
        backup_path = self.backup_root / backup_filename

        try:
            # Copy the file
            shutil.copy2(source_file, backup_path)

            # Record backup metadata
            backup_id = f"{source_file.name}_{timestamp}"
            backup_info = {
                "backup_id": backup_id,
                "original_file": str(source_file),
                "backup_path": str(backup_path),
                "backup_type": backup_type,
                "description": description,
                "tag": tag,
                "created_at": datetime.now().isoformat(),
                "file_size": backup_path.stat().st_size,
                "checksum": self._calculate_checksum(backup_path)
            }

            # Update metadata
            if source_file.name not in self.backup_metadata["backups"]:
                self.backup_metadata["backups"][source_file.name] = []

            self.backup_metadata["backups"][source_file.name].append(backup_info)
            self.backup_metadata["backup_history"].append(backup_info)

            # Cleanup old backups if needed
            self._cleanup_old_backups(source_file.name)

            # Save metadata
            self._save_backup_metadata()

            print(f"✅ Backup created: {backup_filename}")
            print(f"📄 Type: {backup_type}")
            if description:
                print(f"📝 Description: {description}")
            if tag:
                print(f"🏷️ Tag: {tag}")

            return str(backup_path)

        except Exception as e:
            print(f"[ERROR] Failed to create backup: {e}")
            return ""

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate a simple checksum for the file."""
        import hashlib
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""

    def _cleanup_old_backups(self, filename: str):
        """Clean up old backups based on settings."""
        max_backups = self.backup_metadata["settings"]["max_backups_per_file"]

        if filename in self.backup_metadata["backups"]:
            backups = self.backup_metadata["backups"][filename]

            if len(backups) > max_backups:
                # Sort by creation time (oldest first)
                backups.sort(key=lambda x: x["created_at"])

                # Remove oldest backups
                to_remove = backups[:len(backups) - max_backups]

                for backup_info in to_remove:
                    backup_path = Path(backup_info["backup_path"])
                    if backup_path.exists():
                        try:
                            backup_path.unlink()
                            print(f"🗑️ Removed old backup: {backup_path.name}")
                        except Exception as e:
                            print(f"[WARN] Could not remove old backup: {e}")

                # Update metadata
                self.backup_metadata["backups"][filename] = backups[len(backups) - max_backups:]

    def list_backups(self, filename: Optional[str] = None) -> List[Dict]:
        """List available backups."""
        if filename:
            return self.backup_metadata["backups"].get(filename, [])
        else:
            all_backups = []
            for file_backups in self.backup_metadata["backups"].values():
                all_backups.extend(file_backups)
            return sorted(all_backups, key=lambda x: x["created_at"], reverse=True)

    def restore_backup(self, backup_id: str, target_path: Optional[str] = None) -> bool:
        """
        Restore a backup by ID.

        Args:
            backup_id: ID of the backup to restore
            target_path: Optional target path, defaults to original location

        Returns:
            True if restore was successful
        """
        # Find the backup
        backup_info = None
        for file_backups in self.backup_metadata["backups"].values():
            for backup in file_backups:
                if backup["backup_id"] == backup_id:
                    backup_info = backup
                    break
            if backup_info:
                break

        if not backup_info:
            print(f"[ERROR] Backup not found: {backup_id}")
            return False

        backup_path = Path(backup_info["backup_path"])
        if not backup_path.exists():
            print(f"[ERROR] Backup file missing: {backup_path}")
            return False

        # Determine target path
        if target_path:
            target = Path(target_path)
        else:
            target = Path(backup_info["original_file"])

        try:
            # Create backup of current file before restore
            if target.exists():
                current_backup = self.create_backup(
                    str(target),
                    "pre_restore",
                    f"Auto backup before restoring {backup_id}"
                )
                print(f"💾 Created backup of current file: {Path(current_backup).name}")

            # Restore the backup
            shutil.copy2(backup_path, target)

            print(f"✅ Restored backup: {backup_id}")
            print(f"📄 Target: {target}")

            return True

        except Exception as e:
            print(f"[ERROR] Failed to restore backup: {e}")
            return False

    def create_milestone_backup(self,
                              file_path: str,
                              milestone_name: str,
                              description: str = "") -> str:
        """Create a milestone backup with special tagging."""
        return self.create_backup(
            file_path,
            "milestone",
            description or f"Milestone: {milestone_name}",
            milestone_name
        )

    def backup_intelligence_system(self, description: str = "") -> Dict[str, str]:
        """Create a comprehensive backup of the intelligence system."""
        print("🧠 Creating comprehensive intelligence system backup...")

        intelligence_files = [
            "intelligence.py",
            "intelligence_integration.py",
            "goal_forecaster.py",
            "reasoning_memory_layer.py",
            "agent_collaboration_manager.py",
            "cognitive_monitor_dashboard.py"
        ]

        backup_results = {}

        for filename in intelligence_files:
            file_path = self.workspace_path / filename
            if file_path.exists():
                backup_path = self.create_backup(
                    str(file_path),
                    "system_backup",
                    description or "Intelligence system backup",
                    "intelligence_system"
                )
                backup_results[filename] = backup_path
                print(f"✅ Backed up: {filename}")
            else:
                print(f"[WARN] File not found: {filename}")

        print(f"[DISC] Intelligence system backup complete: {len(backup_results)} files backed up")
        return backup_results

    def export_backup_report(self) -> str:
        """Export a comprehensive backup report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.backup_root / f"backup_report_{timestamp}.json"

        # Generate statistics
        total_backups = sum(len(backups) for backups in self.backup_metadata["backups"].values())
        total_size = 0

        for file_backups in self.backup_metadata["backups"].values():
            for backup in file_backups:
                total_size += backup.get("file_size", 0)

        backup_types = {}
        for file_backups in self.backup_metadata["backups"].values():
            for backup in file_backups:
                backup_type = backup["backup_type"]
                backup_types[backup_type] = backup_types.get(backup_type, 0) + 1

        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "backup_location": str(self.backup_root),
                "total_files_tracked": len(self.backup_metadata["backups"]),
                "total_backups": total_backups,
                "total_size_bytes": total_size,
                "backup_types": backup_types
            },
            "backup_summary": self.backup_metadata["backups"],
            "recent_backups": self.backup_metadata["backup_history"][-20:],
            "settings": self.backup_metadata["settings"]
        }

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"📊 Backup report exported: {report_path}")
            return str(report_path)

        except Exception as e:
            print(f"[ERROR] Failed to export backup report: {e}")
            return ""

    def get_backup_status(self) -> Dict:
        """Get current backup system status."""
        total_backups = sum(len(backups) for backups in self.backup_metadata["backups"].values())
        total_size = sum(
            backup.get("file_size", 0)
            for file_backups in self.backup_metadata["backups"].values()
            for backup in file_backups
        )

        return {
            "total_files_tracked": len(self.backup_metadata["backups"]),
            "total_backups": total_backups,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "backup_location": str(self.backup_root),
            "settings": self.backup_metadata["settings"],
            "last_backup": self.backup_metadata["backup_history"][-1]["created_at"] if self.backup_metadata["backup_history"] else "None"
        }


# CLI Interface for developer tools
def main():
    """Main CLI interface for backup tools."""
    import argparse

    parser = argparse.ArgumentParser(description="Lyrixa Developer Backup Tools")
    parser.add_argument("action", choices=["backup", "list", "restore", "milestone", "system", "status", "report"])
    parser.add_argument("--file", "-f", help="File to backup/restore")
    parser.add_argument("--backup-id", "-b", help="Backup ID for restore")
    parser.add_argument("--description", "-d", help="Backup description")
    parser.add_argument("--tag", "-t", help="Backup tag")
    parser.add_argument("--milestone", "-m", help="Milestone name")

    args = parser.parse_args()

    # Initialize backup tools
    backup_tools = LyrixaDeveloperBackupTools()

    if args.action == "backup":
        if not args.file:
            print("[ERROR] File path required for backup")
            return
        backup_tools.create_backup(args.file, "manual", args.description or "", args.tag or "")

    elif args.action == "list":
        backups = backup_tools.list_backups(args.file)
        if backups:
            print(f"📋 Available backups:")
            for backup in backups:
                print(f"  🔹 {backup['backup_id']} - {backup['created_at']} - {backup['backup_type']}")
                if backup.get('description'):
                    print(f"    📝 {backup['description']}")
        else:
            print("📋 No backups found")

    elif args.action == "restore":
        if not args.backup_id:
            print("[ERROR] Backup ID required for restore")
            return
        backup_tools.restore_backup(args.backup_id)

    elif args.action == "milestone":
        if not args.file or not args.milestone:
            print("[ERROR] File path and milestone name required")
            return
        backup_tools.create_milestone_backup(args.file, args.milestone, args.description or "")

    elif args.action == "system":
        backup_tools.backup_intelligence_system(args.description or "")

    elif args.action == "status":
        status = backup_tools.get_backup_status()
        print("📊 Backup System Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

    elif args.action == "report":
        backup_tools.export_backup_report()


if __name__ == "__main__":
    main()
