# Aetherra Testing Guide

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide covers testing practices, test suite structure, and how to write and run tests for Aetherra OS, Hub, and related components.

## Purpose and scope

- Understand Aetherra's test suite organization
- Run different types of tests (unit, integration, smoke, capability)
- Write new tests following project conventions
- Use mocking and fixtures effectively
- Measure and maintain test coverage
- Integrate testing into CI/CD pipelines

## Test Suite Overview

Aetherra uses **pytest** as the primary testing framework with multiple test categories:

| Test Type             | Location              | Purpose                           | Speed   | When to Run       |
| --------------------- | --------------------- | --------------------------------- | ------- | ----------------- |
| **Unit Tests**        | `tests/unit/`         | Test individual functions/classes | Fast    | Every commit      |
| **Integration Tests** | `tests/integration/`  | Test component interactions       | Medium  | Before merge      |
| **Smoke Tests**       | `tests/smoke/`        | Verify basic functionality        | Fast    | After deployment  |
| **Capability Tests**  | `tests/capabilities/` | Validate system claims            | Slow    | Before release    |
| **End-to-End Tests**  | `tests/e2e/`          | Test complete workflows           | Slowest | Release candidate |

---

## Quick Start

### Prerequisites

**Install test dependencies:**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Key testing packages:**

- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities
- `pytest-timeout` - Test timeouts
- `requests-mock` - HTTP mocking

### Running Tests

**Run all tests:**

```bash
pytest
```

**Run specific test category:**

```bash
# Unit tests only
pytest tests/unit/

# Smoke tests
pytest tests/smoke/

# Capability tests
pytest tests/capabilities/
```

**Run specific test file:**

```bash
pytest tests/unit/test_memory_system.py
```

**Run specific test function:**

```bash
pytest tests/unit/test_memory_system.py::test_memory_store_and_retrieve
```

**Run with verbose output:**

```bash
pytest -v
```

**Run with coverage:**

```bash
pytest --cov=Aetherra --cov-report=html
```

**Run tests matching pattern:**

```bash
# Run all tests with "homeostasis" in the name
pytest -k homeostasis
```

---

## Test Suite Structure

### Directory Layout

```
tests/
├── unit/                       # Unit tests
│   ├── test_memory_system.py
│   ├── test_kernel_loop.py
│   ├── test_homeostasis.py
│   └── ...
├── integration/                # Integration tests
│   ├── test_hub_integration.py
│   ├── test_memory_integration.py
│   └── ...
├── smoke/                      # Smoke tests
│   ├── test_os_startup.py
│   ├── test_hub_health.py
│   └── ...
├── capabilities/               # Capability validation tests
│   ├── test_ownership_memory.py
│   ├── test_lyrixa_ownership_answer.py
│   ├── test_hub_metrics_observability.py
│   └── ...
├── e2e/                        # End-to-end tests
│   ├── test_full_workflow.py
│   └── ...
├── data/                       # Test data
│   ├── golden_learning_set.json
│   └── fixtures/
├── conftest.py                 # Shared fixtures
└── README.md                   # Testing documentation
```

### Test Naming Conventions

**Test files:**

- Must start with `test_`
- Use descriptive names: `test_memory_system.py`, `test_hub_api.py`

**Test functions:**

- Must start with `test_`
- Use descriptive names: `test_memory_store_and_retrieve()`
- Use underscores to separate words

**Test classes:**

- Start with `Test`: `class TestMemorySystem:`
- Group related tests together

**Examples:**

```python
# Good test names
def test_memory_stores_event_successfully():
    pass

def test_homeostasis_calculates_health_score():
    pass

def test_hub_returns_401_when_token_missing():
    pass

# Avoid vague names
def test_memory():  # Too vague
    pass

def test_1():  # Non-descriptive
    pass
```

---

## Writing Unit Tests

### Basic Test Structure

