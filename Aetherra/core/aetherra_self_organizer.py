#!/usr/bin/env python3
"""
🧠 Aetherra Self-Directed File Intelligence System
Core autonomous file organization and system optimization engine.

This system provides reflexive intelligence for maintaining clean,
optimal file structure and eliminating technical debt automatically.
"""

import ast
import hashlib
import importlib.util
import json
import logging
import os
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Comprehensive metadata for each file in the system."""

    path: str
    file_type: str
    size: int
    last_modified: float
    content_hash: str
    dependencies: List[str]
    exports: List[str]
    imports: List[str]
    classes: List[str]
    functions: List[str]
    plugins: List[str]
    purpose: str
    risk_level: str
    usage_score: float
    is_orphaned: bool
    suggested_location: Optional[str]


@dataclass
class SystemAnalysis:
    """Overall system analysis results."""

    total_files: int
    orphaned_files: List[str]
    duplicate_logic: List[Tuple[str, str]]
    broken_imports: List[str]
    optimization_suggestions: List[Dict[str, Any]]
    critical_files: List[str]
    refactor_recommendations: List[Dict[str, Any]]


class AetherraFileIntelligence:
    """
    🧠 Core File Intelligence Engine

    Provides autonomous file scanning, analysis, and optimization
    for the entire Aetherra ecosystem.
    """

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.db_path = self.project_root / "file_manifest.db"
        self.live_index_path = self.project_root / "live_file_index.json"
        self.evolution_log_path = self.project_root / "evolution_history.aether"

        # File patterns to analyze
        self.target_extensions = {
            ".py",
            ".aether",
            ".json",
            ".md",
            ".yml",
            ".yaml",
            ".toml",
            ".ini",
        }
        self.critical_directories = {
            "Aetherra",
            "src",
            "plugins",
            "memory",
            "gui",
            "core",
        }

        # Initialize databases and indices
        self._init_database()
        self.file_registry: Dict[str, FileMetadata] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.plugin_mapping: Dict[str, Set[str]] = {}

    def _init_database(self):
        """Initialize the file manifest database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_manifest (
                    path TEXT PRIMARY KEY,
                    file_type TEXT,
                    size INTEGER,
                    last_modified REAL,
                    content_hash TEXT,
                    dependencies TEXT,
                    exports TEXT,
                    imports TEXT,
                    classes TEXT,
                    functions TEXT,
                    plugins TEXT,
                    purpose TEXT,
                    risk_level TEXT,
                    usage_score REAL,
                    is_orphaned BOOLEAN,
                    suggested_location TEXT,
                    scan_timestamp REAL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS evolution_log (
                    timestamp REAL,
                    action TEXT,
                    files_affected TEXT,
                    reason TEXT,
                    success BOOLEAN,
                    details TEXT
                )
            """)

    def scan_project_files(self) -> Dict[str, FileMetadata]:
        """
        📂 Recursively scan entire Aetherra project directory
        Build comprehensive file registry with metadata.
        """
        logger.info(f"🔍 Starting comprehensive project scan: {self.project_root}")

        # Skip directories that are not useful for organization
        skip_dirs = {
            "node_modules",
            ".venv",
            "venv",
            "__pycache__",
            ".git",
            "unused_conservative",
            "Unused",
            "archive",
            ".backups",
            "frontend",
            "aetherra-website",  # Skip frontend and website node_modules
        }

        files_processed = 0

        def should_skip_directory(dir_path: Path) -> bool:
            """Check if we should skip this directory entirely."""
            dir_name = dir_path.name.lower()

            # Skip by exact name
            if dir_name in skip_dirs:
                return True

            # Skip by pattern
            if (
                dir_name.startswith(
                    ("legacy_cleanup_", "aetherra_backup_", "housekeeping_")
                )
                or "backup" in dir_name
                or "unused" in dir_name
            ):
                return True

            return False

        def scan_directory(dir_path: Path):
            """Recursively scan directory, skipping unwanted ones."""
            nonlocal files_processed

            try:
                for item in dir_path.iterdir():
                    if item.is_dir():
                        if not should_skip_directory(item):
                            scan_directory(item)  # Recurse into non-skipped directories
                    elif item.is_file() and item.suffix in self.target_extensions:
                        try:
                            metadata = self._analyze_file(item)
                            self.file_registry[str(item)] = metadata
                            files_processed += 1
                            if files_processed % 100 == 0:
                                logger.info(f"📊 Processed {files_processed} files...")
                            logger.debug(f"Analyzed: {item}")
                        except Exception as e:
                            logger.warning(f"Failed to analyze {item}: {e}")
            except PermissionError:
                logger.warning(f"Permission denied accessing {dir_path}")
            except Exception as e:
                logger.warning(f"Error scanning {dir_path}: {e}")

        # Start scanning from project root
        scan_directory(self.project_root)

        # Build dependency graph
        self._build_dependency_graph()

        # Update database
        self._update_database()

        # Export live index
        self._export_live_index()

        logger.info(f"✅ Scan complete: {len(self.file_registry)} files analyzed")
        return self.file_registry

    def _analyze_file(self, file_path: Path) -> FileMetadata:
        """🧠 Deep semantic analysis of individual files."""
        stat = file_path.stat()
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Initialize metadata
        metadata = FileMetadata(
            path=str(file_path),
            file_type=file_path.suffix,
            size=stat.st_size,
            last_modified=stat.st_mtime,
            content_hash=content_hash,
            dependencies=[],
            exports=[],
            imports=[],
            classes=[],
            functions=[],
            plugins=[],
            purpose="",
            risk_level="low",
            usage_score=0.0,
            is_orphaned=False,
            suggested_location=None,
        )

        # Analyze based on file type
        if file_path.suffix == ".py":
            self._analyze_python_file(content, metadata)
        elif file_path.suffix == ".aether":
            self._analyze_aether_file(content, metadata)
        elif file_path.suffix == ".json":
            self._analyze_json_file(content, metadata)
        elif file_path.suffix == ".md":
            self._analyze_markdown_file(content, metadata)

        # Determine purpose and risk level
        self._infer_file_purpose(metadata)
        self._calculate_risk_level(metadata)

        return metadata

    def _analyze_python_file(self, content: str, metadata: FileMetadata):
        """Analyze Python files using AST parsing."""
        try:
            # Skip very large files that might cause performance issues
            if len(content) > 1_000_000:  # 1MB limit
                logger.warning(
                    f"Skipping large file {metadata.path} ({len(content)} bytes)"
                )
                metadata.risk_level = "high"
                metadata.purpose = "Large file - manual review needed"
                return

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    metadata.classes.append(node.name)
                    metadata.exports.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    metadata.functions.append(node.name)
                    metadata.exports.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata.imports.append(alias.name)
                        metadata.dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        metadata.imports.append(node.module)
                        metadata.dependencies.append(node.module)

            # Check for plugin patterns
            if any("plugin" in cls.lower() for cls in metadata.classes):
                metadata.plugins.extend(
                    [cls for cls in metadata.classes if "plugin" in cls.lower()]
                )

            # Check for Aetherra-specific patterns
            if "lyrixa" in content.lower() or "memory" in content.lower():
                metadata.purpose = "Core Aetherra component"

        except SyntaxError as e:
            logger.warning(f"Syntax error in {metadata.path}: {e}")
            metadata.risk_level = "high"
            metadata.purpose = "Syntax error - needs fixing"
        except Exception as e:
            logger.warning(f"Analysis error in {metadata.path}: {e}")
            metadata.risk_level = "medium"
            metadata.risk_level = "high"

    def _analyze_aether_file(self, content: str, metadata: FileMetadata):
        """Analyze .aether files for goals, plugins, and memory operations."""
        # Extract goals
        goal_pattern = r'goal:\s*"([^"]+)"'
        goals = re.findall(goal_pattern, content)
        metadata.exports.extend(goals)

        # Extract plugin calls
        plugin_pattern = r"plugin:\s*(\w+)\s*\("
        plugins = re.findall(plugin_pattern, content)
        metadata.plugins.extend(plugins)
        metadata.dependencies.extend(plugins)

        # Extract memory operations
        memory_pattern = r'remember\s+.*as\s+"([^"]+)"'
        memory_ops = re.findall(memory_pattern, content)
        metadata.exports.extend(memory_ops)

        metadata.purpose = "Aetherra orchestration script"

    def _analyze_json_file(self, content: str, metadata: FileMetadata):
        """Analyze JSON configuration files."""
        try:
            data = json.loads(content)

            # Handle case where JSON contains a list instead of dict
            if isinstance(data, list):
                metadata.purpose = "JSON data array"
                return

            if not isinstance(data, dict):
                metadata.purpose = "JSON data"
                return

            # Check for plugin configurations
            if "plugins" in data or "plugin" in str(data).lower():
                metadata.purpose = "Plugin configuration"
                if isinstance(data.get("plugins"), list):
                    metadata.plugins.extend(data["plugins"])

            # Check for memory configurations
            if "memory" in str(data).lower():
                metadata.purpose = "Memory configuration"

            # Extract dependencies from package.json style files
            if "dependencies" in data and isinstance(data["dependencies"], dict):
                metadata.dependencies.extend(data["dependencies"].keys())

        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in {metadata.path}")
            metadata.risk_level = "medium"

    def _analyze_markdown_file(self, content: str, metadata: FileMetadata):
        """Analyze Markdown documentation files."""
        if any(
            keyword in content.lower()
            for keyword in ["readme", "documentation", "guide"]
        ):
            metadata.purpose = "Documentation"
        elif "test" in content.lower():
            metadata.purpose = "Test documentation"
        elif "api" in content.lower():
            metadata.purpose = "API documentation"

    def _infer_file_purpose(self, metadata: FileMetadata):
        """Infer file purpose from path and content analysis."""
        path_lower = metadata.path.lower()

        if "test" in path_lower:
            metadata.purpose = "Test file"
        elif "plugin" in path_lower:
            metadata.purpose = "Plugin system"
        elif "memory" in path_lower:
            metadata.purpose = "Memory management"
        elif "gui" in path_lower or "ui" in path_lower:
            metadata.purpose = "User interface"
        elif "core" in path_lower:
            metadata.purpose = "Core system"
        elif "launcher" in path_lower:
            metadata.purpose = "Application launcher"
        elif "demo" in path_lower:
            metadata.purpose = "Demonstration code"
        elif not metadata.purpose:
            metadata.purpose = "Utility module"

    def _calculate_risk_level(self, metadata: FileMetadata):
        """Calculate risk level based on various factors."""
        risk_factors = 0

        # Check for potential issues
        if not metadata.dependencies and metadata.file_type == ".py":
            risk_factors += 1  # Isolated files might be orphaned

        if (
            len(metadata.classes) == 0
            and len(metadata.functions) == 0
            and metadata.file_type == ".py"
        ):
            risk_factors += 2  # Empty or broken Python files

        if "deprecated" in metadata.path.lower() or "old" in metadata.path.lower():
            risk_factors += 3  # Explicitly deprecated

        if metadata.size == 0:
            risk_factors += 2  # Empty files

        # Assign risk level
        if risk_factors >= 4:
            metadata.risk_level = "high"
        elif risk_factors >= 2:
            metadata.risk_level = "medium"
        else:
            metadata.risk_level = "low"

    def _build_dependency_graph(self):
        """Build comprehensive dependency graph."""
        for file_path, metadata in self.file_registry.items():
            self.dependency_graph[file_path] = set()

            for dep in metadata.dependencies:
                # Find actual file paths for dependencies
                matching_files = self._find_dependency_files(dep)
                self.dependency_graph[file_path].update(matching_files)

    def _find_dependency_files(self, dependency: str) -> Set[str]:
        """Find actual file paths for a given dependency."""
        matching_files = set()

        for file_path, metadata in self.file_registry.items():
            # Check if the dependency matches any exports
            if (
                dependency in metadata.exports
                or dependency in metadata.classes
                or dependency in metadata.functions
            ):
                matching_files.add(file_path)

            # Check if the dependency is a module name
            if dependency.replace(".", os.sep) in file_path:
                matching_files.add(file_path)

        return matching_files

    def detect_orphaned_modules(self) -> List[str]:
        """🧩 Identify orphaned modules not linked to anything."""
        orphaned = []

        for file_path, metadata in self.file_registry.items():
            # Skip documentation and configuration files
            if metadata.file_type in {".md", ".json", ".yml", ".yaml"}:
                continue

            # Check if file is referenced by others
            is_referenced = False
            for other_path, other_deps in self.dependency_graph.items():
                if file_path in other_deps and other_path != file_path:
                    is_referenced = True
                    break

            # Check if it's a main/launcher file
            if "main" in metadata.path.lower() or "launcher" in metadata.path.lower():
                is_referenced = True

            if not is_referenced and metadata.file_type in {".py", ".aether"}:
                orphaned.append(file_path)
                metadata.is_orphaned = True

        return orphaned

    def detect_duplicate_logic(self) -> List[Tuple[str, str, float]]:
        """Identify modules with similar/duplicate logic."""
        duplicates = []

        # Compare files with similar purposes and names
        grouped_files = {}
        for file_path, metadata in self.file_registry.items():
            key = (metadata.purpose, metadata.file_type)
            if key not in grouped_files:
                grouped_files[key] = []
            grouped_files[key].append((file_path, metadata))

        for group in grouped_files.values():
            if len(group) > 1:
                # Compare files in the same group
                for i, (path1, meta1) in enumerate(group):
                    for path2, meta2 in group[i + 1 :]:
                        similarity = self._calculate_similarity(meta1, meta2)
                        if similarity > 0.7:  # High similarity threshold
                            duplicates.append((path1, path2, similarity))

        return duplicates

    def _calculate_similarity(self, meta1: FileMetadata, meta2: FileMetadata) -> float:
        """Calculate similarity between two files."""
        # Compare exports/functions
        exports1 = set(meta1.exports + meta1.classes + meta1.functions)
        exports2 = set(meta2.exports + meta2.classes + meta2.functions)

        if not exports1 and not exports2:
            return 0.0

        intersection = len(exports1.intersection(exports2))
        union = len(exports1.union(exports2))

        return intersection / union if union > 0 else 0.0

    def suggest_optimal_structure(self) -> List[Dict[str, Any]]:
        """🛠️ Generate suggestions for optimal file organization."""
        suggestions = []

        # Analyze current directory structure
        directory_purposes = {}
        for file_path, metadata in self.file_registry.items():
            directory = os.path.dirname(file_path)
            if directory not in directory_purposes:
                directory_purposes[directory] = {}

            purpose = metadata.purpose
            if purpose not in directory_purposes[directory]:
                directory_purposes[directory][purpose] = 0
            directory_purposes[directory][purpose] += 1

        # Suggest relocations for misplaced files
        for file_path, metadata in self.file_registry.items():
            current_dir = os.path.dirname(file_path)
            suggested_dir = self._suggest_directory(metadata)

            if suggested_dir and suggested_dir != current_dir:
                suggestions.append(
                    {
                        "type": "relocate",
                        "file": file_path,
                        "current_location": current_dir,
                        "suggested_location": suggested_dir,
                        "reason": f"File purpose '{metadata.purpose}' better fits in {suggested_dir}",
                        "confidence": 0.8,
                    }
                )

        return suggestions

    def _suggest_directory(self, metadata: FileMetadata) -> Optional[str]:
        """Suggest optimal directory for a file based on its purpose."""
        purpose_mapping = {
            "Plugin system": "plugins",
            "Memory management": "memory",
            "User interface": "gui",
            "Core system": "core",
            "Test file": "tests",
            "Documentation": "docs",
            "Demonstration code": "demos",
        }

        return purpose_mapping.get(metadata.purpose)

    def analyze_system_health(self) -> SystemAnalysis:
        """🧠 Comprehensive system analysis and health check."""
        orphaned = self.detect_orphaned_modules()
        duplicates = self.detect_duplicate_logic()
        broken_imports = self._detect_broken_imports()
        suggestions = self.suggest_optimal_structure()
        critical_files = self._identify_critical_files()
        refactor_recommendations = self._generate_refactor_recommendations()

        analysis = SystemAnalysis(
            total_files=len(self.file_registry),
            orphaned_files=orphaned,
            duplicate_logic=[(d[0], d[1]) for d in duplicates],
            broken_imports=broken_imports,
            optimization_suggestions=suggestions,
            critical_files=critical_files,
            refactor_recommendations=refactor_recommendations,
        )

        # Log analysis results
        self._log_analysis(analysis)

        return analysis

    def _detect_broken_imports(self) -> List[str]:
        """Detect files with broken import statements."""
        broken = []

        for file_path, metadata in self.file_registry.items():
            if metadata.file_type == ".py":
                for dependency in metadata.dependencies:
                    # Check if dependency can be resolved
                    if not self._can_resolve_dependency(dependency):
                        broken.append(f"{file_path}: {dependency}")

        return broken

    def _can_resolve_dependency(self, dependency: str) -> bool:
        """Check if a dependency can be resolved."""
        # Check standard library
        try:
            spec = importlib.util.find_spec(dependency)
            if spec is not None:
                return True
        except (ImportError, ValueError, ModuleNotFoundError):
            pass

        # Check project files
        matching_files = self._find_dependency_files(dependency)
        return len(matching_files) > 0

    def _identify_critical_files(self) -> List[str]:
        """Identify files critical to system operation."""
        critical = []

        for file_path, metadata in self.file_registry.items():
            # Files with many dependents are critical
            dependents = sum(
                1 for deps in self.dependency_graph.values() if file_path in deps
            )

            if dependents > 3:  # Threshold for criticality
                critical.append(file_path)

            # Core system files are critical
            if "core" in metadata.purpose.lower() or "launcher" in file_path.lower():
                critical.append(file_path)

        return list(set(critical))

    def _generate_refactor_recommendations(self) -> List[Dict[str, Any]]:
        """Generate high-impact refactoring recommendations."""
        recommendations = []

        # Recommend merging duplicate files
        duplicates = self.detect_duplicate_logic()
        for file1, file2, similarity in duplicates:
            if similarity > 0.8:
                recommendations.append(
                    {
                        "type": "merge_files",
                        "files": [file1, file2],
                        "reason": f"Files have {similarity:.1%} similarity",
                        "impact": "high",
                        "effort": "medium",
                    }
                )

        # Recommend archiving orphaned files
        orphaned = self.detect_orphaned_modules()
        for orphan in orphaned:
            recommendations.append(
                {
                    "type": "archive_file",
                    "file": orphan,
                    "reason": "File appears to be orphaned",
                    "impact": "low",
                    "effort": "low",
                }
            )

        return recommendations

    def _log_analysis(self, analysis: SystemAnalysis):
        """Log analysis results to evolution history."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "system_analysis",
            "files_analyzed": analysis.total_files,
            "orphaned_count": len(analysis.orphaned_files),
            "duplicate_count": len(analysis.duplicate_logic),
            "suggestions_count": len(analysis.optimization_suggestions),
            "critical_files_count": len(analysis.critical_files),
        }

        # Write to .aether format
        aether_log = f"""
# System Analysis - {log_entry["timestamp"]}
goal: "Comprehensive system health analysis"

analysis_results {{
    total_files: {log_entry["files_analyzed"]}
    orphaned_files: {log_entry["orphaned_count"]}
    duplicate_modules: {log_entry["duplicate_count"]}
    optimization_suggestions: {log_entry["suggestions_count"]}
    critical_files: {log_entry["critical_files_count"]}
}}

remember analysis_results as "system_health_{datetime.now().strftime("%Y%m%d_%H%M%S")}"
"""

        with open(self.evolution_log_path, "a", encoding="utf-8") as f:
            f.write(aether_log)

    def _update_database(self):
        """Update the file manifest database."""
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing data
            conn.execute("DELETE FROM file_manifest")

            # Insert current registry
            for metadata in self.file_registry.values():
                conn.execute(
                    """
                    INSERT INTO file_manifest VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """,
                    (
                        metadata.path,
                        metadata.file_type,
                        metadata.size,
                        metadata.last_modified,
                        metadata.content_hash,
                        json.dumps(metadata.dependencies),
                        json.dumps(metadata.exports),
                        json.dumps(metadata.imports),
                        json.dumps(metadata.classes),
                        json.dumps(metadata.functions),
                        json.dumps(metadata.plugins),
                        metadata.purpose,
                        metadata.risk_level,
                        metadata.usage_score,
                        metadata.is_orphaned,
                        metadata.suggested_location,
                        datetime.now().timestamp(),
                    ),
                )

    def _export_live_index(self):
        """Export live file index as JSON."""
        index_data = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.file_registry),
            "files": {
                path: asdict(metadata) for path, metadata in self.file_registry.items()
            },
            "dependency_graph": {
                path: list(deps) for path, deps in self.dependency_graph.items()
            },
        }

        with open(self.live_index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)

    def execute_safe_optimization(
        self, suggestions: List[Dict[str, Any]], dry_run: bool = True
    ) -> Dict[str, Any]:
        """🛡️ Execute optimization suggestions with safety checks."""
        results = {"executed": [], "skipped": [], "errors": [], "dry_run": dry_run}

        for suggestion in suggestions:
            try:
                if suggestion.get("risk_level", "medium") == "high":
                    results["skipped"].append(
                        {
                            "suggestion": suggestion,
                            "reason": "High risk operation requires manual approval",
                        }
                    )
                    continue

                if dry_run:
                    logger.info(
                        f"DRY RUN: Would execute {suggestion['type']} for {suggestion.get('file', 'multiple files')}"
                    )
                    results["executed"].append(suggestion)
                else:
                    # Execute the optimization
                    success = self._execute_suggestion(suggestion)
                    if success:
                        results["executed"].append(suggestion)
                    else:
                        results["errors"].append(
                            {"suggestion": suggestion, "error": "Execution failed"}
                        )

            except Exception as e:
                results["errors"].append({"suggestion": suggestion, "error": str(e)})

        return results

    def _execute_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        """Execute a specific optimization suggestion."""
        suggestion_type = suggestion["type"]

        if suggestion_type == "relocate":
            return self._execute_relocation(suggestion)
        elif suggestion_type == "merge_files":
            return self._execute_merge(suggestion)
        elif suggestion_type == "archive_file":
            return self._execute_archive(suggestion)

        return False

    def _execute_relocation(self, suggestion: Dict[str, Any]) -> bool:
        """Execute file relocation."""
        source = suggestion["file"]
        target_dir = suggestion["suggested_location"]

        # Create target directory if it doesn't exist
        target_path = self.project_root / target_dir
        target_path.mkdir(parents=True, exist_ok=True)

        # Move file
        source_path = Path(source)
        target_file = target_path / source_path.name

        try:
            source_path.rename(target_file)
            logger.info(f"Relocated {source} to {target_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to relocate {source}: {e}")
            return False

    def _execute_merge(self, suggestion: Dict[str, Any]) -> bool:
        """Execute file merge operation."""
        # This is a complex operation that would require careful analysis
        # For now, just log the suggestion
        logger.info(f"Merge suggestion logged: {suggestion['files']}")
        return True

    def _execute_archive(self, suggestion: Dict[str, Any]) -> bool:
        """Execute file archival."""
        file_path = Path(suggestion["file"])
        archive_dir = self.project_root / "archived"
        archive_dir.mkdir(exist_ok=True)

        try:
            archive_path = archive_dir / file_path.name
            file_path.rename(archive_path)
            logger.info(f"Archived {file_path} to {archive_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive {file_path}: {e}")
            return False


