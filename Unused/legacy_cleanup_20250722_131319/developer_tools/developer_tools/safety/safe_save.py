"""
Safe-Save Plugin - Enforced Atomic Write Operations

This module provides a plugin system that enforces safe file operations
throughout the Aetherra & Lyrixa project, ensuring atomic writes, automatic
backups, and corruption prevention.

Key Features:
- Enforced atomic write operations
- Automatic backup creation
- Write validation and verification
- Integration with existing systems
- Plugin-based architecture for extensibility
"""

import os
import json
import hashlib
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager

# Import existing safe file operations
try:
    from safe_file_operations import SafeFileWriter
except ImportError:
    SafeFileWriter = None

try:
    from lyrixa_backup_system import LyrixaBackupSystem
except ImportError:
    LyrixaBackupSystem = None

class SafeSaveConfig:
    """Configuration for Safe-Save plugin"""

    def __init__(self):
        self.enforce_atomic_writes = True
        self.create_backups = True
        self.validate_writes = True
        self.verify_checksums = True
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.backup_retention_days = 7
        self.critical_files = {
            'memory_store.json', 'goals_store.json', 'plugin_registry.json',
            'agent_config.json', 'system_config.json'
        }
        self.critical_extensions = {'.json', '.yaml', '.yml'}
        self.log_file = 'safe_save.log'

class WriteValidator:
    """Validates write operations before execution"""

    def __init__(self, config: SafeSaveConfig):
        self.config = config
        self.logger = logging.getLogger('SafeSave.Validator')

    def validate_file_path(self, filepath: Path) -> bool:
        """Validate file path for safety"""
        try:
            # Check if path is absolute and safe
            resolved_path = filepath.resolve()

            # Prevent writing outside project directory
            current_dir = Path.cwd().resolve()
            if not str(resolved_path).startswith(str(current_dir)):
                self.logger.warning(f"Attempted write outside project directory: {resolved_path}")
                return False

            # Check parent directory exists or can be created
            parent_dir = resolved_path.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.logger.error(f"Cannot create parent directory {parent_dir}: {e}")
                    return False

            # Check write permissions
            if not os.access(parent_dir, os.W_OK):
                self.logger.error(f"No write permission for directory {parent_dir}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating file path {filepath}: {e}")
            return False

    def validate_content(self, content: str, filepath: Path) -> bool:
        """Validate content before writing"""
        try:
            # Check file size
            content_size = len(content.encode('utf-8'))
            if content_size > self.config.max_file_size:
                self.logger.error(f"Content too large ({content_size} bytes) for {filepath}")
                return False

            # Validate JSON files
            if filepath.suffix.lower() == '.json':
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON content for {filepath}: {e}")
                    return False

            # Check for suspicious content patterns
            suspicious_patterns = ['rm -rf', 'del /s', '__import__("os").system']
            content_lower = content.lower()
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    self.logger.warning(f"Suspicious pattern '{pattern}' found in {filepath}")
                    # Don't block, just warn

            return True

        except Exception as e:
            self.logger.error(f"Error validating content for {filepath}: {e}")
            return False

class AtomicWriter:
    """Provides atomic write operations"""

    def __init__(self, config: SafeSaveConfig):
        self.config = config
        self.logger = logging.getLogger('SafeSave.AtomicWriter')

    def write_atomic(self, filepath: Path, content: str, encoding: str = 'utf-8') -> bool:
        """Write content atomically to file"""
        temp_path = None
        try:
            # Create temporary file in same directory
            temp_dir = filepath.parent
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding=encoding,
                dir=temp_dir,
                delete=False,
                prefix=f".{filepath.name}_",
                suffix='.tmp'
            ) as temp_file:
                temp_path = Path(temp_file.name)

                # Write content to temporary file
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # Force write to disk

            # Verify temporary file was written correctly
            if not self._verify_temp_file(temp_path, content, encoding):
                temp_path.unlink(missing_ok=True)
                return False

            # Atomic move to final location
            if os.name == 'nt':  # Windows
                # Windows doesn't support atomic replace, need to handle differently
                if filepath.exists():
                    backup_path = filepath.with_suffix(f'{filepath.suffix}.bak')
                    filepath.rename(backup_path)
                    try:
                        temp_path.rename(filepath)
                        backup_path.unlink(missing_ok=True)
                    except Exception:
                        # Restore backup if rename failed
                        backup_path.rename(filepath)
                        temp_path.unlink(missing_ok=True)
                        raise
                else:
                    temp_path.rename(filepath)
            else:  # Unix-like systems
                temp_path.replace(filepath)

            self.logger.info(f"Atomic write successful: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Atomic write failed for {filepath}: {e}")
            # Clean up temporary file
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except:
                    pass
            return False

    def _verify_temp_file(self, temp_path: Path, expected_content: str, encoding: str) -> bool:
        """Verify temporary file was written correctly"""
        try:
            with open(temp_path, 'r', encoding=encoding) as f:
                actual_content = f.read()

            if actual_content != expected_content:
                self.logger.error(f"Content verification failed for {temp_path}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error verifying temporary file {temp_path}: {e}")
            return False

