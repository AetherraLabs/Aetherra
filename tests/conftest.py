"""
Aetherra Test Configuration and Fixtures
========================================

This module provides shared test fixtures, configuration, and utilities
for the Aetherra test suite, including UI tests, integration tests, and unit tests.
"""

import os
import shutil
import sqlite3
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Generator, Optional
from unittest.mock import Mock, patch

import pytest

# Make sure the project root is in the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "Aetherra"))

# Try to import Qt for testing
try:
    from PySide6.QtWidgets import QApplication

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

# Skip all tests if Qt is not available
pytestmark = pytest.mark.skipif(
    not QT_AVAILABLE, reason="PySide6 is not installed, UI tests will be skipped"
)


@pytest.fixture
def app(qtbot):
    """Create a QApplication instance for testing."""
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Aetherra Test")
    yield app


@pytest.fixture
def style_guide():
    """Return the standard style guide values for testing."""
    return {
        "colors": {
            "primary_bg": "#1e1e1e",
            "secondary_bg": "#252525",
            "tertiary_bg": "#333333",
            "control_bg": "#2d2d2d",
            "primary_text": "#ffffff",
            "secondary_text": "#cccccc",
            "disabled_text": "#888888",
            "primary_accent": "#0078d4",
            "hover_accent": "#106ebe",
            "success": "#107c10",
            "warning": "#d8a629",
            "error": "#d13438",
        },
        "spacing": {
            "default_margin": 8,
            "compact_margin": 4,
            "content_padding": 8,
            "control_padding": 8,
            "vertical_spacing": 8,
        },
        "border_radius": {
            "standard": 6,
            "small": 4,
            "flat": 0,
        },
        "typography": {
            "window_title_size": 16,
            "header_size": 14,
            "body_size": 13,
            "small_size": 12,
            "code_size": 13,
        },
    }


# Test configuration
class TestConfig:
    """Global test configuration"""

    # Test database settings
    TEST_DB_PATH = ":memory:"  # Use in-memory SQLite for tests
    TEST_DB_TIMEOUT = 30

    # Test data directories
    TEST_DATA_DIR = Path(__file__).parent / "data"
    FIXTURES_DIR = Path(__file__).parent / "fixtures"

    # Mock settings
    MOCK_EXTERNAL_APIS = True
    MOCK_NEURAL_INTERFACES = True
    MOCK_QUANTUM_SYSTEMS = True

    # Performance test thresholds
    MAX_RESPONSE_TIME_MS = 1000
    MAX_MEMORY_USAGE_MB = 100

    # Feature flags for testing
    ENABLE_NEURAL_TESTS = os.getenv("ENABLE_NEURAL_TESTS", "false").lower() == "true"
    ENABLE_QUANTUM_TESTS = os.getenv("ENABLE_QUANTUM_TESTS", "false").lower() == "true"
    ENABLE_GPU_TESTS = os.getenv("ENABLE_GPU_TESTS", "false").lower() == "true"
    ENABLE_NETWORK_TESTS = os.getenv("ENABLE_NETWORK_TESTS", "false").lower() == "true"


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration to all tests"""
    return TestConfig()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment"""
    # Create test data directories
    TestConfig.TEST_DATA_DIR.mkdir(exist_ok=True)
    TestConfig.FIXTURES_DIR.mkdir(exist_ok=True)

    # Set environment variables for testing
    os.environ["AETHERRA_ENV"] = "testing"
    os.environ["AETHERRA_DEBUG"] = "true"
    os.environ["AETHERRA_LOG_LEVEL"] = "DEBUG"

    yield

    # Cleanup after all tests
    if TestConfig.TEST_DATA_DIR.exists():
        shutil.rmtree(TestConfig.TEST_DATA_DIR, ignore_errors=True)


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files"""
    temp_path = tempfile.mkdtemp(prefix="aetherra_test_")
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_database():
    """Provide a mock database connection"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        db_path = temp_db.name

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        conn.close()
        os.unlink(db_path)


