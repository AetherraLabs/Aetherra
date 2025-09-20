"""
File Organizer Plugin - Intelligent File Management System
Author: Aetherra Plugin System
Version: 1.0.0

Features:
- Smart file categorization using content and metadata
- Duplicate detection and removal
- Automated sorting rules (by type, date, tags, etc.)
- File tagging and annotation system
- Batch operations (move, copy, delete, rename)
- Integration with Aetherra workflows and plugins
- File preview and metadata extraction
- Rule-based automation (scheduled cleanups, archiving)
- Logging and reporting of file operations
"""

# Standard library imports
import hashlib
import json
import logging
import mimetypes
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FileInfo:
    """File information and metadata."""

    path: str
    name: str
    size: int
    type: str
    created: datetime
    modified: datetime
    tags: List[str]
    hash: Optional[str] = None
    is_duplicate: bool = False
    category: Optional[str] = None


@dataclass
class OrganizerRule:
    """File organization rule."""

    id: str
    name: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    is_active: bool = True
    priority: int = 0


class FileOrganizer:
    """Main File Organizer Plugin class."""

    def __init__(self, root_dir: str = "organized_files"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(exist_ok=True)
        self.rules: List[OrganizerRule] = []
        self.files: Dict[str, FileInfo] = {}
        self.logger = logging.getLogger("FileOrganizer")
        logging.basicConfig(level=logging.INFO)

    def scan_files(self, scan_dir: Optional[str] = None) -> List[FileInfo]:
        """Scan directory for files and collect metadata."""
        scan_path = Path(scan_dir) if scan_dir else self.root_dir
        file_infos = []
        for file_path in scan_path.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                file_info = FileInfo(
                    path=str(file_path),
                    name=file_path.name,
                    size=stat.st_size,
                    type=mimetypes.guess_type(file_path)[0] or "unknown",
                    created=datetime.fromtimestamp(stat.st_ctime),
                    modified=datetime.fromtimestamp(stat.st_mtime),
                    tags=[],
                    hash=None,
                    is_duplicate=False,
                    category=None,
                )
                file_infos.append(file_info)
                self.files[file_info.path] = file_info
        self.logger.info(f"Scanned {len(file_infos)} files in {scan_path}")
        return file_infos

    def compute_hashes(self):
        """Compute hashes for all files for duplicate detection."""
        for file_info in self.files.values():
            try:
                with open(file_info.path, "rb") as f:
                    file_info.hash = hashlib.sha256(f.read()).hexdigest()
            except Exception as e:
                self.logger.error(f"Failed to hash {file_info.path}: {e}")

    def detect_duplicates(self) -> List[FileInfo]:
        """Detect duplicate files by hash."""
        hash_map = {}
        duplicates = []
        for file_info in self.files.values():
            if not file_info.hash:
                continue
            if file_info.hash in hash_map:
                file_info.is_duplicate = True
                duplicates.append(file_info)
            else:
                hash_map[file_info.hash] = file_info
        self.logger.info(f"Detected {len(duplicates)} duplicate files")
        return duplicates

    def categorize_files(self):
        """Categorize files by type, date, or custom rules."""
        for file_info in self.files.values():
            if file_info.type and "image" in file_info.type:
                file_info.category = "Images"
            elif file_info.type and "pdf" in file_info.type:
                file_info.category = "PDFs"
            elif file_info.type and "text" in file_info.type:
                file_info.category = "Text Files"
            elif file_info.type and "audio" in file_info.type:
                file_info.category = "Audio"
            elif file_info.type and "video" in file_info.type:
                file_info.category = "Video"
            else:
                file_info.category = "Other"
        self.logger.info("Categorized files by type")

    def apply_rules(self):
        """Apply organization rules to files."""
        for rule in sorted(self.rules, key=lambda r: r.priority, reverse=True):
            if not rule.is_active:
                continue
            for file_info in self.files.values():
                if self._matches_conditions(file_info, rule.conditions):
                    self._apply_actions(file_info, rule.actions)
        self.logger.info("Applied organization rules")

    def _matches_conditions(
        self, file_info: FileInfo, conditions: Dict[str, Any]
    ) -> bool:
        for field, value in conditions.items():
            if getattr(file_info, field, None) != value:
                return False
        return True

    def _apply_actions(self, file_info: FileInfo, actions: Dict[str, Any]):
        for action, value in actions.items():
            if action == "move_to":
                self.move_file(file_info, value)
            elif action == "add_tag":
                if value not in file_info.tags:
                    file_info.tags.append(value)
            elif action == "delete":
                self.delete_file(file_info)
            elif action == "rename":
                self.rename_file(file_info, value)

    def move_file(self, file_info: FileInfo, target_dir: str):
        target_path = Path(target_dir) / file_info.name
        try:
            shutil.move(file_info.path, target_path)
            file_info.path = str(target_path)
            self.logger.info(f"Moved {file_info.name} to {target_dir}")
        except Exception as e:
            self.logger.error(f"Failed to move {file_info.path}: {e}")

    def delete_file(self, file_info: FileInfo):
        try:
            os.remove(file_info.path)
            self.logger.info(f"Deleted {file_info.name}")
        except Exception as e:
            self.logger.error(f"Failed to delete {file_info.path}: {e}")

    def rename_file(self, file_info: FileInfo, new_name: str):
        target_path = Path(file_info.path).parent / new_name
        try:
            os.rename(file_info.path, target_path)
            file_info.path = str(target_path)
            file_info.name = new_name
            self.logger.info(f"Renamed file to {new_name}")
        except Exception as e:
            self.logger.error(f"Failed to rename {file_info.path}: {e}")

    def add_rule(self, rule: OrganizerRule):
        self.rules.append(rule)
        self.logger.info(f"Added rule: {rule.name}")

    def report(self) -> Dict[str, Any]:
        """Generate report of file operations and status."""
        report = {
            "total_files": len(self.files),
            "duplicates": [asdict(f) for f in self.detect_duplicates()],
            "categories": {},
            "tags": {},
        }
        for file_info in self.files.values():
            cat = file_info.category or "Uncategorized"
            report["categories"].setdefault(cat, 0)
            report["categories"][cat] += 1
            for tag in file_info.tags:
                report["tags"].setdefault(tag, 0)
                report["tags"][tag] += 1
        return report


# Plugin entry point
def create_plugin():
    return FileOrganizer()


if __name__ == "__main__":
    organizer = FileOrganizer()
    organizer.scan_files()
    organizer.compute_hashes()
    organizer.categorize_files()
    organizer.apply_rules()
    print(json.dumps(organizer.report(), indent=2, default=str))
