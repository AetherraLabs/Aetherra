"""
Plugin Processors - JSON, CSV, and Text data processing implementations.

Provides three concrete processors that handle common data formats:
  - JSONProcessor: Parse, validate, transform, and export JSON
  - CSVProcessor: Parse, type-detect, filter, sort, and export CSV
  - TextProcessor: Process text lines with regex and statistics

All processors extend ProcessorBase which defines the common interface.

Example:
    >>> proc = JSONProcessor()
    >>> data = proc.parse('{"name": "Alice", "age": 30}')
    >>> filtered = proc.filter(data, lambda r: r.get("age", 0) > 18)
    >>> output = proc.export(filtered, "json")
"""

import csv
import io
import json
import re
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProcessConfig:
    """Configuration for a processing operation."""

    delimiter: str = ","
    """CSV delimiter character"""
    encoding: str = "utf-8"
    """Text encoding"""
    schema: Optional[Dict] = None
    """JSON schema for validation"""
    filters: List[str] = field(default_factory=list)
    """Filter expressions"""
    sort_by: Optional[str] = None
    """Column to sort by"""
    sort_ascending: bool = True
    """Sort direction"""
    max_rows: int = 0
    """Maximum rows (0 = unlimited)"""
    regex_pattern: Optional[str] = None
    """Regex pattern for text operations"""
    regex_replacement: Optional[str] = None
    """Replacement string for regex substitution"""


@dataclass
class ProcessResult:
    """Result of a processing operation."""

    success: bool
    """Whether processing succeeded"""
    data: Any = None
    """Processed data"""
    error: Optional[str] = None
    """Error message if failed"""
    stats: Dict[str, Any] = field(default_factory=dict)
    """Processing statistics"""
    warnings: List[str] = field(default_factory=list)
    """Non-fatal warnings"""


class ProcessorBase(ABC):
    """Abstract base class for all processors."""

    @abstractmethod
    def parse(self, input_data: Any) -> Any:
        """Parse raw input into structured data."""
        raise NotImplementedError

    @abstractmethod
    def process(self, data: Any, config: ProcessConfig) -> Any:
        """Apply processing operations to parsed data."""
        raise NotImplementedError

    @abstractmethod
    def export(self, data: Any, format: str) -> str:
        """Export processed data to string format."""
        raise NotImplementedError

    def run(
        self,
        input_data: Any,
        config: Optional[ProcessConfig] = None,
        output_format: str = "json",
    ) -> ProcessResult:
        """
        Run full pipeline: parse → process → export.

        Args:
            input_data: Raw input to process
            config: Processing configuration
            output_format: Output format string

        Returns:
            ProcessResult with data and stats
        """
        config = config or ProcessConfig()
        try:
            parsed = self.parse(input_data)
            processed = self.process(parsed, config)
            return ProcessResult(success=True, data=processed)
        except Exception as e:
            return ProcessResult(success=False, error=str(e))


# ---------------------------------------------------------------------------
# JSON Processor
# ---------------------------------------------------------------------------