```python
import pytest
from Aetherra.memory_system import MemorySystem

def test_memory_stores_and_retrieves_event():
    """Test that MemorySystem can store and retrieve an event."""
    # Arrange
    memory = MemorySystem()
    event = {
        "type": "test_event",
        "data": "test data",
        "timestamp": 1730476800
    }

    # Act
    memory.store_event(event)
    retrieved = memory.get_event(event_type="test_event")

    # Assert
    assert retrieved is not None
    assert retrieved["type"] == "test_event"
    assert retrieved["data"] == "test data"
```

### Using Fixtures

**Define shared fixtures in conftest.py:**

```python
# tests/conftest.py
import pytest
from Aetherra.memory_system import MemorySystem
from Aetherra.kernel_loop import KernelLoop

@pytest.fixture
def memory_system():
    """Provide a clean MemorySystem instance."""
    memory = MemorySystem(db_path=":memory:")
    yield memory
    memory.close()

@pytest.fixture
def kernel():
    """Provide a KernelLoop instance."""
    kernel = KernelLoop(test_mode=True)
    yield kernel
    kernel.shutdown()

@pytest.fixture
def sample_event():
    """Provide a sample event for testing."""
    return {
        "type": "test_event",
        "timestamp": 1730476800,
        "data": {"key": "value"}
    }
```

**Use fixtures in tests:**

```python
def test_memory_with_fixture(memory_system, sample_event):
    """Test memory system using fixtures."""
    memory_system.store_event(sample_event)
    retrieved = memory_system.get_event(event_type="test_event")
    assert retrieved["data"]["key"] == "value"
```

### Parametrized Tests

Test multiple inputs with `@pytest.mark.parametrize`:

```python
import pytest

@pytest.mark.parametrize("health_score,expected_state", [
    (0.95, "healthy"),
    (0.75, "moderate"),
    (0.50, "degraded"),
    (0.25, "critical"),
])
def test_homeostasis_state_calculation(health_score, expected_state):
    """Test homeostasis state for different health scores."""
    from Aetherra.homeostasis import calculate_state

    state = calculate_state(health_score)
    assert state == expected_state
```

### Testing Exceptions

```python
import pytest

def test_memory_raises_error_on_invalid_event():
    """Test that MemorySystem raises ValueError for invalid events."""
    from Aetherra.memory_system import MemorySystem

    memory = MemorySystem()

    with pytest.raises(ValueError, match="Event must have 'type' field"):
        memory.store_event({})  # Missing 'type' field
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_memory_query():
    """Test asynchronous memory query."""
    from Aetherra.memory_system import MemorySystem

    memory = MemorySystem()
    result = await memory.async_query("SELECT * FROM events")
    assert isinstance(result, list)
```

---

## Mocking and Patching

### Using pytest-mock

```python
def test_hub_with_mocked_ai_provider(mocker):
    """Test Hub with mocked AI provider."""
    # Mock external AI API call
    mock_ai_response = {
        "response": "Mocked response",
        "model": "mock-model"
    }
    mocker.patch(
        'Aetherra.hub.ai_provider.call_ai',
        return_value=mock_ai_response
    )

    from Aetherra.hub import Hub
    hub = Hub()
    response = hub.ask("test prompt")

    assert response["response"] == "Mocked response"
```

### Mocking HTTP Requests

```python
import requests_mock
import requests

def test_hub_api_call():
    """Test Hub API call with mocked HTTP response."""
    with requests_mock.Mocker() as m:
        # Mock the API endpoint
        m.post(
            'http://localhost:3001/api/ai/ask',
            json={"response": "test response"},
            status_code=200
        )

        # Make request
        response = requests.post(
            'http://localhost:3001/api/ai/ask',
            json={"prompt": "test"}
        )

        assert response.status_code == 200
        assert response.json()["response"] == "test response"
```

### Mocking File System

