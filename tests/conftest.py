# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Pytest configuration for Aetherra tests
"""

# Standard library imports
import asyncio
import inspect
import os
import sys
import threading
import warnings
from pathlib import Path

# Third party imports
import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Aetherra"))

# Set up test environment
os.environ["TESTING"] = "true"
os.environ.setdefault("AETHERRA_SKIP_DOTENV", "1")

# Configure test database paths to use temporary files
os.environ["TEST_MODE"] = "true"
os.environ.setdefault("AETHERRA_TEST_ENFORCE_DISABLED_UNTIL_SET", "1")

# In test runs, default AI developer endpoints to disabled unless explicitly enabled by a test.
# This avoids global defaults from other modules leaking in via imported .env or launchers.
os.environ.setdefault("AETHERRA_AI_API_ENABLED", "0")
os.environ.setdefault("AETHERRA_AI_API_STREAM", "0")
os.environ.setdefault("AETHERRA_AI_API_REQUIRE_TOKEN", "0")

# Deterministically force Lyrixa chat service into offline/fallback mode for tests
# Individual tests can override this by setting it to "0" via monkeypatch if needed.
os.environ.setdefault("AETHERRA_LYRIXA_FORCE_OFFLINE", "1")


@pytest.fixture(scope="session")
def project_root_path():
    """Provide the project root path for tests"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def aetherra_root_path():
    """Provide the Aetherra directory path for tests"""
    return Path(__file__).parent.parent / "Aetherra"


@pytest.fixture
def signing_hub(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("NO_PROXY", "127.0.0.1,localhost")
    for name in (
        "AETHERRA_ALLOW_UNSIGNED_DEV",
        "AETHERRA_PLUGIN_SIGNING_SECRET",
        "AETHERRA_KEYS_MASTER",
    ):
        monkeypatch.delenv(name, raising=False)
    # Third party imports
    from werkzeug.serving import make_server

    # Aetherra imports
    from aetherra_hub.app import create_app
    from aetherra_hub.blueprints import plugins as plugin_routes
    from aetherra_hub.services import plugins as plugin_service

    monkeypatch.setattr(plugin_routes, "_PLUGIN_REGISTRY", {})
    store = plugin_service.PluginStore()
    monkeypatch.setattr(plugin_service, "store", store)
    server = make_server("127.0.0.1", 0, create_app())
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", store
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
        assert not worker.is_alive(), "signing test Hub did not stop"


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment for each test"""
    # Ensure we're in test mode
    os.environ["TESTING"] = "true"
    return
    # Cleanup after test if needed


@pytest.fixture
def mock_env_file():
    """Provide mock environment variables for testing"""
    return {
        "OPENAI_API_KEY": "test-key",
        "ANTHROPIC_API_KEY": "test-key",
        "GOOGLE_API_KEY": "test-key",
    }


# Allow async def tests without requiring pytest-asyncio plugin
@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        kwargs = {
            arg: pyfuncitem.funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames
        }
        asyncio.run(testfunction(**kwargs))
        return True
    return None


@pytest.fixture(autouse=True)
def suppress_resource_warnings():
    warnings.simplefilter("ignore", ResourceWarning)
