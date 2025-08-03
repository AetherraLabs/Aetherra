"""
Phase 4: Plugin State Memory System
===================================

Advanced plugin state persistence that integrates with Lyrixa's cognitive framework.
Allows plugins to maintain context, learn from interactions, and evolve over time.
"""

import hashlib
import json
import pickle
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class PluginStateMemory:
    """
    Persistent state management for plugins with cognitive integration.
    """

    def __init__(self, db_path: str = "plugin_state_memory.db"):
        self.db_path = Path(db_path)
        self.connection: sqlite3.Connection = sqlite3.connect(self.db_path)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.session_id = self._generate_session_id()
        self._initialize_database()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def _initialize_database(self):
        """Initialize the plugin state memory database."""
        # Connection is already established in __init__

        # Plugin state storage
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS plugin_states (
                plugin_name TEXT,
                state_key TEXT,
                state_value BLOB,
                state_type TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                session_id TEXT,
                access_count INTEGER DEFAULT 0,
                PRIMARY KEY (plugin_name, state_key)
            )
        """)

        # Plugin conversation context
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS plugin_contexts (
                plugin_name TEXT,
                context_id TEXT,
                conversation_history TEXT,  -- JSON
                user_preferences TEXT,     -- JSON
                success_patterns TEXT,     -- JSON
                failure_patterns TEXT,     -- JSON
                learning_notes TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                session_count INTEGER DEFAULT 1,
                PRIMARY KEY (plugin_name, context_id)
            )
        """)

        # Plugin behavioral evolution
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS plugin_evolution (
                plugin_name TEXT,
                behavior_hash TEXT,
                adaptation_data TEXT,      -- JSON
                performance_metrics TEXT,  -- JSON
                user_feedback_score REAL DEFAULT 0.0,
                confidence_level REAL DEFAULT 0.5,
                created_at TIMESTAMP,
                last_used TIMESTAMP,
                usage_frequency INTEGER DEFAULT 0,
                PRIMARY KEY (plugin_name, behavior_hash)
            )
        """)

        # Cross-plugin state sharing
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS shared_states (
                state_namespace TEXT,
                state_key TEXT,
                state_value BLOB,
                state_type TEXT,
                owner_plugin TEXT,
                access_permissions TEXT,   -- JSON list of allowed plugins
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                access_log TEXT,           -- JSON access history
                PRIMARY KEY (state_namespace, state_key)
            )
        """)

        self.connection.commit()

    def set_plugin_state(
        self,
        plugin_name: str,
        state_key: str,
        state_value: Any,
        state_type: str = "json",
    ) -> bool:
        """
        Store plugin state with type awareness.

        Args:
            plugin_name: Name of the plugin
            state_key: Key for the state value
            state_value: Value to store
            state_type: Type of value ('json', 'pickle', 'text')

        Returns:
            True if successful
        """
        try:
            # Serialize based on type
            if state_type == "json":
                serialized_value = json.dumps(state_value).encode()
            elif state_type == "pickle":
                serialized_value = pickle.dumps(state_value)
            elif state_type == "text":
                serialized_value = str(state_value).encode()
            else:
                raise ValueError(f"Unsupported state type: {state_type}")

            now = datetime.now()

            # Check if state exists
            cursor = self.connection.execute(
                """
                SELECT access_count FROM plugin_states
                WHERE plugin_name = ? AND state_key = ?
            """,
                (plugin_name, state_key),
            )

            existing = cursor.fetchone()

            if existing:
                # Update existing state
                self.connection.execute(
                    """
                    UPDATE plugin_states
                    SET state_value = ?, state_type = ?, updated_at = ?,
                        session_id = ?, access_count = access_count + 1
                    WHERE plugin_name = ? AND state_key = ?
                """,
                    (
                        serialized_value,
                        state_type,
                        now,
                        self.session_id,
                        plugin_name,
                        state_key,
                    ),
                )
            else:
                # Insert new state
                self.connection.execute(
                    """
                    INSERT INTO plugin_states
                    (plugin_name, state_key, state_value, state_type,
                     created_at, updated_at, session_id, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                    (
                        plugin_name,
                        state_key,
                        serialized_value,
                        state_type,
                        now,
                        now,
                        self.session_id,
                    ),
                )

            self.connection.commit()

            # Update cache
            if plugin_name not in self.memory_cache:
                self.memory_cache[plugin_name] = {}
            self.memory_cache[plugin_name][state_key] = state_value

            return True

        except Exception as e:
            print(f"[WARN] Error setting plugin state: {e}")
            return False

    def get_plugin_state(
        self, plugin_name: str, state_key: str, default: Any = None
    ) -> Any:
        """
        Retrieve plugin state with caching.

        Args:
            plugin_name: Name of the plugin
            state_key: Key for the state value
            default: Default value if not found

        Returns:
            The stored value or default
        """
        # Check cache first
        if (
            plugin_name in self.memory_cache
            and state_key in self.memory_cache[plugin_name]
        ):
            return self.memory_cache[plugin_name][state_key]

        try:
            cursor = self.connection.execute(
                """
                SELECT state_value, state_type FROM plugin_states
                WHERE plugin_name = ? AND state_key = ?
            """,
                (plugin_name, state_key),
            )

            row = cursor.fetchone()
            if not row:
                return default

            serialized_value, state_type = row

            # Deserialize based on type
            if state_type == "json":
                value = json.loads(serialized_value.decode())
            elif state_type == "pickle":
                value = pickle.loads(serialized_value)
            elif state_type == "text":
                value = serialized_value.decode()
            else:
                return default

            # Update cache
            if plugin_name not in self.memory_cache:
                self.memory_cache[plugin_name] = {}
            self.memory_cache[plugin_name][state_key] = value

            # Update access count
            self.connection.execute(
                """
                UPDATE plugin_states SET access_count = access_count + 1
                WHERE plugin_name = ? AND state_key = ?
            """,
                (plugin_name, state_key),
            )
            self.connection.commit()

            return value

        except Exception as e:
            print(f"[WARN] Error getting plugin state: {e}")
            return default

    def delete_plugin_state(
        self, plugin_name: str, state_key: Optional[str] = None
    ) -> bool:
        """
        Delete plugin state(s).

        Args:
            plugin_name: Name of the plugin
            state_key: Specific key to delete, or None to delete all plugin state

        Returns:
            True if successful
        """
        try:
            if state_key:
                self.connection.execute(
                    """
                    DELETE FROM plugin_states
                    WHERE plugin_name = ? AND state_key = ?
                """,
                    (plugin_name, state_key),
                )

                # Remove from cache
                if (
                    plugin_name in self.memory_cache
                    and state_key in self.memory_cache[plugin_name]
                ):
                    del self.memory_cache[plugin_name][state_key]
            else:
                self.connection.execute(
                    """
                    DELETE FROM plugin_states WHERE plugin_name = ?
                """,
                    (plugin_name,),
                )

                # Clear plugin cache
                if plugin_name in self.memory_cache:
                    del self.memory_cache[plugin_name]

            self.connection.commit()
            return True

        except Exception as e:
            print(f"[WARN] Error deleting plugin state: {e}")
            return False

    def get_plugin_context(
        self, plugin_name: str, context_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Get plugin conversation context and learning data.

        Args:
            plugin_name: Name of the plugin
            context_id: Context identifier (e.g., user_id or conversation_id)

        Returns:
            Context dictionary with conversation history and patterns
        """
        try:
            cursor = self.connection.execute(
                """
                SELECT conversation_history, user_preferences, success_patterns,
                       failure_patterns, learning_notes, session_count
                FROM plugin_contexts
                WHERE plugin_name = ? AND context_id = ?
            """,
                (plugin_name, context_id),
            )

            row = cursor.fetchone()
            if not row:
                return {
                    "conversation_history": [],
                    "user_preferences": {},
                    "success_patterns": [],
                    "failure_patterns": [],
                    "learning_notes": "",
                    "session_count": 0,
                }

            return {
                "conversation_history": json.loads(row[0]) if row[0] else [],
                "user_preferences": json.loads(row[1]) if row[1] else {},
                "success_patterns": json.loads(row[2]) if row[2] else [],
                "failure_patterns": json.loads(row[3]) if row[3] else [],
                "learning_notes": row[4] or "",
                "session_count": row[5] or 0,
            }

        except Exception as e:
            print(f"[WARN] Error getting plugin context: {e}")
            return {}

    def update_plugin_context(
        self, plugin_name: str, context_id: str, context_data: Dict[str, Any]
    ) -> bool:
        """
        Update plugin conversation context and learning data.

        Args:
            plugin_name: Name of the plugin
            context_id: Context identifier
            context_data: Context data to update

        Returns:
            True if successful
        """
        try:
            now = datetime.now()

            # Check if context exists
            cursor = self.connection.execute(
                """
                SELECT session_count FROM plugin_contexts
                WHERE plugin_name = ? AND context_id = ?
            """,
                (plugin_name, context_id),
            )

            existing = cursor.fetchone()

            if existing:
                # Update existing context
                self.connection.execute(
                    """
                    UPDATE plugin_contexts
                    SET conversation_history = ?, user_preferences = ?,
                        success_patterns = ?, failure_patterns = ?,
                        learning_notes = ?, updated_at = ?,
                        session_count = session_count + 1
                    WHERE plugin_name = ? AND context_id = ?
                """,
                    (
                        json.dumps(context_data.get("conversation_history", [])),
                        json.dumps(context_data.get("user_preferences", {})),
                        json.dumps(context_data.get("success_patterns", [])),
                        json.dumps(context_data.get("failure_patterns", [])),
                        context_data.get("learning_notes", ""),
                        now,
                        plugin_name,
                        context_id,
                    ),
                )
            else:
                # Insert new context
                self.connection.execute(
                    """
                    INSERT INTO plugin_contexts
                    (plugin_name, context_id, conversation_history, user_preferences,
                     success_patterns, failure_patterns, learning_notes,
                     created_at, updated_at, session_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                    (
                        plugin_name,
                        context_id,
                        json.dumps(context_data.get("conversation_history", [])),
                        json.dumps(context_data.get("user_preferences", {})),
                        json.dumps(context_data.get("success_patterns", [])),
                        json.dumps(context_data.get("failure_patterns", [])),
                        context_data.get("learning_notes", ""),
                        now,
                        now,
                    ),
                )

            self.connection.commit()
            return True

        except Exception as e:
            print(f"[WARN] Error updating plugin context: {e}")
            return False

    def set_shared_state(
        self,
        namespace: str,
        state_key: str,
        state_value: Any,
        owner_plugin: str,
        allowed_plugins: Optional[List[str]] = None,
        state_type: str = "json",
    ) -> bool:
        """
        Set shared state that can be accessed by multiple plugins.

        Args:
            namespace: Namespace for the shared state
            state_key: Key for the state
            state_value: Value to store
            owner_plugin: Plugin that owns this state
            allowed_plugins: List of plugins allowed to access this state
            state_type: Type of the state value

        Returns:
            True if successful
        """
        try:
            # Serialize value
            if state_type == "json":
                serialized_value = json.dumps(state_value).encode()
            elif state_type == "pickle":
                serialized_value = pickle.dumps(state_value)
            elif state_type == "text":
                serialized_value = str(state_value).encode()
            else:
                raise ValueError(f"Unsupported state type: {state_type}")

            now = datetime.now()
            permissions = json.dumps(allowed_plugins or [])
            access_log = json.dumps(
                [
                    {
                        "action": "created",
                        "plugin": owner_plugin,
                        "timestamp": now.isoformat(),
                    }
                ]
            )

            self.connection.execute(
                """
                INSERT OR REPLACE INTO shared_states
                (state_namespace, state_key, state_value, state_type,
                 owner_plugin, access_permissions, created_at, updated_at, access_log)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    namespace,
                    state_key,
                    serialized_value,
                    state_type,
                    owner_plugin,
                    permissions,
                    now,
                    now,
                    access_log,
                ),
            )

            self.connection.commit()
            return True

        except Exception as e:
            print(f"[WARN] Error setting shared state: {e}")
            return False

    def get_shared_state(
        self,
        namespace: str,
        state_key: str,
        requesting_plugin: str,
        default: Any = None,
    ) -> Any:
        """
        Get shared state with permission checking.

        Args:
            namespace: Namespace for the shared state
            state_key: Key for the state
            requesting_plugin: Plugin requesting access
            default: Default value if not found or access denied

        Returns:
            The shared state value or default
        """
        try:
            cursor = self.connection.execute(
                """
                SELECT state_value, state_type, owner_plugin, access_permissions, access_log
                FROM shared_states
                WHERE state_namespace = ? AND state_key = ?
            """,
                (namespace, state_key),
            )

            row = cursor.fetchone()
            if not row:
                return default

            state_value, state_type, owner_plugin, permissions, access_log = row

            # Check permissions
            allowed_plugins = json.loads(permissions)
            if (
                requesting_plugin != owner_plugin
                and allowed_plugins
                and requesting_plugin not in allowed_plugins
            ):
                print(
                    f"[WARN] Plugin {requesting_plugin} denied access to shared state {namespace}.{state_key}"
                )
                return default

            # Deserialize value
            if state_type == "json":
                value = json.loads(state_value.decode())
            elif state_type == "pickle":
                value = pickle.loads(state_value)
            elif state_type == "text":
                value = state_value.decode()
            else:
                return default

            # Update access log
            access_history = json.loads(access_log)
            access_history.append(
                {
                    "action": "accessed",
                    "plugin": requesting_plugin,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Keep only last 50 access entries
            if len(access_history) > 50:
                access_history = access_history[-50:]

            self.connection.execute(
                """
                UPDATE shared_states SET access_log = ?
                WHERE state_namespace = ? AND state_key = ?
            """,
                (json.dumps(access_history), namespace, state_key),
            )
            self.connection.commit()

            return value

        except Exception as e:
            print(f"[WARN] Error getting shared state: {e}")
            return default

    def cleanup_old_states(self, days_old: int = 30) -> int:
        """
        Clean up old states to prevent database bloat.

        Args:
            days_old: Remove states older than this many days

        Returns:
            Number of states removed
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)

            cursor = self.connection.execute(
                """
                DELETE FROM plugin_states
                WHERE updated_at < ? AND access_count = 0
            """,
                (cutoff_date,),
            )

            removed_count = cursor.rowcount

            self.connection.execute(
                """
                DELETE FROM plugin_contexts
                WHERE updated_at < ? AND session_count <= 1
            """,
                (cutoff_date,),
            )

            removed_count += cursor.rowcount

            self.connection.commit()
            return removed_count

        except Exception as e:
            print(f"[WARN] Error cleaning up old states: {e}")
            return 0

    def get_plugin_memory_stats(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get memory usage statistics for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Statistics dictionary
        """
        try:
            # State count and total size
            cursor = self.connection.execute(
                """
                SELECT COUNT(*), SUM(LENGTH(state_value)), MAX(updated_at)
                FROM plugin_states WHERE plugin_name = ?
            """,
                (plugin_name,),
            )

            state_stats = cursor.fetchone() or (0, 0, None)

            # Context information
            cursor = self.connection.execute(
                """
                SELECT COUNT(*), MAX(session_count)
                FROM plugin_contexts WHERE plugin_name = ?
            """,
                (plugin_name,),
            )

            context_stats = cursor.fetchone() or (0, 0)

            return {
                "state_count": state_stats[0],
                "total_state_size_bytes": state_stats[1] or 0,
                "last_state_update": state_stats[2],
                "context_count": context_stats[0],
                "max_sessions": context_stats[1] or 0,
                "cached_states": len(self.memory_cache.get(plugin_name, {})),
            }

        except Exception as e:
            print(f"[WARN] Error getting memory stats: {e}")
            return {}

    def close(self):
        """Close database connection and clear cache."""
        if self.connection:
            self.connection.close()
        self.memory_cache.clear()


class CognitivePluginMemory:
    """
    Higher-level memory interface that integrates with Lyrixa's cognitive architecture.
    """

    def __init__(self, state_memory: PluginStateMemory):
        self.state_memory = state_memory
        self.conversation_context = {}
        self.learning_buffer = {}

    def remember_interaction(
        self,
        plugin_name: str,
        user_input: str,
        plugin_response: str,
        success: bool,
        user_feedback: Optional[str] = None,
    ):
        """
        Remember an interaction for learning purposes.

        Args:
            plugin_name: Name of the plugin
            user_input: What the user requested
            plugin_response: How the plugin responded
            success: Whether the interaction was successful
            user_feedback: Optional user feedback
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "plugin_response": plugin_response,
            "success": success,
            "user_feedback": user_feedback,
            "session_id": self.state_memory.session_id,
        }

        # Add to conversation context
        if plugin_name not in self.conversation_context:
            self.conversation_context[plugin_name] = []

        self.conversation_context[plugin_name].append(interaction)

        # Keep only last 20 interactions in memory
        if len(self.conversation_context[plugin_name]) > 20:
            self.conversation_context[plugin_name] = self.conversation_context[
                plugin_name
            ][-20:]

        # Update persistent context
        context_data = self.state_memory.get_plugin_context(plugin_name)
        context_data["conversation_history"].append(interaction)

        # Keep only last 100 interactions in persistent storage
        if len(context_data["conversation_history"]) > 100:
            context_data["conversation_history"] = context_data["conversation_history"][
                -100:
            ]

        # Update success/failure patterns
        if success:
            pattern = {
                "input_pattern": user_input[:100],  # First 100 chars
                "response_pattern": plugin_response[:100],
                "timestamp": interaction["timestamp"],
            }
            context_data["success_patterns"].append(pattern)

            # Keep only last 50 success patterns
            if len(context_data["success_patterns"]) > 50:
                context_data["success_patterns"] = context_data["success_patterns"][
                    -50:
                ]
        else:
            pattern = {
                "input_pattern": user_input[:100],
                "error_info": plugin_response[:100],
                "timestamp": interaction["timestamp"],
            }
            context_data["failure_patterns"].append(pattern)

            # Keep only last 30 failure patterns
            if len(context_data["failure_patterns"]) > 30:
                context_data["failure_patterns"] = context_data["failure_patterns"][
                    -30:
                ]

        self.state_memory.update_plugin_context(plugin_name, "default", context_data)

    def get_plugin_insights(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get insights about plugin usage and performance.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Insights dictionary
        """
        context_data = self.state_memory.get_plugin_context(plugin_name)
        memory_stats = self.state_memory.get_plugin_memory_stats(plugin_name)

        # Calculate success rate
        total_interactions = len(context_data["conversation_history"])
        successful_interactions = sum(
            1 for i in context_data["conversation_history"] if i["success"]
        )
        success_rate = (
            successful_interactions / total_interactions
            if total_interactions > 0
            else 0.0
        )

        # Find common success patterns
        success_inputs = [
            p["input_pattern"] for p in context_data["success_patterns"][-10:]
        ]
        failure_inputs = [
            p["input_pattern"] for p in context_data["failure_patterns"][-10:]
        ]

        return {
            "total_interactions": total_interactions,
            "success_rate": success_rate,
            "recent_success_patterns": success_inputs,
            "recent_failure_patterns": failure_inputs,
            "session_count": context_data["session_count"],
            "memory_usage": memory_stats,
            "learning_notes": context_data["learning_notes"],
            "user_preferences": context_data["user_preferences"],
        }

    def suggest_optimization(self, plugin_name: str) -> List[str]:
        """
        Suggest optimizations based on plugin usage patterns.

        Args:
            plugin_name: Name of the plugin

        Returns:
            List of optimization suggestions
        """
        insights = self.get_plugin_insights(plugin_name)
        suggestions = []

        if insights["success_rate"] < 0.7:
            suggestions.append(
                "Consider reviewing error patterns and improving error handling"
            )

        if insights["total_interactions"] > 100 and insights["session_count"] < 5:
            suggestions.append("Plugin may need better session state management")

        if len(insights["recent_failure_patterns"]) > len(
            insights["recent_success_patterns"]
        ):
            suggestions.append(
                "Recent performance decline detected - review recent changes"
            )

        memory_size = insights["memory_usage"].get("total_state_size_bytes", 0)
        if memory_size > 1024 * 1024:  # 1MB
            suggestions.append(
                "Consider implementing state cleanup to reduce memory usage"
            )

        return suggestions
