"""
🚀 Optimized Memory Storage with Batch Processing
=================================================

High-performance memory storage system with:
- Write-ahead buffer for batched operations
- Asynchronous tagging and scoring
- Binary format optimization
- Background processing queues
"""

import asyncio
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Lock, Timer
from typing import Any, Dict, List, Optional

try:
    import ujson as json  # Faster JSON processing
except ImportError:
    import json  # Fallback to standard json

from .fractal_mesh.base import MemoryFragment, MemoryFragmentType


@dataclass
class WriteOperation:
    """Represents a pending write operation"""

    operation_type: str  # 'insert', 'update', 'batch_insert'
    fragment: Optional[MemoryFragment] = None
    fragments: Optional[List[MemoryFragment]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class OptimizedMemoryStorage:
    """
    High-performance memory storage with batch processing and async operations
    """

    def __init__(
        self,
        db_path: str = "optimized_memory.db",
        batch_size: int = 50,
        flush_interval_ms: int = 100,
    ):
        self.db_path = Path(db_path)
        self.batch_size = batch_size
        self.flush_interval = flush_interval_ms / 1000.0  # Convert to seconds

        # Write-ahead buffer
        self.write_buffer: List[WriteOperation] = []
        self.buffer_lock = Lock()

        # Background processing
        self.executor = ThreadPoolExecutor(
            max_workers=3, thread_name_prefix="memory_storage"
        )
        self.processing_queue = Queue()

        # Timing control
        self.last_flush = time.time()
        self.flush_timer: Optional[Timer] = None

        # Performance metrics
        self.metrics: Dict[str, float] = {
            "total_writes": 0.0,
            "batch_writes": 0.0,
            "buffer_flushes": 0.0,
            "avg_batch_size": 0.0,
            "last_flush_duration": 0.0,
        }

        # Initialize database
        self._init_database()

        # Start background flush timer
        self._schedule_flush()

    def _init_database(self):
        """Initialize optimized database schema"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Optimized schema with better indexing
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_fragments_optimized (
                    fragment_id TEXT PRIMARY KEY,
                    content_binary BLOB,  -- Binary format for faster I/O
                    fragment_type INTEGER,
                    confidence_score REAL,
                    created_at INTEGER,  -- Unix timestamp for faster sorting
                    last_evolved INTEGER,
                    INDEX(created_at),
                    INDEX(fragment_type),
                    INDEX(confidence_score)
                )
            """)

            # Separate table for tags to normalize storage
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fragment_tags (
                    fragment_id TEXT,
                    tag_type TEXT,  -- 'temporal', 'symbolic', 'associative'
                    tag_key TEXT,
                    tag_value TEXT,
                    PRIMARY KEY (fragment_id, tag_type, tag_key),
                    FOREIGN KEY (fragment_id) REFERENCES memory_fragments_optimized(fragment_id)
                )
            """)

            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
            conn.execute("PRAGMA cache_size=10000")  # Larger cache
            conn.execute("PRAGMA temp_store=MEMORY")  # Memory temp storage

            conn.commit()
        finally:
            conn.close()

    def store_fragment_fast(self, fragment: MemoryFragment) -> str:
        """
        Fast, non-blocking fragment storage using write-ahead buffer
        """
        operation = WriteOperation(operation_type="insert", fragment=fragment)

        with self.buffer_lock:
            self.write_buffer.append(operation)

            # Check if immediate flush is needed
            if len(self.write_buffer) >= self.batch_size:
                self._flush_buffer_sync()

        # Schedule tagging and scoring for background processing
        self._schedule_background_processing(fragment)

        self.metrics["total_writes"] += 1
        return fragment.fragment_id

    def store_fragments_batch(self, fragments: List[MemoryFragment]) -> List[str]:
        """
        Batch storage for multiple fragments
        """
        operation = WriteOperation(operation_type="batch_insert", fragments=fragments)

        with self.buffer_lock:
            self.write_buffer.append(operation)
            self._flush_buffer_sync()  # Immediate flush for batches

        # Schedule background processing for all fragments
        for fragment in fragments:
            self._schedule_background_processing(fragment)

        self.metrics["total_writes"] += len(fragments)
        self.metrics["batch_writes"] += 1

        return [f.fragment_id for f in fragments]

    def _flush_buffer_sync(self):
        """
        Synchronously flush the write buffer to database
        """
        if not self.write_buffer:
            return

        start_time = time.time()
        operations_to_flush = self.write_buffer.copy()
        self.write_buffer.clear()

        # Execute batch write in background thread
        self.executor.submit(self._execute_batch_write, operations_to_flush)

        self.metrics["buffer_flushes"] += 1
        self.metrics["last_flush_duration"] = time.time() - start_time
        self.last_flush = time.time()

    def _execute_batch_write(self, operations: List[WriteOperation]):
        """
        Execute a batch of write operations efficiently
        """
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("BEGIN TRANSACTION")

            fragments_to_write = []

            # Collect all fragments from operations
            for op in operations:
                if op.operation_type == "insert" and op.fragment:
                    fragments_to_write.append(op.fragment)
                elif op.operation_type == "batch_insert" and op.fragments:
                    fragments_to_write.extend(op.fragments)

            if fragments_to_write:
                # Batch insert fragments
                fragment_data = []
                tag_data = []

                for fragment in fragments_to_write:
                    # Serialize fragment to binary format
                    content_binary = self._serialize_fragment_binary(fragment)

                    fragment_data.append(
                        (
                            fragment.fragment_id,
                            content_binary,
                            fragment.fragment_type.value,
                            fragment.confidence_score,
                            int(fragment.created_at.timestamp()),
                            int(fragment.last_evolved.timestamp()),
                        )
                    )

                    # Collect tag data
                    tag_data.extend(self._extract_tag_data(fragment))

                # Execute batch inserts
                conn.executemany(
                    """
                    INSERT OR REPLACE INTO memory_fragments_optimized
                    (fragment_id, content_binary, fragment_type, confidence_score, created_at, last_evolved)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    fragment_data,
                )

                # Clear existing tags and insert new ones
                fragment_ids = [f.fragment_id for f in fragments_to_write]
                placeholders = ",".join("?" * len(fragment_ids))
                conn.execute(
                    f"DELETE FROM fragment_tags WHERE fragment_id IN ({placeholders})",
                    fragment_ids,
                )

                if tag_data:
                    conn.executemany(
                        """
                        INSERT INTO fragment_tags (fragment_id, tag_type, tag_key, tag_value)
                        VALUES (?, ?, ?, ?)
                    """,
                        tag_data,
                    )

            conn.execute("COMMIT")

            # Update metrics
            avg_batch = len(fragments_to_write)
            current_avg = self.metrics.get("avg_batch_size", 0)
            total_batches = self.metrics.get("batch_writes", 0) + 1
            self.metrics["avg_batch_size"] = (
                current_avg * (total_batches - 1) + avg_batch
            ) / total_batches

        except Exception as e:
            conn.execute("ROLLBACK")
            print(f"Batch write error: {e}")
        finally:
            conn.close()

    def _serialize_fragment_binary(self, fragment: MemoryFragment) -> bytes:
        """
        Serialize fragment to compact binary format using ujson
        """
        fragment_dict = {
            "content": fragment.content,
            "temporal_tags": fragment.temporal_tags,
            "symbolic_tags": list(fragment.symbolic_tags),
            "associative_links": fragment.associative_links,
            "access_pattern": fragment.access_pattern,
            "narrative_role": fragment.narrative_role,
        }

        # Use json for faster serialization
        json_str = json.dumps(fragment_dict)
        return json_str.encode("utf-8")

    def _extract_tag_data(self, fragment: MemoryFragment) -> List[tuple]:
        """
        Extract tag data for normalized storage
        """
        tag_data = []

        # Temporal tags
        for key, value in fragment.temporal_tags.items():
            tag_data.append((fragment.fragment_id, "temporal", key, str(value)))

        # Symbolic tags
        for tag in fragment.symbolic_tags:
            tag_data.append((fragment.fragment_id, "symbolic", "tag", str(tag)))

        # Associative links
        for i, link in enumerate(fragment.associative_links):
            tag_data.append(
                (fragment.fragment_id, "associative", f"link_{i}", str(link))
            )

        return tag_data

    def _schedule_background_processing(self, fragment: MemoryFragment):
        """
        Schedule asynchronous tagging and scoring with 1-2 tick delay
        """
        # Add small delay to avoid blocking main storage operation
        delay = 0.001  # 1ms delay

        def delayed_processing():
            time.sleep(delay)
            self.processing_queue.put(("process_fragment", fragment))

        self.executor.submit(delayed_processing)

    def _schedule_flush(self):
        """
        Schedule periodic buffer flush
        """

        def flush_if_needed():
            current_time = time.time()
            if (current_time - self.last_flush) >= self.flush_interval:
                with self.buffer_lock:
                    if self.write_buffer:
                        self._flush_buffer_sync()

            # Schedule next flush
            self._schedule_flush()

        self.flush_timer = Timer(self.flush_interval, flush_if_needed)
        self.flush_timer.start()

    async def force_flush(self):
        """
        Force flush of write buffer (useful for testing)
        """
        with self.buffer_lock:
            if self.write_buffer:
                self._flush_buffer_sync()

        # Wait for background operations to complete
        await asyncio.sleep(0.01)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics
        """
        return {
            **self.metrics,
            "buffer_size": len(self.write_buffer),
            "queue_size": self.processing_queue.qsize(),
            "time_since_last_flush": time.time() - self.last_flush,
        }

    def retrieve_fragment(self, fragment_id: str) -> Optional[MemoryFragment]:
        """
        Fast fragment retrieval with binary deserialization
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                SELECT fragment_id, content_binary, fragment_type, confidence_score, created_at, last_evolved
                FROM memory_fragments_optimized
                WHERE fragment_id = ?
            """,
                (fragment_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            # Deserialize binary content
            content_binary = row[1]
            fragment_dict = json.loads(content_binary.decode("utf-8"))

            # Load tags
            tag_cursor = conn.execute(
                """
                SELECT tag_type, tag_key, tag_value
                FROM fragment_tags
                WHERE fragment_id = ?
            """,
                (fragment_id,),
            )

            temporal_tags = {}
            symbolic_tags = set()
            associative_links = []

            for tag_type, tag_key, tag_value in tag_cursor.fetchall():
                if tag_type == "temporal":
                    temporal_tags[tag_key] = tag_value
                elif tag_type == "symbolic" and tag_key == "tag":
                    symbolic_tags.add(tag_value)
                elif tag_type == "associative":
                    associative_links.append(tag_value)

            return MemoryFragment(
                fragment_id=row[0],
                content=fragment_dict["content"],
                fragment_type=MemoryFragmentType(row[2]),
                temporal_tags=temporal_tags,
                symbolic_tags=symbolic_tags,
                associative_links=associative_links,
                confidence_score=row[3],
                access_pattern=fragment_dict.get("access_pattern", {}),
                narrative_role=fragment_dict.get("narrative_role"),
                created_at=datetime.fromtimestamp(row[4]),
                last_evolved=datetime.fromtimestamp(row[5]),
            )

        finally:
            conn.close()

    def cleanup(self):
        """
        Clean up resources
        """
        if self.flush_timer:
            self.flush_timer.cancel()

        # Final flush
        with self.buffer_lock:
            if self.write_buffer:
                self._flush_buffer_sync()

        # Shutdown executor
        self.executor.shutdown(wait=True)


class AsyncMemoryProcessor:
    """
    Handles asynchronous memory processing tasks like tagging and scoring
    """

    def __init__(self):
        self.processing_queue = asyncio.Queue()
        self.is_running = False

    async def start_processing(self):
        """
        Start the async processing loop
        """
        self.is_running = True
        while self.is_running:
            try:
                # Wait for processing task with timeout
                task = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                await self._process_task(task)
            except asyncio.TimeoutError:
                continue  # Continue loop even if no tasks
            except Exception as e:
                print(f"Processing error: {e}")

    async def _process_task(self, task):
        """
        Process a single async task
        """
        task_type, data = task

        if task_type == "generate_tags":
            await self._generate_tags_async(data)
        elif task_type == "update_scores":
            await self._update_scores_async(data)
        elif task_type == "index_concepts":
            await self._index_concepts_async(data)

    async def _generate_tags_async(self, fragment: MemoryFragment):
        """
        Generate additional tags asynchronously
        """
        # Simulate tag generation with small delay
        await asyncio.sleep(0.001)

        # Add semantic tags based on content
        content_text = str(fragment.content.get("text", ""))
        if "error" in content_text.lower():
            fragment.symbolic_tags.add("error_related")
        if "success" in content_text.lower():
            fragment.symbolic_tags.add("success_related")

    async def _update_scores_async(self, fragment: MemoryFragment):
        """
        Update confidence and importance scores asynchronously
        """
        await asyncio.sleep(0.001)

        # Update access pattern
        current_time = datetime.now()
        fragment.access_pattern["last_accessed"] = current_time.isoformat()
        fragment.access_pattern["access_count"] = (
            fragment.access_pattern.get("access_count", 0) + 1
        )

    async def _index_concepts_async(self, fragment: MemoryFragment):
        """
        Update concept indexes asynchronously
        """
        await asyncio.sleep(0.001)
        # Concept indexing would happen here
        pass

    async def schedule_processing(self, fragment: MemoryFragment):
        """
        Schedule asynchronous processing for a fragment
        """
        await self.processing_queue.put(("generate_tags", fragment))
        await self.processing_queue.put(("update_scores", fragment))
        await self.processing_queue.put(("index_concepts", fragment))

    def stop_processing(self):
        """
        Stop the processing loop
        """
        self.is_running = False