@pytest.fixture
def memory_database():
    """Provide an in-memory SQLite database"""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def sample_memory_data():
    """Provide sample memory system data for testing"""
    return {
        "episodic_memories": [
            {
                "id": 1,
                "content": "User asked about quantum computing",
                "timestamp": datetime.now() - timedelta(hours=1),
                "importance": 0.8,
                "tags": ["quantum", "user_question"],
            },
            {
                "id": 2,
                "content": "Successful neural interface connection",
                "timestamp": datetime.now() - timedelta(minutes=30),
                "importance": 0.9,
                "tags": ["neural", "success"],
            },
        ],
        "semantic_memories": [
            {
                "id": 1,
                "concept": "quantum_computing",
                "definition": "Computing using quantum mechanical phenomena",
                "confidence": 0.95,
                "last_accessed": datetime.now(),
            }
        ],
    }


@pytest.fixture
def sample_agent_data():
    """Provide sample agent data for testing"""
    return {
        "agents": [
            {
                "id": "agent_001",
                "name": "AnalyticsAgent",
                "type": "analytics",
                "status": "active",
                "capabilities": ["data_analysis", "reporting"],
                "created_at": datetime.now() - timedelta(days=1),
            },
            {
                "id": "agent_002",
                "name": "MemoryAgent",
                "type": "memory",
                "status": "idle",
                "capabilities": ["memory_management", "retrieval"],
                "created_at": datetime.now() - timedelta(hours=6),
            },
        ],
        "tasks": [
            {
                "id": "task_001",
                "agent_id": "agent_001",
                "type": "analysis",
                "status": "completed",
                "priority": "high",
                "created_at": datetime.now() - timedelta(hours=2),
                "completed_at": datetime.now() - timedelta(hours=1),
            }
        ],
    }


@pytest.fixture
def mock_neural_interface():
    """Mock neural interface for testing"""
    mock_interface = Mock()
    mock_interface.is_connected.return_value = True
    mock_interface.read_data.return_value = {
        "signal_strength": 0.85,
        "data_quality": "good",
        "timestamp": datetime.now(),
        "raw_data": [0.1, 0.2, 0.3, 0.4, 0.5],
    }
    mock_interface.send_command.return_value = {"status": "success"}

    return mock_interface


@pytest.fixture
def mock_quantum_system():
    """Mock quantum computing system for testing"""
    mock_quantum = Mock()
    mock_quantum.is_available.return_value = True
    mock_quantum.run_circuit.return_value = {
        "result": [0, 1, 1, 0],
        "probability": 0.95,
        "execution_time": 0.1,
        "qubits_used": 4,
    }

    return mock_quantum


@pytest.fixture
def mock_api_responses():
    """Mock external API responses"""
    responses = {
        "health_check": {"status": "ok", "timestamp": datetime.now().isoformat()},
        "agent_status": {"active_agents": 5, "total_tasks": 42},
        "memory_status": {"total_memories": 1000, "recent_activity": 15},
        "analytics_data": {"processed_events": 500, "insights_generated": 12},
    }

    return responses


@contextmanager
def mock_external_apis():
    """Context manager to mock all external API calls"""
    with (
        patch("requests.get") as mock_get,
        patch("requests.post") as mock_post,
        patch("requests.put") as mock_put,
        patch("requests.delete") as mock_delete,
    ):
        # Configure mock responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "mocked"}

        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_put.return_value = mock_response
        mock_delete.return_value = mock_response

        yield {
            "get": mock_get,
            "post": mock_post,
            "put": mock_put,
            "delete": mock_delete,
        }


