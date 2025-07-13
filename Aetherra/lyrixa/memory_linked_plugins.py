#!/usr/bin/env python3
"""
🔗 MEMORY-LINKED PLUGIN SYSTEM
==============================

Enhanced plugin discovery with metadata, context-aware suggestions,
and intelligent plugin recommendations based on memory and goals.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginMetadata:
    """Represents plugin metadata for intelligent discovery"""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.description = ""
        self.tags = []
        self.input_types = []
        self.output_types = []
        self.collaborates_with = []
        self.use_cases = []
        self.confidence_score = 0.0
        self.last_used = None
        self.success_rate = 0.0
        self.performance_score = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "plugin_id": self.plugin_id,
            "description": self.description,
            "tags": self.tags,
            "input_types": self.input_types,
            "output_types": self.output_types,
            "collaborates_with": self.collaborates_with,
            "use_cases": self.use_cases,
            "confidence_score": self.confidence_score,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "success_rate": self.success_rate,
            "performance_score": self.performance_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """Create from dictionary"""
        metadata = cls(data.get("plugin_id", ""))
        metadata.description = data.get("description", "")
        metadata.tags = data.get("tags", [])
        metadata.input_types = data.get("input_types", [])
        metadata.output_types = data.get("output_types", [])
        metadata.collaborates_with = data.get("collaborates_with", [])
        metadata.use_cases = data.get("use_cases", [])
        metadata.confidence_score = data.get("confidence_score", 0.0)
        metadata.success_rate = data.get("success_rate", 0.0)
        metadata.performance_score = data.get("performance_score", 0.0)

        if data.get("last_used"):
            try:
                metadata.last_used = datetime.fromisoformat(data["last_used"])
            except ValueError:
                metadata.last_used = None

        return metadata


class MemoryLinkedPluginDiscovery:
    """
    🔗 Memory-Linked Plugin Discovery System

    Provides intelligent plugin recommendations based on:
    - Memory context and past interactions
    - Goal patterns and user behavior
    - Plugin performance and usage history
    - Contextual relevance and collaboration patterns
    """

    def __init__(self, workspace_path: str, memory_manager=None):
        self.workspace_path = Path(workspace_path)
        self.memory_manager = memory_manager

        # Plugin metadata storage
        self.metadata_file = self.workspace_path / "plugin_metadata.json"
        self.plugin_metadata = {}
        self.load_metadata()

        # Usage tracking
        self.usage_history = []
        self.usage_file = self.workspace_path / "plugin_usage_history.json"
        self.load_usage_history()

        # Context patterns for recommendations
        self.context_patterns = {
            "data_analysis": [
                "visualization",
                "chart",
                "graph",
                "analysis",
                "statistics",
            ],
            "file_management": [
                "file",
                "directory",
                "organize",
                "copy",
                "move",
                "backup",
            ],
            "automation": ["automate", "schedule", "workflow", "batch", "process"],
            "debugging": ["debug", "error", "fix", "troubleshoot", "diagnose"],
            "monitoring": ["monitor", "watch", "track", "observe", "alert"],
            "communication": ["send", "notify", "message", "email", "alert"],
            "security": ["secure", "encrypt", "protect", "validate", "authenticate"],
        }

    def load_metadata(self):
        """Load plugin metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self.plugin_metadata = {
                        plugin_id: PluginMetadata.from_dict(meta_data)
                        for plugin_id, meta_data in data.items()
                    }
                logger.info(
                    f"📚 Loaded metadata for {len(self.plugin_metadata)} plugins"
                )
            except Exception as e:
                logger.error(f"❌ Failed to load plugin metadata: {e}")
                self.plugin_metadata = {}

    def save_metadata(self):
        """Save plugin metadata to file"""
        try:
            data = {
                plugin_id: metadata.to_dict()
                for plugin_id, metadata in self.plugin_metadata.items()
            }
            with open(self.metadata_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"💾 Saved metadata for {len(self.plugin_metadata)} plugins")
        except Exception as e:
            logger.error(f"❌ Failed to save plugin metadata: {e}")

    def load_usage_history(self):
        """Load plugin usage history"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, "r") as f:
                    self.usage_history = json.load(f)
                logger.info(f"📊 Loaded {len(self.usage_history)} usage records")
            except Exception as e:
                logger.error(f"❌ Failed to load usage history: {e}")
                self.usage_history = []

    def save_usage_history(self):
        """Save plugin usage history"""
        try:
            with open(self.usage_file, "w") as f:
                json.dump(self.usage_history, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save usage history: {e}")

    def extract_metadata_from_code(self, plugin_path: Path) -> PluginMetadata:
        """Extract metadata from plugin code"""
        metadata = PluginMetadata(plugin_path.stem)

        try:
            code = plugin_path.read_text(encoding="utf-8")

            # Extract description from docstring
            docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
            if docstring_match:
                metadata.description = docstring_match.group(1).strip()

            # Look for explicit metadata in comments
            json_match = re.search(r"#\s*METADATA:\s*({.*?})", code, re.DOTALL)
            if json_match:
                try:
                    explicit_metadata = json.loads(json_match.group(1))
                    metadata.tags = explicit_metadata.get("tags", [])
                    metadata.input_types = explicit_metadata.get("input_types", [])
                    metadata.output_types = explicit_metadata.get("output_types", [])
                    metadata.collaborates_with = explicit_metadata.get(
                        "collaborates_with", []
                    )
                    metadata.use_cases = explicit_metadata.get("use_cases", [])
                except json.JSONDecodeError:
                    pass

            # Infer tags from code content
            inferred_tags = self._infer_tags_from_code(code)
            metadata.tags.extend(inferred_tags)
            metadata.tags = list(set(metadata.tags))  # Remove duplicates

            # Estimate confidence based on code quality
            metadata.confidence_score = self._estimate_plugin_quality(code)

        except Exception as e:
            logger.error(f"❌ Failed to extract metadata from {plugin_path}: {e}")

        return metadata

    def _infer_tags_from_code(self, code: str) -> List[str]:
        """Infer tags from plugin code content"""
        tags = []
        code_lower = code.lower()

        # Check for common patterns
        if any(word in code_lower for word in ["file", "path", "directory"]):
            tags.append("file_management")

        if any(
            word in code_lower
            for word in ["plot", "chart", "graph", "matplotlib", "visualization"]
        ):
            tags.append("visualization")

        if any(word in code_lower for word in ["async", "asyncio", "threading"]):
            tags.append("async")

        if any(word in code_lower for word in ["http", "request", "api", "web"]):
            tags.append("web")

        if any(word in code_lower for word in ["database", "sql", "sqlite", "mongodb"]):
            tags.append("database")

        if any(word in code_lower for word in ["log", "monitor", "watch", "track"]):
            tags.append("monitoring")

        if any(word in code_lower for word in ["encrypt", "hash", "secure", "auth"]):
            tags.append("security")

        if any(
            word in code_lower for word in ["schedule", "cron", "timer", "interval"]
        ):
            tags.append("automation")

        return tags

    def _estimate_plugin_quality(self, code: str) -> float:
        """Estimate plugin quality/confidence score"""
        score = 0.5  # Base score

        # Positive indicators
        if "def " in code:
            score += 0.1
        if "class " in code:
            score += 0.1
        if '"""' in code or "'''" in code:
            score += 0.1  # Has docstrings
        if "try:" in code and "except" in code:
            score += 0.1  # Has error handling
        if "import " in code:
            score += 0.1  # Uses imports

        # Negative indicators
        if "TODO" in code or "FIXME" in code:
            score -= 0.1
        if len(code.split("\n")) < 10:
            score -= 0.1  # Very short

        return max(0.0, min(1.0, score))

    def discover_plugins_with_metadata(self) -> Dict[str, PluginMetadata]:
        """Discover all plugins and extract/update their metadata"""
        discovered = {}

        # Standard plugin directories
        plugin_dirs = [
            self.workspace_path / "Aetherra" / "plugins",
            self.workspace_path / "plugins",
            self.workspace_path / "src" / "plugins",
        ]

        for plugin_dir in plugin_dirs:
            if not plugin_dir.exists():
                continue

            for ext in ["*.py", "*.aether"]:
                for plugin_file in plugin_dir.glob(ext):
                    if plugin_file.name.startswith("__"):
                        continue

                    plugin_id = plugin_file.stem

                    # Use existing metadata or extract new
                    if plugin_id in self.plugin_metadata:
                        metadata = self.plugin_metadata[plugin_id]
                    else:
                        metadata = self.extract_metadata_from_code(plugin_file)
                        self.plugin_metadata[plugin_id] = metadata

                    discovered[plugin_id] = metadata

        logger.info(f"🔍 Discovered {len(discovered)} plugins with metadata")
        self.save_metadata()
        return discovered

    def search_by_tag(self, tag: str) -> List[PluginMetadata]:
        """Search plugins by tag"""
        results = []
        for metadata in self.plugin_metadata.values():
            if tag.lower() in [t.lower() for t in metadata.tags]:
                results.append(metadata)

        # Sort by confidence score
        results.sort(key=lambda x: x.confidence_score, reverse=True)
        return results

    def search_by_context(self, context_text: str) -> List[PluginMetadata]:
        """Search plugins by context/goal description"""
        context_lower = context_text.lower()
        scored_plugins = []

        for metadata in self.plugin_metadata.values():
            score = 0.0

            # Check description match
            if metadata.description:
                description_lower = metadata.description.lower()
                for word in context_lower.split():
                    if word in description_lower:
                        score += 0.3

            # Check tag relevance
            for tag in metadata.tags:
                if tag.lower() in context_lower:
                    score += 0.5

                # Check context patterns
                for pattern_name, keywords in self.context_patterns.items():
                    if tag.lower() == pattern_name and any(
                        kw in context_lower for kw in keywords
                    ):
                        score += 0.4

            # Check use cases
            for use_case in metadata.use_cases:
                if any(word in use_case.lower() for word in context_lower.split()):
                    score += 0.2

            # Factor in plugin quality and usage
            score *= metadata.confidence_score
            if metadata.success_rate > 0:
                score *= 0.5 + metadata.success_rate * 0.5

            if score > 0.1:  # Minimum relevance threshold
                scored_plugins.append((score, metadata))

        # Sort by score and return metadata
        scored_plugins.sort(key=lambda x: x[0], reverse=True)
        return [metadata for score, metadata in scored_plugins]

    def get_memory_context_suggestions(
        self, user_query: str = ""
    ) -> List[Tuple[PluginMetadata, str]]:
        """Get plugin suggestions based on memory context"""
        suggestions = []

        try:
            # If memory manager is available, analyze memory for patterns
            if self.memory_manager and hasattr(self.memory_manager, "search_memories"):
                # Search for similar past issues/goals
                memory_results = self.memory_manager.search_memories(
                    user_query, limit=5
                )

                for memory in memory_results:
                    # Analyze memory content for plugin opportunities
                    memory_text = (
                        memory.get("content", "") + " " + memory.get("context", "")
                    )
                    relevant_plugins = self.search_by_context(memory_text)

                    for plugin_metadata in relevant_plugins[:2]:  # Top 2 per memory
                        reason = f"Previously helpful for: {memory.get('context', 'similar situation')[:50]}"
                        suggestions.append((plugin_metadata, reason))

            # Also analyze current query directly
            current_suggestions = self.search_by_context(user_query)
            for plugin_metadata in current_suggestions[:3]:  # Top 3 for current query
                reason = "Relevant for current request"
                suggestions.append((plugin_metadata, reason))

            # Remove duplicates and sort by confidence
            seen_plugins = set()
            unique_suggestions = []
            for plugin_metadata, reason in suggestions:
                if plugin_metadata.plugin_id not in seen_plugins:
                    unique_suggestions.append((plugin_metadata, reason))
                    seen_plugins.add(plugin_metadata.plugin_id)

            # Sort by confidence score
            unique_suggestions.sort(key=lambda x: x[0].confidence_score, reverse=True)
            return unique_suggestions[:5]  # Top 5 suggestions

        except Exception as e:
            logger.error(f"❌ Failed to get memory context suggestions: {e}")
            return []

    def record_plugin_usage(self, plugin_id: str, success: bool, context: str = ""):
        """Record plugin usage for learning"""
        usage_record = {
            "plugin_id": plugin_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "context": context,
        }

        self.usage_history.append(usage_record)

        # Update plugin metadata
        if plugin_id in self.plugin_metadata:
            metadata = self.plugin_metadata[plugin_id]
            metadata.last_used = datetime.now()

            # Update success rate
            plugin_uses = [u for u in self.usage_history if u["plugin_id"] == plugin_id]
            if plugin_uses:
                successes = len([u for u in plugin_uses if u["success"]])
                metadata.success_rate = successes / len(plugin_uses)

        # Keep only recent history (last 1000 entries)
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]

        self.save_usage_history()
        self.save_metadata()

    def get_plugin_recommendations(
        self, goal_text: str, max_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """Get comprehensive plugin recommendations for a goal"""
        recommendations = []

        # Get context-based suggestions
        context_suggestions = self.search_by_context(goal_text)

        # Get memory-based suggestions
        memory_suggestions = self.get_memory_context_suggestions(goal_text)

        # Combine and score recommendations
        all_suggestions = {}

        # Add context suggestions
        for i, metadata in enumerate(context_suggestions[:max_recommendations]):
            score = 1.0 - (i * 0.1)  # Decreasing score by ranking
            all_suggestions[metadata.plugin_id] = {
                "metadata": metadata,
                "score": score,
                "reason": "Matches your request context",
                "type": "context_match",
            }

        # Add memory suggestions (higher weight)
        for metadata, reason in memory_suggestions:
            if metadata.plugin_id in all_suggestions:
                # Boost existing suggestion
                all_suggestions[metadata.plugin_id]["score"] += 0.3
                all_suggestions[metadata.plugin_id]["reason"] += f" + {reason}"
            else:
                all_suggestions[metadata.plugin_id] = {
                    "metadata": metadata,
                    "score": 0.8,  # High score for memory-based
                    "reason": reason,
                    "type": "memory_based",
                }

        # Sort by score and create final recommendations
        sorted_suggestions = sorted(
            all_suggestions.items(), key=lambda x: x[1]["score"], reverse=True
        )

        for plugin_id, suggestion in sorted_suggestions[:max_recommendations]:
            metadata = suggestion["metadata"]
            recommendations.append(
                {
                    "plugin_id": plugin_id,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "confidence": metadata.confidence_score,
                    "success_rate": metadata.success_rate,
                    "reason": suggestion["reason"],
                    "type": suggestion["type"],
                    "score": suggestion["score"],
                }
            )

        return recommendations

    def generate_plugin_chain_suggestions(self, goal_text: str) -> List[List[str]]:
        """Suggest chains of plugins that work well together"""
        chains = []

        # Get initial recommendations
        recommendations = self.get_plugin_recommendations(goal_text)

        # Look for collaboration patterns
        for rec in recommendations[:3]:  # Top 3 plugins
            plugin_id = rec["plugin_id"]
            if plugin_id in self.plugin_metadata:
                metadata = self.plugin_metadata[plugin_id]

                # Create chain with collaborating plugins
                chain = [plugin_id]
                for collaborator in metadata.collaborates_with:
                    if collaborator in self.plugin_metadata:
                        chain.append(collaborator)

                if len(chain) > 1:
                    chains.append(chain)

        return chains

    def generate_autocomplete_suggestions(self, partial_input: str) -> List[str]:
        """Generate autocomplete suggestions for plugin names and actions"""
        suggestions = []
        partial_lower = partial_input.lower()

        # Plugin name suggestions
        for plugin_id in self.plugin_metadata:
            if plugin_id.lower().startswith(partial_lower):
                suggestions.append(plugin_id)

        # Tag-based suggestions
        for metadata in self.plugin_metadata.values():
            for tag in metadata.tags:
                if tag.lower().startswith(partial_lower):
                    suggestions.append(f"{tag} (plugin type)")

        # Use case suggestions
        for metadata in self.plugin_metadata.values():
            for use_case in metadata.use_cases:
                if partial_lower in use_case.lower():
                    suggestions.append(f"{use_case} → {metadata.plugin_id}")

        return list(set(suggestions))[:10]  # Top 10 unique suggestions


# Example usage and testing
if __name__ == "__main__":

    def main():
        print("🔗 Memory-Linked Plugin Discovery Test")
        print("=" * 40)

        # Initialize the discovery system
        workspace_path = Path(__file__).parent.parent
        discovery = MemoryLinkedPluginDiscovery(str(workspace_path))

        # Discover plugins with metadata
        plugins = discovery.discover_plugins_with_metadata()
        print(f"📦 Discovered {len(plugins)} plugins")

        # Test search by tag
        file_plugins = discovery.search_by_tag("file_management")
        print(f"📁 File management plugins: {len(file_plugins)}")

        # Test context search
        context_results = discovery.search_by_context("I need to visualize some data")
        print(f"📊 Visualization context results: {len(context_results)}")

        # Test recommendations
        recommendations = discovery.get_plugin_recommendations(
            "I want to organize my files"
        )
        print(f"💡 Recommendations: {len(recommendations)}")
        for rec in recommendations[:3]:
            print(f"   - {rec['plugin_id']}: {rec['reason']}")

        print("🎉 Memory-linked discovery test complete!")

    main()
