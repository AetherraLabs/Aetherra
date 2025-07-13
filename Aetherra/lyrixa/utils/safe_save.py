"""
Safe Save Utility for Lyrixa
Provides atomic write operations with automatic backup and validation
"""

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional


class SafeSavePlugin:
    """Safe file writing with atomic operations and backup creation"""

    def __init__(self, backup_dir: Optional[str] = None):
        self.backup_dir = backup_dir or ".safe_backups"
        os.makedirs(self.backup_dir, exist_ok=True)

    def safe_write_text(
        self, file_path: str, content: str, encoding: str = "utf-8"
    ) -> bool:
        """
        Safely write text content to a file with atomic operations

        Args:
            file_path: Target file path
            content: Text content to write
            encoding: File encoding (default: utf-8)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create backup if file exists
            if os.path.exists(file_path):
                self._create_backup(file_path)

            # Write to temporary file first
            temp_path = file_path + ".tmp"
            with open(temp_path, "w", encoding=encoding) as f:
                f.write(content)

            # Verify write was successful
            if self._verify_file_content(temp_path, content, encoding):
                # Atomic move to final location
                shutil.move(temp_path, file_path)
                return True
            else:
                # Cleanup failed temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False

        except Exception as e:
            print(f"Safe write failed: {e}")
            # Cleanup temp file if it exists
            temp_path = file_path + ".tmp"
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False

    def _create_backup(self, file_path: str) -> str:
        """Create a backup of the existing file"""
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_name = f"{filename}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)

        shutil.copy2(file_path, backup_path)
        return backup_path

    def _verify_file_content(
        self, file_path: str, expected_content: str, encoding: str
    ) -> bool:
        """Verify that file contains expected content"""
        try:
            with open(file_path, "r", encoding=encoding) as f:
                actual_content = f.read()
            return actual_content == expected_content
        except Exception:
            return False

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
