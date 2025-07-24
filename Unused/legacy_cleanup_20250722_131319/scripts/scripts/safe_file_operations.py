#!/usr/bin/env python3
"""
🛡️ SAFE FILE OPERATIONS FOR LYRIXA
===================================

This module provides safe file writing operations to prevent file corruption
that has been occurring in the Lyrixa system.

Features:
- Atomic file writes using temp files + rename
- Automatic backups before overwriting
- Error recovery mechanisms
- Corruption detection and reporting
"""

import hashlib
import json
import os
import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class SafeFileWriter:
    """Safe file writing system with atomic operations and backups"""

    def __init__(self, backup_dir: str = "backups/safe_writes"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.corruption_log = self.backup_dir / "corruption_log.json"
        self.operation_log = self.backup_dir / "operation_log.json"

    def safe_write(self, file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """
        Safely write content to a file using atomic operations

        Args:
            file_path: Path to the file to write
            content: Content to write
            encoding: File encoding (default: utf-8)

        Returns:
            bool: True if successful, False if failed
        """
        file_path = Path(file_path)

        try:
            # Step 1: Create backup if file exists
            backup_path = None
            if file_path.exists():
                backup_path = self._create_backup(file_path)
                if not backup_path:
                    self._log_error(f"Failed to create backup for {file_path}")
                    return False

            # Step 2: Write to temporary file
            temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

            with open(temp_path, "w", encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Step 3: Verify the temp file was written correctly
            if not self._verify_temp_file(temp_path, content):
                self._log_error(f"Temp file verification failed for {file_path}")
                if temp_path.exists():
                    temp_path.unlink()
                return False

            # Step 4: Atomic replace - this is the critical operation
            if os.name == "nt":  # Windows
                # On Windows, we need to remove the target first
                if file_path.exists():
                    file_path.unlink()

            shutil.move(str(temp_path), str(file_path))

            # Step 5: Verify the final file
            if not self._verify_final_file(file_path, content):
                self._log_error(f"Final file verification failed for {file_path}")
                # Try to restore from backup
                if backup_path and backup_path.exists():
                    shutil.copy2(backup_path, file_path)
                    self._log_error(f"Restored {file_path} from backup")
                return False

            # Step 6: Log successful operation
            self._log_operation(file_path, "write_success", len(content))

            return True

        except Exception as e:
            self._log_error(f"Safe write failed for {file_path}: {str(e)}")

            # Cleanup temp file if it exists
            temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass

            # Try to restore from backup if available
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, file_path)
                    self._log_error(f"Restored {file_path} from backup after error")
                except:
                    pass

            return False

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a timestamped backup of the file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            return backup_path

        except Exception as e:
            self._log_error(f"Backup creation failed for {file_path}: {str(e)}")
            return None

    def _verify_temp_file(self, temp_path: Path, expected_content: str) -> bool:
        """Verify that the temp file was written correctly"""
        try:
            if not temp_path.exists():
                return False

            with open(temp_path, "r", encoding="utf-8") as f:
                actual_content = f.read()

            return actual_content == expected_content

        except Exception:
            return False

    def _verify_final_file(self, file_path: Path, expected_content: str) -> bool:
        """Verify that the final file was written correctly"""
        try:
            if not file_path.exists():
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                actual_content = f.read()

            return actual_content == expected_content

        except Exception:
            return False

    def _log_operation(self, file_path: Path, operation: str, size: int):
        """Log successful file operations"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "file_path": str(file_path),
                "operation": operation,
                "size": size,
                "checksum": self._calculate_checksum(file_path),
            }

            self._append_to_log(self.operation_log, log_entry)

        except Exception:
            pass  # Don't fail the main operation for logging issues

    def _log_error(self, error_message: str):
        """Log corruption and error events"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "error": error_message,
                "pid": os.getpid(),
            }

            self._append_to_log(self.corruption_log, log_entry)
            print(f"🛑 SAFE WRITE ERROR: {error_message}")

        except Exception:
            print(f"🛑 CRITICAL ERROR (logging failed): {error_message}")

    def _append_to_log(self, log_file: Path, entry: Dict[str, Any]):
        """Safely append to a log file"""
        try:
            logs = []
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)

            logs.append(entry)

            # Keep only last 1000 entries
            if len(logs) > 1000:
                logs = logs[-1000:]

            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2)

        except Exception:
            # If we can't log, at least print to console
            print(f"📝 {entry}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "unknown"

    def get_corruption_report(self) -> Dict[str, Any]:
        """Get a report of any corruption issues"""
        try:
            if not self.corruption_log.exists():
                return {"corruption_events": 0, "recent_errors": []}

            with open(self.corruption_log, "r", encoding="utf-8") as f:
                logs = json.load(f)

            recent_errors = [log for log in logs if self._is_recent(log["timestamp"])]

            return {
                "corruption_events": len(logs),
                "recent_errors": recent_errors[-10:],  # Last 10 errors
                "log_file": str(self.corruption_log),
            }

        except Exception:
            return {"error": "Could not read corruption log"}

    def _is_recent(self, timestamp_str: str, hours: int = 24) -> bool:
        """Check if a timestamp is within the last N hours"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            return (now - timestamp).total_seconds() < (hours * 3600)
        except:
            return False


# Global safe writer instance
_safe_writer = None


def get_safe_writer() -> SafeFileWriter:
    """Get the global safe file writer instance"""
    global _safe_writer
    if _safe_writer is None:
        _safe_writer = SafeFileWriter()
    return _safe_writer


def safe_write_file(file_path: str, content: str, encoding: str = "utf-8") -> bool:
    """
    Convenience function for safe file writing

    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: File encoding

    Returns:
        bool: True if successful, False if failed
    """
    return get_safe_writer().safe_write(file_path, content, encoding)


def check_for_corruption() -> Dict[str, Any]:
    """Check for any recent file corruption issues"""
    return get_safe_writer().get_corruption_report()


if __name__ == "__main__":
    # Test the safe file writing system
    print("🛡️ TESTING SAFE FILE WRITER")
    print("=" * 40)

    writer = SafeFileWriter("test_backups")

    # Test 1: Basic safe write
    test_file = "test_safe_write.txt"
    test_content = "This is a test of the safe file writing system.\nLine 2\nLine 3"

    print("📝 Testing basic safe write...")
    success = writer.safe_write(test_file, test_content)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

    # Test 2: Write to existing file (should create backup)
    print("\n📝 Testing overwrite with backup...")
    new_content = "This is updated content.\nNew line 2\nNew line 3"
    success = writer.safe_write(test_file, new_content)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

    # Test 3: Check corruption report
    print("\n📊 Checking corruption report...")
    report = writer.get_corruption_report()
    print(f"   Corruption events: {report.get('corruption_events', 0)}")
    print(f"   Recent errors: {len(report.get('recent_errors', []))}")

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

    print("\n🎉 Safe file writer test complete!")