```python
def test_config_loader_with_mock_file(mocker, tmp_path):
    """Test config loader with temporary file."""
    # Create temporary config file
    config_file = tmp_path / "config.json"
    config_file.write_text('{"setting": "value"}')

    # Mock config path
    mocker.patch('Aetherra.config.CONFIG_PATH', str(config_file))

    from Aetherra.config import load_config
    config = load_config()

    assert config["setting"] == "value"
```

### Mocking Environment Variables

```python
def test_with_env_var(monkeypatch):
    """Test behavior with specific environment variable."""
    monkeypatch.setenv("AETHERRA_PROFILE", "test")

    from Aetherra.config import get_profile
    profile = get_profile()

    assert profile == "test"
```

---

## Integration Tests

### Testing Component Interactions

```python
import pytest
import time

@pytest.mark.integration
def test_hub_memory_integration():
    """Test that Hub correctly interacts with Memory system."""
    from Aetherra.hub import Hub
    from Aetherra.memory_system import MemorySystem

    # Initialize components
    memory = MemorySystem(db_path=":memory:")
    hub = Hub(memory_system=memory)

    # Perform action
    hub.process_event({
        "type": "user_message",
        "content": "test message"
    })

    # Verify interaction
    time.sleep(0.1)  # Allow async processing
    events = memory.query_events(event_type="user_message")

    assert len(events) > 0
    assert events[0]["content"] == "test message"
```

### Testing API Endpoints

```python
import pytest
from flask import Flask

@pytest.fixture
def app():
    """Provide Flask test app."""
    from aetherra_hub.hub_server import create_app
    app = create_app(test_mode=True)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Provide Flask test client."""
    return app.test_client()

def test_stats_endpoint(client):
    """Test /api/stats endpoint."""
    response = client.get('/api/stats')

    assert response.status_code == 200
    data = response.get_json()
    assert "uptime" in data
    assert "health_score" in data

def test_ai_ask_endpoint(client):
    """Test /api/ai/ask endpoint."""
    response = client.post(
        '/api/ai/ask',
        json={"prompt": "test prompt"},
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
```

---

## Smoke Tests

### OS Startup Test

```python
import subprocess
import time
import requests

def test_os_starts_successfully():
    """Smoke test: Verify OS starts and responds."""
    # Start OS in subprocess
    process = subprocess.Popen(
        ["python", "aetherra_os_launcher.py", "--mode", "minimal"],
        env={"AETHERRA_PROFILE": "test", "AETHERRA_QUIET": "1"}
    )

    try:
        # Wait for startup
        time.sleep(10)

        # Verify process is running
        assert process.poll() is None, "OS process died"

    finally:
        # Cleanup
        process.terminate()
        process.wait(timeout=10)
```

### Hub Health Check

```python
import requests

def test_hub_health_check():
    """Smoke test: Verify Hub is healthy."""
    response = requests.get('http://localhost:3001/api/stats', timeout=5)

    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert data.get("health_score", 0) > 0.5
```

---

## Capability Tests

Capability tests validate system claims and requirements:

```python
import pytest
import requests

@pytest.mark.capability
def test_ownership_memory_claim():
    """
    Capability Test: Verify ownership tracking in memory system.

    Claim: System must track ownership of all stored events.
    Reference: AETHERRA_CLAIMS_VALIDATION.md
    """
    from Aetherra.memory_system import MemorySystem

    memory = MemorySystem(db_path=":memory:")

    # Store event with ownership
    event = {
        "type": "test_event",
        "owner": "Aetherra Labs",
        "data": "test data"
    }
    memory.store_event(event)

    # Retrieve and verify ownership
    retrieved = memory.get_event(event_type="test_event")
    assert retrieved is not None
    assert retrieved["owner"] == "Aetherra Labs"

@pytest.mark.capability
def test_lyrixa_ownership_answer():
    """
    Capability Test: Verify Lyrixa correctly answers ownership questions.

    Claim: Lyrixa must identify Aetherra Labs as the owner when asked.
    Reference: AETHERRA_CLAIMS_VALIDATION.md
    """
    response = requests.post(
        'http://localhost:3001/api/ai/ask',
        json={"prompt": "Who owns you?"}
    )

    assert response.status_code == 200
    answer = response.json()["response"].lower()
    assert "aetherra labs" in answer
```

