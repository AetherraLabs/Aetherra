"""
WriteGuard System - File Write Monitoring and Protection

This module provides comprehensive file write monitoring, logging, and protection
to prevent data corruption and accidental overwrites in the Aetherra & Lyrixa project.

Key Features:
- File access interception and logging
- Write operation validation and rollback
- Automatic backup creation before writes
- Permission and safety checks
- Integration with existing safe file operations
"""

import os
import sys
import json
import time
import shutil
import hashlib
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from contextlib import contextmanager

# Import existing safe file operations
try:
    from safe_file_operations import SafeFileWriter
except ImportError:
    SafeFileWriter = None

class WriteGuardConfig:
    """Configuration for WriteGuard system"""

    def __init__(self):
        self.log_all_writes = True
        self.backup_before_write = True
        self.validate_permissions = True
        self.protected_extensions = {'.json', '.py', '.md', '.txt', '.yaml', '.yml'}
        self.protected_directories = {'lyrixa', 'core', 'plugins', 'config'}
        self.max_backup_size = 100 * 1024 * 1024  # 100MB
        self.log_file = 'write_guard.log'
        self.rollback_enabled = True
        self.dry_run_mode = False

class WriteOperation:
    """Represents a single write operation"""

    def __init__(self, filepath: str, operation_type: str, size: int = 0):
        self.filepath = Path(filepath)
        self.operation_type = operation_type  # 'create', 'modify', 'delete'
        self.size = size
        self.timestamp = datetime.now()
        self.backup_path: Optional[Path] = None
        self.checksum_before: Optional[str] = None
        self.checksum_after: Optional[str] = None
        self.success = False
        self.error_message: Optional[str] = None

