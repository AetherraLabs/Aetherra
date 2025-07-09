"""
🔌 Enhanced Plugin Registry System
=================================

Beautiful, discoverable plugin management with auto-suggestions,
ratings, and comprehensive plugin lifecycle management.
"""

import importlib
import importlib.util
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use conditional import to avoid file permission issues during testing
try:
    from .memory.logger import MemoryLogger

    MEMORY_LOGGER_AVAILABLE = True
except (ImportError, PermissionError):
    MEMORY_LOGGER_AVAILABLE = False
    MemoryLogger = None


class PluginStatus(Enum):
    """Plugin status states"""

    AVAILABLE = "available"
    INSTALLED = "installed"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    OUTDATED = "outdated"


class PluginCategory(Enum):
    """Plugin categories for organization"""

    CORE = "core"
    UTILITY = "utility"
    DEVELOPMENT = "development"
    DATA_ANALYSIS = "data_analysis"
    AI_ENHANCEMENT = "ai_enhancement"
    UI_THEME = "ui_theme"
    INTEGRATION = "integration"
    AUTOMATION = "automation"
    ENTERTAINMENT = "entertainment"
    EXPERIMENTAL = "experimental"


@dataclass
class PluginRating:
    """Plugin rating and review"""

    user_id: str
    rating: float  # 1-5 stars
    review: str
    timestamp: datetime
    helpful_count: int = 0


@dataclass
class PluginMetadata:
    """Complete plugin metadata"""

    id: str
    name: str
    description: str
    version: str
    author: str
    category: PluginCategory
    tags: List[str]
    keywords: List[str]
    requirements: List[str]
    api_version: str
    status: PluginStatus

    # Usage and performance
    install_count: int = 0
    usage_count: int = 0
    last_used: Optional[datetime] = None
    performance_score: float = 0.0

    # Ratings and reviews
    ratings: Optional[List[PluginRating]] = None
    average_rating: float = 0.0
    total_ratings: int = 0

    # Documentation and support
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    support_url: Optional[str] = None

    # Compatibility and dependencies
    compatible_versions: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    conflicts: Optional[List[str]] = None

    def __post_init__(self):
        if self.ratings is None:
            self.ratings = []
        if self.compatible_versions is None:
            self.compatible_versions = []
        if self.dependencies is None:
            self.dependencies = []
        if self.conflicts is None:
            self.conflicts = []


@dataclass
class PluginUsageStats:
    """Plugin usage statistics"""

    plugin_id: str
    total_invocations: int
    total_execution_time: float
    average_execution_time: float
    success_rate: float
    last_invocation: datetime
    error_count: int
    user_sessions: int


