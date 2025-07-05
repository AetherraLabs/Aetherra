# src/neurocode/plugins/file_tools.py - File Management Plugin
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from core.plugin_manager import register_plugin


@register_plugin(
    name="create_file",
    description="Create a new file with optional content",
    capabilities=["file_creation", "file_management", "workspace"],
    version="1.0.0",
    author="AetherraCode Team",
    category="file_management",
    dependencies=["pathlib"],
    intent_purpose="file creation and workspace management",
    intent_triggers=["create", "new", "file", "make", "write"],
    intent_scenarios=[
        "creating new source files",
        "generating configuration files",
        "setting up project structure",
        "writing documentation files"
    ],
    ai_description="Creates new files with optional initial content. Automatically creates parent directories if needed.",

    example_usage="plugin: create_file 'src/utils.py' 'def hello():\\n    print(\"Hello World\")'",
    confidence_boost=1.2,
)
def create_file(filepath: str, content: str = "") -> Dict[str, Any]:
    """Create a new file with optional content"""
    try:
        path = Path(filepath)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file already exists
        if path.exists():
            return {
                "error": f"File '{filepath}' already exists",
                "suggestion": "Use 'write_file' to overwrite or 'append_file' to add content"
            }

        # Create the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "filepath": str(path.absolute()),
            "size": len(content),
            "created": True
        }

    except Exception as e:
        return {"error": f"Failed to create file: {str(e)}"}


@register_plugin(
    name="read_file",
    description="Read the contents of a file",
    capabilities=["file_reading", "content_access", "workspace"],
    version="1.0.0",
    author="AetherraCode Team",
    category="file_management",
    dependencies=["pathlib"],
    intent_purpose="file content reading and access",
    intent_triggers=["read", "view", "show", "content", "open"],
    intent_scenarios=[
        "reading source code",
        "viewing configuration files",
        "accessing documentation",
        "inspecting file contents"
    ],
    ai_description="Reads and returns the contents of text files. Supports various text encodings.",
    example_usage="plugin: read_file 'config.json'",
    confidence_boost=1.1,
)
def read_file(filepath: str, max_lines: Optional[int] = None) -> Dict[str, Any]:
    """Read the contents of a file"""
    try:
        path = Path(filepath)

        if not path.exists():
            return {"error": f"File '{filepath}' does not exist"}

        if not path.is_file():
            return {"error": f"'{filepath}' is not a file"}

        # Read file content
        with open(path, 'r', encoding='utf-8') as f:
            if max_lines:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip('\n'))
                content = '\n'.join(lines)
                truncated = i + 1 >= max_lines
            else:
                content = f.read()
                truncated = False

        return {
            "success": True,
            "filepath": str(path.absolute()),
            "content": content,
            "size": len(content),
            "lines": content.count('\n') + 1 if content else 0,
            "truncated": truncated
        }

    except UnicodeDecodeError:
        return {"error": f"File '{filepath}' is not a valid text file"}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}


@register_plugin(
    name="write_file",
    description="Write content to a file (overwrites existing content)",
    capabilities=["file_writing", "content_modification", "workspace"],
    version="1.0.0",
    author="AetherraCode Team",
    category="file_management",
    dependencies=["pathlib"],
    intent_purpose="file content writing and modification",
    intent_triggers=["write", "save", "overwrite", "update"],
    intent_scenarios=[
        "updating source code",
        "modifying configuration files",
        "saving generated content",
        "writing documentation"
    ],
    ai_description="Writes content to files, overwriting existing content. Creates parent directories if needed.",
    example_usage="plugin: write_file 'config.json' '{\"debug\": true}'",
    confidence_boost=1.1,
)
def write_file(filepath: str, content: str) -> Dict[str, Any]:
    """Write content to a file (overwrites existing content)"""
    try:
        path = Path(filepath)

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Backup existing file if it exists
        backup_created = False
        if path.exists():
            backup_path = path.with_suffix(path.suffix + '.backup')
            shutil.copy2(path, backup_path)
            backup_created = True

        # Write the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "filepath": str(path.absolute()),
            "size": len(content),
            "backup_created": backup_created,
            "overwritten": backup_created
        }

    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}


