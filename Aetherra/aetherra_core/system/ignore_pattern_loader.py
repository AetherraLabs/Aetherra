"""
Ignore Pattern Loader - Parse and apply .aetherraignore patterns.

Loads and processes .aetherraignore files (similar to .gitignore) to exclude
directories and files from self-incorporation analysis.

Supports:
  - Glob patterns (*.py, tests/**/*, etc.)
  - Regular expressions
  - Negation patterns (!)
  - Comments (#)
  - Directory-specific patterns

File format:
    # Comment
    build/              # Exclude build directory
    *.egg-info/
    __pycache__/
    archive/            # Exclude archive
    !archive_important/ # BUT include this directory
    temp*               # Exclude any file starting with 'temp'

Example:
    >>> loader = IgnorePatternLoader("/path/to/workspace")
    >>> patterns = loader.load()
    >>> should_skip = loader.should_ignore("build/output.o")
"""

import fnmatch
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class IgnorePattern:
    """A single ignore pattern with metadata."""

    pattern: str
    """Pattern string (glob or regex)"""
    is_negation: bool = False
    """Whether this is a negation pattern (!)"""
    is_directory: bool = False
    """Whether this pattern matches directories only"""
    is_regex: bool = False
    """Whether pattern is regex (vs glob)"""
    line_number: int = 0
    """Line number in .aetherraignore file"""
    source: str = ""
    """Source file path"""

    def matches(self, path: str) -> bool:
        """
        Check if pattern matches path.

        Args:
            path: File or directory path to check

        Returns:
            True if pattern matches
        """
        try:
            if self.is_regex:
                return re.match(self.pattern, path) is not None
            else:
                return fnmatch.fnmatch(path, self.pattern)
        except Exception as e:
            logger.warning(f"Pattern matching error: {e}")
            return False

    def __str__(self) -> str:
        """Return string representation."""
        neg = "!" if self.is_negation else ""
        return f"{neg}{self.pattern}"


