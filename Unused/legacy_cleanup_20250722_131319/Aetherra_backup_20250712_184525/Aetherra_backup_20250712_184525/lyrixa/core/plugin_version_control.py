#!/usr/bin/env python3
"""
🔄 LYRIXA PLUGIN VERSION CONTROL & ROLLBACK SYSTEM
=================================================

Advanced version control system for Lyrixa plugins with:
- Automatic timestamped snapshots
- Rollback functionality with validation
- Enhanced diff viewer with color-coded output
- GUI integration for version history
- Conversational integration with Lyrixa

This system ensures plugin safety and enables confident experimentation.
"""

import ast
import difflib
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .memory import LyrixaMemorySystem


class PluginSnapshot:
    """Represents a plugin snapshot with metadata"""

    def __init__(
        self,
        plugin_name: str,
        timestamp: str,
        file_path: str,
        confidence_score: float = 0.0,
        metadata: Optional[Dict] = None,
    ):
        self.plugin_name = plugin_name
        self.timestamp = timestamp
        self.file_path = file_path
        self.confidence_score = confidence_score
        self.metadata = metadata or {}
        self.size = os.path.getsize(file_path) if os.path.exists(file_path) else 0


class PluginVersionControl:
    """
    Comprehensive plugin version control and rollback system

    Features:
    - Automatic snapshot creation on modifications
    - Syntax validation before operations
    - Rollback with safety checks
    - Enhanced diff generation
    - Integration with Lyrixa memory system
    """

    def __init__(
        self,
        history_dir: str = ".plugin_history",
        memory_system: Optional[LyrixaMemorySystem] = None,
    ):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.memory_system = memory_system
        self.db_path = self.history_dir / "version_control.db"

        # Initialize metadata database
        self._initialize_database()

        print(f"✅ Plugin Version Control initialized: {self.history_dir}")

    def _initialize_database(self):
        """Initialize SQLite database for version control metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plugin_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    file_size INTEGER DEFAULT 0,
                    syntax_valid BOOLEAN DEFAULT 1,
                    created_by TEXT DEFAULT 'system',
                    description TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for efficient querying
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_plugin_name ON plugin_snapshots(plugin_name)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON plugin_snapshots(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_confidence ON plugin_snapshots(confidence_score)"
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Failed to initialize version control database: {e}")

    def create_snapshot(
        self,
        plugin_name: str,
        plugin_code: str,
        confidence_score: float = 0.0,
        created_by: str = "system",
        description: str = "",
        metadata: Optional[Dict] = None,
    ) -> Optional[PluginSnapshot]:
        """
        Create a timestamped snapshot of a plugin

        Args:
            plugin_name: Name of the plugin
            plugin_code: Current plugin code
            confidence_score: Confidence score for this version
            created_by: Who/what created this snapshot
            description: Description of changes
            metadata: Additional metadata

        Returns:
            PluginSnapshot object if successful, None otherwise
        """
        try:
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_name = f"{plugin_name}_{timestamp}.py"
            snapshot_path = self.history_dir / snapshot_name

            # Validate syntax before saving
            syntax_valid = self._validate_syntax(plugin_code)
            if not syntax_valid:
                print(
                    f"[WARN] Warning: Plugin {plugin_name} has syntax errors, saving anyway"
                )

            # Write plugin code to snapshot file
            with open(snapshot_path, "w", encoding="utf-8") as f:
                f.write(plugin_code)

            # Store metadata in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO plugin_snapshots
                (plugin_name, timestamp, file_path, confidence_score, file_size,
                 syntax_valid, created_by, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    plugin_name,
                    timestamp,
                    str(snapshot_path),
                    confidence_score,
                    len(plugin_code),
                    syntax_valid,
                    created_by,
                    description,
                    json.dumps(metadata or {}),
                ),
            )

            conn.commit()
            conn.close()

            # Store in Lyrixa memory if available
            if self.memory_system:
                try:
                    import asyncio

                    asyncio.create_task(
                        self._store_snapshot_memory(
                            plugin_name, timestamp, confidence_score, description
                        )
                    )
                except Exception as e:
                    print(f"[WARN] Failed to store snapshot memory: {e}")

            snapshot = PluginSnapshot(
                plugin_name, timestamp, str(snapshot_path), confidence_score, metadata
            )

            print(
                f"✅ Snapshot created: {snapshot_name} (confidence: {confidence_score:.2f})"
            )
            return snapshot

        except Exception as e:
            print(f"❌ Failed to create snapshot for {plugin_name}: {e}")
            return None

    def list_snapshots(self, plugin_name: str) -> List[PluginSnapshot]:
        """List all snapshots for a specific plugin"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT plugin_name, timestamp, file_path, confidence_score, metadata
                FROM plugin_snapshots
                WHERE plugin_name = ?
                ORDER BY timestamp DESC
            """,
                (plugin_name,),
            )

            snapshots = []
            for row in cursor.fetchall():
                metadata = json.loads(row[4]) if row[4] else {}
                snapshot = PluginSnapshot(row[0], row[1], row[2], row[3], metadata)
                snapshots.append(snapshot)

            conn.close()
            return snapshots

        except Exception as e:
            print(f"❌ Failed to list snapshots for {plugin_name}: {e}")
            return []

    def rollback_plugin(
        self, plugin_name: str, timestamp: str, target_path: Optional[str] = None
    ) -> bool:
        """
        Rollback a plugin to a specific version

        Args:
            plugin_name: Name of the plugin
            timestamp: Timestamp of the version to restore
            target_path: Optional custom target path

        Returns:
            True if rollback successful, False otherwise
        """
        try:
            # Find the snapshot
            snapshot_name = f"{plugin_name}_{timestamp}.py"
            snapshot_path = self.history_dir / snapshot_name

            if not snapshot_path.exists():
                print(f"❌ Snapshot not found: {snapshot_path}")
                return False

            # Read and validate the snapshot
            with open(snapshot_path, "r", encoding="utf-8") as f:
                plugin_code = f.read()

            if not self._validate_syntax(plugin_code):
                print(f"[WARN] Warning: Snapshot {timestamp} has syntax errors")
                response = input("Continue with rollback? (y/N): ")
                if response.lower() != "y":
                    return False

            # Determine target path
            if not target_path:
                target_path = f"lyrixa/plugins/{plugin_name}.py"

            target_path_obj = Path(target_path)

            # Create backup of current version before rollback
            if target_path_obj.exists():
                current_backup_name = f"{plugin_name}_backup_before_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
                backup_path = self.history_dir / current_backup_name
                shutil.copy2(target_path_obj, backup_path)
                print(f"📁 Current version backed up to: {backup_path}")

            # Perform rollback
            shutil.copy2(snapshot_path, target_path_obj)

            # Log rollback in memory system
            if self.memory_system:
                try:
                    import asyncio

                    asyncio.create_task(
                        self._store_rollback_memory(plugin_name, timestamp)
                    )
                except Exception as e:
                    print(f"[WARN] Failed to store rollback memory: {e}")

            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE plugin_snapshots
                SET description = description || ' [ROLLED BACK]'
                WHERE plugin_name = ? AND timestamp = ?
            """,
                (plugin_name, timestamp),
            )
            conn.commit()
            conn.close()

            print(f"✅ Plugin {plugin_name} rolled back to version {timestamp}")
            return True

        except Exception as e:
            print(f"❌ Rollback failed for {plugin_name}: {e}")
            return False

    def diff_plugin_versions(
        self,
        plugin_name: str,
        timestamp1: str,
        timestamp2: str,
        output_format: str = "unified",
    ) -> str:
        """
        Generate diff between two plugin versions

        Args:
            plugin_name: Name of the plugin
            timestamp1: First version timestamp
            timestamp2: Second version timestamp
            output_format: 'unified', 'html', or 'context'

        Returns:
            Diff string in requested format
        """
        try:
            # Get snapshot paths
            snapshot1_path = self.history_dir / f"{plugin_name}_{timestamp1}.py"
            snapshot2_path = self.history_dir / f"{plugin_name}_{timestamp2}.py"

            if not snapshot1_path.exists() or not snapshot2_path.exists():
                return f"❌ One or both snapshots not found:\n{snapshot1_path}\n{snapshot2_path}"

            # Read files
            with open(snapshot1_path, "r", encoding="utf-8") as f1:
                lines1 = f1.readlines()

            with open(snapshot2_path, "r", encoding="utf-8") as f2:
                lines2 = f2.readlines()

            # Generate diff based on format
            if output_format == "html":
                differ = difflib.HtmlDiff(tabsize=4)
                diff = differ.make_file(
                    lines1,
                    lines2,
                    fromdesc=f"{plugin_name} @ {timestamp1}",
                    todesc=f"{plugin_name} @ {timestamp2}",
                )
            elif output_format == "context":
                diff = "\n".join(
                    difflib.context_diff(
                        lines1,
                        lines2,
                        fromfile=f"{plugin_name} @ {timestamp1}",
                        tofile=f"{plugin_name} @ {timestamp2}",
                    )
                )
            else:  # unified (default)
                diff = "\n".join(
                    difflib.unified_diff(
                        lines1,
                        lines2,
                        fromfile=f"{plugin_name} @ {timestamp1}",
                        tofile=f"{plugin_name} @ {timestamp2}",
                        lineterm="",
                    )
                )

            return diff

        except Exception as e:
            return f"❌ Diff generation failed: {e}"

    def export_snapshot(
        self, plugin_name: str, timestamp: str, export_path: Optional[str] = None
    ) -> bool:
        """Export a snapshot to a specified location"""
        try:
            snapshot_path = self.history_dir / f"{plugin_name}_{timestamp}.py"

            if not snapshot_path.exists():
                print(f"❌ Snapshot not found: {snapshot_path}")
                return False

            if not export_path:
                export_path = f"{plugin_name}_{timestamp}_export.py"

            shutil.copy2(snapshot_path, export_path)
            print(f"✅ Snapshot exported to: {export_path}")
            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    def cleanup_old_snapshots(self, plugin_name: str, keep_count: int = 10) -> int:
        """
        Clean up old snapshots, keeping only the most recent ones

        Args:
            plugin_name: Name of the plugin
            keep_count: Number of snapshots to keep

        Returns:
            Number of snapshots removed
        """
        try:
            snapshots = self.list_snapshots(plugin_name)

            if len(snapshots) <= keep_count:
                return 0

            # Remove oldest snapshots
            snapshots_to_remove = snapshots[keep_count:]
            removed_count = 0

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for snapshot in snapshots_to_remove:
                try:
                    # Remove file
                    if os.path.exists(snapshot.file_path):
                        os.remove(snapshot.file_path)

                    # Remove from database
                    cursor.execute(
                        """
                        DELETE FROM plugin_snapshots
                        WHERE plugin_name = ? AND timestamp = ?
                    """,
                        (plugin_name, snapshot.timestamp),
                    )

                    removed_count += 1

                except Exception as e:
                    print(f"[WARN] Failed to remove snapshot {snapshot.timestamp}: {e}")

            conn.commit()
            conn.close()

            print(f"🧹 Cleaned up {removed_count} old snapshots for {plugin_name}")
            return removed_count

        except Exception as e:
            print(f"❌ Cleanup failed for {plugin_name}: {e}")
            return 0

    def get_plugin_history_stats(self, plugin_name: str) -> Dict[str, Any]:
        """Get statistics for a plugin's version history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Basic stats
            cursor.execute(
                """
                SELECT COUNT(*), AVG(confidence_score), MAX(confidence_score), MIN(confidence_score)
                FROM plugin_snapshots WHERE plugin_name = ?
            """,
                (plugin_name,),
            )

            count, avg_confidence, max_confidence, min_confidence = cursor.fetchone()

            # Recent activity
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d_%H%M%S")
            cursor.execute(
                """
                SELECT COUNT(*) FROM plugin_snapshots
                WHERE plugin_name = ? AND timestamp >= ?
            """,
                (plugin_name, week_ago),
            )

            recent_count = cursor.fetchone()[0]

            # Size trends
            cursor.execute(
                """
                SELECT file_size FROM plugin_snapshots
                WHERE plugin_name = ? ORDER BY timestamp DESC LIMIT 5
            """,
                (plugin_name,),
            )

            recent_sizes = [row[0] for row in cursor.fetchall()]

            conn.close()

            return {
                "total_snapshots": count or 0,
                "average_confidence": avg_confidence or 0.0,
                "max_confidence": max_confidence or 0.0,
                "min_confidence": min_confidence or 0.0,
                "recent_snapshots": recent_count or 0,
                "recent_sizes": recent_sizes,
                "size_trend": "growing"
                if len(recent_sizes) > 1 and recent_sizes[0] > recent_sizes[-1]
                else "stable",
            }

        except Exception as e:
            print(f"❌ Failed to get stats for {plugin_name}: {e}")
            return {}

    def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax of plugin code"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False

    async def _store_snapshot_memory(
        self,
        plugin_name: str,
        timestamp: str,
        confidence_score: float,
        description: str,
    ):
        """Store snapshot creation in Lyrixa memory"""
        try:
            if self.memory_system:
                content = {
                    "action": "plugin_snapshot_created",
                    "plugin_name": plugin_name,
                    "timestamp": timestamp,
                    "confidence_score": confidence_score,
                    "description": description,
                }

                await self.memory_system.store_memory(
                    content=content,
                    context={"plugin": plugin_name, "action": "version_control"},
                    tags=["plugin", "version_control", "snapshot", plugin_name],
                    importance=0.6,
                    memory_type="project",
                )
        except Exception as e:
            print(f"[WARN] Failed to store snapshot memory: {e}")

    async def _store_rollback_memory(self, plugin_name: str, timestamp: str):
        """Store rollback action in Lyrixa memory"""
        try:
            if self.memory_system:
                content = {
                    "action": "plugin_rollback",
                    "plugin_name": plugin_name,
                    "restored_timestamp": timestamp,
                    "rollback_time": datetime.now().isoformat(),
                }

                await self.memory_system.store_memory(
                    content=content,
                    context={"plugin": plugin_name, "action": "rollback"},
                    tags=["plugin", "version_control", "rollback", plugin_name],
                    importance=0.8,
                    memory_type="project",
                )
        except Exception as e:
            print(f"[WARN] Failed to store rollback memory: {e}")


# Integration hooks for existing plugin system
class PluginVersionHooks:
    """Hooks to integrate version control with existing plugin operations"""

    def __init__(self, version_control: PluginVersionControl):
        self.version_control = version_control

    def before_plugin_save(
        self, plugin_name: str, plugin_code: str, confidence_score: float = 0.0
    ) -> bool:
        """Hook called before saving a plugin"""
        snapshot = self.version_control.create_snapshot(
            plugin_name,
            plugin_code,
            confidence_score,
            created_by="plugin_save",
            description="Auto-snapshot before save",
        )
        return snapshot is not None

    def before_plugin_refactor(
        self, plugin_name: str, plugin_code: str, confidence_score: float = 0.0
    ) -> bool:
        """Hook called before refactoring a plugin"""
        snapshot = self.version_control.create_snapshot(
            plugin_name,
            plugin_code,
            confidence_score,
            created_by="refactor",
            description="Auto-snapshot before refactor",
        )
        return snapshot is not None

    def before_ai_generation(self, plugin_name: str, plugin_code: str) -> bool:
        """Hook called before AI generates/modifies plugin code"""
        snapshot = self.version_control.create_snapshot(
            plugin_name,
            plugin_code,
            0.5,
            created_by="ai_generation",
            description="Auto-snapshot before AI modification",
        )
        return snapshot is not None


if __name__ == "__main__":
    # Example usage
    version_control = PluginVersionControl()

    # Create a test snapshot
    test_code = '''
def test_plugin():
    """A test plugin"""
    print("Hello from test plugin!")
    return {"status": "success"}
'''

    snapshot = version_control.create_snapshot(
        "TestPlugin",
        test_code,
        0.8,
        created_by="test",
        description="Initial test version",
    )

    if snapshot:
        print(f"Created snapshot: {snapshot.timestamp}")

        # List snapshots
        snapshots = version_control.list_snapshots("TestPlugin")
        print(f"Found {len(snapshots)} snapshots")

        # Get stats
        stats = version_control.get_plugin_history_stats("TestPlugin")
        print(f"Stats: {stats}")