class PluginRegistry:
    """Enhanced plugin registry with discovery and management"""

    def __init__(
        self, plugins_dir: Path = Path("plugins"), data_dir: Path = Path("data")
    ):
        self.plugins_dir = plugins_dir
        self.data_dir = data_dir
        self.plugins_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize memory logger conditionally
        if MEMORY_LOGGER_AVAILABLE and MemoryLogger is not None:
            try:
                self.memory_logger = MemoryLogger()
            except (PermissionError, FileNotFoundError):
                self.memory_logger = None
        else:
            self.memory_logger = None

        # Plugin storage
        self.available_plugins: Dict[str, PluginMetadata] = {}
        self.installed_plugins: Dict[str, Any] = {}
        self.active_plugins: Dict[str, Any] = {}

        # Usage tracking
        self.usage_stats: Dict[str, PluginUsageStats] = {}
        self.user_preferences: Dict[str, Any] = {}

        # Auto-suggestion system
        self.suggestion_engine = PluginSuggestionEngine()

        self._load_registry_data()
        self._scan_available_plugins()
        self._load_installed_plugins()

    def _load_registry_data(self):
        """Load registry data from disk"""
        registry_file = self.data_dir / "plugin_registry.json"
        if registry_file.exists():
            try:
                with open(registry_file) as f:
                    data = json.load(f)

                    # Load plugin metadata
                    for plugin_data in data.get("plugins", []):
                        metadata = PluginMetadata(
                            id=plugin_data["id"],
                            name=plugin_data["name"],
                            description=plugin_data["description"],
                            version=plugin_data["version"],
                            author=plugin_data["author"],
                            category=PluginCategory(plugin_data["category"]),
                            tags=plugin_data["tags"],
                            keywords=plugin_data["keywords"],
                            requirements=plugin_data["requirements"],
                            api_version=plugin_data["api_version"],
                            status=PluginStatus(plugin_data["status"]),
                            install_count=plugin_data.get("install_count", 0),
                            usage_count=plugin_data.get("usage_count", 0),
                            average_rating=plugin_data.get("average_rating", 0.0),
                        )

                        # Load ratings
                        for rating_data in plugin_data.get("ratings", []):
                            rating = PluginRating(
                                user_id=rating_data["user_id"],
                                rating=rating_data["rating"],
                                review=rating_data["review"],
                                timestamp=datetime.fromisoformat(
                                    rating_data["timestamp"]
                                ),
                                helpful_count=rating_data.get("helpful_count", 0),
                            )
                            if metadata.ratings is None:
                                metadata.ratings = []
                            metadata.ratings.append(rating)

                        self.available_plugins[metadata.id] = metadata

                    # Load usage stats
                    for stats_data in data.get("usage_stats", []):
                        stats = PluginUsageStats(
                            plugin_id=stats_data["plugin_id"],
                            total_invocations=stats_data["total_invocations"],
                            total_execution_time=stats_data["total_execution_time"],
                            average_execution_time=stats_data["average_execution_time"],
                            success_rate=stats_data["success_rate"],
                            last_invocation=datetime.fromisoformat(
                                stats_data["last_invocation"]
                            ),
                            error_count=stats_data["error_count"],
                            user_sessions=stats_data["user_sessions"],
                        )
                        self.usage_stats[stats.plugin_id] = stats

            except Exception as e:
                print(f"Error loading registry data: {e}")

    def _save_registry_data(self):
        """Save registry data to disk"""
        registry_file = self.data_dir / "plugin_registry.json"
        try:
            data = {"plugins": [], "usage_stats": []}

            # Save plugin metadata
            for metadata in self.available_plugins.values():
                plugin_data = asdict(metadata)
                plugin_data["category"] = metadata.category.value
                plugin_data["status"] = metadata.status.value

                # Convert ratings
                plugin_data["ratings"] = [
                    {
                        "user_id": rating.user_id,
                        "rating": rating.rating,
                        "review": rating.review,
                        "timestamp": rating.timestamp.isoformat(),
                        "helpful_count": rating.helpful_count,
                    }
                    for rating in (metadata.ratings or [])
                ]

                data["plugins"].append(plugin_data)

            # Save usage stats
            for stats in self.usage_stats.values():
                stats_data = asdict(stats)
                stats_data["last_invocation"] = stats.last_invocation.isoformat()
                data["usage_stats"].append(stats_data)

            with open(registry_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            print(f"Error saving registry data: {e}")

    def _scan_available_plugins(self):
        """Scan for available plugins in the plugins directory"""
        if not self.plugins_dir.exists():
            return

        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue

            try:
                # Import plugin module
                spec = importlib.util.spec_from_file_location(
                    plugin_file.stem, plugin_file
                )
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Extract plugin metadata
                if hasattr(module, "PLUGIN_INFO"):
                    info = module.PLUGIN_INFO
                    plugin_id = info.get("id", plugin_file.stem)

                    if plugin_id not in self.available_plugins:
                        metadata = PluginMetadata(
                            id=plugin_id,
                            name=info.get("name", plugin_id),
                            description=info.get("description", "No description"),
                            version=info.get("version", "1.0.0"),
                            author=info.get("author", "Unknown"),
                            category=PluginCategory(info.get("category", "utility")),
                            tags=info.get("tags", []),
                            keywords=info.get("keywords", []),
                            requirements=info.get("requirements", []),
                            api_version=info.get("api_version", "1.0"),
                            status=PluginStatus.AVAILABLE,
                        )
                        self.available_plugins[plugin_id] = metadata

            except Exception as e:
                print(f"Error scanning plugin {plugin_file}: {e}")

    def _load_installed_plugins(self):
        """Load and activate installed plugins"""
        for plugin_id, metadata in self.available_plugins.items():
            if metadata.status in [PluginStatus.INSTALLED, PluginStatus.ACTIVE]:
                try:
                    plugin_instance = self._create_plugin_instance(plugin_id)
                    if plugin_instance:
                        self.installed_plugins[plugin_id] = plugin_instance
                        if metadata.status == PluginStatus.ACTIVE:
                            self.active_plugins[plugin_id] = plugin_instance
                except Exception as e:
                    print(f"Error loading plugin {plugin_id}: {e}")
                    metadata.status = PluginStatus.ERROR

    def _create_plugin_instance(self, plugin_id: str) -> Optional[Any]:
        """Create an instance of a plugin"""
        plugin_file = self.plugins_dir / f"{plugin_id}.py"
        if not plugin_file.exists():
            return None

        try:
            spec = importlib.util.spec_from_file_location(plugin_id, plugin_file)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for plugin class or function
            if hasattr(module, "Plugin"):
                return module.Plugin()
            elif hasattr(module, "create_plugin"):
                return module.create_plugin()
            else:
                return module  # Return module itself

        except Exception as e:
            print(f"Error creating plugin instance for {plugin_id}: {e}")
            return None

    def search_plugins(
        self,
        query: str,
        category: Optional[PluginCategory] = None,
        tags: Optional[List[str]] = None,
    ) -> List[PluginMetadata]:
        """Search plugins by query, category, and tags"""
        query_lower = query.lower()
        results = []

        for metadata in self.available_plugins.values():
            # Text search
            text_match = (
                query_lower in metadata.name.lower()
                or query_lower in metadata.description.lower()
                or any(query_lower in keyword.lower() for keyword in metadata.keywords)
            )

            # Category filter
            category_match = category is None or metadata.category == category

            # Tags filter
            tags_match = tags is None or any(tag in metadata.tags for tag in tags)

            if text_match and category_match and tags_match:
                results.append(metadata)

        # Sort by relevance (rating, usage, etc.)
        results.sort(key=lambda p: (p.average_rating, p.usage_count), reverse=True)
        return results

    def get_plugin_catalog(self) -> Dict[str, Any]:
        """Get comprehensive plugin catalog"""
        catalog = {
            "categories": {},
            "featured": [],
            "popular": [],
            "new": [],
            "trending": [],
            "stats": {
                "total_plugins": len(self.available_plugins),
                "installed_plugins": len(self.installed_plugins),
                "active_plugins": len(self.active_plugins),
            },
        }

        # Group by categories
        for metadata in self.available_plugins.values():
            category = metadata.category.value
            if category not in catalog["categories"]:
                catalog["categories"][category] = []
            catalog["categories"][category].append(asdict(metadata))

        # Featured plugins (high rated and popular)
        featured = [
            p
            for p in self.available_plugins.values()
            if p.average_rating >= 4.0 and p.usage_count > 100
        ]
        catalog["featured"] = sorted(
            featured, key=lambda p: p.average_rating, reverse=True
        )[:10]

        # Popular plugins
        catalog["popular"] = sorted(
            self.available_plugins.values(), key=lambda p: p.usage_count, reverse=True
        )[:10]

        # New plugins (added in last 30 days)
        # This would require tracking when plugins were added

        return catalog

    def install_plugin(self, plugin_id: str) -> bool:
        """Install a plugin"""
        if plugin_id not in self.available_plugins:
            return False

        metadata = self.available_plugins[plugin_id]

        try:
            # Check dependencies
            if metadata.dependencies and not self._check_dependencies(
                metadata.dependencies
            ):
                print(f"Missing dependencies for {plugin_id}")
                return False

            # Create plugin instance
            plugin_instance = self._create_plugin_instance(plugin_id)
            if not plugin_instance:
                return False

            # Update status
            metadata.status = PluginStatus.INSTALLED
            metadata.install_count += 1
            self.installed_plugins[plugin_id] = plugin_instance

            # Log installation
            if self.memory_logger:
                self.memory_logger.log_memory(
                    f"Installed plugin: {metadata.name} [plugin:{plugin_id}]"
                )

            self._save_registry_data()
            return True

        except Exception as e:
            print(f"Error installing plugin {plugin_id}: {e}")
            metadata.status = PluginStatus.ERROR
            return False

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        if plugin_id not in self.installed_plugins:
            return False

        try:
            # Deactivate if active
            if plugin_id in self.active_plugins:
                self.deactivate_plugin(plugin_id)

            # Remove from installed
            del self.installed_plugins[plugin_id]

            # Update status
            metadata = self.available_plugins[plugin_id]
            metadata.status = PluginStatus.AVAILABLE

            # Log uninstallation
            if self.memory_logger:
                self.memory_logger.log_memory(
                    f"Uninstalled plugin: {metadata.name} [plugin:{plugin_id}]"
                )

            self._save_registry_data()
            return True

        except Exception as e:
            print(f"Error uninstalling plugin {plugin_id}: {e}")
            return False

    def activate_plugin(self, plugin_id: str) -> bool:
        """Activate an installed plugin"""
        if plugin_id not in self.installed_plugins:
            return False

        try:
            plugin_instance = self.installed_plugins[plugin_id]

            # Call activation hook if available
            if hasattr(plugin_instance, "activate"):
                plugin_instance.activate()

            self.active_plugins[plugin_id] = plugin_instance
            self.available_plugins[plugin_id].status = PluginStatus.ACTIVE

            self._save_registry_data()
            return True

        except Exception as e:
            print(f"Error activating plugin {plugin_id}: {e}")
            return False

    def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate an active plugin"""
        if plugin_id not in self.active_plugins:
            return False

        try:
            plugin_instance = self.active_plugins[plugin_id]

            # Call deactivation hook if available
            if hasattr(plugin_instance, "deactivate"):
                plugin_instance.deactivate()

            del self.active_plugins[plugin_id]
            self.available_plugins[plugin_id].status = PluginStatus.INSTALLED

            self._save_registry_data()
            return True

        except Exception as e:
            print(f"Error deactivating plugin {plugin_id}: {e}")
            return False

    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if plugin dependencies are satisfied"""
        for dep in dependencies:
            if dep not in self.installed_plugins:
                return False
        return True

    def rate_plugin(
        self, plugin_id: str, rating: float, review: str, user_id: str = "default"
    ) -> bool:
        """Rate and review a plugin"""
        if plugin_id not in self.available_plugins:
            return False

        if not 1.0 <= rating <= 5.0:
            return False

        metadata = self.available_plugins[plugin_id]

        # Add new rating
        new_rating = PluginRating(
            user_id=user_id, rating=rating, review=review, timestamp=datetime.now()
        )

        if metadata.ratings is None:
            metadata.ratings = []
        metadata.ratings.append(new_rating)

        # Recalculate average rating
        if metadata.ratings:
            metadata.average_rating = sum(r.rating for r in metadata.ratings) / len(
                metadata.ratings
            )
            metadata.total_ratings = len(metadata.ratings)

        self._save_registry_data()
        return True

    def get_plugin_suggestions(
        self, context: str, limit: int = 5
    ) -> List[PluginMetadata]:
        """Get plugin suggestions based on context"""
        return self.suggestion_engine.get_suggestions(
            context, self.available_plugins, limit
        )

    def track_plugin_usage(
        self, plugin_id: str, execution_time: float, success: bool = True
    ):
        """Track plugin usage for analytics"""
        if plugin_id not in self.usage_stats:
            self.usage_stats[plugin_id] = PluginUsageStats(
                plugin_id=plugin_id,
                total_invocations=0,
                total_execution_time=0.0,
                average_execution_time=0.0,
                success_rate=1.0,
                last_invocation=datetime.now(),
                error_count=0,
                user_sessions=1,
            )

        stats = self.usage_stats[plugin_id]
        stats.total_invocations += 1
        stats.total_execution_time += execution_time
        stats.average_execution_time = (
            stats.total_execution_time / stats.total_invocations
        )
        stats.last_invocation = datetime.now()

        if not success:
            stats.error_count += 1

        stats.success_rate = (
            stats.total_invocations - stats.error_count
        ) / stats.total_invocations

        # Update plugin metadata
        if plugin_id in self.available_plugins:
            self.available_plugins[plugin_id].usage_count = stats.total_invocations
            self.available_plugins[plugin_id].last_used = stats.last_invocation
            self.available_plugins[plugin_id].performance_score = min(
                1.0, stats.success_rate * (1.0 / max(0.1, stats.average_execution_time))
            )


class PluginSuggestionEngine:
    """Engine for intelligent plugin suggestions"""

    def __init__(self):
        self.context_keywords = {
            "data_analysis": ["data", "analyze", "statistics", "chart", "graph"],
            "development": ["code", "debug", "test", "build", "deploy"],
            "automation": ["automate", "script", "batch", "schedule", "workflow"],
            "ui_enhancement": ["theme", "color", "interface", "display", "visual"],
        }

    def get_suggestions(
        self, context: str, available_plugins: Dict[str, PluginMetadata], limit: int = 5
    ) -> List[PluginMetadata]:
        """Get plugin suggestions based on context"""
        context_lower = context.lower()
        scored_plugins = []

        for metadata in available_plugins.values():
            score = self._calculate_relevance_score(context_lower, metadata)
            if score > 0:
                scored_plugins.append((score, metadata))

        # Sort by score and return top suggestions
        scored_plugins.sort(key=lambda x: x[0], reverse=True)
        return [metadata for _, metadata in scored_plugins[:limit]]

    def _calculate_relevance_score(
        self, context: str, metadata: PluginMetadata
    ) -> float:
        """Calculate relevance score for a plugin given context"""
        score = 0.0

        # Keyword matching
        for keyword in metadata.keywords:
            if keyword.lower() in context:
                score += 2.0

        # Tag matching
        for tag in metadata.tags:
            if tag.lower() in context:
                score += 1.5

        # Description matching
        description_words = metadata.description.lower().split()
        context_words = context.split()
        common_words = set(description_words).intersection(set(context_words))
        score += len(common_words) * 0.5

        # Boost for popular and well-rated plugins
        score += metadata.average_rating * 0.2
        score += min(1.0, metadata.usage_count / 100) * 0.3

        return score


# Global plugin registry instance
plugin_registry = PluginRegistry()


# Convenience functions
def search_plugins(query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search plugins with simplified interface"""
    cat = PluginCategory(category) if category else None
    results = plugin_registry.search_plugins(query, cat)
    return [asdict(plugin) for plugin in results]


def install_plugin(plugin_id: str) -> bool:
    """Install a plugin"""
    return plugin_registry.install_plugin(plugin_id)


def get_plugin_suggestions(context: str) -> List[Dict[str, Any]]:
    """Get plugin suggestions for context"""
    suggestions = plugin_registry.get_plugin_suggestions(context)
    return [asdict(plugin) for plugin in suggestions]


def get_plugin_catalog() -> Dict[str, Any]:
    """Get complete plugin catalog"""
    return plugin_registry.get_plugin_catalog()
