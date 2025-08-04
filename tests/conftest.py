"""
Pytest configuration for Aetherra tests
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Aetherra"))

# Set up test environment
os.environ["TESTING"] = "true"

# Configure test database paths to use temporary files
os.environ["TEST_MODE"] = "true"

import pytest


@pytest.fixture(scope="session")
def project_root_path():
    """Provide the project root path for tests"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def aetherra_root_path():
    """Provide the Aetherra directory path for tests"""
    return Path(__file__).parent.parent / "Aetherra"


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment for each test"""
    # Ensure we're in test mode
    os.environ["TESTING"] = "true"
    yield
    # Cleanup after test if needed


@pytest.fixture
def mock_env_file():
    """Provide mock environment variables for testing"""
    return {
        "OPENAI_API_KEY": "test-key",
        "ANTHROPIC_API_KEY": "test-key",
        "GOOGLE_API_KEY": "test-key"
    }
