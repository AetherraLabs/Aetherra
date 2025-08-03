#!/usr/bin/env python3
"""
Clear Corrupted Plugin Chains
=============================

Removes corrupted plugin chain entries from memory databases.
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


class PluginChainCleaner:
    """Cleans corrupted plugin chains from memory databases."""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or ".")
        self.memory_dbs = [
            self.project_root / "lyrixa_context_memory.db",
            self.project_root / "lyrixa_plugin_memory.db",
            self.project_root / "plugin_state_memory.db",
        ]
        self.required_fields = [
            "name",
            "description",
            "input_schema",
            "output_schema",
            "created_by",
            "plugins",
        ]
        self.cleaned_count = 0

    def clean_database(self, db_path: Path) -> int:
        """Clean corrupted chains from a single database."""
        if not db_path.exists():
            return 0

        print(f"   🔍 Checking: {db_path.name}")

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            deleted_count = 0

            for table in tables:
                # Look for plugin chain related entries
                try:
                    cursor.execute(f"SELECT rowid, * FROM {table}")
                    rows = cursor.fetchall()

                    for row in rows:
                        # Check if this row contains plugin chain data
                        row_str = str(row).lower()
                        if "plugin_chain" in row_str or "plugin" in row_str:
                            # Try to parse any JSON content
                            for item in row[1:]:  # Skip rowid
                                if isinstance(item, str) and (
                                    item.startswith("{") or "plugin" in item
                                ):
                                    try:
                                        data = json.loads(item)
                                        if isinstance(data, dict):
                                            # Check if it's a corrupted chain
                                            missing_fields = [
                                                f
                                                for f in self.required_fields
                                                if f not in data
                                            ]
                                            if missing_fields:
                                                # Delete this corrupted entry
                                                rowid = row[0]
                                                cursor.execute(
                                                    f"DELETE FROM {table} WHERE rowid=?",
                                                    (rowid,),
                                                )
                                                deleted_count += 1
                                                print(
                                                    f"      [ERROR] Deleted corrupted chain (missing: {missing_fields})"
                                                )
                                                break
                                    except (json.JSONDecodeError, TypeError):
                                        continue

                except sqlite3.Error:
                    continue

            conn.commit()
            conn.close()

            if deleted_count > 0:
                print(f"      🧹 Cleaned {deleted_count} corrupted entries")
            else:
                print(f"      ✅ No corrupted entries found")

            return deleted_count

        except Exception as e:
            print(f"      [WARN] Error processing database: {e}")
            return 0

    def clean_all_databases(self):
        """Clean all memory databases."""
        print("🧹 PLUGIN CHAIN CLEANER")
        print("=" * 30)

        total_cleaned = 0

        for db_path in self.memory_dbs:
            cleaned = self.clean_database(db_path)
            total_cleaned += cleaned

        print(f"\n📊 Summary: Cleaned {total_cleaned} corrupted entries")

        # Create a backup flag file
        if total_cleaned > 0:
            flag_file = self.project_root / "plugin_chains_cleaned.flag"
            with open(flag_file, "w") as f:
                f.write(f"Plugin chains cleaned: {datetime.now().isoformat()}\n")
                f.write(f"Entries removed: {total_cleaned}\n")

        return total_cleaned


def main():
    """Main function."""
    cleaner = PluginChainCleaner()
    cleaned_count = cleaner.clean_all_databases()

    if cleaned_count > 0:
        print(
            f"\n✅ Successfully cleaned {cleaned_count} corrupted plugin chain entries!"
        )
        print("🚀 The plugin chain loader should now work properly.")
    else:
        print("\n📝 No corrupted plugin chains found to clean.")

    return cleaned_count


if __name__ == "__main__":
    main()
