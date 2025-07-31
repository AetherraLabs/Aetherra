"""
Phase 4: Semantic Plugin Discovery Enhancement
==============================================

Enhanced semantic plugin discovery system that understands plugin capabilities
and suggests them based on user goals using natural language processing.
"""

import hashlib
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SemanticPluginIndex:
    """
    Advanced plugin indexing system with semantic understanding.
    """

    def __init__(self, db_path: str = "semantic_plugin_index.db"):
        self.db_path = Path(db_path)
        self.connection = None  # Type: sqlite3.Connection
        self.embeddings_cache = {}
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the semantic plugin index database."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS plugin_metadata (
                plugin_name TEXT PRIMARY KEY,
                description TEXT,
                natural_summary TEXT,
                capabilities TEXT,  -- JSON array
                tags TEXT,          -- JSON array
                goals TEXT,         -- JSON array
                category TEXT,
                author TEXT,
                version TEXT,
                file_path TEXT,
                last_updated TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                avg_execution_time REAL DEFAULT 0.0,
                semantic_hash TEXT
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS goal_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_pattern TEXT,
                plugin_name TEXT,
                relevance_score REAL,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                FOREIGN KEY (plugin_name) REFERENCES plugin_metadata (plugin_name)
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS plugin_relationships (
                plugin_a TEXT,
                plugin_b TEXT,
                relationship_type TEXT,  -- 'collaborates', 'depends', 'conflicts'
                strength REAL DEFAULT 1.0,
                FOREIGN KEY (plugin_a) REFERENCES plugin_metadata (plugin_name),
                FOREIGN KEY (plugin_b) REFERENCES plugin_metadata (plugin_name)
            )
        """)

        self.connection.commit()

    def index_plugin(self, plugin_info: Dict[str, Any]) -> bool:
        """
        Index a plugin with semantic understanding.

        Args:
            plugin_info: Plugin information dictionary

        Returns:
            bool: Success status
        """
        try:
            # Generate natural language summary
            natural_summary = self._generate_plugin_summary(plugin_info)

            # Extract semantic information
            capabilities = plugin_info.get("capabilities", [])
            goals = self._extract_goals_from_description(
                plugin_info.get("description", "") + " " + natural_summary
            )

            # Create semantic hash for change detection
            semantic_content = (
                f"{plugin_info.get('description', '')}{capabilities}{goals}"
            )
            semantic_hash = hashlib.md5(semantic_content.encode()).hexdigest()

            # Store in database
            self.connection.execute(
                """
                INSERT OR REPLACE INTO plugin_metadata
                (plugin_name, description, natural_summary, capabilities, tags, goals,
                 category, author, version, file_path, last_updated, semantic_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    plugin_info.get("name", ""),
                    plugin_info.get("description", ""),
                    natural_summary,
                    json.dumps(capabilities),
                    json.dumps(plugin_info.get("tags", [])),
                    json.dumps(goals),
                    plugin_info.get("category", "general"),
                    plugin_info.get("author", ""),
                    plugin_info.get("version", "1.0.0"),
                    plugin_info.get("file_path", ""),
                    datetime.now().isoformat(),
                    semantic_hash,
                ),
            )

            # Index goal mappings
            self._index_goal_mappings(plugin_info.get("name", ""), goals)

            self.connection.commit()
            return True

        except Exception as e:
            print(f"Error indexing plugin {plugin_info.get('name', 'unknown')}: {e}")
            return False

    def _generate_plugin_summary(self, plugin_info: Dict[str, Any]) -> str:
        """Generate a natural language summary of what the plugin does."""
        name = plugin_info.get("name", "")
        description = plugin_info.get("description", "")
        capabilities = plugin_info.get("capabilities", [])
        category = plugin_info.get("category", "")

        # Create natural language summary
        summary_parts = []

        if category:
            summary_parts.append(f"This is a {category} plugin")

        if description:
            summary_parts.append(f"that {description.lower()}")

        if capabilities:
            cap_text = ", ".join(capabilities)
            summary_parts.append(f"It can {cap_text}")

        summary = ". ".join(summary_parts) + "."
        return (
            summary
            if summary != "."
            else f"Plugin {name} provides extended functionality."
        )

    def _extract_goals_from_description(self, text: str) -> List[str]:
        """Extract potential user goals from plugin description."""
        goal_patterns = [
            r"analyze\s+(\w+)",
            r"optimize\s+(\w+)",
            r"generate\s+(\w+)",
            r"test\s+(\w+)",
            r"debug\s+(\w+)",
            r"monitor\s+(\w+)",
            r"manage\s+(\w+)",
            r"create\s+(\w+)",
            r"process\s+(\w+)",
            r"validate\s+(\w+)",
        ]

        goals = []
        text_lower = text.lower()

        for pattern in goal_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                goals.append(f"{pattern.split('\\')[0]} {match}")

        # Add common goals based on keywords
        keyword_goals = {
            "performance": [
                "analyze performance",
                "optimize performance",
                "monitor performance",
            ],
            "test": ["run tests", "generate tests", "validate code"],
            "debug": ["debug code", "find errors", "troubleshoot"],
            "code": ["generate code", "refactor code", "analyze code"],
            "data": ["process data", "analyze data", "transform data"],
            "file": ["manage files", "process files", "organize files"],
        }

        for keyword, related_goals in keyword_goals.items():
            if keyword in text_lower:
                goals.extend(related_goals)

        return list(set(goals))  # Remove duplicates

    def _index_goal_mappings(self, plugin_name: str, goals: List[str]):
        """Index goal-to-plugin mappings for fast lookup."""
        for goal in goals:
            # Calculate relevance score based on goal specificity
            relevance_score = min(1.0, len(goal.split()) / 3.0)

            self.connection.execute(
                """
                INSERT OR REPLACE INTO goal_mappings
                (goal_pattern, plugin_name, relevance_score)
                VALUES (?, ?, ?)
            """,
                (goal, plugin_name, relevance_score),
            )

    def query_plugins_by_goal(
        self, user_goal: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find plugins that match a user goal using semantic understanding.

        Args:
            user_goal: Natural language description of what user wants to do
            limit: Maximum number of plugins to return

        Returns:
            List of matching plugins with relevance scores
        """
        user_goal_lower = user_goal.lower()

        # Direct goal matching
        cursor = self.connection.execute(
            """
            SELECT pm.*, gm.relevance_score, gm.usage_count as goal_usage
            FROM plugin_metadata pm
            JOIN goal_mappings gm ON pm.plugin_name = gm.plugin_name
            WHERE gm.goal_pattern LIKE ? OR gm.goal_pattern LIKE ?
            ORDER BY gm.relevance_score DESC, pm.success_rate DESC, pm.usage_count DESC
            LIMIT ?
        """,
            (f"%{user_goal_lower}%", f"%{user_goal_lower.split()[0]}%", limit),
        )

        results = []
        for row in cursor.fetchall():
            plugin_data = {
                "plugin_name": row[0],
                "description": row[1],
                "natural_summary": row[2],
                "capabilities": json.loads(row[3]) if row[3] else [],
                "tags": json.loads(row[4]) if row[4] else [],
                "goals": json.loads(row[5]) if row[5] else [],
                "category": row[6],
                "relevance_score": row[13],
                "usage_count": row[10],
                "success_rate": row[11],
            }
            results.append(plugin_data)

        # If no direct matches, try fuzzy matching
        if not results:
            results = self._fuzzy_goal_matching(user_goal_lower, limit)

        return results

    def _fuzzy_goal_matching(self, user_goal: str, limit: int) -> List[Dict[str, Any]]:
        """Perform fuzzy matching when direct goal matching fails."""
        # Extract keywords from user goal
        keywords = [word for word in user_goal.split() if len(word) > 2]

        if not keywords:
            return []

        # Search in descriptions and capabilities
        keyword_conditions = []
        params = []

        for keyword in keywords:
            keyword_conditions.extend(
                [
                    "pm.description LIKE ?",
                    "pm.natural_summary LIKE ?",
                    "pm.capabilities LIKE ?",
                    "pm.tags LIKE ?",
                ]
            )
            params.extend([f"%{keyword}%"] * 4)

        where_clause = " OR ".join(keyword_conditions)
        params.append(limit)

        cursor = self.connection.execute(
            f"""
            SELECT pm.*, 0.5 as relevance_score
            FROM plugin_metadata pm
            WHERE {where_clause}
            ORDER BY pm.success_rate DESC, pm.usage_count DESC
            LIMIT ?
        """,
            params,
        )

        results = []
        for row in cursor.fetchall():
            plugin_data = {
                "plugin_name": row[0],
                "description": row[1],
                "natural_summary": row[2],
                "capabilities": json.loads(row[3]) if row[3] else [],
                "tags": json.loads(row[4]) if row[4] else [],
                "goals": json.loads(row[5]) if row[5] else [],
                "category": row[6],
                "relevance_score": 0.5,  # Lower score for fuzzy matches
                "usage_count": row[10],
                "success_rate": row[11],
            }
            results.append(plugin_data)

        return results

    def update_plugin_metrics(
        self, plugin_name: str, success: bool, execution_time: float
    ):
        """Update plugin performance metrics."""
        cursor = self.connection.execute(
            """
            SELECT usage_count, success_rate, avg_execution_time
            FROM plugin_metadata WHERE plugin_name = ?
        """,
            (plugin_name,),
        )

        row = cursor.fetchone()
        if not row:
            return

        usage_count, success_rate, avg_execution_time = row

        # Update metrics
        new_usage_count = usage_count + 1
        new_success_rate = (
            (success_rate * usage_count) + (1.0 if success else 0.0)
        ) / new_usage_count
        new_avg_time = (
            (avg_execution_time * usage_count) + execution_time
        ) / new_usage_count

        self.connection.execute(
            """
            UPDATE plugin_metadata
            SET usage_count = ?, success_rate = ?, avg_execution_time = ?
            WHERE plugin_name = ?
        """,
            (new_usage_count, new_success_rate, new_avg_time, plugin_name),
        )

        self.connection.commit()

    def get_plugin_suggestions_text(self, user_goal: str) -> str:
        """
        Generate human-readable plugin suggestions for a user goal.

        Args:
            user_goal: What the user wants to accomplish

        Returns:
            Human-readable suggestion text
        """
        plugins = self.query_plugins_by_goal(user_goal)

        if not plugins:
            return f"I couldn't find any plugins specifically for '{user_goal}'. Would you like me to search for related capabilities?"

        if len(plugins) == 1:
            plugin = plugins[0]
            return f"I found 1 plugin that can help with '{user_goal}': **{plugin['plugin_name']}** - {plugin['natural_summary']} Want to activate it?"

        # Multiple plugins
        plugin_list = []
        for i, plugin in enumerate(plugins[:3], 1):  # Show top 3
            score_text = f"({plugin['relevance_score']:.1f} relevance)"
            plugin_list.append(
                f"{i}. **{plugin['plugin_name']}** - {plugin['natural_summary']} {score_text}"
            )

        suggestion_text = (
            f"I found {len(plugins)} plugins that can help with '{user_goal}':\n\n"
        )
        suggestion_text += "\n".join(plugin_list)

        if len(plugins) > 3:
            suggestion_text += (
                f"\n\n...and {len(plugins) - 3} more. Which one would you like to use?"
            )
        else:
            suggestion_text += "\n\nWhich one would you like to activate?"

        return suggestion_text

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()


class SemanticPluginDiscovery:
    """
    Main interface for semantic plugin discovery.
    """

    def __init__(self, plugin_manager, plugins_dir: str = "plugins"):
        self.plugin_manager = plugin_manager
        self.plugins_dir = Path(plugins_dir)
        self.semantic_index = SemanticPluginIndex()
        self.goal_history = []

    def discover_and_index_plugins(self) -> int:
        """
        Discover all plugins and index them semantically.

        Returns:
            Number of plugins indexed
        """
        indexed_count = 0

        # Get all plugins from the plugin manager
        if hasattr(self.plugin_manager, "plugin_info"):
            for plugin_name, plugin_info in self.plugin_manager.plugin_info.items():
                plugin_dict = {
                    "name": plugin_info.name,
                    "description": plugin_info.description,
                    "capabilities": plugin_info.capabilities,
                    "category": plugin_info.category,
                    "author": plugin_info.author,
                    "version": plugin_info.version,
                    "file_path": plugin_info.file_path,
                    "tags": getattr(plugin_info, "tags", []),
                }

                if self.semantic_index.index_plugin(plugin_dict):
                    indexed_count += 1

        return indexed_count

    def suggest_plugins_for_goal(self, user_goal: str) -> str:
        """
        Suggest plugins for a user goal and return human-readable text.

        Args:
            user_goal: What the user wants to accomplish

        Returns:
            Human-readable plugin suggestions
        """
        # Track goal for learning
        self.goal_history.append(
            {"goal": user_goal, "timestamp": datetime.now().isoformat()}
        )

        return self.semantic_index.get_plugin_suggestions_text(user_goal)

    async def find_relevant_plugins(
        self, user_goal: str, max_results: int = 5
    ) -> List[str]:
        """
        Find relevant plugin names for a user goal.

        Args:
            user_goal: What the user wants to accomplish
            max_results: Maximum number of plugins to return

        Returns:
            List of plugin names that match the goal
        """
        plugins = self.semantic_index.query_plugins_by_goal(user_goal, max_results)
        return [plugin["plugin_name"] for plugin in plugins]

    def update_plugin_performance(
        self, plugin_name: str, success: bool, execution_time: float
    ):
        """Update plugin performance metrics after execution."""
        self.semantic_index.update_plugin_metrics(plugin_name, success, execution_time)

    def get_goal_history(self) -> List[Dict[str, Any]]:
        """Get recent goal history for learning purposes."""
        return self.goal_history[-10:]  # Return last 10 goals
