# 🛡️ NeuroCode Project Protection System
# Critical file protection and backup safeguards

import datetime
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List


class ProjectProtection:
    """
    Comprehensive protection system for critical NeuroCode project files.
    Prevents accidental deletion and maintains automatic backups.
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.protection_config = self.project_root / ".project_protection.json"
        self.backup_dir = self.project_root / "backups" / "auto_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Load or create protection configuration
        self.config = self.load_protection_config()

    def load_protection_config(self) -> Dict:
        """Load protection configuration or create default."""
        default_config = {
            "protected_files": [
                "README.md",
                "LICENSE",
                "pyproject.toml",
                "requirements.txt",
                "CHANGE_MANAGEMENT_PROTOCOL.md",
                "DOMAIN_SETUP_GUIDE.md",
                "MISSION_COMPLETE.md",
                "SUCCESS_SUMMARY.md",
            ],
            "protected_directories": ["core/", "src/", "docs/", "examples/", "tests/", "data/"],
            "critical_extensions": [".py", ".neuro", ".md", ".json", ".toml", ".yaml", ".yml"],
            "backup_frequency": "daily",
            "max_backups": 30,
            "protection_enabled": True,
        }

        if self.protection_config.exists():
            try:
                with open(self.protection_config) as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"⚠️ Error loading protection config: {e}")
                return default_config
        else:
            self.save_protection_config(default_config)
            return default_config

    def save_protection_config(self, config: Dict):
        """Save protection configuration."""
        try:
            with open(self.protection_config, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving protection config: {e}")

    def is_protected_file(self, file_path: str) -> bool:
        """Check if a file is protected."""
        if not self.config.get("protection_enabled", True):
            return False

        path = Path(file_path)
        rel_path = str(path.relative_to(self.project_root)) if path.is_absolute() else str(path)

        # Check protected files list
        if rel_path in self.config["protected_files"]:
            return True

        # Check protected directories
        for protected_dir in self.config["protected_directories"]:
            if rel_path.startswith(protected_dir):
                return True

        # Check critical extensions
        if path.suffix in self.config["critical_extensions"]:
            return True

        return False

    def protect_file_deletion(self, file_path: str) -> bool:
        """
        Protect against file deletion. Returns True if deletion should be blocked.
        """
        if not self.is_protected_file(file_path):
            return False

        print(f"🛡️ PROTECTION: File '{file_path}' is protected from deletion!")
        print("Use 'force_delete' if you really need to delete this file.")

        # Create backup before any potential deletion
        self.backup_file(file_path)
        return True

    def backup_file(self, file_path: str) -> str:
        """Create a backup of a file."""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return ""

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(source_path, backup_path)
            print(f"✅ Backup created: {backup_path}")

            # Clean old backups
            self.cleanup_old_backups(source_path.stem)
            return str(backup_path)

        except Exception as e:
            print(f"⚠️ Error creating backup for {file_path}: {e}")
            return ""

    def backup_critical_files(self) -> List[str]:
        """Create backups of all critical files."""
        backed_up = []

        for file_path in self.config["protected_files"]:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_file(str(full_path))
                if backup_path:
                    backed_up.append(backup_path)

        return backed_up

    def cleanup_old_backups(self, file_stem: str):
        """Remove old backups beyond the configured limit."""
        try:
            max_backups = self.config.get("max_backups", 30)
            pattern = f"{file_stem}_*"
            backups = sorted(
                self.backup_dir.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True
            )

            for old_backup in backups[max_backups:]:
                old_backup.unlink()
                print(f"🗑️ Removed old backup: {old_backup.name}")

        except Exception as e:
            print(f"⚠️ Error cleaning old backups: {e}")

    def force_delete(self, file_path: str, reason: str = "") -> bool:
        """
        Force delete a protected file with reason logging.
        """
        try:
            # Create backup first
            backup_path = self.backup_file(file_path)

            # Log the deletion
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "file": file_path,
                "backup": backup_path,
                "reason": reason,
                "user": os.getenv("USERNAME", "unknown"),
            }

            self.log_deletion(log_entry)

            # Perform deletion
            Path(file_path).unlink()
            print(f"🗑️ FORCE DELETED: {file_path}")
            print(f"📦 Backup available at: {backup_path}")

            return True

        except Exception as e:
            print(f"❌ Error force deleting {file_path}: {e}")
            return False

    def log_deletion(self, log_entry: Dict):
        """Log file deletions."""
        log_file = self.backup_dir / "deletion_log.json"

        try:
            if log_file.exists():
                with open(log_file) as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(log_entry)

            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print(f"⚠️ Error logging deletion: {e}")

    def restore_file(self, file_path: str, backup_timestamp: str = None) -> bool:
        """Restore a file from backup."""
        try:
            source_path = Path(file_path)
            file_stem = source_path.stem

            if backup_timestamp:
                backup_name = f"{file_stem}_{backup_timestamp}{source_path.suffix}"
                backup_path = self.backup_dir / backup_name
            else:
                # Find most recent backup
                pattern = f"{file_stem}_*{source_path.suffix}"
                backups = sorted(
                    self.backup_dir.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True
                )
                if not backups:
                    print(f"❌ No backups found for {file_path}")
                    return False
                backup_path = backups[0]

            if not backup_path.exists():
                print(f"❌ Backup not found: {backup_path}")
                return False

            shutil.copy2(backup_path, source_path)
            print(f"✅ Restored {file_path} from {backup_path}")
            return True

        except Exception as e:
            print(f"❌ Error restoring {file_path}: {e}")
            return False

    def status_report(self) -> Dict:
        """Generate protection status report."""
        protected_count = 0
        missing_files = []

        for file_path in self.config["protected_files"]:
            full_path = self.project_root / file_path
            if full_path.exists():
                protected_count += 1
            else:
                missing_files.append(file_path)

        backup_count = len(list(self.backup_dir.glob("*"))) if self.backup_dir.exists() else 0

        return {
            "protection_enabled": self.config.get("protection_enabled", True),
            "protected_files_count": len(self.config["protected_files"]),
            "protected_files_existing": protected_count,
            "missing_files": missing_files,
            "backup_count": backup_count,
            "backup_directory": str(self.backup_dir),
            "last_backup": self.get_last_backup_time(),
        }

    def get_last_backup_time(self) -> str:
        """Get timestamp of most recent backup."""
        try:
            if not self.backup_dir.exists():
                return "Never"

            backups = list(self.backup_dir.glob("*"))
            if not backups:
                return "Never"

            latest = max(backups, key=lambda x: x.stat().st_mtime)
            return datetime.datetime.fromtimestamp(latest.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except Exception:
            return "Unknown"


def main():
    """CLI interface for project protection."""
    import sys

    if len(sys.argv) < 2:
        print("🛡️ NeuroCode Project Protection System")
        print("Usage:")
        print("  python project_protection.py status")
        print("  python project_protection.py backup")
        print("  python project_protection.py restore <file_path>")
        print("  python project_protection.py force_delete <file_path> [reason]")
        return

    project_root = os.getcwd()
    protection = ProjectProtection(project_root)

    command = sys.argv[1]

    if command == "status":
        status = protection.status_report()
        print("🛡️ NeuroCode Protection Status:")
        print(f"  Protection Enabled: {status['protection_enabled']}")
        print(
            f"  Protected Files: {status['protected_files_existing']}/{status['protected_files_count']}"
        )
        print(f"  Backup Count: {status['backup_count']}")
        print(f"  Last Backup: {status['last_backup']}")
        if status["missing_files"]:
            print(f"  ⚠️ Missing Files: {', '.join(status['missing_files'])}")

    elif command == "backup":
        print("🔄 Creating backups of critical files...")
        backed_up = protection.backup_critical_files()
        print(f"✅ Created {len(backed_up)} backups")

    elif command == "restore" and len(sys.argv) >= 3:
        file_path = sys.argv[2]
        timestamp = sys.argv[3] if len(sys.argv) >= 4 else None
        protection.restore_file(file_path, timestamp)

    elif command == "force_delete" and len(sys.argv) >= 3:
        file_path = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) >= 4 else "No reason provided"
        protection.force_delete(file_path, reason)

    else:
        print("❌ Invalid command or missing arguments")


if __name__ == "__main__":
    main()