@register_plugin(
    name="list_files",
    description="List files and directories in a given path",
    capabilities=["directory_listing", "file_discovery", "workspace"],
    version="1.0.0",
    author="AetherraCode Team",
    category="file_management",
    dependencies=["pathlib"],
    intent_purpose="directory exploration and file discovery",
    intent_triggers=["list", "show", "directory", "folder", "files"],
    intent_scenarios=[
        "exploring project structure",
        "finding source files",
        "browsing directories",
        "workspace navigation"
    ],
    ai_description="Lists files and directories in a specified path with optional filtering by extensions.",
    example_usage="plugin: list_files 'src' '*.py'",
    confidence_boost=1.0,
)
def list_files(directory: str = ".", pattern: str = "*", include_hidden: bool = False) -> Dict[str, Any]:
    """List files and directories in a given path"""
    try:
        path = Path(directory)

        if not path.exists():
            return {"error": f"Directory '{directory}' does not exist"}

        if not path.is_dir():
            return {"error": f"'{directory}' is not a directory"}

        # Get all matching items
        if pattern == "*":
            items = list(path.iterdir())
        else:
            items = list(path.glob(pattern))

        # Filter hidden files if requested
        if not include_hidden:
            items = [item for item in items if not item.name.startswith('.')]

        # Categorize items
        files = []
        directories = []

        for item in sorted(items):
            item_info = {
                "name": item.name,
                "path": str(item.absolute()),
                "size": item.stat().st_size if item.is_file() else None,
                "modified": item.stat().st_mtime
            }

            if item.is_file():
                files.append(item_info)
            elif item.is_dir():
                directories.append(item_info)

        return {
            "success": True,
            "directory": str(path.absolute()),
            "pattern": pattern,
            "files": files,
            "directories": directories,
            "total_files": len(files),
            "total_directories": len(directories)
        }

    except Exception as e:
        return {"error": f"Failed to list files: {str(e)}"}


@register_plugin(
    name="delete_file",
    description="Delete a file or directory (with safety confirmation)",
    capabilities=["file_deletion", "cleanup", "workspace"],
    version="1.0.0",
    author="AetherraCode Team",
    category="file_management",
    dependencies=["pathlib", "shutil"],
    intent_purpose="file and directory deletion with safety checks",
    intent_triggers=["delete", "remove", "clean", "rm"],
    intent_scenarios=[
        "cleaning up temporary files",
        "removing unused files",
        "workspace cleanup",
        "file management"
    ],
    ai_description="Safely deletes files or directories with backup creation and confirmation. Includes safety checks for important files.",

    example_usage="plugin: delete_file 'temp.txt' true",
    confidence_boost=0.8,  # Lower confidence due to destructive nature
)
def delete_file(filepath: str, confirm: bool = False, create_backup: bool = True) -> Dict[str, Any]:
    """Delete a file or directory (with safety confirmation)"""
    try:
        path = Path(filepath)

        if not path.exists():
            return {"error": f"'{filepath}' does not exist"}

        # Safety check - prevent deletion of important files
        important_files = ['.git', '.project_protection.json', 'README.md', 'requirements.txt']
        if path.name in important_files:
            return {
                "error": f"Cannot delete important file '{path.name}'",
                "suggestion": "This file is protected from deletion"
            }

        if not confirm:
            return {
                "error": "Deletion requires confirmation",
                "suggestion": "Set confirm=true to proceed with deletion"
            }

        backup_path = None
        if create_backup and path.is_file():
            backup_path = path.with_suffix(path.suffix + '.deleted.backup')
            shutil.copy2(path, backup_path)

        # Delete the file/directory
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)

        return {
            "success": True,
            "deleted": str(path.absolute()),
            "type": "file" if path.is_file() else "directory",
            "backup_created": backup_path is not None,
            "backup_path": str(backup_path) if backup_path else None
        }

    except Exception as e:
        return {"error": f"Failed to delete: {str(e)}"}
