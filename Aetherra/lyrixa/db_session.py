"""
🗃️ Database Session Management
================================

Centralized database connection and session management for the Lyrixa system.
Provides connection pooling, transaction management, and thread-safe operations.
"""

import asyncio
import logging
import sqlite3
import threading
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Thread-safe database connection wrapper
    """

    def __init__(self, db_path: str, timeout: float = 30.0):
        self.db_path = db_path
        self.timeout = timeout
        self._local = threading.local()
        self._lock = threading.Lock()
        self._connection_count = 0

        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection"""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            with self._lock:
                self._local.connection = sqlite3.connect(
                    self.db_path, timeout=self.timeout, check_same_thread=False
                )
                self._local.connection.row_factory = sqlite3.Row
                self._local.connection.execute("PRAGMA foreign_keys = ON")
                self._local.connection.execute("PRAGMA journal_mode = WAL")
                self._connection_count += 1
                logger.debug(
                    f"Created database connection {self._connection_count} for {self.db_path}"
                )

        return self._local.connection

    def close_connection(self):
        """Close the thread-local connection"""
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            with self._lock:
                self._connection_count -= 1
                logger.debug(
                    f"Closed database connection, {self._connection_count} remaining"
                )


class DatabaseSessionManager:
    """
    Manages database sessions and connection pooling for the Lyrixa system
    """

    def __init__(self):
        self._connections: Dict[str, DatabaseConnection] = {}
        self._lock = threading.Lock()
        self._initialized_dbs = set()

    def get_connection(self, db_path: str, timeout: float = 30.0) -> DatabaseConnection:
        """Get a database connection for the given path"""
        with self._lock:
            if db_path not in self._connections:
                self._connections[db_path] = DatabaseConnection(db_path, timeout)
        return self._connections[db_path]

    @contextmanager
    def get_session(self, db_path: str, timeout: float = 30.0):
        """Context manager for database sessions with automatic rollback on error"""
        connection_wrapper = self.get_connection(db_path, timeout)
        conn = connection_wrapper.get_connection()

        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction rolled back due to error: {e}")
            raise
        finally:
            # Connection remains open for reuse
            pass

    def execute_query(
        self,
        db_path: str,
        query: str,
        params: Optional[Union[tuple, dict]] = None,
        timeout: float = 30.0,
    ) -> List[sqlite3.Row]:
        """Execute a query and return results"""
        with self.get_session(db_path, timeout) as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            return cursor.fetchall()

    def execute_insert(
        self,
        db_path: str,
        query: str,
        params: Optional[Union[tuple, dict]] = None,
        timeout: float = 30.0,
    ) -> Optional[int]:
        """Execute an insert query and return the last row ID"""
        with self.get_session(db_path, timeout) as conn:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            return cursor.lastrowid

    def execute_many(
        self,
        db_path: str,
        query: str,
        params_list: List[Union[tuple, dict]],
        timeout: float = 30.0,
    ) -> int:
        """Execute a query multiple times with different parameters"""
        with self.get_session(db_path, timeout) as conn:
            cursor = conn.executemany(query, params_list)
            return cursor.rowcount

    def initialize_database(
        self, db_path: str, schema_queries: List[str], timeout: float = 30.0
    ):
        """Initialize a database with the given schema"""
        if db_path in self._initialized_dbs:
            return

        with self.get_session(db_path, timeout) as conn:
            for query in schema_queries:
                conn.execute(query)

        self._initialized_dbs.add(db_path)
        logger.info(f"Initialized database schema for {db_path}")

    def backup_database(
        self, source_db_path: str, backup_path: str, timeout: float = 60.0
    ):
        """Create a backup of a database"""
        source_conn = self.get_connection(source_db_path, timeout).get_connection()

        # Ensure backup directory exists
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(backup_path) as backup_conn:
            source_conn.backup(backup_conn)

        logger.info(f"Database backed up from {source_db_path} to {backup_path}")

    def close_all_connections(self):
        """Close all database connections"""
        with self._lock:
            for connection in self._connections.values():
                connection.close_connection()
            self._connections.clear()
            self._initialized_dbs.clear()
            logger.info("All database connections closed")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about database connections"""
        with self._lock:
            return {
                "active_databases": len(self._connections),
                "database_paths": list(self._connections.keys()),
                "initialized_databases": len(self._initialized_dbs),
                "timestamp": datetime.now().isoformat(),
            }


class AsyncDatabaseSessionManager:
    """
    Async version of database session manager for use with asyncio
    """

    def __init__(self):
        self._sync_manager = DatabaseSessionManager()
        self._executor = None

    def _get_executor(self):
        """Get or create thread pool executor"""
        if self._executor is None:
            import concurrent.futures

            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=5, thread_name_prefix="db_worker"
            )
        return self._executor

    async def execute_query(
        self,
        db_path: str,
        query: str,
        params: Optional[Union[tuple, dict]] = None,
        timeout: float = 30.0,
    ) -> List[Dict[str, Any]]:
        """Async version of execute_query"""
        loop = asyncio.get_event_loop()

        def _execute():
            results = self._sync_manager.execute_query(db_path, query, params, timeout)
            # Convert sqlite3.Row to dict for JSON serialization
            return [dict(row) for row in results]

        return await loop.run_in_executor(self._get_executor(), _execute)

    async def execute_insert(
        self,
        db_path: str,
        query: str,
        params: Optional[Union[tuple, dict]] = None,
        timeout: float = 30.0,
    ) -> Optional[int]:
        """Async version of execute_insert"""
        loop = asyncio.get_event_loop()

        def _execute():
            return self._sync_manager.execute_insert(db_path, query, params, timeout)

        return await loop.run_in_executor(self._get_executor(), _execute)

    async def execute_many(
        self,
        db_path: str,
        query: str,
        params_list: List[Union[tuple, dict]],
        timeout: float = 30.0,
    ) -> int:
        """Async version of execute_many"""
        loop = asyncio.get_event_loop()

        def _execute():
            return self._sync_manager.execute_many(db_path, query, params_list, timeout)

        return await loop.run_in_executor(self._get_executor(), _execute)

    async def initialize_database(
        self, db_path: str, schema_queries: List[str], timeout: float = 30.0
    ):
        """Async version of initialize_database"""
        loop = asyncio.get_event_loop()

        def _initialize():
            self._sync_manager.initialize_database(db_path, schema_queries, timeout)

        await loop.run_in_executor(self._get_executor(), _initialize)

    @asynccontextmanager
    async def get_session(self, db_path: str, timeout: float = 30.0):
        """Async context manager for database sessions"""
        # For async operations, we use the synchronous session manager
        # in a thread executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()

        def _get_connection():
            return self._sync_manager.get_connection(db_path, timeout).get_connection()

        conn = await loop.run_in_executor(self._get_executor(), _get_connection)

        try:
            await loop.run_in_executor(
                self._get_executor(), lambda: conn.execute("BEGIN")
            )
            yield AsyncDatabaseSession(conn, self._get_executor())
            await loop.run_in_executor(self._get_executor(), conn.commit)
        except Exception as e:
            await loop.run_in_executor(self._get_executor(), conn.rollback)
            logger.error(f"Async database transaction rolled back due to error: {e}")
            raise

    async def close_all_connections(self):
        """Async version of close_all_connections"""
        loop = asyncio.get_event_loop()

        def _close_all():
            self._sync_manager.close_all_connections()
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None

        await loop.run_in_executor(self._get_executor(), _close_all)


class AsyncDatabaseSession:
    """
    Async wrapper for database session operations
    """

    def __init__(self, connection: sqlite3.Connection, executor):
        self._connection = connection
        self._executor = executor

    async def execute(
        self, query: str, params: Optional[Union[tuple, dict]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query asynchronously"""
        loop = asyncio.get_event_loop()

        def _execute():
            if params:
                cursor = self._connection.execute(query, params)
            else:
                cursor = self._connection.execute(query)
            return [dict(row) for row in cursor.fetchall()]

        return await loop.run_in_executor(self._executor, _execute)

    async def execute_insert(
        self, query: str, params: Optional[Union[tuple, dict]] = None
    ) -> Optional[int]:
        """Execute an insert query asynchronously"""
        loop = asyncio.get_event_loop()

        def _execute():
            if params:
                cursor = self._connection.execute(query, params)
            else:
                cursor = self._connection.execute(query)
            return cursor.lastrowid

        return await loop.run_in_executor(self._executor, _execute)