class BackupManager:
    """Manages backups for safe-save operations"""

    def __init__(self, config: SafeSaveConfig):
        self.config = config
        self.logger = logging.getLogger('SafeSave.BackupManager')
        self.backup_dir = Path('backups/safe_save')
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, filepath: Path) -> Optional[Path]:
        """Create backup of file before modification"""
        try:
            if not filepath.exists():
                return None

            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}.backup"
            backup_path = self.backup_dir / backup_filename

            # Copy file with metadata
            import shutil
            shutil.copy2(filepath, backup_path)

            self.logger.info(f"Created backup: {backup_path}")
            return backup_path

        except Exception as e:
            self.logger.error(f"Failed to create backup for {filepath}: {e}")
            return None

    def cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            cutoff_time = datetime.now().timestamp() - (self.config.backup_retention_days * 24 * 3600)

            for backup_file in self.backup_dir.glob('*.backup'):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    self.logger.info(f"Cleaned up old backup: {backup_file}")

        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")

class SafeSavePlugin:
    """
    Main Safe-Save Plugin class that enforces atomic operations
    """

    def __init__(self, config: Optional[SafeSaveConfig] = None):
        self.config = config or SafeSaveConfig()
        self.logger = self._setup_logging()

        # Initialize components
        self.validator = WriteValidator(self.config)
        self.atomic_writer = AtomicWriter(self.config)
        self.backup_manager = BackupManager(self.config)

        # Statistics
        self.stats = {
            'total_writes': 0,
            'successful_writes': 0,
            'failed_writes': 0,
            'backups_created': 0,
            'validations_failed': 0
        }

        self.logger.info("SafeSave plugin initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for SafeSave plugin"""
        logger = logging.getLogger('SafeSave')
        logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(self.config.log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)

        return logger

    def is_critical_file(self, filepath: Path) -> bool:
        """Check if file is critical and needs extra protection"""
        filename = filepath.name.lower()
        extension = filepath.suffix.lower()

        return (filename in self.config.critical_files or
                extension in self.config.critical_extensions)

    def safe_write_text(self, filepath: str | Path, content: str, encoding: str = 'utf-8') -> bool:
        """Safely write text content to file with full protection"""
        filepath = Path(filepath)
        self.stats['total_writes'] += 1

        try:
            # Validate file path
            if not self.validator.validate_file_path(filepath):
                self.stats['validations_failed'] += 1
                self.stats['failed_writes'] += 1
                return False

            # Validate content
            if not self.validator.validate_content(content, filepath):
                self.stats['validations_failed'] += 1
                self.stats['failed_writes'] += 1
                return False

            # Create backup if file exists and backups are enabled
            backup_path = None
            if self.config.create_backups and filepath.exists():
                backup_path = self.backup_manager.create_backup(filepath)
                if backup_path:
                    self.stats['backups_created'] += 1

            # Calculate content checksum
            content_checksum = hashlib.md5(content.encode(encoding)).hexdigest()

            # Perform atomic write
            if self.config.enforce_atomic_writes:
                success = self.atomic_writer.write_atomic(filepath, content, encoding)
            else:
                # Fallback to regular write (not recommended)
                try:
                    with open(filepath, 'w', encoding=encoding) as f:
                        f.write(content)
                    success = True
                except Exception as e:
                    self.logger.error(f"Regular write failed for {filepath}: {e}")
                    success = False

            if success:
                # Verify write if enabled
                if self.config.verify_checksums:
                    if not self._verify_write(filepath, content_checksum, encoding):
                        self.logger.error(f"Write verification failed for {filepath}")
                        self.stats['failed_writes'] += 1
                        return False

                self.stats['successful_writes'] += 1
                self.logger.info(f"Safe write completed successfully: {filepath}")
                return True
            else:
                self.stats['failed_writes'] += 1
                return False

        except Exception as e:
            self.logger.error(f"Safe write failed for {filepath}: {e}")
            self.stats['failed_writes'] += 1
            return False

    def safe_write_json(self, filepath: str | Path, data: Any, indent: int = 2) -> bool:
        """Safely write JSON data to file"""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.safe_write_text(filepath, content)
        except Exception as e:
            self.logger.error(f"Failed to serialize JSON for {filepath}: {e}")
            return False

    def _verify_write(self, filepath: Path, expected_checksum: str, encoding: str) -> bool:
        """Verify that file was written correctly"""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()

            actual_checksum = hashlib.md5(content.encode(encoding)).hexdigest()
            return actual_checksum == expected_checksum

        except Exception as e:
            self.logger.error(f"Error verifying write for {filepath}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get plugin statistics"""
        total = self.stats['total_writes']
        return {
            **self.stats,
            'success_rate': self.stats['successful_writes'] / total if total > 0 else 0,
            'failure_rate': self.stats['failed_writes'] / total if total > 0 else 0
        }

    def cleanup_old_data(self):
        """Clean up old backups and logs"""
        try:
            self.backup_manager.cleanup_old_backups()
            self.logger.info("Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

# Global instance for easy access
_safe_save_instance = None

def get_safe_save_plugin(config: Optional[SafeSaveConfig] = None) -> SafeSavePlugin:
    """Get or create global SafeSave plugin instance"""
    global _safe_save_instance
    if _safe_save_instance is None:
        _safe_save_instance = SafeSavePlugin(config)
    return _safe_save_instance

# Convenience functions
def safe_write_file(filepath: str | Path, content: str, encoding: str = 'utf-8') -> bool:
    """Convenience function for safe file writing"""
    plugin = get_safe_save_plugin()
    return plugin.safe_write_text(filepath, content, encoding)

def safe_write_json_file(filepath: str | Path, data: Any, indent: int = 2) -> bool:
    """Convenience function for safe JSON writing"""
    plugin = get_safe_save_plugin()
    return plugin.safe_write_json(filepath, data, indent)

# Context manager for safe operations
@contextmanager
def safe_save_context(config: Optional[SafeSaveConfig] = None):
    """Context manager for safe save operations"""
    plugin = SafeSavePlugin(config)
    try:
        yield plugin
    finally:
        plugin.cleanup_old_data()

if __name__ == "__main__":
    # Example usage and testing
    print("SafeSave Plugin - Testing")

    # Test configuration
    config = SafeSaveConfig()

    with safe_save_context(config) as plugin:
        print("SafeSave plugin active - testing operations")

        # Test safe JSON write
        test_data = {
            "system": "Aetherra & Lyrixa",
            "component": "SafeSave Plugin",
            "timestamp": datetime.now().isoformat(),
            "test": True
        }

        try:
            success = plugin.safe_write_json("test_safe_save.json", test_data)
            print(f"✓ Safe JSON write: {'SUCCESS' if success else 'FAILED'}")
        except Exception as e:
            print(f"✗ Safe JSON write failed: {e}")

        # Test safe text write
        try:
            success = plugin.safe_write_text("test_safe_save.txt", "Test content for SafeSave plugin")
            print(f"✓ Safe text write: {'SUCCESS' if success else 'FAILED'}")
        except Exception as e:
            print(f"✗ Safe text write failed: {e}")

        # Print statistics
        stats = plugin.get_stats()
        print(f"Plugin statistics: {stats}")

        # Test critical file protection
        try:
            success = plugin.safe_write_json("memory_store.json", {"test": "critical_data"})
            print(f"✓ Critical file write: {'SUCCESS' if success else 'FAILED'}")
        except Exception as e:
            print(f"✗ Critical file write failed: {e}")

    print("SafeSave plugin testing completed")