---

## Coverage Requirements

### Measuring Coverage

**Generate HTML coverage report:**

```bash
pytest --cov=Aetherra --cov-report=html
```

**View report:**

```bash
# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Generate terminal report:**

```bash
pytest --cov=Aetherra --cov-report=term-missing
```

### Coverage Targets

| Component         | Target Coverage | Current |
| ----------------- | --------------- | ------- |
| **Core OS**       | 80%             | ~75%    |
| **Memory System** | 85%             | ~80%    |
| **Hub API**       | 75%             | ~70%    |
| **Homeostasis**   | 80%             | ~78%    |
| **Plugins**       | 70%             | ~65%    |

### Coverage Best Practices

**Focus on critical paths:**

- Core business logic
- Error handling
- Security-sensitive code
- Public APIs

**Don't obsess over 100%:**

- Some code is hard to test (UI, external integrations)
- Focus on meaningful coverage, not metrics

**Exclude non-critical code:**

```ini
# .coveragerc
[run]
omit =
    */tests/*
    */migrations/*
    */venv/*
    */__pycache__/*
    */site-packages/*
    */examples/*
```

---

## Test Configuration

### pytest.ini

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Minimum Python version
minversion = 3.11

# Additional options
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=Aetherra
    --cov-report=term-missing:skip-covered
    --cov-fail-under=70

# Test paths
testpaths = tests

# Markers for categorizing tests
markers =
    unit: Unit tests
    integration: Integration tests
    smoke: Smoke tests
    capability: Capability validation tests
    e2e: End-to-end tests
    slow: Tests that take > 1 second
    asyncio: Async tests

# Timeout for tests
timeout = 300
timeout_method = thread

# Asyncio mode
asyncio_mode = auto
```

### Running Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run smoke and capability tests
pytest -m "smoke or capability"

# Run integration tests with verbose output
pytest -m integration -v
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run unit tests
      env:
        AETHERRA_PROFILE: test
        AETHERRA_QUIET: 1
      run: |
        pytest tests/unit/ -v --cov=Aetherra --cov-report=xml

    - name: Run smoke tests
      env:
        AETHERRA_PROFILE: test
      run: |
        pytest tests/smoke/ -v

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

    - name: Check coverage threshold
      run: |
        pytest --cov=Aetherra --cov-fail-under=70
```

---

## Common Testing Patterns

### Testing with Temporary Directories

```python
def test_file_operations(tmp_path):
    """Test file operations using temporary directory."""
    # tmp_path is a pytest fixture providing a temporary directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Perform operations
    from Aetherra.file_utils import read_file
    content = read_file(str(test_file))

    assert content == "test content"
```

### Testing Time-Dependent Code

```python
from unittest.mock import patch
from datetime import datetime

@patch('Aetherra.utils.datetime')
def test_time_dependent_function(mock_datetime):
    """Test function that depends on current time."""
    # Mock current time
    mock_datetime.now.return_value = datetime(2025, 11, 1, 12, 0, 0)

    from Aetherra.scheduler import should_run_task
    result = should_run_task("daily_task")

    assert result is True
```

### Testing Logging

```python
import logging

def test_function_logs_error(caplog):
    """Test that function logs error message."""
    from Aetherra.error_handler import handle_error

    with caplog.at_level(logging.ERROR):
        handle_error(Exception("test error"))

    assert "test error" in caplog.text
```

### Testing Command-Line Arguments

```python
import sys

def test_cli_argument_parsing(monkeypatch):
    """Test CLI argument parsing."""
    # Mock sys.argv
    monkeypatch.setattr(sys, 'argv', ['script.py', '--mode', 'test'])

    from Aetherra.cli import parse_args
    args = parse_args()

    assert args.mode == 'test'
```

---

## Debugging Tests

### Running Tests with Debugger

**Using pdb:**

```python
def test_with_debugger():
    """Test with breakpoint for debugging."""
    from Aetherra.memory_system import MemorySystem

    memory = MemorySystem()

    # Set breakpoint
    import pdb; pdb.set_trace()

    result = memory.query_events()
    assert len(result) > 0
```

**Or use built-in breakpoint():**

```python
def test_with_breakpoint():
    """Test with Python 3.7+ breakpoint."""
    result = some_function()
    breakpoint()  # Debugger will stop here
    assert result == expected
```

### Verbose Test Output

```bash
# Maximum verbosity
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Show full diff on assertion failures
pytest --tb=long
```

### Running Single Test Repeatedly

```bash
# Useful for debugging flaky tests
for i in {1..100}; do
    pytest tests/test_flaky.py::test_something || break
done
```

---

## Test Data Management

### Golden Test Sets

```python
import json
import pytest

@pytest.fixture
def golden_dataset():
    """Load golden test dataset."""
    with open('tests/data/golden_learning_set.json') as f:
        return json.load(f)

def test_learning_evaluation(golden_dataset):
    """Test learning system against golden dataset."""
    from Aetherra.learning import evaluate_learning

    results = evaluate_learning(golden_dataset)

    # Verify metrics meet thresholds
    assert results["accuracy"] > 0.90
    assert results["recall"] > 0.85
```

### Test Fixtures Organization

```
tests/
├── data/
│   ├── fixtures/
│   │   ├── events.json          # Sample events
│   │   ├── configs.json         # Sample configurations
│   │   └── responses.json       # Sample API responses
│   └── golden_learning_set.json
└── conftest.py
```

---

## Best Practices

### Test Independence

**Each test should be independent:**

```python
# Good: Independent test
def test_memory_store():
    memory = MemorySystem(db_path=":memory:")
    memory.store_event({"type": "test"})
    assert memory.count_events() == 1

# Bad: Depends on previous test state
shared_memory = MemorySystem()

def test_store_event():
    shared_memory.store_event({"type": "test"})

def test_count_events():
    # Assumes previous test ran first!
    assert shared_memory.count_events() == 1
```

### Test Readability

**Use Arrange-Act-Assert pattern:**

```python
def test_homeostasis_health_score():
    # Arrange - Set up test data
    metrics = {
        "cpu_usage": 0.5,
        "memory_usage": 0.6,
        "error_rate": 0.1
    }

    # Act - Perform the action
    from Aetherra.homeostasis import calculate_health_score
    score = calculate_health_score(metrics)

    # Assert - Verify results
    assert 0.0 <= score <= 1.0
    assert score > 0.7  # Should be healthy
```

### Test Documentation

```python
def test_memory_query_performance():
    """
    Test that memory query completes within acceptable time.

    Performance requirement: Query < 100ms for 1000 events.

    Steps:
    1. Insert 1000 events
    2. Measure query time
    3. Assert < 100ms
    """
    import time
    from Aetherra.memory_system import MemorySystem

    memory = MemorySystem(db_path=":memory:")

    # Insert test data
    for i in range(1000):
        memory.store_event({"type": "test", "index": i})

    # Measure query time
    start = time.time()
    results = memory.query_events(limit=100)
    elapsed_ms = (time.time() - start) * 1000

    assert elapsed_ms < 100, f"Query took {elapsed_ms}ms (limit: 100ms)"
```

---

## Related Documentation

- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Debugging test failures
- [AETHERRA_HUB_API_REFERENCE.md](./AETHERRA_HUB_API_REFERENCE.md) - API endpoints for testing
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - CI/CD integration
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

---

Status: ✅ Complete - Comprehensive testing guide covering all test types and best practices

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