def main():
    """Main entry point for the file intelligence system."""
    import argparse

    parser = argparse.ArgumentParser(description="Aetherra File Intelligence System")
    parser.add_argument("--scan", action="store_true", help="Scan project files")
    parser.add_argument(
        "--analyze", action="store_true", help="Perform system analysis"
    )
    parser.add_argument("--optimize", action="store_true", help="Execute optimizations")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    # Initialize system
    intelligence = AetherraFileIntelligence(args.project_root)

    if args.scan:
        logger.info("🔍 Scanning project files...")
        intelligence.scan_project_files()
        logger.info("✅ File scan complete")

    if args.analyze:
        logger.info("🧠 Analyzing system health...")
        analysis = intelligence.analyze_system_health()

        print("\n📊 SYSTEM ANALYSIS RESULTS:")
        print(f"Total files: {analysis.total_files}")
        print(f"Orphaned files: {len(analysis.orphaned_files)}")
        print(f"Duplicate logic detected: {len(analysis.duplicate_logic)}")
        print(f"Broken imports: {len(analysis.broken_imports)}")
        print(f"Optimization suggestions: {len(analysis.optimization_suggestions)}")
        print(f"Critical files: {len(analysis.critical_files)}")

    if args.optimize:
        if not hasattr(intelligence, "file_registry") or not intelligence.file_registry:
            intelligence.scan_project_files()

        analysis = intelligence.analyze_system_health()
        results = intelligence.execute_safe_optimization(
            analysis.optimization_suggestions, dry_run=args.dry_run
        )

        print("\n🛠️ OPTIMIZATION RESULTS:")
        print(f"Executed: {len(results['executed'])}")
        print(f"Skipped: {len(results['skipped'])}")
        print(f"Errors: {len(results['errors'])}")


if __name__ == "__main__":
    main()
