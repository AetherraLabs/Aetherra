"""
Plugin Discovery System
=======================

Advanced plugin discovery, indexing, and recommendation system for Lyrixa.
Automatically discovers, categorizes, and suggests relevant plugins.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class PluginMetadata:
    """Plugin metadata container."""

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.category = "unknown"
        self.description = ""
        self.author = ""
        self.version = "1.0.0"
        self.tags = []
        self.dependencies = []
        self.capabilities = []
        self.file_hash = ""
        self.last_modified: Optional[datetime] = None
        self.discovery_time = datetime.now()
        self.usage_count = 0
        self.rating = 0.0
        self.compatibility_score = 0.0


class PluginDiscovery:
    """Plugin discovery and indexing system."""

    def __init__(self, plugins_dir: str = None):
        self.plugins_dir = plugins_dir or os.path.join(os.path.dirname(__file__))
        self.plugin_index = {}
        self.categories = set()
        self.tags = set()
        self.discovery_history = []
        self.search_cache = {}
        self.recommendation_engine = None
        self._initialize_discovery()

    def _initialize_discovery(self):
        """Initialize the discovery system."""
        self._load_plugin_index()
        self._setup_recommendation_engine()

    def _load_plugin_index(self):
        """Load existing plugin index from cache."""
        index_file = os.path.join(self.plugins_dir, ".plugin_index.json")
        if os.path.exists(index_file):
            try:
                with open(index_file, "r") as f:
                    data = json.load(f)
                    self._deserialize_index(data)
            except Exception as e:
                print(f"Could not load plugin index: {e}")

    def _save_plugin_index(self):
        """Save plugin index to cache."""
        index_file = os.path.join(self.plugins_dir, ".plugin_index.json")
        try:
            data = self._serialize_index()
            with open(index_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save plugin index: {e}")

    def _serialize_index(self) -> Dict:
        """Serialize plugin index to JSON-compatible format."""
        return {
            "plugins": {
                name: {
                    "name": meta.name,
                    "path": meta.path,
                    "category": meta.category,
                    "description": meta.description,
                    "author": meta.author,
                    "version": meta.version,
                    "tags": meta.tags,
                    "dependencies": meta.dependencies,
                    "capabilities": meta.capabilities,
                    "file_hash": meta.file_hash,
                    "last_modified": meta.last_modified.isoformat()
                    if meta.last_modified
                    else None,
                    "discovery_time": meta.discovery_time.isoformat(),
                    "usage_count": meta.usage_count,
                    "rating": meta.rating,
                    "compatibility_score": meta.compatibility_score,
                }
                for name, meta in self.plugin_index.items()
            },
            "categories": list(self.categories),
            "tags": list(self.tags),
            "last_discovery": datetime.now().isoformat(),
        }

    def _deserialize_index(self, data: Dict):
        """Deserialize plugin index from JSON data."""
        for name, plugin_data in data.get("plugins", {}).items():
            meta = PluginMetadata(plugin_data["name"], plugin_data["path"])
            meta.category = plugin_data.get("category", "unknown")
            meta.description = plugin_data.get("description", "")
            meta.author = plugin_data.get("author", "")
            meta.version = plugin_data.get("version", "1.0.0")
            meta.tags = plugin_data.get("tags", [])
            meta.dependencies = plugin_data.get("dependencies", [])
            meta.capabilities = plugin_data.get("capabilities", [])
            meta.file_hash = plugin_data.get("file_hash", "")
            meta.usage_count = plugin_data.get("usage_count", 0)
            meta.rating = plugin_data.get("rating", 0.0)
            meta.compatibility_score = plugin_data.get("compatibility_score", 0.0)

            # Parse timestamps
            if plugin_data.get("last_modified"):
                meta.last_modified = datetime.fromisoformat(
                    plugin_data["last_modified"]
                )
            if plugin_data.get("discovery_time"):
                meta.discovery_time = datetime.fromisoformat(
                    plugin_data["discovery_time"]
                )

            self.plugin_index[name] = meta

        self.categories = set(data.get("categories", []))
        self.tags = set(data.get("tags", []))

    def discover_plugins(
        self, force_refresh: bool = False
    ) -> Dict[str, PluginMetadata]:
        """Discover all plugins in the plugins directory."""
        if not force_refresh and self.plugin_index:
            # Check if any files have been modified
            needs_refresh = False
            for name, meta in self.plugin_index.items():
                if os.path.exists(meta.path):
                    current_mtime = datetime.fromtimestamp(os.path.getmtime(meta.path))
                    if meta.last_modified and current_mtime > meta.last_modified:
                        needs_refresh = True
                        break

            if not needs_refresh:
                return self.plugin_index

        discovered_plugins = {}

        if not os.path.exists(self.plugins_dir):
            return discovered_plugins

        for file in os.listdir(self.plugins_dir):
            if file.endswith(".py") and not file.startswith("__"):
                plugin_name = file[:-3]  # Remove .py extension

                # Skip system files
                if plugin_name in [
                    "plugin_manager",
                    "enhanced_plugin_manager",
                    "plugin_analytics",
                    "plugin_quality_control",
                    "plugin_discovery",
                ]:
                    continue

                plugin_path = os.path.join(self.plugins_dir, file)

                # Check if plugin already exists and hasn't changed
                if plugin_name in self.plugin_index and not force_refresh:
                    existing_meta = self.plugin_index[plugin_name]
                    current_hash = self._calculate_file_hash(plugin_path)

                    if existing_meta.file_hash == current_hash:
                        discovered_plugins[plugin_name] = existing_meta
                        continue

                # Analyze plugin file
                metadata = self._analyze_plugin_file(plugin_name, plugin_path)
                if metadata:
                    discovered_plugins[plugin_name] = metadata

                    # Update categories and tags
                    self.categories.add(metadata.category)
                    self.tags.update(metadata.tags)

        # Update index
        self.plugin_index = discovered_plugins
        self._save_plugin_index()

        # Record discovery
        self.discovery_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "plugins_found": len(discovered_plugins),
                "force_refresh": force_refresh,
            }
        )

        return discovered_plugins

    def _analyze_plugin_file(
        self, plugin_name: str, plugin_path: str
    ) -> Optional[PluginMetadata]:
        """Analyze a plugin file to extract metadata."""
        try:
            metadata = PluginMetadata(plugin_name, plugin_path)

            # Calculate file hash
            metadata.file_hash = self._calculate_file_hash(plugin_path)
            metadata.last_modified = datetime.fromtimestamp(
                os.path.getmtime(plugin_path)
            )

            # Read and parse file content
            with open(plugin_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract metadata from content
            self._extract_metadata_from_content(content, metadata)

            # Analyze code structure
            self._analyze_code_structure(content, metadata)

            # Calculate compatibility score
            metadata.compatibility_score = self._calculate_compatibility_score(
                content, metadata
            )

            return metadata

        except Exception as e:
            print(f"Error analyzing plugin {plugin_name}: {e}")
            return None

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content."""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception:
            return ""

    def _extract_metadata_from_content(self, content: str, metadata: PluginMetadata):
        """Extract metadata from plugin file content."""
        lines = content.split("\n")

        # Look for metadata variables
        for line in lines:
            line = line.strip()

            if line.startswith("__version__"):
                metadata.version = self._extract_string_value(line)
            elif line.startswith("__author__"):
                metadata.author = self._extract_string_value(line)
            elif line.startswith("__description__"):
                metadata.description = self._extract_string_value(line)
            elif line.startswith("__category__"):
                metadata.category = self._extract_string_value(line)
            elif line.startswith("__tags__"):
                metadata.tags = self._extract_list_value(line)
            elif line.startswith("__dependencies__"):
                metadata.dependencies = self._extract_list_value(line)

        # Extract description from docstring if not found
        if not metadata.description:
            docstring = self._extract_module_docstring(content)
            if docstring:
                metadata.description = docstring.split("\\n")[0].strip()

        # Auto-detect category if not specified
        if metadata.category == "unknown":
            metadata.category = self._auto_detect_category(content)

        # Auto-generate tags
        auto_tags = self._auto_generate_tags(content, metadata)
        metadata.tags.extend(auto_tags)
        metadata.tags = list(set(metadata.tags))  # Remove duplicates

    def _extract_string_value(self, line: str) -> str:
        """Extract string value from a Python assignment line."""
        try:
            # Find the value after the equals sign
            value_part = line.split("=", 1)[1].strip()
            # Remove quotes
            if value_part.startswith('"') and value_part.endswith('"'):
                return value_part[1:-1]
            elif value_part.startswith("'") and value_part.endswith("'"):
                return value_part[1:-1]
            return value_part
        except Exception:
            return ""

    def _extract_list_value(self, line: str) -> List[str]:
        """Extract list value from a Python assignment line."""
        try:
            # Simple list extraction - assumes format: var = ["item1", "item2"]
            value_part = line.split("=", 1)[1].strip()
            if value_part.startswith("[") and value_part.endswith("]"):
                # Remove brackets and split by comma
                items = value_part[1:-1].split(",")
                return [item.strip().strip("\"'") for item in items if item.strip()]
            return []
        except Exception:
            return []

    def _extract_module_docstring(self, content: str) -> str:
        """Extract module-level docstring."""
        try:
            import ast

            tree = ast.parse(content)
            if (
                tree.body
                and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)
            ):
                return tree.body[0].value.value
        except Exception:
            pass
        return ""

    def _auto_detect_category(self, content: str) -> str:
        """Auto-detect plugin category based on content analysis."""
        content_lower = content.lower()

        # Category detection patterns
        if any(
            keyword in content_lower for keyword in ["api", "request", "http", "rest"]
        ):
            return "integration"
        elif any(
            keyword in content_lower
            for keyword in ["data", "process", "analyze", "filter"]
        ):
            return "data"
        elif any(
            keyword in content_lower
            for keyword in ["text", "string", "parse", "format"]
        ):
            return "text"
        elif any(
            keyword in content_lower for keyword in ["file", "directory", "path", "io"]
        ):
            return "file"
        elif any(
            keyword in content_lower
            for keyword in ["ui", "interface", "gui", "display"]
        ):
            return "interface"
        elif any(keyword in content_lower for keyword in ["utility", "tool", "helper"]):
            return "utility"

        return "general"

    def _auto_generate_tags(self, content: str, metadata: PluginMetadata) -> List[str]:
        """Auto-generate relevant tags based on content analysis."""
        tags = []
        content_lower = content.lower()

        # Technology tags
        tech_keywords = {
            "json": "json",
            "xml": "xml",
            "csv": "csv",
            "sql": "database",
            "http": "web",
            "api": "api",
            "rest": "rest",
            "async": "async",
            "threading": "multithreading",
            "multiprocessing": "parallel",
            "regex": "regex",
            "datetime": "time",
            "pathlib": "filesystem",
        }

        for keyword, tag in tech_keywords.items():
            if keyword in content_lower:
                tags.append(tag)

        # Functionality tags
        if "class" in content_lower and "def execute" in content_lower:
            tags.append("executable")

        if "def main" in content_lower:
            tags.append("standalone")

        if "try:" in content and "except:" in content:
            tags.append("error-handling")

        # Category-specific tags
        if metadata.category == "data":
            tags.extend(["processing", "transformation"])
        elif metadata.category == "integration":
            tags.extend(["external", "connectivity"])

        return tags

    def _analyze_code_structure(self, content: str, metadata: PluginMetadata):
        """Analyze plugin code structure to determine capabilities."""
        try:
            import ast

            tree = ast.parse(content)

            # Find classes and methods
            classes = [
                node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]
            functions = [
                node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
            ]

            capabilities = []

            # Check for standard plugin methods
            method_names = [func.name for func in functions]

            if "execute" in method_names:
                capabilities.append("execute")
            if "main" in method_names:
                capabilities.append("main")
            if "get_info" in method_names:
                capabilities.append("info")
            if "cleanup" in method_names:
                capabilities.append("cleanup")

            # Check for data processing capabilities
            if any(
                name in method_names for name in ["process", "analyze", "transform"]
            ):
                capabilities.append("data_processing")

            # Check for file operations
            if any(
                name in method_names
                for name in ["read_file", "write_file", "process_file"]
            ):
                capabilities.append("file_operations")

            metadata.capabilities = capabilities

        except Exception as e:
            print(f"Error analyzing code structure: {e}")

    def _calculate_compatibility_score(
        self, content: str, metadata: PluginMetadata
    ) -> float:
        """Calculate compatibility score based on code analysis."""
        score = 100.0

        try:
            # Check for Python 3 compatibility
            if "print(" in content:
                score += 10
            elif "print " in content:
                score -= 20  # Python 2 style print

            # Check for type hints
            if "typing" in content or "->" in content:
                score += 15

            # Check for error handling
            if "try:" in content and "except:" in content:
                score += 10

            # Check for documentation
            if '"""' in content or "'''" in content:
                score += 10

            # Check for dangerous operations
            dangerous_patterns = ["eval(", "exec(", "os.system(", "__import__"]
            for pattern in dangerous_patterns:
                if pattern in content:
                    score -= 30

            # Normalize score
            score = max(0, min(100, score))

        except Exception:
            score = 50.0  # Default score if analysis fails

        return score

    def search_plugins(self, query: str, filters: Dict = None) -> List[PluginMetadata]:
        """Search for plugins based on query and filters."""
        # Check cache first
        cache_key = f"{query}:{json.dumps(filters or {}, sort_keys=True)}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]

        results = []
        query_lower = query.lower()
        filters = filters or {}

        for plugin_name, metadata in self.plugin_index.items():
            score = 0

            # Text matching
            if query_lower in metadata.name.lower():
                score += 10
            if query_lower in metadata.description.lower():
                score += 8
            if any(query_lower in tag.lower() for tag in metadata.tags):
                score += 6
            if query_lower in metadata.category.lower():
                score += 5
            if any(query_lower in cap.lower() for cap in metadata.capabilities):
                score += 4

            # Apply filters
            if filters.get("category") and metadata.category != filters["category"]:
                continue
            if filters.get("min_rating") and metadata.rating < filters["min_rating"]:
                continue
            if filters.get("tags") and not any(
                tag in metadata.tags for tag in filters["tags"]
            ):
                continue
            if (
                filters.get("min_compatibility")
                and metadata.compatibility_score < filters["min_compatibility"]
            ):
                continue

            if score > 0:
                results.append((score, metadata))

        # Sort by relevance score
        results.sort(key=lambda x: x[0], reverse=True)
        final_results = [metadata for score, metadata in results]

        # Cache results
        self.search_cache[cache_key] = final_results

        return final_results

    def get_plugins_by_category(self, category: str) -> List[PluginMetadata]:
        """Get all plugins in a specific category."""
        return [
            meta for meta in self.plugin_index.values() if meta.category == category
        ]

    def get_plugins_by_tags(self, tags: List[str]) -> List[PluginMetadata]:
        """Get plugins that have any of the specified tags."""
        return [
            meta
            for meta in self.plugin_index.values()
            if any(tag in meta.tags for tag in tags)
        ]

    def get_recommended_plugins(self, context: Dict = None) -> List[PluginMetadata]:
        """Get recommended plugins based on context."""
        if not self.recommendation_engine:
            # Simple recommendation based on usage and rating
            plugins = list(self.plugin_index.values())
            plugins.sort(key=lambda p: (p.rating, p.usage_count), reverse=True)
            return plugins[:10]

        return self.recommendation_engine.get_recommendations(context)

    def _setup_recommendation_engine(self):
        """Setup the recommendation engine."""
        # Placeholder for advanced recommendation system
        self.recommendation_engine = None

    def update_plugin_usage(self, plugin_name: str):
        """Update plugin usage statistics."""
        if plugin_name in self.plugin_index:
            self.plugin_index[plugin_name].usage_count += 1
            self._save_plugin_index()

    def rate_plugin(self, plugin_name: str, rating: float):
        """Rate a plugin (0.0 to 5.0)."""
        if plugin_name in self.plugin_index:
            # Simple average rating (could be improved with weighted ratings)
            current_rating = self.plugin_index[plugin_name].rating
            if current_rating == 0:
                self.plugin_index[plugin_name].rating = rating
            else:
                self.plugin_index[plugin_name].rating = (current_rating + rating) / 2
            self._save_plugin_index()

    def get_discovery_stats(self) -> Dict:
        """Get plugin discovery statistics."""
        return {
            "total_plugins": len(self.plugin_index),
            "categories": len(self.categories),
            "total_tags": len(self.tags),
            "categories_list": list(self.categories),
            "popular_tags": list(self.tags)[:20],  # Top 20 tags
            "discovery_history": self.discovery_history[-10:],  # Last 10 discoveries
            "average_rating": sum(p.rating for p in self.plugin_index.values())
            / len(self.plugin_index)
            if self.plugin_index
            else 0,
            "average_compatibility": sum(
                p.compatibility_score for p in self.plugin_index.values()
            )
            / len(self.plugin_index)
            if self.plugin_index
            else 0,
        }

    def clear_cache(self):
        """Clear search cache."""
        self.search_cache.clear()

    def export_index(self) -> Dict:
        """Export the complete plugin index."""
        return self._serialize_index()

    def import_index(self, data: Dict):
        """Import plugin index from external data."""
        self._deserialize_index(data)
        self._save_plugin_index()


# Global discovery instance
plugin_discovery = PluginDiscovery()


def discover_plugins(force_refresh: bool = False) -> Dict[str, PluginMetadata]:
    """Convenience function for plugin discovery."""
    return plugin_discovery.discover_plugins(force_refresh)


def search_plugins(query: str, filters: Dict = None) -> List[PluginMetadata]:
    """Convenience function for plugin search."""
    return plugin_discovery.search_plugins(query, filters)
