import json
import os
import sqlite3  # Import sqlite3 for database operations
import unittest

from lyrixa.core.memory import (
    LyrixaMemorySystem,  # Use the correct memory management class
)


class TestMemorySharing(unittest.TestCase):
    def setUp(self):
        self.memory_system = LyrixaMemorySystem(
            "test_memory.db"
        )  # Reinitialize to ensure a fresh connection
        self.test_file = "test_memory.json"

        # Set up a test database
        self.memory_system.ensure_connection()
        conn = self.memory_system.conn
        if conn is None:
            raise RuntimeError("Database connection is not initialized.")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT,
                last_accessed TEXT,
                access_count INTEGER
            )
            """
        )
        cursor.execute(
            "INSERT INTO memories (id, content, last_accessed, access_count, importance) VALUES (?, ?, ?, ?, ?)",
            ("1", "Test content", "2025-07-04T12:00:00", 1, 0.5),
        )
        conn.execute(
            "PRAGMA journal_mode=WAL;"
        )  # Enable Write-Ahead Logging for concurrent access
        conn.commit()
        conn.close()  # Explicitly close the connection after setup

    def tearDown(self):
        # Clean up test database and file
        self.memory_system.close_connection()
        if os.path.exists("test_memory.db"):
            os.remove("test_memory.db")
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_export_memory(self):
        self.memory_system.export_memory(self.test_file)

        # Verify the file was created and contains the correct data
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, "r") as file:
            data = json.load(file)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["id"], "1")

    def test_import_memory(self):
        # Create a test file with memory data
        with open(self.test_file, "w") as file:
            json.dump(
                [
                    {
                        "id": "2",
                        "content": "Imported content",
                        "last_accessed": "2025-07-04T13:00:00",
                        "access_count": 2,
                    }
                ],
                file,
            )

        self.memory_system.import_memory(self.test_file)

        # Verify the data was imported into the database
        conn = sqlite3.connect("test_memory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE id = ?", ("2",))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result[1], "Imported content")


if __name__ == "__main__":
    unittest.main()
