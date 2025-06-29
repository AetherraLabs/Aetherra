#!/usr/bin/env python3
"""
🧬 NeuroCode Standard Library - CoreTools Plugin
Built-in plugin for file access and core utility tools
"""

import base64
import csv
import hashlib
import json
import os
import pathlib
import re
import shutil
import tempfile
import urllib.parse
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional


class CoreToolsPlugin:
    """Core utility tools for file access and common operations"""

    def __init__(self):
        self.name = "coretools"
        self.description = "File access and core utility tools"
        self.available_actions = [
            "read_file",
            "write_file",
            "append_file",
            "list_files",
            "file_exists",
            "create_directory",
            "delete_file",
            "copy_file",
            "move_file",
            "file_info",
            "search_files",
            "compress_files",
            "extract_archive",
            "calculate_hash",
            "read_json",
            "write_json",
            "read_csv",
            "write_csv",
            "parse_text",
            "format_data",
            "validate_data",
            "transform_data",
            "filter_data",
            "sort_data",
            "merge_data",
            "split_data",
            "encode_data",
            "decode_data",
            "status",
        ]
        self.temp_dir = tempfile.mkdtemp(prefix="neurocode_")
        self.operation_history = []

    # File Operations
    def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read content from a file"""
        try:
            with open(file_path, encoding=encoding) as f:
                content = f.read()

            self._log_operation("read_file", {"file_path": file_path, "size": len(content)})
            return content

        except Exception as e:
            self._log_operation("read_file", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to read file {file_path}: {e}") from e

    def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> str:
        """Write content to a file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)

            self._log_operation("write_file", {"file_path": file_path, "size": len(content)})
            return f"Successfully wrote {len(content)} characters to {file_path}"

        except Exception as e:
            self._log_operation("write_file", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to write file {file_path}: {e}") from e

    def append_file(self, file_path: str, content: str, encoding: str = "utf-8") -> str:
        """Append content to a file"""
        try:
            with open(file_path, "a", encoding=encoding) as f:
                f.write(content)

            self._log_operation("append_file", {"file_path": file_path, "size": len(content)})
            return f"Successfully appended {len(content)} characters to {file_path}"

        except Exception as e:
            self._log_operation("append_file", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to append to file {file_path}: {e}") from e

    def list_files(self, directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """List files in a directory"""
        try:
            path_obj = pathlib.Path(directory)

            if recursive:
                files = list(path_obj.rglob(pattern))
            else:
                files = list(path_obj.glob(pattern))

            file_list = [str(f) for f in files if f.is_file()]

            self._log_operation(
                "list_files", {"directory": directory, "pattern": pattern, "count": len(file_list)}
            )

            return file_list

        except Exception as e:
            self._log_operation("list_files", {"directory": directory, "error": str(e)})
            raise Exception(f"Failed to list files in {directory}: {e}") from e

    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists"""
        exists = os.path.exists(file_path)
        self._log_operation("file_exists", {"file_path": file_path, "exists": exists})
        return exists

    def create_directory(self, directory_path: str) -> str:
        """Create a directory"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            self._log_operation("create_directory", {"directory_path": directory_path})
            return f"Directory created: {directory_path}"

        except Exception as e:
            self._log_operation(
                "create_directory", {"directory_path": directory_path, "error": str(e)}
            )
            raise Exception(f"Failed to create directory {directory_path}: {e}") from e

    def delete_file(self, file_path: str) -> str:
        """Delete a file"""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                self._log_operation("delete_file", {"file_path": file_path, "type": "file"})
                return f"File deleted: {file_path}"
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                self._log_operation("delete_file", {"file_path": file_path, "type": "directory"})
                return f"Directory deleted: {file_path}"
            else:
                return f"Path not found: {file_path}"

        except Exception as e:
            self._log_operation("delete_file", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to delete {file_path}: {e}") from e

    def copy_file(self, source: str, destination: str) -> str:
        """Copy a file"""
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            shutil.copy2(source, destination)
            self._log_operation("copy_file", {"source": source, "destination": destination})
            return f"File copied from {source} to {destination}"

        except Exception as e:
            self._log_operation(
                "copy_file", {"source": source, "destination": destination, "error": str(e)}
            )
            raise Exception(f"Failed to copy file from {source} to {destination}: {e}") from e

    def move_file(self, source: str, destination: str) -> str:
        """Move a file"""
        try:
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)

            shutil.move(source, destination)
            self._log_operation("move_file", {"source": source, "destination": destination})
            return f"File moved from {source} to {destination}"

        except Exception as e:
            self._log_operation(
                "move_file", {"source": source, "destination": destination, "error": str(e)}
            )
            raise Exception(f"Failed to move file from {source} to {destination}: {e}") from e

    def file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file"""
        try:
            stat = os.stat(file_path)

            info = {
                "path": file_path,
                "exists": True,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path),
                "permissions": oct(stat.st_mode)[-3:],
                "extension": pathlib.Path(file_path).suffix,
            }

            self._log_operation("file_info", {"file_path": file_path})
            return info

        except Exception as e:
            self._log_operation("file_info", {"file_path": file_path, "error": str(e)})
            return {"path": file_path, "exists": False, "error": str(e)}

    def search_files(
        self, directory: str, search_term: str, file_pattern: str = "*.txt"
    ) -> List[Dict[str, Any]]:
        """Search for text within files"""
        try:
            results = []
            files = self.list_files(directory, file_pattern, recursive=True)

            for file_path in files:
                try:
                    content = self.read_file(file_path)
                    if search_term.lower() in content.lower():
                        # Find line numbers
                        lines = content.split("\n")
                        matching_lines = []

                        for i, line in enumerate(lines, 1):
                            if search_term.lower() in line.lower():
                                matching_lines.append({"line_number": i, "content": line.strip()})

                        results.append(
                            {
                                "file": file_path,
                                "matches": len(matching_lines),
                                "lines": matching_lines[:10],  # Limit to first 10 matches
                            }
                        )

                except Exception:
                    # Skip files that can't be read
                    continue

            self._log_operation(
                "search_files",
                {"directory": directory, "search_term": search_term, "results": len(results)},
            )

            return results

        except Exception as e:
            self._log_operation("search_files", {"directory": directory, "error": str(e)})
            raise Exception(f"Failed to search files in {directory}: {e}") from e

    def calculate_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """Calculate hash of a file"""
        try:
            if algorithm.lower() == "md5":
                hasher = hashlib.md5()
            elif algorithm.lower() == "sha256":
                hasher = hashlib.sha256()
            elif algorithm.lower() == "sha1":
                hasher = hashlib.sha1()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")

            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)

            hash_value = hasher.hexdigest()
            self._log_operation("calculate_hash", {"file_path": file_path, "algorithm": algorithm})
            return hash_value

        except Exception as e:
            self._log_operation("calculate_hash", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to calculate hash for {file_path}: {e}") from e

    # Data Format Operations
    def read_json(self, file_path: str) -> Any:
        """Read JSON data from a file"""
        try:
            content = self.read_file(file_path)
            data = json.loads(content)
            self._log_operation("read_json", {"file_path": file_path})
            return data

        except Exception as e:
            self._log_operation("read_json", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to read JSON from {file_path}: {e}") from e

    def write_json(self, file_path: str, data: Any, indent: int = 2) -> str:
        """Write data to a JSON file"""
        try:
            json_content = json.dumps(data, indent=indent, default=str)
            result = self.write_file(file_path, json_content)
            self._log_operation("write_json", {"file_path": file_path})
            return result

        except Exception as e:
            self._log_operation("write_json", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to write JSON to {file_path}: {e}") from e

    def read_csv(self, file_path: str, delimiter: str = ",") -> List[Dict[str, str]]:
        """Read CSV data from a file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                data = list(reader)

            self._log_operation("read_csv", {"file_path": file_path, "rows": len(data)})
            return data

        except Exception as e:
            self._log_operation("read_csv", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to read CSV from {file_path}: {e}") from e

    def write_csv(self, file_path: str, data: List[Dict[str, Any]], delimiter: str = ",") -> str:
        """Write data to a CSV file"""
        try:
            if not data:
                return "No data to write"

            fieldnames = list(data[0].keys())

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)

            self._log_operation("write_csv", {"file_path": file_path, "rows": len(data)})
            return f"Successfully wrote {len(data)} rows to {file_path}"

        except Exception as e:
            self._log_operation("write_csv", {"file_path": file_path, "error": str(e)})
            raise Exception(f"Failed to write CSV to {file_path}: {e}") from e

    # Archive Operations
    def compress_files(self, file_paths: List[str], archive_path: str) -> str:
        """Compress files into a ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        # Use relative path in archive
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)

            self._log_operation(
                "compress_files", {"file_count": len(file_paths), "archive_path": archive_path}
            )
            return f"Compressed {len(file_paths)} files to {archive_path}"

        except Exception as e:
            self._log_operation("compress_files", {"archive_path": archive_path, "error": str(e)})
            raise Exception(f"Failed to compress files to {archive_path}: {e}") from e

    def extract_archive(self, archive_path: str, extract_to: str) -> str:
        """Extract files from a ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path, "r") as zipf:
                zipf.extractall(extract_to)
                file_count = len(zipf.namelist())

            self._log_operation(
                "extract_archive",
                {"archive_path": archive_path, "extract_to": extract_to, "file_count": file_count},
            )
            return f"Extracted {file_count} files to {extract_to}"

        except Exception as e:
            self._log_operation("extract_archive", {"archive_path": archive_path, "error": str(e)})
            raise Exception(f"Failed to extract archive {archive_path}: {e}") from e

    # Data Processing Operations
    def parse_text(self, text: str, pattern: str) -> List[str]:
        """Parse text using regular expressions"""
        try:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            self._log_operation("parse_text", {"pattern": pattern, "matches": len(matches)})
            return matches

        except Exception as e:
            self._log_operation("parse_text", {"pattern": pattern, "error": str(e)})
            raise Exception(f"Failed to parse text with pattern {pattern}: {e}") from e

    def format_data(self, data: Any, format_type: str) -> str:
        """Format data in various formats"""
        try:
            if format_type.lower() == "json":
                return json.dumps(data, indent=2, default=str)
            elif format_type.lower() == "table":
                return self._format_as_table(data)
            elif format_type.lower() == "csv":
                return self._format_as_csv(data)
            else:
                return str(data)

        except Exception as e:
            raise Exception(f"Failed to format data as {format_type}: {e}") from e

    def validate_data(self, data: Any, validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against rules"""
        try:
            results = {"valid": True, "errors": [], "warnings": []}

            # Basic validation rules
            if "required_fields" in validation_rules and isinstance(data, dict):
                for field in validation_rules["required_fields"]:
                    if field not in data:
                        results["errors"].append(f"Missing required field: {field}")
                        results["valid"] = False

            if "max_length" in validation_rules and isinstance(data, str):
                if len(data) > validation_rules["max_length"]:
                    results["errors"].append(
                        f"String too long: {len(data)} > {validation_rules['max_length']}"
                    )
                    results["valid"] = False

            self._log_operation("validate_data", {"valid": results["valid"]})
            return results

        except Exception as e:
            self._log_operation("validate_data", {"error": str(e)})
            raise Exception(f"Failed to validate data: {e}") from e

    def transform_data(self, data: Any, transformation: str, **kwargs) -> Any:
        """Transform data using various methods"""
        try:
            if transformation == "uppercase" and isinstance(data, str):
                return data.upper()
            elif transformation == "lowercase" and isinstance(data, str):
                return data.lower()
            elif transformation == "reverse" and isinstance(data, (str, list)):
                return data[::-1]
            elif transformation == "sort" and isinstance(data, list):
                return sorted(data, key=kwargs.get("key"))
            elif transformation == "unique" and isinstance(data, list):
                return list(set(data))
            else:
                return data

        except Exception as e:
            raise Exception(f"Failed to transform data: {e}") from e

    def filter_data(self, data: List[Any], filter_func: str, value: Any = None) -> List[Any]:
        """Filter data using various criteria"""
        try:
            if filter_func == "contains" and value:
                return [item for item in data if str(value) in str(item)]
            elif filter_func == "startswith" and value:
                return [item for item in data if str(item).startswith(str(value))]
            elif filter_func == "endswith" and value:
                return [item for item in data if str(item).endswith(str(value))]
            elif filter_func == "not_empty":
                return [item for item in data if item]
            else:
                return data

        except Exception as e:
            raise Exception(f"Failed to filter data: {e}") from e

    def sort_data(
        self, data: List[Any], key: Optional[str] = None, reverse: bool = False
    ) -> List[Any]:
        """Sort data"""
        try:
            if key and isinstance(data[0], dict):
                return sorted(data, key=lambda x: x.get(key, ""), reverse=reverse)
            else:
                return sorted(data, reverse=reverse)

        except Exception as e:
            raise Exception(f"Failed to sort data: {e}") from e

    def merge_data(self, data1: Any, data2: Any) -> Any:
        """Merge two data structures"""
        try:
            if isinstance(data1, dict) and isinstance(data2, dict):
                merged = data1.copy()
                merged.update(data2)
                return merged
            elif isinstance(data1, list) and isinstance(data2, list):
                return data1 + data2
            else:
                return [data1, data2]

        except Exception as e:
            raise Exception(f"Failed to merge data: {e}") from e

    # Encoding/Decoding Operations
    def encode_data(self, data: str, encoding: str = "base64") -> str:
        """Encode data using various methods"""
        try:
            if encoding.lower() == "base64":
                return base64.b64encode(data.encode("utf-8")).decode("utf-8")
            elif encoding.lower() == "url":
                return urllib.parse.quote(data)
            else:
                return data

        except Exception as e:
            raise Exception(f"Failed to encode data: {e}") from e

    def decode_data(self, data: str, encoding: str = "base64") -> str:
        """Decode data using various methods"""
        try:
            if encoding.lower() == "base64":
                return base64.b64decode(data.encode("utf-8")).decode("utf-8")
            elif encoding.lower() == "url":
                return urllib.parse.unquote(data)
            else:
                return data

        except Exception as e:
            raise Exception(f"Failed to decode data: {e}") from e

    def status(self) -> Dict[str, Any]:
        """Get current coretools status"""
        return {
            "name": self.name,
            "description": self.description,
            "available_actions": self.available_actions,
            "temp_directory": self.temp_dir,
            "operations_performed": len(self.operation_history),
            "recent_operations": self.operation_history[-5:] if self.operation_history else [],
        }

    # Private helper methods
    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """Log an operation for tracking"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
        }

        self.operation_history.append(log_entry)

        # Keep history manageable
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-500:]

    def _format_as_table(self, data: Any) -> str:
        """Format data as a simple table"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Table from list of dicts
            headers = list(data[0].keys())
            lines = [" | ".join(headers)]
            lines.append("-" * len(lines[0]))

            for row in data:
                values = [str(row.get(header, "")) for header in headers]
                lines.append(" | ".join(values))

            return "\n".join(lines)
        else:
            return str(data)

    def _format_as_csv(self, data: Any) -> str:
        """Format data as CSV"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        else:
            return str(data)


# Plugin registration
PLUGIN_CLASS = CoreToolsPlugin