class TestHelpers:
    """Utility functions for testing"""

    @staticmethod
    def create_test_memory_db(conn) -> None:
        """Create test memory database schema"""
        schema = """
        CREATE TABLE IF NOT EXISTS episodic_memories (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            importance REAL DEFAULT 0.5,
            tags TEXT
        );

        CREATE TABLE IF NOT EXISTS semantic_memories (
            id INTEGER PRIMARY KEY,
            concept TEXT NOT NULL,
            definition TEXT,
            confidence REAL DEFAULT 0.5,
            last_accessed DATETIME
        );

        CREATE TABLE IF NOT EXISTS memory_associations (
            id INTEGER PRIMARY KEY,
            memory_id_1 INTEGER,
            memory_id_2 INTEGER,
            strength REAL DEFAULT 0.5,
            FOREIGN KEY (memory_id_1) REFERENCES episodic_memories(id),
            FOREIGN KEY (memory_id_2) REFERENCES episodic_memories(id)
        );
        """

        conn.executescript(schema)
        conn.commit()

    @staticmethod
    def create_test_agent_db(conn) -> None:
        """Create test agent database schema"""
        schema = """
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'idle',
            capabilities TEXT,
            created_at DATETIME NOT NULL,
            last_active DATETIME
        );

        CREATE TABLE IF NOT EXISTS agent_tasks (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'normal',
            data TEXT,
            created_at DATETIME NOT NULL,
            completed_at DATETIME,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        );
        """

        conn.executescript(schema)
        conn.commit()

    @staticmethod
    def insert_test_data(conn, table: str, data: list) -> None:
        """Insert test data into a table"""
        if not data:
            return

        # Get column names from first item
        columns = list(data[0].keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join(columns)

        query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

        for item in data:
            values = [item[col] for col in columns]
            conn.execute(query, values)

        conn.commit()

    @staticmethod
    def assert_response_time(start_time: float, max_time_ms: int = 1000) -> None:
        """Assert that operation completed within time limit"""
        import time

        elapsed_ms = (time.time() - start_time) * 1000
        assert elapsed_ms < max_time_ms, (
            f"Operation took {elapsed_ms:.2f}ms, expected < {max_time_ms}ms"
        )

    @staticmethod
    def assert_memory_usage(max_mb: int = 100) -> None:
        """Assert that memory usage is within limits"""
        try:
            import psutil

            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            assert memory_mb < max_mb, (
                f"Memory usage {memory_mb:.2f}MB exceeds limit of {max_mb}MB"
            )
        except ImportError:
            pass  # psutil not available, skip check


# Custom pytest markers for skipping tests based on conditions
def pytest_configure(config):
    """Configure custom pytest markers"""
    # Neural interface tests
    if not TestConfig.ENABLE_NEURAL_TESTS:
        config.addinivalue_line(
            "markers",
            "neural: mark test as requiring neural interface (skip if ENABLE_NEURAL_TESTS=false)",
        )

    # Quantum computing tests
    if not TestConfig.ENABLE_QUANTUM_TESTS:
        config.addinivalue_line(
            "markers",
            "quantum: mark test as requiring quantum system (skip if ENABLE_QUANTUM_TESTS=false)",
        )

    # GPU tests
    if not TestConfig.ENABLE_GPU_TESTS:
        config.addinivalue_line(
            "markers",
            "gpu: mark test as requiring GPU (skip if ENABLE_GPU_TESTS=false)",
        )

    # Network tests
    if not TestConfig.ENABLE_NETWORK_TESTS:
        config.addinivalue_line(
            "markers",
            "network: mark test as requiring network (skip if ENABLE_NETWORK_TESTS=false)",
        )


def pytest_runtest_setup(item):
    """Skip tests based on markers and configuration"""
    # Skip neural tests if disabled
    if item.get_closest_marker("neural") and not TestConfig.ENABLE_NEURAL_TESTS:
        pytest.skip("Neural interface tests disabled")

    # Skip quantum tests if disabled
    if item.get_closest_marker("quantum") and not TestConfig.ENABLE_QUANTUM_TESTS:
        pytest.skip("Quantum computing tests disabled")

    # Skip GPU tests if disabled
    if item.get_closest_marker("gpu") and not TestConfig.ENABLE_GPU_TESTS:
        pytest.skip("GPU tests disabled")

    # Skip network tests if disabled
    if item.get_closest_marker("network") and not TestConfig.ENABLE_NETWORK_TESTS:
        pytest.skip("Network tests disabled")