# Global session managers
sync_db_manager = DatabaseSessionManager()
async_db_manager = AsyncDatabaseSessionManager()


def get_db_session(db_path: str, timeout: float = 30.0):
    """Get a synchronous database session"""
    return sync_db_manager.get_session(db_path, timeout)


async def get_async_db_session(db_path: str, timeout: float = 30.0):
    """Get an asynchronous database session"""
    return async_db_manager.get_session(db_path, timeout)


def initialize_common_schemas():
    """Initialize common database schemas used across the system"""

    # Memory system schema
    memory_schema = [
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            context TEXT,
            tags TEXT,
            importance REAL DEFAULT 0.5,
            memory_type TEXT DEFAULT 'general',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 0,
            last_accessed_at TEXT
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)
        """,
    ]

    # Reasoning system schema
    reasoning_schema = [
        """
        CREATE TABLE IF NOT EXISTS reasoning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            context TEXT NOT NULL,
            reasoning_type TEXT NOT NULL,
            conclusion TEXT,
            confidence REAL,
            evidence TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_reasoning_type ON reasoning_sessions(reasoning_type)
        """,
    ]

    # Self-improvement schema
    improvement_schema = [
        """
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_unit TEXT,
            context TEXT,
            recorded_at TEXT NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_metrics_name ON performance_metrics(metric_name)
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_metrics_recorded ON performance_metrics(recorded_at)
        """,
    ]

    # Initialize schemas
    sync_db_manager.initialize_database("lyrixa_memory.db", memory_schema)
    sync_db_manager.initialize_database("lyrixa_reasoning.db", reasoning_schema)
    sync_db_manager.initialize_database("lyrixa_improvement.db", improvement_schema)

    logger.info("Common database schemas initialized")


async def test_database_session():
    """Test database session functionality"""
    import os
    import tempfile

    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db = tmp.name

    try:
        # Test synchronous operations
        print("Testing synchronous database operations...")

        # Initialize test schema
        schema = [
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value INTEGER,
                created_at TEXT NOT NULL
            )
            """
        ]
        sync_db_manager.initialize_database(test_db, schema)

        # Insert test data
        insert_id = sync_db_manager.execute_insert(
            test_db,
            "INSERT INTO test_table (name, value, created_at) VALUES (?, ?, ?)",
            ("test_record", 42, datetime.now().isoformat()),
        )
        print(f"Inserted record with ID: {insert_id}")

        # Query test data
        results = sync_db_manager.execute_query(
            test_db, "SELECT * FROM test_table WHERE id = ?", (insert_id,)
        )
        print(f"Query results: {dict(results[0]) if results else 'No results'}")

        # Test asynchronous operations
        print("\nTesting asynchronous database operations...")

        insert_id2 = await async_db_manager.execute_insert(
            test_db,
            "INSERT INTO test_table (name, value, created_at) VALUES (?, ?, ?)",
            ("async_test", 84, datetime.now().isoformat()),
        )
        print(f"Async inserted record with ID: {insert_id2}")

        async_results = await async_db_manager.execute_query(
            test_db, "SELECT * FROM test_table ORDER BY id"
        )
        print(f"Async query results: {len(async_results)} records")

        # Test async session context manager
        async with async_db_manager.get_session(test_db) as session:
            session_results = await session.execute(
                "SELECT COUNT(*) as count FROM test_table"
            )
            print(f"Session count query: {session_results[0]['count']} records")

        # Get connection stats
        stats = sync_db_manager.get_connection_stats()
        print(f"\nConnection stats: {stats}")

        print("✅ Database session tests completed successfully")

    finally:
        # Cleanup
        await async_db_manager.close_all_connections()
        sync_db_manager.close_all_connections()
        os.unlink(test_db)


if __name__ == "__main__":
    asyncio.run(test_database_session())