class WriteGuard:
    """
    Main WriteGuard class that monitors and protects file write operations
    """

    def __init__(self, config: Optional[WriteGuardConfig] = None):
        self.config = config or WriteGuardConfig()
        self.logger = self._setup_logging()
        self.operations_log: List[WriteOperation] = []
        self.active_operations: Dict[str, WriteOperation] = {}
        self.lock = threading.Lock()
        self.rollback_stack: List[WriteOperation] = []

        # Hook into Python's file operations
        self._setup_file_hooks()

        self.logger.info("WriteGuard system initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for WriteGuard"""
        logger = logging.getLogger('WriteGuard')
        logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(self.config.log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)

        # Console handler for critical issues
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)

        return logger

    def _setup_file_hooks(self):
        """Setup hooks to intercept file operations"""
        # Store original functions
        self._original_open = open
        self._original_remove = os.remove
        self._original_rename = os.rename

        # Replace with monitored versions
        __builtins__['open'] = self._monitored_open
        os.remove = self._monitored_remove
        os.rename = self._monitored_rename

    def _get_file_checksum(self, filepath: Path) -> Optional[str]:
        """Calculate file checksum"""
        try:
            if not filepath.exists():
                return None

            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to calculate checksum for {filepath}: {e}")
            return None

    def _should_protect_file(self, filepath: Path) -> bool:
        """Determine if a file should be protected"""
        # Check extension
        if filepath.suffix.lower() in self.config.protected_extensions:
            return True

        # Check if in protected directory
        try:
            for protected_dir in self.config.protected_directories:
                if protected_dir in str(filepath).lower():
                    return True
        except Exception:
            pass

        return False

    def _create_backup(self, filepath: Path) -> Optional[Path]:
        """Create backup of file before modification"""
        try:
            if not filepath.exists():
                return None

            # Check file size
            if filepath.stat().st_size > self.config.max_backup_size:
                self.logger.warning(f"File {filepath} too large for backup")
                return None

            # Create backup path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path("backups/write_guard")
            backup_dir.mkdir(parents=True, exist_ok=True)

            backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}.backup"
            backup_path = backup_dir / backup_filename

            # Copy file
            shutil.copy2(filepath, backup_path)
            self.logger.info(f"Created backup: {backup_path}")

            return backup_path

        except Exception as e:
            self.logger.error(f"Failed to create backup for {filepath}: {e}")
            return None

    def _validate_write_operation(self, filepath: Path, operation_type: str) -> bool:
        """Validate if write operation should be allowed"""
        try:
            # Check if file is locked by another process
            if filepath.exists() and operation_type == 'modify':
                try:
                    with open(filepath, 'r+'):
                        pass
                except PermissionError:
                    self.logger.warning(f"File {filepath} is locked by another process")
                    return False

            # Check available disk space
            if operation_type in ['create', 'modify']:
                stat = shutil.disk_usage(filepath.parent)
                if stat.free < 100 * 1024 * 1024:  # Less than 100MB free
                    self.logger.warning(f"Insufficient disk space for operation on {filepath}")
                    return False

            # Check permissions
            if self.config.validate_permissions:
                parent_dir = filepath.parent
                if not os.access(parent_dir, os.W_OK):
                    self.logger.warning(f"No write permission for directory {parent_dir}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating write operation: {e}")
            return False

    def _log_operation(self, operation: WriteOperation):
        """Log a write operation"""
        with self.lock:
            self.operations_log.append(operation)

            # Log to file
            log_data = {
                'timestamp': operation.timestamp.isoformat(),
                'filepath': str(operation.filepath),
                'operation_type': operation.operation_type,
                'size': operation.size,
                'success': operation.success,
                'error': operation.error_message,
                'backup_path': str(operation.backup_path) if operation.backup_path else None
            }

            self.logger.info(f"Write operation: {json.dumps(log_data)}")

    def _monitored_open(self, file, mode='r', **kwargs):
        """Monitored version of open()"""
        filepath = Path(file)

        # Check if this is a write operation
        if any(m in mode for m in ['w', 'a', 'x', '+']):
            return self._handle_write_operation(filepath, mode, **kwargs)
        else:
            # Read operation, use original
            return self._original_open(file, mode, **kwargs)

    def _monitored_remove(self, path):
        """Monitored version of os.remove()"""
        filepath = Path(path)

        if self._should_protect_file(filepath):
            operation = WriteOperation(str(filepath), 'delete')

            try:
                # Validate operation
                if not self._validate_write_operation(filepath, 'delete'):
                    raise PermissionError("Write operation not allowed by WriteGuard")

                # Create backup
                if self.config.backup_before_write:
                    operation.backup_path = self._create_backup(filepath)

                # Perform operation if not in dry run mode
                if not self.config.dry_run_mode:
                    self._original_remove(path)

                operation.success = True

            except Exception as e:
                operation.error_message = str(e)
                self.logger.error(f"Failed to remove {filepath}: {e}")
                raise
            finally:
                self._log_operation(operation)
        else:
            # Not protected, use original
            self._original_remove(path)

    def _monitored_rename(self, src, dst):
        """Monitored version of os.rename()"""
        src_path = Path(src)
        dst_path = Path(dst)

        if self._should_protect_file(src_path) or self._should_protect_file(dst_path):
            operation = WriteOperation(str(src_path), 'move')

            try:
                # Validate operation
                if not self._validate_write_operation(src_path, 'move'):
                    raise PermissionError("Write operation not allowed by WriteGuard")

                # Create backup of source
                if self.config.backup_before_write:
                    operation.backup_path = self._create_backup(src_path)

                # Perform operation if not in dry run mode
                if not self.config.dry_run_mode:
                    self._original_rename(src, dst)

                operation.success = True

            except Exception as e:
                operation.error_message = str(e)
                self.logger.error(f"Failed to rename {src_path} to {dst_path}: {e}")
                raise
            finally:
                self._log_operation(operation)
        else:
            # Not protected, use original
            self._original_rename(src, dst)

    def _handle_write_operation(self, filepath: Path, mode: str, **kwargs):
        """Handle a write operation through open()"""
        if not self._should_protect_file(filepath):
            return self._original_open(filepath, mode, **kwargs)

        # Determine operation type
        operation_type = 'create' if not filepath.exists() else 'modify'
        operation = WriteOperation(str(filepath), operation_type)

        try:
            # Validate operation
            if not self._validate_write_operation(filepath, operation_type):
                raise PermissionError("Write operation not allowed by WriteGuard")

            # Get checksum before
            operation.checksum_before = self._get_file_checksum(filepath)

            # Create backup
            if self.config.backup_before_write and filepath.exists():
                operation.backup_path = self._create_backup(filepath)

            # Store operation for monitoring
            with self.lock:
                self.active_operations[str(filepath)] = operation

            # Use SafeFileWriter if available, otherwise original open
            if SafeFileWriter and 'w' in mode:
                if self.config.dry_run_mode:
                    # Return a dummy file-like object for dry run
                    return open(os.devnull, 'w')
                else:
                    return SafeFileWriter(str(filepath))
            else:
                if self.config.dry_run_mode:
                    return open(os.devnull, mode)
                else:
                    return MonitoredFile(filepath, mode, self, operation, **kwargs)

        except Exception as e:
            operation.error_message = str(e)
            operation.success = False
            self._log_operation(operation)
            raise

    def rollback_operation(self, operation: WriteOperation) -> bool:
        """Rollback a write operation using backup"""
        try:
            if not operation.backup_path or not operation.backup_path.exists():
                self.logger.error(f"No backup available for rollback: {operation.filepath}")
                return False

            # Restore from backup
            shutil.copy2(operation.backup_path, operation.filepath)
            self.logger.info(f"Rolled back {operation.filepath} from backup")

            return True

        except Exception as e:
            self.logger.error(f"Failed to rollback {operation.filepath}: {e}")
            return False

    def rollback_last_operation(self) -> bool:
        """Rollback the last write operation"""
        with self.lock:
            if not self.rollback_stack:
                self.logger.warning("No operations to rollback")
                return False

            last_operation = self.rollback_stack.pop()
            return self.rollback_operation(last_operation)

    def get_operation_stats(self) -> Dict[str, Any]:
        """Get statistics about write operations"""
        with self.lock:
            total_ops = len(self.operations_log)
            successful_ops = sum(1 for op in self.operations_log if op.success)
            failed_ops = total_ops - successful_ops

            operation_types = {}
            for op in self.operations_log:
                operation_types[op.operation_type] = operation_types.get(op.operation_type, 0) + 1

            return {
                'total_operations': total_ops,
                'successful_operations': successful_ops,
                'failed_operations': failed_ops,
                'success_rate': successful_ops / total_ops if total_ops > 0 else 0,
                'operation_types': operation_types,
                'active_operations': len(self.active_operations)
            }

    def cleanup(self):
        """Cleanup and restore original file functions"""
        try:
            # Restore original functions
            __builtins__['open'] = self._original_open
            os.remove = self._original_remove
            os.rename = self._original_rename

            self.logger.info("WriteGuard cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during WriteGuard cleanup: {e}")

