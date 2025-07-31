#!/usr/bin/env python3
"""
Enhanced Plugin Chain Cleaner
============================

Comprehensive tool to find and clean corrupted plugin chains from ALL database files.
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict


class EnhancedPluginChainCleaner:
    """Enhanced plugin chain cleaner for all databases."""

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.required_fields = [
            "name",
            "description",
            "input_schema",
            "output_schema",
            "created_by",
            "plugins",
        ]
        self.cleaned_count = 0
        self.checked_count = 0
        self.database_files = []

    def find_all_databases(self):
        """Find all database files in the project."""
        print("🔍 Scanning for database files...")

        # Find all .db files
        db_files = list(self.project_root.rglob("*.db"))

        for db_file in db_files:
            try:
                # Test if it's a valid SQLite database
                conn = sqlite3.connect(str(db_file))
                conn.close()
                self.database_files.append(db_file)
                print(f"   ✅ Found database: {db_file}")
            except Exception:
                print(f"   ❌ Invalid database: {db_file}")

        print(f"📊 Found {len(self.database_files)} valid database files")

    def clean_all_databases(self):
        """Clean corrupted plugin chains from all databases."""
        print("\n🧹 ENHANCED PLUGIN CHAIN CLEANER")
        print("=" * 50)

        self.find_all_databases()

        for db_path in self.database_files:
            self._clean_database(db_path)

        print("\n📊 Summary:")
        print(f"   🔍 Databases checked: {self.checked_count}")
        print(f"   🧹 Corrupted entries cleaned: {self.cleaned_count}")

        if self.cleaned_count > 0:
            print("✅ Plugin chain cleanup completed!")
        else:
            print("📝 No corrupted plugin chains found to clean.")

    def _clean_database(self, db_path: Path):
        """Clean a single database file."""
        print(f"\n   🔍 Checking: {db_path.name}")
        self.checked_count += 1

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table_tuple in tables:
                table_name = table_tuple[0]
                self._clean_table(cursor, table_name, db_path)

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"      ⚠️ Error processing database: {e}")

    def _clean_table(self, cursor, table_name: str, db_path: Path):
        """Clean corrupted plugin chains from a specific table."""
        try:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]

            # Look for tables that might contain plugin data
            plugin_indicators = ["plugin", "chain", "content", "data", "memory"]
            has_plugin_indicator = any(
                indicator in table_name.lower() for indicator in plugin_indicators
            )
            has_content_column = any(
                col.lower() in ["content", "data", "value", "json"] for col in columns
            )

            if not (has_plugin_indicator or has_content_column):
                return

            # Try to find and clean plugin chain data
            for column in columns:
                if column.lower() in ["content", "data", "value", "json"]:
                    self._clean_plugin_data_in_column(
                        cursor, table_name, column, db_path
                    )

        except Exception as e:
            print(f"      ⚠️ Error processing table {table_name}: {e}")

    def _clean_plugin_data_in_column(
        self, cursor, table_name: str, column: str, db_path: Path
    ):
        """Clean plugin data from a specific column."""
        try:
            # Get all rows from this table
            cursor.execute(f"SELECT rowid, {column} FROM {table_name}")
            rows = cursor.fetchall()

            deleted_count = 0

            for rowid, content in rows:
                if content and isinstance(content, str):
                    try:
                        # Try to parse as JSON
                        if (
                            content.strip().startswith("{")
                            or "plugin_chain" in content.lower()
                        ):
                            data = (
                                json.loads(content)
                                if content.strip().startswith("{")
                                else {"raw": content}
                            )

                            # Check if this looks like plugin chain data
                            if self._is_corrupted_plugin_chain(data, content):
                                # Delete this row
                                cursor.execute(
                                    f"DELETE FROM {table_name} WHERE rowid = ?",
                                    (rowid,),
                                )
                                deleted_count += 1
                                self.cleaned_count += 1
                                print(
                                    f"      🗑️ Deleted corrupted entry from {table_name} (rowid: {rowid})"
                                )

                    except (json.JSONDecodeError, TypeError):
                        # Check if raw content indicates plugin chain
                        if "plugin_chain" in content.lower() and any(
                            field not in content for field in self.required_fields
                        ):
                            cursor.execute(
                                f"DELETE FROM {table_name} WHERE rowid = ?", (rowid,)
                            )
                            deleted_count += 1
                            self.cleaned_count += 1
                            print(
                                f"      🗑️ Deleted corrupted raw entry from {table_name} (rowid: {rowid})"
                            )

            if deleted_count > 0:
                print(
                    f"      ✅ Cleaned {deleted_count} corrupted entries from {table_name}"
                )

        except Exception as e:
            print(f"      ⚠️ Error cleaning column {column} in {table_name}: {e}")

    def _is_corrupted_plugin_chain(self, data: Dict, raw_content: str) -> bool:
        """Check if data represents a corrupted plugin chain."""
        # Check for plugin chain indicators
        plugin_chain_indicators = [
            "plugin_chain" in raw_content.lower(),
            "type" in data and data.get("type") == "plugin_chain",
            "plugins" in data,
            any(
                field in data
                for field in ["input_schema", "output_schema", "created_by"]
            ),
        ]

        if not any(plugin_chain_indicators):
            return False

        # Check if it's missing required fields
        missing_fields = [field for field in self.required_fields if field not in data]

        # If it has plugin chain indicators but missing required fields, it's corrupted
        return len(missing_fields) > 0


if __name__ == "__main__":
    cleaner = EnhancedPluginChainCleaner()
    cleaner.clean_all_databases()