class JSONProcessor(ProcessorBase):
    """Process JSON data with validation, transform, and filter support."""

    def parse(self, input_data: str) -> dict | list:
        """
        Parse JSON string into Python objects.

        Args:
            input_data: JSON string or already-parsed dict/list

        Returns:
            Parsed Python object (dict or list)

        Raises:
            ValueError: If JSON is invalid
        """
        if isinstance(input_data, (dict, list)):
            return input_data
        if not isinstance(input_data, str):
            raise ValueError(f"Expected str or dict/list, got {type(input_data).__name__}")
        try:
            return json.loads(input_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e

    def process(self, data: Any, config: ProcessConfig) -> Any:
        """
        Apply transform and filter operations.

        Args:
            data: Parsed JSON data
            config: Processing configuration

        Returns:
            Processed data
        """
        result = data

        # Apply schema validation if provided
        if config.schema:
            errors = self.validate_schema(result, config.schema)
            if errors:
                raise ValueError(f"Schema validation failed: {errors}")

        # Filter list items based on filters
        if config.filters and isinstance(result, list):
            result = self._apply_filters(result, config.filters)

        # Apply row limit
        if config.max_rows and isinstance(result, list):
            result = result[: config.max_rows]

        return result

    def export(self, data: Any, format: str = "json") -> str:
        """
        Export data as JSON string.

        Args:
            data: Data to export
            format: Must be 'json' (only format supported)

        Returns:
            JSON string
        """
        if format not in ("json", "pretty"):
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'pretty'")
        indent = 2 if format == "pretty" else None
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def validate_schema(self, data: Any, schema: Dict) -> List[str]:
        """
        Validate data against a simple JSON schema.

        Args:
            data: Data to validate
            schema: Schema dict with 'required', 'properties', 'type'

        Returns:
            List of validation errors (empty = valid)
        """
        errors: List[str] = []

        if "type" in schema:
            expected_type = schema["type"]
            type_map = {
                "object": dict,
                "array": list,
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "null": type(None),
            }
            expected = type_map.get(expected_type)
            if expected and not isinstance(data, expected):
                errors.append(f"Expected type {expected_type}, got {type(data).__name__}")

        if "required" in schema:
            items_to_check = data if isinstance(data, list) else [data]
            for item in items_to_check:
                if isinstance(item, dict):
                    for field_name in schema["required"]:
                        if field_name not in item:
                            errors.append(f"Missing required field: {field_name}")

        if "properties" in schema and isinstance(data, dict):
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in data:
                    prop_errors = self.validate_schema(data[prop_name], prop_schema)
                    errors.extend([f"{prop_name}: {e}" for e in prop_errors])

        return errors

    def filter(self, data: list, predicate) -> list:
        """
        Filter list data using a callable predicate.

        Args:
            data: List to filter
            predicate: Callable that returns True to keep item

        Returns:
            Filtered list
        """
        if not isinstance(data, list):
            raise ValueError("filter() requires a list")
        return [item for item in data if predicate(item)]

    def transform(self, data: Any, transform_fn) -> Any:
        """
        Apply a transform function to data.

        Args:
            data: Data to transform (list or dict)
            transform_fn: Function to apply to each item

        Returns:
            Transformed data
        """
        if isinstance(data, list):
            return [transform_fn(item) for item in data]
        return transform_fn(data)

    def _apply_filters(self, data: list, filters: List[str]) -> list:
        """Apply string filter expressions to list data."""
        result = data
        for f in filters:
            # Simple key=value filter
            if "=" in f:
                key, value = f.split("=", 1)
                key = key.strip()
                value = value.strip()
                result = [
                    item
                    for item in result
                    if isinstance(item, dict) and str(item.get(key, "")) == value
                ]
        return result


# ---------------------------------------------------------------------------
# CSV Processor
# ---------------------------------------------------------------------------


class CSVProcessor(ProcessorBase):
    """Process CSV data with type detection, filtering, sorting."""

    # Type detection patterns
    _INT_PATTERN = re.compile(r"^-?\d+$")
    _FLOAT_PATTERN = re.compile(r"^-?\d+\.\d+$")
    _BOOL_PATTERN = re.compile(r"^(true|false|yes|no|1|0)$", re.IGNORECASE)
    _DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def parse(self, input_data: str, delimiter: str = ",") -> List[Dict[str, Any]]:
        """
        Parse CSV string into list of row dicts.

        Args:
            input_data: CSV string content
            delimiter: Column delimiter character

        Returns:
            List of row dictionaries with type-detected values
        """
        if not isinstance(input_data, str):
            raise ValueError(f"Expected str, got {type(input_data).__name__}")

        reader = csv.DictReader(io.StringIO(input_data), delimiter=delimiter)
        rows = []
        for row in reader:
            typed_row = {k: self._detect_type(v) for k, v in row.items()}
            rows.append(typed_row)
        return rows

    def process(self, data: List[Dict], config: ProcessConfig) -> List[Dict]:
        """
        Apply filter and sort operations to CSV rows.

        Args:
            data: List of row dicts
            config: Processing configuration with filters and sort

        Returns:
            Processed list of rows
        """
        result = data

        # Apply filters
        if config.filters:
            result = self._apply_filters(result, config.filters)

        # Apply sort
        if config.sort_by:
            result = self._sort_rows(result, config.sort_by, config.sort_ascending)

        # Apply row limit
        if config.max_rows:
            result = result[: config.max_rows]

        return result

    def export(self, data: List[Dict], format: str = "csv") -> str:
        """
        Export rows to CSV or JSON string.

        Args:
            data: List of row dicts
            format: 'csv' or 'json'

        Returns:
            String in requested format
        """
        if format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)

        if format != "csv":
            raise ValueError(f"Unsupported format: {format}. Use 'csv' or 'json'")

        if not data:
            return ""

        output = io.StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def get_column_types(self, data: List[Dict]) -> Dict[str, str]:
        """
        Infer column types from all rows.

        Args:
            data: List of row dicts

        Returns:
            Dict of column_name -> detected_type
        """
        if not data:
            return {}

        types: Dict[str, set] = {}
        for row in data:
            for col, val in row.items():
                if col not in types:
                    types[col] = set()
                types[col].add(type(val).__name__)

        type_name_map = {
            "int": "int",
            "float": "float",
            "bool": "bool",
            "str": "string",
            "NoneType": "null",
        }

        return {
            col: type_name_map.get(next(iter(type_set)), next(iter(type_set)))
            if len(type_set) == 1
            else "mixed"
            for col, type_set in types.items()
        }

    def get_stats(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Compute statistics for numeric columns.

        Args:
            data: List of row dicts

        Returns:
            Stats dict with min, max, mean per numeric column
        """
        if not data:
            return {}

        stats: Dict[str, Any] = {
            "row_count": len(data),
            "column_count": len(data[0]),
            "columns": {},
        }

        # Per-column numeric statistics
        columns = data[0].keys()
        for col in columns:
            values = [row[col] for row in data if isinstance(row[col], (int, float))]
            if values:
                stats["columns"][col] = {
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "count": len(values),
                }

        return stats

    def _detect_type(self, value: str) -> Any:
        """Detect and convert type of a string value."""
        if value is None or value == "":
            return None
        if self._INT_PATTERN.match(value):
            return int(value)
        if self._FLOAT_PATTERN.match(value):
            return float(value)
        if self._BOOL_PATTERN.match(value):
            return value.lower() in ("true", "yes", "1")
        return value

    def _apply_filters(self, data: List[Dict], filters: List[str]) -> List[Dict]:
        """Apply filter expressions to CSV rows."""
        result = data
        for f in filters:
            if "=" in f:
                key, value = f.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Try type coercion for numeric comparisons
                try:
                    num_value = float(value)
                    result = [
                        r for r in result if r.get(key) == num_value or str(r.get(key, "")) == value
                    ]
                except ValueError:
                    result = [r for r in result if str(r.get(key, "")) == value]
            elif ">" in f:
                key, value = f.split(">", 1)
                try:
                    threshold = float(value.strip())
                    result = [
                        r
                        for r in result
                        if isinstance(r.get(key.strip()), (int, float))
                        and r[key.strip()] > threshold
                    ]
                except ValueError:
                    pass
            elif "<" in f:
                key, value = f.split("<", 1)
                try:
                    threshold = float(value.strip())
                    result = [
                        r
                        for r in result
                        if isinstance(r.get(key.strip()), (int, float))
                        and r[key.strip()] < threshold
                    ]
                except ValueError:
                    pass
        return result

    def _sort_rows(self, data: List[Dict], sort_by: str, ascending: bool) -> List[Dict]:
        """Sort rows by a column."""
        try:
            return sorted(
                data,
                key=lambda r: (r.get(sort_by) is None, r.get(sort_by, "")),
                reverse=not ascending,
            )
        except TypeError:
            return data


# ---------------------------------------------------------------------------
# Text Processor
# ---------------------------------------------------------------------------


class TextProcessor(ProcessorBase):
    """Process text data with line operations, regex, and statistics."""

    def parse(self, input_data: str) -> List[str]:
        """
        Parse text into list of lines.

        Args:
            input_data: Raw text string

        Returns:
            List of non-empty lines
        """
        if not isinstance(input_data, str):
            raise ValueError(f"Expected str, got {type(input_data).__name__}")
        return input_data.splitlines()

    def process(self, data: List[str], config: ProcessConfig) -> List[str]:
        """
        Apply filter and transform operations to lines.

        Args:
            data: List of text lines
            config: Processing configuration

        Returns:
            Processed list of lines
        """
        result = data

        # Apply regex filter
        if config.regex_pattern:
            pattern = re.compile(config.regex_pattern)
            if config.regex_replacement is not None:
                result = [pattern.sub(config.regex_replacement, line) for line in result]
            else:
                result = [line for line in result if pattern.search(line)]

        # Apply string filters
        if config.filters:
            for f in config.filters:
                result = [line for line in result if f.lower() in line.lower()]

        # Apply row limit
        if config.max_rows:
            result = result[: config.max_rows]

        return result

    def export(self, data: List[str], format: str = "text") -> str:
        """
        Export lines to text or JSON string.

        Args:
            data: List of text lines
            format: 'text' or 'json'

        Returns:
            String in requested format
        """
        if format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        if format not in ("text", "lines"):
            raise ValueError(f"Unsupported format: {format}. Use 'text', 'lines', or 'json'")
        return "\n".join(data)

    def get_stats(self, data: List[str]) -> Dict[str, Any]:
        """
        Compute text statistics.

        Args:
            data: List of text lines

        Returns:
            Dict with line/word/char counts and other stats
        """
        if not data:
            return {
                "line_count": 0,
                "word_count": 0,
                "char_count": 0,
                "empty_lines": 0,
                "avg_line_length": 0.0,
            }

        all_text = "\n".join(data)
        words = all_text.split()
        empty_lines = sum(1 for line in data if not line.strip())
        line_lengths = [len(line) for line in data]

        return {
            "line_count": len(data),
            "word_count": len(words),
            "char_count": len(all_text),
            "empty_lines": empty_lines,
            "avg_line_length": (statistics.mean(line_lengths) if line_lengths else 0.0),
            "max_line_length": max(line_lengths) if line_lengths else 0,
        }

    def find_pattern(self, data: List[str], pattern: str) -> List[Dict[str, Any]]:
        """
        Find all regex matches in text lines.

        Args:
            data: List of text lines
            pattern: Regex pattern to search

        Returns:
            List of match dicts with line_number, match, and line
        """
        compiled = re.compile(pattern)
        matches = []
        for i, line in enumerate(data, 1):
            for match in compiled.finditer(line):
                matches.append(
                    {
                        "line_number": i,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "line": line,
                    }
                )
        return matches

    def replace_pattern(self, data: List[str], pattern: str, replacement: str) -> List[str]:
        """
        Replace regex pattern in all lines.

        Args:
            data: List of text lines
            pattern: Regex pattern to replace
            replacement: Replacement string

        Returns:
            Lines with replacements applied
        """
        compiled = re.compile(pattern)
        return [compiled.sub(replacement, line) for line in data]

    def filter_lines(
        self, data: List[str], contains: str, case_sensitive: bool = False
    ) -> List[str]:
        """
        Filter lines containing a substring.

        Args:
            data: List of text lines
            contains: Substring to search for
            case_sensitive: Whether to match case

        Returns:
            Filtered list of lines
        """
        if case_sensitive:
            return [line for line in data if contains in line]
        contains_lower = contains.lower()
        return [line for line in data if contains_lower in line.lower()]