class MonitoredFile:
    """Wrapper for file objects to monitor write operations"""

    def __init__(self, filepath: Path, mode: str, write_guard: WriteGuard, operation: WriteOperation, **kwargs):
        self.filepath = filepath
        self.write_guard = write_guard
        self.operation = operation
        self._file = write_guard._original_open(filepath, mode, **kwargs)
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattr__(self, name):
        return getattr(self._file, name)

    def write(self, data):
        """Monitor write operations"""
        try:
            result = self._file.write(data)
            self.operation.size += len(str(data))
            return result
        except Exception as e:
            self.operation.error_message = str(e)
            raise

    def close(self):
        """Close file and finalize operation monitoring"""
        if self._closed:
            return

        try:
            self._file.close()

            # Calculate checksum after
            self.operation.checksum_after = self.write_guard._get_file_checksum(self.filepath)
            self.operation.success = True

            # Add to rollback stack if successful
            if self.operation.success and self.write_guard.config.rollback_enabled:
                with self.write_guard.lock:
                    self.write_guard.rollback_stack.append(self.operation)
                    # Keep only last 10 operations for rollback
                    if len(self.write_guard.rollback_stack) > 10:
                        self.write_guard.rollback_stack.pop(0)

        except Exception as e:
            self.operation.error_message = str(e)
            self.operation.success = False

        finally:
            # Remove from active operations and log
            with self.write_guard.lock:
                self.write_guard.active_operations.pop(str(self.filepath), None)

            self.write_guard._log_operation(self.operation)
            self._closed = True

# Context manager for temporary WriteGuard activation
@contextmanager
def write_guard_protection(config: Optional[WriteGuardConfig] = None):
    """Context manager for temporary WriteGuard protection"""
    guard = WriteGuard(config)
    try:
        yield guard
    finally:
        guard.cleanup()

# Decorator for protecting specific functions
def protected_write_operation(func: Callable) -> Callable:
    """Decorator to protect write operations in specific functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with write_guard_protection():
            return func(*args, **kwargs)
    return wrapper

if __name__ == "__main__":
    # Example usage and testing
    print("WriteGuard System - Testing")

    # Test configuration
    config = WriteGuardConfig()
    config.dry_run_mode = True  # Safe testing mode

    with write_guard_protection(config) as guard:
        print("WriteGuard active - testing file operations")

        # Test protected write
        try:
            with open("test_protected.json", "w") as f:
                f.write('{"test": "data"}')
            print("✓ Protected write successful")
        except Exception as e:
            print(f"✗ Protected write failed: {e}")

        # Test unprotected write
        try:
            with open("test_unprotected.tmp", "w") as f:
                f.write("temporary data")
            print("✓ Unprotected write successful")
        except Exception as e:
            print(f"✗ Unprotected write failed: {e}")

        # Print statistics
        stats = guard.get_operation_stats()
        print(f"Operation statistics: {stats}")