class IgnorePatternLoader:
    """Load and apply .aetherraignore patterns."""

    # Default patterns (always applied)
    DEFAULT_IGNORE_PATTERNS = [
        # Build artifacts
        "build/",
        "dist/",
        "*.egg-info/",
        "*.egg/",
        "*.whl",
        "target/",
        "*.o",
        "*.a",
        "*.lib",
        # Package managers
        "node_modules/",
        ".pip-cache/",
        "vendor/",
        # Development
        ".git/",
        ".gitignore",
        ".venv/",
        "venv/",
        ".env",
        ".env.local",
        ".editorconfig",
        ".DS_Store",
        "Thumbs.db",
        # Python
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache/",
        ".coverage",
        "htmlcov/",
        ".mypy_cache/",
        ".tox/",
        # IDE
        ".vscode/",
        ".idea/",
        ".vs/",
        "*.swp",
        "*.swo",
        "*~",
        # Testing
        ".pytest_cache/",
        "test_*.py",
        "*_test.py",
        # Temporary
        "tmp/",
        "temp/",
        "*.tmp",
        ".backup/",
    ]

    def __init__(
        self,
        root_dir: str,
        ignore_file: str = ".aetherraignore",
        use_defaults: bool = True,
    ):
        """
        Initialize pattern loader.

        Args:
            root_dir: Root directory to scan for .aetherraignore
            ignore_file: Name of ignore file to look for
            use_defaults: Whether to include default ignore patterns
        """
        self.root_dir = Path(root_dir)
        self.ignore_file = ignore_file
        self.use_defaults = use_defaults
        self.patterns: List[IgnorePattern] = []
        self.negation_patterns: List[IgnorePattern] = []
        self.ignore_file_path: Optional[Path] = None
        logger.debug(
            f"IgnorePatternLoader initialized: root={root_dir}, use_defaults={use_defaults}"
        )

    def load(self) -> Tuple[bool, Set[str]]:
        """
        Load ignore patterns from file and defaults.

        Searches for .aetherraignore in:
          1. Specified root_dir
          2. Parent directories (up to 5 levels)
          3. Environment variable AETHERRA_IGNORE_FILE

        Returns:
            Tuple of (success, pattern_set)
        """
        try:
            # Add default patterns if enabled
            if self.use_defaults:
                self._add_default_patterns()

            # Find and load .aetherraignore file
            ignore_path = self._find_ignore_file()
            if ignore_path:
                self._load_from_file(str(ignore_path))
                self.ignore_file_path = ignore_path
                logger.info(f"Loaded patterns from: {ignore_path}")
            else:
                logger.debug("No .aetherraignore file found, using defaults only")

            # Separate negation patterns
            self._process_patterns()

            pattern_set = {str(p.pattern) for p in self.patterns if not p.is_negation}
            logger.info(
                f"Loaded {len(pattern_set)} patterns, {len(self.negation_patterns)} negations"
            )

            return True, pattern_set

        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
            return False, set()

    def _find_ignore_file(self) -> Optional[Path]:
        """
        Find .aetherraignore file in root or parent directories.

        Search order:
          1. {root_dir}/.aetherraignore
          2. Parent directories (up to 5 levels)
          3. Environment variable AETHERRA_IGNORE_FILE

        Returns:
            Path to .aetherraignore or None
        """
        # Check root directory
        ignore_path = self.root_dir / self.ignore_file
        if ignore_path.exists():
            return ignore_path

        # Check parent directories (up to 5 levels)
        current = self.root_dir.parent
        for _ in range(5):
            ignore_path = current / self.ignore_file
            if ignore_path.exists():
                return ignore_path
            current = current.parent

        # Check environment variable
        env_path = os.getenv("AETHERRA_IGNORE_FILE")
        if env_path and Path(env_path).exists():
            return Path(env_path)

        return None

    def _add_default_patterns(self):
        """Add default ignore patterns."""
        for pattern_str in self.DEFAULT_IGNORE_PATTERNS:
            pattern = IgnorePattern(
                pattern=pattern_str,
                is_directory=pattern_str.endswith("/"),
                source="<defaults>",
            )
            self.patterns.append(pattern)

    def _load_from_file(self, file_path: str):
        """
        Load patterns from .aetherraignore file.

        Args:
            file_path: Path to .aetherraignore file
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                # Remove comments and whitespace
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse pattern
                pattern = self._parse_pattern_line(line, line_num, file_path)
                if pattern:
                    self.patterns.append(pattern)

        except Exception as e:
            logger.error(f"Error reading .aetherraignore: {e}")

    def _parse_pattern_line(
        self,
        line: str,
        line_num: int,
        source: str,
    ) -> Optional[IgnorePattern]:
        """
        Parse single pattern line.

        Args:
            line: Pattern line from file
            line_num: Line number
            source: Source file path

        Returns:
            IgnorePattern object or None
        """
        # Handle negation patterns
        is_negation = False
        if line.startswith("!"):
            is_negation = True
            line = line[1:].strip()

        # Handle directory-specific patterns
        is_directory = False
        if line.endswith("/"):
            is_directory = True

        # Detect regex patterns (start/end with /)
        is_regex = False
        if line.startswith("/") and line.endswith("/"):
            is_regex = True
            line = line[1:-1]  # Remove delimiters

        # Normalize path separators
        pattern_str = self._normalize_pattern(line)

        if not pattern_str:
            return None

        return IgnorePattern(
            pattern=pattern_str,
            is_negation=is_negation,
            is_directory=is_directory,
            is_regex=is_regex,
            line_number=line_num,
            source=source,
        )

    def _normalize_pattern(self, pattern: str) -> str:
        """
        Normalize pattern for matching.

        Args:
            pattern: Raw pattern string

        Returns:
            Normalized pattern
        """
        if not pattern:
            return ""

        # Normalize path separators (convert to forward slash)
        pattern = pattern.replace("\\", "/")

        # Handle leading slashes (anchor to root)
        if pattern.startswith("/"):
            pattern = pattern[1:]

        # Expand ** for recursive matching
        if "**" in pattern:
            # Convert ** to match any depth
            pattern = pattern.replace("**", "*")

        return pattern

    def _process_patterns(self):
        """Separate negation patterns."""
        self.negation_patterns = [p for p in self.patterns if p.is_negation]

    def should_ignore(self, file_path: str) -> bool:
        """
        Check if file path should be ignored.

        Algorithm:
          1. Normalize path
          2. Check against patterns
          3. Check negation patterns last
          4. Negation patterns override ignore patterns

        Args:
            file_path: Path to check (relative to root)

        Returns:
            True if file should be ignored
        """
        # Normalize path
        normalized_path = Path(file_path).as_posix()

        # Check against ignore patterns
        is_ignored = False
        for pattern in self.patterns:
            if pattern.is_negation:
                continue  # Skip negations for now

            if pattern.is_directory:
                # Directory pattern: check if path is under directory
                # Remove trailing slash for comparison
                dir_pattern = pattern.pattern.rstrip("/")
                if normalized_path == dir_pattern or normalized_path.startswith(dir_pattern + "/"):
                    is_ignored = True
                    break
            else:
                # Regular glob pattern: check full path
                if pattern.matches(normalized_path):
                    is_ignored = True
                    break

        # Check negation patterns (override ignore) - check all negation patterns
        if is_ignored:
            for neg_pattern in self.negation_patterns:
                if neg_pattern.matches(normalized_path):
                    is_ignored = False
                    break

        return is_ignored

    def should_ignore_directory(self, dir_path: str) -> bool:
        """
        Check if entire directory should be ignored.

        Useful for skipping directory traversal in scans.

        Args:
            dir_path: Directory path (relative to root)

        Returns:
            True if directory should be skipped
        """
        # Ensure trailing slash for directory pattern matching
        normalized = Path(dir_path).as_posix()
        if not normalized.endswith("/"):
            normalized += "/"

        return self.should_ignore(normalized)

    def get_ignored_paths(self, start_path: Optional[str] = None) -> Set[str]:
        """
        Get all ignored paths within workspace.

        Args:
            start_path: Starting path for scan

        Returns:
            Set of ignored file paths
        """
        ignored = set()
        start = Path(start_path) if start_path else self.root_dir

        if not start.exists():
            return ignored

        for path in start.rglob("*"):
            rel_path = path.relative_to(self.root_dir).as_posix()
            if self.should_ignore(rel_path):
                ignored.add(rel_path)

        return ignored

    def list_patterns(self, include_negations: bool = True) -> List[str]:
        """
        List all loaded patterns.

        Args:
            include_negations: Whether to include negation patterns

        Returns:
            List of pattern strings
        """
        patterns = [str(p) for p in self.patterns]
        if not include_negations:
            patterns = [p for p in patterns if not p.startswith("!")]
        return patterns

    def get_pattern_info(self) -> dict:
        """
        Get information about loaded patterns.

        Returns:
            Dictionary with pattern statistics
        """
        return {
            "total_patterns": len(self.patterns),
            "ignore_patterns": len([p for p in self.patterns if not p.is_negation]),
            "negation_patterns": len(self.negation_patterns),
            "directory_patterns": len([p for p in self.patterns if p.is_directory]),
            "regex_patterns": len([p for p in self.patterns if p.is_regex]),
            "ignore_file_path": str(self.ignore_file_path) if self.ignore_file_path else None,
        }
